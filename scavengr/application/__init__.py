"""scavengr.application
=======================

Capa de aplicación - Casos de uso y lógica de orquestación.

Esta capa contiene los casos de uso que orquestan los componentes del dominio
y la infraestructura para implementar las funcionalidades de la aplicación.

Casos de Uso Disponibles:
    - ExtractMetadata: Extracción de metadatos desde bases de datos
    - ValidateDBML: Validación de archivos DBML
    - GenerateDictionary: Generación de diccionarios de datos

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

from scavengr.application.extract import ExtractMetadata, ExtractionResult
from scavengr.application.validate import ValidateDBML, ValidationResult, ValidationIssue
from scavengr.application.dictionary import GenerateDictionary, DictionaryResult

__all__ = [
    # Use Cases
    "ExtractMetadata",
    "ValidateDBML",
    "GenerateDictionary",
    # Result Objects
    "ExtractionResult",
    "ValidationResult",
    "ValidationIssue",
    "DictionaryResult",
]
