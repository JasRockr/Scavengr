"""scavengr.infrastructure.database.base_scanner
=================================================

Módulo base para escaneo de metadatos de bases de datos.
Define interfaces abstractas e implementaciones para diferentes motores.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from scavengr.infrastructure.database.connector import DatabaseConnector


class MetadataScanner(ABC):
    """Clase abstracta base para escaneo de metadata en bases de datos."""

    def __init__(self, connector: DatabaseConnector) -> None:
        """
        Inicializar el escáner con un conector de base de datos.

        Args:
            connector: Conector de base de datos inicializado
        """
        self.connector = connector
        self.connection = connector.connection
        self.cursor = None

    def _execute_query(
        self, query: str, params: Optional[List[Any]] = None
    ) -> List[Tuple[Any, ...]]:
        """
        Ejecuta una consulta en la base de datos y devuelve los resultados.

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)

        Returns:
            List[Tuple[Any, ...]]: Resultados de la consulta
        """
        result = self.connector.execute_query(query, params)
        if isinstance(result, list):
            return result
        return []

    @abstractmethod
    def get_columns(self) -> List[Tuple[Any, ...]]:
        """
        Obtener información de columnas de las tablas.

        Returns:
            List[Tuple[Any, ...]]: Lista de tuplas con información de columnas
                        (schema, table, column_name, data_type, max_length, precision, is_nullable, default_value)
        """
        pass

    @abstractmethod
    def get_primary_keys(self) -> List[Tuple[Any, ...]]:
        """
        Obtener información de claves primarias.

        Returns:
            List[Tuple[Any, ...]]: Lista de tuplas con información de claves primarias
                        (table_name, column_name)
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[Tuple[Any, ...]]:
        """
        Obtener información de claves foráneas.

        Returns:
            List[Tuple[Any, ...]]: Lista de tuplas con información de claves foráneas
                        (constraint_name, table_name, column_name, referenced_table, referenced_column)
        """
        pass

    @abstractmethod
    def get_indexes(self) -> List[Tuple[Any, ...]]:
        """
        Obtener información de índices.

        Returns:
            List[Tuple[Any, ...]]: Lista de tuplas con información de índices
        """
        pass

    def close_cursor(self) -> None:
        """Cerrar el cursor si está abierto."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Obtener información completa del esquema de la base de datos.

        Returns:
            Dict[str, Any]: Diccionario con toda la información del esquema
        """
        columns = self.get_columns()
        primary_keys = self.get_primary_keys()
        foreign_keys = self.get_foreign_keys()
        indexes = self.get_indexes()

        # Construir estructura de datos organizada por tablas
        tables = {}

        # Procesar columnas
        for column in columns:
            (
                schema,
                table,
                column_name,
                dtype,
                max_length,
                precision,
                is_nullable,
                default,
            ) = column

            if table not in tables:
                tables[table] = {
                    "schema": schema,
                    "table": table,
                    "columns": [],
                    "primary_key": [],
                    "foreign_keys": [],
                    "indexes": [],
                }

            tables[table]["columns"].append(
                {
                    "name": column_name,
                    "data_type": dtype,
                    "max_length": max_length,
                    "precision": precision,
                    "is_nullable": is_nullable,
                    "default_value": default,
                }
            )

        # Procesar claves primarias
        for pk_info in primary_keys:
            if len(pk_info) >= 2:
                table, column = pk_info[:2]
                if table in tables:
                    tables[table]["primary_key"].append(column)

        # Procesar claves foráneas
        for fk_info in foreign_keys:
            if len(fk_info) >= 5:
                fk_name, table, column, ref_table, ref_column = fk_info[:5]
                if table in tables:
                    tables[table]["foreign_keys"].append(
                        {
                            "name": fk_name,
                            "column": column,
                            "references_table": ref_table,
                            "references_column": ref_column,
                        }
                    )

        # Procesar índices
        for idx_info in indexes:
            if len(idx_info) >= 3:
                # Adaptamos el formato según el motor de base de datos
                table = idx_info[1] if len(idx_info) > 1 else None
                if table and table in tables:
                    index_name = idx_info[2]
                    index_data = {"name": index_name}

                    # Si hay información adicional disponible
                    if len(idx_info) > 3:
                        if isinstance(idx_info[3], str) and idx_info[3].startswith(
                            "CREATE"
                        ):
                            # PostgreSQL
                            index_data["definition"] = idx_info[3]
                        elif len(idx_info) > 4:
                            # MySQL y otros
                            index_data["columns"] = idx_info[4]
                            if len(idx_info) > 5:
                                index_data["type"] = idx_info[5]

                    tables[table]["indexes"].append(index_data)

        # Construir resultado final
        schema_info = {"tables": [info for info in tables.values()]}

        return schema_info
