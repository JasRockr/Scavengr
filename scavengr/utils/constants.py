"""scavengr.utils.constants
============================

Constantes compartidas para el proyecto Scavengr.
Define comandos CLI, formatos soportados y mensajes estándar.

Author: Json Rivera
Date: 2025-10-09
Version: 0.0.3
"""

__all__ = ["Commands", "Formats", "Messages"]


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
