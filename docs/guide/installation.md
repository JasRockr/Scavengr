# Instalación

Necesitas Python 3.11 o superior.

## Desde PyPI

Scavengr no instala drivers de base de datos por defecto. Elige el extra del motor que vas a usar:

```bash
pip install "scavengr[postgres]"     # PostgreSQL (psycopg2-binary)
pip install "scavengr[mysql]"        # MySQL/MariaDB (mysql-connector-python)
pip install "scavengr[mssql]"        # SQL Server (pyodbc)
pip install "scavengr[all-db]"       # los tres
```

!!! note "Versión publicada"
    La versión de PyPI (0.0.4.post1) todavía declara Python 3.8+. La rama `main` ya exige 3.11, porque la 3.10 dejó de recibir parches de seguridad el 1 de octubre de 2026.

### SQL Server

Además de `pyodbc`, necesitas un [driver ODBC de Microsoft](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server) instalado en el sistema. Hoy Scavengr siempre usa el driver llamado `SQL Server` e ignora `DB_DRIVER` (hallazgo C1, se corrige en la 0.0.5).

## Desde el código

```bash
git clone https://github.com/JasRockr/Scavengr.git
cd Scavengr
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows (PowerShell)
source .venv/bin/activate           # Linux/macOS
pip install -e ".[dev,postgres,mysql,mssql]"
pre-commit install
```

## Comprobar

```bash
scavengr --version
scavengr --help
```
