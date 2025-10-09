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

Sistema de logging centralizado con soporte de colores ANSI multiplataforma y herencia automática de configuración.

### Características

- ✅ **Colores automáticos** por nivel de log (DEBUG=cyan, INFO=verde, WARNING=amarillo, ERROR=rojo, CRITICAL=rojo con fondo)
- ✅ **Detección automática** de soporte de color en el terminal
- ✅ **Forzado de color** mediante parámetro o variable de entorno
- ✅ **Soporte UTF-8** en Windows (maneja emojis y caracteres especiales)
- ✅ **Handler a archivo** opcional para persistir logs
- ✅ **Herencia automática** - configura el logger raíz para que todos los sub-loggers hereden nivel DEBUG/INFO
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

### Opción 2: Usar el logger ya configurado (herencia automática)

```python
# Después de que el CLI configure el logger principal
import logging

# Cualquier sub-logger hereda automáticamente la configuración DEBUG/INFO
logger = logging.getLogger(__name__)  # Ej: "scavengr.application.extract"
logger.debug("Este mensaje se verá si verbose=True fue configurado")
logger.info("Reutilizando configuración del logger raíz")
```

### Opción 3: Logger específico de aplicación

```python
# Si necesitas el logger principal específico
import logging

logger = logging.getLogger("Scavengr")
logger.info("Logger principal de la aplicación")
```

### Opción 4: Logger por módulo (recomendado para casos de uso)

```python
# Para crear un logger específico que herede automáticamente
import logging

logger = logging.getLogger(__name__)  # Ej: "scavengr.core.services" 
logger.debug("Logger específico que hereda configuración global")
```

---

## Ejemplo de integración en CLI

En `scavengr/cli.py`:

```python
from scavengr.utils import setup_logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    
    # Configurar logging (configura tanto el logger principal como el raíz)
    global logger
    if args.verbose:
        logger = setup_logging(verbose=True)
        logger.info("Modo detallado (DEBUG) activado")
        logger.debug(f"Argumentos parseados: {vars(args)}")
    else:
        logger = setup_logging(verbose=False)
    
    # Usar el logger
    logger.info("Iniciando aplicación")
```

### Herencia automática en casos de uso

Después de configurar el logger en CLI, cualquier módulo puede usar logging sin configuración adicional:

```python
# En scavengr/application/extract.py
import logging

logger = logging.getLogger(__name__)  # "scavengr.application.extract"

def extract_metadata():
    logger.debug("[DEBUG] Iniciando extracción...")  # ✅ Se ve si verbose=True
    logger.info("[INFO] Conectando a base de datos...")  # ✅ Siempre se ve
    logger.error("[ERROR] Error de conexión")  # ✅ Siempre se ve
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

## Comportamiento de herencia mejorado

### ✅ Antes vs Ahora

**Antes (problemático):**

```python
# CLI configuraba solo "Scavengr"
setup_logging(verbose=True)  # Solo afecta al logger "Scavengr"

# En casos de uso:
logger = logging.getLogger(__name__)  # "scavengr.application.extract"
logger.debug("No se veía")  # ❌ No heredaba la configuración DEBUG
```

**Ahora (solucionado):**

```python
# CLI configura tanto el logger principal como el raíz
setup_logging(verbose=True)  # Afecta al logger raíz + "Scavengr"

# En casos de uso:
logger = logging.getLogger(__name__)  # "scavengr.application.extract"  
logger.debug("Se ve perfectamente")  # ✅ Hereda DEBUG del logger raíz
```

### Ventajas de la nueva implementación

- 🎯 **Configuración única**: Una sola llamada a `setup_logging()` configura toda la aplicación
- 🔄 **Herencia automática**: Todos los módulos heredan nivel DEBUG/INFO sin configuración adicional
- 🧹 **Limpieza de handlers**: Evita handlers duplicados al reconfigurar
- 📝 **Mejor troubleshooting**: Mensajes DEBUG de todos los módulos visibles con `--verbose`

## Principios de diseño

- **DRY (Don't Repeat Yourself)**: Configuración centralizada, un solo lugar para modificar.
- **KISS (Keep It Simple, Stupid)**: API simple, sin complejidad innecesaria.
- **Clean Architecture**: Separación clara entre infraestructura (logging) y lógica de aplicación.
- **Herencia inteligente**: Los sub-loggers heredan automáticamente la configuración del raíz.
- **Sin dependencias externas**: Solo usa la biblioteca estándar de Python.

---

## Mejores prácticas recomendadas

### ✅ Recomendado

```python
# En casos de uso y módulos de aplicación
import logging

logger = logging.getLogger(__name__)  # Hereda configuración automáticamente
logger.debug("[DEBUG] Paso 1: Inicializando...")
logger.info("[INFO] Proceso completado exitosamente")
```

### ⚠️ Evitar

```python
# No crear loggers personalizados innecesarios
from scavengr.utils import setup_logging
logger = setup_logging(name="MiLogger")  # ❌ Innecesario en la mayoría de casos

# No configurar logging múltiples veces
setup_logging(verbose=True)
setup_logging(verbose=False)  # ❌ Puede causar handlers duplicados
```

### 🎯 Patrón recomendado para casos de uso

```python
# scavengr/application/extract.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)  # "scavengr.application.extract"

class ExtractMetadata:
    def execute(self, output_path: str) -> ExtractResult:
        logger.debug(f"[DEBUG] Iniciando extracción hacia: {output_path}")
        logger.info("[INFO] Conectando a base de datos...")
        
        try:
            # Lógica de extracción...
            logger.debug("[DEBUG] Metadatos extraídos exitosamente")
            logger.info("[SUCCESS] Extracción completada")
        except Exception as e:
            logger.error(f"[ERROR] Error en extracción: {str(e)}")
            raise
```

## Extensiones futuras proyectadas

Posibles mejoras sin romper la API actual:

- [ ] `RotatingFileHandler` para rotación de logs por tamaño
- [ ] `TimedRotatingFileHandler` para rotación por tiempo
- [ ] Formatter JSON para integración con sistemas de logging centralizados
- [ ] Soporte para configuración desde archivo YAML/TOML
- [ ] Handlers adicionales (Syslog, HTTP, etc.)
- [ ] Logger context manager para operaciones específicas

---

## Contacto

Para preguntas o mejoras, consultar con el equipo de desarrollo de Scavengr.
