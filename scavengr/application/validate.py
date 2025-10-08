"""Caso de uso para validación de archivos DBML.

Este módulo implementa la lógica de aplicación para validar la sintaxis
y estructura de archivos DBML.

Examples:
    >>> from scavengr.application.validate import ValidateDBML
    >>> use_case = ValidateDBML()
    >>> result = use_case.execute("schema.dbml")
    >>> print(result.is_valid)
    True

Author: Json Rivera
Date: 2025-01-06
Version: 1.0.0
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass, field

from scavengr.core.entities import DatabaseSchema

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Representa un problema encontrado durante la validación.
    
    Attributes:
        severity (str): Nivel de severidad ('error', 'warning', 'info').
        line (Optional[int]): Número de línea donde ocurre el problema.
        message (str): Descripción del problema.
        context (Optional[str]): Contexto adicional del problema.
    """
    
    severity: str
    message: str
    line: Optional[int] = None
    context: Optional[str] = None


@dataclass
class ValidationResult:
    """Resultado de la validación de un archivo DBML.
    
    Attributes:
        is_valid (bool): Indica si el archivo es válido.
        file_path (str): Ruta del archivo validado.
        schema (Optional[DatabaseSchema]): Esquema parseado si es válido.
        issues (List[ValidationIssue]): Lista de problemas encontrados.
        tables_count (int): Número de tablas encontradas.
        relationships_count (int): Número de relaciones encontradas.
    """
    
    is_valid: bool
    file_path: str
    schema: Optional[DatabaseSchema] = None
    issues: List[ValidationIssue] = field(default_factory=list)
    tables_count: int = 0
    relationships_count: int = 0
    
    def has_errors(self) -> bool:
        """Verifica si hay errores en la validación.
        
        Returns:
            bool: True si hay errores, False en caso contrario.
        """
        return any(issue.severity == 'error' for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Verifica si hay advertencias en la validación.
        
        Returns:
            bool: True si hay advertencias, False en caso contrario.
        """
        return any(issue.severity == 'warning' for issue in self.issues)
    
    def get_errors(self) -> List[ValidationIssue]:
        """Obtiene solo los errores.
        
        Returns:
            List[ValidationIssue]: Lista de errores.
        """
        return [issue for issue in self.issues if issue.severity == 'error']
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Obtiene solo las advertencias.
        
        Returns:
            List[ValidationIssue]: Lista de advertencias.
        """
        return [issue for issue in self.issues if issue.severity == 'warning']


class ValidateDBML:
    """Caso de uso para validar archivos DBML.
    
    Realiza validación de:
    1. Existencia del archivo
    2. Sintaxis DBML correcta
    3. Estructura de tablas y columnas
    4. Referencias entre tablas
    5. Integridad de relaciones
    
    Examples:
        >>> use_case = ValidateDBML()
        >>> result = use_case.execute("schema.dbml")
        >>> if result.is_valid:
        ...     print(f"Válido: {result.tables_count} tablas")
        ... else:
        ...     for error in result.get_errors():
        ...         print(f"Error: {error.message}")
    """
    
    def __init__(self):
        """Inicializa el caso de uso de validación."""
        # Note: DBMLParser actual requiere file_path en constructor
        # No inicializamos el parser aquí
        pass
    
    def execute(self, file_path: str) -> ValidationResult:
        """Ejecuta la validación de un archivo DBML.
        
        Args:
            file_path (str): Ruta del archivo DBML a validar.
            
        Returns:
            ValidationResult: Resultado de la validación.
        """
        logger.info(f"[VALIDATE] Validando archivo: {file_path}")
        
        issues = []
        schema = None
        
        # Validación 1: Existencia del archivo
        if not os.path.exists(file_path):
            issue = ValidationIssue(
                severity='error',
                message=f"Archivo no encontrado: {file_path}"
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")
            
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                issues=issues
            )
        
        # Validación 2: Lectura del archivo (verificar que se puede leer)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                _ = f.read()  # Solo verificar que se puede leer
        except Exception as e:
            issue = ValidationIssue(
                severity='error',
                message=f"Error al leer archivo: {str(e)}"
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")
            
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                issues=issues
            )
        
        # Validación 3: Parsing DBML
        try:
            from scavengr.infrastructure.parsers import DBMLParser
            parser = DBMLParser(file_path)
            schema_dict = parser.parse()
            
            # Convertir a DatabaseSchema si es necesario
            if isinstance(schema_dict, dict) and 'tables' in schema_dict:
                # El parser devuelve un dict, convertir a DatabaseSchema
                schema = DatabaseSchema(
                    name=schema_dict.get('name', 'unknown'),
                    tables=schema_dict.get('tables', []),
                    relationships=schema_dict.get('relationships', []),
                    indexes=schema_dict.get('indexes', []),
                    metadata=schema_dict.get('metadata', {})
                )
            else:
                schema = schema_dict  # Asumir que ya es DatabaseSchema
            
            logger.info("[INFO] Archivo parseado exitosamente")
        except SyntaxError as e:
            issue = ValidationIssue(
                severity='error',
                message=f"Error de sintaxis DBML: {str(e)}",
                context=str(e)
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")
            
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                issues=issues
            )
        except Exception as e:
            issue = ValidationIssue(
                severity='error',
                message=f"Error al parsear DBML: {str(e)}",
                context=str(e)
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")
            
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                issues=issues
            )
        
        # Validación 4: Estructura del esquema
        validation_issues = self._validate_schema_structure(schema)
        issues.extend(validation_issues)
        
        # Validación 5: Integridad de relaciones
        relationship_issues = self._validate_relationships(schema)
        issues.extend(relationship_issues)
        
        # Determinar si es válido (no hay errores)
        is_valid = not any(issue.severity == 'error' for issue in issues)
        
        # Estadísticas
        tables_count = len(schema.tables) if schema else 0
        relationships_count = len(schema.relationships) if schema else 0
        
        # Log resultado
        if is_valid:
            logger.info(
                f"[SUCCESS] Validación exitosa: "
                f"{tables_count} tablas, "
                f"{relationships_count} relaciones"
            )
            if issues:
                logger.warning(f"[WARNING] {len(issues)} advertencias encontradas")
        else:
            error_count = sum(1 for i in issues if i.severity == 'error')
            logger.error(f"[ERROR] Validación fallida: {error_count} errores")
        
        return ValidationResult(
            is_valid=is_valid,
            file_path=file_path,
            schema=schema,
            issues=issues,
            tables_count=tables_count,
            relationships_count=relationships_count
        )
    
    def _validate_schema_structure(
        self,
        schema: DatabaseSchema
    ) -> List[ValidationIssue]:
        """Valida la estructura del esquema.
        
        Args:
            schema (DatabaseSchema): Esquema a validar.
            
        Returns:
            List[ValidationIssue]: Lista de problemas encontrados.
        """
        issues = []
        
        # Validar que hay tablas
        if not schema.tables:
            issues.append(ValidationIssue(
                severity='warning',
                message="No se encontraron tablas en el esquema"
            ))
        
        # Validar cada tabla
        for table in schema.tables:
            # Validar que la tabla tiene nombre
            if not table.name:
                issues.append(ValidationIssue(
                    severity='error',
                    message="Tabla sin nombre encontrada"
                ))
                continue
            
            # Validar que la tabla tiene columnas
            if not table.columns:
                issues.append(ValidationIssue(
                    severity='warning',
                    message=f"Tabla '{table.name}' no tiene columnas"
                ))
                continue
            
            # Validar cada columna
            for column in table.columns:
                # Validar nombre de columna
                if not column.name:
                    issues.append(ValidationIssue(
                        severity='error',
                        message=f"Columna sin nombre en tabla '{table.name}'"
                    ))
                
                # Validar tipo de columna
                if not column.type:
                    issues.append(ValidationIssue(
                        severity='error',
                        message=f"Columna '{column.name}' sin tipo en tabla '{table.name}'"
                    ))
            
            # Validar que hay al menos una primary key
            has_pk = any(col.is_pk for col in table.columns)
            if not has_pk:
                issues.append(ValidationIssue(
                    severity='warning',
                    message=f"Tabla '{table.name}' no tiene primary key definida"
                ))
        
        return issues
    
    def _validate_relationships(
        self,
        schema: DatabaseSchema
    ) -> List[ValidationIssue]:
        """Valida la integridad de las relaciones.
        
        Args:
            schema (DatabaseSchema): Esquema a validar.
            
        Returns:
            List[ValidationIssue]: Lista de problemas encontrados.
        """
        issues = []
        
        # Crear diccionario de tablas para búsqueda rápida
        # Incluir tanto el nombre completo (schema.tabla) como solo el nombre de tabla
        tables_dict = {}
        for table in schema.tables:
            # Agregar con nombre completo
            tables_dict[table.name] = table
            # Si tiene schema, agregar también sin schema para compatibilidad
            if '.' in table.name:
                table_name_only = table.name.split('.')[-1]
                # Solo agregar si no hay colisión
                if table_name_only not in tables_dict:
                    tables_dict[table_name_only] = table
        
        # Validar cada relación
        for relationship in schema.relationships:
            # Validar tabla origen
            if relationship.from_table not in tables_dict:
                issues.append(ValidationIssue(
                    severity='error',
                    message=(
                        f"Relación referencia tabla origen inexistente: "
                        f"'{relationship.from_table}'"
                    )
                ))
                continue
            
            # Validar tabla destino
            if relationship.to_table not in tables_dict:
                issues.append(ValidationIssue(
                    severity='error',
                    message=(
                        f"Relación referencia tabla destino inexistente: "
                        f"'{relationship.to_table}'"
                    )
                ))
                continue
            
            # Validar columna origen
            from_table = tables_dict[relationship.from_table]
            from_column_exists = any(
                col.name == relationship.from_column
                for col in from_table.columns
            )
            if not from_column_exists:
                issues.append(ValidationIssue(
                    severity='error',
                    message=(
                        f"Relación referencia columna origen inexistente: "
                        f"'{relationship.from_table}.{relationship.from_column}'"
                    )
                ))
            
            # Validar columna destino
            to_table = tables_dict[relationship.to_table]
            to_column_exists = any(
                col.name == relationship.to_column
                for col in to_table.columns
            )
            if not to_column_exists:
                issues.append(ValidationIssue(
                    severity='error',
                    message=(
                        f"Relación referencia columna destino inexistente: "
                        f"'{relationship.to_table}.{relationship.to_column}'"
                    )
                ))
        
        return issues
