"""scavengr.utils.ui_helpers
==============================

Helpers para interfaz de usuario y feedback visual en consola.
Provee funciones para mostrar mensajes coloreados y formateados.
"""

__all__ = ["provide_user_feedback"]


def provide_user_feedback(message: str, level: str = "info") -> None:
    """Proporciona feedback mejorado al usuario con colores y formateo.

    Args:
        message: Mensaje a mostrar.
        level: Nivel del mensaje (info, warning, error, success).

    Examples:
        >>> provide_user_feedback("Operacion exitosa", "success")
        >>> provide_user_feedback("Advertencia detectada", "warning")
        >>> provide_user_feedback("Error critico", "error")

    Note:
        Los colores ANSI pueden no funcionar en todas las consolas.
        En Windows cmd/PowerShell antiguo puede verse sin colores.
    """
    colors = {
        'info': '\033[94m',      # Azul
        'warning': '\033[93m',   # Amarillo
        'error': '\033[91m',     # Rojo
        'success': '\033[92m',   # Verde
        'reset': '\033[0m'       # Reset
    }

    # Prefijos sin emojis para compatibilidad multiplataforma
    prefixes = {
        'info': '[INFO]',
        'warning': '[WARNING]',
        'error': '[ERROR]',
        'success': '[SUCCESS]'
    }

    color = colors.get(level, colors['info'])
    prefix = prefixes.get(level, '[INFO]')

    print(f"{color}{prefix} {message}{colors['reset']}")
