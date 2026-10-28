# 🗃️ Scavengr

![CI/CD](https://github.com/JasRockr/Scavengr/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-282%2F282-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-74%25-brightgreen.svg)
![Version](https://img.shields.io/badge/version-0.0.4-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-yellow.svg)
[![PyPI version](https://badge.fury.io/py/scavengr.svg)](https://pypi.org/project/scavengr/)

> _"Descubre lo que tus bases esconden."_

**Scavengr** es una herramienta de línea de comandos para extraer, validar y documentar metadatos de bases de datos con **inteligencia automática** 🧠✨

Extrae esquemas de bases de datos, genera archivos DBML compatibles con [dbdiagram.io](https://dbdiagram.io), crea diccionarios de datos profesionales y produce informes analíticos detallados.

---

## 🚀 Características Principales

### 🔍 **Extracción de Metadatos**

- **Múltiples motores**: PostgreSQL, MySQL/MariaDB y SQL Server
- **Extracción completa**: Tablas, columnas, tipos de datos, relaciones, índices
- **Formato DBML**: Archivos compatibles con dbdiagram.io para visualización
- **Configuración simple**: Usa archivo `.env` para credenciales

### 📊 **Diccionarios de Datos Profesionales**

- **Formato Excel avanzado**: 19 campos especializados por columna
- **Análisis de sensibilidad**: Clasificación automática (CRÍTICO, ALTO, MEDIO, BAJO)
- **Descripciones inteligentes**: Generación automática basada en 80+ patrones
- **Observaciones contextuales**: Warnings y recomendaciones automáticas

### ✅ **Validación de Esquemas DBML**

- **Validación exhaustiva**: Sintaxis, estructura y consistencia
- **Detección de errores**: Tablas, relaciones, claves y tipos de datos
- **Análisis de integridad**: Verifica referencias y relaciones
- **Validaciones de calidad**: Detecta problemas automáticos (CamelCase, tipos con espacios, autoreferences, índices incompletos)

### 📈 **Reportes Analíticos**

- **Score de calidad**: Evaluación en 7 dimensiones
- **Análisis estadístico**: Distribución de tipos, tamaños, relaciones
- **Recomendaciones**: Mejoras priorizadas por impacto
- **Formato Excel**: 5 hojas con información completa

---

## ✅ Flujo de trabajo típico

### 1. Configuración inicial (una sola vez)

```bash
scavengr init
```

### 2. Flujo principal

```bash
scavengr extract -o schema.dbml                    # Extraer
scavengr validate -i schema.dbml                   # Validar
scavengr dictionary -i schema.dbml -o dict.xlsx    # Documentar
scavengr report -i schema.dbml -o report.xlsx      # Analizar
```

---

## ⚡ Instalación

### Requisitos Previos

- **Python**: 3.8 o superior (recomendado: 3.10+)
- **pip**: Gestor de paquetes de Python

### Instalación desde PyPI

La forma más sencilla de instalar **Scavengr** es directamente desde PyPI:

```bash
# Instalación básica
pip install scavengr

# Verificar instalación
scavengr --version

# Configuración inicial (crea archivo .env)
scavengr init

# ¡Listo para usar!
scavengr extract -o mi-esquema.dbml
```

### Instalación desde Fuente - En modo Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/JasRockr/Scavengr.git
cd Scavengr

# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar entorno virtual
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/Mac:
source .venv/bin/activate

# Instalar Scavengr en modo desarrollo
pip install -e .

# Verificar instalación
scavengr --version
```

### Dependencias por Motor de Base de Datos

```bash
# Para PostgreSQL
pip install psycopg2-binary

# Para MySQL/MariaDB
pip install mysql-connector-python

# Para SQL Server
pip install pyodbc
# En Windows: Instalar ODBC Driver 17 for SQL Server
# Descargar desde: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

---

## 🎯 Uso Básico

### 1️⃣ **Configuración Inicial**

#### 🚀 **Configuración Rápida (Recomendado)**

```bash
# Generar archivo de configuración automáticamente
scavengr init

# O crear configuración global (disponible en cualquier directorio)
scavengr init --global
```

#### 🔧 **Configuración Manual**

```bash
# Opción 1: Crear archivo .env local (desde desarrollo)
cp .env.example .env

# Opción 2: Crear archivo .env desde cero
echo 'DB_TYPE=postgresql' > .env
echo 'DB_HOST=localhost' >> .env
echo 'DB_NAME=mi_base_datos' >> .env
echo 'DB_USER=usuario_lectura' >> .env
echo 'DB_PASSWORD=contraseña_segura' >> .env
```

#### 📍 **Ubicaciones de Configuración**

Scavengr busca configuración en este orden de prioridad:

1. **Archivo específico**: `--env-file mi-config.env`
2. **Directorio actual**: `.env.local` → `.env`
3. **Configuración global**: `~/.scavengr.env`
4. **Variables del sistema**: `export DB_TYPE=postgresql`

**Tipos de base de datos soportados**: `postgresql`, `mysql`, `mssql`

### 2️⃣ **Extraer Esquema de Base de Datos**

```bash
# Extrae esquema completo a archivo DBML
scavengr extract -o /ruta/mi-esquema.dbml
```

**Resultado**: Archivo DBML con:

- ✅ Definición de tablas y columnas
- ✅ Tipos de datos nativos
- ✅ Primary keys y foreign keys
- ✅ Índices con columnas
- ✅ Valores por defecto
- ✅ Relaciones entre tablas

### 3️⃣ **Validar Archivo DBML**

```bash
# Valida sintaxis y estructura
scavengr validate -i /ruta/mi-esquema.dbml

# Salida típica:
# ✓ Estructura de tablas: OK
# ✓ Relaciones: 875 validadas
# ⚠ Advertencias: 16 (tablas de auditoría, temporales)
# ✓ Errores: 0
```

### 4️⃣ **Generar Diccionario de Datos**

```bash
# Genera diccionario en Excel (recomendado)
scavengr dictionary -i /ruta/mi-esquema.dbml -o /ruta/diccionario.xlsx
```

**Resultado**: Archivo Excel con 19 campos por columna:

- Nombre de tabla y columna
- Tipo de dato y tamaño
- Clasificación de sensibilidad (CRÍTICO, ALTO, MEDIO, BAJO)
- Descripción generada automáticamente
- Observaciones y recomendaciones
- Máscaras de datos sugeridas
- Ejemplos de valores
- Criterios de calidad

### 5️⃣ **Generar Reporte Analítico**

```bash
# Genera reporte con métricas en Excel
scavengr report -i /ruta/mi-esquema.dbml -o /ruta/reporte-analisis.xlsx
```

**Resultado**: Archivo Excel con 5 hojas:

1. **Resumen Ejecutivo**: Score de calidad y métricas principales
2. **Análisis de Calidad**: 7 dimensiones evaluadas
3. **Estadísticas**: Distribución de tipos, tamaños, relaciones
4. **Sensibilidad**: Campos críticos y protegidos
5. **Recomendaciones**: Mejoras priorizadas por impacto

---

## ⚡ Comandos Disponibles

```bash
# Ayuda general
scavengr --help

# Ayuda por comando
scavengr init --help
scavengr extract --help
scavengr validate --help
scavengr dictionary --help
scavengr report --help

# Versión
scavengr --version
```

### Comando `extract`

```bash
scavengr extract [OPTIONS]

Opciones:
  -o, --output PATH        Archivo DBML de salida (requerido)
  --env-file PATH          Archivo .env alternativo a usar
  --cache                  Habilita caché de metadatos (MetadataCache)
  --force-refresh          Invalida caché y reextrae desde BD
  --help                   Mostrar ayuda
```

**Sistema de Caché (MetadataCache)**:
- **Serialización**: Pickle (rápido) o JSON (portable)
- **TTL**: 24 horas por defecto (configurable)
- **Ubicación**: `.scavengr_cache/` (auto-creado, ignorado por git)
- **Rendimiento**: ~90% reducción en tiempo de extracciones subsecuentes
- **Gestión**: Expiración automática basada en TTL

```bash
# Primera extracción (crea caché)
scavengr extract --cache -o schema.dbml

# Subsecuentes (usa caché, ~90% más rápido)
scavengr extract --cache -o schema.dbml

# Forzar actualización (si BD cambió)
scavengr extract --cache --force-refresh -o schema.dbml
```

### Comando `validate`

```bash
scavengr validate [OPTIONS]

Opciones:
  -i, --input PATH         Archivo DBML a validar (requerido)
  --help                   Mostrar ayuda
```

### Comando `dictionary`

```bash
scavengr dictionary [OPTIONS]

Opciones:
  -i, --input PATH         Archivo DBML de entrada (requerido)
  -o, --output PATH        Archivo de salida .xlsx (requerido)
  --help                   Mostrar ayuda
```

### Comando `init`

```bash
scavengr init [OPTIONS]

Opciones:
  --global                 Crear configuración global en directorio home
  --help                   Mostrar ayuda
```

### Comando `report`

```bash
scavengr report [OPTIONS]

Opciones:
  -i, --input PATH         Archivo DBML de entrada (requerido)
  -o, --output PATH        Archivo de salida .xlsx (requerido)
  --help                   Mostrar ayuda
```

---

## � Características Avanzadas

### Validaciones Proactivas de Calidad

El comando `validate` ahora detecta y reporta **problemas automáticos** que serán corregidos durante la generación:

#### **Problemas Detectados por Motor de Base de Datos**

| Motor          | Problema                         | Acción                                                         |
| -------------- | -------------------------------- | -------------------------------------------------------------- |
| **MySQL**      | Índices BTREE sin columnas       | Inferidas automáticamente                                      |
| **MySQL**      | Índices PRIMARY vacíos           | Se agregan todas las PKs                                       |
| **PostgreSQL** | Identificadores CamelCase        | Escapados con comillas dobles                                  |
| **PostgreSQL** | Tipos con espacios               | Normalizados (ej: `timestamp without time zone` → `timestamp`) |
| **MSSQL**      | Autoreferences al mismo endpoint | Filtradas para evitar ciclos                                   |

#### **Ejemplo de Uso**

```bash
scavengr validate -i schema.dbml

✅ VALIDACIONES BÁSICAS: OK
   - Archivo: Existe y se puede leer
   - Sintaxis DBML: Correcta

⚠️  VALIDACIONES DE CALIDAD: 5 ADVERTENCIAS
   [MySQL] 2 índices BTREE sin columnas → Serán inferidas
   [PostgreSQL] 3 identificadores CamelCase → Serán escapados

✅ RESULTADO: Esquema procesable
```

---

## �🛡️ Seguridad y Permisos

### Permisos de Base de Datos Requeridos

Scavengr necesita **solo lectura** en vistas del sistema:

#### **PostgreSQL**

```sql
GRANT CONNECT ON DATABASE mi_base TO usuario_scavengr;
GRANT USAGE ON SCHEMA information_schema TO usuario_scavengr;
GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO usuario_scavengr;
```

#### **MySQL/MariaDB**

```sql
GRANT SELECT ON information_schema.* TO 'usuario_scavengr'@'%';
```

#### **SQL Server**

```sql
GRANT VIEW DEFINITION TO usuario_scavengr;
-- O simplemente:
ALTER ROLE db_datareader ADD MEMBER usuario_scavengr;
```

> **🔒 Scavengr NUNCA modifica datos**: Solo lee metadatos del esquema

### Protección de Credenciales

```bash
# El archivo .env NO se debe versionar (está en .gitignore)
# Usa .env.example como plantilla

# Permisos recomendados (Linux/Mac):
chmod 600 .env
```

---

## 🏗️ Arquitectura

Scavengr implementa **Clean Architecture** con separación clara de responsabilidades:

```text
scavengr/
├── application/          # Casos de uso (extract, validate, dictionary, report)
├── core/                 # Entidades de dominio y servicios
│   ├── entities.py       # DatabaseSchema, Table, Column, Relationship, Index
│   ├── interfaces.py     # Contratos (Scanner, Parser, Exporter)
│   └── services.py       # 10 servicios de dominio
├── infrastructure/       # Adaptadores externos
│   ├── database/         # Scanners (PostgreSQL, MySQL, MSSQL)
│   ├── parsers/          # Parser DBML
│   ├── formatters/       # Formatter DBML
│   └── exporters/        # Exportadores (Excel, JSON)
├── config/               # Gestión de configuración
├── utils/                # Utilidades transversales
└── cli.py                # Interfaz de línea de comandos
```

**Beneficios**:

- ✅ Lógica de negocio desacoplada de infraestructura
- ✅ Fácilmente testeable y extensible
- ✅ Agregar nuevos motores de BD sin modificar el core
- ✅ Cambiar formatos de salida sin afectar la lógica

---

## 🎯 Casos de Uso

> Algunos casos de uso continuan en desarrollo y requieren extenderse para cobertura completa.

### **Caso 1: Documentar Base de Datos Existente**

```bash
# 1. Extraer esquema
scavengr extract -o /ruta/produccion.dbml

# 2. Validar integridad
scavengr validate -i /ruta/produccion.dbml

# 3. Generar diccionario para el equipo
scavengr dictionary -i /ruta/produccion.dbml -o /ruta/diccionario-produccion.xlsx
```

### **Caso 2: Auditoría de Calidad**

```bash
# 1. Extraer esquema
scavengr extract -o /ruta/auditoria.dbml

# 2. Generar reporte analítico
scavengr report -i /ruta/auditoria.dbml -o /ruta/reporte-calidad.xlsx

# 3. Revisar score de calidad y recomendaciones
# (Abrir reporte-calidad.xlsx)
```

### **Caso 3: Cumplimiento Protección de Datos**

```bash
# 1. Generar diccionario con análisis de sensibilidad
scavengr dictionary -i /ruta/esquema.dbml -o /ruta/datos-sensibles.xlsx

# 2. Filtrar campos CRÍTICOS y ALTOS en Excel
# 3. Aplicar máscaras de datos sugeridas
```

### **Caso 4: Migración de Base de Datos**

```bash
# 1. Extraer esquema origen
scavengr extract -o /ruta/origen.dbml

# 2. Extraer esquema destino
scavengr extract --env-file /ruta/destino.env -o /ruta/destino.dbml

# 3. Comparar manualmente (diff tool)
# 4. Validar ambos esquemas
scavengr validate -i origen.dbml
scavengr validate -i destino.dbml
```

---

## 🧪 Ejemplo de Salida

### Archivo DBML Generado

```dbml
Table dbo.usuarios {
  id_usuario int [pk, increment]
  nombre varchar(100) [not null]
  email varchar(255) [unique, not null]
  fecha_registro datetime [default: `getdate()`]
  id_departamento int [ref: > dbo.departamentos.id_departamento]

  indexes {
    email [unique, name: 'idx_usuarios_email']
    (nombre, email) [name: 'idx_usuarios_nombre_email']
  }
}

Table dbo.departamentos {
  id_departamento int [pk, increment]
  nombre varchar(100) [not null]
  descripcion text
}

Ref: dbo.usuarios.id_departamento > dbo.departamentos.id_departamento
```

### Diccionario de Datos (Excel)

| Tabla         | Columna | Tipo         | Sensibilidad | Descripción                    |
| ------------- | ------- | ------------ | ------------ | ------------------------------ |
| usuarios      | email   | varchar(255) | CRÍTICO      | Correo electrónico del usuario |
| usuarios      | nombre  | varchar(100) | ALTO         | Nombre completo del usuario    |
| departamentos | nombre  | varchar(100) | BAJO         | Nombre del departamento        |

---

## 🛠️ Requisitos del Sistema

- **Python**: 3.8+ (recomendado: 3.10 o superior)
- **Sistema Operativo**: Windows, Linux, macOS
- **Memoria**: Mínimo 512MB, recomendado 2GB para esquemas grandes
- **Dependencias**: Ver `pyproject.toml` para lista completa

---

## ✅ Validación de Código y Type Hints (v0.0.4)

Scavengr implementa **type hints completos** y pasa validación strict de mypy.

### Validación Local

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar mypy (strict mode)
python -m mypy scavengr/ --strict
# Resultado esperado: ✅ Success: no issues found in 33 source files

# Ejecutar tests
python -m pytest tests/ -v
# Resultado esperado: ✅ 51 passed in 2.26s

# Ejecutar tests con coverage
python -m pytest tests/ --cov=scavengr --cov-report=html
```

### Commandos de Validación Disponibles

```bash
# Validación rápida (mypy)
python -m mypy scavengr/ --strict

# Validación con linting
python -m flake8 scavengr/
python -m black --check scavengr/

# Formateo automático
python -m black scavengr/
python -m isort scavengr/

# Tests con salida detallada
python -m pytest tests/ -v --tb=short

# Tests con coverage
python -m pytest tests/ --cov=scavengr --cov-report=term-missing

# Pre-commit (si está configurado)
pre-commit run --all-files
```

### Características de Type Hints

- ✅ **100% Type Coverage**: Todas las funciones públicas y privadas tienen anotaciones
- ✅ **Mypy --strict**: 0 errores sin excepciones
- ✅ **IDE Support**: Autocomplete completo en VSCode, PyCharm, etc.
- ✅ **Runtime Safety**: Detecta errores de tipo antes de ejecución
- ✅ **Documentation**: Types sirven como documentación en línea

### Configuración de IDE Recomendada

#### VSCode

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": [
    "--strict"
  ],
  "python.linting.enabled": true
}
```

#### PyCharm

- Settings → Project → Python Interpreter
- Enable Code Inspections → Python
- Activate "Type checker" inspection

---

---

## 🧪 Testing

Scavengr mantiene una suite de tests completa con **51 tests** (44% coverage) que garantizan la calidad del código.

### Ejecutar Tests

```bash
# Suite completa
pytest

# Con verbosidad
pytest -v

# Con output detallado
pytest -v --tb=short

# Tests específicos por archivo
pytest tests/unit/test_entities.py
pytest tests/integration/test_dictionary_usecase.py

# Tests específicos por nombre
pytest -k "test_column"
pytest -k "test_sensitivity"

# Tests con debugging
pytest -vv -s --tb=long
```

### Coverage

```bash
# Generar reporte de cobertura
pytest --cov=scavengr --cov-report=term-missing

# Reporte HTML detallado
pytest --cov=scavengr --cov-report=html
# Abrir: htmlcov/index.html en navegador

# Coverage mínimo requerido (CI/CD)
pytest --cov=scavengr --cov-fail-under=44
```

### Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas
├── unit/                    # Tests unitarios (33 tests)
│   ├── test_entities.py     # 11 tests - Entidades core
│   ├── test_validators.py   # 12 tests - Validadores utils
│   ├── test_description_generator.py  # 6 tests
│   ├── test_regex_inference.py        # 7 tests
│   └── test_sensitivity_analyzer.py   # 7 tests
└── integration/             # Tests integración (8 tests)
    ├── test_dictionary_usecase.py  # 4 tests
    └── test_validate_usecase.py    # 4 tests
```

### Escribir Nuevos Tests

#### Test Unitario Básico

```python
def test_column_entity_creation():
    """Test creación básica de columna."""
    column = Column(
        name="user_id",
        type="integer",
        nullable=False,
        primary_key=True
    )
    assert column.name == "user_id"
    assert column.primary_key is True
```

#### Test con Fixtures

```python
def test_sensitivity_analysis(mock_sensitive_column):
    """Test análisis de sensibilidad usando fixture."""
    service = SensitivityAnalyzerService()
    result = service.analyze_column(mock_sensitive_column)
    
    assert result["nivel"] == "CRÍTICO"
    assert "datos personales" in result["razon"]
```

#### Test de Integración

```python
def test_dictionary_generation_excel(tmp_path):
    """Test generación completa de diccionario Excel."""
    # Preparar
    input_file = "tests/fixtures/schema.dbml"
    output_file = tmp_path / "dictionary.xlsx"
    
    # Ejecutar
    use_case = GenerateDictionary()
    result = use_case.execute(input_file, str(output_file))
    
    # Validar
    assert result.success is True
    assert output_file.exists()
    assert output_file.stat().st_size > 0
```

### Fixtures Disponibles

```python
# En conftest.py
@pytest.fixture
def mock_database_schema():
    """Esquema completo con 2 tablas y relación."""
    
@pytest.fixture
def mock_simple_column():
    """Columna email básica."""
    
@pytest.fixture
def mock_sensitive_column():
    """Columna SSN (dato sensible)."""
    
@pytest.fixture
def mock_payment_column():
    """Columna tarjeta de crédito."""
```

### Validación Completa Pre-Push

```bash
# Suite completa: Tests + Type checking + Linting
pytest -v && \
python -m mypy scavengr/ --strict && \
python -m flake8 scavengr/ && \
python -m black --check scavengr/ && \
python -m isort --check-only scavengr/

# O usar pre-commit
pre-commit run --all-files
```

### Métricas de Calidad

| Métrica              | Valor Actual | Target   | Estado |
| -------------------- | ------------ | -------- | ------ |
| **Tests Totales**    | 51           | 100+     | 🟡     |
| **Coverage Global**  | 44%          | 80%      | 🔴     |
| **Coverage Core**    | 100%         | 100%     | ✅     |
| **MyPy Errors**      | 0            | 0        | ✅     |
| **Flake8 Warnings**  | 0            | 0        | ✅     |
| **Tests Passing**    | 51/51        | 100%     | ✅     |

---

## 🤝 Contributing

### Guía Rápida para Contribuir

Scavengr acepta contribuciones siguiendo estos principios:

1. **Clean Architecture**: Mantener separación de capas
2. **Type Hints Completos**: 100% de cobertura de tipos
3. **Tests Requeridos**: Coverage mínimo 80% para código nuevo
4. **Docstrings Google Style**: Documentación clara
5. **Pre-commit Hooks**: Formateo y validación automática

### Setup Inicial

```bash
# 1. Fork del repositorio en GitHub
# 2. Clonar tu fork
git clone https://github.com/TU_USUARIO/Scavengr.git
cd Scavengr

# 3. Crear entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate  # Linux/Mac

# 4. Instalar en modo desarrollo
pip install -e ".[dev]"

# 5. Configurar pre-commit hooks
pre-commit install
```

### Workflow de Contribución

#### 1. Crear Branch

```bash
# Feature nueva
git checkout -b feature/agregar-soporte-oracle

# Bug fix
git checkout -b fix/corregir-parsing-indices-mysql

# Documentación
git checkout -b docs/actualizar-guia-instalacion
```

#### 2. Hacer Cambios

**Código nuevo debe incluir:**

- ✅ Type hints completos
- ✅ Docstrings Google style
- ✅ Tests unitarios (coverage >80%)
- ✅ Tests de integración si aplica
- ✅ Actualizar documentación

**Ejemplo de código bien documentado:**

```python
from typing import Dict, List, Optional
from scavengr.core.entities import DatabaseSchema

def extract_metadata(
    connection: DatabaseConnector,
    schema_filter: Optional[str] = None
) -> DatabaseSchema:
    """Extrae metadatos completos de la base de datos.
    
    Args:
        connection: Conexión activa a la base de datos.
        schema_filter: Filtro opcional para esquemas específicos.
        
    Returns:
        DatabaseSchema con tablas, columnas y relaciones.
        
    Raises:
        DatabaseConnectionError: Si la conexión falla.
        ValidationError: Si el schema_filter es inválido.
        
    Example:
        >>> connector = PostgreSQLConnector(config)
        >>> schema = extract_metadata(connector, "public")
        >>> print(len(schema.tables))
        42
    """
    pass
```

#### 3. Validar Localmente

```bash
# Ejecutar tests
pytest -v

# Validar coverage
pytest --cov=scavengr --cov-report=term-missing

# Type checking
python -m mypy scavengr/ --strict

# Linting
python -m flake8 scavengr/

# Formateo
python -m black scavengr/ tests/
python -m isort scavengr/ tests/

# O ejecutar pre-commit
pre-commit run --all-files
```

#### 4. Commit con Conventional Commits

```bash
# Feature
git commit -m "feat: Agregar soporte para Oracle Database"

# Bug fix
git commit -m "fix: Corregir parsing de índices compuestos en MySQL"

# Documentación
git commit -m "docs: Actualizar guía de instalación con Oracle"

# Tests
git commit -m "test: Agregar tests para OracleScanner"

# Refactoring
git commit -m "refactor: Extraer lógica común de scanners a BaseScanner"

# Performance
git commit -m "perf: Optimizar queries de metadata en PostgreSQL"
```

**Prefijos válidos:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `style`, `ci`

#### 5. Push y Pull Request

```bash
# Push a tu fork
git push origin feature/agregar-soporte-oracle

# Crear Pull Request en GitHub con:
# - Título descriptivo
# - Descripción del cambio
# - Tests agregados/modificados
# - Screenshots si aplica
# - Referencia a issues (#123)
```

### Code Style

#### Pre-commit Hooks

Los hooks se ejecutan automáticamente en cada commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black  # Formateo automático
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort  # Ordenamiento imports
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8  # Linting
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

```bash
# Ejecutar manualmente
pre-commit run --all-files

# Actualizar hooks
pre-commit autoupdate

# Skip hooks (solo en emergencias)
git commit --no-verify -m "mensaje"
```

#### Convenciones de Código

- **PEP 8**: Estilo general de Python
- **Line length**: 88 caracteres (Black default)
- **Type hints**: Obligatorios en todas las funciones públicas
- **Docstrings**: Google style para módulos, clases, funciones
- **Imports**: Ordenados con isort (stdlib, third-party, local)

### Arquitectura y Principios

#### Clean Architecture

```text
scavengr/
├── core/              # ⚠️ Sin dependencias externas
│   ├── entities.py    # Entidades de dominio puras
│   ├── interfaces.py  # Contratos (ABC)
│   └── services.py    # Lógica de negocio
├── application/       # ⚠️ Depende solo de core/
│   ├── extract.py     # Casos de uso
│   ├── validate.py
│   └── dictionary.py
├── infrastructure/    # ✅ Implementa interfaces de core/
│   ├── database/      # Scanners concretos
│   ├── parsers/       # Parser DBML
│   └── exporters/     # Excel, JSON, CSV
└── cli.py            # ✅ Orquesta application/
```

#### Principios SOLID

- **SRP**: Una responsabilidad por clase
- **OCP**: Abierto a extensión, cerrado a modificación
- **LSP**: Subtipos deben ser sustituibles
- **ISP**: Interfaces segregadas
- **DIP**: Depender de abstracciones

#### Ejemplo: Agregar Nuevo Motor de BD

```python
# 1. Implementar interfaz DatabaseScanner (infrastructure/database/)
class OracleScanner(DatabaseScanner):
    """Scanner para Oracle Database."""
    
    def scan_schema(self) -> DatabaseSchema:
        """Implementación específica Oracle."""
        pass

# 2. Agregar tipo en utils/constants.py
class DatabaseTypes:
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MSSQL = "mssql"
    ORACLE = "oracle"  # Nuevo

# 3. Registrar en connector.py
def _create_scanner(self) -> DatabaseScanner:
    if self.db_type == DatabaseTypes.ORACLE:
        return OracleScanner(self.connection)
    # ...

# 4. Agregar tests
def test_oracle_scanner():
    """Test extracción Oracle."""
    pass
```

### Checklist Pre-Pull Request

- [ ] **Tests pasan**: `pytest -v` (51/51 passing)
- [ ] **Coverage >80%**: `pytest --cov=scavengr` (nuevo código)
- [ ] **MyPy strict**: `mypy scavengr/ --strict` (0 errores)
- [ ] **Flake8 limpio**: `flake8 scavengr/` (0 warnings)
- [ ] **Black formateado**: `black scavengr/ tests/`
- [ ] **Isort ordenado**: `isort scavengr/ tests/`
- [ ] **Pre-commit pasa**: `pre-commit run --all-files`
- [ ] **Documentación actualizada**: README, docs/, docstrings
- [ ] **CHANGELOG actualizado**: Si aplica (features, fixes)
- [ ] **Commits descriptivos**: Conventional commits
- [ ] **Branch actualizado**: `git pull origin main`

### Reportar Bugs

Usa [GitHub Issues](https://github.com/JasRockr/Scavengr/issues) incluyendo:

```markdown
**Descripción del Bug**
Descripción clara del problema.

**Pasos para Reproducir**
1. Ejecutar `scavengr extract -o schema.dbml`
2. Error en línea X

**Comportamiento Esperado**
Debería generar archivo DBML correctamente.

**Comportamiento Actual**
Arroja DatabaseConnectionError.

**Entorno**
- OS: Windows 11
- Python: 3.10.5
- Scavengr: 0.0.4.dev1
- Motor BD: PostgreSQL 14.2

**Logs/Screenshots**
```
DatabaseConnectionError: Failed to connect to localhost:5432
```
```

### Proponer Features

1. **Abrir Issue** describiendo:
   - Problema que resuelve
   - Solución propuesta
   - Casos de uso
2. **Discutir** con el equipo antes de implementar
3. **Implementar** siguiendo workflow de contribución
4. **Documentar** en README y docs/

### Recursos Adicionales

- **Documentación completa**: [scavengr.jsonrivera.dev/docs](https://scavengr.jsonrivera.dev/docs/)
- **Guía de contribución detallada**: [docs/contributing.md](https://scavengr.jsonrivera.dev/docs/contributing/)
- **Arquitectura**: [README.md - Sección Arquitectura](#-arquitectura)
- **API Reference**: [docs/api/](https://scavengr.jsonrivera.dev/docs/api/)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes, consulta la [Guía de Contribución](#-contributing) completa.

**Quick start**:

1. Fork del repositorio
2. Crea branch: `git checkout -b feature/AmazingFeature`
3. Commit cambios: `git commit -m 'feat: Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Abre Pull Request

**Más información**: Ver sección [Contributing](#-contributing) para guía completa.

---

## 📝 Roadmap

### v0.1.0

- [ - ] Reportes más detallados
- [ - ] Optimizaciones
- [ - ] CLI interactivo
- [ - ] API REST

---

## 📞 Soporte

- 🐛 **Reportar Issues**: [GitHub Issues](https://github.com/JasRockr/Scavengr/issues)
- 💬 **Preguntas**: [GitHub Discussions](https://github.com/JasRockr/Scavengr/discussions)
- 📧 **Contacto**: [jsonrivera@proton.me](mailto:jsonrivera@proton.me)

---

## 📄 Licencia

**Licencia**: MIT License - Ver [LICENSE](LICENSE) para detalles completos

**Autor**: Jason Rivera (@JasRockr)  
**Repositorio**: [https://github.com/JasRockr/Scavengr](https://github.com/JasRockr/Scavengr)

---

## 🙏 Agradecimientos

- **dbdiagram.io**: Por el estándar DBML
- **Python Community**: Por las excelentes librerías
- **Comunidad Open Source**: Por inspiración y apoyo

---

_✨ Hecho con Python y mucho ☕ para revelar los secretos de tus bases de datos._
