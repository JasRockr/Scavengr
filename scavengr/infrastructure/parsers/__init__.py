"""scavengr.infrastructure.parsers
====================================

Parsers de formatos de archivos.
Implementa IParser para diferentes formatos (DBML, SQL DDL, etc.).
"""

from scavengr.infrastructure.parsers.dbml_parser import DBMLParser

__all__ = [
    "DBMLParser",
]
