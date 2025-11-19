"""Caso de uso para extracción de metadatos de base de datos.

Este módulo implementa la lógica de aplicación para extraer metadatos
de bases de datos y generar archivos DBML, orquestando los componentes
de infraestructura necesarios.

Examples:
    >>> from scavengr.application.extract import ExtractMetadata
    >>> use_case = ExtractMetadata(db_config, generation_config)
    >>> result = use_case.execute("output.dbml")
    >>> print(result.success)
    True

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from scavengr.core.entities import Column, DatabaseSchema, Index, Relationship, Table
from scavengr.infrastructure.cache import MetadataCache
from scavengr.infrastructure.database import create_connector, create_scanner
from scavengr.infrastructure.database.base_scanner import MetadataScanner
from scavengr.infrastructure.database.connector import DatabaseConnector
from scavengr.infrastructure.formatters import DBMLFormatter

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Resultado de la extracción de metadatos.

    Attributes:
        success (bool): Indica si la extracción fue exitosa.
        output_path (str): Ruta del archivo generado.
        tables_count (int): Número de tablas extraídas.
        columns_count (int): Número de columnas extraídas.
        relationships_count (int): Número de relaciones extraídas.
        indexes_count (int): Número de índices extraídos.
        file_size (int): Tamaño del archivo generado en bytes.
        error_message (Optional[str]): Mensaje de error si la extracción falló.
    """

    success: bool
    output_path: str = ""
    tables_count: int = 0
    columns_count: int = 0
    relationships_count: int = 0
    indexes_count: int = 0
    file_size: int = 0
    error_message: Optional[str] = None


class ExtractMetadata:
    """Caso de uso para extraer metadatos de una base de datos.

    Orquesta el proceso completo de:
    1. Conexión a la base de datos
    2. Extracción de metadatos (tablas, columnas, relaciones, índices)
    3. Normalización a entidades de dominio
    4. Generación de archivo DBML

    Args:
        db_config (Dict[str, Any]): Configuración de base de datos.
        generation_config (Dict[str, Any]): Configuración de generación.

    Examples:
        >>> db_config = {
        ...     'type': 'postgresql',
        ...     'host': 'localhost',
        ...     'database': 'mydb',
        ...     'user': 'user',
        ...     'password': 'pass'
        ... }
        >>> gen_config = {'source_system': {'name': 'MySystem'}}
        >>> use_case = ExtractMetadata(db_config, gen_config)
        >>> result = use_case.execute("output.dbml")
    """

    def __init__(
        self,
        db_config: Dict[str, Any],
        generation_config: Optional[Dict[str, Any]] = None,
        use_cache: bool = False,
        force_refresh: bool = False,
    ) -> None:
        """Inicializa el caso de uso de extracción.

        Args:
            db_config (Dict[str, Any]): Configuración de conexión a BD.
            generation_config (Optional[Dict[str, Any]]): Configuración de generación.
            use_cache (bool): Si True, usa caching de metadatos. Default: False.
            force_refresh (bool): Si True, invalida cache existente. Default: False.
        """
        self.db_config = db_config
        self.generation_config = generation_config or {}
        self.connector: Optional[DatabaseConnector] = None
        self.scanner: Optional[MetadataScanner] = None
        self.use_cache = use_cache
        self.force_refresh = force_refresh
        self.cache: Optional[MetadataCache] = None

        # Inicializar cache si está habilitado
        if self.use_cache:
            self.cache = MetadataCache(
                cache_dir=".scavengr_cache", ttl_hours=24, serialization="pickle"
            )

    def execute(self, output_path: str) -> ExtractionResult:
        """Ejecuta la extracción de metadatos.

        Args:
            output_path (str): Ruta donde guardar el archivo DBML.

        Returns:
            ExtractionResult: Resultado de la operación con estadísticas.

        Raises:
            ConnectionError: Si no se puede conectar a la base de datos.
            ValueError: Si la configuración es inválida.
        """
        try:
            logger.info("[EXTRACT] Iniciando extracción de metadatos...")
            logger.debug(
                f"[DEBUG] Configuración BD: {self.db_config['type']} en {self.db_config['host']}"
            )
            logger.debug(f"[DEBUG] Archivo destino: {output_path}")
            logger.debug(
                f"[DEBUG] Cache: {'habilitado' if self.use_cache else 'deshabilitado'}, "
                f"Force refresh: {self.force_refresh}"
            )

            # Paso 0: Intentar cargar desde cache
            raw_metadata: Optional[Dict[str, Any]] = None
            if self.use_cache and self.cache:
                logger.debug("[DEBUG] Paso 0: Verificando cache...")
                raw_metadata = self.cache.load(self.db_config, self.force_refresh)
                if raw_metadata:
                    logger.info(
                        "[CACHE] Metadatos cargados desde cache (sin conexión a BD)"
                    )

            # Si no hay cache válido, extraer de BD
            if raw_metadata is None:
                # Paso 1: Conectar a la base de datos
                logger.debug("[DEBUG] Paso 1: Conectando a base de datos...")
                self._connect()
                logger.debug("[DEBUG] Conexión establecida exitosamente")

                # Paso 2: Extraer metadatos raw
                logger.debug("[DEBUG] Paso 2: Extrayendo metadatos raw...")
                raw_metadata = self._extract_raw_metadata()

                # Guardar en cache si está habilitado
                if self.use_cache and self.cache:
                    logger.debug("[DEBUG] Guardando metadatos en cache...")
                    self.cache.save(self.db_config, raw_metadata)

            # Contar tablas únicas desde las columnas si no hay tables explícitas
            tables_count = len(raw_metadata.get("tables", [])) or len(
                set(col[1] for col in raw_metadata.get("columns", []))
            )
            logger.debug(
                f"[DEBUG] Metadatos procesados: {tables_count} tablas, {len(raw_metadata.get('columns', []))} columnas"
            )

            # Paso 3: Normalizar a entidades de dominio
            logger.debug("[DEBUG] Paso 3: Normalizando a entidades de dominio...")
            schema = self._normalize_to_domain_entities(raw_metadata)
            logger.debug(
                f"[DEBUG] Esquema normalizado: {len(schema.tables)} tablas, {sum(len(t.columns) for t in schema.tables)} columnas"
            )

            # Paso 4: Generar archivo DBML
            self._generate_dbml(schema, output_path)

            # Paso 5: Cerrar conexión
            self._disconnect()

            # Paso 6: Construir resultado
            file_size = os.path.getsize(output_path)

            result = ExtractionResult(
                success=True,
                output_path=output_path,
                tables_count=len(schema.tables),
                columns_count=sum(len(table.columns) for table in schema.tables),
                relationships_count=len(schema.relationships),
                indexes_count=len(schema.indexes),
                file_size=file_size,
            )

            logger.info(
                f"[SUCCESS] Extracción completada: "
                f"{result.tables_count} tablas, "
                f"{result.columns_count} columnas, "
                f"{result.relationships_count} relaciones"
            )

            return result

        except Exception as e:
            logger.error(f"[ERROR] Error en extracción: {str(e)}")
            self._disconnect()  # Asegurar desconexión incluso en error

            return ExtractionResult(success=False, error_message=str(e))

    def _connect(self) -> None:
        """Establece conexión a la base de datos.

        Raises:
            ConnectionError: Si no se puede establecer la conexión.
        """
        logger.info(f"[INFO] Conectando a {self.db_config['type']}...")

        # Crear conector
        self.connector = create_connector(self.db_config)

        # Establecer conexión
        self.connector.connect()

        # Crear scanner
        self.scanner = create_scanner(self.connector)

        logger.info("[INFO] Conexión establecida exitosamente")

    def _extract_raw_metadata(self) -> Dict[str, Any]:
        """Extrae metadatos raw de la base de datos.

        Returns:
            Dict[str, Any]: Metadatos en formato raw (tuplas).
        """
        logger.info("[INFO] Extrayendo metadatos...")

        if not self.scanner:
            raise RuntimeError("Scanner no inicializado")

        # Extraer cada tipo de metadata
        tables_data: List[Any] = (
            self.scanner.get_tables() if hasattr(self.scanner, "get_tables") else []
        )
        columns_data = self.scanner.get_columns()
        foreign_keys_data = self.scanner.get_foreign_keys()
        primary_keys_data: List[Any] = (
            self.scanner.get_primary_keys()
            if hasattr(self.scanner, "get_primary_keys")
            else []
        )
        indexes_data: List[Any] = (
            self.scanner.get_indexes() if hasattr(self.scanner, "get_indexes") else []
        )

        logger.info(
            f"[STATS] Encontradas: "
            f"{len(set(col[1] for col in columns_data))} tablas, "
            f"{len(columns_data)} columnas, "
            f"{len(foreign_keys_data)} relaciones, "
            f"{len(indexes_data)} índices"
        )

        return {
            "tables": tables_data,
            "columns": columns_data,
            "foreign_keys": foreign_keys_data,
            "primary_keys": primary_keys_data,
            "indexes": indexes_data,
        }

    def _normalize_to_domain_entities(
        self, raw_metadata: Dict[str, Any]
    ) -> DatabaseSchema:
        """Normaliza metadatos raw a entidades de dominio.

        Args:
            raw_metadata (Dict[str, Any]): Metadatos en formato raw.

        Returns:
            DatabaseSchema: Esquema normalizado con entidades de dominio.
        """
        logger.info("[INFO] Normalizando metadatos a entidades de dominio...")

        # Agrupar columnas por tabla
        tables_dict: Dict[str, Dict[str, Any]] = {}
        for col_data in raw_metadata["columns"]:
            schema_name = col_data[0]
            table_name = col_data[1]
            col_full_table_name = f"{schema_name}.{table_name}"

            if col_full_table_name not in tables_dict:
                tables_dict[col_full_table_name] = {
                    "name": table_name,
                    "schema": schema_name,
                    "columns": [],
                }

            # Crear entidad Column
            # col_data tiene: [0]schema, [1]table, [2]column_name, [3]data_type,
            #                 [4]max_length, [5]precision, [6]is_nullable, [7]default_value
            column = Column(
                name=col_data[2],
                type=col_data[3],
                is_nullable=(col_data[6] == "YES") if len(col_data) > 6 else True,
                is_pk=False,  # Se actualiza después
                default=col_data[7] if len(col_data) > 7 else None,
            )

            tables_dict[col_full_table_name]["columns"].append(column)

        # Marcar primary keys
        # NOTA: Los scanners retornan formatos diferentes:
        # - MSSQL/MySQL: 2 campos [table_name, column_name]
        # - PostgreSQL: 3 campos [schema_name, table_name, column_name]
        for pk_data in raw_metadata["primary_keys"]:
            full_table_name: Optional[str] = None
            if len(pk_data) == 2:
                # MSSQL/MySQL format - buscar tabla en cualquier schema
                table_name = pk_data[0]
                column_name = pk_data[1]
                # Buscar la tabla en tables_dict
                for key in tables_dict.keys():
                    if key.endswith(f".{table_name}"):
                        full_table_name = key
                        break
            else:
                # PostgreSQL format
                schema_name = pk_data[0]
                table_name = pk_data[1]
                column_name = pk_data[2]
                full_table_name = f"{schema_name}.{table_name}"

            if full_table_name and full_table_name in tables_dict:
                for col in tables_dict[full_table_name]["columns"]:
                    if col.name == column_name:
                        col.is_pk = True

        # Crear entidades Table
        tables = [
            Table(
                name=table_info["name"],
                columns=table_info["columns"],
                schema=table_info["schema"],
            )
            for table_info in tables_dict.values()
        ]

        # Crear entidades Relationship
        # fk_data tiene: [0]constraint_name, [1]table_name, [2]column_name,
        #                [3]referenced_table, [4]referenced_column
        # Incluir el schema completo en las referencias para DBML
        relationships = []
        for fk_data in raw_metadata["foreign_keys"]:
            from_table_name = fk_data[1]
            to_table_name = fk_data[3]
            from_column_name = fk_data[2]
            to_column_name = fk_data[4]

            # Buscar el full_table_name con schema para from_table
            from_table_full = from_table_name
            for key in tables_dict.keys():
                if key.endswith(f".{from_table_name}"):
                    from_table_full = key
                    break

            # Buscar el full_table_name con schema para to_table
            to_table_full = to_table_name
            for key in tables_dict.keys():
                if key.endswith(f".{to_table_name}"):
                    to_table_full = key
                    break

            # FILTRO: Evitar autorreferencias al mismo endpoint exacto (causa "Two endpoints are the same" en dbdiagram.io)
            # Solo filtrar cuando TABLA y COLUMNA son EXACTAMENTE iguales: tabla.columna [ref: > tabla.columna]
            # NOTA: Relaciones jerárquicas válidas (ej. padre_id -> id, vice_departamento -> departamento) se mantienen
            if (
                from_table_full == to_table_full
                and from_column_name.lower() == to_column_name.lower()
            ):
                logger.warning(
                    f"[EXTRACT] Autorreferencia al mismo endpoint exacto ignorada (DBML incompatible): "
                    f"{from_table_full}.{from_column_name} -> {to_table_full}.{to_column_name}"
                )
                continue

            relationships.append(
                Relationship(
                    from_table=from_table_full,
                    from_column=from_column_name,
                    to_table=to_table_full,
                    to_column=to_column_name,
                )
            )

        # Crear entidades Index
        # NOTA: Los scanners retornan formatos diferentes:
        # - PostgreSQL: 5 campos [schema_name, table_name, index_name, index_definition, is_unique]
        # - MSSQL/MySQL: 6 campos [schema_name, table_name, index_name, index_type, is_unique, indexed_columns]
        indexes = []
        for idx_data in raw_metadata["indexes"]:
            if len(idx_data) >= 6:
                # MSSQL/MySQL format con indexed_columns
                index_type = idx_data[3] if idx_data[3] else None
                # Normalizar index_type a formato estándar
                if index_type and isinstance(index_type, str):
                    if index_type.upper() in ("1", "BTREE"):
                        index_type = "btree"
                    elif index_type.upper() in ("2", "HASH"):
                        index_type = "hash"
                    else:
                        index_type = index_type.lower()

                indexes.append(
                    Index(
                        name=idx_data[2],
                        table=idx_data[1],
                        columns=idx_data[5].split(", ") if idx_data[5] else [],
                        unique=bool(idx_data[4]),
                        index_type=index_type,
                    )
                )
            else:
                # PostgreSQL format con index_definition
                # Extraer columnas desde la definición: "CREATE INDEX ... (col1, col2, ...)"
                index_def = idx_data[3] if len(idx_data) > 3 else ""
                columns = self._extract_columns_from_index_definition(index_def)

                indexes.append(
                    Index(
                        name=idx_data[2],
                        table=idx_data[1],
                        columns=columns,
                        unique=bool(idx_data[4]) if len(idx_data) > 4 else False,
                        index_type=None,  # PostgreSQL type será extraído desde la definición si se necesita
                    )
                )

        # Crear DatabaseSchema
        schema = DatabaseSchema(
            name=self.db_config.get("name", "unknown"),
            tables=tables,
            relationships=relationships,
            indexes=indexes,
            metadata={
                "source_system": self.generation_config.get("source_system", {}),
                "database_info": {
                    "type": self.db_config["type"],
                    "host": self.db_config["host"],
                    "database": self.db_config["name"],
                },
                "extraction_date": datetime.now().isoformat(),
            },
        )

        return schema

    def _extract_columns_from_index_definition(self, index_def: str) -> List[str]:
        """Extraer columnas desde la definición de índice de PostgreSQL.

        La definición tiene formato:
        CREATE INDEX idx_name ON schema.table USING btree (column1, column2, ...)

        Args:
            index_def (str): Definición SQL del índice.

        Returns:
            List[str]: Lista de nombres de columnas.
        """
        if not index_def:
            return []

        # Buscar el contenido entre paréntesis al final
        match = re.search(r"\(([^)]+)\)(?:\s*WHERE)?", index_def)
        if match:
            columns_str = match.group(1)
            # Dividir por coma y limpiar espacios
            columns = [col.strip() for col in columns_str.split(",")]
            # Eliminar cualquier especificación adicional (ASC, DESC, COLLATE, etc)
            cleaned_columns: List[str] = []
            for col in columns:
                # Tomar solo el nombre de la columna (primera palabra)
                col_parts = col.split()
                if col_parts:
                    cleaned_columns.append(col_parts[0])
            return cleaned_columns

        return []

    def _generate_dbml(self, schema: DatabaseSchema, output_path: str) -> None:
        """Genera archivo DBML desde el esquema de dominio.

        Args:
            schema (DatabaseSchema): Esquema normalizado.
            output_path (str): Ruta del archivo de salida.
        """
        logger.info("[INFO] Generando archivo DBML...")

        # Crear directorio si no existe
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Generar DBML usando formatter con entidad de dominio
        formatter = DBMLFormatter(schema=schema, metadata=schema.metadata)
        dbml_content = formatter.format()

        # Guardar archivo
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dbml_content)

        logger.info(f"[INFO] Archivo DBML guardado: {output_path}")

    def _disconnect(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.connector:
            try:
                self.connector.close()
                logger.info("[INFO] Conexión cerrada")
            except Exception as e:
                logger.warning(f"[WARNING] Error al cerrar conexión: {str(e)}")
