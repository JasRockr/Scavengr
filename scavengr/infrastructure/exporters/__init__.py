"""scavengr.infrastructure.exporters
======================================

Exportadores de datos.
Implementa IExporter para diferentes formatos (Excel, CSV, JSON, etc.).
"""

from scavengr.infrastructure.exporters.output_writer import OutputWriter

__all__ = [
    "OutputWriter",
]
