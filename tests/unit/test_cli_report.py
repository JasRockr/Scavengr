"""
Tests unitarios para el comando CLI 'report'.

Este módulo contiene tests para verificar el comportamiento del comando
'scavengr report', que genera informes analíticos desde archivos DBML.

Tests incluidos:
- Generación exitosa de informe
- Validación de archivo de entrada
- Logging de estadísticas (tablas, columnas, quality score)
- Manejo de errores de generación
- Manejo de excepciones inesperadas
- Detección de formato de salida

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


class TestReportCommand:
    """Tests para el comando 'report' del CLI."""

    @pytest.fixture
    def cli(self):
        """Fixture que proporciona instancia del CLI con logger configurado."""
        cli_instance = cli_module.ScavengrCLI()
        # Inicializar logger global con NullHandler para evitar warnings
        cli_module.logger = logging.getLogger("test_cli")
        cli_module.logger.addHandler(logging.NullHandler())
        return cli_instance

    @pytest.fixture
    def mock_report_result_success(self):
        """Fixture que proporciona resultado exitoso de generación de informe."""
        result = mock.MagicMock()
        result.success = True
        result.output_path = "/tmp/test_report.xlsx"
        result.tables_analyzed = 25
        result.columns_analyzed = 350
        result.quality_score = 85.5
        result.format = "excel"
        result.error_message = None
        return result

    @pytest.fixture
    def mock_report_result_failure(self):
        """Fixture que proporciona resultado fallido de generación de informe."""
        result = mock.MagicMock()
        result.success = False
        result.output_path = None
        result.tables_analyzed = 0
        result.columns_analyzed = 0
        result.quality_score = 0
        result.format = None
        result.error_message = "Error al analizar esquema DBML"
        return result

    def test_report_creates_file(self, cli, mock_report_result_success):
        """Test que report crea archivo de informe exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_success

                # Ejecutar comando
                result = cli.report_command(args)

                # Verificar resultado
                assert result is True
                MockGenerateReport.assert_called_once_with(version=cli.version)
                mock_use_case.execute.assert_called_once_with(
                    str(input_file), str(output_file)
                )

    def test_report_validates_input_file(self, cli):
        """Test que report valida existencia de archivo de entrada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "nonexistent.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Configurar argumentos con archivo inexistente
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Ejecutar comando - debe fallar en validación
            result = cli.report_command(args)

            # Verificar que retorna False
            assert result is False

    def test_report_logs_statistics(self, cli, mock_report_result_success):
        """Test que report registra estadísticas correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_success

                # Capturar logs
                with mock.patch.object(cli_module.logger, "info") as mock_logger:
                    # Ejecutar comando
                    result = cli.report_command(args)

                    # Verificar resultado
                    assert result is True

                    # Verificar que se registraron estadísticas
                    info_calls = [call[0][0] for call in mock_logger.call_args_list]
                    assert any("25 tablas" in str(call) for call in info_calls)
                    assert any("350 columnas" in str(call) for call in info_calls)
                    assert any("85.5%" in str(call) for call in info_calls)

    def test_report_handles_generation_failure(self, cli, mock_report_result_failure):
        """Test que report maneja errores de generación correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_failure

                # Ejecutar comando
                result = cli.report_command(args)

                # Verificar resultado
                assert result is False

    def test_report_handles_exception(self, cli):
        """Test que report maneja excepciones inesperadas correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Mock de GenerateReport que lanza excepción
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock para lanzar excepción
                MockGenerateReport.side_effect = Exception(
                    "Error de procesamiento simulado"
                )

                # Ejecutar comando
                result = cli.report_command(args)

                # Verificar que retorna False
                assert result is False

    def test_report_detects_excel_format(self, cli, mock_report_result_success):
        """Test que report detecta formato Excel correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Actualizar resultado mock para Excel
            mock_report_result_success.format = "excel"

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_success

                # Ejecutar comando
                result = cli.report_command(args)

                # Verificar resultado
                assert result is True
                assert mock_report_result_success.format == "excel"

    def test_report_detects_json_format(self, cli, mock_report_result_success):
        """Test que report detecta formato JSON correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.json"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Actualizar resultado mock para JSON
            mock_report_result_success.format = "json"

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_success

                # Ejecutar comando
                result = cli.report_command(args)

                # Verificar resultado
                assert result is True
                assert mock_report_result_success.format == "json"

    def test_report_quality_score_logging(self, cli, mock_report_result_success):
        """Test que report registra el quality score correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test_schema.dbml"
            output_file = Path(tmpdir) / "test_report.xlsx"

            # Crear archivo de entrada mock
            input_file.write_text("Table users { id int [pk] }")

            # Configurar argumentos
            args = mock.MagicMock()
            args.input = str(input_file)
            args.output = str(output_file)

            # Mock de GenerateReport
            with mock.patch(
                "scavengr.application.GenerateReport"
            ) as MockGenerateReport:
                # Configurar mock
                mock_use_case = MockGenerateReport.return_value
                mock_use_case.execute.return_value = mock_report_result_success

                # Capturar logs
                with mock.patch.object(cli_module.logger, "info") as mock_logger:
                    # Ejecutar comando
                    result = cli.report_command(args)

                    # Verificar resultado
                    assert result is True

                    # Verificar que se registró el quality score
                    info_calls = [call[0][0] for call in mock_logger.call_args_list]
                    assert any(
                        "Score de calidad" in str(call) and "85.5%" in str(call)
                        for call in info_calls
                    )
