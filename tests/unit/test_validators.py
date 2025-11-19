"""Tests unitarios para utils.validators."""

import os
import tempfile
from pathlib import Path

import pytest

from scavengr.utils.exceptions import (
    FileNotFoundError,
    InvalidFormatError,
    ValidationError,
)
from scavengr.utils.validators import (
    validate_file_exists,
    validate_input_file_format,
    validate_output_format,
    validate_write_permissions,
)


class TestValidateFileExists:
    """Tests para validación de existencia de archivos."""

    def test_file_exists_returns_path(self):
        """Test: Archivo existente retorna Path object."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            result = validate_file_exists(tmp_path)
            assert isinstance(result, Path)
            assert result.exists()
        finally:
            os.unlink(tmp_path)

    def test_file_not_exists_raises_error(self):
        """Test: Archivo inexistente lanza FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_file_exists("/non/existent/file.dbml")


class TestValidateOutputFormat:
    """Tests para validación de formatos de salida."""

    def test_detect_csv_format(self):
        """Test: Detecta formato CSV por extensión."""
        fmt = validate_output_format("output.csv")
        assert fmt == "csv"

    def test_detect_excel_format_xlsx(self):
        """Test: Detecta formato Excel (.xlsx)."""
        fmt = validate_output_format("output.xlsx")
        assert fmt == "excel"

    def test_detect_json_format(self):
        """Test: Detecta formato JSON."""
        fmt = validate_output_format("output.json")
        assert fmt == "json"

    def test_format_override(self):
        """Test: Parámetro format_override prevalece."""
        fmt = validate_output_format("output.txt", "csv")
        assert fmt == "csv"

    def test_invalid_format_raises_error(self):
        """Test: Formato no soportado lanza InvalidFormatError."""
        with pytest.raises(InvalidFormatError):
            validate_output_format("output.txt")


class TestValidateWritePermissions:
    """Tests para validación de permisos de escritura."""

    def test_write_permissions_valid_directory(self):
        """Test: Directorio válido para escritura."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.csv")
            result = validate_write_permissions(output_path)
            assert isinstance(result, Path)

    def test_write_permissions_creates_directory(self):
        """Test: Crea directorio padre si no existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "nested", "deep", "output.csv")
            result = validate_write_permissions(nested_path)
            assert result.parent.exists()


class TestValidateInputFileFormat:
    """Tests para validación de formatos de entrada."""

    def test_valid_dbml_file(self):
        """Test: Archivo DBML válido."""
        with tempfile.NamedTemporaryFile(suffix=".dbml", delete=False) as tmp:
            tmp.write(b"Table users { id int }")
            tmp_path = tmp.name

        try:
            result = validate_input_file_format(tmp_path)
            assert result.suffix == ".dbml"
        finally:
            os.unlink(tmp_path)

    def test_empty_file_invalid(self):
        """Test: Archivo vacío lanza ValidationError."""
        with tempfile.NamedTemporaryFile(suffix=".dbml", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(ValidationError):
                validate_input_file_format(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_unsupported_format_invalid(self):
        """Test: Formato no soportado lanza ValidationError."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            with pytest.raises(ValidationError):
                validate_input_file_format(tmp_path)
        finally:
            os.unlink(tmp_path)
