# Instalación

## Requisitos Previos

- **Python**: 3.8 o superior (recomendado: 3.10+)
- **pip**: Gestor de paquetes de Python

---

## Instalación desde PyPI (Recomendado)

La forma más sencilla es instalar directamente desde PyPI:

```bash
# Instalación básica
pip install scavengr

# Verificar instalación
scavengr --version

# Configuración inicial
scavengr init
```

---

## Instalación desde Fuente

### Para Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/JasRockr/Scavengr.git
cd Scavengr

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Pre-commit hooks
pre-commit install
```

---

## Dependencias por Motor de BD

### PostgreSQL

```bash
pip install psycopg2-binary
```

### MySQL/MariaDB

```bash
pip install mysql-connector-python
```

### SQL Server

```bash
pip install pyodbc
```

!!! note "Windows ODBC Driver"
    En Windows necesitas instalar **ODBC Driver 17 for SQL Server**.
    
    [Descargar aquí](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## Verificación

```bash
# Ver versión
scavengr --version

# Ver ayuda
scavengr --help

# Listar comandos disponibles
scavengr
```
