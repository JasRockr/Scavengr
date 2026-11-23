# Comandos

Opciones globales, antes del comando:

| Opción | Qué hace |
| --- | --- |
| `-v`, `--version` | Muestra la versión |
| `--verbose` | Activa el detalle de depuración |
| `-h`, `--help` | Muestra la ayuda; `scavengr <comando> --help` la de cada comando |

## `init`

Crea el archivo `.env` con la plantilla de configuración. Si ya existe, pregunta antes de sobrescribirlo.

| Opción | Qué hace |
| --- | --- |
| `--global` | Lo crea en `~/.scavengr.env` en vez del directorio actual |

## `extract`

Lee tablas, columnas, tipos, PK, FK e índices de la base configurada y escribe un archivo DBML que se puede abrir en [dbdiagram.io](https://dbdiagram.io).

| Opción | Qué hace |
| --- | --- |
| `-o`, `--output` | Archivo de salida. Sin esta opción usa `<OUTPUT_FILE_PREFIX>_extracted.dbml` |
| `--env-file` | Archivo `.env` que quieres usar. Hoy lo pisan los otros `.env` (ver [Configuración](configuration.md#que-archivo-gana)) |
| `--cache` | Guarda los metadatos y los reutiliza durante 24 horas |
| `--force-refresh` | Con `--cache`, descarta lo guardado y vuelve a leer la base |

```bash
scavengr extract -o esquema.dbml
scavengr extract --env-file prod.env -o esquema-prod.dbml
scavengr extract --cache -o esquema.dbml
scavengr extract --cache --force-refresh -o esquema.dbml
```

La caché se guarda con pickle en `.scavengr_cache/`, dentro del directorio actual, y vence a las 24 horas. Su clave sale del tipo de base, el host y el nombre de la base; no incluye el puerto ni el usuario, así que dos usuarios con permisos distintos sobre la misma base comparten la caché (hallazgo M3).

!!! warning "Limitaciones conocidas"
    Se ignoran `DB_PORT` y `DB_DRIVER` (C1). En PostgreSQL, las llaves foráneas pueden salir sin esquema, repetidas o con el esquema equivocado (C2), y un usuario que no es dueño de las tablas no ve PK ni FK (C3). Los índices se asocian a la tabla por nombre, sin esquema (A2). Todo esto se corrige en la 0.0.5.

## `validate`

Revisa un archivo DBML.

| Opción | Qué hace |
| --- | --- |
| `-i`, `--input` | Archivo DBML |

Comprueba que:

- el archivo exista y se pueda parsear;
- haya tablas, que cada una tenga columnas y PK;
- cada relación apunte a una tabla y una columna que existen.

También avisa de patrones típicos de cada motor: índices de MySQL sin columnas, identificadores camelCase y tipos con espacios en PostgreSQL, y referencias de una columna a sí misma en SQL Server.

Las tablas sin PK y los patrones de cada motor son advertencias; el comando termina bien aunque las haya. No es una validación completa del formato DBML: puede aprobar archivos que el parser oficial rechaza (A4).

## `dictionary`

Genera el diccionario de datos: una fila por columna.

| Opción | Qué hace |
| --- | --- |
| `-i`, `--input` | Archivo DBML |
| `-o`, `--output` | Archivo de salida |
| `-f`, `--format` | `excel`, `csv` o `json`. Sin esta opción sale de la extensión: `.xlsx`/`.xls`, `.csv` o `.json` |

```bash
scavengr dictionary -i esquema.dbml -o diccionario.xlsx
scavengr dictionary -i esquema.dbml -o diccionario.csv
scavengr dictionary -i esquema.dbml -o salida.txt -f json
```

Los 19 campos de cada fila:

| Campo | Contenido |
| --- | --- |
| `TABLA`, `NOMBRE_DATO` | Tabla (con esquema) y columna |
| `TIPO_DE_DATO`, `LONGITUD` | Tipo y longitud o precisión |
| `DESCRIPCION` | Descripción generada a partir del nombre |
| `REGEX`, `MASCARA` | Patrón de validación sugerido y máscara para ocultar el dato |
| `CRITERIOS_CALIDAD` | Reglas de calidad sugeridas |
| `TABLA_MAESTRA`, `CAMPO_MAESTRO`, `TIPO_RELACION` | A qué tabla y columna apunta, si es FK |
| `ES_MAESTRA`, `ES_PK`, `ES_NULLABLE` | Si la tabla es maestra, si la columna es PK y si acepta nulos |
| `EJEMPLOS_VALIDOS` | Valores de ejemplo inventados, no leídos de la base |
| `FUENTE_CAPTURA`, `MODULO` | Sistema de origen y módulo funcional estimado |
| `SENSIBILIDAD` | `BAJO`, `MEDIO`, `ALTO` o `CRÍTICO` |
| `OBSERVACIONES` | Advertencias y recomendaciones |

La sensibilidad se decide por el nombre de la columna; Scavengr no lee los datos. Hoy detecta pocas columnas con datos personales y marca algunas que no lo son (C5). Además, se pierden las columnas camelCase que el DBML escribe entre comillas (C4).

## `report`

Genera un informe de calidad del esquema.

| Opción | Qué hace |
| --- | --- |
| `-i`, `--input` | Archivo DBML |
| `-o`, `--output` | Archivo de salida: `.xlsx` para Excel; cualquier otra extensión, JSON |

```bash
scavengr report -i esquema.dbml -o informe.xlsx
scavengr report -i esquema.dbml -o informe.json
```

Contenido:

- **Resumen General:** tablas, columnas, relaciones, PK, FK, nulos.
- **Calidad de Datos:** puntuación general y por dimensión (completitud, integridad referencial, consistencia de nombres y documentación).
- **Tipos de Datos:** los tipos más usados y su distribución por categoría.
- **Seguridad:** distribución de sensibilidad y campos críticos.
- **Recomendaciones.**

En Excel, cada punto es una hoja. El JSON trae además el análisis de relaciones y de normalización. No hay salida CSV: con `-o informe.csv` el archivo se escribe en JSON.

## Flujo completo

```bash
scavengr init
scavengr extract -o esquema.dbml
scavengr validate -i esquema.dbml
scavengr dictionary -i esquema.dbml -o diccionario.xlsx
scavengr report -i esquema.dbml -o informe.xlsx
```
