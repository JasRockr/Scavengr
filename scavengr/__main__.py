#!/usr/bin/env python3
"""Entry point para el CLI de Scavengr.

Este módulo permite ejecutar Scavengr como un módulo de Python:
    python -m scavengr

Redirige la ejecución al CLI principal ubicado en cli.py.

Examples:
    $ python -m scavengr extract -o output.dbml
    $ python -m scavengr validate -i schema.dbml
    $ python -m scavengr dictionary -i schema.dbml -o dict.xlsx
"""

import sys

# Importar la función main desde el módulo CLI
from scavengr.cli import main

if __name__ == "__main__":
    sys.exit(main())