"""scavengr.infrastructure.database.scanners
=============================================

Implementaciones específicas de escáneres de metadatos para diferentes motores de bases de datos.
Incluye SQL Server, MySQL y PostgreSQL.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

from typing import List, Tuple

from scavengr.infrastructure.database.base_scanner import MetadataScanner
from scavengr.infrastructure.database.connector import (
    MSSQLConnector,
    MySQLConnector,
    PostgreSQLConnector
)


class MSSQLScanner(MetadataScanner):
    """Escáner de metadatos específico para SQL Server."""
    
    def get_columns(self) -> List[Tuple]:
        """
        Obtener información de columnas en SQL Server.
        
        Returns:
            List[Tuple]: Lista de columnas con sus propiedades
        """
        query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            c.name AS column_name,
            ty.name AS data_type,
            CASE WHEN ty.name IN ('varchar', 'nvarchar', 'char', 'nchar') 
                 THEN c.max_length
                 ELSE NULL 
            END AS max_length,
            CASE WHEN ty.name IN ('decimal', 'numeric') 
                 THEN c.precision
                 ELSE NULL 
            END AS precision,
            CASE WHEN c.is_nullable = 1 THEN 'YES' ELSE 'NO' END AS is_nullable,
            OBJECT_DEFINITION(c.default_object_id) AS default_value
        FROM 
            sys.columns c
        JOIN 
            sys.tables t ON c.object_id = t.object_id
        JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        JOIN 
            sys.types ty ON c.user_type_id = ty.user_type_id
        ORDER BY 
            s.name, t.name, c.column_id
        """
        return self._execute_query(query)
    
    def get_primary_keys(self) -> List[Tuple]:
        """
        Obtener información de claves primarias en SQL Server.
        
        Returns:
            List[Tuple]: Lista de claves primarias
        """
        query = """
        SELECT 
            t.name AS table_name,
            c.name AS column_name
        FROM 
            sys.indexes i
        JOIN 
            sys.tables t ON i.object_id = t.object_id
        JOIN 
            sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN 
            sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE 
            i.is_primary_key = 1
        ORDER BY 
            t.name, ic.key_ordinal
        """
        return self._execute_query(query)
    
    def get_foreign_keys(self) -> List[Tuple]:
        """
        Obtener información de claves foráneas en SQL Server.
        
        Returns:
            List[Tuple]: Lista de claves foráneas
        """
        query = """
        SELECT 
            fk.name AS constraint_name,
            tab.name AS table_name,
            col.name AS column_name,
            ref_tab.name AS referenced_table,
            ref_col.name AS referenced_column
        FROM 
            sys.foreign_keys fk
        JOIN 
            sys.tables tab ON fk.parent_object_id = tab.object_id
        JOIN 
            sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN 
            sys.columns col ON fkc.parent_object_id = col.object_id AND fkc.parent_column_id = col.column_id
        JOIN 
            sys.tables ref_tab ON fk.referenced_object_id = ref_tab.object_id
        JOIN 
            sys.columns ref_col ON fkc.referenced_object_id = ref_col.object_id AND fkc.referenced_column_id = ref_col.column_id
        ORDER BY 
            tab.name, col.name
        """
        return self._execute_query(query)
    
    def get_indexes(self) -> List[Tuple]:
        """
        Obtener información de índices en SQL Server.
        
        Returns:
            List[Tuple]: Lista de índices
        """
        query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            i.is_unique,
            STUFF((SELECT ', ' + c.name
                  FROM sys.index_columns ic
                  JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                  WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id
                  ORDER BY ic.key_ordinal
                  FOR XML PATH('')), 1, 2, '') AS indexed_columns
        FROM 
            sys.indexes i
        JOIN 
            sys.tables t ON i.object_id = t.object_id
        JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        WHERE 
            i.index_id > 0  -- Ignorar heaps
        ORDER BY 
            t.name, i.name
        """
        return self._execute_query(query)

    def get_stored_procedures(self) -> List[Tuple]:
        """
        Obtener información de procedimientos almacenados en SQL Server.
        
        Returns:
            List[Tuple]: Lista de procedimientos almacenados con sus definiciones
        """
        query = """
        SELECT 
            s.name AS schema_name,
            p.name AS procedure_name,
            m.definition AS definition
        FROM 
            sys.procedures p
        JOIN 
            sys.schemas s ON p.schema_id = s.schema_id
        JOIN 
            sys.sql_modules m ON p.object_id = m.object_id
        ORDER BY 
            s.name, p.name
        """
        return self._execute_query(query)

    def get_triggers(self) -> List[Tuple]:
        """
        Obtener información de triggers en SQL Server.
        
        Returns:
            List[Tuple]: Lista de triggers con sus definiciones
        """
        query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            tr.name AS trigger_name,
            OBJECT_DEFINITION(tr.object_id) AS definition
        FROM 
            sys.triggers tr
        JOIN 
            sys.tables t ON tr.parent_id = t.object_id
        JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        ORDER BY 
            s.name, t.name, tr.name
        """
        return self._execute_query(query)

    def get_functions(self) -> List[Tuple]:
        """
        Obtener información de funciones definidas por el usuario en SQL Server.
        
        Returns:
            List[Tuple]: Lista de funciones con sus definiciones
        """
        query = """
        SELECT 
            s.name AS schema_name,
            f.name AS function_name,
            t.name AS return_type,
            m.definition AS definition
        FROM 
            sys.objects f
        JOIN 
            sys.schemas s ON f.schema_id = s.schema_id
        JOIN 
            sys.sql_modules m ON f.object_id = m.object_id
        JOIN 
            sys.types t ON f.type = t.user_type_id
        WHERE 
            f.type IN ('FN', 'IF', 'TF')
        ORDER BY 
            s.name, f.name
        """
        return self._execute_query(query)

    def get_table_statistics(self) -> List[Tuple]:
        """
        Obtener estadísticas de tablas en SQL Server.
        
        Returns:
            List[Tuple]: Lista de estadísticas de tablas
        """
        query = """
        SELECT 
            s.name AS schema_name,
            t.name AS table_name,
            p.rows AS row_count,
            CAST(SUM(a.total_pages) * 8 AS BIGINT) AS total_size_kb
        FROM 
            sys.tables t
        JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        JOIN 
            sys.partitions p ON t.object_id = p.object_id
        JOIN 
            sys.allocation_units a ON p.partition_id = a.container_id
        GROUP BY 
            s.name, t.name, p.rows
        ORDER BY 
            s.name, t.name
        """
        return self._execute_query(query)


class MySQLScanner(MetadataScanner):
    """Escáner de metadatos específico para MySQL."""
    
    def get_columns(self) -> List[Tuple]:
        """
        Obtener información de columnas en MySQL.
        
        Returns:
            List[Tuple]: Lista de columnas con sus propiedades
        """
        query = """
        SELECT 
            TABLE_SCHEMA AS schema_name,
            TABLE_NAME AS table_name,
            COLUMN_NAME AS column_name,
            DATA_TYPE AS data_type,
            IF(CHARACTER_MAXIMUM_LENGTH IS NULL, 0, CHARACTER_MAXIMUM_LENGTH) AS max_length,
            NUMERIC_PRECISION AS `precision`,
            IS_NULLABLE AS is_nullable,
            COLUMN_DEFAULT AS default_value
        FROM 
            INFORMATION_SCHEMA.COLUMNS
        WHERE 
            TABLE_SCHEMA = DATABASE()
        ORDER BY 
            TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
        """
        return self._execute_query(query)
    
    def get_primary_keys(self) -> List[Tuple]:
        """
        Obtener información de claves primarias en MySQL.
        
        Returns:
            List[Tuple]: Lista de claves primarias
        """
        query = """
        SELECT 
            TABLE_NAME AS table_name,
            COLUMN_NAME AS column_name
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE 
            CONSTRAINT_SCHEMA = DATABASE()
            AND CONSTRAINT_NAME = 'PRIMARY'
        ORDER BY 
            TABLE_NAME, ORDINAL_POSITION
        """
        return self._execute_query(query)
    
    def get_foreign_keys(self) -> List[Tuple]:
        """
        Obtener información de claves foráneas en MySQL.
        
        Returns:
            List[Tuple]: Lista de claves foráneas
        """
        query = """
        SELECT 
            CONSTRAINT_NAME AS constraint_name,
            TABLE_NAME AS table_name,
            COLUMN_NAME AS column_name,
            REFERENCED_TABLE_NAME AS referenced_table,
            REFERENCED_COLUMN_NAME AS referenced_column
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE 
            CONSTRAINT_SCHEMA = DATABASE()
            AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY 
            TABLE_NAME, COLUMN_NAME
        """
        return self._execute_query(query)
    
    def get_indexes(self) -> List[Tuple]:
        """
        Obtener información de índices en MySQL.
        
        Returns:
            List[Tuple]: Lista de índices
        """
        query = """
        SELECT 
            TABLE_SCHEMA AS schema_name,
            TABLE_NAME AS table_name,
            INDEX_NAME AS index_name,
            NOT NON_UNIQUE AS is_unique,
            GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS indexed_columns,
            INDEX_TYPE AS index_type
        FROM 
            INFORMATION_SCHEMA.STATISTICS
        WHERE 
            TABLE_SCHEMA = DATABASE()
        GROUP BY 
            TABLE_SCHEMA, TABLE_NAME, INDEX_NAME
        ORDER BY 
            TABLE_NAME, INDEX_NAME
        """
        return self._execute_query(query)


class PostgreSQLScanner(MetadataScanner):
    """Escáner de metadatos específico para PostgreSQL."""
    
    def get_columns(self) -> List[Tuple]:
        """
        Obtener información de columnas en PostgreSQL.
        
        Returns:
            List[Tuple]: Lista de columnas con sus propiedades
        """
        query = """
        SELECT 
            n.nspname AS schema_name,
            c.relname AS table_name,
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
            CASE 
                WHEN a.atttypid IN (1042, 1043) THEN a.atttypmod - 4
                ELSE NULL
            END AS max_length,
            CASE 
                WHEN a.atttypid IN (1700) THEN
                    --(pg_catalog.format_type(a.atttypid, a.atttypmod))::text::varchar::numeric
                    pg_catalog.format_type(a.atttypid, a.atttypmod)
                ELSE NULL
            END AS precision,
            CASE WHEN a.attnotnull THEN 'NO' ELSE 'YES' END AS is_nullable,
            pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_value
        FROM 
            pg_catalog.pg_attribute a
        JOIN 
            pg_catalog.pg_class c ON a.attrelid = c.oid
        JOIN 
            pg_catalog.pg_namespace n ON c.relnamespace = n.oid
        LEFT JOIN 
            pg_catalog.pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
        WHERE 
            a.attnum > 0
            AND NOT a.attisdropped
            AND c.relkind = 'r'
            AND n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            n.nspname, c.relname, a.attnum
        """
        return self._execute_query(query)
    
    def get_primary_keys(self) -> List[Tuple]:
        """
        Obtener información de claves primarias en PostgreSQL.
        
        Returns:
            List[Tuple]: Lista de claves primarias (schema_name, table_name, column_name)
        """
        query = """
        SELECT 
            tc.table_schema AS schema_name,
            tc.table_name,
            kcu.column_name
        FROM 
            information_schema.table_constraints tc
        JOIN 
            information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE 
            tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            tc.table_schema, tc.table_name, kcu.ordinal_position
        """
        return self._execute_query(query)
    
    def get_foreign_keys(self) -> List[Tuple]:
        """
        Obtener información de claves foráneas en PostgreSQL.
        
        Returns:
            List[Tuple]: Lista de claves foráneas
        """
        query = """
        SELECT 
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM 
            information_schema.table_constraints tc
        JOIN 
            information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN 
            information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        WHERE 
            tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            tc.table_name, kcu.column_name
        """
        return self._execute_query(query)
    
    def get_indexes(self) -> List[Tuple]:
        """
        Obtener información de índices en PostgreSQL.
        
        Returns:
            List[Tuple]: Lista de índices
        """
        query = """
        SELECT 
            n.nspname AS schema_name,
            t.relname AS table_name,
            i.relname AS index_name,
            pg_get_indexdef(i.oid) AS index_definition,
            ix.indisunique AS is_unique
        FROM 
            pg_catalog.pg_index ix
        JOIN 
            pg_catalog.pg_class i ON i.oid = ix.indexrelid
        JOIN 
            pg_catalog.pg_class t ON t.oid = ix.indrelid
        JOIN 
            pg_catalog.pg_namespace n ON n.oid = t.relnamespace
        WHERE 
            t.relkind = 'r'
            AND n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            t.relname, i.relname
        """
        return self._execute_query(query)


def create_scanner(connector) -> MetadataScanner:
    """
    Crea el escáner apropiado según el tipo de conector.
    
    Args:
        connector: Instancia de un conector de base de datos
        
    Returns:
        MetadataScanner: Escáner apropiado para el tipo de base de datos
        
    Raises:
        ValueError: Si el tipo de conector no es soportado
    """
    if isinstance(connector, MSSQLConnector):
        return MSSQLScanner(connector)
    elif isinstance(connector, MySQLConnector):
        return MySQLScanner(connector)
    elif isinstance(connector, PostgreSQLConnector):
        return PostgreSQLScanner(connector)
    else:
        raise ValueError(f"Tipo de conector no soportado: {type(connector).__name__}")