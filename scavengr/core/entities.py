"""scavengr.core.entities
=========================

Entidades del dominio.
Define las estructuras de datos fundamentales del sistema.

Entidades:
- Column: Representa una columna en una tabla
- Table: Representa una tabla en el esquema
- Relationship: Representa una relación entre tablas
- Index: Representa un índice en una tabla
- DatabaseSchema: Representa el esquema completo de una base de datos

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Column:
    """Representa una columna en una tabla.

    Attributes:
        name: Nombre de la columna.
        type: Tipo de dato de la columna (VARCHAR, INTEGER, etc.).
        is_pk: True si la columna es clave primaria.
        is_nullable: True si la columna acepta valores NULL.
        default: Valor por defecto de la columna.
        note: Nota o comentario descriptivo sobre la columna.
        ref_table: Tabla referenciada si es clave foránea.
        ref_column: Columna referenciada si es clave foránea.
        attributes: Atributos adicionales de la columna.
    """

    name: str
    type: str
    is_pk: bool = False
    is_nullable: bool = True
    default: Optional[str] = None
    note: Optional[str] = None
    ref_table: Optional[str] = None
    ref_column: Optional[str] = None
    attributes: List[str] = field(default_factory=list)


@dataclass
class Table:
    """Representa una tabla en el esquema.

    Attributes:
        name: Nombre de la tabla.
        columns: Lista de columnas que componen la tabla.
        schema: Nombre del esquema al que pertenece la tabla.
        note: Nota o comentario descriptivo sobre la tabla.
        is_master: True si la tabla es maestra (tablas de referencia).
    """

    name: str
    columns: List[Column] = field(default_factory=list)
    schema: Optional[str] = None
    note: Optional[str] = None
    is_master: bool = False


@dataclass
class Relationship:
    """Representa una relación entre tablas.

    Attributes:
        from_table: Tabla origen de la relación.
        from_column: Columna origen de la relación.
        to_table: Tabla destino de la relación.
        to_column: Columna destino de la relación.
        relationship_type: Tipo de relación (>, <, -, <>).
    """

    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str = ">"


@dataclass
class Index:
    """Representa un índice en una tabla.

    Attributes:
        table: Nombre de la tabla que contiene el índice.
        columns: Lista de columnas que componen el índice.
        name: Nombre del índice (opcional).
        unique: True si el índice es único.
    """

    table: str
    columns: List[str]
    name: Optional[str] = None
    unique: bool = False


@dataclass
class DatabaseSchema:
    """Representa el esquema completo de una base de datos.

    Attributes:
        tables: Lista de tablas del esquema.
        relationships: Lista de relaciones entre tablas.
        indexes: Lista de índices definidos.
        name: Nombre del esquema o base de datos (opcional).
        metadata: Metadata adicional del esquema (opcional).
    """

    tables: List[Table] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    indexes: List[Index] = field(default_factory=list)
    name: Optional[str] = None
    metadata: dict = field(default_factory=dict)
