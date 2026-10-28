"""Tests de integración para application.dictionary."""

import os
import tempfile
from pathlib import Path

import pytest

from scavengr.application.dictionary import GenerateDictionary


class TestGenerateDictionaryIntegration:
    """Tests de integración para el caso de uso GenerateDictionary."""

    @pytest.fixture
    def valid_dbml_file(self) -> str:
        """Fixture: Archivo DBML válido para testing."""
        content = """
Table users {
  id integer [primary key]
  email varchar(255) [not null, unique]
  name varchar(100)
  created_at timestamp [default: `now()`]
}

Table posts {
  id integer [primary key]
  user_id integer [not null]
  title varchar(500) [not null]
  content text
  published boolean [default: false]
}

Ref: posts.user_id > users.id
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dbml", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        return tmp_path

    def test_generate_dictionary_json(self, valid_dbml_file: str):
        """Test: Genera diccionario en formato JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as out:
            output_file = out.name

        try:
            generator = GenerateDictionary()
            result = generator.execute(valid_dbml_file, output_file, "json")

            # Debe retornar un resultado exitoso
            assert result is not None
            assert result.success is True
            assert Path(output_file).exists()

        finally:
            if Path(valid_dbml_file).exists():
                try:
                    os.unlink(valid_dbml_file)
                except PermissionError:
                    pass
            if Path(output_file).exists():
                try:
                    os.unlink(output_file)
                except PermissionError:
                    pass

    def test_generate_dictionary_csv(self, valid_dbml_file: str):
        """Test: Genera diccionario en formato CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as out:
            output_file = out.name

        try:
            generator = GenerateDictionary()
            result = generator.execute(valid_dbml_file, output_file, "csv")

            assert result is not None
            assert result.success is True
            assert Path(output_file).exists()

        finally:
            if Path(valid_dbml_file).exists():
                try:
                    os.unlink(valid_dbml_file)
                except PermissionError:
                    pass
            if Path(output_file).exists():
                try:
                    os.unlink(output_file)
                except PermissionError:
                    pass

    def test_generate_dictionary_xlsx(self, valid_dbml_file: str):
        """Test: Genera diccionario en formato Excel."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as out:
            output_file = out.name

        try:
            generator = GenerateDictionary()
            # Usar 'excel' en lugar de 'xlsx' como formato
            result = generator.execute(valid_dbml_file, output_file, "excel")

            assert result is not None
            assert result.success is True
            assert Path(output_file).exists()

        finally:
            if Path(valid_dbml_file).exists():
                try:
                    os.unlink(valid_dbml_file)
                except PermissionError:
                    pass
            if Path(output_file).exists():
                try:
                    os.unlink(output_file)
                except PermissionError:
                    pass

    def test_input_file_not_found(self):
        """Test: Archivo no encontrado retorna resultado fallido."""
        generator = GenerateDictionary()

        result = generator.execute("/path/not/found.dbml", "/output.json", "json")

        # Debe retornar un resultado con success=False
        assert result is not None
        assert result.success is False
