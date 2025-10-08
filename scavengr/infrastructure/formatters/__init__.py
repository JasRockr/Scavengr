"""scavengr.infrastructure.formatters
======================================

Formateadores de salida.
Transforma entidades del dominio a formatos específicos (DBML, JSON, etc.).
"""

from scavengr.infrastructure.formatters.dbml_formatter import DBMLFormatter

__all__ = [
    "DBMLFormatter",
]
