# Scavengr

[![CI](https://github.com/JasRockr/Scavengr/actions/workflows/ci.yml/badge.svg)](https://github.com/JasRockr/Scavengr/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/scavengr.svg)](https://pypi.org/project/scavengr/)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
[![Licencia](https://img.shields.io/github/license/JasRockr/Scavengr.svg)](LICENSE)

> _"Descubre lo que tus bases esconden."_

Scavengr es una herramienta de línea de comandos que lee los metadatos de una base de datos (PostgreSQL, MySQL/MariaDB o SQL Server) y genera un archivo DBML, un diccionario de datos con la sensibilidad de cada columna y un informe de calidad del esquema.

## Estado del proyecto

Scavengr está en alfa. En octubre de 2026 hice una [auditoría técnica](docs/auditoria-tecnica/README.md) con un laboratorio de bases reales y encontré fallos que dan resultados incorrectos sin avisar. Los estoy corrigiendo en la versión 0.0.5. Hasta entonces, ten en cuenta estas limitaciones:

- **Puerto y driver:** se ignoran `DB_PORT` y `DB_DRIVER`. Siempre se conecta al puerto por defecto del motor y, en SQL Server, con el driver ODBC `SQL Server` (C1).
- **Orden de los archivos `.env`:** un `--env-file` explícito pierde contra `.env.local`, `.env` y `~/.scavengr.env` (A1). Ver [Configuración](#configuración).
- **Llaves foráneas en PostgreSQL:** pueden salir sin esquema, repetidas o con el esquema equivocado, y las compuestas se multiplican (C2).
- **Usuario de solo lectura en PostgreSQL:** no ve ninguna PK ni FK y la extracción igual termina en éxito (C3).
- **Columnas entre comillas:** `dictionary` y `report` pierden las columnas camelCase que el mismo DBML escribe entre comillas (C4).
- **`validate`:** aprueba archivos que el parser oficial de DBML rechaza (A4).
- **Clasificación de sensibilidad:** detecta pocas columnas con datos personales y marca algunas que no lo son (C5).

## Instalación

Necesitas Python 3.11 o superior.

```bash
pip install scavengr                 # sin drivers de base de datos
pip install "scavengr[postgres]"     # PostgreSQL (psycopg2-binary)
pip install "scavengr[mysql]"        # MySQL/MariaDB (mysql-connector-python)
pip install "scavengr[mssql]"        # SQL Server (pyodbc)
pip install "scavengr[all-db]"       # los tres
```

La versión publicada en PyPI (0.0.4.post1) todavía declara Python 3.8+. La rama `main` ya exige 3.11, porque la 3.10 dejó de recibir parches de seguridad el 1 de octubre de 2026.

Para SQL Server también necesitas un [driver ODBC de Microsoft](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server) instalado en el sistema.

## Configuración

Scavengr lee la conexión de variables de entorno o de archivos `.env`. Para crear uno con la plantilla:

```bash
scavengr init            # crea .env en el directorio actual
scavengr init --global   # crea ~/.scavengr.env
```

También puedes copiar [`.env.example`](.env.example).

| Variable | Obligatoria | Para qué sirve |
| --- | --- | --- |
| `DB_TYPE` | Sí | `postgresql`, `mysql` o `mssql` |
| `DB_HOST` | Sí | Servidor |
| `DB_NAME` | Sí | Base de datos |
| `DB_USER` | Sí | Usuario |
| `DB_PASSWORD` | Sí | Contraseña |
| `DB_PORT` | No | Puerto. Hoy se ignora (C1) |
| `DB_DRIVER` | No | Driver ODBC de SQL Server. Hoy se ignora (C1) |
| `SOURCE_SYSTEM_NAME` | No | Nombre del sistema que aparece en el diccionario |
| `SOURCE_SYSTEM_VERSION` | No | Versión del sistema |
| `SOURCE_ENVIRONMENT` | No | Entorno (`production` por defecto) |
| `OUTPUT_FILE_PREFIX` | No | Prefijo del archivo que genera `extract` sin `-o` (`diccionario_datos` por defecto) |

Scavengr carga, si existen y en este orden: el archivo de `--env-file`, `.env.local`, `.env` y `~/.scavengr.env`. Cada uno pisa los valores del anterior y también las variables del sistema, así que **gana el último**: el global. Es el hallazgo A1. En la 0.0.5, `--env-file` va a ser exclusivo y las variables del sistema van a tener prioridad sobre los archivos implícitos.

## Uso

```bash
scavengr extract -o esquema.dbml                     # lee la base y genera el DBML
scavengr validate -i esquema.dbml                    # revisa el DBML
scavengr dictionary -i esquema.dbml -o dicc.xlsx     # diccionario de datos
scavengr report -i esquema.dbml -o informe.xlsx      # informe de calidad
```

`scavengr <comando> --help` muestra las opciones de cada comando, y `scavengr --verbose <comando>` activa el detalle de depuración.

### `extract`

Lee tablas, columnas, tipos, PK, FK e índices, y escribe un archivo DBML que se puede abrir en [dbdiagram.io](https://dbdiagram.io).

| Opción | Qué hace |
| --- | --- |
| `-o`, `--output` | Archivo de salida. Sin esta opción usa `<OUTPUT_FILE_PREFIX>_extracted.dbml` |
| `--env-file` | Archivo `.env` que quieres usar (ver A1 arriba) |
| `--cache` | Guarda los metadatos en `.scavengr_cache/` y los reutiliza durante 24 horas |
| `--force-refresh` | Con `--cache`, descarta lo guardado y vuelve a leer la base |

La caché se guarda con pickle en el directorio actual. Su clave sale del tipo de base, el host y el nombre, pero no del puerto ni del usuario: dos usuarios con permisos distintos sobre la misma base comparten la caché (M3).

### `validate`

Revisa que el archivo exista y se pueda parsear, que haya tablas con columnas y PK, y que las relaciones apunten a tablas y columnas que existen. También avisa de patrones típicos de cada motor: índices de MySQL sin columnas, identificadores camelCase y tipos con espacios en PostgreSQL, y referencias de una columna a sí misma en SQL Server. No es una validación completa del formato DBML (A4).

### `dictionary`

Genera una fila por columna con 19 campos: `TABLA`, `NOMBRE_DATO`, `TIPO_DE_DATO`, `LONGITUD`, `DESCRIPCION`, `REGEX`, `MASCARA`, `CRITERIOS_CALIDAD`, `TABLA_MAESTRA`, `CAMPO_MAESTRO`, `TIPO_RELACION`, `ES_MAESTRA`, `ES_PK`, `ES_NULLABLE`, `EJEMPLOS_VALIDOS`, `FUENTE_CAPTURA`, `MODULO`, `SENSIBILIDAD` y `OBSERVACIONES`.

La sensibilidad va de `BAJO` a `CRÍTICO` (`BAJO`, `MEDIO`, `ALTO`, `CRÍTICO`) y se decide por el nombre de la columna; Scavengr no lee los datos.

El formato sale de la extensión de `-o` (`.xlsx`, `.xls`, `.csv` o `.json`), o lo fijas con `-f excel|csv|json`.

### `report`

Genera un informe con el resumen del esquema, una puntuación de calidad (completitud, integridad referencial, consistencia de nombres y documentación), la distribución de tipos, las relaciones, la sensibilidad y recomendaciones.

Con `-o informe.xlsx` sale un Excel de 5 hojas: Resumen General, Calidad de Datos, Tipos de Datos, Seguridad y Recomendaciones. Con cualquier otra extensión sale JSON; incluso con `.csv`, el contenido es JSON.

### `init`

Crea el archivo `.env` con la plantilla. Si ya existe, pregunta antes de sobrescribirlo.

## Permisos en la base de datos

Scavengr solo ejecuta consultas de lectura sobre el catálogo del motor, pero no abre la sesión en modo de solo lectura. Usa un usuario sin permisos de escritura.

En PostgreSQL, `information_schema` le oculta las restricciones al usuario que no es dueño de las tablas. Con un usuario que solo tiene `SELECT`, la extracción sale sin PK ni FK (C3). Mientras se corrige, la extracción solo es completa con el dueño de las tablas.

## Desarrollo

```bash
git clone https://github.com/JasRockr/Scavengr.git
cd Scavengr
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1    Linux/macOS: source .venv/bin/activate
pip install -e ".[dev,postgres,mysql,mssql]"
pre-commit install
```

| Comando | Qué hace |
| --- | --- |
| `pytest tests -m "not lab" -q` | Pruebas rápidas, con mocks |
| `docker compose -f tests/lab/docker-compose.yml up -d --wait` | Levanta el laboratorio: PostgreSQL 16, MariaDB 10.11 y SQL Server 2022 |
| `npm ci --prefix tests/lab` | Instala `@dbml/core`, el parser oficial de DBML (una vez) |
| `pytest tests/integration -m lab -q` | Pruebas contra el laboratorio |
| `ruff check scavengr tests` | Errores reales de código. Bloquea en CI |
| `bandit -r scavengr -ll` | Problemas de seguridad de severidad media o alta. Bloquea en CI |
| `mypy scavengr` | Tipos. Informativo hasta la Fase 1 |

El CI (`.github/workflows/ci.yml`) corre las pruebas rápidas en Python 3.11 a 3.14 sobre Ubuntu y en 3.14 sobre Windows, y las del laboratorio en 3.11 y 3.14. Los checks `test`, `lint` y `security` son obligatorios para fusionar en `main`.

La estructura sigue capas:

```text
scavengr/
├── core/             # entidades, interfaces y servicios (clasificación, descripciones, máscaras…)
├── application/      # casos de uso: extract, validate, dictionary, report
├── infrastructure/   # conectores y escáneres de BD, caché, parser y formateador DBML, exportadores
├── config/           # carga de la configuración desde .env
├── utils/            # constantes, excepciones, logging y validadores
└── cli.py            # línea de comandos
```

Para contribuir, mira [docs/contributing.md](docs/contributing.md).

## Roadmap

La [auditoría técnica](docs/auditoria-tecnica/README.md#roadmap-por-fases) describe las fases hasta la v1.0: primero estabilizar (0.0.5), luego un modelo de datos propio con SQLAlchemy y pydbml, después la librería y las integraciones con dbt y BigQuery, y al final REST y MCP.

## Licencia y contacto

MIT. Ver [LICENSE](LICENSE).

Json Rivera ([@JasRockr](https://github.com/JasRockr)) · [jsonrivera@proton.me](mailto:jsonrivera@proton.me) · [Issues](https://github.com/JasRockr/Scavengr/issues)
