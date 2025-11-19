"""scavengr.utils
==================

Utilidades compartidas para el proyecto Scavengr.
Incluye helpers, logging, validadores, excepciones y constantes.
"""

# Constantes
from .constants import Commands, Formats, Messages

# Excepciones
from .exceptions import (
    FileNotFoundError,
    InvalidFormatError,
    ProcessingError,
    ScavengrError,
    ValidationError,
)

# Logging
from .logging_config import (
    DEFAULT_LOG_FORMAT,
    ColorFormatter,
    setup_logging,
    supports_color,
)

# UI Helpers
from .ui_helpers import provide_user_feedback

# Validadores
from .validators import (
    validate_file_exists,
    validate_input_file_format,
    validate_output_format,
    validate_write_permissions,
)

__all__ = [
    # Logging
    "setup_logging",
    "ColorFormatter",
    "supports_color",
    "DEFAULT_LOG_FORMAT",
    # Excepciones
    "ScavengrError",
    "FileNotFoundError",
    "InvalidFormatError",
    "ProcessingError",
    "ValidationError",
    # Constantes
    "Commands",
    "Formats",
    "Messages",
    # Validadores
    "validate_file_exists",
    "validate_output_format",
    "validate_write_permissions",
    "validate_input_file_format",
    # UI Helpers
    "provide_user_feedback",
]
