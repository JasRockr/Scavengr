"""Tests unitarios para el comando extract del CLI.

Pruebas para el comando `scavengr extract`:
- Creación exitosa de archivos DBML
- Validación de configuración de BD
- Manejo de errores de conexión
- Uso de archivos .env personalizados
- Logging de estadísticas
"""

import argparse
import logging
import os
import tempfile
from unittest import mock

import pytest

from scavengr import cli as cli_module
from scavengr.cli import ScavengrCLI


class TestExtractCommand:
    """Tests para el comando extract del CLI."""

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
    def mock_env_config(self):
        """Fixture que retorna configuración de BD válida."""
        return {
            "db_config": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
            },
            "generation_config": {
                "source_system": {"name": "TestSystem"},
                "file_prefix": "test",
            },
        }

    @pytest.fixture
    def mock_extract_result_success(self):
        """Fixture que retorna resultado exitoso de extracción."""
        result = mock.Mock()
        result.success = True
        result.tables_count = 10
        result.columns_count = 50
        result.relationships_count = 8
        result.output_path = "/tmp/test_extracted.dbml"
        result.file_size = 1024
        return result

    @pytest.fixture
    def mock_extract_result_failure(self):
        """Fixture que retorna resultado fallido de extracción."""
        result = mock.Mock()
        result.success = False
        result.error_message = "Connection refused"
        return result

    def test_extract_creates_dbml_file(
        self, cli, mock_env_config, mock_extract_result_success
    ):
        """Test: extract crea archivo DBML exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "schema.dbml")
            args = argparse.Namespace(
                output=output_file, env_file=None, cache=False, force_refresh=False
            )

            # Mock EnvConfigManager (se importa dentro de la función)
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                mock_env_manager = MockEnvConfig.return_value
                mock_env_manager.validate_config.return_value = {
                    "valid": True,
                    "issues": [],
                    "warnings": [],
                }
                mock_env_manager.get_db_config.return_value = mock_env_config[
                    "db_config"
                ]
                mock_env_manager.get_generation_config.return_value = mock_env_config[
                    "generation_config"
                ]

                # Mock ExtractMetadata use case (se importa desde scavengr.application)
                with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                    mock_use_case = MockExtract.return_value
                    mock_use_case.execute.return_value = mock_extract_result_success

                    result = cli.extract_command(args)

                    assert result is True
                    # Verificar que se llamó con los 4 parámetros (incluyendo cache)
                    MockExtract.assert_called_once_with(
                        mock_env_config["db_config"],
                        mock_env_config["generation_config"],
                        use_cache=False,
                        force_refresh=False,
                    )
                    mock_use_case.execute.assert_called_once_with(output_file)

    def test_extract_uses_default_output_filename(
        self, cli, mock_env_config, mock_extract_result_success
    ):
        """Test: extract usa nombre por defecto si no se especifica output."""
        args = argparse.Namespace(
            output=None, env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": True,
                "issues": [],
                "warnings": [],
            }
            mock_env_manager.get_db_config.return_value = mock_env_config["db_config"]
            mock_env_manager.get_generation_config.return_value = mock_env_config[
                "generation_config"
            ]

            with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                mock_use_case = MockExtract.return_value
                mock_use_case.execute.return_value = mock_extract_result_success

                result = cli.extract_command(args)

                assert result is True
                # Verificar que se llamó con el nombre por defecto
                expected_filename = f"{mock_env_config['generation_config']['file_prefix']}_extracted.dbml"
                mock_use_case.execute.assert_called_once_with(expected_filename)

    def test_extract_validates_db_config(self, cli):
        """Test: extract valida la configuración de BD antes de procesar."""
        args = argparse.Namespace(
            output="test.dbml", env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": False,
                "issues": ["DB_HOST no configurado", "DB_TYPE inválido"],
                "warnings": [],
            }

            result = cli.extract_command(args)

            assert result is False
            mock_env_manager.validate_config.assert_called_once()

    def test_extract_handles_connection_error(
        self, cli, mock_env_config, mock_extract_result_failure
    ):
        """Test: extract maneja correctamente errores de conexión."""
        args = argparse.Namespace(
            output="test.dbml", env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": True,
                "issues": [],
                "warnings": [],
            }
            mock_env_manager.get_db_config.return_value = mock_env_config["db_config"]
            mock_env_manager.get_generation_config.return_value = mock_env_config[
                "generation_config"
            ]

            with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                mock_use_case = MockExtract.return_value
                mock_use_case.execute.return_value = mock_extract_result_failure

                result = cli.extract_command(args)

                assert result is False

    def test_extract_shows_warnings(
        self, cli, mock_env_config, mock_extract_result_success
    ):
        """Test: extract muestra warnings de configuración."""
        args = argparse.Namespace(
            output="test.dbml", env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": True,
                "issues": [],
                "warnings": ["Puerto no especificado, usando 5432 por defecto"],
            }
            mock_env_manager.get_db_config.return_value = mock_env_config["db_config"]
            mock_env_manager.get_generation_config.return_value = mock_env_config[
                "generation_config"
            ]

            with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                mock_use_case = MockExtract.return_value
                mock_use_case.execute.return_value = mock_extract_result_success

                # Capturar logs
                with mock.patch.object(cli_module.logger, "warning") as mock_warning:
                    result = cli.extract_command(args)

                    assert result is True
                    mock_warning.assert_called_once()
                    assert "Puerto no especificado" in str(mock_warning.call_args)

    def test_extract_uses_custom_env_file(
        self, cli, mock_env_config, mock_extract_result_success
    ):
        """Test: extract puede usar archivo .env personalizado."""
        custom_env = "/path/to/.env.production"
        args = argparse.Namespace(
            output="test.dbml", env_file=custom_env, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": True,
                "issues": [],
                "warnings": [],
            }
            mock_env_manager.get_db_config.return_value = mock_env_config["db_config"]
            mock_env_manager.get_generation_config.return_value = mock_env_config[
                "generation_config"
            ]

            with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                mock_use_case = MockExtract.return_value
                mock_use_case.execute.return_value = mock_extract_result_success

                result = cli.extract_command(args)

                assert result is True
                # Verificar que EnvConfigManager se inicializó con el archivo correcto
                MockEnvConfig.assert_called_once_with(custom_env)

    def test_extract_handles_exception(self, cli):
        """Test: extract maneja excepciones inesperadas correctamente."""
        args = argparse.Namespace(
            output="test.dbml", env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            MockEnvConfig.side_effect = Exception("Unexpected error")

            result = cli.extract_command(args)

            assert result is False

    def test_extract_logs_statistics(
        self, cli, mock_env_config, mock_extract_result_success
    ):
        """Test: extract registra estadísticas de extracción."""
        args = argparse.Namespace(
            output="test.dbml", env_file=None, cache=False, force_refresh=False
        )

        with mock.patch("scavengr.config.env_config.EnvConfigManager") as MockEnvConfig:
            mock_env_manager = MockEnvConfig.return_value
            mock_env_manager.validate_config.return_value = {
                "valid": True,
                "issues": [],
                "warnings": [],
            }
            mock_env_manager.get_db_config.return_value = mock_env_config["db_config"]
            mock_env_manager.get_generation_config.return_value = mock_env_config[
                "generation_config"
            ]

            with mock.patch("scavengr.application.ExtractMetadata") as MockExtract:
                mock_use_case = MockExtract.return_value
                mock_use_case.execute.return_value = mock_extract_result_success

                # Capturar logs
                with mock.patch.object(cli_module.logger, "info") as mock_info:
                    result = cli.extract_command(args)

                    assert result is True
                    # Verificar que se loguearon estadísticas
                    info_calls = [str(call) for call in mock_info.call_args_list]
                    assert any("tablas" in call for call in info_calls)
                    assert any("columnas" in call for call in info_calls)
                    assert any("relaciones" in call for call in info_calls)
