# 🗃️ Scavengr

![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-alpha-orange.svg)
[![PyPI version](https://badge.fury.io/py/scavengr.svg)](https://pypi.org/project/scavengr/)

> *"Descubre lo que tus bases esconden."*

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
  --env-file PATH          Archivo .env específico a usar (default: .env)
  --help                   Mostrar ayuda
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

## 🛡️ Seguridad y Permisos

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

> Algunos casos de uso continuan en desarrollo y requieren  extenderse para cobertura completa.

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

| Tabla | Columna | Tipo | Sensibilidad | Descripción |
|-------|---------|------|--------------|-------------|
| usuarios | email | varchar(255) | CRÍTICO | Correo electrónico del usuario |
| usuarios | nombre | varchar(100) | ALTO | Nombre completo del usuario |
| departamentos | nombre | varchar(100) | BAJO | Nombre del departamento |

---

## 🛠️ Requisitos del Sistema

- **Python**: 3.8+ (recomendado: 3.10 o superior)
- **Sistema Operativo**: Windows, Linux, macOS
- **Memoria**: Mínimo 512MB, recomendado 2GB para esquemas grandes
- **Dependencias**: Ver `pyproject.toml` para lista completa

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Roadmap

### v0.1.0 (Q1 2026)

- [ - ] Exportación JSON y CSV para diccionarios
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

*✨ Hecho con Python y mucho ☕ para revelar los secretos de tus bases de datos.*
