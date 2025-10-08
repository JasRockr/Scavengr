"""scavengr.infrastructure.database
====================================

Adaptadores de bases de datos.
Implementa interfaces del dominio para conectores y scanners.
"""

from scavengr.infrastructure.database.connector import (
    DatabaseConnector,
    PostgreSQLConnector,
    MySQLConnector,
    MSSQLConnector,
    create_connector,
)
from scavengr.infrastructure.database.base_scanner import MetadataScanner
from scavengr.infrastructure.database.scanners import (
    MSSQLScanner,
    MySQLScanner,
    PostgreSQLScanner,
    create_scanner,
)

# Alias para compatibilidad
SQLServerConnector = MSSQLConnector

__all__ = [
    # Connectors
    "DatabaseConnector",
    "PostgreSQLConnector",
    "MySQLConnector",
    "MSSQLConnector",
    "SQLServerConnector",  # Alias
    "create_connector",  # Factory function
    # Scanners
    "MetadataScanner",
    "MSSQLScanner",
    "MySQLScanner",
    "PostgreSQLScanner",
    "create_scanner",  # Factory function
]
