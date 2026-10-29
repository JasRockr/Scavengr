# Configuración

Scavengr lee la conexión de variables de entorno o de archivos `.env`.

## Crear el archivo

```bash
scavengr init            # crea .env en el directorio actual
scavengr init --global   # crea ~/.scavengr.env
```

Si el archivo ya existe, `init` pregunta antes de sobrescribirlo. También puedes copiar [`.env.example`](https://github.com/JasRockr/Scavengr/blob/main/.env.example) del repositorio.

## Variables

| Variable | Obligatoria | Para qué sirve |
| --- | --- | --- |
| `DB_TYPE` | Sí | `postgresql`, `mysql` o `mssql` |
| `DB_HOST` | Sí | Servidor |
| `DB_NAME` | Sí | Base de datos |
| `DB_USER` | Sí | Usuario |
| `DB_PASSWORD` | Sí | Contraseña |
| `DB_PORT` | No | Puerto (5432, 3306 o 1433 por defecto) |
| `DB_DRIVER` | No | Driver ODBC de SQL Server |
| `SOURCE_SYSTEM_NAME` | No | Nombre del sistema en el diccionario (`Sistema de Base de Datos`) |
| `SOURCE_SYSTEM_VERSION` | No | Versión del sistema (`1.0`) |
| `SOURCE_ENVIRONMENT` | No | Entorno (`production`) |
| `OUTPUT_FILE_PREFIX` | No | Prefijo del archivo que genera `extract` sin `-o` (`diccionario_datos`) |

!!! warning "Puerto y driver ignorados (C1)"
    Hoy los conectores no leen `DB_PORT` ni `DB_DRIVER`: siempre usan el puerto por defecto del motor y, en SQL Server, el driver `SQL Server`. Si tu base está en otro puerto, Scavengr se conecta al puerto por defecto. Se corrige en la 0.0.5.

## Qué archivo gana

Scavengr carga, si existen y en este orden:

1. El archivo de `--env-file`.
2. `.env.local` del directorio actual.
3. `.env` del directorio actual.
4. `~/.scavengr.env`.

Cada archivo pisa los valores de los anteriores y también las variables del sistema. Por eso **gana el último que exista**, y un valor de `~/.scavengr.env` se impone a tu `--env-file` (hallazgo A1). Si tienes un archivo global, revisa a qué base te estás conectando.

En la 0.0.5 esto cambia: con `--env-file` se carga solo ese archivo, y sin él, las variables del sistema ganan a `.env.local`, este a `.env` y este al global.

## Varias bases

```bash
scavengr extract --env-file prod.env -o esquema-prod.dbml
scavengr extract --env-file dev.env -o esquema-dev.dbml
```

Mientras A1 no esté corregido, haz esto en un directorio sin `.env` ni `.env.local` y sin `~/.scavengr.env`.

## Seguridad

- No versiones los `.env`; el `.gitignore` del proyecto ya los excluye.
- En Linux/macOS, `chmod 600 .env`.
- Usa un usuario sin permisos de escritura: Scavengr solo hace consultas de lectura, pero no abre la sesión en modo de solo lectura.
- En PostgreSQL, un usuario que no es dueño de las tablas no ve sus PK ni FK en `information_schema`, y la extracción sale incompleta sin avisar (hallazgo C3).

## Si no conecta

1. Mira la línea `Variables de entorno cargadas desde:` que imprime `extract`: ahí ves qué archivos se cargaron y, por el orden de arriba, cuál ganó.
2. Confirma que el servidor responde en el puerto por defecto del motor (ver C1).
3. En SQL Server, confirma que el driver ODBC `SQL Server` está instalado.
