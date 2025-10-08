"""scavengr.utils.logging_config
=================================

Configuración centralizada de logging para Scavengr.
Provee un formateador con color ANSI y una función `setup_logging` que
configura un logger con consola (y opción de archivo) sin depender de
paquetes externos.

"""
from __future__ import annotations

import logging
import sys
import os
from typing import Optional

__all__ = ["setup_logging", "ColorFormatter", "supports_color", "DEFAULT_LOG_FORMAT"]


# Constantes de configuración
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ColorFormatter(logging.Formatter):
    """Formateador con colores ANSI configurables por nivel.

    Args:
        fmt: Formato del mensaje (opcional).
        datefmt: Formato de fecha (opcional).
        use_color: Si True aplica colores cuando el stream lo soporte.
    """

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[1;41m', # Bold White on Red background
    }
    RESET = '\033[0m'

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, use_color: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if self.use_color and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            message = f"{color}{message}{self.RESET}"
        return message


def supports_color() -> bool:
    """Detecta si el entorno de salida soporta colores ANSI.

    Compatible con Linux, macOS y WSL. En Windows intenta detectar terminales
    modernos comprobando variables de entorno.
    """
    try:
        if sys.platform != "win32":
            return sys.stdout.isatty()
        # En Windows, comprobar algunas variables comunes (WT = Windows Terminal)
        return bool(os.getenv("ANSICON") or os.getenv("WT_SESSION") or os.getenv("TERM"))
    except Exception:
        return False


def setup_logging(
    verbose: bool = False,
    name: str = "Scavengr",
    log_file: Optional[str] = None,
    file_level: int = logging.INFO,
    force_color: Optional[bool] = None,
    fmt: Optional[str] = None
) -> logging.Logger:
    """Configura el sistema de logging de forma centralizada con soporte de color.

    Args:
        verbose: Si True activa nivel DEBUG, si False usa INFO.
        name: Nombre base del logger.
        log_file: Ruta opcional para escribir logs a archivo.
        file_level: Nivel para el handler de archivo (por defecto INFO).
        force_color: Si True fuerza colores, si False los deshabilita, si None detecta automáticamente.
        fmt: Formato personalizado del log. Si no se provee usa DEFAULT_LOG_FORMAT.

    Returns:
        Logger configurado para la aplicación.

    Examples:
        >>> # Uso básico
        >>> logger = setup_logging()
        >>> logger.info("Mensaje de información")

        >>> # Con verbose y archivo
        >>> logger = setup_logging(verbose=True, log_file="app.log")
        >>> logger.debug("Depuración detallada")

        >>> # Forzar colores
        >>> logger = setup_logging(force_color=True)
        
        >>> # Con formato personalizado
        >>> logger = setup_logging(fmt="%(levelname)s: %(message)s")
    """

    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar handlers duplicados si se llama varias veces
    if logger.hasHandlers():
        logger.handlers.clear()

    # Determinar si forzar color por variable de entorno o parámetro
    env_force = os.getenv("SCAVENGR_FORCE_COLOR")
    if force_color is None and env_force is not None:
        env_val = env_force.lower()
        if env_val in ("1", "true", "yes", "on"):
            force_color = True
        elif env_val in ("0", "false", "no", "off"):
            force_color = False

    use_color = bool(force_color) if force_color is not None else supports_color()

    log_format = fmt if fmt is not None else DEFAULT_LOG_FORMAT
    formatter = ColorFormatter(fmt=log_format, use_color=use_color)

    # StreamHandler (consola) con soporte UTF-8 en Windows
    try:
        # Intentar configurar UTF-8 en Windows
        if sys.platform == "win32":
            import io
            console_handler = logging.StreamHandler(
                io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
    except (AttributeError, OSError):
        # Fallback: usar StreamHandler normal
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # Handler opcional a archivo
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


if __name__ == "__main__":
    # Uso de demostración
    log = setup_logging(verbose=True, force_color=True)
    log.debug("Depuración detallada")
    log.info("Proceso iniciado correctamente")
    log.warning("Advertencia de prueba")
    log.error("Error detectado")
    log.critical("Fallo crítico")
