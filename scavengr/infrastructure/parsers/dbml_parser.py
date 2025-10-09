"""
Módulo para el análisis de archivos DBML.
Parsea archivos DBML y genera una estructura de datos que representa el esquema.
Este módulo combina las mejores características para procesar archivos DBML de manera robusta.

Author: Json Rivera
Date: 2025-09-26
Version: 0.0.1
"""

import os
import re
from typing import List, Dict, Any, Optional

from scavengr.core.entities import Column, Table, Relationship, Index, DatabaseSchema


class DBMLParser:
    """
    Clase para parsear archivos DBML y generar una estructura de datos representativa.
    """
    
    def __init__(self, dbml_file_path: str):
        """
        Inicializa el parser con la ruta al archivo DBML.
        
        Args:
            dbml_file_path: Ruta al archivo DBML
        """
        self.dbml_file_path = dbml_file_path
        self.tables = {}
        self.relationships = []
        self.indexes = []
        
    def parse(self) -> Dict[str, Any]:
        """
        Parsea el archivo DBML y devuelve un diccionario con la estructura del esquema.
        Versión robusta con mejor validación y manejo de errores.
        
        Returns:
            Dict[str, Any]: Estructura del esquema de la base de datos
            
        Raises:
            FileNotFoundError: Si el archivo DBML no existe
            ValueError: Si el formato del archivo DBML es inválido
        """
        if not os.path.exists(self.dbml_file_path):
            raise FileNotFoundError(f"Archivo DBML no encontrado: {self.dbml_file_path}")
        
        try:
            with open(self.dbml_file_path, 'r', encoding='utf-8') as file:
                dbml_content = file.read()
            
            if not dbml_content.strip():
                raise ValueError(f"El archivo DBML está vacío: {self.dbml_file_path}")
                
            # Parsear tablas
            self._parse_tables(dbml_content)
            
            # Parsear relaciones
            self._parse_relationships(dbml_content)
            
            # Identificar tablas maestras basadas en relaciones
            self._identify_master_tables()
            
            # Convertir a lista de objetos Table para compatibilidad
            tables_list = list(self.tables.values())
            
            # Construir resultado con formato esperado por data_generator
            schema = {
                'tables': tables_list,
                'relationships': self.relationships
            }
            
            return schema
        except Exception as e:
            raise ValueError(f"Error al parsear el archivo DBML: {str(e)}")
    
    def _parse_tables(self, content: str):
        """
        Parsea las definiciones de tablas con mejor manejo de atributos.
        Versión robusta que combina ambas implementaciones.
        
        Args:
            content: Contenido del archivo DBML
        """
        # Regex robusto para encontrar bloques de tablas (incluyendo esquema.tabla)
        table_pattern = r'Table\s+([\w\.]+)\s*\{(.*?)\}'
        table_matches = re.findall(table_pattern, content, re.DOTALL)
        
        for table_name, table_content in table_matches:
            # Crear la tabla
            table = Table(name=table_name)
            
            # Parsear columnas con lógica robusta de /src
            columns = self._parse_columns(table_content, table_name)
            table.columns = columns
            
            # Parsear nota de tabla
            table_note = self._parse_table_note(table_content)
            table.note = table_note
            
            self.tables[table_name] = table
    
    def _parse_columns(self, table_content: str, table_name: str) -> List[Column]:
        """
        Parsea las columnas con mejor detección de atributos y referencias.
        Combina la lógica robusta de ambas versiones.
        
        Args:
            table_content: Contenido de la definición de la tabla
            table_name: Nombre de la tabla
            
        Returns:
            List[Column]: Lista de columnas de la tabla
        """
        columns = []
        # Patrón robusto para capturar atributos complejos (de /src)
        column_pattern = r"(\w+)\s+([\w\(\)\,]+)\s*(?:\[(.*?)\])?"

        for line in table_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("indexes"):
                continue

            match = re.match(column_pattern, line)
            if match:
                name, data_type, attributes_str = match.groups()
                attributes_str = attributes_str or ""

                # Parsear atributos individuales
                attributes = [attr.strip() for attr in attributes_str.split(',') if attr.strip()]

                # Extraer referencia si existe (lógica de /src)
                ref_match = re.search(r"ref:\s*[<>-]*\s*([\w\.]+)", attributes_str)
                ref_table, ref_column = None, None
                if ref_match:
                    ref_full = ref_match.group(1)
                    if "." in ref_full:
                        ref_table, ref_column = ref_full.split(".")
                    else:
                        # Auto-referencia
                        ref_table = table_name
                        ref_column = ref_full

                column = Column(
                    name=name.strip(),
                    type=data_type.strip(),
                    is_pk="pk" in attributes_str or "primary key" in attributes_str.lower(),
                    is_nullable="not null" not in attributes_str.lower(),
                    note=None,
                    ref_table=ref_table,
                    ref_column=ref_column,
                    attributes=attributes  # Mantenemos para compatibilidad
                )
                columns.append(column)

        return columns
    
    def _parse_table_note(self, table_content: str) -> Optional[str]:
        """
        Extraer comentarios de la tabla.
        
        Args:
            table_content: Contenido de la definición de la tabla
            
        Returns:
            Optional[str]: Comentario de la tabla si existe
        """
        # Buscar comentarios de tabla
        note_match = re.search(r"//\s*(.*?)$", table_content, re.MULTILINE)
        return note_match.group(1).strip() if note_match else None
    
    def _parse_relationships(self, content: str):
        """
        Parsea las relaciones con mejor detección de patrones.
        Versión robusta que maneja múltiples formatos.
        
        Args:
            content: Contenido del archivo DBML
        """
        # Buscar relaciones explícitas con sintaxis Ref: (lógica de /src)
        ref_pattern = r"Ref:\s*([\w\.]+)\s*([<>-]+)\s*([\w\.]+)"
        ref_matches = re.findall(ref_pattern, content, re.MULTILINE | re.IGNORECASE)

        for from_ref, rel_type, to_ref in ref_matches:
            from_table, from_column = (
                from_ref.split(".") if "." in from_ref else (None, from_ref)
            )
            to_table, to_column = to_ref.split(".") if "." in to_ref else (None, to_ref)

            relationship = Relationship(
                from_table=from_table or "",
                from_column=from_column or "",
                to_table=to_table or "",
                to_column=to_column or "",
                relationship_type=rel_type,
            )
            self.relationships.append(relationship)
    
    def _identify_master_tables(self):
        """
        Identificar tablas maestras basadas en relaciones.
        Lógica robusta de /src.
        """
        # Tablas que son referenciadas por otras
        referenced_tables = set()
        for rel in self.relationships:
            if rel.to_table:
                referenced_tables.add(rel.to_table)

        # Marcar tablas como maestras
        for table_name in referenced_tables:
            if table_name in self.tables:
                self.tables[table_name].is_master = True
            
            # Verificar si tiene columnas PK que son referenciadas
            if table_name in self.tables:
                for col in self.tables[table_name].columns:
                    if col.is_pk and any(
                        rel.to_table == table_name and rel.to_column == col.name
                        for rel in self.relationships
                    ):
                        self.tables[table_name].is_master = True
                        break
