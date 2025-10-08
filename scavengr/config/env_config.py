"""
Módulo para gestión segura de configuración basada en variables de entorno.
Toda la configuración se obtiene desde archivos .env

Author: Json Rivera
Date: 2024-09-26
Version: 0.1
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    pass


class EnvConfigManager:
    """
    Gestor de configuración simple basado solo en variables de entorno.
    Una sola fuente de configuración desde archivos .env
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Inicializar el gestor de configuración.
        
        Args:
            env_file: Archivo .env específico a cargar (opcional)
        """
        self._load_environment(env_file)
    
    def _load_environment(self, env_file: Optional[str] = None):
        """Cargar variables de entorno desde archivos .env"""
        env_files_to_try = []
        
        if env_file:
            env_files_to_try.append(env_file)
        
        # Orden de prioridad para archivos .env
        env_files_to_try.extend([
            ".env.local",   # Específico del desarrollador (máxima prioridad)
            ".env",         # General del proyecto
        ])
        
        loaded_files = []
        for env_file_path in env_files_to_try:
            if os.path.exists(env_file_path):
                load_dotenv(env_file_path, override=True)
                loaded_files.append(env_file_path)
        
        if loaded_files:
            print(f"✅ Variables de entorno cargadas desde: {', '.join(loaded_files)}")
        else:
            print("ℹ️  No se encontraron archivos .env, usando variables del sistema")
    
    def _validate_env_var(self, env_var: str, default: Any = None, required: bool = False) -> Any:
        """
        Validar una variable de entorno.

        Args:
            env_var (str): Nombre de la variable de entorno.
            default (Any): Valor por defecto si no está configurada.
            required (bool): Indica si la variable es obligatoria.

        Returns:
            Any: Valor de la variable de entorno.

        Raises:
            ConfigError: Si la variable requerida no está configurada.
        """
        value = os.getenv(env_var, default)
        if required and not value and value != "":
            raise ConfigError(f"La variable de entorno requerida '{env_var}' no está configurada.")
        return value

    def get_db_config(self, env_prefix: str = "DB") -> Dict[str, Any]:
        """
        Obtener configuración de base de datos desde variables de entorno.
        
        Args:
            env_prefix: Prefijo para las variables (DB, PROD_DB, DEV_DB, etc.)
            
        Returns:
            Dict con configuración de base de datos
        """
        prefix = f"{env_prefix}_" if not env_prefix.endswith("_") else env_prefix
        
        # Variables requeridas
        required_vars = {
            'type': f"{prefix}TYPE",
            'host': f"{prefix}HOST", 
            'name': f"{prefix}NAME",
            'user': f"{prefix}USER",
            'password': f"{prefix}PASSWORD"
        }

        # Variables opcionales con valores por defecto
        optional_vars = {
            'port': (f"{prefix}PORT", None),
            'driver': (f"{prefix}DRIVER", None)
        }

        config = {}

        # Validar y cargar variables requeridas
        for key, env_var in required_vars.items():
            config[key] = self._validate_env_var(env_var, required=True)

        # Validar el tipo de base de datos
        supported_db_types = ['postgresql', 'mysql', 'mssql']
        if config['type'].lower() not in supported_db_types:
            raise ConfigError(f"Tipo de base de datos no soportado: {config['type']}. Tipos soportados: {', '.join(supported_db_types)}")

        # Cargar variables opcionales con nombres simples
        for key, (env_var, default) in optional_vars.items():
            config[key] = self._validate_env_var(env_var, default=default)

        # Convertir puerto a entero si está presente
        if 'port' in config and config['port']:
            try:
                config['port'] = int(config['port'])
            except ValueError:
                # Si no se puede convertir, usar puertos por defecto según el tipo
                default_ports = {
                    'postgresql': 5432,
                    'mysql': 3306,
                    'mssql': 1433
                }
                config['port'] = default_ports.get(config['type'].lower(), None)

        return config
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Obtener configuración para generación de diccionarios."""
        return {
            'source_system': {
                'name': os.getenv('SOURCE_SYSTEM_NAME', 'Sistema de Base de Datos'),
                'version': os.getenv('SOURCE_SYSTEM_VERSION', '1.0'),
                'environment': os.getenv('SOURCE_ENVIRONMENT', 'production')
            },
            'file_prefix': os.getenv('OUTPUT_FILE_PREFIX', 'diccionario_datos')
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtener configuración básica de logging (mantenido por compatibilidad)."""
        return {
            'level': 'INFO',
            'debug_mode': False
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Obtener configuración básica de seguridad (mantenido por compatibilidad)."""
        return {
            'connection_timeout': 30,
            'max_retries': 3
        }
    
    def get_advanced_config(self) -> Dict[str, Any]:
        """Obtener configuración básica (mantenido por compatibilidad)."""
        return {}
    
    def get_all_config(self) -> Dict[str, Any]:
        """Obtener toda la configuración consolidada."""
        return {
            'database': self.get_db_config(),
            'generation': self.get_generation_config(),
            'logging': self.get_logging_config(),
            'security': self.get_security_config(),
            'advanced': self.get_advanced_config()
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validar configuración esencial.
        
        Returns:
            Dict con resultado de validación
        """
        issues = []
        warnings = []
        
        try:
            db_config = self.get_db_config()

            # Contraseñas inseguras comunes
            non_secured_pass = ["", "password", "123456", "admin", "root"]
            
            #  == 'test_password' or db_config['password'] == ""
            # Validar configuración de BD
            if db_config['password'] in non_secured_pass:
                warnings.append("Parece estar usando una contraseña de prueba o vacía.")
                warnings.append("Considere usar contraseñas seguras en entornos de producción.")
                
        except ConfigError as e:
            issues.append(str(e))
        
        # Validar archivos .env
        if not os.path.exists('.env'):
            warnings.append("Archivo .env no encontrado, usando variables del sistema")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _get_bool(self, env_var: str, default: bool) -> bool:
        """Obtener variable booleana de entorno."""
        value = os.getenv(env_var)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_int(self, env_var: str, default: int) -> int:
        """Obtener variable entera de entorno."""
        value = os.getenv(env_var)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            print(f"⚠️  Valor inválido para {env_var}: {value}, usando por defecto: {default}")
            return default


# Funciones de utilidad para compatibilidad
def load_env_config(env_file: Optional[str] = None) -> EnvConfigManager:
    """
    Función de utilidad para crear gestor de configuración.
    
    Args:
        env_file: Archivo .env específico (opcional)
        
    Returns:
        EnvConfigManager configurado
    """
    return EnvConfigManager(env_file)


def get_database_config(env_prefix: str = "DB") -> Dict[str, Any]:
    """
    Función rápida para obtener configuración de BD.
    
    Args:
        env_prefix: Prefijo de variables (DB, PROD_DB, DEV_DB)
        
    Returns:
        Dict con configuración de base de datos
    """
    manager = EnvConfigManager()
    return manager.get_db_config(env_prefix)


if __name__ == "__main__":
    # Ejemplo de uso y validación
    print("🔧 Scavengr - Gestor de Configuración")
    print("=" * 50)
    
    manager = EnvConfigManager()
    validation = manager.validate_config()
    
    if validation['valid']:
        print("✅ Configuración válida")
        config = manager.get_all_config()
        print(f"📊 Configuración cargada para: {config['generation']['source_system']['name']}")
    else:
        print("❌ Problemas de configuración:")
        for issue in validation['issues']:
            print(f"   • {issue}")
    
    if validation['warnings']:
        print("\n⚠️  Advertencias:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
            
    print("\n💡 Para configurar, copie .env.example a .env y edite las variables")