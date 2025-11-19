"""Tests unitarios para infrastructure/database/connector.py.

Tests para conectores de base de datos (PostgreSQL, MySQL, MSSQL) y
gestión de conexiones sin conexiones reales.

Cobertura:
- Creación de conectores específicos por motor de BD
- Establecimiento de conexiones (mockeadas)
- Manejo de errores de conexión
- Cierre de conexiones
- Validación de estado de conexión
- Ejecución de queries
- Gestor de conexiones (ConnectionManager)

Author: Jason Rivera
Date: 2025-11-18
"""

from unittest import mock

import pytest

from scavengr.infrastructure.database.connector import (
    ConnectionManager,
    DatabaseConnector,
    MSSQLConnector,
    MySQLConnector,
    PostgreSQLConnector,
    create_connector,
)


@pytest.fixture
def postgresql_config():
    """Configuración de prueba para PostgreSQL."""
    return {
        "type": "postgresql",
        "host": "localhost",
        "name": "test_db",
        "user": "postgres",
        "password": "password123",
        "DB_PORT": 5432,
    }


@pytest.fixture
def mysql_config():
    """Configuración de prueba para MySQL."""
    return {
        "type": "mysql",
        "host": "localhost",
        "name": "test_db",
        "user": "root",
        "password": "password123",
        "DB_PORT": 3306,
    }


@pytest.fixture
def mssql_config():
    """Configuración de prueba para SQL Server."""
    return {
        "type": "mssql",
        "host": "localhost",
        "name": "test_db",
        "user": "sa",
        "password": "Password123!",
        "DB_DRIVER": "ODBC Driver 17 for SQL Server",
    }


class TestDatabaseConnectorBase:
    """Tests para la clase base DatabaseConnector."""

    def test_init_creates_instance(self, postgresql_config):
        """Debe crear instancia con configuración."""
        connector = DatabaseConnector(postgresql_config)

        assert connector.config == postgresql_config
        assert connector.connection is None
        assert connector.cursor is None

    def test_connect_not_implemented(self, postgresql_config):
        """Debe lanzar NotImplementedError en clase base."""
        connector = DatabaseConnector(postgresql_config)

        with pytest.raises(NotImplementedError) as exc_info:
            connector.connect()

        assert "debe ser implementado" in str(exc_info.value).lower()

    def test_is_connected_returns_false_initially(self, postgresql_config):
        """Debe retornar False cuando no hay conexión."""
        connector = DatabaseConnector(postgresql_config)

        assert connector.is_connected() is False

    def test_is_connected_returns_true_when_connected(self, postgresql_config):
        """Debe retornar True cuando existe conexión."""
        connector = DatabaseConnector(postgresql_config)
        connector.connection = mock.MagicMock()

        assert connector.is_connected() is True

    def test_close_closes_connection(self, postgresql_config):
        """Debe cerrar conexión cuando existe."""
        connector = DatabaseConnector(postgresql_config)
        mock_connection = mock.MagicMock()
        connector.connection = mock_connection

        connector.close()

        mock_connection.close.assert_called_once()
        assert connector.connection is None
        assert connector.cursor is None

    def test_close_handles_none_connection(self, postgresql_config):
        """Debe manejar correctamente cuando connection es None."""
        connector = DatabaseConnector(postgresql_config)
        connector.connection = None

        # No debe lanzar excepción
        connector.close()

        assert connector.connection is None

    def test_execute_query_raises_without_connection(self, postgresql_config):
        """Debe lanzar excepción si no hay conexión."""
        connector = DatabaseConnector(postgresql_config)

        with pytest.raises(Exception) as exc_info:
            connector.execute_query("SELECT 1")

        assert "no hay una conexión" in str(exc_info.value).lower()

    def test_execute_query_select(self, postgresql_config):
        """Debe ejecutar query SELECT correctamente."""
        connector = DatabaseConnector(postgresql_config)
        mock_connection = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [(1, "test")]

        connector.connection = mock_connection
        connector.cursor = mock_cursor

        result = connector.execute_query("SELECT id, name FROM users")

        mock_cursor.execute.assert_called_once_with("SELECT id, name FROM users")
        mock_cursor.fetchall.assert_called_once()
        assert result == [(1, "test")]

    def test_execute_query_with_params(self, postgresql_config):
        """Debe ejecutar query con parámetros."""
        connector = DatabaseConnector(postgresql_config)
        mock_connection = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_cursor.fetchall.return_value = [(1,)]

        connector.connection = mock_connection
        connector.cursor = mock_cursor

        result = connector.execute_query(
            "SELECT id FROM users WHERE name = %s", ["test"]
        )

        mock_cursor.execute.assert_called_once_with(
            "SELECT id FROM users WHERE name = %s", ["test"]
        )
        assert result == [(1,)]

    def test_execute_query_insert_commits(self, postgresql_config):
        """Debe hacer commit en queries INSERT."""
        connector = DatabaseConnector(postgresql_config)
        mock_connection = mock.MagicMock()
        mock_cursor = mock.MagicMock()

        connector.connection = mock_connection
        connector.cursor = mock_cursor

        result = connector.execute_query("INSERT INTO users VALUES (1, 'test')")

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

    def test_execute_query_rollback_on_error(self, postgresql_config):
        """Debe hacer rollback en caso de error."""
        connector = DatabaseConnector(postgresql_config)
        mock_connection = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_cursor.execute.side_effect = Exception("DB Error")

        connector.connection = mock_connection
        connector.cursor = mock_cursor

        with pytest.raises(Exception) as exc_info:
            connector.execute_query("SELECT * FROM users")

        mock_connection.rollback.assert_called_once()
        assert "error al ejecutar la consulta" in str(exc_info.value).lower()


class TestPostgreSQLConnector:
    """Tests para PostgreSQLConnector."""

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.pgsql")
    def test_connect_success(self, mock_pgsql, postgresql_config):
        """Debe conectar exitosamente a PostgreSQL."""
        mock_connection = mock.MagicMock()
        mock_pgsql.connect.return_value = mock_connection

        connector = PostgreSQLConnector(postgresql_config)
        result = connector.connect()

        mock_pgsql.connect.assert_called_once_with(
            host="localhost",
            port=5432,
            dbname="test_db",
            user="postgres",
            password="password123",
        )
        assert result == mock_connection
        assert connector.connection == mock_connection

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.pgsql")
    def test_connect_uses_default_port(self, mock_pgsql, postgresql_config):
        """Debe usar puerto por defecto si no está en config."""
        del postgresql_config["DB_PORT"]
        mock_connection = mock.MagicMock()
        mock_pgsql.connect.return_value = mock_connection

        connector = PostgreSQLConnector(postgresql_config)
        connector.connect()

        # Verificar que usa puerto 5432 por defecto
        call_kwargs = mock_pgsql.connect.call_args[1]
        assert call_kwargs["port"] == 5432

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", False)
    def test_connect_raises_import_error(self, postgresql_config):
        """Debe lanzar ImportError si psycopg2 no está disponible."""
        connector = PostgreSQLConnector(postgresql_config)

        with pytest.raises(ImportError) as exc_info:
            connector.connect()

        assert "psycopg2" in str(exc_info.value).lower()
        assert "pip install" in str(exc_info.value).lower()

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.pgsql")
    def test_connect_raises_on_connection_error(self, mock_pgsql, postgresql_config):
        """Debe manejar errores de conexión."""
        from psycopg2 import OperationalError

        mock_pgsql.connect.side_effect = OperationalError("Connection refused")
        mock_pgsql.Error = OperationalError

        connector = PostgreSQLConnector(postgresql_config)

        with pytest.raises(Exception) as exc_info:
            connector.connect()

        assert "error al conectar a postgresql" in str(exc_info.value).lower()


class TestMySQLConnector:
    """Tests para MySQLConnector."""

    @mock.patch("scavengr.infrastructure.database.connector.MYSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mysql")
    def test_connect_success(self, mock_mysql, mysql_config):
        """Debe conectar exitosamente a MySQL."""
        mock_connection = mock.MagicMock()
        mock_mysql.connect.return_value = mock_connection

        connector = MySQLConnector(mysql_config)
        result = connector.connect()

        mock_mysql.connect.assert_called_once_with(
            host="localhost",
            port=3306,
            database="test_db",
            user="root",
            password="password123",
        )
        assert result == mock_connection
        assert connector.connection == mock_connection

    @mock.patch("scavengr.infrastructure.database.connector.MYSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mysql")
    def test_connect_uses_default_port(self, mock_mysql, mysql_config):
        """Debe usar puerto por defecto si no está en config."""
        del mysql_config["DB_PORT"]
        mock_connection = mock.MagicMock()
        mock_mysql.connect.return_value = mock_connection

        connector = MySQLConnector(mysql_config)
        connector.connect()

        # Verificar que usa puerto 3306 por defecto
        call_kwargs = mock_mysql.connect.call_args[1]
        assert call_kwargs["port"] == 3306

    @mock.patch("scavengr.infrastructure.database.connector.MYSQL_AVAILABLE", False)
    def test_connect_raises_import_error(self, mysql_config):
        """Debe lanzar ImportError si mysql-connector no está disponible."""
        connector = MySQLConnector(mysql_config)

        with pytest.raises(ImportError) as exc_info:
            connector.connect()

        assert "mysql-connector-python" in str(exc_info.value).lower()
        assert "pip install" in str(exc_info.value).lower()

    @mock.patch("scavengr.infrastructure.database.connector.MYSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mysql")
    def test_connect_raises_on_connection_error(self, mock_mysql, mysql_config):
        """Debe manejar errores de conexión."""
        from mysql.connector import Error as MySQLError

        mock_mysql.connect.side_effect = MySQLError("Access denied")
        mock_mysql.Error = MySQLError

        connector = MySQLConnector(mysql_config)

        with pytest.raises(Exception) as exc_info:
            connector.connect()

        assert "error al conectar a mysql" in str(exc_info.value).lower()


class TestMSSQLConnector:
    """Tests para MSSQLConnector."""

    @mock.patch("scavengr.infrastructure.database.connector.MSSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mssql")
    def test_connect_success(self, mock_mssql, mssql_config):
        """Debe conectar exitosamente a SQL Server."""
        mock_connection = mock.MagicMock()
        mock_mssql.connect.return_value = mock_connection

        connector = MSSQLConnector(mssql_config)
        result = connector.connect()

        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=test_db;"
            "UID=sa;"
            "PWD=Password123!;"
        )
        mock_mssql.connect.assert_called_once_with(expected_conn_str)
        assert result == mock_connection
        assert connector.connection == mock_connection

    @mock.patch("scavengr.infrastructure.database.connector.MSSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mssql")
    def test_connect_uses_default_driver(self, mock_mssql, mssql_config):
        """Debe usar driver por defecto si no está en config."""
        del mssql_config["DB_DRIVER"]
        mock_connection = mock.MagicMock()
        mock_mssql.connect.return_value = mock_connection

        connector = MSSQLConnector(mssql_config)
        connector.connect()

        # Verificar que usa "SQL Server" como driver por defecto
        conn_str = mock_mssql.connect.call_args[0][0]
        assert "DRIVER={SQL Server}" in conn_str

    @mock.patch("scavengr.infrastructure.database.connector.MSSQL_AVAILABLE", False)
    def test_connect_raises_import_error(self, mssql_config):
        """Debe lanzar ImportError si pyodbc no está disponible."""
        connector = MSSQLConnector(mssql_config)

        with pytest.raises(ImportError) as exc_info:
            connector.connect()

        assert "pyodbc" in str(exc_info.value).lower()
        assert "pip install" in str(exc_info.value).lower()

    @mock.patch("scavengr.infrastructure.database.connector.MSSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mssql")
    def test_connect_raises_on_connection_error(self, mock_mssql, mssql_config):
        """Debe manejar errores de conexión."""
        from pyodbc import Error as PyODBCError

        mock_mssql.connect.side_effect = PyODBCError("Login failed")
        mock_mssql.Error = PyODBCError

        connector = MSSQLConnector(mssql_config)

        with pytest.raises(Exception) as exc_info:
            connector.connect()

        assert "error al conectar a sql server" in str(exc_info.value).lower()

    @mock.patch("scavengr.infrastructure.database.connector.MSSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.mssql")
    def test_connect_validates_connection(self, mock_mssql, mssql_config):
        """Debe validar que la conexión se estableció."""
        # Simular conexión None (fallo silencioso)
        mock_mssql.connect.return_value = None

        connector = MSSQLConnector(mssql_config)

        with pytest.raises(Exception) as exc_info:
            connector.connect()

        assert "no se pudo establecer" in str(exc_info.value).lower()


class TestCreateConnector:
    """Tests para la función factory create_connector."""

    def test_create_postgresql_connector(self, postgresql_config):
        """Debe crear conector PostgreSQL."""
        connector = create_connector(postgresql_config)

        assert isinstance(connector, PostgreSQLConnector)
        assert connector.config == postgresql_config

    def test_create_mysql_connector(self, mysql_config):
        """Debe crear conector MySQL."""
        connector = create_connector(mysql_config)

        assert isinstance(connector, MySQLConnector)
        assert connector.config == mysql_config

    def test_create_mssql_connector(self, mssql_config):
        """Debe crear conector MSSQL."""
        connector = create_connector(mssql_config)

        assert isinstance(connector, MSSQLConnector)
        assert connector.config == mssql_config

    def test_create_connector_case_insensitive(self):
        """Debe ser case-insensitive al crear conectores."""
        config_lower = {"type": "postgresql", "host": "localhost"}
        config_mixed = {"type": "PostgreSQL", "host": "localhost"}

        connector1 = create_connector(config_lower)
        connector2 = create_connector(config_mixed)

        assert isinstance(connector1, PostgreSQLConnector)
        assert isinstance(connector2, PostgreSQLConnector)

    def test_create_connector_unsupported_type(self):
        """Debe lanzar ValueError para tipo no soportado."""
        config = {"type": "oracle", "host": "localhost"}

        with pytest.raises(ValueError) as exc_info:
            create_connector(config)

        assert "no soportado" in str(exc_info.value).lower()
        assert "oracle" in str(exc_info.value).lower()

    def test_create_connector_missing_type(self):
        """Debe lanzar ValueError si falta tipo de BD."""
        config = {"host": "localhost"}

        with pytest.raises(ValueError) as exc_info:
            create_connector(config)

        assert "no soportado" in str(exc_info.value).lower()


class TestConnectionManager:
    """Tests para ConnectionManager."""

    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_init_creates_instance(self, mock_config_manager):
        """Debe crear instancia de ConnectionManager."""
        manager = ConnectionManager()

        assert manager.connections == {}
        mock_config_manager.assert_called_once_with(None)

    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_init_with_config_path(self, mock_config_manager):
        """Debe usar config_path especificado."""
        _ = ConnectionManager(config_path="/path/to/config.env")  # noqa: F841

        mock_config_manager.assert_called_once_with("/path/to/config.env")

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.pgsql")
    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_get_connection_creates_new(
        self, mock_config_manager, mock_pgsql, postgresql_config
    ):
        """Debe crear nueva conexión si no existe."""
        mock_connection = mock.MagicMock()
        mock_pgsql.connect.return_value = mock_connection

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.get_db_config.return_value = postgresql_config

        manager = ConnectionManager()
        result = manager.get_connection("main")

        mock_cm_instance.get_db_config.assert_called_once_with("main")
        assert result == mock_connection
        assert "main" in manager.connections

    @mock.patch("scavengr.infrastructure.database.connector.PGSQL_AVAILABLE", True)
    @mock.patch("scavengr.infrastructure.database.connector.pgsql")
    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_get_connection_reuses_existing(
        self, mock_config_manager, mock_pgsql, postgresql_config
    ):
        """Debe reusar conexión existente si está activa."""
        mock_connection = mock.MagicMock()
        mock_pgsql.connect.return_value = mock_connection

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.get_db_config.return_value = postgresql_config

        manager = ConnectionManager()

        # Primera llamada - crea conexión
        result1 = manager.get_connection("main")

        # Segunda llamada - debe reusar
        result2 = manager.get_connection("main")

        # Debe llamar connect solo una vez
        assert mock_pgsql.connect.call_count == 1
        assert result1 == result2

    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_close_connection_existing(self, mock_config_manager):
        """Debe cerrar conexión existente."""
        manager = ConnectionManager()
        mock_connector = mock.MagicMock()
        manager.connections["main"] = mock_connector

        result = manager.close_connection("main")

        mock_connector.close.assert_called_once()
        assert "main" not in manager.connections
        assert result is True

    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_close_connection_non_existing(self, mock_config_manager):
        """Debe retornar False si la conexión no existe."""
        manager = ConnectionManager()

        result = manager.close_connection("non_existent")

        assert result is False

    @mock.patch("scavengr.infrastructure.database.connector.ConfigManager")
    def test_close_all_connections(self, mock_config_manager):
        """Debe cerrar todas las conexiones."""
        manager = ConnectionManager()
        mock_connector1 = mock.MagicMock()
        mock_connector2 = mock.MagicMock()
        manager.connections["conn1"] = mock_connector1
        manager.connections["conn2"] = mock_connector2

        manager.close_all_connections()

        mock_connector1.close.assert_called_once()
        mock_connector2.close.assert_called_once()
        assert manager.connections == {}
