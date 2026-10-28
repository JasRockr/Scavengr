"""
Tests para manejo de errores en Scavengr.

Verifica que todas las excepciones personalizadas se lancen correctamente
en los escenarios apropiados y que contengan la información necesaria.

Author: Jason Rivera
Date: 2025-11-18
"""

from unittest import mock

import pytest

from scavengr.utils.exceptions import (
    FileNotFoundError,
    InvalidFormatError,
    ProcessingError,
    ScavengrError,
    ValidationError,
)
from scavengr.utils.validators import (
    validate_file_exists,
    validate_input_file_format,
    validate_output_format,
    validate_write_permissions,
)

# ===================================================================
# TESTS DE EXCEPCIONES BASE
# ===================================================================


class TestScavengrErrorException:
    """Tests para la excepción base ScavengrError."""

    def test_scavengr_error_is_exception(self):
        """ScavengrError hereda de Exception."""
        assert issubclass(ScavengrError, Exception)

    def test_scavengr_error_can_be_raised(self):
        """ScavengrError puede ser lanzada con mensaje."""
        with pytest.raises(ScavengrError) as exc_info:
            raise ScavengrError("Error de prueba")

        assert str(exc_info.value) == "Error de prueba"

    def test_scavengr_error_can_be_caught_as_exception(self):
        """ScavengrError puede ser capturada como Exception."""
        try:
            raise ScavengrError("Error genérico")
        except Exception as e:
            assert isinstance(e, ScavengrError)


# ===================================================================
# TESTS DE FileNotFoundError
# ===================================================================


class TestFileNotFoundErrorException:
    """Tests para la excepción FileNotFoundError."""

    def test_file_not_found_error_inherits_from_scavengr_error(self):
        """FileNotFoundError hereda de ScavengrError."""
        assert issubclass(FileNotFoundError, ScavengrError)

    def test_file_not_found_error_with_filepath_only(self):
        """FileNotFoundError puede ser creada solo con filepath."""
        error = FileNotFoundError("/path/to/missing.dbml")

        assert error.filepath == "/path/to/missing.dbml"
        assert error.file_type == "archivo"
        assert "Archivo no encontrado: /path/to/missing.dbml" in str(error)

    def test_file_not_found_error_with_file_type(self):
        """FileNotFoundError puede especificar tipo de archivo."""
        error = FileNotFoundError("/path/to/missing.dbml", "DBML")

        assert error.filepath == "/path/to/missing.dbml"
        assert error.file_type == "DBML"
        # El mensaje capitaliza solo la primera letra
        assert "no encontrado: /path/to/missing.dbml" in str(error)

    def test_file_not_found_error_raised_by_validator(self, tmp_path):
        """validate_file_exists lanza FileNotFoundError si archivo no existe."""
        missing_file = tmp_path / "nonexistent.dbml"

        with pytest.raises(FileNotFoundError) as exc_info:
            validate_file_exists(str(missing_file), "DBML")

        assert exc_info.value.filepath == str(missing_file)
        assert exc_info.value.file_type == "DBML"


# ===================================================================
# TESTS DE InvalidFormatError
# ===================================================================


class TestInvalidFormatErrorException:
    """Tests para la excepción InvalidFormatError."""

    def test_invalid_format_error_inherits_from_scavengr_error(self):
        """InvalidFormatError hereda de ScavengrError."""
        assert issubclass(InvalidFormatError, ScavengrError)

    def test_invalid_format_error_with_format_and_valid_formats(self):
        """InvalidFormatError almacena formato y formatos válidos."""
        error = InvalidFormatError(".txt", ["csv", "xlsx", "json"])

        assert error.format_provided == ".txt"
        assert error.valid_formats == ["csv", "xlsx", "json"]
        assert "Formato no soportado: .txt" in str(error)
        assert "csv, xlsx, json" in str(error)

    def test_invalid_format_error_message_clarity(self):
        """InvalidFormatError tiene mensaje descriptivo."""
        error = InvalidFormatError(".pdf", ["dbml"])

        message = str(error)
        assert ".pdf" in message
        assert "dbml" in message
        assert "Formato no soportado" in message

    def test_invalid_format_error_raised_by_validator(self, tmp_path):
        """validate_output_format lanza InvalidFormatError si formato no soportado."""
        output_file = tmp_path / "output.txt"

        with pytest.raises(InvalidFormatError) as exc_info:
            validate_output_format(str(output_file))

        assert exc_info.value.format_provided == ".txt"
        # Los formatos válidos incluyen descripción como "csv (.csv)"
        assert any("csv" in fmt for fmt in exc_info.value.valid_formats)
        assert any("xlsx" in fmt for fmt in exc_info.value.valid_formats)


# ===================================================================
# TESTS DE ProcessingError
# ===================================================================


class TestProcessingErrorException:
    """Tests para la excepción ProcessingError."""

    def test_processing_error_inherits_from_scavengr_error(self):
        """ProcessingError hereda de ScavengrError."""
        assert issubclass(ProcessingError, ScavengrError)

    def test_processing_error_with_operation_and_details(self):
        """ProcessingError almacena operación y detalles."""
        error = ProcessingError("parseo DBML", "sintaxis inválida en línea 42")

        assert error.operation == "parseo DBML"
        assert error.details == "sintaxis inválida en línea 42"
        assert "Error procesando parseo DBML" in str(error)
        assert "sintaxis inválida en línea 42" in str(error)

    def test_processing_error_message_format(self):
        """ProcessingError tiene formato de mensaje consistente."""
        error = ProcessingError("extracción", "conexión perdida")

        message = str(error)
        assert message.startswith("Error procesando")
        assert "extracción" in message
        assert "conexión perdida" in message

    def test_processing_error_for_database_operations(self):
        """ProcessingError puede describir errores de BD."""
        error = ProcessingError(
            "conexión a PostgreSQL", "timeout después de 30 segundos"
        )

        assert "PostgreSQL" in str(error)
        assert "timeout" in str(error)

    def test_processing_error_for_parsing_operations(self):
        """ProcessingError puede describir errores de parseo."""
        error = ProcessingError(
            "parseo de relaciones",
            "relación circular detectada: tabla_a -> tabla_b -> tabla_a",
        )

        assert "parseo de relaciones" in str(error)
        assert "relación circular" in str(error)


# ===================================================================
# TESTS DE ValidationError
# ===================================================================


class TestValidationErrorException:
    """Tests para la excepción ValidationError."""

    def test_validation_error_inherits_from_scavengr_error(self):
        """ValidationError hereda de ScavengrError."""
        assert issubclass(ValidationError, ScavengrError)

    def test_validation_error_with_message(self):
        """ValidationError puede ser creada con mensaje descriptivo."""
        error = ValidationError("Sin permisos de escritura en /output")

        assert "Sin permisos de escritura en /output" in str(error)

    def test_validation_error_for_permission_issues(self):
        """ValidationError describe errores de permisos."""
        error = ValidationError("No se puede crear el directorio /protected")

        assert "directorio" in str(error)
        assert "/protected" in str(error)

    def test_validation_error_for_empty_files(self):
        """ValidationError describe archivos vacíos."""
        error = ValidationError("El archivo schema.dbml está vacío")

        assert "vacío" in str(error)
        assert "schema.dbml" in str(error)

    def test_validation_error_raised_by_write_permissions(self, tmp_path):
        """validate_write_permissions lanza ValidationError si no hay permisos."""
        protected_dir = tmp_path / "protected"
        protected_dir.mkdir()
        output_file = protected_dir / "output.dbml"

        # Mock para simular falta de permisos
        with mock.patch("os.access", return_value=False):
            with pytest.raises(ValidationError) as exc_info:
                validate_write_permissions(str(output_file))

            assert "permisos" in str(exc_info.value).lower()


# ===================================================================
# TESTS DE ESCENARIOS DE ERROR - VALIDADORES
# ===================================================================


class TestValidatorErrorScenarios:
    """Tests de escenarios de error en validadores."""

    def test_validate_file_exists_nonexistent_file(self, tmp_path):
        """validate_file_exists lanza error si archivo no existe."""
        missing = tmp_path / "missing.dbml"

        with pytest.raises(FileNotFoundError) as exc_info:
            validate_file_exists(str(missing))

        assert exc_info.value.filepath == str(missing)

    def test_validate_output_format_unsupported_extension(self, tmp_path):
        """validate_output_format lanza error para extensión no soportada."""
        output = tmp_path / "output.pdf"

        with pytest.raises(InvalidFormatError) as exc_info:
            validate_output_format(str(output))

        assert exc_info.value.format_provided == ".pdf"

    def test_validate_output_format_with_format_override_invalid(self, tmp_path):
        """validate_output_format lanza error si override es inválido."""
        output = tmp_path / "output.xlsx"

        with pytest.raises(InvalidFormatError) as exc_info:
            validate_output_format(str(output), format_override="xml")

        assert exc_info.value.format_provided == "xml"

    def test_validate_input_file_format_invalid_extension(self, tmp_path):
        """validate_input_file_format lanza error para formato inválido."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("content")

        with pytest.raises(ValidationError) as exc_info:
            validate_input_file_format(str(input_file))

        # El mensaje usa "formato de archivo no soportado"
        assert "formato" in str(exc_info.value).lower()
        assert "no soportado" in str(exc_info.value).lower()

    def test_validate_input_file_format_empty_file(self, tmp_path):
        """validate_input_file_format lanza error para archivo vacío."""
        empty_file = tmp_path / "empty.dbml"
        empty_file.write_text("")

        with pytest.raises(ValidationError) as exc_info:
            validate_input_file_format(str(empty_file))

        # El mensaje usa "esta vacio" (sin acento)
        assert "vacio" in str(exc_info.value).lower()


# ===================================================================
# TESTS DE ESCENARIOS DE ERROR - CONEXIONES BD
# ===================================================================


class TestDatabaseConnectionErrors:
    """Tests de errores de conexión a base de datos."""

    def test_postgresql_connection_error_simulation(self):
        """Simular error de conexión PostgreSQL."""
        from scavengr.infrastructure.database.connector import PostgreSQLConnector

        bad_config = {
            "host": "invalid-host.example.com",
            "database": "nonexistent_db",
            "user": "invalid_user",
            "password": "wrong_password",
            "port": 5432,
        }

        connector = PostgreSQLConnector(bad_config)

        # La conexión debería fallar o retornar None
        with pytest.raises((Exception, ConnectionError)):
            connection = connector.connect()
            if connection is None:
                raise ConnectionError("Failed to connect")

    def test_mysql_connection_error_simulation(self):
        """Simular error de conexión MySQL."""
        from scavengr.infrastructure.database.connector import MySQLConnector

        bad_config = {
            "host": "invalid-host.example.com",
            "database": "nonexistent_db",
            "user": "invalid_user",
            "password": "wrong_password",
            "port": 3306,
        }

        connector = MySQLConnector(bad_config)

        # La conexión debería fallar o retornar None
        with pytest.raises((Exception, ConnectionError)):
            connection = connector.connect()
            if connection is None:
                raise ConnectionError("Failed to connect")

    def test_mssql_connection_error_simulation(self):
        """Simular error de conexión SQL Server."""
        from scavengr.infrastructure.database.connector import MSSQLConnector

        bad_config = {
            "host": "invalid-host.example.com",
            "database": "nonexistent_db",
            "user": "invalid_user",
            "password": "wrong_password",
            "port": 1433,
            "driver": "ODBC Driver 17 for SQL Server",
        }

        connector = MSSQLConnector(bad_config)

        # La conexión debería fallar o retornar None
        with pytest.raises((Exception, ConnectionError)):
            connection = connector.connect()
            if connection is None:
                raise ConnectionError("Failed to connect")


# ===================================================================
# TESTS DE ESCENARIOS DE ERROR - PARSEO DBML
# ===================================================================


class TestDBMLParsingErrors:
    """Tests de errores de parseo DBML."""

    def test_dbml_parser_file_not_found(self, tmp_path):
        """DBMLParser lanza error si archivo no existe."""
        from scavengr.infrastructure.parsers.dbml_parser import DBMLParser

        missing_file = tmp_path / "nonexistent.dbml"

        parser = DBMLParser(str(missing_file))

        # El parser debería lanzar FileNotFoundError al parsear
        with pytest.raises((FileNotFoundError, Exception)):
            parser.parse()

    def test_dbml_parser_invalid_syntax(self, tmp_path):
        """DBMLParser maneja sintaxis DBML inválida."""
        from scavengr.infrastructure.parsers.dbml_parser import DBMLParser

        invalid_dbml = tmp_path / "invalid.dbml"
        invalid_dbml.write_text(
            """
        Table usuarios {{{
            id int [pk]
            # Sintaxis inválida: llaves sin cerrar
        """
        )

        parser = DBMLParser(str(invalid_dbml))

        # El parser debería manejar el error sin crash
        try:
            result = parser.parse()
            # Si no lanza excepción, debería retornar schema vacío o incompleto
            assert result is not None
        except Exception as e:
            # Si lanza excepción, debería ser descriptiva
            assert str(e) != ""

    def test_dbml_parser_empty_file(self, tmp_path):
        """DBMLParser maneja archivo DBML vacío."""
        from scavengr.infrastructure.parsers.dbml_parser import DBMLParser

        empty_dbml = tmp_path / "empty.dbml"
        empty_dbml.write_text("")

        parser = DBMLParser(str(empty_dbml))

        # El parser lanza ValueError para archivos vacíos
        with pytest.raises(ValueError) as exc_info:
            parser.parse()

        assert "vacío" in str(exc_info.value).lower()


# ===================================================================
# TESTS DE ESCENARIOS DE ERROR - EXPORTACIÓN
# ===================================================================


class TestExportErrors:
    """Tests de errores durante exportación."""

    def test_output_writer_permission_error(self, tmp_path):
        """OutputWriter maneja errores de permisos."""
        from scavengr.infrastructure.exporters.output_writer import OutputWriter

        protected_file = tmp_path / "protected.xlsx"

        # Crear escritor con parámetros requeridos
        writer = OutputWriter(output_path=str(protected_file), output_format="excel")

        # Mock para simular falta de permisos
        with mock.patch.object(
            writer,
            "_validate_output_permissions",
            side_effect=PermissionError("Access denied"),
        ):
            with pytest.raises(PermissionError):
                writer.write([{"col1": "val1"}])

    def test_output_writer_disk_full_simulation(self, tmp_path):
        """OutputWriter maneja errores de disco lleno."""
        from scavengr.infrastructure.exporters.output_writer import OutputWriter

        output_file = tmp_path / "output.json"

        # Crear escritor con parámetros requeridos
        writer = OutputWriter(output_path=str(output_file), output_format="json")

        # Mock para simular disco lleno en escritura JSON
        # El OutputWriter captura OSError y lo re-lanza como Exception
        with mock.patch(
            "builtins.open", side_effect=OSError("No space left on device")
        ):
            with pytest.raises(Exception) as exc_info:
                writer.write([{"col1": "val1"}])

            assert "No space left on device" in str(exc_info.value)


# ===================================================================
# TESTS DE PROPAGACIÓN DE ERRORES
# ===================================================================


class TestErrorPropagation:
    """Tests de propagación de errores a través de las capas."""

    def test_error_propagation_from_validator_to_cli(self, tmp_path):
        """Errores de validación se propagan al CLI."""
        missing_file = tmp_path / "missing.dbml"

        # Simular llamada desde CLI
        with pytest.raises(FileNotFoundError) as exc_info:
            validate_file_exists(str(missing_file), "DBML")

        # El error debería contener información útil para el usuario
        assert exc_info.value.filepath == str(missing_file)
        # El mensaje capitaliza solo la primera letra
        assert "dbml" in str(exc_info.value).lower()

    def test_error_propagation_preserves_context(self):
        """Errores preservan contexto al propagarse."""
        original_error = ProcessingError("extracción", "timeout después de 30s")

        try:
            raise original_error
        except ProcessingError as e:
            # Al capturar, el contexto debe estar intacto
            assert e.operation == "extracción"
            assert e.details == "timeout después de 30s"
            assert "extracción" in str(e)
            assert "timeout" in str(e)


# ===================================================================
# TESTS DE MENSAJES DE ERROR
# ===================================================================


class TestErrorMessages:
    """Tests de calidad de mensajes de error."""

    def test_file_not_found_message_is_descriptive(self):
        """Mensajes de FileNotFoundError son descriptivos."""
        error = FileNotFoundError("/path/to/schema.dbml", "DBML")
        message = str(error)

        # El mensaje capitaliza solo la primera letra
        assert "dbml" in message.lower()
        assert "/path/to/schema.dbml" in message
        assert "no encontrado" in message.lower()

    def test_invalid_format_message_suggests_alternatives(self):
        """Mensajes de InvalidFormatError sugieren alternativas."""
        error = InvalidFormatError(".txt", ["csv", "xlsx", "json"])
        message = str(error)

        assert ".txt" in message
        assert "csv" in message
        assert "xlsx" in message
        assert "json" in message

    def test_processing_error_message_explains_what_failed(self):
        """Mensajes de ProcessingError explican qué falló."""
        error = ProcessingError("conexión a BD", "host no alcanzable")
        message = str(error)

        assert "conexión a BD" in message
        assert "host no alcanzable" in message
        assert "Error procesando" in message

    def test_validation_error_message_is_actionable(self):
        """Mensajes de ValidationError son accionables."""
        error = ValidationError("Sin permisos de escritura en /output")
        message = str(error)

        assert "permisos" in message.lower()
        assert "/output" in message
