# Changelog

Los cambios notables de cada versión. El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y el proyecto usa [Semantic Versioning](https://semver.org/lang/es/). Las fechas son las de publicación en PyPI.

## [Unreleased]

Esta versión (0.0.5) es la Fase 0 de la [auditoría técnica](docs/auditoria-tecnica/README.md): estabilizar antes de agregar funciones.

### Added

- Laboratorio de bases de datos en `tests/lab`: PostgreSQL 16, MariaDB 10.11 y SQL Server 2022 con Docker Compose, en puertos no estándar (5433, 3307 y 14333) y con un rol `lector` de solo lectura. Incluye `@dbml/core` para validar el DBML con el parser oficial.
- Pruebas de integración contra el laboratorio (`pytest -m lab`).
- CI en GitHub Actions (`ci.yml`): `lint` (ruff), `security` (bandit y pip-audit), pruebas en Python 3.11–3.14 sobre Ubuntu y en 3.14 sobre Windows, y pruebas del laboratorio en 3.11 y 3.14.
- Dependabot semanal para pip, GitHub Actions y npm del laboratorio.
- La auditoría técnica, en `docs/auditoria-tecnica/`.

### Changed

- Python mínimo: 3.11. La 3.10 dejó de recibir parches de seguridad el 1 de octubre de 2026.
- Las dependencias pasan de versiones exactas a rangos (`>=x,<y`). Mínimos que suben por seguridad: `python-dotenv>=1.2.2` (PYSEC-2026-2270) y, en el build, `setuptools>=78.1.1` (CVE-2025-47273).
- `safety` sale de las dependencias de desarrollo; la auditoría de dependencias la hace `pip-audit`.
- README y `docs/` reescritos para describir lo que el código hace hoy, con las limitaciones conocidas.

### Fixed

- `connector.py` fallaba al importarse si faltaba el driver de un motor.
- La caché de metadatos no vencía exactamente al cumplir su TTL.
- Pruebas que dependían del entorno: escribir en `C:\Windows\System32` y tener pyodbc instalado.

## [0.0.4.post1] - 2025-11-20

Mismo commit que 0.0.4 (`d299eb7`), publicado otra vez en PyPI el mismo día.

## [0.0.4] - 2025-11-20

### Added

- Caché de metadatos (`infrastructure/cache/metadata_cache.py`) con las opciones `extract --cache` y `--force-refresh`. Guarda con pickle en `.scavengr_cache/` y vence a las 24 horas.
- El parser de DBML lee los bloques `indexes`, incluidos los índices sin columnas (`() [type: primary]`). Antes los saltaba.
- Advertencias de calidad en `validate`: tablas sin PK o sin columnas, esquema vacío, índices de MySQL sin columnas, identificadores camelCase y tipos con espacios en PostgreSQL, y referencias de una columna a sí misma en SQL Server.
- 283 pruebas (274 unitarias y 9 de integración), todas con mocks, con 75 % de cobertura medida en la auditoría.
- Documentación con MkDocs en `docs/`, la página de inicio `index.html`, `DEPLOYMENT.md`, `.github/BRANCH_PROTECTION_GUIDE.md`, este CHANGELOG y el dominio `scavengr.jsonrivera.dev` (`CNAME`).
- `scripts/publish.ps1` para publicar versiones (detecta protecciones de rama y propone la versión a partir de los tags) y `scripts/cleanup-release.ps1` para deshacer un release.
- Configuración de pre-commit con black, isort y flake8.

### Fixed

- `validate` fallaba con `'NoneType' object has no attribute 'upper'` cuando un índice tenía `index_type=None`.

### Notas

Las versiones anteriores de este CHANGELOG describían seis workflows de GitHub Actions (`test`, `lint`, `security`, `docs`, `release` y un orquestador), escaneo con CodeQL, despliegue de la documentación con MkDocs a una rama `gh-pages` y un archivo `code-evaluation-v010.md`. Nada de eso llegó al repositorio en esta versión: el único CI es el de la 0.0.5 y GitHub Pages publica la rama `main` tal cual. También decía 282 pruebas, divididas en 151 unitarias y 131 de integración; la cifra real es la de arriba.

## [0.0.3] - 2025-10-09

### Added

- Comando `init` para crear el `.env` local o `~/.scavengr.env` (`--global`).
- Archivo de configuración global `~/.scavengr.env`, que se suma a `.env.local` y `.env`.
- `python -m scavengr`.
- Guía de logging ampliada en `scavengr/utils/README.md`.

### Changed

- El informe de `report` pasa de la CLI a su propio caso de uso, `application/report.py`.

## [0.0.2] - 2025-10-09

### Changed

- README con las instrucciones de instalación desde PyPI y las insignias. Sin cambios de código.

## [0.0.1] - 2025-10-08

Primera versión publicada.

### Added

- Comandos `extract`, `validate`, `dictionary` y `report`, con argparse. `extract` acepta `--env-file`.
- Lectura de metadatos de PostgreSQL, MySQL/MariaDB y SQL Server, y salida en DBML.
- `validate`: revisa que el DBML se pueda parsear, que las tablas tengan columnas y que las relaciones apunten a columnas que existen.
- `dictionary`: diccionario de datos de 19 campos por columna en Excel, CSV o JSON, con la sensibilidad (`BAJO`, `MEDIO`, `ALTO`, `CRÍTICO`) decidida por el nombre de la columna.
- `report`: Excel de 5 hojas (Resumen General, Calidad de Datos, Tipos de Datos, Seguridad y Recomendaciones) con una puntuación de calidad de 4 dimensiones: completitud, integridad referencial, consistencia de nombres y documentación.
- Configuración desde `.env.local` y `.env` (`EnvConfigManager`).
- Capas `core`, `application`, `infrastructure`, `config` y `utils`: entidades (`DatabaseSchema`, `Table`, `Column`, `Relationship`, `Index`), interfaces (`IMetadataScanner`, `IParser`, `IFormatter`, `IExporter`), servicios de dominio (sensibilidad, descripciones, regex, máscaras, ejemplos, criterios de calidad, módulos, relaciones, observaciones y estadísticas), `OutputWriter` y las excepciones `ScavengrError`, `FileNotFoundError`, `InvalidFormatError`, `ProcessingError` y `ValidationError`.
- Logging con colores ANSI.
- Dependencias: `python-dotenv` y `openpyxl`, y los drivers de cada motor como extras (`postgres`, `mysql`, `mssql`, `all-db`). Python 3.8+.

[Unreleased]: https://github.com/JasRockr/Scavengr/compare/v0.0.4.post1...HEAD
[0.0.4.post1]: https://github.com/JasRockr/Scavengr/compare/v0.0.4...v0.0.4.post1
[0.0.4]: https://github.com/JasRockr/Scavengr/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/JasRockr/Scavengr/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/JasRockr/Scavengr/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/JasRockr/Scavengr/releases/tag/v0.0.1
