"""Tests unitarios para core.services - DescriptionGeneratorService."""

import pytest

from scavengr.core.entities import Column
from scavengr.core.services import DescriptionGeneratorService


class TestDescriptionGeneratorService:
    """Tests para el generador automático de descripciones."""

    def test_generate_description_email_column(self):
        """Test: Genera descripción para columna de email."""
        generator = DescriptionGeneratorService()
        email_column = Column(name="email", type="VARCHAR(255)")

        description = generator.generate_description(email_column)
        assert description is not None
        assert len(description) > 0
        assert isinstance(description, str)

    def test_generate_description_timestamp(self):
        """Test: Genera descripción para columna timestamp."""
        generator = DescriptionGeneratorService()
        created_col = Column(name="created_at", type="TIMESTAMP")

        description = generator.generate_description(created_col)
        assert description is not None
        assert len(description) > 0

    def test_generate_description_primary_key(self):
        """Test: Genera descripción para clave primaria."""
        generator = DescriptionGeneratorService()
        id_col = Column(name="user_id", type="INTEGER", is_pk=True)

        description = generator.generate_description(id_col)
        assert description is not None
        assert (
            "Identificador único" in description
            or "identificador" in description.lower()
        )

    def test_generate_description_phone(self):
        """Test: Genera descripción para número de teléfono."""
        generator = DescriptionGeneratorService()
        phone_col = Column(name="phone_number", type="VARCHAR(20)")

        description = generator.generate_description(phone_col)
        assert description is not None
        assert len(description) > 0

    def test_generate_description_cedula(self):
        """Test: Genera descripción para cédula (número de identificación)."""
        generator = DescriptionGeneratorService()
        cedula_col = Column(name="cedula", type="VARCHAR(20)")

        description = generator.generate_description(cedula_col)
        assert description is not None
        assert (
            "cédula" in description.lower() or "identificación" in description.lower()
        )

    def test_generate_description_nullable_field(self):
        """Test: Indica si un campo es opcional."""
        generator = DescriptionGeneratorService()
        optional_col = Column(name="middle_name", type="VARCHAR(100)", is_nullable=True)

        description = generator.generate_description(optional_col)
        assert description is not None
        assert "opcional" in description.lower() or "Campo opcional" in description
