---
name: lab-check
description: Levanta el laboratorio de bases de datos de Scavengr (PostgreSQL, MariaDB, SQL Server), extrae los esquemas y valida el resultado. Úsalo después de cambiar conectores, scanners, extract, el parser o el formatter DBML.
---

# Verificación contra el laboratorio

El laboratorio (`tests/lab/`) reproduce los casos de la auditoría: `clientes` en dos esquemas, FK compuesta, FK entre esquemas, columnas camelCase, índice por expresión, tabla particionada, vista y un rol de solo lectura. Los puertos no son los por defecto, a propósito.

| Motor | Puerto | Base | Admin | Solo lectura |
| --- | --- | --- | --- | --- |
| PostgreSQL 16 | 5433 | `scv` | `postgres` / `postgres` | `lector` / `Lect0r!;x=1` |
| MariaDB 10.11 | 3307 | `scv` | `root` / `root` | `scv` / `x` |
| SQL Server 2022 | 14333 | `scv` | `sa` / `Scavengr_Lab_2026!` | `lector` / `Lect0r!;x=1` |

El `;` en la contraseña de `lector` es intencional (escape ODBC, A6).

## Pasos

1. `docker compose -f tests/lab/docker-compose.yml up -d --wait` y `npm ci --prefix tests/lab`.
2. SQL Server no ejecuta scripts al iniciar; cárgalo una vez:
   `docker compose -f tests/lab/docker-compose.yml exec -T mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "Scavengr_Lab_2026!" -i /lab/mssql.sql`
3. Extrae cada motor con la CLI (`scavengr extract --env-file <tmp>.env -o temp/lab-out/<motor>_<usuario>.dbml`), primero con el usuario de solo lectura y luego con el admin. Ejecuta desde un directorio sin `.env` para que no se mezcle otra configuración.
4. Valida cada DBML: `node tests/lab/dbmlcheck.js temp/lab-out/<archivo>.dbml`.
5. Compara con lo esperado:
   - PostgreSQL: PK en `public.clientes`, `ventas.pedidos`, `ventas.items(pedido_id, linea)`, `rrhh.clientes` y `rrhh.empleados`. 4 FK: `ventas.pedidos(cliente_id) → public.clientes(id)`, `ventas.items(pedido_id) → ventas.pedidos(id)`, `ventas.items_hist(pedido_id, linea) → ventas.items(pedido_id, linea)`, `rrhh.empleados(cliente_codigo) → rrhh.clientes(codigo)`. Índice `idx_ped_lower` con su expresión.
   - SQL Server: las mismas 4 FK, con `dbo.clientes` en lugar de `public.clientes`; 5 tablas con PK.
   - MariaDB: 3 FK (con la compuesta de `items_hist`); `pedidos.idx_cli_estado` = `(cliente_id, estado)` no único; `clientes.email varchar(255)`, `saldo decimal(12,2)`.
   - Todos: el usuario de solo lectura da lo mismo que el admin, o una advertencia explícita. Ninguna columna se pierde entre `extract` y `dictionary`.
   - Fuera de la Fase 0 (M2): `public.eventos` como tabla padre particionada y los comentarios.
6. Reporta una tabla motor | usuario | tablas | PK | FK | DBML válido | diferencias.

No borres volúmenes ni modifiques los scripts del laboratorio para que una prueba pase.
