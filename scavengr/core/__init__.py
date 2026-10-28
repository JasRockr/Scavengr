"""scavengr.core
=================

Capa de dominio - Lógica de negocio central.
Contiene entidades, servicios e interfaces independientes de frameworks.

Módulos:
- entities: Entidades del dominio (Column, Table, Relationship, etc.)
- services: Servicios de dominio con lógica de negocio
- interfaces: Interfaces y contratos (Ports)
"""

from scavengr.core.entities import Column, DatabaseSchema, Index, Relationship, Table
from scavengr.core.interfaces import IExporter, IFormatter, IMetadataScanner, IParser
from scavengr.core.services import (
    DescriptionGeneratorService,
    ExampleGeneratorService,
    MaskGeneratorService,
    ModuleClassifierService,
    ObservationGeneratorService,
    QualityCriteriaService,
    RegexInferenceService,
    RelationshipAnalyzer,
    SensitivityAnalyzerService,
    StatisticsAnalyzerService,
)

__all__ = [
    # Entities
    "Column",
    "Table",
    "Relationship",
    "Index",
    "DatabaseSchema",
    # Interfaces
    "IMetadataScanner",
    "IParser",
    "IFormatter",
    "IExporter",
    # Services
    "RegexInferenceService",
    "MaskGeneratorService",
    "QualityCriteriaService",
    "RelationshipAnalyzer",
    "ExampleGeneratorService",
    "ModuleClassifierService",
    "SensitivityAnalyzerService",
    "ObservationGeneratorService",
    "DescriptionGeneratorService",
    "StatisticsAnalyzerService",
]
