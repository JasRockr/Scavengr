"""Tests unitarios para core.services - RegexInferenceService."""

import pytest

from scavengr.core.services import RegexInferenceService


class TestRegexInferenceService:
    """Tests para el servicio de inferencia de patrones regex."""

    def test_infer_email_pattern(self):
        """Test: Infiere patrón regex para email."""
        service = RegexInferenceService()

        pattern = service.infer_regex("varchar(255)", "email")
        assert pattern is not None
        assert isinstance(pattern, str)
        assert "@" in pattern or "email" in pattern.lower() or "[a-zA-Z0-9" in pattern

    def test_infer_phone_pattern(self):
        """Test: Infiere patrón regex para teléfono."""
        service = RegexInferenceService()

        pattern = service.infer_regex("varchar(20)", "phone")
        assert pattern is not None
        assert isinstance(pattern, str)

    def test_infer_url_pattern(self):
        """Test: Infiere patrón regex para URL."""
        service = RegexInferenceService()

        pattern = service.infer_regex("varchar(500)", "website_url")
        assert pattern is not None
        assert isinstance(pattern, str)

    def test_infer_date_pattern(self):
        """Test: Infiere patrón regex para fecha."""
        service = RegexInferenceService()

        pattern = service.infer_regex("date", "birth_date")
        assert pattern is not None
        assert isinstance(pattern, str)

    def test_infer_integer_pattern(self):
        """Test: Infiere patrón regex para entero."""
        service = RegexInferenceService()

        pattern = service.infer_regex("int", "user_id")
        assert pattern is not None
        assert "[0-9]" in pattern

    def test_infer_nit_pattern(self):
        """Test: Infiere patrón regex para NIT (Colombia)."""
        service = RegexInferenceService(country_code="CO")

        pattern = service.infer_regex("varchar(20)", "nit")
        assert pattern is not None
        assert isinstance(pattern, str)

    def test_get_regex_description(self):
        """Test: Obtiene descripción legible de patrón regex."""
        service = RegexInferenceService()

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        description = service.get_regex_description(email_regex)
        assert description is not None
        assert "email" in description.lower() or "@" in description
