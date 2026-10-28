# Configuración

## Archivo de Configuración

Scavengr usa archivos `.env` para almacenar credenciales de base de datos.

---

## Métodos de Configuración

### 1. Configuración Rápida (Recomendado)

```bash
# Crear configuración local
scavengr init

# Crear configuración global
scavengr init --global
```

### 2. Configuración Manual

```bash
# Copiar ejemplo
cp .env.example .env

# O crear desde cero
cat > .env << EOF
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mi_base_datos
DB_USER=usuario_lectura
DB_PASSWORD=contraseña_segura
EOF
```

---

## Prioridad de Configuración

Scavengr busca configuración en este orden:

1. **Archivo específico**: `--env-file mi-config.env`
2. **Directorio actual**: `.env.local` → `.env`
3. **Configuración global**: `~/.scavengr.env`
4. **Variables de entorno**: `export DB_TYPE=postgresql`

---

## Parámetros de Configuración

### Obligatorios

| Parámetro       | Descripción                      | Ejemplo              |
|-----------------|----------------------------------|----------------------|
| `DB_TYPE`       | Tipo de motor                    | `postgresql`         |
| `DB_HOST`       | Host del servidor                | `localhost`          |
| `DB_NAME`       | Nombre de la base de datos       | `mi_base_datos`      |
| `DB_USER`       | Usuario de BD                    | `usuario_lectura`    |
| `DB_PASSWORD`   | Contraseña                       | `contraseña_segura`  |

### Opcionales

| Parámetro       | Descripción                      | Valor por Defecto    |
|-----------------|----------------------------------|----------------------|
| `DB_PORT`       | Puerto del servidor              | `5432` (PostgreSQL)  |
| `DB_DRIVER`     | Driver ODBC (solo SQL Server)    | `SQL Server`         |
| `DB_SCHEMA`     | Esquema específico (PostgreSQL)  | `public`             |

---

## Tipos de Base de Datos

### PostgreSQL

```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mi_db
DB_USER=postgres
DB_PASSWORD=secret
DB_SCHEMA=public  # Opcional
```

### MySQL/MariaDB

```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mi_db
DB_USER=root
DB_PASSWORD=secret
```

### SQL Server

```bash
DB_TYPE=mssql
DB_HOST=localhost
DB_PORT=1433
DB_NAME=mi_db
DB_USER=sa
DB_PASSWORD=secret
DB_DRIVER="SQL Server"  # Opcional
```

---

## Seguridad

!!! warning "Protección de Credenciales"
    - **NO versiones** archivos `.env` (ya está en `.gitignore`)
    - Usa **permisos restrictivos**: `chmod 600 .env` (Linux/Mac)
    - Considera **variables de entorno** en producción

!!! info "Permisos de BD"
    Scavengr solo necesita **permisos de lectura** en vistas del sistema:
    
    - PostgreSQL: `information_schema`, `pg_catalog`
    - MySQL: `information_schema`
    - SQL Server: `VIEW DEFINITION` o `db_datareader`

---

## Uso con Múltiples Bases de Datos

```bash
# Crear configuración por proyecto
scavengr init  # .env local

# Usar configuración específica
scavengr extract --env-file prod.env -o schema-prod.dbml
scavengr extract --env-file dev.env -o schema-dev.dbml
```

---

## Troubleshooting

### Error: "Archivo de configuración no encontrado"

```bash
# Verificar ubicación
ls -la .env

# Crear configuración
scavengr init
```

### Error: "Conexión a BD falló"

1. Verificar credenciales en `.env`
2. Verificar que el servidor esté accesible
3. Verificar permisos del usuario
4. Verificar driver instalado (SQL Server)

```bash
# Test conexión (PostgreSQL)
psql -h localhost -U usuario_lectura -d mi_db

# Test conexión (MySQL)
mysql -h localhost -u root -p mi_db
```
