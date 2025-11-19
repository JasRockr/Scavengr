# 🔐 Branch Protection Setup Guide

## Configuración Manual de Protección de Rama

GitHub Actions está configurado en el repositorio. Para proteger la rama `main`, sigue estos pasos:

### Via GitHub Web Interface

1. **Ir a Settings del Repositorio**
   - Navega a `https://github.com/JasRockr/Scavengr/settings`
   - Selecciona `Branches` en el menú lateral

2. **Add Branch Protection Rule**
   - Click en `Add rule`
   - Branch name pattern: `main`

3. **Configurar Reglas**
   - ✅ Require a pull request before merging
     - Require approvals: `1`
     - Require review from Code Owners: `optional`
   - ✅ Require status checks to pass before merging
     - Require branches to be up to date before merging: `true`
     - Select the following required status checks:
       - `test` (all matrix combinations)
       - `lint`
       - `security`
       - `build`
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

4. **Dismiss stale reviews**
   - Dismiss stale pull request approvals when new commits are pushed: `true`

5. **Save Changes**

---

## 🔄 GitHub Actions Status

### Workflows Configurados

| Workflow | Trigger | Descripción |
|----------|---------|-------------|
| **CI/CD Pipeline** (ci.yml) | Push main/develop, PR | Tests + Lint + Security + Build (orquestador) |
| **Test** (test.yml) | Invocado por CI | Pytest en 3 OS × 5 Python versions = 15 combinaciones |
| **Lint** (lint.yml) | Invocado por CI | flake8 + black + isort + mypy |
| **Security** (security.yml) | Invocado por CI | safety + bandit |
| **Docs** (docs.yml) | Push main (docs/**), workflow_dispatch | Build y deploy MkDocs a GitHub Pages |
| **Release** (release.yml) | Push tags v* | Build y publica en PyPI |

### Status Checks

- ✅ **test** - Pytest en 3 OS × 5 Python versions = 15 combinaciones
- ✅ **lint** - flake8 + black + isort + mypy (strict mode)
- ✅ **security** - safety + bandit (continue-on-error)
- ✅ **build** - Construye el paquete en main
- ✅ **docs** - Despliega documentación MkDocs a GitHub Pages

---

## 📊 Badges para README.md

```markdown
# Scavengr

![CI/CD](https://github.com/JasRockr/Scavengr/workflows/CI%2FCD%20Pipeline/badge.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://codecov.io/gh/JasRockr/Scavengr/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
```

---

## 🚀 Publishing to PyPI

### Prerequisites

1. **PyPI Account**
   - Crear cuenta en <https://pypi.org>
   - Generar API token en <https://pypi.org/manage/account/>

2. **GitHub Secret**
   - Ir a Settings → Secrets → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: Token de PyPI

3. **Version Tagging**

   ```bash
   git tag -a v0.0.4 -m "Release vX.y.z"
   git push origin v0.0.4
   ```

### Automatic Release

El workflow `release.yml` se activa automáticamente cuando se crea un tag `v*` y:

- ✅ Compila el paquete
- ✅ Sube a PyPI
- ✅ Genera artifacts

---

## 📋 Checklist de Configuración

- [ ] Rama `main` protegida
- [ ] Status checks configurados
- [ ] Require PR reviews habilitado
- [ ] PYPI_API_TOKEN en secrets
- [ ] Badges agregados a README.md
- [ ] Workflows probados exitosamente
- [ ] Documentación completada

---

## 🔍 Verificación

### Verificar que los workflows están activos

```bash
# Ver workflows disponibles
gh workflow list

# Ver últimos runs
gh run list --workflow=ci.yml

# Trigger un workflow manualmente (si es necesario)
gh workflow run ci.yml
```

### Ver resultados en GitHub

<https://github.com/JasRockr/Scavengr/actions>

---

**Última actualización:** 2025-11-13  
**Estado:** ✅ Workflows configurados y listos
