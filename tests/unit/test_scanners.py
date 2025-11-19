"""
Tests unitarios para infrastructure/database/scanners.py

Prueba los escáneres de metadatos para SQL Server, MySQL y PostgreSQL.
Valida las queries de extracción y el factory create_scanner.

Author: Jason Rivera
Date: 2025-11-18
"""

import unittest.mock as mock

import pytest

from scavengr.infrastructure.database.connector import (
    MSSQLConnector,
    MySQLConnector,
    PostgreSQLConnector,
)
from scavengr.infrastructure.database.scanners import (
    MSSQLScanner,
    MySQLScanner,
    PostgreSQLScanner,
    create_scanner,
)

# ===================================================================
# FIXTURES
# ===================================================================


@pytest.fixture
def mock_mssql_connector():
    """Mock de conector SQL Server."""
    connector = mock.MagicMock(spec=MSSQLConnector)
    connector.connection = mock.MagicMock()
    connector.is_connected.return_value = True
    return connector


@pytest.fixture
def mock_mysql_connector():
    """Mock de conector MySQL."""
    connector = mock.MagicMock(spec=MySQLConnector)
    connector.connection = mock.MagicMock()
    connector.is_connected.return_value = True
    return connector


@pytest.fixture
def mock_postgresql_connector():
    """Mock de conector PostgreSQL."""
    connector = mock.MagicMock(spec=PostgreSQLConnector)
    connector.connection = mock.MagicMock()
    connector.is_connected.return_value = True
    return connector


# ===================================================================
# TESTS: MSSQLScanner
# ===================================================================


class TestMSSQLScanner:
    """Tests para el escáner de SQL Server."""

    def test_initialization(self, mock_mssql_connector):
        """Test que el escáner se inicializa correctamente."""
        scanner = MSSQLScanner(mock_mssql_connector)
        assert scanner.connector == mock_mssql_connector

    def test_get_columns_executes_correct_query(self, mock_mssql_connector):
        """Test que get_columns ejecuta la query correcta."""
        # Mock execute_query para retornar resultados
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "usuarios", "id", "int", None, None, "NO", None),
            ("dbo", "usuarios", "nombre", "varchar", 100, None, "YES", None),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_columns()

        # Verificar que se llamó execute_query
        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.columns" in query
        assert "sys.tables" in query
        assert len(result) == 2

    def test_get_primary_keys_executes_correct_query(self, mock_mssql_connector):
        """Test que get_primary_keys ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("usuarios", "id"),
            ("productos", "id"),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_primary_keys()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.indexes" in query
        assert "is_primary_key = 1" in query
        assert len(result) == 2

    def test_get_foreign_keys_executes_correct_query(self, mock_mssql_connector):
        """Test que get_foreign_keys ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("fk_usuario_id", "pedidos", "usuario_id", "usuarios", "id"),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_foreign_keys()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.foreign_keys" in query
        assert len(result) == 1

    def test_get_indexes_executes_correct_query(self, mock_mssql_connector):
        """Test que get_indexes ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "usuarios", "idx_email", "NONCLUSTERED", 1, "email"),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_indexes()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.indexes" in query
        assert "index_id > 0" in query  # Ignorar heaps
        assert len(result) == 1

    def test_get_stored_procedures_executes_correct_query(self, mock_mssql_connector):
        """Test que get_stored_procedures ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "sp_get_users", "CREATE PROCEDURE sp_get_users AS..."),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_stored_procedures()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.procedures" in query
        assert "sys.sql_modules" in query
        assert len(result) == 1

    def test_get_triggers_executes_correct_query(self, mock_mssql_connector):
        """Test que get_triggers ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "usuarios", "trg_audit", "CREATE TRIGGER..."),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_triggers()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.triggers" in query
        assert len(result) == 1

    def test_get_functions_executes_correct_query(self, mock_mssql_connector):
        """Test que get_functions ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "fn_calculate", "int", "CREATE FUNCTION..."),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_functions()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.objects" in query
        assert "type IN ('FN', 'IF', 'TF')" in query
        assert len(result) == 1

    def test_get_table_statistics_executes_correct_query(self, mock_mssql_connector):
        """Test que get_table_statistics ejecuta la query correcta."""
        mock_mssql_connector.execute_query.return_value = [
            ("dbo", "usuarios", 1000, 8192),
        ]

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_table_statistics()

        mock_mssql_connector.execute_query.assert_called_once()
        query = mock_mssql_connector.execute_query.call_args[0][0]
        assert "sys.partitions" in query
        assert "sys.allocation_units" in query
        assert len(result) == 1


# ===================================================================
# TESTS: MySQLScanner
# ===================================================================


class TestMySQLScanner:
    """Tests para el escáner de MySQL."""

    def test_initialization(self, mock_mysql_connector):
        """Test que el escáner se inicializa correctamente."""
        scanner = MySQLScanner(mock_mysql_connector)
        assert scanner.connector == mock_mysql_connector

    def test_get_columns_executes_correct_query(self, mock_mysql_connector):
        """Test que get_columns ejecuta la query correcta."""
        mock_mysql_connector.execute_query.return_value = [
            ("mydb", "usuarios", "id", "int", 0, None, "NO", None),
            ("mydb", "usuarios", "email", "varchar", 100, None, "YES", None),
        ]

        scanner = MySQLScanner(mock_mysql_connector)
        result = scanner.get_columns()

        mock_mysql_connector.execute_query.assert_called_once()
        query = mock_mysql_connector.execute_query.call_args[0][0]
        assert "INFORMATION_SCHEMA.COLUMNS" in query
        assert "DATABASE()" in query
        assert len(result) == 2

    def test_get_primary_keys_executes_correct_query(self, mock_mysql_connector):
        """Test que get_primary_keys ejecuta la query correcta."""
        mock_mysql_connector.execute_query.return_value = [
            ("usuarios", "id"),
        ]

        scanner = MySQLScanner(mock_mysql_connector)
        result = scanner.get_primary_keys()

        mock_mysql_connector.execute_query.assert_called_once()
        query = mock_mysql_connector.execute_query.call_args[0][0]
        assert "INFORMATION_SCHEMA.KEY_COLUMN_USAGE" in query
        assert "CONSTRAINT_NAME = 'PRIMARY'" in query
        assert len(result) == 1

    def test_get_foreign_keys_executes_correct_query(self, mock_mysql_connector):
        """Test que get_foreign_keys ejecuta la query correcta."""
        mock_mysql_connector.execute_query.return_value = [
            ("fk_usuario", "pedidos", "usuario_id", "usuarios", "id"),
        ]

        scanner = MySQLScanner(mock_mysql_connector)
        result = scanner.get_foreign_keys()

        mock_mysql_connector.execute_query.assert_called_once()
        query = mock_mysql_connector.execute_query.call_args[0][0]
        assert "INFORMATION_SCHEMA.KEY_COLUMN_USAGE" in query
        assert "REFERENCED_TABLE_NAME IS NOT NULL" in query
        assert len(result) == 1

    def test_get_indexes_executes_correct_query(self, mock_mysql_connector):
        """Test que get_indexes ejecuta la query correcta."""
        mock_mysql_connector.execute_query.return_value = [
            ("mydb", "usuarios", "idx_email", 1, "email", "BTREE"),
        ]

        scanner = MySQLScanner(mock_mysql_connector)
        result = scanner.get_indexes()

        mock_mysql_connector.execute_query.assert_called_once()
        query = mock_mysql_connector.execute_query.call_args[0][0]
        assert "INFORMATION_SCHEMA.STATISTICS" in query
        assert "GROUP_CONCAT" in query
        assert len(result) == 1


# ===================================================================
# TESTS: PostgreSQLScanner
# ===================================================================


class TestPostgreSQLScanner:
    """Tests para el escáner de PostgreSQL."""

    def test_initialization(self, mock_postgresql_connector):
        """Test que el escáner se inicializa correctamente."""
        scanner = PostgreSQLScanner(mock_postgresql_connector)
        assert scanner.connector == mock_postgresql_connector

    def test_get_columns_executes_correct_query(self, mock_postgresql_connector):
        """Test que get_columns ejecuta la query correcta."""
        mock_postgresql_connector.execute_query.return_value = [
            ("public", "usuarios", "id", "integer", None, None, "NO", None),
            (
                "public",
                "usuarios",
                "email",
                "character varying(100)",
                100,
                None,
                "YES",
                None,
            ),
        ]

        scanner = PostgreSQLScanner(mock_postgresql_connector)
        result = scanner.get_columns()

        mock_postgresql_connector.execute_query.assert_called_once()
        query = mock_postgresql_connector.execute_query.call_args[0][0]
        assert "pg_catalog.pg_attribute" in query
        assert "pg_catalog.pg_class" in query
        # Optimización: Ahora incluye pg_toast en el filtro
        assert "NOT IN ('pg_catalog', 'information_schema', 'pg_toast')" in query
        assert len(result) == 2

    def test_get_primary_keys_executes_correct_query(self, mock_postgresql_connector):
        """Test que get_primary_keys ejecuta la query correcta."""
        mock_postgresql_connector.execute_query.return_value = [
            ("public", "usuarios", "id"),
        ]

        scanner = PostgreSQLScanner(mock_postgresql_connector)
        result = scanner.get_primary_keys()

        mock_postgresql_connector.execute_query.assert_called_once()
        query = mock_postgresql_connector.execute_query.call_args[0][0]
        assert "information_schema.table_constraints" in query
        assert "constraint_type = 'PRIMARY KEY'" in query
        assert len(result) == 1

    def test_get_foreign_keys_executes_correct_query(self, mock_postgresql_connector):
        """Test que get_foreign_keys ejecuta la query correcta."""
        mock_postgresql_connector.execute_query.return_value = [
            ("fk_usuario", "pedidos", "usuario_id", "usuarios", "id"),
        ]

        scanner = PostgreSQLScanner(mock_postgresql_connector)
        result = scanner.get_foreign_keys()

        mock_postgresql_connector.execute_query.assert_called_once()
        query = mock_postgresql_connector.execute_query.call_args[0][0]
        assert "information_schema.table_constraints" in query
        assert "constraint_type = 'FOREIGN KEY'" in query
        assert len(result) == 1

    def test_get_indexes_executes_correct_query(self, mock_postgresql_connector):
        """Test que get_indexes ejecuta la query correcta."""
        mock_postgresql_connector.execute_query.return_value = [
            ("public", "usuarios", "idx_email", "btree", True, "email"),
        ]

        scanner = PostgreSQLScanner(mock_postgresql_connector)
        result = scanner.get_indexes()

        mock_postgresql_connector.execute_query.assert_called_once()
        query = mock_postgresql_connector.execute_query.call_args[0][0]
        # Optimización: Ahora usa string_agg en lugar de pg_get_indexdef
        assert "string_agg" in query
        assert "pg_catalog.pg_index" in query
        assert len(result) == 1


# ===================================================================
# TESTS: create_scanner Factory
# ===================================================================


class TestCreateScanner:
    """Tests para la función factory create_scanner."""

    def test_create_mssql_scanner(self, mock_mssql_connector):
        """Test que crea un MSSQLScanner correctamente."""
        scanner = create_scanner(mock_mssql_connector)
        assert isinstance(scanner, MSSQLScanner)
        assert scanner.connector == mock_mssql_connector

    def test_create_mysql_scanner(self, mock_mysql_connector):
        """Test que crea un MySQLScanner correctamente."""
        scanner = create_scanner(mock_mysql_connector)
        assert isinstance(scanner, MySQLScanner)
        assert scanner.connector == mock_mysql_connector

    def test_create_postgresql_scanner(self, mock_postgresql_connector):
        """Test que crea un PostgreSQLScanner correctamente."""
        scanner = create_scanner(mock_postgresql_connector)
        assert isinstance(scanner, PostgreSQLScanner)
        assert scanner.connector == mock_postgresql_connector

    def test_create_scanner_unsupported_connector(self):
        """Test que lanza ValueError para conector no soportado."""
        mock_unsupported = mock.MagicMock()

        with pytest.raises(ValueError) as exc_info:
            create_scanner(mock_unsupported)

        assert "Tipo de conector no soportado" in str(exc_info.value)


# ===================================================================
# TESTS: Integración de Scanners
# ===================================================================


class TestScannersIntegration:
    """Tests de integración para los escáneres."""

    def test_mssql_scanner_returns_empty_list_when_no_results(
        self, mock_mssql_connector
    ):
        """Test que MSSQL scanner retorna lista vacía cuando no hay resultados."""
        mock_mssql_connector.execute_query.return_value = []

        scanner = MSSQLScanner(mock_mssql_connector)
        result = scanner.get_columns()

        assert result == []
        assert isinstance(result, list)

    def test_mysql_scanner_returns_empty_list_when_no_results(
        self, mock_mysql_connector
    ):
        """Test que MySQL scanner retorna lista vacía cuando no hay resultados."""
        mock_mysql_connector.execute_query.return_value = []

        scanner = MySQLScanner(mock_mysql_connector)
        result = scanner.get_primary_keys()

        assert result == []
        assert isinstance(result, list)

    def test_postgresql_scanner_returns_empty_list_when_no_results(
        self, mock_postgresql_connector
    ):
        """Test que PostgreSQL scanner retorna lista vacía cuando no hay resultados."""
        mock_postgresql_connector.execute_query.return_value = []

        scanner = PostgreSQLScanner(mock_postgresql_connector)
        result = scanner.get_foreign_keys()

        assert result == []
        assert isinstance(result, list)

    def test_all_scanners_inherit_from_base(
        self, mock_mssql_connector, mock_mysql_connector, mock_postgresql_connector
    ):
        """Test que todos los scanners heredan de MetadataScanner."""
        from scavengr.infrastructure.database.base_scanner import MetadataScanner

        mssql_scanner = MSSQLScanner(mock_mssql_connector)
        mysql_scanner = MySQLScanner(mock_mysql_connector)
        postgresql_scanner = PostgreSQLScanner(mock_postgresql_connector)

        assert isinstance(mssql_scanner, MetadataScanner)
        assert isinstance(mysql_scanner, MetadataScanner)
        assert isinstance(postgresql_scanner, MetadataScanner)
