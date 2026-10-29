# Protección de `main`

`main` está protegida con el ruleset **`deploy-main`** (Settings → Rules → Rulesets). Estas son sus reglas:

| Regla | Efecto |
| --- | --- |
| Restrict deletions | No se puede borrar `main` |
| Block force pushes | No se puede reescribir su historial |
| Require status checks to pass | Para actualizar `main` tienen que pasar `test`, `lint` y `security`, sobre una rama al día con `main` |

El ruleset no exige PR ni aprobaciones, pero un push directo también tiene que pasar los tres checks. El rol de administrador del repositorio está en la lista de bypass.

## Los checks

Los tres salen de `.github/workflows/ci.yml`, que corre en cada PR, en cada push a `main` y a mano (`workflow_dispatch`):

| Check | Qué revisa |
| --- | --- |
| `lint` | `ruff check scavengr tests` con las reglas de errores reales de `pyproject.toml`. El informe de estilo y mypy se muestra, pero no bloquea |
| `security` | `bandit -r scavengr -ll` y `pip-audit` sobre las dependencias instaladas |
| `test` | Pasa solo si pasaron todas las combinaciones de `unit` (Python 3.11–3.14 en Ubuntu y 3.14 en Windows) y de `lab` (Python 3.11 y 3.14 contra el laboratorio de `tests/lab`) |

Si se agrega, quita o renombra un job de `ci.yml`, hay que revisar que estos nombres sigan coincidiendo con los del ruleset; si no, ningún PR se podrá fusionar.

## Consultar el ruleset

```bash
gh api repos/JasRockr/Scavengr/rulesets
gh api repos/JasRockr/Scavengr/rulesets/<id>
```

## Publicar en PyPI

No hay workflow de publicación. Las versiones se publican a mano con `scripts/publish.ps1` (ver [scripts/README.md](../scripts/README.md)).
