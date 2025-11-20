# Comandos CLI

Referencia completa de todos los comandos disponibles en Scavengr.

---

## `scavengr init`

Crea archivo de configuración `.env` interactivo.

### Sintaxis

```bash
scavengr init [OPTIONS]
```

### Opciones

| Opción      | Descripción                            | Valor por Defecto |
|-------------|----------------------------------------|-------------------|
| `--global`  | Crear configuración global en `~/.scavengr.env` | `false`  |
| `--help`    | Mostrar ayuda                          | -                 |

### Ejemplos

```bash
# Configuración local
scavengr init

# Configuración global
scavengr init --global
```

---

## `scavengr extract`

Extrae metadatos de base de datos y genera archivo DBML.

### Sintaxis

```bash
scavengr extract -o OUTPUT [OPTIONS]
```

### Opciones

| Opción            | Descripción                    | Requerido |
|-------------------|--------------------------------|-----------|
| `-o, --output`    | Archivo DBML de salida         | ✅ Sí     |
| `--env-file`      | Archivo de configuración       | ❌ No     |
| `--cache`         | Habilitar caché de metadatos   | ❌ No     |
| `--force-refresh` | Invalidar caché y reextraer    | ❌ No     |
| `--help`          | Mostrar ayuda                  | -         |

### Ejemplos

```bash
# Extracción básica
scavengr extract -o schema.dbml

# Con configuración específica
scavengr extract -o schema.dbml --env-file prod.env

# Con caché habilitado (primera vez: crea caché)
scavengr extract --cache -o schema.dbml

# Usando caché (subsecuentes: ~90% más rápido)
scavengr extract --cache -o schema.dbml

# Forzar actualización de caché (si BD cambió)
scavengr extract --cache --force-refresh -o schema.dbml

# Ruta completa
scavengr extract -o /ruta/completa/mi-esquema.dbml
```

### Sistema de Caché

**Características:**
- **Serialización**: Pickle (rápido) o JSON (portable)
- **TTL**: 24 horas por defecto (configurable)
- **Ubicación**: `.scavengr_cache/` (auto-creado, ignorado por git)
- **Rendimiento**: ~90% reducción en tiempo de extracciones subsecuentes
- **Gestión**: Expiración automática basada en TTL

**Uso:**
```bash
# Primera extracción (crea caché)
scavengr extract --cache -o schema.dbml
# Tiempo: ~30 segundos

# Subsecuentes (usa caché)
scavengr extract --cache -o schema.dbml
# Tiempo: ~3 segundos (90% más rápido)

# Si la BD cambió, forzar actualización
scavengr extract --cache --force-refresh -o schema.dbml
```

### Salida

Archivo DBML con:

- ✅ Tablas y columnas
- ✅ Tipos de datos
- ✅ Primary keys y foreign keys
- ✅ Índices con columnas
- ✅ Valores por defecto
- ✅ Relaciones entre tablas

---

## `scavengr validate`

Valida sintaxis y estructura de archivos DBML.

### Sintaxis

```bash
scavengr validate -i INPUT [OPTIONS]
```

### Opciones

| Opción            | Descripción                    | Requerido |
|-------------------|--------------------------------|-----------|
| `-i, --input`     | Archivo DBML a validar         | ✅ Sí     |
| `--help`          | Mostrar ayuda                  | -         |

### Ejemplos

```bash
# Validación básica
scavengr validate -i schema.dbml

# Ruta completa
scavengr validate -i /ruta/completa/mi-esquema.dbml
```

### Validaciones

- **Básicas**: Existencia de archivo, sintaxis DBML
- **Estructura**: Tablas, columnas, relaciones
- **Integridad**: Referencias entre tablas
- **Calidad**: CamelCase, tipos con espacios, índices vacíos

### Salida

```text
✅ VALIDACIONES BÁSICAS: OK
   - Archivo: Existe y se puede leer
   - Sintaxis DBML: Correcta

⚠️  VALIDACIONES DE CALIDAD: 5 ADVERTENCIAS
   [MySQL] 2 índices BTREE sin columnas → Serán inferidas
   [PostgreSQL] 3 identificadores CamelCase → Serán escapados

✅ RESULTADO: Esquema procesable
```

---

## `scavengr dictionary`

Genera diccionario de datos en Excel, CSV o JSON.

### Sintaxis

```bash
scavengr dictionary -i INPUT -o OUTPUT [OPTIONS]
```

### Opciones

| Opción            | Descripción                      | Requerido |
|-------------------|----------------------------------|-----------|
| `-i, --input`     | Archivo DBML de entrada          | ✅ Sí     |
| `-o, --output`    | Archivo de salida                | ✅ Sí     |
| `-f, --format`    | Formato (`excel`, `csv`, `json`) | ❌ No     |
| `--help`          | Mostrar ayuda                    | -         |

### Ejemplos

```bash
# Excel (detecta por extensión)
scavengr dictionary -i schema.dbml -o diccionario.xlsx

# CSV
scavengr dictionary -i schema.dbml -o diccionario.csv

# JSON
scavengr dictionary -i schema.dbml -o diccionario.json

# Forzar formato
scavengr dictionary -i schema.dbml -o output.txt -f excel
```

### Campos del Diccionario

| Campo                   | Descripción                               |
|-------------------------|-------------------------------------------|
| Tabla                   | Nombre de la tabla                        |
| Columna                 | Nombre de la columna                      |
| Tipo de Dato            | Tipo nativo de BD                         |
| Tamaño                  | Longitud/precisión                        |
| Nullable                | Permite valores NULL                      |
| Primary Key             | Es clave primaria                         |
| Foreign Key             | Referencia a otra tabla                   |
| Default                 | Valor por defecto                         |
| Descripción             | Generada automáticamente (80+ patrones)   |
| Sensibilidad            | CRÍTICO, ALTO, MEDIO, BAJO                |
| Máscara Sugerida        | Para datos sensibles                      |
| Observaciones           | Warnings y recomendaciones                |
| Ejemplo                 | Valores de ejemplo                        |
| Formato Regex           | Patrón de validación                      |
| **+ 5 campos más**      | Índices, relaciones, estadísticas         |

---

## `scavengr report`

Genera reporte analítico con métricas de calidad.

### Sintaxis

```bash
scavengr report -i INPUT -o OUTPUT [OPTIONS]
```

### Opciones

| Opción            | Descripción                      | Requerido |
|-------------------|----------------------------------|-----------|
| `-i, --input`     | Archivo DBML de entrada          | ✅ Sí     |
| `-o, --output`    | Archivo de salida                | ✅ Sí     |
| `-f, --format`    | Formato (`excel`, `json`)        | ❌ No     |
| `--help`          | Mostrar ayuda                    | -         |

### Ejemplos

```bash
# Excel
scavengr report -i schema.dbml -o reporte.xlsx

# JSON
scavengr report -i schema.dbml -o reporte.json
```

### Contenido del Reporte

**5 hojas en Excel:**

1. **Resumen Ejecutivo**
   - Score de calidad global
   - Métricas principales
   - Top 10 tablas

2. **Análisis de Calidad**
   - 7 dimensiones evaluadas
   - Normalization Score
   - Naming Conventions
   - Data Types Consistency
   - Relationships Integrity
   - Indexing Strategy
   - Sensitive Data Handling
   - Documentation Level

3. **Estadísticas**
   - Distribución de tipos de datos
   - Tamaños de tablas
   - Cardinalidad de relaciones

4. **Sensibilidad**
   - Campos críticos y protegidos
   - Distribución por nivel
   - Recomendaciones de seguridad

5. **Recomendaciones**
   - Mejoras priorizadas
   - Impacto estimado
   - Esfuerzo requerido

---

## Opciones Globales

Disponibles para todos los comandos:

```bash
scavengr --version  # Ver versión
scavengr --help     # Ayuda general
```

---

## Ejemplos de Flujo Completo

### Flujo Básico

```bash
# 1. Configurar
scavengr init

# 2. Extraer
scavengr extract -o schema.dbml

# 3. Validar
scavengr validate -i schema.dbml

# 4. Documentar
scavengr dictionary -i schema.dbml -o diccionario.xlsx

# 5. Analizar
scavengr report -i schema.dbml -o reporte.xlsx
```

### Múltiples Bases de Datos

```bash
# Producción
scavengr extract --env-file prod.env -o schema-prod.dbml
scavengr dictionary -i schema-prod.dbml -o dict-prod.xlsx

# Desarrollo
scavengr extract --env-file dev.env -o schema-dev.dbml
scavengr dictionary -i schema-dev.dbml -o dict-dev.xlsx
```

### CI/CD Integration

```bash
# Extraer en pipeline
scavengr extract -o schema.dbml --env-file ci.env

# Validar en PR
scavengr validate -i schema.dbml || exit 1

# Generar artefactos
scavengr dictionary -i schema.dbml -o artifacts/dictionary.xlsx
scavengr report -i schema.dbml -o artifacts/report.xlsx
```
