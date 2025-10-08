"""scavengr.infrastructure.database.connector
=============================================

Conectores de bases de datos para Scavengr.
Proporciona una interfaz unificada para conectar con diferentes motores de bases de datos.

Author: Json Rivera
Date: 2024-09-26
Version: 1.0
"""

from math import log
from typing import Dict, Any, Optional

# Importar conectores de bases de datos
try:
    import mysql.connector as mysql
    from mysql.connector import Error as mysql_errors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2 as pgsql
    from psycopg2 import Error as pgsql_errors
    PGSQL_AVAILABLE = True
except ImportError:
    PGSQL_AVAILABLE = False

try:
    import pyodbc as mssql
    from pyodbc import Error as mssql_errors
    MSSQL_AVAILABLE = True
except ImportError:
    MSSQL_AVAILABLE = False

from scavengr.config.config_manager import ConfigManager


class DatabaseConnector:
    """
    Clase base para conectores de bases de datos.
    Proporciona una interfaz común para diferentes tipos de bases de datos.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el conector base con la configuración.
        
        Args:
            config: Diccionario con la configuración de conexión
        """
        self.config = config
        self.connection = None
        self.cursor = None
        
    
    def connect(self):
        """
        Método abstracto para establecer la conexión.
        Debe ser implementado por las clases hijas.
        
        Raises:
            NotImplementedError: Esta clase base no implementa el método
        """
        raise NotImplementedError("El método connect debe ser implementado por las clases hijas")
    
    def close(self):
        """Cierra la conexión si está abierta."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.cursor = None
            except Exception as e:
                print(f"Error al cerrar la conexión: {e}")
    
    def is_connected(self) -> bool:
        """
        Verifica si la conexión está establecida.
        
        Returns:
            bool: True si la conexión está activa
        """
        return self.connection is not None
    
    def execute_query(self, query: str, params=None):
        """
        Ejecuta una consulta en la base de datos.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Resultado de la consulta
            
        Raises:
            Exception: Si hay un error al ejecutar la consulta
        """
        if not self.connection:
            raise Exception("No hay una conexión establecida")
            
        if not self.cursor:
            self.cursor = self.connection.cursor()
            
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            # Para consultas SELECT
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            
            # Para consultas de modificación
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Error al ejecutar la consulta: {e}")


class MSSQLConnector(DatabaseConnector):
    """Conector específico para SQL Server."""
    
    def connect(self):
        """
        Establece una conexión a SQL Server.
        
        Returns:
            Connection: Objeto de conexión a SQL Server
            
        Raises:
            ImportError: Si no está instalado el paquete pyodbc
            Exception: Si hay un error al conectar
        """
        if not MSSQL_AVAILABLE:
            raise ImportError("El paquete pyodbc no está instalado. Instálelo con: pip install pyodbc")
            
        try:
            # Obtener driver desde configuración o usar el predeterminado
            driver = self.config.get("DB_DRIVER", "SQL Server")
            
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={self.config['host']};"
                f"DATABASE={self.config['name']};"
                f"UID={self.config['user']};"
                f"PWD={self.config['password']};"
            )

            self.connection = mssql.connect(conn_str)
            
            # Validar la conexión
            if not self.connection:
                raise Exception("No se pudo establecer la conexión a SQL Server.")

            return self.connection
        except mssql_errors as e:
            raise Exception(f"Error al conectar a SQL Server: {e}")


class MySQLConnector(DatabaseConnector):
    """Conector específico para MySQL."""
    
    def connect(self):
        """
        Establece una conexión a MySQL.
        
        Returns:
            Connection: Objeto de conexión a MySQL
            
        Raises:
            ImportError: Si no está instalado el paquete mysql-connector-python
            Exception: Si hay un error al conectar
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("El paquete mysql-connector-python no está instalado. Instálelo con: pip install mysql-connector-python")
            
        try:
            # Obtener puerto desde configuración o usar el predeterminado
            port = self.config.get("DB_PORT", 3306)
            
            self.connection = mysql.connect(
                host=self.config["host"],
                port=port,
                database=self.config["name"],
                user=self.config["user"],
                password=self.config["password"]
            )
            return self.connection
        except mysql_errors as e:
            raise Exception(f"Error al conectar a MySQL: {e}")


class PostgreSQLConnector(DatabaseConnector):
    """Conector específico para PostgreSQL."""
    
    def connect(self):
        """
        Establece una conexión a PostgreSQL.
        
        Returns:
            Connection: Objeto de conexión a PostgreSQL
            
        Raises:
            ImportError: Si no está instalado el paquete psycopg2
            Exception: Si hay un error al conectar
        """
        if not PGSQL_AVAILABLE:
            raise ImportError("El paquete psycopg2 no está instalado. Instálelo con: pip install psycopg2-binary")
            
        try:
            # Obtener puerto desde configuración o usar el predeterminado
            port = self.config.get("DB_PORT", 5432)
            
            self.connection = pgsql.connect(
                host=self.config["host"],
                port=port,
                dbname=self.config["name"],
                user=self.config["user"],
                password=self.config["password"]
            )
            return self.connection
        except pgsql_errors as e:
            raise Exception(f"Error al conectar a PostgreSQL: {e}")


def create_connector(config: Dict[str, Any]) -> DatabaseConnector:
    """
    Fábrica de conectores - crea el conector apropiado según el tipo de base de datos.
    
    Args:
        config: Configuración de la conexión con la clave DB_TYPE
        
    Returns:
        DatabaseConnector: Instancia del conector apropiado
        
    Raises:
        ValueError: Si el tipo de base de datos no es soportado
    """
    db_type = config.get("type", "").upper()
    
    if db_type == "MSSQL":
        return MSSQLConnector(config)
    elif db_type == "MYSQL":
        return MySQLConnector(config)
    elif db_type == "POSTGRESQL":
        return PostgreSQLConnector(config)
    else:
        raise ValueError(f"Tipo de base de datos no soportado: {db_type}")


class ConnectionManager:
    """
    Gestor de conexiones para Scavengr.
    Maneja la creación, obtención y cierre de conexiones a bases de datos.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el gestor de conexiones.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_manager = ConfigManager(config_path)
        self.connections = {}
    
    def get_connection(self, connection_name: str):
        """
        Obtiene una conexión a una base de datos específica.
        Si la conexión ya existe, la devuelve; si no, la crea.
        
        Args:
            connection_name: Nombre de la conexión en el archivo de configuración
            
        Returns:
            Connection: Objeto de conexión a la base de datos
            
        Raises:
            KeyError: Si no existe la conexión especificada
            Exception: Si hay un error al establecer la conexión
        """
        # Si ya existe una conexión activa con ese nombre, la devuelve
        if connection_name in self.connections and self.connections[connection_name].is_connected():
            return self.connections[connection_name].connection
        
        # Obtiene la configuración y crea el conector
        db_config = self.config_manager.get_db_config(connection_name)
        connector = create_connector(db_config)
        
        # Establece la conexión y la guarda
        connection = connector.connect()
        self.connections[connection_name] = connector
        
        return connection
    
    def close_connection(self, connection_name: str) -> bool:
        """
        Cierra una conexión específica.
        
        Args:
            connection_name: Nombre de la conexión a cerrar
            
        Returns:
            bool: True si la conexión se cerró correctamente
        """
        if connection_name in self.connections:
            self.connections[connection_name].close()
            del self.connections[connection_name]
            return True
        return False
    
    def close_all_connections(self):
        """Cierra todas las conexiones abiertas."""
        for connector in self.connections.values():
            connector.close()
        self.connections = {}