"""Configuración global y fixtures para tests."""

from typing import Any, Dict, List, Optional, Tuple
from unittest import mock

import pytest

# Importar entidades del core para mocks
from scavengr.core.entities import Column, DatabaseSchema, Index, Relationship, Table


@pytest.fixture
def mock_database_schema() -> Dict[str, Any]:
    """Fixture: Esquema de base de datos simulado para tests."""
    return {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False},
                    {"name": "email", "type": "VARCHAR(255)", "nullable": False},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": True},
                ],
                "primary_keys": ["id"],
                "relationships": [
                    {
                        "name": "users_posts",
                        "table": "users",
                        "foreign_key": "id",
                        "referenced_table": "posts",
                        "referenced_key": "user_id",
                    }
                ],
                "indexes": [
                    {"name": "idx_email", "columns": ["email"], "type": "UNIQUE"}
                ],
            },
            {
                "name": "posts",
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False},
                    {"name": "user_id", "type": "INTEGER", "nullable": False},
                    {"name": "title", "type": "VARCHAR(500)", "nullable": False},
                    {"name": "content", "type": "TEXT", "nullable": True},
                ],
                "primary_keys": ["id"],
                "relationships": [],
                "indexes": [],
            },
        ]
    }


@pytest.fixture
def mock_simple_column() -> Dict[str, Any]:
    """Fixture: Columna simulada para tests de servicios."""
    return {
        "name": "email",
        "type": "VARCHAR(255)",
        "nullable": False,
        "default": None,
        "description": None,
    }


@pytest.fixture
def mock_sensitive_column() -> Dict[str, Any]:
    """Fixture: Columna sensible (PII) para tests."""
    return {
        "name": "ssn",
        "type": "VARCHAR(11)",
        "nullable": False,
        "default": None,
        "description": "Social Security Number",
    }


@pytest.fixture
def mock_payment_column() -> Dict[str, Any]:
    """Fixture: Columna de pago para tests de sensibilidad."""
    return {
        "name": "credit_card",
        "type": "VARCHAR(19)",
        "nullable": True,
        "default": None,
        "description": "Credit card number",
    }


# ===================================================================
# MOCKS PARA DATABASE ADAPTERS
# ===================================================================


@pytest.fixture
def mock_db_connection():
    """Fixture: Mock de conexión a base de datos.

    Simula una conexión genérica a BD sin necesidad de conexión real.
    Útil para tests de conectores y scanners.
    """
    connection = mock.MagicMock()
    connection.is_connected.return_value = True
    connection.cursor.return_value = mock.MagicMock()
    return connection


@pytest.fixture
def mock_postgresql_scanner():
    """Fixture: Mock de PostgreSQLScanner con datos de ejemplo.

    Simula un scanner de PostgreSQL que retorna metadatos completos.
    """
    scanner = mock.MagicMock()

    # Mock de scan_schema() - retorna DatabaseSchema completo
    users_table = Table(
        schema="public",
        name="users",
        columns=[
            Column(
                name="id", type="integer", is_nullable=False, is_pk=True, default=None
            ),
            Column(
                name="email",
                type="character varying",
                is_nullable=False,
                is_pk=False,
                default=None,
            ),
            Column(
                name="created_at",
                type="timestamp without time zone",
                is_nullable=True,
                is_pk=False,
                default="CURRENT_TIMESTAMP",
            ),
        ],
    )

    posts_table = Table(
        schema="public",
        name="posts",
        columns=[
            Column(
                name="id", type="integer", is_nullable=False, is_pk=True, default=None
            ),
            Column(
                name="user_id",
                type="integer",
                is_nullable=False,
                is_pk=False,
                default=None,
                ref_table="users",
                ref_column="id",
            ),
            Column(
                name="title",
                type="character varying",
                is_nullable=False,
                is_pk=False,
                default=None,
            ),
            Column(
                name="content", type="text", is_nullable=True, is_pk=False, default=None
            ),
        ],
    )

    schema = DatabaseSchema(
        name="test_db",
        tables=[users_table, posts_table],
        relationships=[
            Relationship(
                from_table="posts",
                from_column="user_id",
                to_table="users",
                to_column="id",
                relationship_type=">",
            )
        ],
        indexes=[
            Index(
                name="idx_users_email",
                table="users",
                columns=["email"],
                unique=True,
                index_type="btree",
            )
        ],
    )

    scanner.scan_schema.return_value = schema

    # Mock de get_columns()
    scanner.get_columns.return_value = [
        ("users", "id", True, False, None),
        ("users", "email", False, False, None),
        ("users", "created_at", False, False, "CURRENT_TIMESTAMP"),
        ("posts", "id", True, False, None),
        ("posts", "user_id", False, True, None),
        ("posts", "title", False, False, None),
        ("posts", "content", False, False, None),
    ]

    return scanner


@pytest.fixture
def mock_mysql_scanner():
    """Fixture: Mock de MySQLScanner con datos de ejemplo.

    Simula un scanner de MySQL/MariaDB que retorna metadatos completos.
    """
    scanner = mock.MagicMock()

    # Mock de scan_schema() - retorna DatabaseSchema completo
    users_table = Table(
        schema="test_db",
        name="users",
        columns=[
            Column(name="id", type="int", is_nullable=False, is_pk=True, default=None),
            Column(
                name="username",
                type="varchar(100)",
                is_nullable=False,
                is_pk=False,
                default=None,
            ),
            Column(
                name="status",
                type="enum('active','inactive')",
                is_nullable=False,
                is_pk=False,
                default="'active'",
            ),
        ],
    )

    schema = DatabaseSchema(
        name="test_db",
        tables=[users_table],
        relationships=[],
        indexes=[
            Index(
                name="PRIMARY",
                table="users",
                columns=["id"],
                unique=True,
                index_type="BTREE",
            ),
            Index(
                name="idx_username",
                table="users",
                columns=["username"],
                unique=True,
                index_type="BTREE",
            ),
        ],
    )

    scanner.scan_schema.return_value = schema
    scanner.get_columns.return_value = [
        ("users", "id", True, False, None),
        ("users", "username", False, False, None),
        ("users", "status", False, False, "'active'"),
    ]

    return scanner


@pytest.fixture
def mock_mssql_scanner():
    """Fixture: Mock de MSSQLScanner con datos de ejemplo.

    Simula un scanner de SQL Server que retorna metadatos completos.
    """
    scanner = mock.MagicMock()

    # Mock de scan_schema() - retorna DatabaseSchema completo
    employees_table = Table(
        schema="dbo",
        name="employees",
        columns=[
            Column(
                name="EmployeeID",
                type="int",
                is_nullable=False,
                is_pk=True,
                default=None,
            ),
            Column(
                name="FirstName",
                type="nvarchar(50)",
                is_nullable=False,
                is_pk=False,
                default=None,
            ),
            Column(
                name="LastName",
                type="nvarchar(50)",
                is_nullable=False,
                is_pk=False,
                default=None,
            ),
            Column(
                name="HireDate",
                type="datetime",
                is_nullable=True,
                is_pk=False,
                default="getdate()",
            ),
        ],
    )

    schema = DatabaseSchema(
        name="TestDB",
        tables=[employees_table],
        relationships=[],
        indexes=[
            Index(
                name="PK_employees",
                table="employees",
                columns=["EmployeeID"],
                unique=True,
                index_type="CLUSTERED",
            )
        ],
    )

    scanner.scan_schema.return_value = schema
    scanner.get_columns.return_value = [
        ("employees", "EmployeeID", True, False, None),
        ("employees", "FirstName", False, False, None),
        ("employees", "LastName", False, False, None),
        ("employees", "HireDate", False, False, "getdate()"),
    ]

    return scanner


@pytest.fixture
def mock_db_config_postgresql() -> Dict[str, Any]:
    """Fixture: Configuración de BD PostgreSQL para tests."""
    return {
        "db_type": "postgresql",
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "test_db",
        "db_user": "test_user",
        "db_password": "test_password",
        "db_schema": "public",
    }


@pytest.fixture
def mock_db_config_mysql() -> Dict[str, Any]:
    """Fixture: Configuración de BD MySQL para tests."""
    return {
        "db_type": "mysql",
        "db_host": "localhost",
        "db_port": 3306,
        "db_name": "test_db",
        "db_user": "test_user",
        "db_password": "test_password",
    }


@pytest.fixture
def mock_db_config_mssql() -> Dict[str, Any]:
    """Fixture: Configuración de BD SQL Server para tests."""
    return {
        "db_type": "mssql",
        "db_host": "localhost",
        "db_port": 1433,
        "db_name": "TestDB",
        "db_user": "test_user",
        "db_password": "test_password",
    }


@pytest.fixture
def mock_metadata_response_postgresql() -> List[Tuple]:
    """Fixture: Respuesta de metadatos cruda de PostgreSQL.

    Simula el resultado de queries directas a information_schema.
    """
    return [
        # (table_name, column_name, data_type, is_nullable, column_default, character_maximum_length)
        ("users", "id", "integer", "NO", None, None),
        ("users", "email", "character varying", "NO", None, 255),
        (
            "users",
            "created_at",
            "timestamp without time zone",
            "YES",
            "CURRENT_TIMESTAMP",
            None,
        ),
        ("posts", "id", "integer", "NO", None, None),
        ("posts", "user_id", "integer", "NO", None, None),
        ("posts", "title", "character varying", "NO", None, 500),
        ("posts", "content", "text", "YES", None, None),
    ]


@pytest.fixture
def mock_metadata_response_mysql() -> List[Tuple]:
    """Fixture: Respuesta de metadatos cruda de MySQL.

    Simula el resultado de queries directas a information_schema.
    """
    return [
        # (table_name, column_name, data_type, is_nullable, column_default, column_type)
        ("users", "id", "int", "NO", None, "int(11)"),
        ("users", "username", "varchar", "NO", None, "varchar(100)"),
        ("users", "status", "enum", "NO", "'active'", "enum('active','inactive')"),
    ]


@pytest.fixture
def mock_metadata_response_mssql() -> List[Tuple]:
    """Fixture: Respuesta de metadatos cruda de SQL Server.

    Simula el resultado de queries directas a sys.columns.
    """
    return [
        # (schema_name, table_name, column_name, data_type, is_nullable, column_default, max_length)
        ("dbo", "employees", "EmployeeID", "int", 0, None, 4),
        ("dbo", "employees", "FirstName", "nvarchar", 0, None, 100),
        ("dbo", "employees", "LastName", "nvarchar", 0, None, 100),
        ("dbo", "employees", "HireDate", "datetime", 1, "getdate()", 8),
    ]


@pytest.fixture
def mock_db_connection_error():
    """Fixture: Mock de conexión que falla.

    Simula errores de conexión a BD (timeout, credenciales inválidas, etc).
    """
    connection = mock.MagicMock()
    connection.connect.side_effect = Exception(
        "Connection timeout: Unable to connect to database"
    )
    connection.is_connected.return_value = False
    return connection


@pytest.fixture
def mock_scanner_empty_database():
    """Fixture: Mock de scanner para base de datos vacía.

    Simula un scanner que conecta exitosamente pero no encuentra tablas.
    """
    scanner = mock.MagicMock()

    schema = DatabaseSchema(name="empty_db", tables=[], relationships=[], indexes=[])

    scanner.scan_schema.return_value = schema
    scanner.get_columns.return_value = []

    return scanner
