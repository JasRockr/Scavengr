"""scavengr.utils.constants
============================

Constantes compartidas para el proyecto Scavengr.
Define comandos CLI, formatos soportados, mensajes estándar,
puertos por defecto y OIDs de PostgreSQL.

Author: Json Rivera
Date: 2025-10-09
Version: 0.0.3
"""

__all__ = ["Commands", "Formats", "Messages", "DatabaseDefaults", "PostgreSQLOIDs"]


class Commands:
    """Constantes para nombres de comandos CLI.

    Attributes:
        EXTRACT: Comando para extraer metadatos de BD.
        VALIDATE: Comando para validar archivos DBML.
        DICTIONARY: Comando para generar diccionarios de datos.
        REPORT: Comando para generar informes.
        INIT: Comando para inicializar configuración.
    """

    EXTRACT = "extract"
    VALIDATE = "validate"
    DICTIONARY = "dictionary"
    REPORT = "report"
    INIT = "init"


class Formats:
    """Constantes para formatos de salida soportados.

    Attributes:
        CSV: Formato CSV (valores separados por comas).
        EXCEL: Formato Excel (.xlsx, .xls).
        JSON: Formato JSON.
        SUPPORTED: Lista de todos los formatos soportados.
    """

    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    SUPPORTED = [CSV, EXCEL, JSON]


class Messages:
    """Constantes para mensajes de error y información.

    Plantillas de mensajes con placeholders para formateo.
    """

    FILE_NOT_FOUND = "Archivo no encontrado: {}"
    DBML_NOT_FOUND = "Archivo DBML no encontrado: {}"
    CONFIG_NOT_FOUND = "Archivo de configuracion no encontrado: {}"
    INVALID_FORMAT = "Formato no soportado: {}. Formatos validos: {}"
    PROCESSING_ERROR = "Error procesando {}: {}"
    SUCCESS_MESSAGE = "[SUCCESS] {} completado exitosamente"


class DatabaseDefaults:
    """Constantes para puertos por defecto de bases de datos.

    Attributes:
        MYSQL_PORT: Puerto por defecto para MySQL/MariaDB (3306).
        POSTGRESQL_PORT: Puerto por defecto para PostgreSQL (5432).
        MSSQL_PORT: Puerto por defecto para SQL Server (1433).
        MSSQL_DRIVER: Driver ODBC por defecto para SQL Server.
    """

    MYSQL_PORT = 3306
    POSTGRESQL_PORT = 5432
    MSSQL_PORT = 1433
    MSSQL_DRIVER = "SQL Server"


class PostgreSQLOIDs:
    """Constantes para OIDs (Object Identifiers) de tipos PostgreSQL.

    Los OIDs son identificadores internos de PostgreSQL para tipos de datos.
    Se usan en consultas al catálogo del sistema (pg_catalog).

    Attributes:
        CHAR: OID para tipo char/bpchar (1042).
        VARCHAR: OID para tipo varchar/character varying (1043).
        NUMERIC: OID para tipo numeric/decimal (1700).
        TYPMOD_OFFSET: Offset para calcular longitud desde atttypmod (4).
    """

    CHAR = 1042
    VARCHAR = 1043
    NUMERIC = 1700
    TYPMOD_OFFSET = 4
