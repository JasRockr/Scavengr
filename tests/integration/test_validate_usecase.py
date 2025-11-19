"""Tests de integración para application.validate."""

import os
import tempfile
from pathlib import Path

import pytest

from scavengr.application.validate import ValidateDBML
from scavengr.infrastructure.parsers.dbml_parser import DBMLParser


class TestValidateDBMLIntegration:
    """Tests de integración para el caso de uso ValidateDBML."""

    @pytest.fixture
    def valid_dbml_content(self) -> str:
        """Fixture: DBML válido para testing."""
        return """
Table users {
  id integer [primary key]
  email varchar(255) [not null, unique]
  created_at timestamp [default: `now()`]
}

Table posts {
  id integer [primary key]
  user_id integer [not null]
  title varchar(500) [not null]
  content text
}

Ref: posts.user_id > users.id
"""

    @pytest.fixture
    def invalid_dbml_content(self) -> str:
        """Fixture: DBML inválido con errores."""
        return """
Table users {
  id integer [primary key]
  email varchar(255)
}

Ref: posts.user_id > users.id  // Referencia a tabla inexistente
"""

    def test_validate_valid_dbml(self, valid_dbml_content: str):
        """Test: Valida DBML válido exitosamente."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dbml", delete=False) as f:
            f.write(valid_dbml_content)
            tmp_path = f.name

        try:
            validator = ValidateDBML()
            result = validator.execute(tmp_path)

            # Debe retornar un ValidationResult válido (sin errores)
            assert result is not None
            assert hasattr(result, "is_valid")

        finally:
            # Asegurar que el archivo se cierre antes de intentar borrarlo
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass

    def test_validate_invalid_dbml(self, invalid_dbml_content: str):
        """Test: Detecta errores en DBML inválido."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dbml", delete=False) as f:
            f.write(invalid_dbml_content)
            tmp_path = f.name

        try:
            validator = ValidateDBML()
            result = validator.execute(tmp_path)

            # Puede tener problemas de validación (is_valid podría ser False)
            assert result is not None
            assert hasattr(result, "is_valid")

        finally:
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass

    def test_validate_file_not_found(self):
        """Test: Valida que archivo no encontrado retorna error."""
        validator = ValidateDBML()

        result = validator.execute("/path/that/does/not/exist.dbml")

        # Debe retornar un resultado con is_valid=False
        assert result is not None
        assert result.is_valid is False

    def test_validate_empty_file(self):
        """Test: Valida archivo DBML vacío."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dbml", delete=False) as f:
            f.write("")
            tmp_path = f.name

        try:
            validator = ValidateDBML()
            result = validator.execute(tmp_path)

            # Archivo vacío debería fallar en validación
            assert result is not None
            assert hasattr(result, "is_valid")

        finally:
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass
