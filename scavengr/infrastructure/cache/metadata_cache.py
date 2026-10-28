"""scavengr.infrastructure.cache.metadata_cache
===============================================

Implementación de caching para metadatos de bases de datos.

Este módulo proporciona caching opcional de metadatos extraídos para
mejorar el rendimiento en extracciones repetidas. Soporta serialización
mediante pickle y JSON, con invalidación basada en timestamp.

**ADVERTENCIA DE SEGURIDAD:**
    El formato pickle se usa SOLO para cache local controlado. Los archivos
    de cache son generados por el propio sistema en el directorio del proyecto
    (.scavengr_cache/). NUNCA deben cargarse archivos pickle de fuentes externas
    o no confiables, ya que pickle puede ejecutar código arbitrario durante
    la deserialización.

    Para entornos donde se requiera máxima seguridad, usar serialization="json".

Examples:
    >>> cache = MetadataCache(cache_dir=".scavengr_cache")
    >>> cache.save(db_config, metadata)
    >>> cached_data = cache.load(db_config)
    >>> cache.clear(db_config)

Author: Json Rivera
Date: 2025-11-18
Version: 0.1.0
"""

import hashlib
import json
import logging

# import os
import pickle  # nosec B403 - Pickle usado solo para cache local controlado
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MetadataCache:
    """Gestiona el caching de metadatos de bases de datos.

    Proporciona funcionalidad para guardar, cargar e invalidar cache de
    metadatos extraídos. Usa hashing de configuración para identificar
    caches únicos por base de datos.

    **Consideraciones de Seguridad:**
        - Pickle: Usado solo para cache local generado por el sistema
        - Cache directory: Controlado (.scavengr_cache/ en proyecto)
        - NO cargar archivos pickle de fuentes externas
        - Alternativa segura: usar serialization="json"

    Args:
        cache_dir (str): Directorio donde almacenar archivos de cache.
            Default: ".scavengr_cache" en directorio actual.
        ttl_hours (int): Tiempo de vida del cache en horas. Default: 24.
        serialization (str): Formato de serialización ("pickle" o "json").
            Default: "pickle" (más eficiente).

    Attributes:
        cache_dir (Path): Ruta del directorio de cache.
        ttl (timedelta): Tiempo de vida del cache.
        serialization (str): Formato de serialización usado.

    Examples:
        >>> # Uso básico con pickle
        >>> cache = MetadataCache()
        >>> db_config = {"type": "postgresql", "host": "localhost", "name": "mydb"}
        >>> metadata = {"tables": [...], "columns": [...]}
        >>> cache.save(db_config, metadata)
        >>> cached = cache.load(db_config)

        >>> # Uso con JSON (mayor portabilidad)
        >>> cache_json = MetadataCache(serialization="json")
        >>> cache_json.save(db_config, metadata)
    """

    def __init__(
        self,
        cache_dir: str = ".scavengr_cache",
        ttl_hours: int = 24,
        serialization: str = "pickle",
    ) -> None:
        """Inicializa el gestor de cache.

        Args:
            cache_dir (str): Directorio de cache. Default: ".scavengr_cache".
            ttl_hours (int): Horas de validez del cache. Default: 24.
            serialization (str): Formato ("pickle" o "json"). Default: "pickle".

        Raises:
            ValueError: Si serialization no es "pickle" o "json".
        """
        if serialization not in ("pickle", "json"):
            raise ValueError(
                f"Serialization debe ser 'pickle' o 'json', recibido: {serialization}"
            )

        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.serialization = serialization

        # Crear directorio si no existe
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"[CACHE] Directorio de cache: {self.cache_dir.absolute()}")

    def _generate_cache_key(self, db_config: Dict[str, Any]) -> str:
        """Genera una clave única para la configuración de BD.

        Usa hash MD5 de campos relevantes de configuración (type, host, name)
        para crear un identificador único y reproducible.

        Args:
            db_config (Dict[str, Any]): Configuración de base de datos.

        Returns:
            str: Hash MD5 hexadecimal (32 caracteres).

        Examples:
            >>> cache = MetadataCache()
            >>> config = {"type": "postgresql", "host": "localhost", "name": "db1"}
            >>> key = cache._generate_cache_key(config)
            >>> len(key)
            32
        """
        # Usar campos determinísticos para generar hash
        key_parts = [
            db_config.get("type", ""),
            db_config.get("host", ""),
            db_config.get("name", ""),
        ]
        key_str = "|".join(key_parts)

        # Generar hash MD5 (no usado para seguridad, solo para cache keys)
        # nosec B324 - MD5 usado solo para generar identificadores de cache, no para seguridad
        hash_obj = hashlib.md5(key_str.encode("utf-8"), usedforsecurity=False)  # nosec
        cache_key = hash_obj.hexdigest()

        logger.debug(f"[CACHE] Cache key generada: {cache_key} para {key_str}")
        return cache_key

    def _get_cache_path(self, cache_key: str) -> Path:
        """Obtiene la ruta del archivo de cache.

        Args:
            cache_key (str): Clave de cache generada.

        Returns:
            Path: Ruta completa del archivo de cache.
        """
        extension = "pkl" if self.serialization == "pickle" else "json"
        return self.cache_dir / f"{cache_key}.{extension}"

    def save(self, db_config: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Guarda metadatos en cache.

        Args:
            db_config (Dict[str, Any]): Configuración de BD (para generar key).
            metadata (Dict[str, Any]): Metadatos a cachear.

        Returns:
            bool: True si guardado exitoso, False si error.

        Examples:
            >>> cache = MetadataCache()
            >>> config = {"type": "mysql", "host": "db.example.com", "name": "prod"}
            >>> data = {"tables": [{"name": "users"}], "columns": [...]}
            >>> cache.save(config, data)
            True
        """
        try:
            cache_key = self._generate_cache_key(db_config)
            cache_path = self._get_cache_path(cache_key)

            # Agregar timestamp al metadata
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "db_config": {
                    "type": db_config.get("type"),
                    "host": db_config.get("host"),
                    "name": db_config.get("name"),
                },
                "metadata": metadata,
            }

            # Serializar según formato configurado
            if self.serialization == "pickle":
                # nosec B301 - Pickle usado solo para cache local controlado, no datos externos
                with open(cache_path, "wb") as f:
                    pickle.dump(
                        cache_data, f, protocol=pickle.HIGHEST_PROTOCOL
                    )  # nosec
            else:  # json
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"[CACHE] Metadatos guardados: {cache_path.name} "
                f"({self.serialization.upper()})"
            )
            return True

        except Exception as e:
            logger.error(f"[CACHE] Error guardando cache: {str(e)}")
            return False

    def load(
        self, db_config: Dict[str, Any], force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Carga metadatos desde cache si está válido.

        Args:
            db_config (Dict[str, Any]): Configuración de BD.
            force_refresh (bool): Si True, invalida cache y retorna None.
                Default: False.

        Returns:
            Optional[Dict[str, Any]]: Metadatos cacheados o None si no existe
                o está expirado.

        Examples:
            >>> cache = MetadataCache(ttl_hours=1)
            >>> config = {"type": "postgresql", "host": "localhost", "name": "db"}
            >>> # Primera carga (sin cache)
            >>> cache.load(config)
            None
            >>> # Después de save
            >>> cache.save(config, {"tables": [...]})
            True
            >>> # Segunda carga (desde cache)
            >>> data = cache.load(config)
            >>> data is not None
            True
        """
        if force_refresh:
            logger.info("[CACHE] Force refresh activado, ignorando cache")
            return None

        try:
            cache_key = self._generate_cache_key(db_config)
            cache_path = self._get_cache_path(cache_key)

            # Verificar si existe
            if not cache_path.exists():
                logger.debug(f"[CACHE] No existe cache: {cache_path.name}")
                return None

            # Deserializar según formato
            if self.serialization == "pickle":
                # nosec B301 - Pickle usado solo para cache local controlado, no datos externos
                with open(cache_path, "rb") as f:
                    cache_data = pickle.load(f)  # nosec
            else:  # json
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

            # Verificar timestamp y TTL
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            age = datetime.now() - cached_time

            if age > self.ttl:
                logger.info(
                    f"[CACHE] Cache expirado: {age.total_seconds() / 3600:.1f}h "
                    f"(TTL: {self.ttl.total_seconds() / 3600}h)"
                )
                return None

            logger.info(
                f"[CACHE] Cache válido cargado: {cache_path.name} "
                f"(edad: {age.total_seconds() / 60:.1f}min)"
            )
            return cache_data["metadata"]

        except Exception as e:
            logger.warning(f"[CACHE] Error cargando cache: {str(e)}")
            return None

    def clear(self, db_config: Optional[Dict[str, Any]] = None) -> int:
        """Limpia archivos de cache.

        Args:
            db_config (Optional[Dict[str, Any]]): Si se proporciona, elimina
                solo el cache de esa BD. Si es None, elimina todo el cache.
                Default: None.

        Returns:
            int: Número de archivos eliminados.

        Examples:
            >>> cache = MetadataCache()
            >>> # Limpiar cache específico
            >>> config = {"type": "mysql", "host": "localhost", "name": "test"}
            >>> cache.clear(config)
            1
            >>> # Limpiar todo el cache
            >>> cache.clear()
            5
        """
        try:
            deleted_count = 0

            if db_config:
                # Eliminar cache específico
                cache_key = self._generate_cache_key(db_config)
                cache_path = self._get_cache_path(cache_key)

                if cache_path.exists():
                    cache_path.unlink()
                    deleted_count = 1
                    logger.info(f"[CACHE] Cache eliminado: {cache_path.name}")
            else:
                # Eliminar todos los caches
                for cache_file in self.cache_dir.glob("*"):
                    if cache_file.is_file():
                        cache_file.unlink()
                        deleted_count += 1

                logger.info(f"[CACHE] {deleted_count} archivo(s) de cache eliminados")

            return deleted_count

        except Exception as e:
            logger.error(f"[CACHE] Error limpiando cache: {str(e)}")
            return 0

    def get_cache_info(self, db_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene información del cache sin cargarlo.

        Args:
            db_config (Dict[str, Any]): Configuración de BD.

        Returns:
            Optional[Dict[str, Any]]: Información del cache (timestamp, edad,
                tamaño) o None si no existe.

        Examples:
            >>> cache = MetadataCache()
            >>> config = {"type": "postgresql", "host": "localhost", "name": "db"}
            >>> info = cache.get_cache_info(config)
            >>> if info:
            ...     print(f"Edad: {info['age_hours']:.1f}h")
        """
        try:
            cache_key = self._generate_cache_key(db_config)
            cache_path = self._get_cache_path(cache_key)

            if not cache_path.exists():
                return None

            # Leer timestamp sin cargar metadata completa
            if self.serialization == "pickle":
                # nosec B301 - Pickle usado solo para cache local controlado, no datos externos
                with open(cache_path, "rb") as f:
                    cache_data = pickle.load(f)  # nosec
            else:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            age = datetime.now() - cached_time

            return {
                "path": str(cache_path),
                "timestamp": cached_time.isoformat(),
                "age_hours": age.total_seconds() / 3600,
                "is_valid": age <= self.ttl,
                "size_bytes": cache_path.stat().st_size,
                "serialization": self.serialization,
            }

        except Exception as e:
            logger.warning(f"[CACHE] Error obteniendo info de cache: {str(e)}")
            return None
