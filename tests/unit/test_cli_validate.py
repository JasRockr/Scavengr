"""Tests unitarios para el comando validate del CLI.

Pruebas para el comando `scavengr validate`:
- Validación exitosa de archivos DBML
- Detección de errores de sintaxis
- Manejo de warnings
- Validación de archivo no encontrado
"""

import argparse
import logging
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from scavengr import cli as cli_module
from scavengr.cli import ScavengrCLI


class TestValidateCommand:
    """Tests para el comando validate del CLI."""

    @pytest.fixture
    def cli(self):
        """Fixture que retorna instancia del CLI con logger inicializado."""
        # Inicializar logger global (necesario para cli.py)
        cli_module.logger = logging.getLogger("scavengr")
        cli_module.logger.setLevel(logging.INFO)
        handler = logging.NullHandler()
        cli_module.logger.addHandler(handler)
        return ScavengrCLI()

    @pytest.fixture
    def mock_validate_result_success(self):
        """Fixture que retorna resultado exitoso de validación."""
        result = mock.Mock()
        result.is_valid = True
        result.tables_count = 15
        result.relationships_count = 12
        result.has_warnings = mock.Mock(return_value=False)
        result.get_warnings = mock.Mock(return_value=[])
        result.get_errors = mock.Mock(return_value=[])
        return result

    @pytest.fixture
    def mock_validate_result_with_warnings(self):
        """Fixture que retorna resultado exitoso con advertencias."""
        warning1 = mock.Mock()
        warning1.message = "Tabla 'audit_log' parece temporal"

        warning2 = mock.Mock()
        warning2.message = "Índice BTREE sin columnas especificadas"

        result = mock.Mock()
        result.is_valid = True
        result.tables_count = 15
        result.relationships_count = 12
        result.has_warnings = mock.Mock(return_value=True)
        result.get_warnings = mock.Mock(return_value=[warning1, warning2])
        result.get_errors = mock.Mock(return_value=[])
        return result

    @pytest.fixture
    def mock_validate_result_failure(self):
        """Fixture que retorna resultado fallido de validación."""
        error1 = mock.Mock()
        error1.message = "Sintaxis inválida en definición de tabla"
        error1.line = 45

        error2 = mock.Mock()
        error2.message = "Relación referencia tabla inexistente 'users_old'"
        error2.line = None

        result = mock.Mock()
        result.is_valid = False
        result.tables_count = 0
        result.relationships_count = 0
        result.has_warnings = mock.Mock(return_value=False)
        result.get_warnings = mock.Mock(return_value=[])
        result.get_errors = mock.Mock(return_value=[error1, error2])
        return result

    def test_validate_success(self, cli, mock_validate_result_success):
        """Test: validate valida archivo DBML exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo temporal
            dbml_file = os.path.join(tmpdir, "schema.dbml")
            Path(dbml_file).write_text("Table users { id int [pk] }")

            args = argparse.Namespace(input=dbml_file)

            # Mock ValidateDBML use case
            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                mock_use_case = MockValidate.return_value
                mock_use_case.execute.return_value = mock_validate_result_success

                result = cli.validate_command(args)

                assert result is True
                mock_use_case.execute.assert_called_once_with(dbml_file)

    def test_validate_shows_warnings(self, cli, mock_validate_result_with_warnings):
        """Test: validate muestra advertencias encontradas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_file = os.path.join(tmpdir, "schema.dbml")
            Path(dbml_file).write_text("Table audit_log { id int [pk] }")

            args = argparse.Namespace(input=dbml_file)

            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                mock_use_case = MockValidate.return_value
                mock_use_case.execute.return_value = mock_validate_result_with_warnings

                # Capturar logs de warnings
                with mock.patch.object(cli_module.logger, "warning") as mock_warning:
                    result = cli.validate_command(args)

                    assert result is True
                    # Verificar que se loguearon las advertencias
                    assert mock_warning.call_count >= 2
                    warning_calls = [str(call) for call in mock_warning.call_args_list]
                    assert any(
                        "advertencias encontradas" in call for call in warning_calls
                    )

    def test_validate_shows_errors(self, cli, mock_validate_result_failure):
        """Test: validate muestra errores encontrados."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_file = os.path.join(tmpdir, "invalid.dbml")
            Path(dbml_file).write_text("Table { invalid syntax")

            args = argparse.Namespace(input=dbml_file)

            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                mock_use_case = MockValidate.return_value
                mock_use_case.execute.return_value = mock_validate_result_failure

                # Capturar logs de errores
                with mock.patch.object(cli_module.logger, "error") as mock_error:
                    result = cli.validate_command(args)

                    assert result is False
                    # Verificar que se loguearon los errores
                    assert mock_error.call_count >= 2
                    error_calls = [str(call) for call in mock_error.call_args_list]
                    assert any("errores encontrados" in call for call in error_calls)

    def test_validate_file_not_found(self, cli):
        """Test: validate maneja correctamente archivo no encontrado."""
        args = argparse.Namespace(input="/path/to/nonexistent.dbml")

        # validate_file_exists lanzará FileNotFoundError
        with mock.patch("scavengr.cli.validate_file_exists") as mock_validate_file:
            mock_validate_file.side_effect = FileNotFoundError("Archivo no encontrado")

            result = cli.validate_command(args)

            assert result is False

    def test_validate_logs_statistics(self, cli, mock_validate_result_success):
        """Test: validate registra estadísticas de validación."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_file = os.path.join(tmpdir, "schema.dbml")
            Path(dbml_file).write_text("Table users { id int [pk] }")

            args = argparse.Namespace(input=dbml_file)

            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                mock_use_case = MockValidate.return_value
                mock_use_case.execute.return_value = mock_validate_result_success

                # Capturar logs
                with mock.patch.object(cli_module.logger, "info") as mock_info:
                    result = cli.validate_command(args)

                    assert result is True
                    # Verificar que se loguearon estadísticas
                    info_calls = [str(call) for call in mock_info.call_args_list]
                    assert any("tablas" in call for call in info_calls)
                    assert any("relaciones" in call for call in info_calls)

    def test_validate_handles_exception(self, cli):
        """Test: validate maneja excepciones inesperadas correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_file = os.path.join(tmpdir, "schema.dbml")
            Path(dbml_file).write_text("Table users { id int [pk] }")

            args = argparse.Namespace(input=dbml_file)

            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                MockValidate.side_effect = Exception("Unexpected error")

                result = cli.validate_command(args)

                assert result is False

    def test_validate_error_with_line_number(self, cli):
        """Test: validate muestra número de línea cuando está disponible."""
        error_with_line = mock.Mock()
        error_with_line.message = "Sintaxis inválida"
        error_with_line.line = 42

        result = mock.Mock()
        result.is_valid = False
        result.tables_count = 0
        result.relationships_count = 0
        result.has_warnings = mock.Mock(return_value=False)
        result.get_warnings = mock.Mock(return_value=[])
        result.get_errors = mock.Mock(return_value=[error_with_line])

        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_file = os.path.join(tmpdir, "schema.dbml")
            Path(dbml_file).write_text("Table users { id int [pk] }")

            args = argparse.Namespace(input=dbml_file)

            with mock.patch("scavengr.application.ValidateDBML") as MockValidate:
                mock_use_case = MockValidate.return_value
                mock_use_case.execute.return_value = result

                # Capturar logs de errores
                with mock.patch.object(cli_module.logger, "error") as mock_error:
                    result = cli.validate_command(args)

                    assert result is False
                    # Verificar que se incluyó el número de línea
                    error_calls = [str(call) for call in mock_error.call_args_list]
                    assert any("Línea 42" in call for call in error_calls)
