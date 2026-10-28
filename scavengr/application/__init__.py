"""scavengr.application
=======================

Capa de aplicación - Casos de uso y lógica de orquestación.

Esta capa contiene los casos de uso que orquestan los componentes del dominio
y la infraestructura para implementar las funcionalidades de la aplicación.

Casos de Uso Disponibles:
    - InitConfiguration: Inicialización y configuración del entorno
    - ExtractMetadata: Extracción de metadatos desde bases de datos
    - ValidateDBML: Validación de archivos DBML
    - GenerateDictionary: Generación de diccionarios de datos
    - GenerateReport: Generación de informes analíticos avanzados

Principios:
    - Orquestación sin lógica de negocio
    - Independiente de frameworks
    - Inyección de dependencias
    - Testeable y mantenible

Examples:
    >>> from scavengr.application import ExtractMetadata
    >>> use_case = ExtractMetadata(db_config, gen_config)
    >>> result = use_case.execute("output.dbml")
    >>> print(result.success)
    True
"""

from scavengr.application.dictionary import DictionaryResult, GenerateDictionary
from scavengr.application.extract import ExtractionResult, ExtractMetadata
from scavengr.application.report import GenerateReport, ReportResult
from scavengr.application.validate import (
    ValidateDBML,
    ValidationIssue,
    ValidationResult,
)

__all__ = [
    # Use Cases
    "ExtractMetadata",
    "ValidateDBML",
    "GenerateDictionary",
    "GenerateReport",
    # Result Objects
    "ExtractionResult",
    "ValidationResult",
    "ValidationIssue",
    "DictionaryResult",
    "ReportResult",
]
