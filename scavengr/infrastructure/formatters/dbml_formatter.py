"""scavengr.infrastructure.formatters.dbml_formatter
====================================================

Formateador de DBML para Scavengr.
Convierte entidades de dominio (DatabaseSchema) a formato DBML.
Implementa IFormatter del dominio.

Author: Json Rivera
Date: 2024-09-28
Version: 1.0
"""

from typing import Dict, Any, List
from datetime import datetime
import re


class DBMLFormatter:
    """Formateador para generar archivos DBML a partir de entidades de dominio.
    
    Convierte DatabaseSchema con sus tablas, columnas, relaciones e índices
    en sintaxis DBML válida conforme a la especificación de dbdiagram.io.
    """
    
    def __init__(self, schema=None, metadata: Dict[str, Any] = None):
        """
        Inicializar el formateador con schema y/o metadata.
        
        Args:
            schema: DatabaseSchema (entidad de dominio principal)
            metadata: Diccionario opcional con metadata adicional (source_system, database_info)
        """
        self.schema = schema
        self.metadata = metadata or {}
    
    def format(self) -> str:
        """
        Generar el contenido DBML a partir del schema de dominio.
        
        Returns:
            str: Contenido DBML generado
            
        Raises:
            ValueError: Si no hay schema disponible
        """
        if not self.schema:
            raise ValueError("Se requiere un DatabaseSchema para generar DBML")
        
        dbml_content = []
        
        # Comentario de encabezado
        dbml_content.append("// DBML generado automáticamente por Scavengr")
        dbml_content.append(f"// Fecha: {self.metadata.get('extraction_date', datetime.now().isoformat())}")
        dbml_content.append("")

        # Agregar objeto Project
        source_system = self.metadata.get('source_system', {})
        db_info = self.metadata.get('database_info', {})
        
        # Calcular métricas desde el schema
        tables_count = len(self.schema.tables)
        columns_count = sum(len(table.columns) for table in self.schema.tables)
        relationships_count = len(self.schema.relationships)
        indexes_count = len(self.schema.indexes)
        
        dbml_content.append(f'Project "{source_system.get("name", "Unknown")}" {{')
        dbml_content.append(f'  database_type: "{db_info.get("type", "unknown")}"')
        dbml_content.append("  note: '''")
        dbml_content.append(f'    # "{db_info.get("database", "Unknown")}" Base de Datos')
        dbml_content.append(f'\t\t* {tables_count} Tablas')
        dbml_content.append(f'\t\t* {columns_count} Campos')
        dbml_content.append(f'    * Relaciones: {relationships_count}')
        dbml_content.append(f'    * Índices: {indexes_count}')
        dbml_content.append(f'    * Escaneado por Scavengr - {datetime.now().strftime("%Y-%m-%d")}')
        dbml_content.append("  '''")
        dbml_content.append("}")
        dbml_content.append("")
        
        # Formatear tablas desde schema
        for table in self.schema.tables:
            dbml_content.extend(self._format_table(table))
            dbml_content.append("")
        
        # Formatear relaciones
        for rel in self.schema.relationships:
            dbml_content.append(self._format_relationship(rel))
        
        return "\n".join(dbml_content)
    
    def _format_table(self, table) -> List[str]:
        """
        Formatear una tabla desde entidad de dominio.
        
        Args:
            table: Entidad Table del dominio con sus columnas
            
        Returns:
            List[str]: Líneas DBML de la tabla
        """
        lines = []
        table_name = f"{table.schema}.{table.name}" if hasattr(table, 'schema') and table.schema else table.name
        lines.append(f"Table {table_name} {{")
        
        # Obtener foreign keys que apuntan desde esta tabla para agregar refs inline
        table_fks = self._get_table_foreign_keys(table)
        
        # Columnas
        for col in table.columns:
            col_line = f"  {col.name} {col.type}"
            attrs = []
            
            # Primary Key
            if col.is_pk:
                attrs.append("pk")
            
            # Nullability
            if not col.is_nullable:
                attrs.append("not null")
            
            # Foreign Key - Verificar si esta columna es una FK
            if col.name in table_fks:
                ref_table, ref_column = table_fks[col.name]
                attrs.append(f"ref: > {ref_table}.{ref_column}")
            
            # Default value
            if col.default:
                # Limpiar y formatear el valor por defecto
                default_val = str(col.default).strip()
                
                # Eliminar saltos de línea y espacios múltiples
                default_val = re.sub(r'\s+', ' ', default_val)
                
                # Eliminar paréntesis externos si los hay
                default_val = re.sub(r'^\((.*)\)$', r'\1', default_val)
                
                if default_val and default_val.upper() != "NULL":
                    # Para definiciones complejas de SQL Server (CREATE DEFAULT, etc)
                    # extraer solo el valor final después de "AS"
                    if 'create default' in default_val.lower():
                        match = re.search(r'\bas\s+(.+)$', default_val, re.IGNORECASE)
                        if match:
                            default_val = match.group(1).strip()
                    
                    attrs.append(f"default: `{default_val}`")
            
            # Note/Comment
            if hasattr(col, 'note') and col.note:
                # Escapar comillas simples en la nota
                note_escaped = str(col.note).replace("'", "\\'")
                attrs.append(f"note: '{note_escaped}'")
            
            if attrs:
                col_line += f" [{', '.join(attrs)}]"
            lines.append(col_line)
        
        # Bloque de índices agrupados para esta tabla
        table_indexes = self._get_table_indexes(table)
        if table_indexes:
            lines.append("")
            lines.append("  indexes {")
            for idx in table_indexes:
                if idx.columns:
                    columns_str = ", ".join(idx.columns)
                    attrs = []
                    if idx.unique:
                        attrs.append("unique")
                    if idx.name:
                        attrs.append(f"name: '{idx.name}'")
                    attr_str = f" [{', '.join(attrs)}]" if attrs else ""
                    lines.append(f"    ({columns_str}){attr_str}")
            lines.append("  }")
        
        lines.append("}")
        return lines
    
    def _get_table_foreign_keys(self, table) -> Dict[str, tuple]:
        """
        Obtener foreign keys que salen de esta tabla.
        
        Args:
            table: Entidad Table
            
        Returns:
            Dict[str, tuple]: Mapeo de columna_origen -> (tabla_destino, columna_destino)
        """
        fks = {}
        table_name = table.name
        
        # Buscar relaciones en el schema
        if self.schema and hasattr(self.schema, 'relationships'):
            for rel in self.schema.relationships:
                # Comparar solo el nombre de la tabla (sin schema)
                rel_from_table = rel.from_table.split('.')[-1] if '.' in rel.from_table else rel.from_table
                if rel_from_table == table_name:
                    fks[rel.from_column] = (rel.to_table, rel.to_column)
        
        return fks
    
    def _get_table_indexes(self, table) -> List:
        """
        Obtener índices de esta tabla desde el schema.
        
        Args:
            table: Entidad Table
            
        Returns:
            List[Index]: Lista de índices de la tabla
        """
        table_indexes = []
        table_name = table.name
        
        # Buscar índices en el schema
        if self.schema and hasattr(self.schema, 'indexes'):
            for idx in self.schema.indexes:
                # Comparar solo el nombre de la tabla (sin schema)
                idx_table = idx.table.split('.')[-1] if '.' in idx.table else idx.table
                if idx_table == table_name:
                    table_indexes.append(idx)
        
        return table_indexes
    
    def _format_relationship(self, rel) -> str:
        """
        Formatear relación desde entidad de dominio.
        
        Args:
            rel: Entidad Relationship del dominio
            
        Returns:
            str: Línea DBML de la relación
        """
        # Determinar el tipo de relación (>, <, -, <>, etc.)
        rel_type = getattr(rel, 'relationship_type', '>')
        return f"Ref: {rel.from_table}.{rel.from_column} {rel_type} {rel.to_table}.{rel.to_column}"
    
    def save_to_file(self, output_path: str) -> None:
        """
        Generar y guardar el archivo DBML.
        
        Args:
            output_path: Ruta donde guardar el archivo DBML
        """
        dbml_content = self.format()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dbml_content)
