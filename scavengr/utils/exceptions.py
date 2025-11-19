"""scavengr.utils.exceptions
==============================

Excepciones personalizadas para Scavengr.
Todas las excepciones del proyecto heredan de ScavengrError.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

__all__ = [
    "ScavengrError",
    "FileNotFoundError",
    "InvalidFormatError",
    "ProcessingError",
    "ValidationError",
]


class ScavengrError(Exception):
    """Excepción base para todos los errores de Scavengr.

    Todas las excepciones personalizadas de Scavengr deben heredar de esta clase.
    """

    pass


class FileNotFoundError(ScavengrError):
    """Excepción para archivos no encontrados.

    Args:
        filepath: Ruta del archivo que no se encontró.
        file_type: Tipo de archivo (para mensajes descriptivos).

    Examples:
        >>> raise FileNotFoundError("/path/to/file.dbml", "DBML")
    """

    def __init__(self, filepath: str, file_type: str = "archivo"):
        self.filepath = filepath
        self.file_type = file_type
        super().__init__(f"{file_type.capitalize()} no encontrado: {filepath}")


class InvalidFormatError(ScavengrError):
    """Excepción para formatos de archivo no válidos.

    Args:
        format_provided: Formato proporcionado que no es válido.
        valid_formats: Lista de formatos válidos.

    Examples:
        >>> raise InvalidFormatError(".txt", ["csv", "xlsx", "json"])
    """

    def __init__(self, format_provided: str, valid_formats: list[str]) -> None:
        self.format_provided = format_provided
        self.valid_formats = valid_formats
        super().__init__(
            f"Formato no soportado: {format_provided}. "
            f"Formatos validos: {', '.join(valid_formats)}"
        )


class ProcessingError(ScavengrError):
    """Excepción para errores durante el procesamiento.

    Args:
        operation: Nombre de la operación que falló.
        details: Detalles del error.

    Examples:
        >>> raise ProcessingError("parseo DBML", "sintaxis invalida en linea 42")
    """

    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Error procesando {operation}: {details}")


class ValidationError(ScavengrError):
    """Excepción para errores de validación de archivos y permisos.

    Args:
        message: Mensaje descriptivo del error de validación.

    Examples:
        >>> raise ValidationError("Sin permisos de escritura en /path/to/dir")
    """

    pass
