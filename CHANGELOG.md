# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Próximos Pasos

- Validación en entornos productivos reales
- Feedback de usuarios en casos de uso empresariales
- Ajustes basados en experiencia de uso en producción

---

## [0.0.4] - 2025-11-19

### Added [0.0.4]

- **Parser DBML Completo**: Soporte completo para bloques de índices
  - Parseo de índices con columnas: `(col1, col2) [type: btree]`
  - Parseo de índices vacíos: `() [type: primary]`
  - Atributo `indexes` en entidad `Table`
  - Método `_parse_indexes()` en `DBMLParser`
- **Sistema de Validación de Calidad**: 8 tipos de advertencias detectadas
  - Genéricas: Tablas sin PK, tablas sin columnas, esquemas vacíos
  - MySQL: Índices BTREE/PRIMARY sin columnas (inferencia automática)
  - PostgreSQL: Identificadores CamelCase, tipos con espacios
  - SQL Server: Autoreferences al mismo endpoint
  - Categorización y resumen de advertencias
- **Suite de Tests Completa**: 282 tests (100% passing)
  - Tests unitarios: 151 tests
  - Tests de integración: 131 tests
  - Cobertura global: 74% (supera objetivo 60%)
  - Módulos clave:
    - `infrastructure/database/scanners.py`: 100%
    - `infrastructure/database/connector.py`: 92%
    - `infrastructure/formatters/dbml_formatter.py`: 95%
    - `infrastructure/cache/metadata_cache.py`: 85%
- **Sistema de Caché de Metadatos**: Implementado y testeado (85% coverage)
  - `infrastructure/cache/metadata_cache.py`: Clase MetadataCache
  - Flags CLI: `--cache` para habilitar, `--force-refresh` para invalidar
  - Serialización: Pickle (rápido) y JSON (portable)
  - TTL configurable (default: 24 horas)
  - 18 tests unitarios pasando (100% funcional)
  - Reducción ~90% en tiempo de extracciones subsecuentes
- **CI/CD Workflows**: 6 workflows en GitHub Actions
  - `ci.yml`: Orquestador principal
  - `test.yml`: Tests en 15 combinaciones (3 OS × 5 Python)
  - `lint.yml`: Linting (black, isort, flake8, mypy)
  - `security.yml`: Seguridad (safety, bandit)
  - `docs.yml`: Documentación MkDocs → GitHub Pages
  - `release.yml`: Publicación automática a PyPI
- **Documentación Completa**:
  - `docs/`: Documentación MkDocs con API reference
  - `DEPLOYMENT.md`: Guía de arquitectura GitHub Pages
  - `.github/BRANCH_PROTECTION_GUIDE.md`: Guía de protección de ramas
  - Landing page profesional en `index.html`
  - Dominio personalizado: `scavengr.jsonrivera.dev`
- **Sistema de Versionado Automático**:
  - `scripts/publish.ps1`: Script de publicación con consulta de tags
  - Setuptools-scm para versioning desde Git tags
  - Sugerencias automáticas de versión (patch/minor/major)

### Changed [0.0.4]

- **Cobertura de Código**: 44% → 74% (+30%)
  - Mejora significativa en módulos infrastructure
  - Mejora en módulos application
  - Parser DBML: 93% → 67% (ajustado a realidad)
- **Validación de Esquemas**: Detección proactiva de problemas
  - MySQL: Detección por índices (BTREE, PRIMARY, HASH, etc.)
  - PostgreSQL: Detección por tipos (serial, jsonb, etc.)
  - SQL Server: Detección por tipos nativos
- **Mensajes de Usuario**: Compatibilidad Windows/PowerShell
  - Eliminados acentos en todos los mensajes
  - Encoding limpio en terminales Windows

### Fixed [0.0.4]

- **BUG CRÍTICO: Validación con índices None**: Corregido error `'NoneType' object has no attribute 'upper'`
  - **Problema**: `scavengr validate` fallaba cuando un índice tenía `index_type=None` explícitamente
  - **Causa**: `getattr(index, "index_type", "")` devolvía `None` si el atributo existía con valor `None`
  - **Solución**: Usar operador `or` para garantizar string vacío: `(getattr(index, "index_type", None) or "").upper()`
  - **Ubicación**: `scavengr/application/validate.py` líneas 464 y 609
  - **Test de regresión**: `tests/integration/test_validate_usecase.py::test_validate_dbml_with_none_index_type`
  - **Reportado en**: Testing E2E con archivos DBML reales (struct-dwh_test_mysql.dbml)
- **Estructura de Proyecto**:
  - `.gitignore`: Configuración corregida (docs/, tests/ NO ignorados)
  - `.gitignore`: Solo workflows y `*_GUIDE.md` en `.github/`
  - Eliminados archivos obsoletos de testing

### Fixed [0.0.4]

- **Parser DBML**: Bloques de índices ahora se parsean completamente
  - Bug crítico: `if line.startswith("indexes"): continue` → `break`
  - Índices disponibles para validaciones MySQL/PostgreSQL
- **Atributos de Entidades**: Coherencia en nombres
  - `Index.type` → `Index.index_type` (corrección en validate.py)
  - Todos los accesos a atributos validados
- **Detección MySQL**: PRIMARY incluido en indicadores
  - Lista actualizada: BTREE, HASH, FULLTEXT, SPATIAL, PRIMARY
  - Tablas con solo PRIMARY ahora detectadas correctamente
- **Encoding Windows**: Mensajes sin caracteres especiales
  - "índice" → "indice", "será" → "sera", etc.
  - Output limpio en PowerShell

### Infrastructure [0.0.4]

- **GitHub Pages**: Arquitectura de dos niveles
  - `/` → Landing page (index.html)
  - `/docs/` → Documentación MkDocs
  - Deployment automático desde workflow docs.yml
  - Rama `gh-pages` auto-generada
- **Pre-commit Hooks**: Configuración `.pre-commit-config.yaml`
  - Validación automática en commits locales
  - Hooks: black, isort, flake8
- **Security**: Análisis completo sin vulnerabilidades
  - Bandit: 0 issues encontrados
  - Safety: Dependencias actualizadas
  - CodeQL: Escaneo automático en CI

### Documentation [0.0.4]

- **README.md**: Actualizado con métricas reales
  - Badges: 282 tests, 74% coverage, v0.0.4
  - Sección de validaciones proactivas agregada
  - Ejemplos de uso actualizados
- **index.html**: Actualizado a Alpha v0.0.4
  - Métricas sincronizadas con proyecto
  - Quality section actualizada
- **code-evaluation-v010.md**: Evaluación técnica completa
  - Todas las métricas de cobertura corregidas
  - Estado: "Excelente estado de testing"

---

## [0.0.3] - 2025-10-12

### Added [0.0.3]

- **Logging Coloreado ANSI**: Sistema de logging con colores para mejor UX en terminal
  - `utils/logging_config.py`: ColorFormatter personalizado
  - Niveles: DEBUG (cyan), INFO (verde), WARNING (amarillo), ERROR (rojo), CRITICAL (rojo bold)
- **Tests Iniciales**: Primeros tests exploratorios del proyecto
- **Guía de Configuración**: Documentación mejorada para configuración de entorno

### Changed [0.0.3]

- **Arquitectura Clean Architecture**: Mejoras en separación de capas
  - Refactorización de `core/` para mejor separación de responsabilidades
  - Mejora en interfaces y contratos
- **Optimización PyPI**: Mejoras en empaquetado y distribución
  - Actualización de `pyproject.toml`
  - Configuración de setuptools_scm para versionado automático

### Fixed [0.0.3]

- Correcciones menores en documentación
- Ajustes en manejo de errores

---

## [0.0.2] - 2025-10-05

### Added [0.0.2]

- **Comando `report`**: Generación de reportes analíticos en Excel
  - Score de calidad en 7 dimensiones
  - Análisis estadístico de esquema
  - Recomendaciones priorizadas por impacto
  - 5 hojas en archivo Excel: Resumen, Calidad, Estadísticas, Sensibilidad, Recomendaciones
- **Comando `dictionary`**: Generación de diccionarios de datos profesionales
  - 19 campos especializados por columna
  - Análisis de sensibilidad automático (CRÍTICO, ALTO, MEDIO, BAJO)
  - Descripciones inteligentes basadas en 80+ patrones
  - Exportación a Excel, CSV, JSON

### Changed [0.0.2]

- **Servicios de Dominio**: 10 servicios implementados en `core/services.py`
  - RegexInferenceService: Inferencia de patrones regex
  - MaskGeneratorService: Generación de máscaras de datos
  - QualityCriteriaService: Criterios de calidad
  - ExampleGeneratorService: Generación de ejemplos
  - ModuleClassifierService: Clasificación de módulos
  - SensitivityAnalyzerService: Análisis de sensibilidad PII/PCII
  - ObservationGeneratorService: Generación de observaciones
  - DescriptionGeneratorService: Generación de descripciones automáticas
  - StatisticsAnalyzerService: Análisis estadístico
  - RelationshipAnalyzer: Análisis de relaciones

### Fixed [0.0.2]

- Mejoras en manejo de excepciones personalizadas
- Correcciones en exportadores

---

## [0.0.1] - 2025-09-28

### Added [0.0.1]

- **Comando `init`**: Configuración inicial del proyecto
  - Generación de archivo `.env` local o global
  - Plantilla con variables de configuración de BD
- **Comando `extract`**: Extracción de metadatos de bases de datos
  - Soporte PostgreSQL
  - Soporte MySQL/MariaDB
  - Soporte SQL Server
  - Generación de archivos DBML compatibles con dbdiagram.io
- **Comando `validate`**: Validación de archivos DBML
  - Validación de sintaxis DBML
  - Validación de estructura (tablas, columnas, relaciones)
  - Validación de integridad referencial
  - Validaciones de calidad (CamelCase, tipos con espacios, autoreferences, índices)
- **Entidades de Dominio**: Modelo rico de datos
  - `DatabaseSchema`: Esquema completo de BD
  - `Table`: Tabla con columnas, relaciones e índices
  - `Column`: Columna con tipo, constraints y metadatos
  - `Relationship`: Relación entre tablas con cardinalidad
  - `Index`: Índice con columnas y tipo
- **Infraestructura de BD**: Adaptadores para motores
  - `PostgreSQLScanner`: Extractor para PostgreSQL
  - `MySQLScanner`: Extractor para MySQL/MariaDB
  - `MSSQLScanner`: Extractor para SQL Server
  - `DBMLParser`: Parser de archivos DBML
  - `DBMLFormatter`: Formateador de salida DBML
- **Exportadores**: Múltiples formatos de salida
  - `ExcelExporter`: Exportación a Excel (.xlsx)
  - `CSVExporter`: Exportación a CSV
  - `JSONExporter`: Exportación a JSON
- **Configuración**: Gestión de configuración flexible
  - `EnvConfigManager`: Gestor de variables de entorno
  - Soporte para `.env` local, global y variables del sistema
  - Priorización de fuentes de configuración
- **CLI Profesional**: Interfaz de línea de comandos con Click
  - Help messages descriptivos
  - Validación de argumentos
  - Feedback visual con colores
  - Manejo de errores amigable

### Infrastructure [0.0.1]

- **Arquitectura Clean Architecture**: Separación clara de capas
  - `application/`: Casos de uso
  - `core/`: Dominio (entidades, servicios, interfaces)
  - `infrastructure/`: Adaptadores externos
  - `config/`: Configuración
  - `utils/`: Utilidades transversales
- **Interfaces y Contratos**: Diseño por contratos
  - `IScanner`: Interfaz para scanners de BD
  - `IParser`: Interfaz para parsers
  - `IFormatter`: Interfaz para formateadores
  - `IExporter`: Interfaz para exportadores
- **Validadores**: Utilidades de validación
  - `validate_file_exists`: Validación de existencia de archivos
  - `validate_output_format`: Detección de formatos
  - `validate_write_permissions`: Validación de permisos
  - `validate_input_file_format`: Validación de formatos de entrada
- **Excepciones Personalizadas**: Manejo de errores específico del dominio
  - `DatabaseConnectionError`: Errores de conexión a BD
  - `DBMLParsingError`: Errores de parseo DBML
  - `ValidationError`: Errores de validación
  - `ExportError`: Errores de exportación

### Documentation [0.0.1]

- **README.md**: Documentación completa (530 líneas)
  - Guía de instalación detallada
  - Casos de uso documentados
  - Ejemplos de comandos
  - Requisitos del sistema
  - Arquitectura del proyecto
- **index.html**: Landing page profesional (499 líneas)
  - Características principales
  - Flujo de trabajo típico
  - Opciones de instalación
  - Ejemplos de uso
- **Docstrings**: Documentación en código
  - Google Style docstrings en todos los módulos
  - Documentación de parámetros, retornos y excepciones

### Dependencies

- **Core**: Click, python-dotenv
- **Database Drivers**: psycopg2-binary, mysql-connector-python, pyodbc
- **Export**: openpyxl (Excel), csv (stdlib), json (stdlib)
- **Development**: pytest, mypy, black, isort, flake8

---

## Notas de Migración

### De 0.0.3 a 0.0.4

- **Tests**: Suite completa con 282 tests. Ejecutar `pytest tests/` para validar
- **CI/CD**: 6 workflows activos. Revisar configuración en `.github/workflows/`
- **Coverage**: Objetivo de 74% superado. Verificar con `pytest --cov=scavengr`
- **Parser DBML**: Ahora parsea índices completamente. Archivos DBML existentes compatibles
- **Validación**: 8 tipos de advertencias detectadas. Ejecutar `scavengr validate -i schema.dbml`
- **Versionado**: Usar `scripts/publish.ps1` para publicar (consulta tags automáticamente)
- **GitHub Pages**: Dominio `scavengr.jsonrivera.dev` configurado con documentación MkDocs

### De 0.0.2 a 0.0.3

- **Logging**: Colores ANSI en terminal. Configurar para mejor experiencia
- **Arquitectura**: Refactorización en `core/`. Revisar imports personalizados

### De 0.0.1 a 0.0.2

- **Comandos**: `dictionary` y `report` disponibles. Actualizar flujos de trabajo
- **Servicios**: 10 servicios de dominio para extensiones

---

## [0.0.0] - 2025-09-20

### Initial Commit

- Estructura inicial del proyecto
- Configuración de repositorio Git
- Licencia MIT
- `.gitignore` configurado

---

## Enlaces

- **Repositorio**: <https://github.com/JasRockr/Scavengr>
- **PyPI**: <https://pypi.org/project/scavengr/>
- **Documentación**: <https://scavengr.jsonrivera.dev>
- **Issues**: <https://github.com/JasRockr/Scavengr/issues>
- **Pull Requests**: <https://github.com/JasRockr/Scavengr/pulls>

---

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/lang/es/):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible con versiones anteriores
- **PATCH**: Correcciones de bugs compatibles con versiones anteriores

**Versión Actual**: 0.0.4 (Alpha)  
**Fecha de Release**: 2025-11-19  
**Próxima Versión Planeada**: 0.1.0 (Beta) - Reportes más detalados y Optimizaciones
