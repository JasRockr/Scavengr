"""Tests unitarios para application/report.py.

Tests para el caso de uso GenerateReport que genera informes analíticos
avanzados desde archivos DBML con estadísticas y análisis de calidad.

Cobertura:
- Generación de informes en formato Excel y JSON
- Análisis estadístico y score de calidad
- Manejo de errores y validaciones
- Creación de directorios automática
- Detección de formatos de salida

Author: Jason Rivera
Date: 2025-11-13
"""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from scavengr.application.report import GenerateReport, ReportResult
from scavengr.core.entities import Column, DatabaseSchema, Table


@pytest.fixture
def sample_schema():
    """Schema de prueba con datos representativos."""
    tables = [
        Table(
            name="usuarios",
            columns=[
                Column(name="id", type="int", is_pk=True),
                Column(name="nombre", type="varchar(100)"),
                Column(name="email", type="varchar(255)"),
                Column(name="created_at", type="timestamp"),
            ],
        ),
        Table(
            name="productos",
            columns=[
                Column(name="id", type="int", is_pk=True),
                Column(name="codigo", type="varchar(50)"),
                Column(name="precio", type="decimal(10,2)"),
            ],
        ),
    ]
    return DatabaseSchema(
        name="test_database",
        tables=tables,
        relationships=[],
        indexes=[],
        metadata={"source_system": "Test System"},
    )


@pytest.fixture
def mock_stats_service():
    """Mock del servicio de estadísticas con datos realistas."""
    mock_service = mock.MagicMock()
    mock_service.analyze_schema.return_value = {
        "resumen_general": {
            "total_tablas": 2,
            "total_columnas": 7,
            "total_relaciones": 0,
            "promedio_columnas_por_tabla": 3.5,
            "tablas_maestras": 1,
            "tablas_transaccionales": 1,
        },
        "calidad_datos": {
            "score_general": 85.5,
            "completitud": {"score": 90.0},
            "integridad_referencial": {"score": 85.0},
            "consistencia_nombres": {"score": 80.0},
            "documentacion": {"score": 75.0},
        },
        "distribucion_tipos": {
            "top_10_tipos": [
                {"tipo": "int", "cantidad": 2},
                {"tipo": "varchar", "cantidad": 3},
                {"tipo": "decimal", "cantidad": 1},
                {"tipo": "timestamp", "cantidad": 1},
            ],
        },
        "seguridad_sensibilidad": {
            "distribucion_sensibilidad": {
                "CRÍTICO": {"cantidad": 1, "porcentaje": 14.3},
                "ALTO": {"cantidad": 2, "porcentaje": 28.6},
                "MEDIO": {"cantidad": 3, "porcentaje": 42.9},
                "BAJO": {"cantidad": 1, "porcentaje": 14.2},
            },
        },
        "recomendaciones": [
            {
                "prioridad": "CRÍTICA",
                "categoria": "Seguridad",
                "recomendacion": "Encriptar columna 'email'",
                "tablas_afectadas": ["usuarios"],
            },
            {
                "prioridad": "ALTA",
                "categoria": "Integridad",
                "recomendacion": "Agregar foreign keys faltantes",
                "tablas_afectadas": ["productos"],
            },
        ],
    }
    return mock_service


class TestGenerateReport:
    """Tests para el caso de uso GenerateReport."""

    def test_generate_json_report_success(self, sample_schema, mock_stats_service):
        """Debe generar informe JSON exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.json")
            dbml_path = os.path.join(tmpdir, "test.dbml")

            # Crear archivo DBML de prueba
            with open(dbml_path, "w") as f:
                f.write("Table usuarios { id int [pk] }")

            # Mock del parser
            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = sample_schema

                use_case = GenerateReport(version="0.0.3")
                use_case.stats_service = mock_stats_service

                result = use_case.execute(dbml_path, output_path)

                assert result.success is True
                assert result.output_path == output_path
                assert result.format == "json"
                assert result.tables_analyzed == 2
                assert result.columns_analyzed == 7
                assert result.quality_score == 85.5
                assert os.path.exists(output_path)

                # Verificar contenido JSON
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    assert "metadatos" in data
                    assert "analisis" in data
                    assert data["analisis"]["resumen_general"]["total_tablas"] == 2

    def test_generate_excel_report_success(self, sample_schema, mock_stats_service):
        """Debe generar informe Excel exitosamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.xlsx")
            dbml_path = os.path.join(tmpdir, "test.dbml")

            with open(dbml_path, "w") as f:
                f.write("Table usuarios { id int [pk] }")

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = sample_schema

                use_case = GenerateReport(version="0.0.3")
                use_case.stats_service = mock_stats_service

                result = use_case.execute(dbml_path, output_path)

                assert result.success is True
                assert result.format == "xlsx"
                assert os.path.exists(output_path)
                assert result.file_size > 0

    def test_generate_report_dbml_not_found(self):
        """Debe fallar si el archivo DBML no existe."""
        use_case = GenerateReport(version="0.0.3")

        result = use_case.execute("non_existent.dbml", "output.json")

        assert result.success is False
        assert "no encontrado" in result.error_message.lower()

    def test_generate_report_parse_error(self):
        """Debe manejar error de parseo de DBML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "invalid.dbml")
            output_path = os.path.join(tmpdir, "report.json")

            with open(dbml_path, "w") as f:
                f.write("Invalid DBML content")

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = None

                use_case = GenerateReport(version="0.0.3")

                result = use_case.execute(dbml_path, output_path)

                assert result.success is False
                assert "parsear" in result.error_message.lower()

    def test_generate_report_creates_output_directory(
        self, sample_schema, mock_stats_service
    ):
        """Debe crear directorio de salida si no existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "reports", "2025", "november")
            output_path = os.path.join(nested_dir, "report.json")
            dbml_path = os.path.join(tmpdir, "test.dbml")

            with open(dbml_path, "w") as f:
                f.write("Table test { id int }")

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = sample_schema

                use_case = GenerateReport(version="0.0.3")
                use_case.stats_service = mock_stats_service

                result = use_case.execute(dbml_path, output_path)

                assert result.success is True
                assert os.path.exists(nested_dir)
                assert os.path.exists(output_path)

    def test_generate_report_with_empty_schema(self, mock_stats_service):
        """Debe manejar esquema vacío sin tablas."""
        empty_schema = DatabaseSchema(
            name="empty_db", tables=[], relationships=[], indexes=[]
        )

        mock_stats_service.analyze_schema.return_value = {
            "resumen_general": {
                "total_tablas": 0,
                "total_columnas": 0,
                "total_relaciones": 0,
                "promedio_columnas_por_tabla": 0,
                "tablas_maestras": 0,
                "tablas_transaccionales": 0,
            },
            "calidad_datos": {
                "score_general": 0.0,
                "completitud": {"score": 0.0},
                "integridad_referencial": {"score": 0.0},
                "consistencia_nombres": {"score": 0.0},
                "documentacion": {"score": 0.0},
            },
            "distribucion_tipos": {"top_10_tipos": []},
            "seguridad_sensibilidad": {"distribucion_sensibilidad": {}},
            "recomendaciones": [],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "empty.dbml")
            output_path = os.path.join(tmpdir, "report.json")

            with open(dbml_path, "w") as f:
                f.write("")

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = empty_schema

                use_case = GenerateReport(version="0.0.3")
                use_case.stats_service = mock_stats_service

                result = use_case.execute(dbml_path, output_path)

                assert result.success is True
                assert result.tables_analyzed == 0
                assert result.columns_analyzed == 0

    def test_generate_report_detects_format_correctly(self):
        """Debe detectar formatos de salida correctamente."""
        use_case = GenerateReport(version="0.0.3")

        assert use_case._detect_output_format("report.xlsx") == "xlsx"
        assert use_case._detect_output_format("report.XLSX") == "xlsx"
        assert use_case._detect_output_format("report.json") == "json"
        assert use_case._detect_output_format("report.JSON") == "json"
        assert use_case._detect_output_format("report.txt") == "json"  # Default

    def test_generate_metadata_includes_required_fields(self):
        """Debe incluir todos los campos requeridos en metadatos."""
        use_case = GenerateReport(version="0.0.3")

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.dbml")
            output_path = os.path.join(tmpdir, "output.json")

            metadata = use_case._generate_metadata(input_path, output_path)

            assert "version_scavengr" in metadata
            assert metadata["version_scavengr"] == "0.0.3"
            assert "fecha_generacion" in metadata
            assert "generado_en" in metadata
            assert "archivo_origen" in metadata
            assert "archivo_salida" in metadata
            assert "usuario" in metadata

    def test_parse_dbml_file_handles_dict_result(self):
        """Debe convertir resultado dict a DatabaseSchema."""
        use_case = GenerateReport(version="0.0.3")

        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "test.dbml")
            with open(dbml_path, "w") as f:
                f.write("Table test { id int }")

            parse_result = {
                "name": "test_db",
                "tables": [],
                "relationships": [],
                "indexes": [],
                "metadata": {},
            }

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = parse_result

                schema = use_case._parse_dbml_file(dbml_path)

                assert schema is not None
                assert isinstance(schema, DatabaseSchema)
                assert schema.name == "test_db"

    def test_parse_dbml_file_handles_schema_result(self, sample_schema):
        """Debe aceptar DatabaseSchema directamente."""
        use_case = GenerateReport(version="0.0.3")

        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "test.dbml")
            with open(dbml_path, "w") as f:
                f.write("Table test { id int }")

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = sample_schema

                schema = use_case._parse_dbml_file(dbml_path)

                assert schema is not None
                assert isinstance(schema, DatabaseSchema)
                assert schema == sample_schema

    def test_report_result_dataclass_structure(self):
        """Debe validar estructura de ReportResult."""
        result = ReportResult(
            success=True,
            output_path="/path/to/report.xlsx",
            format="xlsx",
            tables_analyzed=10,
            columns_analyzed=50,
            quality_score=78.5,
            file_size=1024,
            error_message=None,
        )

        assert result.success is True
        assert result.output_path == "/path/to/report.xlsx"
        assert result.format == "xlsx"
        assert result.tables_analyzed == 10
        assert result.columns_analyzed == 50
        assert result.quality_score == 78.5
        assert result.file_size == 1024
        assert result.error_message is None

    def test_report_result_with_error(self):
        """Debe manejar ReportResult con error."""
        result = ReportResult(
            success=False,
            error_message="Error de conexión",
        )

        assert result.success is False
        assert result.error_message == "Error de conexión"
        assert result.output_path == ""
        assert result.tables_analyzed == 0

    def test_generate_report_unexpected_exception(self):
        """Debe manejar excepciones inesperadas durante generación."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "test.dbml")
            output_path = os.path.join(tmpdir, "report.json")

            with open(dbml_path, "w") as f:
                f.write("Table test { id int }")

            # Mock que lanza excepción después de parsear exitosamente
            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                # Parser tiene éxito pero stats_service falla
                mock_parser.return_value.parse.return_value = DatabaseSchema(
                    name="test", tables=[], relationships=[], indexes=[]
                )

                use_case = GenerateReport(version="0.0.3")

                # Crear mock para stats_service
                mock_stats = mock.MagicMock()
                mock_stats.analyze_schema.side_effect = RuntimeError(
                    "Error crítico en análisis"
                )
                use_case.stats_service = mock_stats

                result = use_case.execute(dbml_path, output_path)

                assert result.success is False
                assert "error inesperado" in result.error_message.lower()

    def test_write_report_file_handles_write_error(
        self, sample_schema, mock_stats_service
    ):
        """Debe manejar errores de escritura del archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dbml_path = os.path.join(tmpdir, "test.dbml")
            # Path inválido para forzar error de escritura
            output_path = os.path.join(tmpdir, "readonly", "report.json")

            with open(dbml_path, "w") as f:
                f.write("Table test { id int }")

            # Crear directorio readonly y hacerlo de solo lectura en Unix
            readonly_dir = os.path.join(tmpdir, "readonly")
            os.makedirs(readonly_dir, exist_ok=True)

            with mock.patch("scavengr.application.report.DBMLParser") as mock_parser:
                mock_parser.return_value.parse.return_value = sample_schema

                # Mock para simular error de escritura
                with mock.patch("builtins.open", side_effect=PermissionError):
                    use_case = GenerateReport(version="0.0.3")
                    use_case.stats_service = mock_stats_service

                    result = use_case.execute(dbml_path, output_path)

                    assert result.success is False
                    assert result.error_message is not None
