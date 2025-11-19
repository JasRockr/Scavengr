#!/usr/bin/env python3
"""
🗃️ Scavengr CLI - "Descubre lo que tus bases esconden."
===============================================

CLI principal para Scavengr, proporciona comandos intuitivos para:
- Inicializar configuración del entorno
- Extraer metadatos de bases de datos
- Validar archivos DBML
- Generar diccionarios de datos
- Crear informes de análisis

Comandos disponibles (orden lógico de uso):
- scavengr init [--global]                      → configurar entorno inicial
- scavengr extract -o <output>                  → extraer metadatos y generar DBML
- scavengr validate -i <dbml>                   → validar DBML existente
- scavengr dictionary -i <dbml> -o <outputd>    → exportar diccionario
- scavengr report -i <dbml> -o <output>         → generar informe analítico

Author: Jason Rivera
Date: 2025-10-09
Version: 0.0.3
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Importar utilidades centralizadas
from scavengr.utils import (
    Commands,
    Formats,
    ProcessingError,
    ScavengrError,
    provide_user_feedback,
    setup_logging,
    validate_file_exists,
    validate_input_file_format,
    validate_output_format,
    validate_write_permissions,
)

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ===================================================================
# FORMATTER PERSONALIZADO PARA HELP CON EJEMPLOS
# ===================================================================


class ScavengrHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Formatter personalizado que soporta ejemplos en el help."""

    pass


# ===================================================================
# LAZY LOADING DE MÓDULOS PESADOS
# ===================================================================


# Configuración de logging: se inicializa en main() según argumentos
logger: Optional[logging.Logger] = None


# ===================================================================
# CLASE PRINCIPAL DEL CLI
# ===================================================================


class ScavengrCLI:
    """Clase principal del CLI de Scavengr"""

    def __init__(self) -> None:
        self.version: str = "0.0.3"

    def extract_command(self, args: argparse.Namespace) -> bool:
        """Comando para extraer metadatos y generar DBML usando caso de uso."""
        if logger is None:
            return False

        try:
            logger.info("[EXTRACT] Iniciando extracción de metadatos...")

            # Cargar configuración
            from scavengr.config.env_config import EnvConfigManager

            env_manager: EnvConfigManager = EnvConfigManager(
                getattr(args, "env_file", None)
            )

            # Validar configuración
            validation: Dict[str, Any] = env_manager.validate_config()
            if not validation["valid"]:
                logger.error("[ERROR] Configuración inválida:")
                for issue in validation["issues"]:
                    logger.error(f"  - {issue}")
                return False

            if validation["warnings"]:
                for warning in validation["warnings"]:
                    logger.warning(f"[WARNING] {warning}")

            db_config: Dict[str, Any] = env_manager.get_db_config()
            generation_config: Dict[str, Any] = env_manager.get_generation_config()

            logger.info(f"[INFO] Sistema: {generation_config['source_system']['name']}")
            logger.info(
                f"[INFO] BD configurada: {db_config['type']} en {db_config['host']}"
            )

            # Determinar archivo de salida
            output_file: str = (
                args.output or f"{generation_config['file_prefix']}_extracted.dbml"
            )

            # Validar flags de cache
            use_cache: bool = getattr(args, "cache", False)
            force_refresh: bool = getattr(args, "force_refresh", False)

            if force_refresh and not use_cache:
                logger.warning(
                    "[WARNING] --force-refresh requiere --cache, habilitando cache automáticamente"
                )
                use_cache = True

            # Log de configuración de cache
            if use_cache:
                if force_refresh:
                    logger.info("[CACHE] Cache habilitado con forzado de refresco")
                else:
                    logger.info("[CACHE] Cache habilitado (TTL: 24h)")
            else:
                logger.debug("[CACHE] Cache deshabilitado")

            # Feedback al usuario
            provide_user_feedback(
                f"Conectando a {db_config['type']} en {db_config['host']}", "info"
            )

            # Ejecutar caso de uso
            from scavengr.application import ExtractionResult, ExtractMetadata

            use_case: ExtractMetadata = ExtractMetadata(
                db_config,
                generation_config,
                use_cache=use_cache,
                force_refresh=force_refresh,
            )
            result: ExtractionResult = use_case.execute(output_file)

            # Procesar resultado
            if result.success:
                provide_user_feedback(
                    f"Esquema extraído exitosamente: {result.tables_count} tablas procesadas",
                    "success",
                )
                logger.info(
                    f"[SUCCESS] Extracción completada: {result.output_path} "
                    f"({result.file_size:,} bytes)"
                )
                logger.info(
                    f"[STATS] {result.tables_count} tablas, "
                    f"{result.columns_count} columnas, "
                    f"{result.relationships_count} relaciones"
                )
                return True
            else:
                logger.error(f"[ERROR] Error en extracción: {result.error_message}")
                provide_user_feedback(f"Error: {result.error_message}", "error")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error en extracción: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False

    def _categorize_warnings(self, warnings: list) -> str:
        """
        Categoriza los warnings y genera un resumen.

        Args:
            warnings: Lista de ValidationIssue warnings

        Returns:
            str: Mensaje de resumen categorizado
        """
        categories = {
            "sin_pk": 0,
            "mysql_btree": 0,
            "mysql_primary": 0,
            "pg_camelcase": 0,
            "pg_tipos_espacios": 0,
            "mssql_autoreference": 0,
            "sin_tablas": 0,
            "sin_columnas": 0,
        }

        for warning in warnings:
            msg = warning.message.lower()
            if "no tiene primary key" in msg:
                categories["sin_pk"] += 1
            elif "btree sin columnas" in msg:
                categories["mysql_btree"] += 1
            elif "primary sin columnas" in msg:
                categories["mysql_primary"] += 1
            elif "camelcase" in msg:
                categories["pg_camelcase"] += 1
            elif "tipo con espacios" in msg:
                categories["pg_tipos_espacios"] += 1
            elif "autoreference" in msg or "auto-referencia" in msg:
                categories["mssql_autoreference"] += 1
            elif "no se encontraron tablas" in msg:
                categories["sin_tablas"] += 1
            elif "no tiene columnas" in msg:
                categories["sin_columnas"] += 1

        # Construir resumen
        parts = []
        if categories["sin_pk"] > 0:
            parts.append(f"{categories['sin_pk']} tablas sin PK")
        if categories["mysql_btree"] > 0:
            parts.append(f"{categories['mysql_btree']} indices BTREE sin columnas")
        if categories["mysql_primary"] > 0:
            parts.append(f"{categories['mysql_primary']} indices PRIMARY sin columnas")
        if categories["pg_camelcase"] > 0:
            parts.append(f"{categories['pg_camelcase']} identificadores CamelCase")
        if categories["pg_tipos_espacios"] > 0:
            parts.append(f"{categories['pg_tipos_espacios']} tipos con espacios")
        if categories["mssql_autoreference"] > 0:
            parts.append(f"{categories['mssql_autoreference']} auto-referencias")
        if categories["sin_tablas"] > 0:
            parts.append("esquema vacío")
        if categories["sin_columnas"] > 0:
            parts.append(f"{categories['sin_columnas']} tablas sin columnas")

        if not parts:
            return f"{len(warnings)} advertencias encontradas"

        return f"{len(warnings)} advertencias encontradas ({', '.join(parts)})"

    def validate_command(self, args: argparse.Namespace) -> bool:
        """Comando para validar archivos DBML usando caso de uso."""
        if logger is None:
            return False

        try:
            logger.info(f"[VALIDATE] Validando archivo DBML: {args.input}")

            # Validar que el archivo existe
            input_path: Path = validate_file_exists(args.input, "Archivo DBML")
            provide_user_feedback(f"Validando: {input_path}", "info")

            # Ejecutar caso de uso
            from scavengr.application import ValidateDBML, ValidationResult

            use_case: ValidateDBML = ValidateDBML()
            result: ValidationResult = use_case.execute(str(input_path))

            # Procesar resultado
            if result.is_valid:
                logger.info("[SUCCESS] Archivo DBML válido")
                logger.info(
                    f"[STATS] {result.tables_count} tablas, "
                    f"{result.relationships_count} relaciones"
                )
                provide_user_feedback(
                    f"Validación exitosa: {result.tables_count} tablas encontradas",
                    "success",
                )

                # Mostrar advertencias si las hay
                if result.has_warnings():
                    logger.warning(
                        f"[WARNING] {len(result.get_warnings())} advertencias encontradas:"
                    )
                    for warning in result.get_warnings():
                        logger.warning(f"  - {warning.message}")

                    # Generar resumen de categorías de warnings
                    warning_summary = self._categorize_warnings(result.get_warnings())
                    if warning_summary:
                        provide_user_feedback(warning_summary, "warning")

                return True
            else:
                logger.error("[ERROR] Archivo DBML inválido")
                logger.error(f"[ERROR] {len(result.get_errors())} errores encontrados:")

                # Mostrar errores
                for error in result.get_errors():
                    error_msg = error.message
                    if error.line:
                        error_msg = f"Línea {error.line}: {error_msg}"
                    logger.error(f"  - {error_msg}")
                    provide_user_feedback(error_msg, "error")

                return False

        except Exception as e:
            logger.error(f"[ERROR] Error al validar DBML: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False

    def dictionary_command(self, args: argparse.Namespace) -> bool:
        """Comando para generar diccionarios de datos usando caso de uso."""
        if logger is None:
            return False

        try:
            logger.info(f"[DICTIONARY] Generando diccionario desde: {args.input}")

            # Validar archivo de entrada
            input_path: Path = validate_input_file_format(args.input)
            provide_user_feedback(
                f"Archivo de entrada validado: {input_path}", "success"
            )

            # Validar permisos de escritura
            try:
                output_path: Path = validate_write_permissions(args.output)
                provide_user_feedback(
                    f"Permisos de escritura verificados: {output_path.parent}", "info"
                )
            except Exception as e:
                provide_user_feedback(
                    f"No se puede escribir en: {args.output}. Detalle: {str(e)}",
                    "error",
                )
                logger.error(f"[ERROR] Permisos de escritura: {str(e)}")
                return False

            # Determinar formato de salida
            output_format: str = validate_output_format(args.output, args.format)
            logger.info(f"[INFO] Formato de salida: {output_format.upper()}")

            # Cargar configuración para contexto
            from scavengr.config.env_config import EnvConfigManager

            env_manager: EnvConfigManager = EnvConfigManager(
                getattr(args, "env_file", None)
            )
            generation_config: Dict[str, Any] = env_manager.get_generation_config()

            # Ejecutar caso de uso
            from scavengr.application import DictionaryResult, GenerateDictionary

            use_case: GenerateDictionary = GenerateDictionary(config=generation_config)
            result: DictionaryResult = use_case.execute(
                input_path=str(input_path),
                output_path=args.output,
                output_format=output_format,
            )

            # Procesar resultado
            if result.success:
                logger.info(f"[SUCCESS] Diccionario generado: {result.output_path}")
                logger.info(
                    f"[STATS] {result.entries_count} entradas, "
                    f"formato {result.format.upper()}, "
                    f"{result.file_size:,} bytes"
                )
                provide_user_feedback(
                    f"Diccionario generado exitosamente: {result.entries_count} entradas",
                    "success",
                )
                return True
            else:
                logger.error(
                    f"[ERROR] Error generando diccionario: {result.error_message}"
                )
                provide_user_feedback(f"Error: {result.error_message}", "error")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error al generar diccionario: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False

    def report_command(self, args: argparse.Namespace) -> bool:
        """Comando para generar informes avanzados usando caso de uso."""
        if logger is None:
            return False

        try:
            logger.info(f"[REPORT] Generando informe desde: {args.input}")

            # Validar que el archivo existe
            input_path: Path = validate_file_exists(args.input, "Archivo DBML")
            provide_user_feedback(f"Generando informe desde: {input_path}", "info")

            # Ejecutar caso de uso
            from scavengr.application import GenerateReport, ReportResult

            use_case: GenerateReport = GenerateReport(version=self.version)
            result: ReportResult = use_case.execute(str(input_path), args.output)

            # Procesar resultado
            if result.success:
                logger.info(f"[SUCCESS] Informe generado: {result.output_path}")
                logger.info(
                    f"[STATS] {result.tables_analyzed} tablas, "
                    f"{result.columns_analyzed} columnas analizadas"
                )
                logger.info(f"[STATS] Score de calidad: {result.quality_score}%")
                provide_user_feedback(
                    f"Informe generado exitosamente: formato {result.format.upper()}",
                    "success",
                )
                return True
            else:
                logger.error(f"[ERROR] Error generando informe: {result.error_message}")
                provide_user_feedback(f"Error: {result.error_message}", "error")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error al generar informe: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False

    def init_command(self, args: argparse.Namespace) -> bool:
        """Comando para inicializar configuración de Scavengr."""
        if logger is None:
            return False

        try:
            logger.info("[INIT] Inicializando configuración de Scavengr...")

            # Determinar ruta del archivo .env
            if args.global_config:
                env_path: str = os.path.expanduser("~/.scavengr.env")
                config_type: str = "global"
            else:
                env_path = os.path.join(os.getcwd(), ".env")
                config_type = "local"

            # Verificar si ya existe
            if os.path.exists(env_path):
                response: str = input(
                    f"⚠️  Ya existe configuración {config_type} en {env_path}. ¿Sobrescribir? (y/N): "
                )
                if response.lower() not in ["y", "yes", "sí", "s"]:
                    logger.info("[CANCELLED] Inicialización cancelada por el usuario")
                    return True

            # Contenido del archivo .env de ejemplo
            env_content: str = """
# ====================================================================
# 🗃️ SCAVENGR - CONFIGURACIÓN DE VARIABLES DE ENTORNO
# ====================================================================

# CONFIGURACIÓN DE BASE DE DATOS (REQUERIDA)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mi_base_datos
DB_USER=usuario_bd
DB_PASSWORD=contraseña_segura

# CONFIGURACIÓN DEL SISTEMA (OPCIONAL)
SOURCE_SYSTEM_NAME=Mi Sistema
SOURCE_SYSTEM_VERSION=1.0
SOURCE_ENVIRONMENT=production
OUTPUT_FILE_PREFIX=diccionario_datos

# ====================================================================
# INSTRUCCIONES:
# 1. Edite las variables DB_* con sus credenciales reales
# 2. Mantenga este archivo seguro (no lo comparta)
# 3. Para más información: https://github.com/JasRockr/Scavengr#configuración
# ====================================================================
"""

            # Crear directorio si no existe
            os.makedirs(os.path.dirname(env_path), exist_ok=True)

            # Escribir archivo
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(env_content)

            logger.info(f"[SUCCESS] Configuración {config_type} creada: {env_path}")
            provide_user_feedback(
                f"Configuración {config_type} creada exitosamente", "success"
            )

            print()
            print("📝 Próximos pasos:")
            if config_type == "global":
                print(f"   1. Edite el archivo: {env_path}")
            else:
                print("   1. Edite el archivo .env en este directorio")
            print("   2. Configure sus credenciales de base de datos")
            print("   3. Ejecute: scavengr extract -o mi-esquema.dbml")

            return True

        except Exception as e:
            logger.error(f"[ERROR] Error al inicializar configuración: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Configura y retorna el parser de argumentos CLI.

    Returns:
        ArgumentParser configurado con todos los comandos y opciones.
    """
    cli: ScavengrCLI = ScavengrCLI()

    # Parser principal con ejemplos
    examples: str = """
EJEMPLOS DE USO:

  Flujo completo (orden recomendado):
    scavengr init                                  # Configuración inicial (una sola vez)
    scavengr extract -o mi-esquema.dbml            # Extraer metadatos de la BD
    scavengr validate -i mi-esquema.dbml           # Validar estructura DBML
    scavengr dictionary -i mi-esquema.dbml -o dict.xlsx  # Generar diccionario
    scavengr report -i mi-esquema.dbml -o report.json    # Análisis detallado

  Comandos individuales:
    scavengr init --global                         # Config global en home directory
    scavengr validate -i esquema.dbml              # Solo validar (sin cambios)
    scavengr dictionary -i esquema.dbml -o dict.csv     # Exportar a CSV
    scavengr report -i esquema.dbml -o report.json      # Solo reporte

  Uso con caché (mejora rendimiento ~90%):
    scavengr extract --cache -o schema.dbml        # Primera extracción (crea caché)
    scavengr extract --cache -o schema.dbml        # Subsecuentes (~90% más rápido)
    scavengr extract --cache --force-refresh -o schema.dbml  # Invalidar y reextraer

  Modo detallado (debugging):
    scavengr --verbose extract -o schema.dbml      # Ver detalles de la extracción
    scavengr --verbose validate -i schema.dbml     # Ver detalles de validación

PARA MÁS INFORMACIÓN:
  scavengr <comando> --help    # Ayuda específica de cada comando
  GitHub: https://github.com/JasRockr/Scavengr
  Email: jsonrivera@proton.me
"""

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="scavengr",
        description="🗃️ Scavengr - Descubre lo que tus bases esconden",
        epilog=examples,
        formatter_class=ScavengrHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Scavengr {cli.version}",
        help="Muestra la versión actual de Scavengr y sale.",
    )

    # Agregar argumento verbose
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Habilita el modo detallado (DEBUG) para el logging.",
    )

    # Subcommands
    subparsers: Any = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando extract
    extract_parser: argparse.ArgumentParser = subparsers.add_parser(
        Commands.EXTRACT,
        help="Extraer metadatos de base de datos y generar DBML",
        description="Extrae metadatos completos de la BD configurada en .env",
        epilog="""
EJEMPLOS:
  scavengr extract -o mi-bd.dbml                  # Salida en archivo especificado
  scavengr extract                                # Usa nombre por defecto (prefijo_extracted.dbml)
  scavengr --verbose extract -o schema.dbml       # Con información de debugging
  scavengr extract --env-file .env.production     # Usar archivo .env alternativo

  Uso con caché (recomendado para esquemas grandes):
  scavengr extract --cache -o schema.dbml         # Habilitar caché (primera vez)
  scavengr extract --cache -o schema.dbml         # Usar caché (~90% más rápido)
  scavengr extract --cache --force-refresh -o schema.dbml  # Invalidar caché

SISTEMA DE CACHÉ:
  📦 MetadataCache - Reducción ~90% en tiempo de extracciones subsecuentes

  Características:
    • Serialización: Pickle (rápido) o JSON (portable)
    • TTL: 24 horas por defecto (configurable)
    • Ubicación: .scavengr_cache/ (auto-creado, ignorado por git)
    • Clave: Hash de configuración BD (type + host + name)
    • Gestión automática de expiración

  Flags:
    --cache              Habilita caché de metadatos
    --force-refresh      Invalida caché existente (requiere --cache)

  Primer uso:
    1. scavengr extract --cache -o schema.dbml  → Extrae y guarda en caché
    2. scavengr extract --cache -o schema.dbml  → Lee desde caché (rápido)
    3. Si BD cambia: --force-refresh para actualizar

SALIDA:
  - Archivo DBML con tablas, columnas, relaciones e índices
  - Log detallado con conteo de metadatos extraídos
  - Mensaje de caché: [CACHE HIT] o [CACHE MISS] (si --cache activo)
        """,
        formatter_class=ScavengrHelpFormatter,
    )
    extract_parser.add_argument(
        "-o",
        "--output",
        help="Archivo DBML de salida (por defecto: <prefijo>_extracted.dbml)",
    )
    extract_parser.add_argument(
        "--env-file", help="Archivo .env específico a usar (por defecto: .env)"
    )
    extract_parser.add_argument(
        "--cache",
        action="store_true",
        help="Habilita caché de metadatos con MetadataCache (serialización pickle/JSON, TTL 24h, reducción ~90%% tiempo)",
    )
    extract_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Invalida caché existente y reextrae desde BD (requiere --cache, útil cuando el esquema ha cambiado)",
    )

    # Comando validate
    validate_parser: argparse.ArgumentParser = subparsers.add_parser(
        Commands.VALIDATE,
        help="Validar archivo DBML existente",
        description="Valida sintaxis, estructura e integridad de un archivo DBML",
        epilog="""
EJEMPLOS:
  scavengr validate -i mi-esquema.dbml            # Validación completa
  scavengr --verbose validate -i esquema.dbml     # Con detalles de cada validación

VALIDACIONES REALIZADAS:
  ✓ Existencia y permisos del archivo
  ✓ Sintaxis DBML correcta
  ✓ Estructura de tablas y columnas
  ✓ Integridad de relaciones
  ✓ Calidad de datos (CamelCase, tipos, índices, etc.)

SALIDA:
  - Reporte de validación con errores y advertencias
  - Estadísticas: tablas, columnas, relaciones
        """,
        formatter_class=ScavengrHelpFormatter,
    )
    validate_parser.add_argument(
        "-i", "--input", required=True, help="Ruta al archivo DBML a validar"
    )

    # Comando dictionary
    dict_parser: argparse.ArgumentParser = subparsers.add_parser(
        Commands.DICTIONARY,
        help="Generar diccionario de datos desde DBML",
        description="Genera diccionario de datos profesional con 19 campos especializados",
        epilog="""
EJEMPLOS:
  scavengr dictionary -i esquema.dbml -o diccionario.xlsx   # Excel (por defecto)
  scavengr dictionary -i esquema.dbml -o diccionario.csv    # CSV
  scavengr dictionary -i esquema.dbml -o diccionario.json   # JSON

CAMPOS GENERADOS (19):
  Tabla, Columna, Tipo, Tamaño, PK, FK, Nullable, Default
  Sensibilidad, Descripción, Máscara, Ejemplo, Criterios
  Observaciones, Módulo, Referencias, Índices, Patrones, Recomendaciones

FORMATOS SOPORTADOS:
  .xlsx - Excel con formato y colores (recomendado)
  .csv  - CSV separado por comas (compatible con Excel/Sheets)
  .json - JSON estructurado (para integración)
        """,
        formatter_class=ScavengrHelpFormatter,
    )
    dict_parser.add_argument(
        "-i", "--input", required=True, help="Ruta al archivo DBML de entrada"
    )
    dict_parser.add_argument(
        "-o", "--output", required=True, help="Ruta del archivo de salida"
    )
    dict_parser.add_argument(
        "-f",
        "--format",
        choices=Formats.SUPPORTED,
        help="Formato de salida (se detecta automáticamente por extensión)",
    )

    # Comando report
    report_parser: argparse.ArgumentParser = subparsers.add_parser(
        Commands.REPORT,
        help="Generar informe con análisis desde archivo DBML",
        description="Genera análisis detallado con score de calidad en 7 dimensiones",
        epilog="""
EJEMPLOS:
  scavengr report -i esquema.dbml -o reporte.xlsx      # Reporte Excel
  scavengr report -i esquema.dbml -o reporte.json      # Reporte JSON
  scavengr report -i esquema.dbml -o reporte.csv       # Reporte CSV
  scavengr --verbose report -i esquema.dbml -o reporte.xlsx  # Con detalles

ANÁLISIS INCLUIDO:
  📊 Score de Calidad (7 dimensiones):
    - Nomenclatura de tablas y columnas
    - Normalización de datos
    - Integridad referencial
    - Tipos de datos
    - Índices
    - Documentación
    - Seguridad

  📈 Estadísticas:
    - Distribución de tipos de datos
    - Análisis de tamaños
    - Métricas de relaciones

  💡 Recomendaciones priorizadas por impacto

SALIDA:
  - Múltiples hojas (Excel) o secciones (JSON)
  - Resumen ejecutivo
  - Análisis detallado por tabla
        """,
        formatter_class=ScavengrHelpFormatter,
    )
    report_parser.add_argument(
        "-i", "--input", required=True, help="Ruta al archivo DBML de entrada"
    )
    report_parser.add_argument(
        "-o", "--output", required=True, help="Ruta del archivo de informe de salida"
    )

    # Comando init (nuevo)
    init_parser: argparse.ArgumentParser = subparsers.add_parser(
        "init",
        help="Inicializar configuración de Scavengr (crear .env)",
        description="Crea archivo .env con plantilla de configuración",
        epilog="""
EJEMPLOS:
  scavengr init                     # Crear .env en directorio actual
  scavengr init --global            # Crear ~/.scavengr.env global

CONFIGURACIÓN:
  El archivo .env contiene:
    - Tipo y credenciales de BD (PostgreSQL, MySQL, SQL Server)
    - Parámetros de generación (prefijos, nombres de sistema)
    - Rutas de salida

NOTAS:
  - Se crea solo si no existe
  - Los valores por defecto son ejemplos (ACTUALIZAR con tus datos)
  - Archivo global (~/.scavengr.env) tiene prioridad menor
  - Archivo local (.env) sobrescribe la configuración

SEGURIDAD:
  ⚠️  El archivo .env contiene credenciales - NUNCA lo debes incluir en commits con Git
  ✓ Se proporciona plantilla con valores seguros por defecto
  ✓ Se recomienda chmod 600 ~/.scavengr.env (Habilita solo lectura/escritura al usuario)
        """,
        formatter_class=ScavengrHelpFormatter,
    )
    init_parser.add_argument(
        "--global",
        action="store_true",
        dest="global_config",
        help="Crear configuración global en directorio home",
    )

    return parser


def execute_command(command: str, args: argparse.Namespace) -> bool:
    """
    Dispatcher de comandos - ejecuta el comando correspondiente.

    Args:
        command: Nombre del comando a ejecutar
        args: Argumentos parseados

    Returns:
        bool: True si el comando se ejecutó exitosamente

    Raises:
        ProcessingError: Si hay error en el procesamiento
    """
    cli: ScavengrCLI = ScavengrCLI()

    command_map: Dict[str, Any] = {
        Commands.EXTRACT: cli.extract_command,
        Commands.VALIDATE: cli.validate_command,
        Commands.DICTIONARY: cli.dictionary_command,
        Commands.REPORT: cli.report_command,
        "init": cli.init_command,
    }

    command_func: Optional[Callable[[argparse.Namespace], bool]] = command_map.get(
        command
    )
    if not command_func:
        raise ProcessingError("comando", f"Comando desconocido: {command}")

    result: bool = command_func(args)
    return result


def main() -> int:
    """Función principal del CLI - simplificada y modular."""
    parser: argparse.ArgumentParser = setup_argument_parser()
    args: argparse.Namespace = parser.parse_args()

    # Configurar logging según el argumento verbose
    global logger
    if args.verbose:
        logger = setup_logging(verbose=True)
        logger.info("Modo detallado (DEBUG) activado")
        logger.debug(f"Argumentos parseados: {vars(args)}")
    else:
        logger = setup_logging(verbose=False)

    if not args.command:
        parser.print_help()
        return 1

    # Ejecutar comando usando el dispatcher
    try:
        success: bool = execute_command(args.command, args)
        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("[CANCELLED] Operacion cancelada por el usuario")
        return 1
    except ScavengrError as e:
        logger.error(f"[ERROR] {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"[ERROR] Error inesperado: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
