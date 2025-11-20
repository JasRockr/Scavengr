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

---

## 🚀 Características Principales

### 🔍 Extracción de Metadatos

- **Múltiples motores**: PostgreSQL, MySQL/MariaDB y SQL Server
- **Extracción completa**: Tablas, columnas, tipos de datos, relaciones, índices
- **Formato DBML**: Compatible con [dbdiagram.io](https://dbdiagram.io)
- **Configuración simple**: Archivo `.env` para credenciales

### 📊 Diccionarios de Datos

- **Formato Excel**: 19 campos especializados por columna
- **Análisis de sensibilidad**: Clasificación automática
- **Descripciones inteligentes**: 80+ patrones de detección
- **Observaciones contextuales**: Warnings y recomendaciones

### ✅ Validación de Esquemas

- **Validación exhaustiva**: Sintaxis, estructura y consistencia
- **Detección de errores**: Tablas, relaciones, claves
- **Análisis de integridad**: Referencias y relaciones
- **Validaciones de calidad**: CamelCase, tipos, índices

### 📈 Reportes Analíticos

- **Score de calidad**: 7 dimensiones evaluadas
- **Análisis estadístico**: Tipos, tamaños, relaciones
- **Recomendaciones**: Priorizadas por impacto
- **Formato Excel**: 5 hojas detalladas

---

## ⚡ Inicio Rápido

```bash
# Instalación
pip install scavengr

# Configuración
scavengr init

# Uso básico
scavengr extract -o schema.dbml
scavengr validate -i schema.dbml
scavengr dictionary -i schema.dbml -o dict.xlsx
scavengr report -i schema.dbml -o report.xlsx
```

---

## ✨ Novedades en v0.0.4

### 🚀 Sistema de Caché de Metadatos

Extracción hasta **90% más rápida** con caché automático:

```bash
# Primera extracción (crea caché)
scavengr extract --cache -o schema.dbml

# Subsecuentes (usa caché, ~90% más rápido)
scavengr extract --cache -o schema.dbml

# Forzar actualización (si BD cambió)
scavengr extract --cache --force-refresh -o schema.dbml
```

### ✅ Suite de Tests Completa

- **282 tests** (100% passing)
- **74% coverage** global
- **100% coverage** en módulos críticos
- **0 errores mypy** (type hints completos)

### 🔍 Validaciones de Calidad Mejoradas

- Detección de índices BTREE/PRIMARY sin columnas (MySQL)
- Identificadores CamelCase escapados (PostgreSQL)
- Tipos con espacios normalizados
- Autoreferences filtradas (SQL Server)

---

## 📚 Documentación

- **[Instalación](guide/installation.md)**: Guía de instalación detallada
- **[Configuración](guide/configuration.md)**: Configuración de credenciales
- **[Comandos CLI](guide/commands.md)**: Referencia completa de comandos
- **[API Reference](api/core/entities.md)**: Documentación del código

---

## 🏗️ Arquitectura

Scavengr implementa **Clean Architecture** con separación clara:

```mermaid
graph TD
    A[CLI] --> B[Application]
    B --> C[Core]
    B --> D[Infrastructure]
    D --> E[Database]
    D --> F[Exporters]
    D --> G[Formatters]
```

- **Core**: Entidades de dominio, interfaces y servicios
- **Application**: Casos de uso (extract, validate, dictionary, report)
- **Infrastructure**: Conectores de BD, exportadores, formateadores
- **CLI**: Interfaz de línea de comandos

---

## 🤝 Contribuir

¿Quieres contribuir? Consulta nuestra [guía de contribución](contributing.md).

---

## 📝 Licencia

MIT License - ver [LICENSE](https://github.com/JasRockr/Scavengr/blob/main/LICENSE)
