"""Tests unitarios para application/extract.py

Tests para el caso de uso de extracción de metadatos de bases de datos.
Verifica la orquestación completa del proceso de extracción.

Author: Jason Rivera
Date: 2025-11-18
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from scavengr.application.extract import ExtractionResult, ExtractMetadata
from scavengr.core.entities import Column, DatabaseSchema, Table


class TestExtractMetadata:
    """Tests para el caso de uso ExtractMetadata."""

    @pytest.fixture
    def db_config_postgresql(self):
        """Configuración de BD PostgreSQL para tests."""
        return {
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass",
        }

    @pytest.fixture
    def db_config_mysql(self):
        """Configuración de BD MySQL para tests."""
        return {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "name": "test_db",
            "user": "test_user",
            "password": "test_pass",
        }

    @pytest.fixture
    def db_config_mssql(self):
        """Configuración de BD SQL Server para tests."""
        return {
            "type": "mssql",
            "host": "localhost",
            "port": 1433,
            "name": "TestDB",
            "user": "test_user",
            "password": "test_pass",
        }

    @pytest.fixture
    def generation_config(self):
        """Configuración de generación para tests."""
        return {"source_system": {"name": "TestSystem", "version": "1.0.0"}}

    @pytest.fixture
    def mock_scanner_with_data(self):
        """Mock de scanner con datos de ejemplo."""
        scanner = mock.MagicMock()

        # Mock get_tables()
        scanner.get_tables.return_value = []

        # Mock get_columns() - formato: [schema, table, column, type, max_length, precision, nullable, default]
        scanner.get_columns.return_value = [
            ("public", "users", "id", "integer", None, None, "NO", None),
            ("public", "users", "email", "character varying", 255, None, "NO", None),
            (
                "public",
                "users",
                "created_at",
                "timestamp without time zone",
                None,
                None,
                "YES",
                "CURRENT_TIMESTAMP",
            ),
        ]

        # Mock get_foreign_keys() - formato: [constraint, table, column, ref_table, ref_column]
        scanner.get_foreign_keys.return_value = []

        # Mock get_primary_keys() - formato: [schema, table, column] para PostgreSQL
        scanner.get_primary_keys.return_value = [
            ("public", "users", "id"),
        ]

        # Mock get_indexes() - formato: [schema, table, index_name, index_def, is_unique]
        scanner.get_indexes.return_value = [
            (
                "public",
                "users",
                "idx_users_email",
                "CREATE INDEX idx_users_email ON public.users USING btree (email)",
                True,
            ),
        ]

        return scanner

    def test_extract_postgresql_success(
        self, db_config_postgresql, generation_config, mock_scanner_with_data
    ):
        """Test extracción exitosa desde PostgreSQL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_output.dbml")

            # Mock de connector y scanner
            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_connector.connect.return_value = None
                mock_connector.close.return_value = None

                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner_with_data

                # Ejecutar extracción
                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                # Verificaciones
                assert result.success is True
                assert result.output_path == output_path
                assert result.tables_count == 1
                assert result.columns_count == 3
                assert result.indexes_count == 1
                assert result.error_message is None
                assert os.path.exists(output_path)
                assert result.file_size > 0

                # Verificar que se llamaron los métodos correctos
                mock_connector.connect.assert_called_once()
                mock_scanner_with_data.get_columns.assert_called_once()
                mock_connector.close.assert_called_once()

    def test_extract_mysql_success(self, db_config_mysql, generation_config):
        """Test extracción exitosa desde MySQL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "mysql_output.dbml")

            # Mock scanner con formato MySQL
            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("test_db", "users", "id", "int", None, None, "NO", None),
                (
                    "test_db",
                    "users",
                    "username",
                    "varchar(100)",
                    None,
                    None,
                    "NO",
                    None,
                ),
            ]
            mock_scanner.get_foreign_keys.return_value = []
            # MySQL usa formato de 2 campos: [table, column]
            mock_scanner.get_primary_keys.return_value = [
                ("users", "id"),
            ]
            # MySQL usa formato de 6 campos: [schema, table, index_name, index_type, is_unique, columns]
            mock_scanner.get_indexes.return_value = [
                ("test_db", "users", "PRIMARY", "BTREE", True, "id"),
            ]

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_mysql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.tables_count == 1
                assert result.columns_count == 2
                assert os.path.exists(output_path)

    def test_extract_mssql_success(self, db_config_mssql, generation_config):
        """Test extracción exitosa desde SQL Server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "mssql_output.dbml")

            # Mock scanner con formato MSSQL
            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("dbo", "employees", "EmployeeID", "int", None, None, "NO", None),
                (
                    "dbo",
                    "employees",
                    "FirstName",
                    "nvarchar(50)",
                    None,
                    None,
                    "NO",
                    None,
                ),
            ]
            mock_scanner.get_foreign_keys.return_value = []
            # MSSQL usa formato de 2 campos: [table, column]
            mock_scanner.get_primary_keys.return_value = [
                ("employees", "EmployeeID"),
            ]
            # MSSQL usa formato de 6 campos
            mock_scanner.get_indexes.return_value = [
                ("dbo", "employees", "PK_employees", "CLUSTERED", True, "EmployeeID"),
            ]

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_mssql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.tables_count == 1
                assert result.columns_count == 2
                assert os.path.exists(output_path)

    def test_extract_connection_error(self, db_config_postgresql, generation_config):
        """Test manejo de error de conexión."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "error_output.dbml")

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector:
                mock_connector = mock.MagicMock()
                mock_connector.connect.side_effect = ConnectionError(
                    "No se puede conectar a la BD"
                )
                mock_create_connector.return_value = mock_connector

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is False
                assert result.error_message is not None
                assert "No se puede conectar" in result.error_message
                assert result.tables_count == 0
                assert not os.path.exists(output_path)

    def test_extract_scanner_error(self, db_config_postgresql, generation_config):
        """Test manejo de error en el scanner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "scanner_error.dbml")

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_scanner = mock.MagicMock()
                mock_scanner.get_columns.side_effect = RuntimeError(
                    "Error al consultar metadata"
                )

                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is False
                assert "Error al consultar metadata" in result.error_message
                # Verificar que se intentó cerrar la conexión incluso con error
                mock_connector.close.assert_called_once()

    def test_extract_with_relationships(self, db_config_postgresql, generation_config):
        """Test extracción con relaciones entre tablas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "with_relationships.dbml")

            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("public", "users", "id", "integer", None, None, "NO", None),
                ("public", "posts", "id", "integer", None, None, "NO", None),
                ("public", "posts", "user_id", "integer", None, None, "NO", None),
            ]
            mock_scanner.get_foreign_keys.return_value = [
                ("fk_posts_user", "posts", "user_id", "users", "id"),
            ]
            mock_scanner.get_primary_keys.return_value = [
                ("public", "users", "id"),
                ("public", "posts", "id"),
            ]
            mock_scanner.get_indexes.return_value = []

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.tables_count == 2
                assert result.relationships_count == 1
                assert os.path.exists(output_path)

    def test_extract_filters_self_references(
        self, db_config_postgresql, generation_config
    ):
        """Test que filtra autorreferencias al mismo endpoint (incompatibles con DBML)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "self_ref.dbml")

            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("public", "departments", "id", "integer", None, None, "NO", None),
                (
                    "public",
                    "departments",
                    "parent_id",
                    "integer",
                    None,
                    None,
                    "YES",
                    None,
                ),
            ]
            # Autorreferencia inválida: departments.id -> departments.id (mismo endpoint exacto)
            mock_scanner.get_foreign_keys.return_value = [
                ("fk_self_ref", "departments", "id", "departments", "id"),
            ]
            mock_scanner.get_primary_keys.return_value = [
                ("public", "departments", "id"),
            ]
            mock_scanner.get_indexes.return_value = []

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                # La autorreferencia debe ser filtrada
                assert result.success is True
                assert result.tables_count == 1
                assert result.relationships_count == 0  # Filtrada

    def test_extract_creates_output_directory(
        self, db_config_postgresql, generation_config, mock_scanner_with_data
    ):
        """Test que crea el directorio de salida si no existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "subdir", "nested", "output.dbml")

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner_with_data

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(nested_path)

                assert result.success is True
                assert os.path.exists(nested_path)
                assert os.path.exists(os.path.dirname(nested_path))

    def test_extract_without_generation_config(
        self, db_config_postgresql, mock_scanner_with_data
    ):
        """Test extracción sin configuración de generación (usa defaults)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "no_config.dbml")

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner_with_data

                use_case = ExtractMetadata(
                    db_config_postgresql
                )  # Sin generation_config
                result = use_case.execute(output_path)

                assert result.success is True
                assert os.path.exists(output_path)

    def test_extract_empty_database(self, db_config_postgresql, generation_config):
        """Test extracción de base de datos vacía (sin tablas)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty_db.dbml")

            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = []
            mock_scanner.get_foreign_keys.return_value = []
            mock_scanner.get_primary_keys.return_value = []
            mock_scanner.get_indexes.return_value = []

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.tables_count == 0
                assert result.columns_count == 0
                assert result.relationships_count == 0
                assert os.path.exists(output_path)

    def test_extract_with_multiple_indexes(
        self, db_config_postgresql, generation_config
    ):
        """Test extracción con múltiples índices."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "multiple_indexes.dbml")

            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("public", "users", "id", "integer", None, None, "NO", None),
                (
                    "public",
                    "users",
                    "email",
                    "character varying",
                    255,
                    None,
                    "NO",
                    None,
                ),
                (
                    "public",
                    "users",
                    "username",
                    "character varying",
                    100,
                    None,
                    "NO",
                    None,
                ),
            ]
            mock_scanner.get_foreign_keys.return_value = []
            mock_scanner.get_primary_keys.return_value = [
                ("public", "users", "id"),
            ]
            mock_scanner.get_indexes.return_value = [
                (
                    "public",
                    "users",
                    "idx_email",
                    "CREATE INDEX idx_email ON public.users USING btree (email)",
                    True,
                ),
                (
                    "public",
                    "users",
                    "idx_username",
                    "CREATE INDEX idx_username ON public.users USING btree (username)",
                    False,
                ),
                (
                    "public",
                    "users",
                    "idx_email_username",
                    "CREATE INDEX idx_email_username ON public.users USING btree (email, username)",
                    False,
                ),
            ]

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.indexes_count == 3
                assert os.path.exists(output_path)

    def test_extract_normalizes_index_types(self, db_config_mysql, generation_config):
        """Test que normaliza los tipos de índices correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "index_types.dbml")

            mock_scanner = mock.MagicMock()
            mock_scanner.get_tables.return_value = []
            mock_scanner.get_columns.return_value = [
                ("test_db", "users", "id", "int", None, None, "NO", None),
            ]
            mock_scanner.get_foreign_keys.return_value = []
            mock_scanner.get_primary_keys.return_value = [("users", "id")]
            # MySQL retorna tipos como '1', '2', 'BTREE', 'HASH'
            mock_scanner.get_indexes.return_value = [
                ("test_db", "users", "idx1", "1", True, "id"),  # '1' -> 'btree'
                (
                    "test_db",
                    "users",
                    "idx2",
                    "BTREE",
                    False,
                    "id",
                ),  # 'BTREE' -> 'btree'
                ("test_db", "users", "idx3", "2", False, "id"),  # '2' -> 'hash'
            ]

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_mysql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is True
                assert result.indexes_count == 3

    def test_extract_closes_connection_on_error(
        self, db_config_postgresql, generation_config
    ):
        """Test que cierra la conexión incluso cuando hay error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "error.dbml")

            with mock.patch(
                "scavengr.application.extract.create_connector"
            ) as mock_create_connector, mock.patch(
                "scavengr.application.extract.create_scanner"
            ) as mock_create_scanner:

                mock_connector = mock.MagicMock()
                mock_scanner = mock.MagicMock()
                mock_scanner.get_columns.side_effect = Exception("Error crítico")

                mock_create_connector.return_value = mock_connector
                mock_create_scanner.return_value = mock_scanner

                use_case = ExtractMetadata(db_config_postgresql, generation_config)
                result = use_case.execute(output_path)

                assert result.success is False
                # Verificar que se intentó cerrar la conexión
                mock_connector.close.assert_called_once()

    def test_extraction_result_dataclass(self):
        """Test de la estructura del ExtractionResult."""
        result = ExtractionResult(
            success=True,
            output_path="/tmp/test.dbml",
            tables_count=5,
            columns_count=25,
            relationships_count=10,
            indexes_count=8,
            file_size=4096,
        )

        assert result.success is True
        assert result.output_path == "/tmp/test.dbml"
        assert result.tables_count == 5
        assert result.columns_count == 25
        assert result.relationships_count == 10
        assert result.indexes_count == 8
        assert result.file_size == 4096
        assert result.error_message is None

    def test_extraction_result_with_error(self):
        """Test de ExtractionResult con error."""
        result = ExtractionResult(success=False, error_message="Connection timeout")

        assert result.success is False
        assert result.error_message == "Connection timeout"
        assert result.tables_count == 0
        assert result.output_path == ""
