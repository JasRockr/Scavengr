"""Caso de uso para generación de diccionarios de datos.

Este módulo implementa la lógica de aplicación para generar diccionarios
de datos desde archivos DBML, usando los servicios de dominio para
inferencia de regex, máscaras y criterios de calidad.

Examples:
    >>> from scavengr.application.dictionary import GenerateDictionary
    >>> use_case = GenerateDictionary()
    >>> result = use_case.execute("schema.dbml", "dictionary.xlsx", "excel")
    >>> print(result.success)
    True

Author: Json Rivera
Date: 2025-01-06
Version: 1.0.0
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from scavengr.infrastructure.parsers import DBMLParser
from scavengr.infrastructure.exporters import OutputWriter
from scavengr.core.entities import DatabaseSchema, Table, Column
from scavengr.core.services import (
    RegexInferenceService,
    MaskGeneratorService,
    QualityCriteriaService,
    RelationshipAnalyzer,
    ExampleGeneratorService,
    ModuleClassifierService,
    SensitivityAnalyzerService,
    ObservationGeneratorService,
    DescriptionGeneratorService,
)

logger = logging.getLogger(__name__)


@dataclass
class DictionaryResult:
    """Resultado de la generación del diccionario.
    
    Attributes:
        success (bool): Indica si la generación fue exitosa.
        output_path (str): Ruta del archivo generado.
        entries_count (int): Número de entradas generadas.
        format (str): Formato del archivo generado.
        file_size (int): Tamaño del archivo en bytes.
        error_message (Optional[str]): Mensaje de error si la generación falló.
    """
    
    success: bool
    output_path: str = ""
    entries_count: int = 0
    format: str = ""
    file_size: int = 0
    error_message: Optional[str] = None


class GenerateDictionary:
    """Caso de uso para generar diccionarios de datos.
    
    Orquesta el proceso completo de:
    1. Parseo del archivo DBML
    2. Inferencia de regex y máscaras usando servicios de dominio
    3. Generación de criterios de calidad
    4. Análisis de relaciones
    5. Exportación a formato deseado (Excel, CSV, JSON)
    
    Args:
        config (Optional[Dict[str, Any]]): Configuración adicional.
        
    Examples:
        >>> use_case = GenerateDictionary()
        >>> result = use_case.execute(
        ...     input_path="schema.dbml",
        ...     output_path="dict.xlsx",
        ...     output_format="excel"
        ... )
        >>> if result.success:
        ...     print(f"Generado: {result.entries_count} entradas")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa el caso de uso.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuración opcional.
        """
        self.config = config or {}
        
        # Inicializar servicios de dominio
        country_code = self.config.get('country_code', 'CO')
        default_module = self.config.get('default_module', 'General')
        
        self.regex_service = RegexInferenceService(country_code)
        self.mask_service = MaskGeneratorService()
        self.quality_service = QualityCriteriaService()
        self.relationship_analyzer = RelationshipAnalyzer()
        self.example_service = ExampleGeneratorService()
        self.module_service = ModuleClassifierService(default_module)
        self.sensitivity_service = SensitivityAnalyzerService()
        self.observation_service = ObservationGeneratorService()
        self.description_service = DescriptionGeneratorService()
    
    def execute(
        self,
        input_path: str,
        output_path: str,
        output_format: str = "excel"
    ) -> DictionaryResult:
        """Ejecuta la generación del diccionario de datos.
        
        Args:
            input_path (str): Ruta del archivo DBML de entrada.
            output_path (str): Ruta del archivo de salida.
            output_format (str): Formato de salida ('excel', 'csv', 'json').
            
        Returns:
            DictionaryResult: Resultado de la operación.
            
        Raises:
            FileNotFoundError: Si el archivo de entrada no existe.
            ValueError: Si el formato de salida no es soportado.
        """
        try:
            logger.info(f"[DICTIONARY] Generando diccionario desde: {input_path}")
            
            # Paso 1: Validar archivo de entrada
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
            
            # Paso 2: Parsear DBML
            schema = self._parse_dbml(input_path)
            
            # Paso 3: Generar entradas del diccionario
            entries = self._generate_dictionary_entries(schema)
            
            # Paso 4: Exportar a formato deseado
            self._export_dictionary(entries, output_path, output_format)
            
            # Paso 5: Construir resultado
            file_size = os.path.getsize(output_path)
            
            result = DictionaryResult(
                success=True,
                output_path=output_path,
                entries_count=len(entries),
                format=output_format,
                file_size=file_size
            )
            
            logger.info(
                f"[SUCCESS] Diccionario generado: "
                f"{result.entries_count} entradas en formato {output_format}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Error generando diccionario: {str(e)}")
            
            return DictionaryResult(
                success=False,
                error_message=str(e)
            )
    
    def _parse_dbml(self, file_path: str) -> DatabaseSchema:
        """Parsea el archivo DBML a esquema de dominio.
        
        Args:
            file_path (str): Ruta del archivo DBML.
            
        Returns:
            DatabaseSchema: Esquema parseado.
        """
        logger.info("[INFO] Parseando archivo DBML...")
        
        # Instanciar parser con la ruta del archivo
        parser = DBMLParser(file_path)
        schema_dict = parser.parse()
        
        # Convertir dict a DatabaseSchema
        schema = DatabaseSchema(
            name="Database",
            tables=schema_dict.get('tables', []),
            relationships=schema_dict.get('relationships', []),
            metadata=schema_dict
        )
        
        logger.info(
            f"[INFO] Parseado exitoso: "
            f"{len(schema.tables)} tablas, "
            f"{len(schema.relationships)} relaciones"
        )
        
        return schema
    
    def _generate_dictionary_entries(
        self,
        schema: DatabaseSchema
    ) -> List[Dict[str, Any]]:
        """Genera entradas del diccionario desde el esquema.
        
        Args:
            schema (DatabaseSchema): Esquema de base de datos.
            
        Returns:
            List[Dict[str, Any]]: Lista de entradas del diccionario.
        """
        logger.info("[INFO] Generando entradas del diccionario...")
        
        entries = []
        
        # Crear mapa de relaciones por tabla.columna
        relationships_map = {}
        for rel in schema.relationships:
            key = f"{rel.from_table}.{rel.from_column}"
            relationships_map[key] = rel
        
        # Procesar cada tabla
        for table in schema.tables:
            # Procesar cada columna
            for column in table.columns:
                entry = self._generate_column_entry(
                    table,
                    column,
                    relationships_map.get(f"{table.name}.{column.name}"),
                    schema
                )
                entries.append(entry)
        
        logger.info(f"[INFO] Generadas {len(entries)} entradas")
        
        return entries
    
    def _generate_column_entry(
        self,
        table: Table,
        column: Column,
        relationship: Optional[Any],
        schema: DatabaseSchema
    ) -> Dict[str, Any]:
        """Genera una entrada de diccionario para una columna.
        
        Args:
            table (Table): Tabla que contiene la columna.
            column (Column): Columna a procesar.
            relationship (Optional[Any]): Relación asociada si existe.
            schema (DatabaseSchema): Esquema completo para metadata.
            
        Returns:
            Dict[str, Any]: Entrada del diccionario.
        """
        # Inferir regex y máscara usando servicios del dominio
        regex = self.regex_service.infer_regex(column.type, column.name)
        mask = self._infer_mask(column.type, column.name, regex)

        # Criterios de calidad y tipo de relación
        criteria = self._generate_quality_criteria(column, relationship, regex)
        rel_type = self._get_relationship_type(column, relationship, table.name)

        # Construir entrada con la estructura requerida
        entry = {
            "TABLA": table.name,
            "NOMBRE_DATO": column.name,
            "TIPO_DE_DATO": (column.type or '').upper(),
            "LONGITUD": self._extract_length(column.type),
            "DESCRIPCION": self._generate_description(column, relationship, table.is_master),
            "REGEX": regex or "",
            "MASCARA": mask,
            "CRITERIOS_CALIDAD": criteria,
            "TABLA_MAESTRA": (relationship.to_table if relationship else column.ref_table),
            "CAMPO_MAESTRO": (relationship.to_column if relationship else column.ref_column),
            "TIPO_RELACION": rel_type,
            "ES_MAESTRA": bool(table.is_master),
            "ES_PK": bool(column.is_pk),
            "ES_NULLABLE": bool(column.is_nullable),
            "EJEMPLOS_VALIDOS": self.example_service.generate_example(
                column.type, column.name, mask
            ),
            # Normalizar FUENTE_CAPTURA: si es un dict, tomar el campo 'name'
            "FUENTE_CAPTURA": (
                (self.config.get('source_system') or 'Sistema Origen').get('name')
                if isinstance(self.config.get('source_system'), dict)
                else (self.config.get('source_system') or 'Sistema Origen')
            ),
            "MODULO": self.module_service.classify_module(table.name),
            "SENSIBILIDAD": self.sensitivity_service.analyze_sensitivity(column.name).get('nivel', 'BAJO'),
            "OBSERVACIONES": self.observation_service.generate_observation(
                column, relationship
            ),
        }

        return entry

    # ---------------- Helper methods para estructura del diccionario ----------------
    def _generate_description(self, column: Column, relationship: Optional[Any], is_master: bool) -> str:
        """Genera una descripción inteligente para la columna usando DescriptionGeneratorService.

        Args:
            column (Column): Columna a describir.
            relationship (Optional[Any]): Relación asociada si existe.
            is_master (bool): Si la tabla es maestra.
            
        Returns:
            str: Descripción inteligente generada.
        """
        return self.description_service.generate_description(column, relationship, is_master)

    def _infer_mask(self, data_type: str, field_name: str, regex: Optional[str]) -> str:
        """Wrapper para generar máscara usando MaskGeneratorService."""
        try:
            return self.mask_service.generate_mask(data_type, field_name, regex)
        except Exception:
            return ""

    def _generate_quality_criteria(self, column: Column, relationship: Optional[Any], regex: Optional[str]) -> str:
        """Wrapper que delega en QualityCriteriaService."""
        try:
            return self.quality_service.generate_criteria(column, relationship, regex)
        except Exception:
            return ""

    def _get_relationship_type(self, column: Column, relationship: Optional[Any], current_table: Optional[str] = None) -> str:
        """Devuelve el tipo de relación usando RelationshipAnalyzer."""
        try:
            return self.relationship_analyzer.analyze_relationship(column, relationship, current_table or "")
        except Exception:
            return ""
    
    def _extract_length(self, data_type: str) -> str:
        """Extrae la longitud de un tipo de dato.
        
        Args:
            data_type (str): Tipo de dato (ej: "varchar(50)").
            
        Returns:
            str: Longitud extraída o cadena vacía.
        """
        import re
        match = re.search(r'\((\d+)\)', data_type)
        return match.group(1) if match else ""
    
    def _get_key_type(self, column: Column, rel_type: str) -> str:
        """Determina el tipo de llave de una columna.
        
        Args:
            column (Column): Columna a evaluar.
            rel_type (str): Tipo de relación.
            
        Returns:
            str: Tipo de llave ('PK', 'FK', 'PK/FK', '').
        """
        if column.is_pk and "FK" in rel_type:
            return "PK/FK"
        elif column.is_pk:
            return "PK"
        elif "FK" in rel_type:
            return "FK"
        return ""
    
    def _generate_example(self, column: Column, mask: str) -> str:
        """Genera un ejemplo de valor para una columna.
        
        Args:
            column (Column): Columna.
            mask (str): Máscara de formato.
            
        Returns:
            str: Ejemplo de valor.
        """
        # Si hay máscara, usarla como ejemplo
        if mask and mask != "VALOR":
            return mask
        
        # Ejemplos por tipo de dato
        base_type = column.type.split("(")[0].lower()
        
        examples = {
            'int': '123',
            'bigint': '123456789',
            'smallint': '12',
            'varchar': 'Texto de ejemplo',
            'char': 'ABC',
            'text': 'Texto largo de ejemplo...',
            'date': '2025-01-06',
            'datetime': '2025-01-06 10:30:00',
            'timestamp': '2025-01-06 10:30:00',
            'time': '10:30:00',
            'boolean': 'true',
            'bit': '1',
            'decimal': '123.45',
            'numeric': '123.45',
            'float': '123.45',
            'real': '123.45',
            'money': '1234.56',
            'json': '{"key": "value"}',
            'jsonb': '{"key": "value"}',
            'uuid': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
        }
        
        return examples.get(base_type, 'Valor de ejemplo')
    
    def _export_dictionary(
        self,
        entries: List[Dict[str, Any]],
        output_path: str,
        output_format: str
    ) -> None:
        """Exporta el diccionario al formato deseado.
        
        Args:
            entries (List[Dict[str, Any]]): Entradas del diccionario.
            output_path (str): Ruta del archivo de salida.
            output_format (str): Formato de salida.
        """
        logger.info(f"[INFO] Exportando a formato {output_format}...")
        
        # Crear directorio si no existe
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Exportar usando OutputWriter
        writer = OutputWriter(output_path, output_format)
        writer.write(entries)
        
        logger.info(f"[INFO] Diccionario exportado: {output_path}")
