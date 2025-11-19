"""scavengr.core.interfaces
===========================

Interfaces (Ports) del dominio.
Define contratos que deben implementar los adaptadores de infraestructura.

Siguiendo el principio de Inversión de Dependencias (DIP):
- El dominio define QUÉ necesita (interfaces)
- La infraestructura implementa CÓMO lo hace (adaptadores)

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

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
    def get_columns(self) -> List[Tuple[str, str, bool, bool, Optional[str]]]:
        """Obtiene información de columnas de las tablas.

        Returns:
            List[Tuple]: Lista de tuplas con (table, column, is_pk, is_fk, default).
        """
        pass

    @abstractmethod
    def get_primary_keys(self) -> List[Tuple[str, str]]:
        """Obtiene información de claves primarias.

        Returns:
            List[Tuple]: Lista de tuplas con (table, column).
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[Tuple[str, str, str, str]]:
        """Obtiene información de claves foráneas.

        Returns:
            List[Tuple]: Lista de tuplas con (table, column, ref_table, ref_column).
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
            content (str): Contenido del archivo a parsear.

        Returns:
            DatabaseSchema: Esquema parseado y normalizado.

        Raises:
            InvalidFormatError: Si el formato no es válido.
            ProcessingError: Si falla el parsing.
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: Union[str, Path]) -> DatabaseSchema:
        """Parsea un archivo y retorna esquema normalizado.

        Args:
            file_path (Union[str, Path]): Ruta al archivo a parsear.

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
            schema (DatabaseSchema): Esquema a formatear.

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
    def export(self, data: Any, output_path: Union[str, Path], format: str) -> None:
        """Exporta datos al formato y ubicación especificados.

        Args:
            data (Any): Datos a exportar.
            output_path (Union[str, Path]): Ruta del archivo de salida.
            format (str): Formato de exportación (csv, excel, json).

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
            format (str): Formato a verificar.

        Returns:
            bool: True si el formato es soportado.
        """
        pass
