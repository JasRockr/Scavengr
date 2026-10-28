"""
Módulo para el análisis de archivos DBML.
Parsea archivos DBML y genera una estructura de datos que representa el esquema.
Este módulo combina las mejores características para procesar archivos DBML de manera robusta.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

import os
import re
from typing import Any, Dict, List, Optional

from scavengr.core.entities import Column, Relationship, Table


class DBMLParser:
    """
    Clase para parsear archivos DBML y generar una estructura de datos representativa.
    """

    def __init__(self, dbml_file_path: str) -> None:
        """
        Inicializa el parser con la ruta al archivo DBML.

        Args:
            dbml_file_path: Ruta al archivo DBML
        """
        self.dbml_file_path = dbml_file_path
        self.tables: Dict[str, Any] = {}
        self.relationships: List[Any] = []
        self.indexes: List[Any] = []

    def parse(self) -> Dict[str, Any]:
        """
        Parsea el archivo DBML y devuelve un diccionario con la estructura del esquema.
        Versión robusta con mejor validación y manejo de errores.

        Returns:
            Dict[str, Any]: Estructura del esquema de la base de datos

        Raises:
            FileNotFoundError: Si el archivo DBML no existe
            ValueError: Si el formato del archivo DBML es inválido
        """
        if not os.path.exists(self.dbml_file_path):
            raise FileNotFoundError(
                f"Archivo DBML no encontrado: {self.dbml_file_path}"
            )

        try:
            with open(self.dbml_file_path, "r", encoding="utf-8") as file:
                dbml_content = file.read()

            if not dbml_content.strip():
                raise ValueError(f"El archivo DBML está vacío: {self.dbml_file_path}")

            # Parsear tablas
            self._parse_tables(dbml_content)

            # Parsear relaciones
            self._parse_relationships(dbml_content)

            # Identificar tablas maestras basadas en relaciones
            self._identify_master_tables()

            # Convertir a lista de objetos Table para compatibilidad
            tables_list = list(self.tables.values())

            # Construir resultado con formato esperado por data_generator
            schema = {"tables": tables_list, "relationships": self.relationships}

            return schema
        except Exception as e:
            raise ValueError(f"Error al parsear el archivo DBML: {str(e)}")

    def _parse_tables(self, content: str) -> None:
        """
        Parsea las definiciones de tablas con mejor manejo de atributos.
        Versión robusta que combina ambas implementaciones.

        Args:
            content: Contenido del archivo DBML
        """
        # Regex robusto para encontrar bloques de tablas (incluyendo esquema.tabla)
        table_pattern = r"Table\s+([\w\.]+)\s*\{(.*?)\}"
        table_matches = re.findall(table_pattern, content, re.DOTALL)

        for table_name, table_content in table_matches:
            # Crear la tabla
            table = Table(name=table_name)

            # Parsear columnas con lógica robusta de /src
            columns = self._parse_columns(table_content, table_name)
            table.columns = columns

            # Parsear índices
            indexes = self._parse_indexes(table_content, table_name)
            table.indexes = indexes

            # Parsear nota de tabla
            table_note = self._parse_table_note(table_content)
            table.note = table_note

            self.tables[table_name] = table

    def _parse_columns(self, table_content: str, table_name: str) -> List[Column]:
        """
        Parsea las columnas con mejor detección de atributos y referencias.
        Combina la lógica robusta de ambas versiones.

        Args:
            table_content: Contenido de la definición de la tabla
            table_name: Nombre de la tabla

        Returns:
            List[Column]: Lista de columnas de la tabla
        """
        columns = []
        # Patrón robusto para capturar atributos complejos (de /src)
        column_pattern = r"(\w+)\s+([\w\(\)\,]+)\s*(?:\[(.*?)\])?"

        for line in table_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            # Saltar bloques de índices (se parsean por separado)
            if line.startswith("indexes"):
                break

            match = re.match(column_pattern, line)
            if match:
                name, data_type, attributes_str = match.groups()
                attributes_str = attributes_str or ""

                # Parsear atributos individuales
                attributes = [
                    attr.strip() for attr in attributes_str.split(",") if attr.strip()
                ]

                # Extraer referencia si existe (lógica de /src)
                ref_match = re.search(r"ref:\s*[<>-]*\s*([\w\.]+)", attributes_str)
                ref_table, ref_column = None, None
                if ref_match:
                    ref_full = ref_match.group(1)
                    if "." in ref_full:
                        # Manejar referencias con esquema: schema.table.column
                        parts = ref_full.split(".")
                        if len(parts) == 3:
                            # schema.table.column → usar table.column como ref_table
                            ref_table = f"{parts[0]}.{parts[1]}"
                            ref_column = parts[2]
                        elif len(parts) == 2:
                            # table.column
                            ref_table, ref_column = parts
                        else:
                            # Más de 3 partes o formato inválido, tomar últimos 2
                            ref_table = ".".join(parts[:-1])
                            ref_column = parts[-1]
                    else:
                        # Auto-referencia
                        ref_table = table_name
                        ref_column = ref_full

                column = Column(
                    name=name.strip(),
                    type=data_type.strip(),
                    is_pk="pk" in attributes_str
                    or "primary key" in attributes_str.lower(),
                    is_nullable="not null" not in attributes_str.lower(),
                    note=None,
                    ref_table=ref_table,
                    ref_column=ref_column,
                    attributes=attributes,  # Mantenemos para compatibilidad
                )
                columns.append(column)

        return columns

    def _parse_indexes(self, table_content: str, table_name: str) -> List[Any]:
        """
        Parsea los bloques de índices en una tabla.

        Args:
            table_content: Contenido de la definición de la tabla
            table_name: Nombre de la tabla

        Returns:
            List[Any]: Lista de objetos Index
        """
        from scavengr.core.entities import Index

        indexes = []
        in_indexes_block = False

        for line in table_content.split("\n"):
            line = line.strip()

            # Detectar inicio de bloque indexes
            if line.startswith("indexes"):
                in_indexes_block = True
                continue

            # Detectar fin de bloque indexes
            if in_indexes_block and line == "}":
                break

            # Parsear índice dentro del bloque
            if in_indexes_block and line and not line.startswith("//"):
                # Patrón: (col1, col2) [type: btree, name: 'idx_name', unique]
                # O simplemente: () [type: btree]
                index_match = re.match(r"\((.*?)\)\s*(?:\[(.*?)\])?", line)

                if index_match:
                    columns_str, attrs_str = index_match.groups()

                    # Parsear columnas
                    columns_list = []
                    if columns_str.strip():
                        columns_list = [
                            col.strip() for col in columns_str.split(",") if col.strip()
                        ]

                    # Parsear atributos
                    index_type = None
                    index_name = None
                    is_unique = False

                    if attrs_str:
                        # Buscar type
                        type_match = re.search(r"type:\s*(\w+)", attrs_str)
                        if type_match:
                            index_type = type_match.group(1).upper()

                        # Buscar name
                        name_match = re.search(
                            r"name:\s*['\"]([^'\"]+)['\"]", attrs_str
                        )
                        if name_match:
                            index_name = name_match.group(1)

                        # Buscar unique
                        if "unique" in attrs_str.lower():
                            is_unique = True

                    # Crear objeto Index
                    index = Index(
                        table=table_name,
                        columns=columns_list,
                        name=index_name,
                        unique=is_unique,
                        index_type=index_type,
                    )
                    indexes.append(index)

        return indexes

    def _parse_table_note(self, table_content: str) -> Optional[str]:
        """
        Extraer comentarios de la tabla.

        Args:
            table_content: Contenido de la definición de la tabla

        Returns:
            Optional[str]: Comentario de la tabla si existe
        """
        # Buscar comentarios de tabla
        note_match = re.search(r"//\s*(.*?)$", table_content, re.MULTILINE)
        return note_match.group(1).strip() if note_match else None

    def _parse_relationships(self, content: str) -> None:
        """
        Parsea las relaciones con mejor detección de patrones.
        Versión robusta que maneja múltiples formatos.

        Args:
            content: Contenido del archivo DBML
        """
        # Buscar relaciones explícitas con sintaxis Ref: (lógica de /src)
        ref_pattern = r"Ref:\s*([\w\.]+)\s*([<>-]+)\s*([\w\.]+)"
        ref_matches = re.findall(ref_pattern, content, re.MULTILINE | re.IGNORECASE)

        for from_ref, rel_type, to_ref in ref_matches:
            # Parsear referencia FROM con soporte para schema.table.column
            if "." in from_ref:
                parts = from_ref.split(".")
                if len(parts) == 3:
                    from_table = f"{parts[0]}.{parts[1]}"
                    from_column = parts[2]
                elif len(parts) == 2:
                    from_table, from_column = parts
                else:
                    from_table = ".".join(parts[:-1])
                    from_column = parts[-1]
            else:
                from_table = None
                from_column = from_ref

            # Parsear referencia TO con soporte para schema.table.column
            if "." in to_ref:
                parts = to_ref.split(".")
                if len(parts) == 3:
                    to_table = f"{parts[0]}.{parts[1]}"
                    to_column = parts[2]
                elif len(parts) == 2:
                    to_table, to_column = parts
                else:
                    to_table = ".".join(parts[:-1])
                    to_column = parts[-1]
            else:
                to_table = None
                to_column = to_ref

            relationship = Relationship(
                from_table=from_table or "",
                from_column=from_column or "",
                to_table=to_table or "",
                to_column=to_column or "",
                relationship_type=rel_type,
            )
            self.relationships.append(relationship)

    def _identify_master_tables(self) -> None:
        """
        Identificar tablas maestras basadas en relaciones.
        Lógica robusta de /src.
        """
        # Tablas que son referenciadas por otras
        referenced_tables = set()
        for rel in self.relationships:
            if rel.to_table:
                referenced_tables.add(rel.to_table)

        # Marcar tablas como maestras
        for table_name in referenced_tables:
            if table_name in self.tables:
                self.tables[table_name].is_master = True

            # Verificar si tiene columnas PK que son referenciadas
            if table_name in self.tables:
                for col in self.tables[table_name].columns:
                    if col.is_pk and any(
                        rel.to_table == table_name and rel.to_column == col.name
                        for rel in self.relationships
                    ):
                        self.tables[table_name].is_master = True
                        break
