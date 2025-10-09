"""Scavengr - Descubre lo que tus bases esconden.

Scavengr es una herramienta ligera y multiplataforma para explorar, procesar 
y documentar metadatos de bases de datos. Convierte estructuras de esquemas 
en DBML validado, genera diccionarios de datos en múltiples formatos y 
revela insights ocultos que antes quedaban bajo tierra.

Porque en cada tabla, cada columna y cada índice... cada dato cuenta su historia.

Architecture:
    - core/: Entidades de dominio e interfaces (Clean Architecture)
    - application/: Casos de uso y lógica de aplicación
    - infrastructure/: Implementaciones de infraestructura (database, parsers, formatters, exporters)
    - config/: Configuración y gestión de entorno
    - utils/: Utilidades transversales (logging, validación, excepciones)

Author: Json Rivera
Date: 2025-10-09
Version: 0.0.3
"""

import sys
import warnings

# Intentar importar la versión desde un archivo separado
try:
    from scavengr._version import __version__ 
except ImportError:
    __version__ = "0.0.1"

# Metadatos del paquete
__author__ = "Json Rivera"
__email__ = "jsonrivera@proton.me"
__description__ = "Descubre lo que tus bases esconden."
__project_name__ = "Scavengr"

# Validación de compatibilidad de Python
if sys.version_info < (3, 8):
    raise RuntimeError("Scavengr requiere Python 3.8 o superior")

# Exportar componentes principales para uso como librería
# NOTA: Se mantiene compatibilidad con rutas antiguas mediante deprecation warnings
try:
    # Importar desde nuevas ubicaciones (Clean Architecture)
    from scavengr.core.entities import Column, Table, Relationship, Index, DatabaseSchema
    from scavengr.infrastructure.parsers import DBMLParser
    from scavengr.infrastructure.formatters import DBMLFormatter
    from scavengr.infrastructure.exporters import OutputWriter
    from scavengr.infrastructure.database import DatabaseConnector, MetadataScanner
    from scavengr.config.env_config import EnvConfigManager
    
    __all__ = [
        # Entidades de dominio
        'Column',
        'Table', 
        'Relationship',
        'Index',
        'DatabaseSchema',
        # Componentes de infraestructura
        'DBMLParser',
        'DBMLFormatter',
        'OutputWriter',
        'DatabaseConnector',
        'MetadataScanner',
        'EnvConfigManager'
    ]
except ImportError as e:
    # En caso de problemas de importación, definir __all__ vacío
    # pero permitir que el paquete se cargue para uso del CLI
    __all__ = []
    warnings.warn(
        f"Algunas dependencias de Scavengr no están disponibles: {e}",
        UserWarning
    )

def main():
    """Entry point para el CLI de Scavengr.
    
    Redirige la ejecución al módulo cli.py que contiene la implementación
    completa del CLI.
    
    Returns:
        int: Código de salida del CLI (0 = éxito, != 0 = error)
    """
    from scavengr.cli import main as cli_main
    return cli_main()