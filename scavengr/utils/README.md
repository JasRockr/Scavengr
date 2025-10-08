# Scavengr Utils

Módulo de utilidades compartidas para el proyecto Scavengr.

## Estructura

```text
scavengr/utils/
├── __init__.py             # Exporta funciones principales
├── constants.py            # Constantes compartidas
├── exceptions.py           # Excepciones personalizadas
├── logging_config.py       # Sistema de logging centralizado
├── ui_helpers.py           # Helpers para interfaz de usuario y feedback visual en consola
├── validators.py           # Validadores de archivos y permisos
└── README.md               # Este archivo
```

---

## Logging (`logging_config.py`)

Sistema de logging centralizado con soporte de colores ANSI multiplataforma.

### Características

- ✅ **Colores automáticos** por nivel de log (DEBUG=cyan, INFO=verde, WARNING=amarillo, ERROR=rojo, CRITICAL=rojo con fondo)
- ✅ **Detección automática** de soporte de color en el terminal
- ✅ **Forzado de color** mediante parámetro o variable de entorno
- ✅ **Soporte UTF-8** en Windows (maneja emojis y caracteres especiales)
- ✅ **Handler a archivo** opcional para persistir logs
- ✅ **Sin dependencias externas** (solo stdlib: `logging`, `sys`, `os`)

### Uso básico

```python
from scavengr.utils import setup_logging

# Configuración simple
logger = setup_logging()
logger.info("Mensaje de información")
logger.error("Algo salió mal")

# Con modo verbose (DEBUG)
logger = setup_logging(verbose=True)
logger.debug("Depuración detallada")

# Con archivo de log
logger = setup_logging(log_file="app.log")
logger.info("Este mensaje va a consola y archivo")

# Forzar colores (útil en CI/CD)
logger = setup_logging(force_color=True)

# Con formato personalizado
from scavengr.utils import DEFAULT_LOG_FORMAT
logger = setup_logging(fmt="[%(levelname)s] %(message)s")
logger.info("Formato simplificado")

# Usando el formato por defecto explícitamente
logger = setup_logging(fmt=DEFAULT_LOG_FORMAT)
```

### Configuración de colores

#### Por código

```python
logger = setup_logging(force_color=True)  # Forzar colores
logger = setup_logging(force_color=False) # Deshabilitar colores
```

#### Por variable de entorno

```powershell
# PowerShell (Windows)
$env:SCAVENGR_FORCE_COLOR = "1"
python -m scavengr.scavengr extract --verbose

# Bash/Zsh (Linux/macOS)
export SCAVENGR_FORCE_COLOR=1
python -m scavengr.scavengr extract --verbose
```

Valores aceptados:

- `1`, `true`, `yes`, `on` → habilita colores
- `0`, `false`, `no`, `off` → deshabilita colores

### API Completa

```python
def setup_logging(
    verbose: bool = False,
    name: str = "Scavengr",
    log_file: Optional[str] = None,
    file_level: int = logging.INFO,
    force_color: Optional[bool] = None,
    fmt: Optional[str] = None
) -> logging.Logger
```

**Parámetros:**

- `verbose`: Si `True`, activa nivel DEBUG; si `False`, usa INFO.
- `name`: Nombre del logger (por defecto: "Scavengr").
- `log_file`: Ruta opcional para escribir logs a archivo.
- `file_level`: Nivel de log para el archivo (por defecto: INFO).
- `force_color`: Si `True` fuerza colores, si `False` los deshabilita, si `None` detecta automáticamente.
- `fmt`: Formato personalizado del log. Si no se provee usa `DEFAULT_LOG_FORMAT`.

**Retorna:**

- `logging.Logger` configurado y listo para usar.

**Constantes:**

- `DEFAULT_LOG_FORMAT`: Formato por defecto = `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`

---

## Cómo usar en otros módulos

### Opción 1: Importar directamente desde utils

```python
# En cualquier módulo de scavengr
from scavengr.utils import setup_logging

logger = setup_logging()
logger.info("Módulo inicializado")
```

### Opción 2: Usar el logger ya configurado

```python
# Si scavengr.scavengr ya configuró el logger
import logging

logger = logging.getLogger("Scavengr")
logger.info("Reutilizando logger configurado")
```

### Opción 3: Logger por módulo

```python
# Para crear un logger específico por módulo
from scavengr.utils import setup_logging

logger = setup_logging(name="Scavengr.Connectors")
logger.debug("Logger específico para connectors")
```

---

## Ejemplo de integración en CLI

En `scavengr/scavengr.py`:

```python
from scavengr.utils import setup_logging

# Logger por defecto (INFO)
logger = setup_logging()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    
    # Reconfigurar si verbose=True
    if args.verbose:
        setup_logging(verbose=True)
        logger.info("Modo detallado (DEBUG) activado")
    
    # Usar el logger
    logger.info("Iniciando aplicación")
```

---

## Detección de soporte de color

El módulo detecta automáticamente si el terminal soporta colores ANSI:

- **Linux/macOS**: Comprueba si `sys.stdout.isatty()` es `True`
- **Windows**: Detecta terminales modernos (Windows Terminal, ConEmu, etc.) mediante variables de entorno:
  - `ANSICON`
  - `WT_SESSION`
  - `TERM`

Si no hay detección, usa colores por defecto. Puedes forzarlos con `force_color=True`.

---

## Formato de mensajes

Formato por defecto:

```bash
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Ejemplo de salida:

```bash
2025-10-06 08:47:58,979 - Scavengr - INFO - Proceso iniciado
```

---

## Pruebas

Para probar el módulo de logging directamente:

```powershell
# Ejecutar el módulo como script
python -m scavengr.utils.logging_config

# O importar y probar
python -c "from scavengr.utils import setup_logging; log=setup_logging(verbose=True, force_color=True); log.debug('Test'); log.info('Test'); log.warning('Test'); log.error('Test')"
```

---

## Principios de diseño

- **DRY (Don't Repeat Yourself)**: Configuración centralizada, un solo lugar para modificar.
- **KISS (Keep It Simple, Stupid)**: API simple, sin complejidad innecesaria.
- **Clean Architecture**: Separación clara entre infraestructura (logging) y lógica de aplicación.
- **Sin dependencias externas**: Solo usa la biblioteca estándar de Python.

---

## Extensiones futuras proyectadas

Posibles mejoras sin romper la API actual:

- [ ] `RotatingFileHandler` para rotación de logs por tamaño
- [ ] `TimedRotatingFileHandler` para rotación por tiempo
- [ ] Formatter JSON para integración con sistemas de logging centralizados
- [ ] Soporte para configuración desde archivo YAML/TOML
- [ ] Handlers adicionales (Syslog, HTTP, etc.)

---

## Contacto

Para preguntas o mejoras, consultar con el equipo de desarrollo de Scavengr.
