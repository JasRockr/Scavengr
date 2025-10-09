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

import sys
import argparse
import os
from pathlib import Path
import json

# Importar utilidades centralizadas
from scavengr.utils import (
    setup_logging,
    Commands,
    Formats,
    ScavengrError,
    ProcessingError,
    validate_file_exists,
    validate_output_format,
    validate_write_permissions,
    validate_input_file_format,
    provide_user_feedback,
)

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ===================================================================
# LAZY LOADING DE MÓDULOS PESADOS
# ===================================================================



# Configuración de logging: se inicializa en main() según argumentos
logger = None


# ===================================================================
# CLASE PRINCIPAL DEL CLI
# ===================================================================

class ScavengrCLI:
    """Clase principal del CLI de Scavengr"""
    
    def __init__(self):
        self.version = "0.0.1"
    
    def extract_command(self, args):
        """Comando para extraer metadatos y generar DBML usando caso de uso."""
        try:
            logger.info("[EXTRACT] Iniciando extracción de metadatos...")
            
            # Cargar configuración
            from scavengr.config.env_config import EnvConfigManager
            env_manager = EnvConfigManager(getattr(args, 'env_file', None))
            
            # Validar configuración
            validation = env_manager.validate_config()
            if not validation['valid']:
                logger.error("[ERROR] Configuración inválida:")
                for issue in validation['issues']:
                    logger.error(f"  - {issue}")
                return False

            if validation['warnings']:
                for warning in validation['warnings']:
                    logger.warning(f"[WARNING] {warning}")
            
            db_config = env_manager.get_db_config()
            generation_config = env_manager.get_generation_config()
            
            logger.info(f"[INFO] Sistema: {generation_config['source_system']['name']}")
            logger.info(f"[INFO] BD configurada: {db_config['type']} en {db_config['host']}")

            # Determinar archivo de salida
            output_file = args.output or f"{generation_config['file_prefix']}_extracted.dbml"

            # Feedback al usuario
            provide_user_feedback(
                f"Conectando a {db_config['type']} en {db_config['host']}",
                "info"
            )
            
            # Ejecutar caso de uso
            from scavengr.application import ExtractMetadata
            use_case = ExtractMetadata(db_config, generation_config)
            result = use_case.execute(output_file)
            
            # Procesar resultado
            if result.success:
                provide_user_feedback(
                    f"Esquema extraído exitosamente: {result.tables_count} tablas procesadas",
                    "success"
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
                provide_user_feedback(
                    f"Error: {result.error_message}",
                    "error"
                )
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error en extracción: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False
    
    def validate_command(self, args):
        """Comando para validar archivos DBML usando caso de uso."""
        try:
            logger.info(f"[VALIDATE] Validando archivo DBML: {args.input}")
            
            # Validar que el archivo existe
            input_path = validate_file_exists(args.input, "Archivo DBML")
            provide_user_feedback(f"Validando: {input_path}", "info")
            
            # Ejecutar caso de uso
            from scavengr.application import ValidateDBML
            use_case = ValidateDBML()
            result = use_case.execute(str(input_path))
            
            # Procesar resultado
            if result.is_valid:
                logger.info("[SUCCESS] Archivo DBML válido")
                logger.info(
                    f"[STATS] {result.tables_count} tablas, "
                    f"{result.relationships_count} relaciones"
                )
                provide_user_feedback(
                    f"Validación exitosa: {result.tables_count} tablas encontradas",
                    "success"
                )
                
                # Mostrar advertencias si las hay
                if result.has_warnings():
                    logger.warning(f"[WARNING] {len(result.get_warnings())} advertencias encontradas:")
                    for warning in result.get_warnings():
                        logger.warning(f"  - {warning.message}")
                
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
    
    def dictionary_command(self, args):
        """Comando para generar diccionarios de datos usando caso de uso."""
        try:
            logger.info(f"[DICTIONARY] Generando diccionario desde: {args.input}")
            
            # Validar archivo de entrada
            input_path = validate_input_file_format(args.input)
            provide_user_feedback(f"Archivo de entrada validado: {input_path}", "success")
            
            # Validar permisos de escritura
            try:
                output_path = validate_write_permissions(args.output)
                provide_user_feedback(
                    f"Permisos de escritura verificados: {output_path.parent}",
                    "info"
                )
            except Exception as e:
                provide_user_feedback(
                    f"No se puede escribir en: {args.output}. Detalle: {str(e)}",
                    "error"
                )
                logger.error(f"[ERROR] Permisos de escritura: {str(e)}")
                return False
            
            # Determinar formato de salida
            output_format = validate_output_format(args.output, args.format)
            logger.info(f"[INFO] Formato de salida: {output_format.upper()}")
            
            # Cargar configuración para contexto
            from scavengr.config.env_config import EnvConfigManager
            env_manager = EnvConfigManager(getattr(args, 'env_file', None))
            generation_config = env_manager.get_generation_config()
            
            # Ejecutar caso de uso
            from scavengr.application import GenerateDictionary
            use_case = GenerateDictionary(config=generation_config)
            result = use_case.execute(
                input_path=str(input_path),
                output_path=args.output,
                output_format=output_format
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
                    "success"
                )
                return True
            else:
                logger.error(f"[ERROR] Error generando diccionario: {result.error_message}")
                provide_user_feedback(
                    f"Error: {result.error_message}",
                    "error"
                )
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Error al generar diccionario: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False
    
    def report_command(self, args):
        """Comando para generar informes avanzados usando caso de uso."""
        try:
            logger.info(f"[REPORT] Generando informe desde: {args.input}")
            
            # Validar que el archivo existe
            input_path = validate_file_exists(args.input, "Archivo DBML")
            provide_user_feedback(f"Generando informe desde: {input_path}", "info")
            
            # Ejecutar caso de uso
            from scavengr.application import GenerateReport
            use_case = GenerateReport(version=self.version)
            result = use_case.execute(str(input_path), args.output)
            
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
                    "success"
                )
                return True
            else:
                logger.error(f"[ERROR] Error generando informe: {result.error_message}")
                provide_user_feedback(
                    f"Error: {result.error_message}",
                    "error"
                )
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error al generar informe: {str(e)}")
            provide_user_feedback(f"Error inesperado: {str(e)}", "error")
            return False
    

    
    def init_command(self, args):
        """Comando para inicializar configuración de Scavengr."""
        try:
            logger.info("[INIT] Inicializando configuración de Scavengr...")
            
            # Determinar ruta del archivo .env
            if args.global_config:
                env_path = os.path.expanduser("~/.scavengr.env")
                config_type = "global"
            else:
                env_path = os.path.join(os.getcwd(), ".env")
                config_type = "local"
            
            # Verificar si ya existe
            if os.path.exists(env_path):
                response = input(f"⚠️  Ya existe configuración {config_type} en {env_path}. ¿Sobrescribir? (y/N): ")
                if response.lower() not in ['y', 'yes', 'sí', 's']:
                    logger.info("[CANCELLED] Inicialización cancelada por el usuario")
                    return True
            
            # Contenido del archivo .env de ejemplo
            env_content = '''
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
'''
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(env_path), exist_ok=True)
            
            # Escribir archivo
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info(f"[SUCCESS] Configuración {config_type} creada: {env_path}")
            provide_user_feedback(
                f"Configuración {config_type} creada exitosamente",
                "success"
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
    cli = ScavengrCLI()

    # Parser principal
    parser = argparse.ArgumentParser(
        prog='scavengr',
        description='🗃️ Scavengr - Descubre lo que tus bases esconden',
        epilog='Para más información, visite: https://github.com/JasRockr/Scavengr'
    )

    parser.add_argument(
        '-v', '--version',
        action='version', 
        version=f'Scavengr {cli.version}',
        help='Muestra la versión actual de Scavengr y sale.'
    )

    # Agregar argumento verbose
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Habilita el modo detallado (DEBUG) para el logging.'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # Comando extract
    extract_parser = subparsers.add_parser(
        Commands.EXTRACT, 
        help='Extraer metadatos de base de datos y generar DBML'
    )
    extract_parser.add_argument(
        '-o', '--output',
        help="Archivo DBML de salida (por defecto: <prefijo>_extracted.dbml)"
    )
    extract_parser.add_argument(
        '--env-file',
        help='Archivo .env específico a usar (por defecto: .env)'
    )

    # Comando validate
    validate_parser = subparsers.add_parser(
        Commands.VALIDATE,
        help='Validar archivo DBML existente'
    )
    validate_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Ruta al archivo DBML a validar'
    )

    # Comando dictionary
    dict_parser = subparsers.add_parser(
        Commands.DICTIONARY,
        help='Generar diccionario de datos desde DBML'
    )
    dict_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Ruta al archivo DBML de entrada'
    )
    dict_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Ruta del archivo de salida'
    )
    dict_parser.add_argument(
        '-f', '--format',
        choices=Formats.SUPPORTED,
        help='Formato de salida (se detecta automáticamente por extensión)'
    )
    
    # Comando report
    report_parser = subparsers.add_parser(
        Commands.REPORT,
        help='Generar informe con análisis desde archivo DBML'
    )
    report_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Ruta al archivo DBML de entrada'
    )
    report_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Ruta del archivo de informe de salida (JSON)'
    )
    
    # Comando init (nuevo)
    init_parser = subparsers.add_parser(
        'init',
        help='Inicializar configuración de Scavengr (crear .env)'
    )
    init_parser.add_argument(
        '--global',
        action='store_true',
        dest='global_config',
        help='Crear configuración global en directorio home'
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
    cli = ScavengrCLI()
    
    command_map = {
        Commands.EXTRACT: cli.extract_command,
        Commands.VALIDATE: cli.validate_command,
        Commands.DICTIONARY: cli.dictionary_command,
        Commands.REPORT: cli.report_command,
        'init': cli.init_command
    }
    
    command_func = command_map.get(command)
    if not command_func:
        raise ProcessingError("comando", f"Comando desconocido: {command}")
    
    return command_func(args)


def main():
    """Función principal del CLI - simplificada y modular."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
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
        success = execute_command(args.command, args)
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


if __name__ == '__main__':
        sys.exit(main())