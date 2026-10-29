# Cómo contribuir

Gracias por el interés. Antes de un cambio grande, abre un [issue](https://github.com/JasRockr/Scavengr/issues) para conversarlo: el proyecto está en plena estabilización y el plan de cada fase está en la [auditoría técnica](https://github.com/JasRockr/Scavengr/blob/main/docs/auditoria-tecnica/README.md).

## Entorno

```bash
git clone https://github.com/<tu-usuario>/Scavengr.git
cd Scavengr
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows (PowerShell)
source .venv/bin/activate           # Linux/macOS
pip install -e ".[dev,postgres,mysql,mssql]"
pre-commit install
```

Necesitas Python 3.11 o superior. Para las pruebas contra bases reales, también Docker y Node.js.

## Pruebas

```bash
pytest tests -m "not lab" -q                                   # rápidas, con mocks
docker compose -f tests/lab/docker-compose.yml up -d --wait    # laboratorio
npm ci --prefix tests/lab                                      # @dbml/core, una vez
pytest tests/integration -m lab -q                             # contra el laboratorio
```

El laboratorio (`tests/lab`) levanta PostgreSQL 16 en el puerto 5433, MariaDB 10.11 en el 3307 y SQL Server 2022 en el 14333, con esquemas pensados para reproducir los hallazgos de la auditoría. Sus credenciales son públicas y solo sirven para el laboratorio.

Las pruebas nuevas van en `tests/unit/` o `tests/integration/`. Las que necesitan el laboratorio llevan el marcador `lab`.

## Estilo y revisiones

| Comando | En CI |
| --- | --- |
| `ruff check scavengr tests` | Bloquea: solo errores reales (sintaxis, nombres indefinidos, imports sin usar) |
| `bandit -r scavengr -ll` | Bloquea: problemas de seguridad de severidad media o alta |
| `mypy scavengr` | Informativo hasta la Fase 1 |

`pre-commit` aplica black, isort y flake8 antes de cada commit. Las líneas son de 88 caracteres y los docstrings, estilo Google: la [referencia de la API](api/core/entities.md) se genera desde ellos.

## Commits y PR

- Ramas desde `main`: `feat/…`, `fix/…`, `docs/…` o `chore/…`.
- Mensajes con [Conventional Commits](https://www.conventionalcommits.org/es/): `fix(scanner): …`, `docs: …`. Si el cambio corrige un hallazgo de la auditoría, pon su ID al final: `[C2]`.
- Cada arreglo de un hallazgo lleva primero una prueba que falla contra el laboratorio y después el arreglo.
- Para fusionar en `main` tienen que pasar los checks `test`, `lint` y `security`.
- Si cambias el comportamiento, actualiza el README, `docs/` y el CHANGELOG en el mismo PR.

## Documentación

```bash
pip install mkdocs-material "mkdocstrings[python]"
mkdocs serve        # http://127.0.0.1:8000
```

## Reportar un error

Abre un [issue](https://github.com/JasRockr/Scavengr/issues) con los pasos para reproducirlo, lo que esperabas, lo que pasó, y tu sistema operativo, versión de Python, versión de Scavengr y motor de base de datos. No pegues credenciales ni datos reales.
