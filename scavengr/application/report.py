"""Caso de uso para generación de informes analíticos.

Este módulo implementa la lógica de aplicación para generar informes
analíticos avanzados desde archivos DBML, usando los servicios de dominio
para análisis estadístico y calidad de datos.

Examples:
    >>> from scavengr.application.report import GenerateReport
    >>> use_case = GenerateReport()
    >>> result = use_case.execute("schema.dbml", "report.xlsx")
    >>> print(result.success)
    True

Author: Json Rivera
Date: 2025-10-09
Version: 0.0.3
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from scavengr.infrastructure.parsers import DBMLParser
from scavengr.core.entities import DatabaseSchema
from scavengr.core.services import StatisticsAnalyzerService

logger = logging.getLogger(__name__)


@dataclass
class ReportResult:
    """Resultado de la generación de informe analítico.
    
    Attributes:
        success (bool): Indica si la generación fue exitosa.
        output_path (str): Ruta del archivo generado.
        format (str): Formato del archivo generado (xlsx, json).
        tables_analyzed (int): Número de tablas analizadas.
        columns_analyzed (int): Número de columnas analizadas.
        quality_score (float): Score de calidad general (0-100).
        file_size (int): Tamaño del archivo generado en bytes.
        error_message (Optional[str]): Mensaje de error si la generación falló.
    """
    
    success: bool
    output_path: str = ""
    format: str = ""
    tables_analyzed: int = 0
    columns_analyzed: int = 0
    quality_score: float = 0.0
    file_size: int = 0
    error_message: Optional[str] = None


class GenerateReport:
    """Caso de uso para generación de informes analíticos avanzados.
    
    Este caso de uso orquesta la generación de informes analíticos detallados
    que incluyen estadísticas, análisis de calidad y recomendaciones de mejora.
    
    Args:
        version (str): Versión de Scavengr para incluir en metadatos.
    
    Examples:
        >>> use_case = GenerateReport("0.0.1")
        >>> result = use_case.execute("schema.dbml", "report.xlsx")
        >>> if result.success:
        ...     print(f"Informe generado: {result.output_path}")
        ...     print(f"Score de calidad: {result.quality_score}%")
    """
    
    def __init__(self, version: str = "0.0.1"):
        """Inicializar el caso de uso de generación de informes.
        
        Args:
            version: Versión de Scavengr para incluir en metadatos.
        """
        self.version = version
        self.stats_service = StatisticsAnalyzerService()
    
    def execute(self, input_path: str, output_path: str) -> ReportResult:
        """Ejecutar la generación de informe analítico.
        
        Args:
            input_path: Ruta del archivo DBML de entrada.
            output_path: Ruta del archivo de salida (xlsx o json).
        
        Returns:
            ReportResult: Resultado de la operación con estadísticas.
        
        Raises:
            FileNotFoundError: Si el archivo DBML no existe.
            ValueError: Si el formato de salida no es soportado.
        """
        try:
            logger.info(f"[REPORT] Iniciando generación de informe desde: {input_path}")
            
            # Validar archivo de entrada
            if not os.path.exists(input_path):
                error_msg = f"Archivo DBML no encontrado: {input_path}"
                logger.error(f"[ERROR] {error_msg}")
                return ReportResult(
                    success=False,
                    error_message=error_msg
                )
            
            # Parsear archivo DBML
            schema = self._parse_dbml_file(input_path)
            if not schema:
                error_msg = "No se pudo parsear el archivo DBML"
                logger.error(f"[ERROR] {error_msg}")
                return ReportResult(
                    success=False,
                    error_message=error_msg
                )
            
            # Generar análisis estadístico avanzado
            logger.info("[REPORT] Analizando esquema con estadísticas avanzadas...")
            advanced_stats = self.stats_service.analyze_schema(schema)
            
            # Generar metadatos del informe
            metadata = self._generate_metadata(input_path, output_path)
            
            # Crear directorio de salida si no existe
            self._ensure_output_directory(output_path)
            
            # Determinar formato y generar archivo
            output_format = self._detect_output_format(output_path)
            success = self._write_report_file(
                output_path, 
                output_format, 
                metadata, 
                advanced_stats
            )
            
            if not success:
                error_msg = "Error al escribir el archivo de informe"
                return ReportResult(
                    success=False,
                    error_message=error_msg
                )
            
            # Calcular estadísticas del resultado
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            resumen = advanced_stats.get('resumen_general', {})
            calidad = advanced_stats.get('calidad_datos', {})
            
            logger.info(f"[SUCCESS] Informe generado: {output_path}")
            logger.info(f"[STATS] Tablas analizadas: {resumen.get('total_tablas', 0)}")
            logger.info(f"[STATS] Columnas analizadas: {resumen.get('total_columnas', 0)}")
            logger.info(f"[STATS] Score de calidad: {calidad.get('score_general', 0)}%")
            
            return ReportResult(
                success=True,
                output_path=output_path,
                format=output_format,
                tables_analyzed=resumen.get('total_tablas', 0),
                columns_analyzed=resumen.get('total_columnas', 0),
                quality_score=calidad.get('score_general', 0.0),
                file_size=file_size
            )
            
        except Exception as e:
            error_msg = f"Error inesperado al generar informe: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            logger.exception("Detalles del error:")
            return ReportResult(
                success=False,
                error_message=error_msg
            )
    
    def _parse_dbml_file(self, input_path: str) -> Optional[DatabaseSchema]:
        """Parsear archivo DBML y retornar el esquema.
        
        Args:
            input_path: Ruta del archivo DBML.
        
        Returns:
            DatabaseSchema o None si hay error.
        """
        try:
            parser = DBMLParser(input_path)
            return parser.parse()
        except Exception as e:
            logger.error(f"[ERROR] Error parseando DBML: {str(e)}")
            return None
    
    def _generate_metadata(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Generar metadatos del informe.
        
        Args:
            input_path: Ruta del archivo de entrada.
            output_path: Ruta del archivo de salida.
        
        Returns:
            Dict con metadatos del informe.
        """
        return {
            "version_scavengr": self.version,
            "fecha_generacion": datetime.now().isoformat(timespec='seconds'),
            "generado_en": str(Path().cwd()),
            "archivo_origen": os.path.abspath(input_path),
            "archivo_salida": os.path.abspath(output_path),
            "usuario": os.getenv("USERNAME") or os.getenv("USER") or "desconocido",
        }
    
    def _ensure_output_directory(self, output_path: str) -> None:
        """Asegurar que el directorio de salida existe.
        
        Args:
            output_path: Ruta del archivo de salida.
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"[INFO] Directorio creado: {output_dir}")
    
    def _detect_output_format(self, output_path: str) -> str:
        """Detectar formato de salida basado en la extensión.
        
        Args:
            output_path: Ruta del archivo de salida.
        
        Returns:
            Formato detectado ('xlsx' o 'json').
        """
        output_ext = Path(output_path).suffix.lower()
        return 'xlsx' if output_ext == '.xlsx' else 'json'
    
    def _write_report_file(
        self, 
        output_path: str, 
        format: str, 
        metadata: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> bool:
        """Escribir archivo de informe en el formato especificado.
        
        Args:
            output_path: Ruta del archivo de salida.
            format: Formato de salida ('xlsx' o 'json').
            metadata: Metadatos del informe.
            stats: Estadísticas analizadas.
        
        Returns:
            True si se escribió exitosamente, False en caso contrario.
        """
        try:
            if format == 'xlsx':
                return self._write_excel_report(output_path, metadata, stats)
            else:
                return self._write_json_report(output_path, metadata, stats)
        except Exception as e:
            logger.error(f"[ERROR] Error escribiendo archivo {format}: {str(e)}")
            return False
    
    def _write_json_report(
        self, 
        output_path: str, 
        metadata: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> bool:
        """Escribir informe en formato JSON.
        
        Args:
            output_path: Ruta del archivo de salida.
            metadata: Metadatos del informe.
            stats: Estadísticas analizadas.
        
        Returns:
            True si se escribió exitosamente.
        """
        import json
        
        report = {
            "metadatos": metadata,
            "analisis": stats
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[INFO] Informe JSON generado: {output_path}")
        return True
    
    def _write_excel_report(
        self, 
        output_path: str, 
        metadata: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> bool:
        """Escribir informe avanzado en formato Excel con múltiples hojas.
        
        Args:
            output_path: Ruta del archivo de salida.
            metadata: Metadatos del informe.
            stats: Estadísticas analizadas.
        
        Returns:
            True si se escribió exitosamente.
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.chart import BarChart, PieChart, Reference

            wb = Workbook()
            
            # Estilos reutilizables
            header_font = Font(bold=True, size=14, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            subheader_font = Font(bold=True, size=12)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # === HOJA 1: RESUMEN GENERAL ===
            ws_resumen = wb.active
            ws_resumen.title = "Resumen General"
            
            ws_resumen['A1'] = "📊 INFORME DE ANÁLISIS DE BASE DE DATOS"
            ws_resumen['A1'].font = Font(bold=True, size=18, color="FFFFFF")
            ws_resumen['A1'].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            ws_resumen.merge_cells('A1:C1')
            
            # Metadatos
            row = 3
            ws_resumen[f'A{row}'] = "Fecha de Generación:"
            ws_resumen[f'B{row}'] = metadata['fecha_generacion']
            row += 1
            ws_resumen[f'A{row}'] = "Versión Scavengr:"
            ws_resumen[f'B{row}'] = metadata['version_scavengr']
            row += 1
            ws_resumen[f'A{row}'] = "Usuario:"
            ws_resumen[f'B{row}'] = metadata['usuario']
            
            # Resumen General
            row += 2
            resumen = stats['resumen_general']
            ws_resumen[f'A{row}'] = "MÉTRICAS GENERALES"
            ws_resumen[f'A{row}'].font = subheader_font
            row += 1
            
            metricas_generales = [
                ("📋 Total de Tablas", resumen['total_tablas']),
                ("📊 Total de Columnas", resumen['total_columnas']),
                ("🔗 Total de Relaciones", resumen['total_relaciones']),
                ("📈 Promedio Columnas/Tabla", resumen['promedio_columnas_por_tabla']),
                ("🏢 Tablas Maestras", resumen['tablas_maestras']),
                ("💼 Tablas Transaccionales", resumen['tablas_transaccionales']),
            ]
            
            for label, valor in metricas_generales:
                ws_resumen[f'A{row}'] = label
                ws_resumen[f'B{row}'] = valor
                ws_resumen[f'A{row}'].font = Font(bold=True)
                row += 1
            
            # Score de Calidad
            row += 1
            calidad = stats['calidad_datos']
            ws_resumen[f'A{row}'] = "SCORE DE CALIDAD"
            ws_resumen[f'A{row}'].font = subheader_font
            row += 1
            
            ws_resumen[f'A{row}'] = "⭐ Score General"
            ws_resumen[f'B{row}'] = f"{calidad['score_general']}%"
            ws_resumen[f'B{row}'].font = Font(bold=True, size=14, color="FF0000" if calidad['score_general'] < 50 else "00B050")
            
            ws_resumen.column_dimensions['A'].width = 30
            ws_resumen.column_dimensions['B'].width = 20
            
            # === HOJA 2: CALIDAD DE DATOS ===
            ws_calidad = wb.create_sheet("Calidad de Datos")
            self._write_quality_sheet(ws_calidad, header_font, header_fill, stats['calidad_datos'])
            
            # === HOJA 3: DISTRIBUCIÓN DE TIPOS ===
            ws_tipos = wb.create_sheet("Tipos de Datos")
            self._write_types_sheet(ws_tipos, header_font, header_fill, stats['distribucion_tipos'])
            
            # === HOJA 4: SEGURIDAD ===
            ws_seguridad = wb.create_sheet("Seguridad")
            self._write_security_sheet(ws_seguridad, header_font, header_fill, stats['seguridad_sensibilidad'])
            
            # === HOJA 5: RECOMENDACIONES ===
            ws_recs = wb.create_sheet("Recomendaciones")
            self._write_recommendations_sheet(ws_recs, header_font, header_fill, stats['recomendaciones'])
            
            wb.save(output_path)
            logger.info(f"[INFO] Informe Excel generado: {output_path}")
            return True
            
        except ImportError:
            logger.warning("[WARNING] openpyxl no disponible, generando JSON como fallback")
            return self._write_json_report(output_path, metadata, stats)
        except Exception as e:
            logger.error(f"[ERROR] Error generando Excel: {str(e)}")
            return False
    
    def _write_quality_sheet(self, ws, header_font, header_fill, calidad_datos):
        """Escribir hoja de análisis de calidad de datos."""
        from openpyxl.styles import Font
        
        ws['A1'] = "ANÁLISIS DE CALIDAD DE DATOS"
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws.merge_cells('A1:C1')
        
        row = 3
        dimensiones = [
            ("Completitud", calidad_datos['completitud']),
            ("Integridad Referencial", calidad_datos['integridad_referencial']),
            ("Consistencia Nombres", calidad_datos['consistencia_nombres']),
            ("Documentación", calidad_datos['documentacion']),
        ]
        
        for dimension, datos in dimensiones:
            ws[f'A{row}'] = dimension
            ws[f'B{row}'] = f"{datos['score']}%"
            ws[f'A{row}'].font = Font(bold=True)
            row += 1
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
    
    def _write_types_sheet(self, ws, header_font, header_fill, distribucion_tipos):
        """Escribir hoja de distribución de tipos de datos."""
        from openpyxl.styles import Font, PatternFill
        
        ws['A1'] = "DISTRIBUCIÓN DE TIPOS DE DATOS"
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws.merge_cells('A1:C1')
        
        row = 3
        ws[f'A{row}'] = "Tipo de Dato"
        ws[f'B{row}'] = "Cantidad"
        ws[f'C{row}'] = "Porcentaje"
        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = Font(bold=True)
            ws[f'{col}{row}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        row += 1
        
        total_count = sum(item['cantidad'] for item in distribucion_tipos.get('top_10_tipos', []))
        for item in distribucion_tipos.get('top_10_tipos', []):
            ws[f'A{row}'] = item['tipo']
            ws[f'B{row}'] = item['cantidad']
            percentage = (item['cantidad'] / total_count * 100) if total_count > 0 else 0
            ws[f'C{row}'] = f"{percentage:.1f}%"
            row += 1
        
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 15
    
    def _write_security_sheet(self, ws, header_font, header_fill, seguridad_datos):
        """Escribir hoja de análisis de seguridad y sensibilidad."""
        from openpyxl.styles import Font
        
        ws['A1'] = "ANÁLISIS DE SEGURIDAD Y SENSIBILIDAD"
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws.merge_cells('A1:C1')
        
        row = 3
        ws[f'A{row}'] = "Nivel"
        ws[f'B{row}'] = "Cantidad"
        ws[f'C{row}'] = "Porcentaje"
        for col in ['A', 'B', 'C']:
            ws[f'{col}{row}'].font = Font(bold=True)
        row += 1
        
        for nivel, datos in seguridad_datos.get('distribucion_sensibilidad', {}).items():
            ws[f'A{row}'] = nivel
            ws[f'B{row}'] = datos.get('cantidad', 0)
            ws[f'C{row}'] = f"{datos.get('porcentaje', 0)}%"
            row += 1
    
    def _write_recommendations_sheet(self, ws, header_font, header_fill, recomendaciones):
        """Escribir hoja de recomendaciones de mejora."""
        from openpyxl.styles import Font
        
        ws['A1'] = "RECOMENDACIONES DE MEJORA"
        ws['A1'].font = header_font
        ws['A1'].fill = header_fill
        ws.merge_cells('A1:D1')
        
        row = 3
        ws[f'A{row}'] = "Prioridad"
        ws[f'B{row}'] = "Categoría"
        ws[f'C{row}'] = "Recomendación"
        ws[f'D{row}'] = "Tablas Afectadas"
        for col in ['A', 'B', 'C', 'D']:
            ws[f'{col}{row}'].font = Font(bold=True)
        row += 1
        
        for rec in recomendaciones:
            ws[f'A{row}'] = rec.get('prioridad', '')
            ws[f'B{row}'] = rec.get('categoria', '')
            ws[f'C{row}'] = rec.get('recomendacion', '')
            tablas_afectadas = rec.get('tablas_afectadas', [])
            ws[f'D{row}'] = ", ".join(tablas_afectadas[:3]) if tablas_afectadas else "-"
            
            # Color según prioridad
            if rec.get('prioridad') == 'CRÍTICA':
                ws[f'A{row}'].font = Font(color="FF0000", bold=True)
            elif rec.get('prioridad') == 'ALTA':
                ws[f'A{row}'].font = Font(color="FFC000", bold=True)
            
            row += 1
        
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 50
        ws.column_dimensions['D'].width = 30