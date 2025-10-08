"""scavengr.core.interfaces
===========================

Interfaces (Ports) del dominio.
Define contratos que deben implementar los adaptadores de infraestructura.

Siguiendo el principio de Inversión de Dependencias (DIP):
- El dominio define QUÉ necesita (interfaces)
- La infraestructura implementa CÓMO lo hace (adaptadores)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from scavengr.core.entities import DatabaseSchema


class IMetadataScanner(ABC):
    """Puerto para escanear metadata de bases de datos.

    Los adaptadores concretos implementan esta interfaz para
    diferentes motores de base de datos (PostgreSQL, MySQL, SQL Server, etc.).
    """

    @abstractmethod
    def scan_schema(self) -> DatabaseSchema:
        """Escanea el esquema de la base de datos y retorna estructura normalizada.

        Returns:
            DatabaseSchema: Esquema completo con tablas, relaciones e índices.

        Raises:
            ProcessingError: Si falla el escaneo de la base de datos.
        """
        pass

    @abstractmethod
    def get_columns(self) -> List[tuple]:
        """Obtiene información de columnas de las tablas.

        Returns:
            List[tuple]: Lista de tuplas con información de columnas.
        """
        pass

    @abstractmethod
    def get_primary_keys(self) -> List[tuple]:
        """Obtiene información de claves primarias.

        Returns:
            List[tuple]: Lista de tuplas con información de PKs.
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[tuple]:
        """Obtiene información de claves foráneas.

        Returns:
            List[tuple]: Lista de tuplas con información de FKs.
        """
        pass


class IParser(ABC):
    """Puerto para parsear archivos.

    Los adaptadores concretos implementan esta interfaz para
    diferentes formatos (DBML, SQL DDL, JSON, etc.).
    """

    @abstractmethod
    def parse(self, content: str) -> DatabaseSchema:
        """Parsea contenido y retorna esquema normalizado.

        Args:
            content: Contenido del archivo a parsear.

        Returns:
            DatabaseSchema: Esquema parseado y normalizado.

        Raises:
            InvalidFormatError: Si el formato no es válido.
            ProcessingError: Si falla el parsing.
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: str) -> DatabaseSchema:
        """Parsea un archivo y retorna esquema normalizado.

        Args:
            file_path: Ruta al archivo a parsear.

        Returns:
            DatabaseSchema: Esquema parseado y normalizado.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            InvalidFormatError: Si el formato no es válido.
        """
        pass


class IFormatter(ABC):
    """Puerto para formatear datos.

    Los adaptadores concretos implementan esta interfaz para
    diferentes formatos de salida (DBML, JSON, Markdown, etc.).
    """

    @abstractmethod
    def format(self, schema: DatabaseSchema) -> str:
        """Formatea un esquema a un formato específico.

        Args:
            schema: Esquema a formatear.

        Returns:
            str: Contenido formateado como string.

        Raises:
            ProcessingError: Si falla el formateo.
        """
        pass


class IExporter(ABC):
    """Puerto para exportar datos.

    Los adaptadores concretos implementan esta interfaz para
    diferentes formatos de exportación (Excel, CSV, JSON, etc.).
    """

    @abstractmethod
    def export(self, data: Any, output_path: str, format: str) -> None:
        """Exporta datos al formato y ubicación especificados.

        Args:
            data: Datos a exportar.
            output_path: Ruta del archivo de salida.
            format: Formato de exportación (csv, excel, json).

        Raises:
            InvalidFormatError: Si el formato no es soportado.
            ValidationError: Si no hay permisos de escritura.
            ProcessingError: Si falla la exportación.
        """
        pass

    @abstractmethod
    def supports_format(self, format: str) -> bool:
        """Verifica si el exportador soporta un formato.

        Args:
            format: Formato a verificar.

        Returns:
            bool: True si el formato es soportado.
        """
        pass
