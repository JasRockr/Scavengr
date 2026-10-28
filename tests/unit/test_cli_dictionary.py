"""
Tests unitarios para el comando CLI 'dictionary'.

Este módulo contiene tests para verificar el comportamiento del comando
'scavengr dictionary', que genera diccionarios de datos desde archivos DBML.

Tests incluidos:
- Generación exitosa de diccionario
- Detección automática de formato de salida
- Validación de archivo de entrada
- Validación de permisos de escritura
- Manejo de errores de generación
- Logging de estadísticas
- Manejo de excepciones inesperadas

Author: Jason Rivera
Date: 2025-11-18
"""

import logging
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Import CLI module
import scavengr.cli as cli_module


class TestDictionaryCommand:
    """Tests para el comando 'dictionary' del CLI."""

    @pytest.fixture
    def cli(self):
        """Fixture que proporciona instancia del CLI con logger configurado."""
        cli_instance = cli_module.ScavengrCLI()
        # Inicializar logger global con NullHandler para evitar warnings
        cli_module.logger = logging.getLogger("test_cli")
        cli_module.logger.addHandler(logging.NullHandler())
        return cli_instance

    @pytest.fixture
    def mock_generation_config(self):
        """Fixture que proporciona configuración de generación mock."""
        return {
            "system_name": "TestSystem",
            "output_prefix": "test",
            "default_sensitivity": "MEDIO",
        }

    @pytest.fixture
    def mock_dictionary_result_success(self):
        """Fixture que proporciona resultado exitoso de generación de diccionario."""
        result = mock.MagicMock()
        result.success = True
        result.output_path = "/tmp/test_dictionary.xlsx"
        result.entries_count = 150
        result.format = "xlsx"
        result.file_size = 45678
        result.error_message = None
        return result

    @pytest.fixture
    def mock_dictionary_result_failure(self):
        """Fixture que proporciona resultado fallido de generación de diccionario."""
        result = mock.MagicMock()
        result.success = False
        result.output_path = None
        result.entries_count = 0
        result.format = None
        result.file_size = 0
        result.error_message = "Error al procesar esquema DBML"
        return result

    def test_dictionary_creates_file(
        self, cli, mock_generation_config, mock_dictionary_result_success
    ):
        """Test que dictionary crea archivo de diccionario exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None  # Detección automática
            args.env_file = None

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_success

                    # Ejecutar comando
                    result = cli.dictionary_command(args)

                    # Verificar resultado
                    assert result is True
                    MockGenerateDictionary.assert_called_once_with(
                        config=mock_generation_config
                    )
                    mock_use_case.execute.assert_called_once_with(
                        input_path=str(input_file),
                        output_path=str(output_file),
                        output_format="excel",
                    )

    def test_dictionary_detects_format_csv(
        self, cli, mock_generation_config, mock_dictionary_result_success
    ):
        """Test que dictionary detecta formato CSV automáticamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.csv"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None  # Detección automática
            args.env_file = None

            # Actualizar resultado mock para CSV
            mock_dictionary_result_success.format = "csv"

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_success

                    # Ejecutar comando
                    result = cli.dictionary_command(args)

                    # Verificar resultado
                    assert result is True
                    mock_use_case.execute.assert_called_once()
                    call_args = mock_use_case.execute.call_args[1]
                    assert call_args["output_format"] == "csv"

    def test_dictionary_detects_format_json(
        self, cli, mock_generation_config, mock_dictionary_result_success
    ):
        """Test que dictionary detecta formato JSON automáticamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.json"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None  # Detección automática
            args.env_file = None

            # Actualizar resultado mock para JSON
            mock_dictionary_result_success.format = "json"

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_success

                    # Ejecutar comando
                    result = cli.dictionary_command(args)

                    # Verificar resultado
                    assert result is True
                    mock_use_case.execute.assert_called_once()
                    call_args = mock_use_case.execute.call_args[1]
                    assert call_args["output_format"] == "json"

    def test_dictionary_validates_input_file(self, cli):
        """Test que dictionary valida existencia de archivo de entrada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "nonexistent.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"

            # Configurar argumentos con archivo inexistente
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = None

            # Ejecutar comando - debe fallar en validación
            result = cli.dictionary_command(args)

            # Verificar que retorna False
            assert result is False

    def test_dictionary_validates_write_permissions(self, cli):
        """Test que dictionary valida permisos de escritura."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            # Ruta inválida para escritura (en Windows, ruta de sistema)
            output_file = Path("C:\\Windows\\System32\\test_dictionary.xlsx")

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = None

            # Ejecutar comando - debe fallar en validación de permisos
            result = cli.dictionary_command(args)

            # Verificar que retorna False
            assert result is False

    def test_dictionary_handles_generation_failure(
        self, cli, mock_generation_config, mock_dictionary_result_failure
    ):
        """Test que dictionary maneja errores de generación correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = None

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_failure

                    # Ejecutar comando
                    result = cli.dictionary_command(args)

                    # Verificar resultado
                    assert result is False

    def test_dictionary_logs_statistics(
        self, cli, mock_generation_config, mock_dictionary_result_success
    ):
        """Test que dictionary registra estadísticas correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = None

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_success

                    # Capturar logs
                    with mock.patch.object(cli_module.logger, "info") as mock_logger:
                        # Ejecutar comando
                        result = cli.dictionary_command(args)

                        # Verificar resultado
                        assert result is True

                        # Verificar que se registraron estadísticas
                        info_calls = [call[0][0] for call in mock_logger.call_args_list]
                        assert any("150 entradas" in str(call) for call in info_calls)
                        assert any("XLSX" in str(call).upper() for call in info_calls)
                        assert any("45,678 bytes" in str(call) for call in info_calls)

    def test_dictionary_handles_exception(self, cli, mock_generation_config):
        """Test que dictionary maneja excepciones inesperadas correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = None

            # Mock de EnvConfigManager que lanza excepción
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                # Configurar mock para lanzar excepción
                MockEnvConfig.side_effect = Exception("Error de conexión simulado")

                # Ejecutar comando
                result = cli.dictionary_command(args)

                # Verificar que retorna False
                assert result is False

    def test_dictionary_uses_custom_env_file(
        self, cli, mock_generation_config, mock_dictionary_result_success
    ):
        """Test que dictionary usa archivo .env personalizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_dictionary.xlsx"
            custom_env = Path(tmpdir) / ".env.custom"

            # Crear archivos mock
            input_file.write_text("Table users { id int [pk] }")
            custom_env.write_text("DB_TYPE=postgresql\nDB_HOST=localhost")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)
            args.format = None
            args.env_file = str(custom_env)

            # Mock de EnvConfigManager y GenerateDictionary
            with mock.patch(
                "scavengr.config.env_config.EnvConfigManager"
            ) as MockEnvConfig:
                with mock.patch(
                    "scavengr.application.GenerateDictionary"
                ) as MockGenerateDictionary:
                    # Configurar mocks
                    mock_env_instance = MockEnvConfig.return_value
                    mock_env_instance.get_generation_config.return_value = (
                        mock_generation_config
                    )

                    mock_use_case = MockGenerateDictionary.return_value
                    mock_use_case.execute.return_value = mock_dictionary_result_success

                    # Ejecutar comando
                    result = cli.dictionary_command(args)

                    # Verificar resultado
                    assert result is True
                    MockEnvConfig.assert_called_once_with(str(custom_env))
