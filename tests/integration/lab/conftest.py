"""Fixtures para las pruebas contra el laboratorio de bases de datos (tests/lab).

El laboratorio se levanta con `docker compose -f tests/lab/docker-compose.yml up -d`.
Si no está disponible, las pruebas se saltan en local y fallan en CI
(SCAVENGR_LAB_REQUIRED=1), para que nunca pasen en verde sin haberse ejecutado.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict

import pytest

LAB_DIR = Path(__file__).resolve().parents[2] / "lab"

# Credenciales públicas del laboratorio (las mismas de docker-compose.yml y los .sql)
LAB = {
    "postgres": {"host": "localhost", "port": 5433, "database": "scv",
                 "admin": ("postgres", "postgres"), "lector": ("lector", "Lect0r!;x=1")},
    "mariadb": {"host": "127.0.0.1", "port": 3307, "database": "scv",
                "admin": ("root", "root"), "lector": ("scv", "x")},
    "mssql": {"host": "localhost", "port": 14333, "database": "scv",
              "admin": ("sa", "Scavengr_Lab_2026!"), "lector": ("lector", "Lect0r!;x=1")},
}


def _lab_unavailable(reason: str) -> None:
    if os.environ.get("SCAVENGR_LAB_REQUIRED") == "1":
        pytest.fail(f"Laboratorio requerido y no disponible: {reason}")
    pytest.skip(f"Laboratorio no disponible: {reason}")


def _odbc_value(value: str) -> str:
    """Escapa un valor de la cadena ODBC entre llaves (el `;` de la contraseña es intencional)."""
    return "{" + value.replace("}", "}}") + "}"


def _odbc_driver() -> str:
    import pyodbc

    configured = os.environ.get("SCAVENGR_LAB_ODBC_DRIVER")
    if configured:
        return configured
    drivers = sorted(d for d in pyodbc.drivers() if d.startswith("ODBC Driver") and "SQL Server" in d)
    if not drivers:
        _lab_unavailable("no hay un driver ODBC de SQL Server instalado")
    return drivers[-1]


def _connect(engine: str, user: str) -> Any:
    cfg = LAB[engine]
    name, password = cfg[user]
    try:
        if engine == "postgres":
            import psycopg2

            return psycopg2.connect(host=cfg["host"], port=cfg["port"], dbname=cfg["database"],
                                    user=name, password=password, connect_timeout=5)
        if engine == "mariadb":
            import mysql.connector

            return mysql.connector.connect(host=cfg["host"], port=cfg["port"], database=cfg["database"],
                                           user=name, password=password, connection_timeout=5)
        import pyodbc

        conn_str = (
            f"DRIVER={{{_odbc_driver()}}};SERVER={cfg['host']},{cfg['port']};"
            f"DATABASE={cfg['database']};UID={_odbc_value(name)};PWD={_odbc_value(password)};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, timeout=5)
    except ImportError as e:
        _lab_unavailable(f"falta el driver de {engine}: {e}")
    except Exception as e:  # noqa: BLE001 - cualquier fallo de conexión significa laboratorio caído
        _lab_unavailable(f"{engine} ({user}) no responde: {e}")


@pytest.fixture
def lab_connect() -> Callable[[str, str], Any]:
    """Conexión directa al laboratorio, sin pasar por Scavengr: lab_connect("postgres", "lector")."""
    opened = []

    def factory(engine: str, user: str = "admin") -> Any:
        conn = _connect(engine, user)
        opened.append(conn)
        return conn

    yield factory
    for conn in opened:
        conn.close()


@pytest.fixture
def dbml_check(tmp_path: Path) -> Callable[[str], Dict[str, Any]]:
    """Valida DBML con @dbml/core (tests/lab/dbmlcheck.js). Requiere `npm ci --prefix tests/lab`."""
    node = shutil.which("node")
    if not node or not (LAB_DIR / "node_modules" / "@dbml" / "core").is_dir():
        _lab_unavailable("falta node o @dbml/core (npm ci --prefix tests/lab)")

    def check(dbml: str) -> Dict[str, Any]:
        path = tmp_path / "check.dbml"
        path.write_text(dbml, encoding="utf-8")
        out = subprocess.run([node, str(LAB_DIR / "dbmlcheck.js"), str(path)],
                             capture_output=True, text=True, encoding="utf-8", check=False).stdout
        return {"valid": out.startswith("VALID"), "output": out.strip()}

    return check
