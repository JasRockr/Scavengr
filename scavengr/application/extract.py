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
Date: 2025-01-06
Version: 1.0.0
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from scavengr.infrastructure.database import create_connector, create_scanner
from scavengr.infrastructure.formatters import DBMLFormatter
from scavengr.core.entities import DatabaseSchema, Table, Column, Relationship, Index

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
        generation_config: Optional[Dict[str, Any]] = None
    ):
        """Inicializa el caso de uso de extracción.
        
        Args:
            db_config (Dict[str, Any]): Configuración de conexión a BD.
            generation_config (Optional[Dict[str, Any]]): Configuración de generación.
        """
        self.db_config = db_config
        self.generation_config = generation_config or {}
        self.connector = None
        self.scanner = None
    
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
            
            # Paso 1: Conectar a la base de datos
            self._connect()
            
            # Paso 2: Extraer metadatos raw
            raw_metadata = self._extract_raw_metadata()
            
            # Paso 3: Normalizar a entidades de dominio
            schema = self._normalize_to_domain_entities(raw_metadata)
            
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
                file_size=file_size
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
            
            return ExtractionResult(
                success=False,
                error_message=str(e)
            )
    
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
        
        # Extraer cada tipo de metadata
        tables_data = (
            self.scanner.get_tables()
            if hasattr(self.scanner, 'get_tables')
            else []
        )
        columns_data = self.scanner.get_columns()
        foreign_keys_data = self.scanner.get_foreign_keys()
        primary_keys_data = (
            self.scanner.get_primary_keys()
            if hasattr(self.scanner, 'get_primary_keys')
            else []
        )
        indexes_data = (
            self.scanner.get_indexes()
            if hasattr(self.scanner, 'get_indexes')
            else []
        )
        
        logger.info(
            f"[STATS] Encontradas: "
            f"{len(set(col[1] for col in columns_data))} tablas, "
            f"{len(columns_data)} columnas, "
            f"{len(foreign_keys_data)} relaciones, "
            f"{len(indexes_data)} índices"
        )
        
        return {
            'tables': tables_data,
            'columns': columns_data,
            'foreign_keys': foreign_keys_data,
            'primary_keys': primary_keys_data,
            'indexes': indexes_data
        }
    
    def _normalize_to_domain_entities(
        self,
        raw_metadata: Dict[str, Any]
    ) -> DatabaseSchema:
        """Normaliza metadatos raw a entidades de dominio.
        
        Args:
            raw_metadata (Dict[str, Any]): Metadatos en formato raw.
            
        Returns:
            DatabaseSchema: Esquema normalizado con entidades de dominio.
        """
        logger.info("[INFO] Normalizando metadatos a entidades de dominio...")
        
        # Agrupar columnas por tabla
        tables_dict = {}
        for col_data in raw_metadata['columns']:
            schema_name = col_data[0]
            table_name = col_data[1]
            full_table_name = f"{schema_name}.{table_name}"
            
            if full_table_name not in tables_dict:
                tables_dict[full_table_name] = {
                    'name': table_name,
                    'schema': schema_name,
                    'columns': []
                }
            
            # Crear entidad Column
            # col_data tiene: [0]schema, [1]table, [2]column_name, [3]data_type,
            #                 [4]max_length, [5]precision, [6]is_nullable, [7]default_value
            column = Column(
                name=col_data[2],
                type=col_data[3],
                is_nullable=(col_data[6] == 'YES') if len(col_data) > 6 else True,
                is_pk=False,  # Se actualiza después
                default=col_data[7] if len(col_data) > 7 else None
            )
            
            tables_dict[full_table_name]['columns'].append(column)
        
        # Marcar primary keys
        # NOTA: Los scanners retornan formatos diferentes:
        # - MSSQL/MySQL: 2 campos [table_name, column_name]
        # - PostgreSQL: 3 campos [schema_name, table_name, column_name]
        for pk_data in raw_metadata['primary_keys']:
            if len(pk_data) == 2:
                # MSSQL/MySQL format - buscar tabla en cualquier schema
                table_name = pk_data[0]
                column_name = pk_data[1]
                # Buscar la tabla en tables_dict
                full_table_name = None
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
                for col in tables_dict[full_table_name]['columns']:
                    if col.name == column_name:
                        col.is_pk = True
        
        # Crear entidades Table
        tables = [
            Table(
                name=table_info['name'],
                columns=table_info['columns'],
                schema=table_info['schema']
            )
            for table_info in tables_dict.values()
        ]
        
        # Crear entidades Relationship
        # fk_data tiene: [0]constraint_name, [1]table_name, [2]column_name,
        #                [3]referenced_table, [4]referenced_column
        relationships = [
            Relationship(
                from_table=fk_data[1],
                from_column=fk_data[2],
                to_table=fk_data[3],
                to_column=fk_data[4]
            )
            for fk_data in raw_metadata['foreign_keys']
        ]
        
        # Crear entidades Index
        # NOTA: Los scanners retornan formatos diferentes:
        # - PostgreSQL: 5 campos [schema_name, table_name, index_name, index_definition, is_unique]
        # - MSSQL/MySQL: 6 campos [schema_name, table_name, index_name, index_type, is_unique, indexed_columns]
        indexes = []
        for idx_data in raw_metadata['indexes']:
            if len(idx_data) >= 6:
                # MSSQL/MySQL format con indexed_columns
                indexes.append(Index(
                    name=idx_data[2],
                    table=idx_data[1],
                    columns=idx_data[5].split(', ') if idx_data[5] else [],
                    unique=bool(idx_data[4])
                ))
            else:
                # PostgreSQL format con index_definition
                # Extraer columnas desde la definición: "CREATE INDEX ... (col1, col2, ...)"
                index_def = idx_data[3] if len(idx_data) > 3 else ""
                columns = self._extract_columns_from_index_definition(index_def)
                
                indexes.append(Index(
                    name=idx_data[2],
                    table=idx_data[1],
                    columns=columns,
                    unique=bool(idx_data[4]) if len(idx_data) > 4 else False
                ))
        
        # Crear DatabaseSchema
        schema = DatabaseSchema(
            name=self.db_config.get('name', 'unknown'),
            tables=tables,
            relationships=relationships,
            indexes=indexes,
            metadata={
                'source_system': self.generation_config.get('source_system', {}),
                'database_info': {
                    'type': self.db_config['type'],
                    'host': self.db_config['host'],
                    'database': self.db_config['name']
                },
                'extraction_date': datetime.now().isoformat()
            }
        )
        
        return schema
    
    def _extract_columns_from_index_definition(self, index_def: str) -> List[str]:
        """
        Extraer columnas desde la definición de índice de PostgreSQL.
        
        La definición tiene formato:
        CREATE INDEX idx_name ON schema.table USING btree (column1, column2, ...)
        
        Args:
            index_def: Definición SQL del índice
            
        Returns:
            List[str]: Lista de nombres de columnas
        """
        if not index_def:
            return []
        
        # Buscar el contenido entre paréntesis al final
        match = re.search(r'\(([^)]+)\)(?:\s*WHERE)?', index_def)
        if match:
            columns_str = match.group(1)
            # Dividir por coma y limpiar espacios
            columns = [col.strip() for col in columns_str.split(',')]
            # Eliminar cualquier especificación adicional (ASC, DESC, COLLATE, etc)
            cleaned_columns = []
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
        with open(output_path, 'w', encoding='utf-8') as f:
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
