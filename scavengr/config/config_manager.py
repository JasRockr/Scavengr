"""
Módulo de gestión de configuración para Scavengr.
Gestor de configuración que usa variables de entorno (.env)

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

from typing import Any, Dict, List, Optional

from .env_config import EnvConfigManager


class ConfigManager:
    """
    Clase para gestionar la configuración basada en variables de entorno.
    Toda la configuración se obtiene desde archivos .env
    Compatible con la interfaz anterior para mantener funcionalidad.
    """

    def __init__(self, env_file: Optional[str] = None) -> None:
        """
        Inicializa el gestor de configuración.

        Args:
            env_file: Archivo .env específico a cargar (opcional)
        """
        self.env_manager: EnvConfigManager = EnvConfigManager(env_file)
        # Mantener compatibilidad
        self.config_data: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde variables de entorno.

        Returns:
            Dict[str, Any]: Datos de configuración cargados desde .env
        """
        # Usar el EnvConfigManager para cargar toda la configuración
        try:
            db_config: Dict[str, Any] = self.env_manager.get_db_config()
            generation_config: Dict[str, Any] = self.env_manager.get_generation_config()

            # Estructura compatible
            self.config_data = {"default": {**db_config, **generation_config}}

            return self.config_data
        except Exception:
            # Si falla la carga desde .env, devolver estructura vacía pero válida
            self.config_data = {}
            return self.config_data

    def get_db_config(self, connection_name: str = "default") -> Dict[str, Any]:
        """
        Obtiene la configuración para una conexión específica.
        Ahora obtiene datos desde variables de entorno.

        Args:
            connection_name: Nombre de la conexión (usa "default")

        Returns:
            Dict[str, Any]: Configuración de la conexión desde .env
        """
        try:
            # Usar EnvConfigManager directamente
            return self.env_manager.get_db_config()
        except Exception as e:
            raise KeyError(
                f"No se pudo cargar la configuración de la conexión '{connection_name}': {e}"
            )

    def get_available_connections(self) -> list[str]:
        """
        Obtiene la lista de conexiones disponibles.
        Siempre hay una conexión "default" desde .env

        Returns:
            list[str]: Lista de nombres de conexiones (["default"])
        """
        try:
            # Verificar si hay configuración válida en .env
            self.env_manager.get_db_config()
            return ["default"]
        except Exception:
            return []

    def validate_connection_config(self, connection_config: Dict[str, Any]) -> bool:
        """
        Valida que una configuración de conexión tenga todos los campos necesarios.
        Usa la validación de EnvConfigManager.

        Args:
            connection_config: Configuración a validar

        Returns:
            bool: True si la configuración es válida
        """
        try:
            # Usar la validación del EnvConfigManager
            required_fields: List[str] = [
                "DB_TYPE",
                "host",
                "DB_NAME",
                "DB_USER",
                "DB_PASSWORD",
            ]

            for field in required_fields:
                if field not in connection_config or not connection_config[field]:
                    raise ValueError(f"Campo requerido faltante: {field}")

            db_type: str = connection_config.get("DB_TYPE", "").upper()
            if db_type not in ["MSSQL", "MYSQL", "POSTGRESQL"]:
                raise ValueError(f"Tipo de base de datos no soportado: {db_type}")

            return True
        except Exception as e:
            raise ValueError(f"Configuración inválida: {e}")

    # Métodos adicionales
    def get_generation_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de generación desde .env

        Returns:
            Dict[str, Any]: Configuración de generación
        """
        try:
            return self.env_manager.get_generation_config()
        except Exception:
            return {}
