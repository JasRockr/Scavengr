"""scavengr.utils.validators
==============================

Validadores de archivos y permisos para Scavengr.
Provee funciones para validar existencia de archivos, formatos y permisos.
"""

import os
from pathlib import Path
from typing import Optional

from .exceptions import FileNotFoundError, InvalidFormatError, ValidationError
from .constants import Formats

__all__ = [
    "validate_file_exists",
    "validate_output_format",
    "validate_write_permissions",
    "validate_input_file_format",
]


def validate_file_exists(filepath: str, file_type: str = "archivo") -> Path:
    """Valida que un archivo existe y retorna un objeto Path.

    Args:
        filepath: Ruta del archivo a validar.
        file_type: Tipo de archivo para mensajes de error.

    Returns:
        Path: Objeto Path del archivo validado.

    Raises:
        FileNotFoundError: Si el archivo no existe.

    Examples:
        >>> path = validate_file_exists("schema.dbml", "DBML")
        >>> print(path.exists())
        True
    """
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(str(path_obj), file_type)
    return path_obj


def validate_output_format(filepath: str, format_override: Optional[str] = None) -> str:
    """Valida y determina el formato de salida basado en extensión o parámetro.

    Args:
        filepath: Ruta del archivo de salida.
        format_override: Formato especificado explícitamente (opcional).

    Returns:
        str: Formato validado (csv, excel, json).

    Raises:
        InvalidFormatError: Si el formato no es soportado.

    Examples:
        >>> fmt = validate_output_format("output.xlsx")
        >>> print(fmt)
        excel

        >>> fmt = validate_output_format("output.txt", "csv")
        >>> print(fmt)
        csv
    """
    if format_override:
        if format_override not in Formats.SUPPORTED:
            raise InvalidFormatError(format_override, Formats.SUPPORTED)
        return format_override

    # Detectar por extensión
    extension = Path(filepath).suffix.lower()
    format_map = {
        '.csv': Formats.CSV,
        '.xlsx': Formats.EXCEL,
        '.xls': Formats.EXCEL,
        '.json': Formats.JSON
    }

    detected_format = format_map.get(extension)
    if not detected_format:
        raise InvalidFormatError(
            extension,
            [f"{fmt} ({ext})" for ext, fmt in format_map.items()]
        )

    return detected_format


def validate_write_permissions(filepath: str) -> Path:
    """Valida que se puede escribir en la ruta especificada.

    Args:
        filepath: Ruta donde se quiere escribir.

    Returns:
        Path: Objeto Path validado para escritura.

    Raises:
        ValidationError: Si no se puede escribir en la ubicación.

    Examples:
        >>> path = validate_write_permissions("output/result.xlsx")
        >>> print(path.parent.exists())
        True
    """
    path_obj = Path(filepath)

    # Verificar si el directorio padre existe y es escribible
    parent_dir = path_obj.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise ValidationError(f"No se puede crear el directorio {parent_dir}: {e}")

    if not os.access(parent_dir, os.W_OK):
        raise ValidationError(f"Sin permisos de escritura en {parent_dir}")

    # Si el archivo existe, verificar que se puede sobrescribir
    if path_obj.exists() and not os.access(path_obj, os.W_OK):
        raise ValidationError(f"Sin permisos para sobrescribir {path_obj}")

    return path_obj


def validate_input_file_format(filepath: str) -> Path:
    """Valida que el archivo de entrada tiene un formato soportado.

    Args:
        filepath: Ruta del archivo de entrada.

    Returns:
        Path: Objeto Path del archivo validado.

    Raises:
        ValidationError: Si el formato no es soportado o el archivo está vacío.

    Examples:
        >>> path = validate_input_file_format("schema.dbml")
        >>> print(path.suffix)
        .dbml
    """
    path_obj = validate_file_exists(filepath, "entrada")

    # Validar extensión
    extension = path_obj.suffix.lower()
    supported_extensions = ['.dbml', '.sql', '.ddl']

    if extension not in supported_extensions:
        raise ValidationError(
            f"Formato de archivo no soportado: {extension}. "
            f"Formatos validos: {', '.join(supported_extensions)}"
        )

    # Validar que no esté vacío
    if path_obj.stat().st_size == 0:
        raise ValidationError(f"El archivo {path_obj} esta vacio")

    return path_obj
