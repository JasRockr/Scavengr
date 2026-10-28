"""scavengr.infrastructure.formatters.dbml_formatter
====================================================

Formateador de DBML para Scavengr.
Convierte entidades de dominio (DatabaseSchema) a formato DBML.
Implementa IFormatter del dominio.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def _needs_escaping(identifier: str) -> bool:
    """
    Determinar si un identificador DBML necesita escaparse con comillas.

    DBML requiere comillas si el identificador:
    - Contiene espacios
    - Contiene caracteres especiales (excepto _ y números después del primer carácter)
    - Es una palabra reservada
    - Contiene CamelCase (cualquier mayúscula después del primer carácter)

    Args:
        identifier: El nombre a verificar

    Returns:
        bool: True si necesita escaparse
    """
    if not identifier:
        return False

    # Palabras reservadas DBML/SQL
    reserved_words = {
        "table",
        "database",
        "project",
        "ref",
        "indexes",
        "index",
        "pk",
        "note",
        "type",
        "unique",
        "default",
        "null",
        "not",
        "true",
        "false",
        "as",
        "on",
    }

    if identifier.lower() in reserved_words:
        return True

    # Contiene espacios
    if " " in identifier:
        return True

    # Contiene caracteres especiales (excepto _ )
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        return True

    # Contiene CamelCase (mayúscula que no es al inicio)
    if re.search(r"[a-z][A-Z]", identifier):
        return True

    return False


def _escape_identifier(identifier: str) -> str:
    """
    Escapar un identificador DBML si es necesario.

    Args:
        identifier: El nombre a escapar

    Returns:
        str: Identificador escapado con comillas si es necesario
    """
    if _needs_escaping(identifier):
        # Escapar comillas dentro del identificador
        escaped = identifier.replace('"', '\\"')
        return f'"{escaped}"'
    return identifier


def _normalize_postgresql_type(col_type: str) -> str:
    """
    Normalizar tipos PostgreSQL para compatibilidad con DBML.

    PostgreSQL utiliza tipos con espacios (ej: 'timestamp without time zone')
    que deben escaparse o simplificarse en DBML.

    ESTRATEGIA:
    1. Si el tipo tiene espacios, intentar mapear a versión simplificada
    2. Si está mapeado y tiene parámetros, preservarlos
    3. Si no está mapeado pero tiene espacios, escapar todo con comillas
    4. Si no tiene espacios, retornar tal cual

    Args:
        col_type: Tipo PostgreSQL original

    Returns:
        str: Tipo normalizado para DBML
    """
    if not col_type:
        return col_type

    col_type_clean = col_type.strip()
    col_type_lower = col_type_clean.lower()

    # Mapeo de tipos PostgreSQL complejos a versiones simplificadas
    # NOTA: Estos son los tipos base SIN parámetros
    type_mappings = {
        "timestamp without time zone": "timestamp",
        "timestamp with time zone": "timestamptz",
        "character varying": "varchar",
        "double precision": "float8",
    }

    # Si el tipo NO contiene espacios, retornar sin cambios
    if " " not in col_type_lower:
        return col_type_clean

    # El tipo contiene espacios - intentar normalizar
    for original_type, simplified_type in type_mappings.items():
        # Buscar el tipo base (sin parámetros)
        if col_type_lower.startswith(original_type):
            # Extraer parámetros si existen (ej: character varying(100) -> (100))
            params_match = re.search(r"\(.*\)$", col_type_clean)
            params = params_match.group(0) if params_match else ""

            # Retornar tipo simplificado + parámetros
            return simplified_type + params

    # El tipo tiene espacios pero NO está en el mapeo
    # Escapar completamente con comillas
    escaped = col_type_clean.replace('"', '\\"')
    return f'"{escaped}"'


class DBMLFormatter:
    """Formateador para generar archivos DBML a partir de entidades de dominio.

    Convierte DatabaseSchema con sus tablas, columnas, relaciones e índices
    en sintaxis DBML válida conforme a la especificación de dbdiagram.io.
    """

    def __init__(
        self, schema: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializar el formateador con schema y/o metadata.

        Args:
            schema: DatabaseSchema (entidad de dominio principal)
            metadata: Diccionario opcional con metadata adicional (source_system, database_info)
        """
        self.schema = schema
        self.metadata = metadata or {}

    def format(self) -> str:
        """
        Generar el contenido DBML a partir del schema de dominio.

        Returns:
            str: Contenido DBML generado

        Raises:
            ValueError: Si no hay schema disponible
        """
        if not self.schema:
            raise ValueError("Se requiere un DatabaseSchema para generar DBML")

        dbml_content = []

        # Comentario de encabezado
        dbml_content.append("// DBML generado por Scavengr")
        dbml_content.append(
            f"// Fecha: {self.metadata.get('extraction_date', datetime.now().isoformat())}"
        )
        dbml_content.append("")

        # Agregar objeto Project
        source_system = self.metadata.get("source_system", {})
        db_info = self.metadata.get("database_info", {})

        # Calcular métricas desde el schema
        tables_count = len(self.schema.tables)
        columns_count = sum(len(table.columns) for table in self.schema.tables)
        relationships_count = len(self.schema.relationships)
        indexes_count = len(self.schema.indexes)

        dbml_content.append(f'Project "{source_system.get("name", "Unknown")}" {{')
        dbml_content.append(f'  database_type: "{db_info.get("type", "unknown")}"')
        dbml_content.append("  note: '''")
        dbml_content.append(
            f'    # "{db_info.get("database", "Unknown")}" Base de Datos'
        )
        dbml_content.append(f"\t\t* {tables_count} Tablas")
        dbml_content.append(f"\t\t* {columns_count} Campos")
        dbml_content.append(f"    * Relaciones: {relationships_count}")
        dbml_content.append(f"    * Índices: {indexes_count}")
        dbml_content.append(
            f'    * Escaneado por Scavengr - {datetime.now().strftime("%Y-%m-%d")}'
        )
        dbml_content.append("  '''")
        dbml_content.append("}")
        dbml_content.append("")

        # Formatear tablas desde schema
        for table in self.schema.tables:
            dbml_content.extend(self._format_table(table))
            dbml_content.append("")

        # Formatear relaciones
        # for rel in self.schema.relationships:
        #     dbml_content.append(self._format_relationship(rel))

        return "\n".join(dbml_content)

    def _format_table(self, table: Any) -> List[str]:
        """
        Formatear una tabla desde entidad de dominio.

        Args:
            table: Entidad Table del dominio con sus columnas

        Returns:
            List[str]: Líneas DBML de la tabla
        """
        lines = []
        table_name = (
            f"{table.schema}.{table.name}"
            if hasattr(table, "schema") and table.schema
            else table.name
        )
        lines.append(f"Table {table_name} {{")

        # Obtener foreign keys que apuntan desde esta tabla para agregar refs inline
        table_fks = self._get_table_foreign_keys(table)

        # Columnas
        for col in table.columns:
            # [POSTGRESQL FIX] Escapar nombres de columnas con CamelCase o caracteres especiales
            col_name_escaped = _escape_identifier(col.name)

            # [POSTGRESQL FIX] Normalizar tipos de datos PostgreSQL (timestamp without time zone -> timestamp)
            col_type_normalized = _normalize_postgresql_type(col.type)

            col_line = f"  {col_name_escaped} {col_type_normalized}"
            attrs = []

            # Primary Key
            if col.is_pk:
                attrs.append("pk")

            # Nullability
            if not col.is_nullable:
                attrs.append("not null")

            # Foreign Key - Verificar si esta columna es una FK
            if col.name in table_fks:
                ref_table, ref_column = table_fks[col.name]
                attrs.append(f"ref: > {ref_table}.{ref_column}")

            # Default value
            if col.default:
                # Limpiar y formatear el valor por defecto
                default_val = str(col.default).strip()

                # Eliminar saltos de línea y espacios múltiples
                default_val = re.sub(r"\s+", " ", default_val)

                # Eliminar paréntesis externos si los hay
                default_val = re.sub(r"^\((.*)\)$", r"\1", default_val)

                if default_val and default_val.upper() != "NULL":
                    # Para definiciones complejas de SQL Server (CREATE DEFAULT, etc)
                    # extraer solo el valor final después de "AS"
                    if "create default" in default_val.lower():
                        match = re.search(r"\bas\s+(.+)$", default_val, re.IGNORECASE)
                        if match:
                            default_val = match.group(1).strip()

                    attrs.append(f"default: `{default_val}`")

            # Note/Comment
            if hasattr(col, "note") and col.note:
                # Escapar comillas simples en la nota
                note_escaped = str(col.note).replace("'", "\\'")
                attrs.append(f"note: '{note_escaped}'")

            if attrs:
                col_line += f" [{', '.join(attrs)}]"
            lines.append(col_line)

        # Bloque de índices agrupados para esta tabla
        table_indexes = self._get_table_indexes(table)
        if table_indexes:
            lines.append("")
            lines.append("  indexes {")
            # Lista de nombres de columnas de la tabla para ayudas como heurística
            table_col_names = [c.name for c in table.columns]
            # Lista de columnas que son clave primaria
            pk_columns = [c.name for c in table.columns if c.is_pk]

            for idx in table_indexes:
                # Detectar casos donde el scanner pudo haber puesto el tipo (ej. BTREE)
                # en la lista de columnas (caso reportado para MySQL). Normalmente
                # idx.columns contiene los nombres de las columnas que componen el índice.
                columns = []
                detected_type = None

                if idx.columns:
                    # Si alguna entrada en idx.columns es 'BTREE' (o similar), lo tratamos
                    # como indicación del tipo y buscamos los nombres reales de las columnas
                    # por heurística dentro del nombre del índice o comparando con las
                    # columnas de la tabla.
                    cols_upper = [c.upper() for c in idx.columns]
                    if any("BTREE" == c for c in cols_upper) or any(
                        "BTREE" in c for c in cols_upper
                    ):
                        detected_type = "btree"

                        # Primero intentar obtener columnas desde el campo 'name' del índice
                        if idx.name:
                            name_lower = idx.name.lower()
                            # Buscar todas las columnas de la tabla que aparezcan en el nombre
                            # Mantener el orden original de las columnas de la tabla
                            for tcol in table_col_names:
                                if tcol.lower() in name_lower and tcol not in columns:
                                    columns.append(tcol)

                        # Si el índice se llama 'PRIMARY' y no encontramos columnas,
                        # usar las columnas que son clave primaria
                        if not columns and idx.name and idx.name.upper() == "PRIMARY":
                            columns = pk_columns.copy()

                        # Si aún no encontramos columnas por el nombre, intentar tomar cualquier
                        # valor en idx.columns que no sea 'BTREE' y que coincida con nombres
                        # de la tabla
                        if not columns:
                            for raw in idx.columns:
                                if raw and raw.upper() != "BTREE":
                                    candidate = raw.strip()
                                    # Normalizar comillas o paréntesis
                                    candidate = re.sub(
                                        r"^[\(\)'\"]+|[\)\'\"]+$", "", candidate
                                    )
                                    if (
                                        candidate in table_col_names
                                        and candidate not in columns
                                    ):
                                        columns.append(candidate)

                    else:
                        # Caso normal: idx.columns contiene ya los nombres de columnas
                        columns = [c for c in idx.columns]

                # Formatear atributos del índice
                attrs = []
                if detected_type:
                    attrs.append(f"type: {detected_type}")
                if idx.unique:
                    attrs.append("unique")
                if idx.name:
                    attrs.append(f"name: '{idx.name}'")

                # Construir línea: si no se pudieron resolver columnas, mostrar paréntesis vacíos
                columns_str = ", ".join(columns) if columns else ""
                attr_str = f" [{', '.join(attrs)}]" if attrs else ""
                lines.append(f"    ({columns_str}){attr_str}")

            lines.append("  }")

        lines.append("}")
        return lines

    def _get_table_foreign_keys(self, table: Any) -> Dict[str, tuple[Any, Any]]:
        """
        Obtener foreign keys que salen de esta tabla.

        Args:
            table: Entidad Table

        Returns:
            Dict[str, tuple[Any, Any]]: Mapeo de columna_origen -> (tabla_destino, columna_destino)
        """
        fks = {}
        table_name = table.name
        table_schema = table.schema if hasattr(table, "schema") else None

        # Construir nombre completo de tabla (schema.nombre o solo nombre)
        full_table_name = f"{table_schema}.{table_name}" if table_schema else table_name

        # Buscar relaciones en el schema
        if self.schema and hasattr(self.schema, "relationships"):
            for rel in self.schema.relationships:
                # Comparar con nombre completo o solo nombre
                rel_from_table = rel.from_table

                # Comparar si coincide (ya sea con schema o sin)
                if rel_from_table == full_table_name or rel_from_table.endswith(
                    f".{table_name}"
                ):
                    # Usar el nombre completo de la tabla destino si está disponible
                    to_table = rel.to_table
                    fks[rel.from_column] = (to_table, rel.to_column)

        return fks

    def _get_table_indexes(self, table: Any) -> List[Any]:
        """
        Obtener índices de esta tabla desde el schema.

        Args:
            table: Entidad Table

        Returns:
            List[Any]: Lista de índices de la tabla
        """
        table_indexes = []
        table_name = table.name

        # Buscar índices en el schema
        if self.schema and hasattr(self.schema, "indexes"):
            for idx in self.schema.indexes:
                # Comparar solo el nombre de la tabla (sin schema)
                idx_table = idx.table.split(".")[-1] if "." in idx.table else idx.table
                if idx_table == table_name:
                    table_indexes.append(idx)

        return table_indexes

    def _format_relationship(self, rel: Any) -> str:
        """
        Formatear relación desde entidad de dominio.

        Args:
            rel: Entidad Relationship del dominio

        Returns:
            str: Línea DBML de la relación
        """
        # Determinar el tipo de relación (>, <, -, <>, etc.)
        rel_type = getattr(rel, "relationship_type", ">")
        return f"Ref: {rel.from_table}.{rel.from_column} {rel_type} {rel.to_table}.{rel.to_column}"

    def save_to_file(self, output_path: str) -> None:
        """
        Generar y guardar el archivo DBML.

        Args:
            output_path: Ruta donde guardar el archivo DBML
        """
        dbml_content = self.format()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dbml_content)
