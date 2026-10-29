# Scavengr — guía para Claude Code

Scavengr extrae metadatos de bases de datos (PostgreSQL, MySQL/MariaDB, SQL Server), clasifica la sensibilidad de las columnas (Ley 1581 de Colombia, PCI, GDPR) y genera DBML, diccionarios Excel y reportes. Objetivo v1.0: una librería Python usable como dependencia, con integraciones a dbt y BigQuery primero y REST/MCP después.

Fuente de verdad: `docs/auditoria-tecnica/README.md`. Si este archivo la contradice, gana la auditoría; avisa de la contradicción.

## Decisiones tomadas (no reabrir sin preguntar)

- Ramas `feat/*`, `fix/*` y `chore/*` desde `main`.
- Licencia: Apache-2.0 desde la próxima versión (las versiones ya publicadas siguen MIT).
- SQL Server: pyodbc vía SQLAlchemy por defecto; pymssql como extra opcional.
- Reflexión de esquemas: SQLAlchemy 2.x Inspector. SQL nativo solo para extras (procedimientos, triggers, estadísticas).
- DBML: pydbml para leer y escribir; `@dbml/core` como validador en CI.
- Modelo canónico: Pydantic v2, contrato versionado `scavengr.catalog/v1`. El DBML deja de ser formato intermedio.
- Python `>=3.11`: solo versiones con soporte de seguridad (la 3.10 dejó de tenerlo el 1 oct 2026; esto reemplaza el `>=3.10` de la auditoría). Dependencias con rangos (`>=x,<y`), nunca pines exactos.

## Fase actual: 0 — Estabilización (v0.0.5)

Trabaja solo en tareas de esta fase salvo que se pida otra cosa. Puerta de salida:

- Laboratorio PostgreSQL: 4/4 FK y 5/5 PK correctas, también con el rol de solo lectura `lector`.
- DBML válido según `@dbml/core` en PostgreSQL, MariaDB y SQL Server.
- `DB_PORT` no estándar respetado (el laboratorio usa 5433, 3307 y 14333 a propósito).
- CI en verde con Python 3.11–3.14.

## Comandos

```bash
pip install -e ".[dev,postgres,mysql,mssql]"
pytest tests -m "not lab" -q              # rápido, con mocks
docker compose -f tests/lab/docker-compose.yml up -d --wait
npm ci --prefix tests/lab                  # una vez
pytest tests/integration -m lab -q         # contra el laboratorio
node tests/lab/dbmlcheck.js <archivo.dbml> # parser oficial de DBML
ruff check scavengr tests                  # bloquea en CI (errores reales)
bandit -r scavengr -ll                     # bloquea en CI (severidad media o alta)
mypy scavengr                              # informativo hasta la Fase 1
```

Comandos y rutas deben funcionar en Windows (PowerShell) y en Linux.

## Reglas de código (invariantes)

- Toda tabla se identifica por `(schema, table)`. Nunca asociar índices, PK o FK solo por nombre de tabla.
- FK compuestas conservan el orden de columnas; nunca producto cartesiano.
- Visibilidad incompleta (constraints ocultas, permisos) = advertencia explícita en el resultado. Nunca un éxito silencioso con datos incompletos.
- Librería sin `print()`, sin `sys.exit()` y sin configurar logging global (logger por módulo + `NullHandler`). La salida a consola vive solo en `cli.py`.
- Excepciones tipadas que heredan de `ScavengrError`; nada de `raise Exception(...)`.
- Conexiones de solo lectura (`SET TRANSACTION READ ONLY` o equivalente); contraseñas nunca en logs ni en caché.
- Los valores de las columnas (muestreo) nunca se persisten ni se registran; solo conteos y patrones.
- Las etiquetas legales citan el artículo correcto. La Ley 1581 no define "privado/semiprivado/público"; no atribuirlo al Art. 6.

## Cómo trabajar

- Cada fix de un hallazgo (C1–C5, A1–A6, M1–M5) lleva primero un test que falla contra el laboratorio y luego el arreglo. Conventional Commits pequeños con el ID: `fix(scanner): ... [C2]`.
- No cambies comandos ni flags de la CLI sin preguntar; las rutas de import viejas se mantienen con `DeprecationWarning` durante dos versiones menores.
- No publiques en PyPI, no hagas push a `main` ni cambies la licencia sin confirmación explícita.
- Tras cambiar conectores, scanners, extract, parser o formatter, corre la skill `lab-check`. Antes de cerrar una fase, el subagente `gate-reviewer`.
