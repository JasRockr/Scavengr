"""Tests unitarios para MetadataCache.

Este módulo contiene tests para el sistema de caching de metadatos.

Author: Json Rivera
Date: 2025-11-18
Version: 0.1.0
"""

import json
import pickle
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest

from scavengr.infrastructure.cache import MetadataCache


class TestMetadataCache:
    """Tests para la clase MetadataCache."""

    @pytest.fixture
    def temp_cache_dir(self) -> Path:
        """Crea un directorio temporal para tests de cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_db_config(self) -> Dict[str, Any]:
        """Configuración de BD de ejemplo."""
        return {
            "type": "postgresql",
            "host": "localhost",
            "name": "test_db",
            "user": "test_user",
        }

    @pytest.fixture
    def sample_metadata(self) -> Dict[str, Any]:
        """Metadatos de ejemplo."""
        return {
            "tables": [{"name": "users"}, {"name": "products"}],
            "columns": [
                ["public", "users", "id", "integer", None, None, "NO", None],
                ["public", "users", "email", "varchar", 255, None, "NO", None],
            ],
            "foreign_keys": [],
            "primary_keys": [["public", "users", "id"]],
            "indexes": [],
        }

    def test_initialization_default(self, temp_cache_dir: Path) -> None:
        """Test inicialización con parámetros por defecto."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        assert cache.cache_dir == temp_cache_dir
        assert cache.ttl == timedelta(hours=24)
        assert cache.serialization == "pickle"
        assert temp_cache_dir.exists()

    def test_initialization_custom(self, temp_cache_dir: Path) -> None:
        """Test inicialización con parámetros personalizados."""
        cache = MetadataCache(
            cache_dir=str(temp_cache_dir), ttl_hours=48, serialization="json"
        )

        assert cache.ttl == timedelta(hours=48)
        assert cache.serialization == "json"

    def test_initialization_invalid_serialization(self, temp_cache_dir: Path) -> None:
        """Test error con formato de serialización inválido."""
        with pytest.raises(ValueError, match="Serialization debe ser"):
            MetadataCache(cache_dir=str(temp_cache_dir), serialization="xml")

    def test_generate_cache_key_consistency(
        self, temp_cache_dir: Path, sample_db_config: Dict[str, Any]
    ) -> None:
        """Test que la clave de cache es consistente para misma configuración."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        key1 = cache._generate_cache_key(sample_db_config)
        key2 = cache._generate_cache_key(sample_db_config)

        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length

    def test_generate_cache_key_different_configs(self, temp_cache_dir: Path) -> None:
        """Test que configuraciones diferentes generan claves diferentes."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        config1 = {"type": "postgresql", "host": "host1", "name": "db1"}
        config2 = {"type": "postgresql", "host": "host2", "name": "db1"}

        key1 = cache._generate_cache_key(config1)
        key2 = cache._generate_cache_key(config2)

        assert key1 != key2

    def test_save_and_load_pickle(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test guardar y cargar con formato pickle."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir), serialization="pickle")

        # Guardar
        result = cache.save(sample_db_config, sample_metadata)
        assert result is True

        # Cargar
        loaded = cache.load(sample_db_config)
        assert loaded is not None
        assert loaded["tables"] == sample_metadata["tables"]
        assert loaded["columns"] == sample_metadata["columns"]

    def test_save_and_load_json(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test guardar y cargar con formato JSON."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir), serialization="json")

        # Guardar
        result = cache.save(sample_db_config, sample_metadata)
        assert result is True

        # Cargar
        loaded = cache.load(sample_db_config)
        assert loaded is not None
        assert loaded["tables"] == sample_metadata["tables"]

    def test_load_nonexistent_cache(
        self, temp_cache_dir: Path, sample_db_config: Dict[str, Any]
    ) -> None:
        """Test cargar cache que no existe."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        loaded = cache.load(sample_db_config)
        assert loaded is None

    def test_load_with_force_refresh(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que force_refresh invalida cache existente."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        # Guardar cache
        cache.save(sample_db_config, sample_metadata)

        # Cargar con force_refresh
        loaded = cache.load(sample_db_config, force_refresh=True)
        assert loaded is None

    def test_cache_expiration(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que cache expirado retorna None."""
        # Cache con TTL muy corto
        cache = MetadataCache(cache_dir=str(temp_cache_dir), ttl_hours=0)

        # Guardar
        cache.save(sample_db_config, sample_metadata)

        # Cargar (debería estar expirado)
        loaded = cache.load(sample_db_config)
        assert loaded is None

    def test_clear_specific_cache(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test eliminar cache específico."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        # Guardar
        cache.save(sample_db_config, sample_metadata)

        # Verificar que existe
        assert cache.load(sample_db_config) is not None

        # Eliminar
        deleted = cache.clear(sample_db_config)
        assert deleted == 1

        # Verificar que ya no existe
        assert cache.load(sample_db_config) is None

    def test_clear_all_caches(
        self, temp_cache_dir: Path, sample_metadata: Dict[str, Any]
    ) -> None:
        """Test eliminar todos los caches."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        # Guardar múltiples caches
        config1 = {"type": "postgresql", "host": "host1", "name": "db1"}
        config2 = {"type": "mysql", "host": "host2", "name": "db2"}

        cache.save(config1, sample_metadata)
        cache.save(config2, sample_metadata)

        # Eliminar todos
        deleted = cache.clear()
        assert deleted == 2

        # Verificar que no existen
        assert cache.load(config1) is None
        assert cache.load(config2) is None

    def test_get_cache_info_valid(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test obtener información de cache válido."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        # Guardar
        cache.save(sample_db_config, sample_metadata)

        # Obtener info
        info = cache.get_cache_info(sample_db_config)

        assert info is not None
        assert "timestamp" in info
        assert "age_hours" in info
        assert info["is_valid"] is True
        assert info["serialization"] == "pickle"
        assert info["size_bytes"] > 0

    def test_get_cache_info_nonexistent(
        self, temp_cache_dir: Path, sample_db_config: Dict[str, Any]
    ) -> None:
        """Test obtener información de cache inexistente."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        info = cache.get_cache_info(sample_db_config)
        assert info is None

    def test_cache_file_format_pickle(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que archivo pickle tiene estructura correcta."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir), serialization="pickle")

        cache.save(sample_db_config, sample_metadata)

        # Leer archivo directamente
        cache_key = cache._generate_cache_key(sample_db_config)
        cache_path = cache._get_cache_path(cache_key)

        with open(cache_path, "rb") as f:
            cache_data = pickle.load(f)

        assert "timestamp" in cache_data
        assert "db_config" in cache_data
        assert "metadata" in cache_data
        assert cache_data["metadata"] == sample_metadata

    def test_cache_file_format_json(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que archivo JSON tiene estructura correcta."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir), serialization="json")

        cache.save(sample_db_config, sample_metadata)

        # Leer archivo directamente
        cache_key = cache._generate_cache_key(sample_db_config)
        cache_path = cache._get_cache_path(cache_key)

        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        assert "timestamp" in cache_data
        assert "db_config" in cache_data
        assert "metadata" in cache_data
        assert cache_data["metadata"] == sample_metadata

    def test_cache_timestamp_format(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que timestamp tiene formato ISO correcto."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        cache.save(sample_db_config, sample_metadata)

        info = cache.get_cache_info(sample_db_config)
        assert info is not None

        # Validar que es parseable como ISO datetime
        timestamp = datetime.fromisoformat(info["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_cache_db_config_storage(
        self,
        temp_cache_dir: Path,
        sample_db_config: Dict[str, Any],
        sample_metadata: Dict[str, Any],
    ) -> None:
        """Test que db_config se guarda correctamente (sin credenciales)."""
        cache = MetadataCache(cache_dir=str(temp_cache_dir))

        cache.save(sample_db_config, sample_metadata)

        # Leer cache
        cache_key = cache._generate_cache_key(sample_db_config)
        cache_path = cache._get_cache_path(cache_key)

        with open(cache_path, "rb") as f:
            cache_data = pickle.load(f)

        # Verificar que solo contiene campos no sensibles
        stored_config = cache_data["db_config"]
        assert stored_config["type"] == "postgresql"
        assert stored_config["host"] == "localhost"
        assert stored_config["name"] == "test_db"
        assert "user" not in stored_config  # No debe guardar credenciales
        assert "password" not in stored_config
