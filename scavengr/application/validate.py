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
Date: 2025-09-26
Version: 0.0.1
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from scavengr.core.entities import DatabaseSchema, Table

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
        return any(issue.severity == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Verifica si hay advertencias en la validación.

        Returns:
            bool: True si hay advertencias, False en caso contrario.
        """
        return any(issue.severity == "warning" for issue in self.issues)

    def get_errors(self) -> List[ValidationIssue]:
        """Obtiene solo los errores.

        Returns:
            List[ValidationIssue]: Lista de errores.
        """
        return [issue for issue in self.issues if issue.severity == "error"]

    def get_warnings(self) -> List[ValidationIssue]:
        """Obtiene solo las advertencias.

        Returns:
            List[ValidationIssue]: Lista de advertencias.
        """
        return [issue for issue in self.issues if issue.severity == "warning"]


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

    def __init__(self) -> None:
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

        issues: List[ValidationIssue] = []
        schema: Optional[DatabaseSchema] = None

        # Validación 1: Existencia del archivo
        if not os.path.exists(file_path):
            issue = ValidationIssue(
                severity="error", message=f"Archivo no encontrado: {file_path}"
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")

            return ValidationResult(is_valid=False, file_path=file_path, issues=issues)

        # Validación 2: Lectura del archivo (verificar que se puede leer)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _ = f.read()  # Solo verificar que se puede leer
        except Exception as e:
            issue = ValidationIssue(
                severity="error", message=f"Error al leer archivo: {str(e)}"
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")

            return ValidationResult(is_valid=False, file_path=file_path, issues=issues)

        # Validación 3: Parsing DBML
        try:
            from scavengr.infrastructure.parsers import DBMLParser

            parser = DBMLParser(file_path)
            schema_dict: Union[Dict[str, Any], DatabaseSchema] = parser.parse()

            # Convertir a DatabaseSchema si es necesario
            if isinstance(schema_dict, dict) and "tables" in schema_dict:
                # El parser devuelve un dict, convertir a DatabaseSchema
                schema = DatabaseSchema(
                    name=schema_dict.get("name", "unknown"),
                    tables=schema_dict.get("tables", []),
                    relationships=schema_dict.get("relationships", []),
                    indexes=schema_dict.get("indexes", []),
                    metadata=schema_dict.get("metadata", {}),
                )
            elif isinstance(schema_dict, DatabaseSchema):
                schema = schema_dict
            else:
                # Asumir que es un dict que no tiene la estructura esperada
                schema = DatabaseSchema(
                    name="unknown", tables=[], relationships=[], indexes=[], metadata={}
                )

            logger.info("[INFO] Archivo parseado exitosamente")
        except SyntaxError as e:
            issue = ValidationIssue(
                severity="error",
                message=f"Error de sintaxis DBML: {str(e)}",
                context=str(e),
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")

            return ValidationResult(is_valid=False, file_path=file_path, issues=issues)
        except Exception as e:
            issue = ValidationIssue(
                severity="error",
                message=f"Error al parsear DBML: {str(e)}",
                context=str(e),
            )
            issues.append(issue)
            logger.error(f"[ERROR] {issue.message}")

            return ValidationResult(is_valid=False, file_path=file_path, issues=issues)

        # Validación 4: Estructura del esquema
        if schema is None:
            raise RuntimeError("Schema no fue parseado correctamente")

        validation_issues = self._validate_schema_structure(schema)
        issues.extend(validation_issues)

        # Validación 5: Integridad de relaciones
        relationship_issues = self._validate_relationships(schema)
        issues.extend(relationship_issues)

        # Validación 6: Validaciones de calidad (problemas de generación)
        quality_issues = self._validate_quality_issues(schema)
        issues.extend(quality_issues)

        # Determinar si es válido (no hay errores)
        is_valid = not any(issue.severity == "error" for issue in issues)

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
            error_count = sum(1 for i in issues if i.severity == "error")
            logger.error(f"[ERROR] Validación fallida: {error_count} errores")

        return ValidationResult(
            is_valid=is_valid,
            file_path=file_path,
            schema=schema,
            issues=issues,
            tables_count=tables_count,
            relationships_count=relationships_count,
        )

    def _validate_schema_structure(
        self, schema: DatabaseSchema
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
            issues.append(
                ValidationIssue(
                    severity="warning", message="No se encontraron tablas en el esquema"
                )
            )

        # Validar cada tabla
        for table in schema.tables:
            # Validar que la tabla tiene nombre
            if not table.name:
                issues.append(
                    ValidationIssue(
                        severity="error", message="Tabla sin nombre encontrada"
                    )
                )
                continue

            # Validar que la tabla tiene columnas
            if not table.columns:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Tabla '{table.name}' no tiene columnas",
                    )
                )
                continue

            # Validar cada columna
            for column in table.columns:
                # Validar nombre de columna
                if not column.name:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"Columna sin nombre en tabla '{table.name}'",
                        )
                    )

                # Validar tipo de columna
                if not column.type:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"Columna '{column.name}' sin tipo en tabla '{table.name}'",
                        )
                    )

            # Validar que hay al menos una primary key
            has_pk = any(col.is_pk for col in table.columns)
            if not has_pk:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Tabla '{table.name}' no tiene primary key definida",
                    )
                )

        return issues

    def _validate_relationships(self, schema: DatabaseSchema) -> List[ValidationIssue]:
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
            if "." in table.name:
                table_name_only = table.name.split(".")[-1]
                # Solo agregar si no hay colisión
                if table_name_only not in tables_dict:
                    tables_dict[table_name_only] = table

        # Validar cada relación
        for relationship in schema.relationships:
            # Validar tabla origen
            if relationship.from_table not in tables_dict:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Relación referencia tabla origen inexistente: "
                            f"'{relationship.from_table}'"
                        ),
                    )
                )
                continue

            # Validar tabla destino
            if relationship.to_table not in tables_dict:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Relación referencia tabla destino inexistente: "
                            f"'{relationship.to_table}'"
                        ),
                    )
                )
                continue

            # Validar columna origen
            from_table = tables_dict[relationship.from_table]
            from_column_exists = any(
                col.name == relationship.from_column for col in from_table.columns
            )
            if not from_column_exists:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Relación referencia columna origen inexistente: "
                            f"'{relationship.from_table}.{relationship.from_column}'"
                        ),
                    )
                )

            # Validar columna destino
            to_table = tables_dict[relationship.to_table]
            to_column_exists = any(
                col.name == relationship.to_column for col in to_table.columns
            )
            if not to_column_exists:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Relación referencia columna destino inexistente: "
                            f"'{relationship.to_table}.{relationship.to_column}'"
                        ),
                    )
                )

        return issues

    def _validate_quality_issues(self, schema: DatabaseSchema) -> List[ValidationIssue]:
        """Valida problemas de calidad de generación DBML.

        Detecta problemas que serán "arreglados" automáticamente durante la generación:
        1. MySQL: Índices BTREE sin columnas especificadas
        2. MySQL: Índices PRIMARY sin columnas
        3. MSSQL: Autoreferences al mismo endpoint
        4. PostgreSQL: Identificadores CamelCase sin escapar
        5. PostgreSQL: Tipos con espacios sin normalizar

        Args:
            schema (DatabaseSchema): Esquema a validar.

        Returns:
            List[ValidationIssue]: Lista de problemas de calidad detectados.
        """
        issues = []

        # Agrupar columnas por tabla para análisis más eficiente
        for table in schema.tables:
            # Detectar problemas MySQL con índices
            mysql_issues = self._detect_mysql_index_issues(table)
            issues.extend(mysql_issues)

            # Detectar problemas PostgreSQL
            pgsql_issues = self._detect_postgresql_issues(table)
            issues.extend(pgsql_issues)

            # Detectar autoreferences MSSQL
            mssql_issues = self._detect_mssql_autoreference_issues(table, schema)
            issues.extend(mssql_issues)

        return issues

    def _detect_mysql_index_issues(self, table: Table) -> List[ValidationIssue]:
        """Detecta problemas de índices en MySQL.

        Args:
            table (Table): Tabla a analizar.

        Returns:
            List[ValidationIssue]: Lista de problemas de índices.
        """
        issues: List[ValidationIssue] = []

        # Verificar si es tabla MySQL (por convención de nombre o metadata)
        if not self._is_mysql_table(table):
            return issues

        # Verificar índices sin columnas
        if hasattr(table, "indexes"):
            for index in table.indexes:
                index_type = (getattr(index, "index_type", None) or "").upper()
                columns = getattr(index, "columns", [])

                # BTREE sin columnas
                if index_type in ["BTREE", "B-TREE"] and not columns:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=(
                                f"[MySQL] Indice BTREE sin columnas en tabla '{table.name}' "
                                "sera inferida automaticamente durante generacion"
                            ),
                            context=f"Indice: {getattr(index, 'name', 'sin nombre')}",
                        )
                    )

                # PRIMARY sin columnas
                if index_type == "PRIMARY" and not columns:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=(
                                f"[MySQL] Indice PRIMARY sin columnas en tabla '{table.name}' "
                                "agregara todas las columnas PK automaticamente"
                            ),
                            context=f"Tabla: {table.name}",
                        )
                    )

        return issues

    def _detect_postgresql_issues(self, table: Table) -> List[ValidationIssue]:
        """Detecta problemas de PostgreSQL.

        Args:
            table: Tabla a analizar.

        Returns:
            List[ValidationIssue]: Lista de problemas PostgreSQL.
        """
        issues: List[ValidationIssue] = []

        # Verificar si es tabla PostgreSQL
        if not self._is_postgresql_table(table):
            return issues

        for column in table.columns:
            col_name = column.name
            col_type = column.type or ""

            # Detectar CamelCase sin escapar
            if self._has_camelcase(col_name):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=(
                            f"[PostgreSQL] Identificador CamelCase detectado '{col_name}' "
                            f"en tabla '{table.name}' sera escapado automaticamente "
                            'con comillas dobles ("ValidoDesde")'
                        ),
                        context=f"Columna: {col_name}",
                    )
                )

            # Detectar tipos con espacios
            if " " in col_type:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=(
                            f"[PostgreSQL] Tipo con espacios detectado '{col_type}' "
                            f"en columna '{col_name}' de tabla '{table.name}' "
                            "sera normalizado automaticamente (ej: 'timestamp without time zone' -> 'timestamp')"
                        ),
                        context=f"Columna: {col_name} | Tipo: {col_type}",
                    )
                )

        return issues

    def _detect_mssql_autoreference_issues(
        self, table: Table, schema: DatabaseSchema
    ) -> List[ValidationIssue]:
        """Detecta autoreferences al mismo endpoint en MSSQL.

        Args:
            table: Tabla a analizar.
            schema (DatabaseSchema): Schema completo para análisis de relaciones.

        Returns:
            List[ValidationIssue]: Lista de problemas de autoreferences.
        """
        issues: List[ValidationIssue] = []

        # Verificar si es tabla MSSQL
        if not self._is_mssql_table(table):
            return issues

        # Buscar relaciones que apunten a la misma tabla
        if hasattr(schema, "relationships"):
            table_name = table.name

            for rel in schema.relationships:
                from_table = getattr(rel, "from_table", "")
                to_table = getattr(rel, "to_table", "")

                # Si ambos son la misma tabla (autoreference)
                if from_table == table_name and to_table == table_name:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            message=(
                                f"[MSSQL] Autoreference detectada en tabla '{table_name}' "
                                "será filtrada automáticamente para evitar ciclos de integridad referencial"
                            ),
                            context=(
                                f"De: {from_table}.{getattr(rel, 'from_column', '?')} "
                                f"→ A: {to_table}.{getattr(rel, 'to_column', '?')}"
                            ),
                        )
                    )

        return issues

    def _is_mysql_table(self, table: Table) -> bool:
        """Verifica si la tabla proviene de MySQL.

        Args:
            table: Tabla a verificar.

        Returns:
            bool: True si es tabla MySQL.
        """
        # Heurística: Verificar metadatos o nombre de tabla
        metadata = getattr(table, "metadata", {})
        engine = (
            metadata.get("engine", "").lower() if isinstance(metadata, dict) else ""
        )

        if "mysql" in engine or "innodb" in engine or "myisam" in engine:
            return True

        # Por defecto, si tiene índices BTREE o PRIMARY, probablemente es MySQL
        if hasattr(table, "indexes"):
            for index in table.indexes:
                index_type = (getattr(index, "index_type", None) or "").upper()
                if index_type in ["BTREE", "HASH", "FULLTEXT", "SPATIAL", "PRIMARY"]:
                    return True

        return False

    def _is_postgresql_table(self, table: Table) -> bool:
        """Verifica si la tabla proviene de PostgreSQL.

        Args:
            table: Tabla a verificar.

        Returns:
            bool: True si es tabla PostgreSQL.
        """
        # Heurística: Verificar metadatos
        metadata = getattr(table, "metadata", {})
        engine = (
            metadata.get("engine", "").lower() if isinstance(metadata, dict) else ""
        )

        if "postgres" in engine or "postgresql" in engine or "pg" in engine:
            return True

        # Por convención: Si tiene tipos específicos de PostgreSQL
        for column in table.columns:
            col_type = (column.type or "").lower()
            pgsql_types = [
                "serial",
                "bigserial",
                "smallserial",
                "bytea",
                "timestamp without time zone",
                "timestamp with time zone",
                "character varying",
                "smallint",
                "uuid",
                "json",
                "jsonb",
            ]
            if any(pgsql_type in col_type for pgsql_type in pgsql_types):
                return True

        return False

    def _is_mssql_table(self, table: Table) -> bool:
        """Verifica si la tabla proviene de MSSQL.

        Args:
            table: Tabla a verificar.

        Returns:
            bool: True si es tabla MSSQL.
        """
        # Heurística: Verificar metadatos
        metadata = getattr(table, "metadata", {})
        engine = (
            metadata.get("engine", "").lower() if isinstance(metadata, dict) else ""
        )

        if "mssql" in engine or "sqlserver" in engine or "sql server" in engine:
            return True

        # Por convención: Si tiene tipos específicos de MSSQL
        for column in table.columns:
            col_type = (column.type or "").lower()
            mssql_types = [
                "datetime2",
                "datetimeoffset",
                "smalldatetime",
                "nvarchar",
                "nchar",
                "ntext",
                "varbinary",
                "uniqueidentifier",
                "hierarchyid",
            ]
            if any(mssql_type in col_type for mssql_type in mssql_types):
                return True

        return False

    def _has_camelcase(self, identifier: str) -> bool:
        """Verifica si un identificador contiene CamelCase.

        Args:
            identifier (str): Identificador a verificar.

        Returns:
            bool: True si contiene CamelCase.
        """
        # CamelCase: Tiene mayúsculas internas (no al inicio de palabra)
        # Ejemplo: ValidoDesde, FechaModificacion, userID

        # Ignorar si es todo mayúsculas (CONSTANTE) o todo minúsculas
        if identifier.isupper() or identifier.islower():
            return False

        # Ignorar si es snake_case puro
        if "_" in identifier:
            # Verificar cada parte del snake_case
            parts = identifier.split("_")
            has_camelcase_part = False
            for part in parts:
                if (
                    part
                    and not part[0].isupper()
                    and any(c.isupper() for c in part[1:])
                ):
                    has_camelcase_part = True
                    break
            return has_camelcase_part

        # Si no tiene guión bajo y tiene mayúsculas internas, es CamelCase
        return any(c.isupper() for c in identifier[1:])
