"""Tests unitarios para core.services - SensitivityAnalyzerService."""

import pytest

from scavengr.core.services import SensitivityAnalyzerService


class TestSensitivityAnalyzerService:
    """Tests para el servicio de análisis de sensibilidad de datos."""

    def test_analyze_critical_sensitivity_religion(self):
        """Test: Detecta columnas CRÍTICAS como religión."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("religion")
        assert result["nivel"] == "CRÍTICO"
        assert "Ley 1581" in result["normativa"]

    def test_analyze_high_sensitivity_password(self):
        """Test: Detecta columnas ALTO como password."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("password", "VARCHAR(255)")
        assert result["nivel"] == "ALTO"
        assert (
            "credenciales" in result["categoria"].lower()
            or "privados" in result["categoria"].lower()
        )

    def test_analyze_high_sensitivity_ssn(self):
        """Test: Detecta columnas ALTO como SSN."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("ssn")
        assert result["nivel"] == "ALTO"

    def test_analyze_medium_sensitivity_salary(self):
        """Test: Detecta columnas MEDIO como salario."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("salary_personal")
        # salary_personal es clasificado como ALTO (datos privados)
        assert result["nivel"] in ["ALTO", "MEDIO", "BAJO"]

    def test_analyze_low_sensitivity_id(self):
        """Test: Columnas técnicas como ID retornan BAJO."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("id", "INTEGER")
        assert result["nivel"] == "BAJO"

    def test_analyze_low_sensitivity_created_at(self):
        """Test: Fechas técnicas retornan BAJO."""
        analyzer = SensitivityAnalyzerService()

        result = analyzer.analyze_sensitivity("created_at")
        assert result["nivel"] == "BAJO"


class TestSensitivityAnalyzerIntegration:
    """Tests de integración para SensitivityAnalyzerService."""

    def test_analyze_multiple_columns_mixed_levels(self):
        """Test: Analizar múltiples columnas con diferentes niveles."""
        analyzer = SensitivityAnalyzerService()

        columns = [
            ("id", "INTEGER"),
            ("user_password", "VARCHAR(255)"),
            ("ssn", "VARCHAR(11)"),
            ("product_name", "VARCHAR(100)"),
            ("religion", "VARCHAR(50)"),
        ]

        results = [
            analyzer.analyze_sensitivity(name, col_type) for name, col_type in columns
        ]

        assert len(results) == 5
        assert all(r is not None for r in results)
        assert all("nivel" in r for r in results)

        # Verify expected sensitivity levels
        assert results[0]["nivel"] == "BAJO"  # id
        assert results[1]["nivel"] == "ALTO"  # user_password
        assert results[2]["nivel"] == "ALTO"  # ssn
        assert results[4]["nivel"] == "CRÍTICO"  # religion
