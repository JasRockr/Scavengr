"""Comprueba que el laboratorio está montado como esperan las pruebas de la Fase 0.

No usa Scavengr: si algo falla aquí, el problema es del laboratorio o del entorno de CI.
"""

import pytest

pytestmark = pytest.mark.lab

TABLAS = {
    "postgres": (
        "SELECT table_schema || '.' || table_name FROM information_schema.tables "
        "WHERE table_schema IN ('public', 'ventas', 'rrhh') AND table_type = 'BASE TABLE'",
        {"public.clientes", "public.eventos", "public.eventos_2026", "ventas.pedidos", "ventas.items",
         "ventas.items_hist", "rrhh.clientes", "rrhh.empleados"},
    ),
    "mariadb": (
        "SELECT CONCAT(table_schema, '.', table_name) FROM information_schema.tables "
        "WHERE table_schema = 'scv'",
        {"scv.clientes", "scv.pedidos", "scv.items", "scv.items_hist"},
    ),
    "mssql": (
        "SELECT s.name + '.' + t.name FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id",
        {"dbo.clientes", "ventas.pedidos", "ventas.items", "ventas.items_hist", "rrhh.clientes",
         "rrhh.empleados"},
    ),
}


@pytest.mark.parametrize("engine", list(TABLAS))
@pytest.mark.parametrize("user", ["admin", "lector"])
def test_tablas_del_laboratorio(lab_connect, engine, user):
    query, esperadas = TABLAS[engine]
    cur = lab_connect(engine, user).cursor()
    cur.execute(query)
    assert {row[0] for row in cur.fetchall()} == esperadas


def test_validador_dbml(dbml_check):
    valido = dbml_check("Table a {\n  id int [pk]\n}\nTable b {\n  a_id int [ref: > a.id]\n}\n")
    invalido = dbml_check("Table a {\n  id int\n  indexes {\n    () [name: 'vacio']\n  }\n}\n")
    assert valido["valid"], valido["output"]
    assert not invalido["valid"], invalido["output"]
