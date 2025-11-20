# 📚 Arquitectura de Documentación y GitHub Pages

## 🎯 Estructura de URLs

```skeleton
https://scavengr.jsonrivera.dev/
├── /                          → Landing page (index.html)
└── /docs/                     → Documentación MkDocs
    ├── /                      → Home de la documentación
    ├── /guide/                → Guías de usuario
    │   ├── /installation/     → Instalación
    │   ├── /configuration/    → Configuración
    │   └── /commands/         → Comandos CLI
    ├── /api/                  → API Reference
    │   ├── /core/             → Entidades, Interfaces, Servicios
    │   ├── /application/      → Extract, Validate, Dictionary, Report
    │   ├── /infrastructure/   → Database, Exporters, Formatters
    │   └── /utils/            → Constants, Exceptions, Validators
    ├── /contributing/         → Guía de contribución
    └── /changelog/            → Historial de cambios
```

## 🏗️ Arquitectura

### Rama `main`

- **Código fuente**: Todo el código de Scavengr
- **`index.html`**: Landing page estático
- **`CNAME`**: scavengr.jsonrivera.dev
- **`docs/`**: Archivos Markdown para MkDocs
- **`mkdocs.yml`**: Configuración de MkDocs

### Rama `gh-pages` (Auto-generada)

```skeleton
gh-pages/
├── index.html              → Landing (copiado de main)
├── CNAME                   → Dominio personalizado (copiado de main)
└── docs/                   → Documentación (generada por MkDocs)
    ├── index.html
    ├── api/
    ├── guide/
    └── ...
```

## 🔄 Flujo de Deployment

### 1. Desarrollo Local

```bash
# Ver landing page
open index.html

# Servidor de documentación
mkdocs serve
# Visitar: http://127.0.0.1:8000

# Build de documentación
mkdocs build
# Output: site/
```

### 2. Push a `main`

Cuando haces push a `main` con cambios en:

- `docs/**`
- `mkdocs.yml`
- `scavengr/**/*.py`

**GitHub Actions** (`.github/workflows/docs.yml`) automáticamente:

1. ✅ Instala dependencias (mkdocs, mkdocstrings, mkdocs-material)
2. ✅ Instala Scavengr en modo desarrollo
3. ✅ Build de MkDocs → `site/`
4. ✅ Checkout rama `gh-pages`
5. ✅ Copia `site/` → `docs/`
6. ✅ Recupera `index.html` y `CNAME` de `main`
7. ✅ Commit y push a `gh-pages`

### 3. GitHub Pages Publica

GitHub Pages sirve automáticamente desde `gh-pages`:

- `/` → `index.html` (landing)
- `/docs/` → `docs/index.html` (documentación)

## 🎨 Componentes

### Landing Page (`index.html`)

- **Propósito**: Primera impresión, marketing
- **Características**:
  - Hero section con badges
  - Features destacadas
  - Botón "Documentación" → `/docs/`
  - Quality Assurance metrics
  - Links a GitHub, PyPI, contacto
- **Tecnología**: HTML/CSS puro, responsive

### Documentación (`docs/`)

- **Propósito**: Referencia técnica completa
- **Contenido**:
  - Guías de instalación, configuración, comandos
  - API Reference auto-generada desde docstrings
  - Guía de contribución
  - Changelog
- **Tecnología**: MkDocs + Material theme
- **Características**:
  - Búsqueda integrada
  - Modo oscuro/claro
  - Navegación con tabs
  - Code highlighting
  - Responsive

## 🚀 Comandos Útiles

```bash
# Desarrollo local
mkdocs serve              # Servidor local
mkdocs serve -a 0.0.0.0:8000  # Accesible en red

# Build
mkdocs build              # Generar site/
mkdocs build --clean      # Limpiar antes de generar

# Deploy manual (NO recomendado, usar GitHub Actions)
mkdocs gh-deploy          # Deploy directo a gh-pages
```

## 🔧 Configuración

### `mkdocs.yml`

```yaml
site_url: https://scavengr.jsonrivera.dev/docs/
# Nota: /docs/ al final es importante para rutas correctas

theme:
  name: material
  # Tema profesional con modo oscuro

plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            # Auto-genera desde docstrings
```

### GitHub Pages Settings

1. Repository → Settings → Pages
2. **Source**: Deploy from branch `gh-pages`
3. **Folder**: `/` (root)
4. **Custom domain**: scavengr.jsonrivera.dev

## 📝 Mantenimiento

### Actualizar Documentación

1. **Editar archivos Markdown** en `docs/`
2. **Verificar localmente**: `mkdocs serve`
3. **Commit y push** a `main`
4. **GitHub Actions** despliega automáticamente

### Actualizar Landing

1. **Editar** `index.html`
2. **Commit y push** a `main`
3. **GitHub Actions** copia a `gh-pages`

### Actualizar API Reference

¡No requiere acción manual!

- **Auto-generada** desde docstrings
- Al actualizar código en `scavengr/`, se regenera automáticamente
- Asegúrate de seguir estilo Google en docstrings

## ⚠️ Consideraciones

### URLs Absolutas vs Relativas

MkDocs usa `site_url` para generar URLs absolutas:

- **Bien**: `https://scavengr.jsonrivera.dev/docs/api/core/entities/`
- **Mal**: `/api/core/entities/` (relativo, puede romperse)

### CNAME

El archivo `CNAME` es **crítico**:

- Sin él, GitHub Pages servirá en `jasrockr.github.io/Scavengr/`
- Con él, servirá en `scavengr.jsonrivera.dev`
- Debe estar en la raíz de `gh-pages`

### Caché

GitHub Pages puede cachear agresivamente:

- Cambios pueden tardar 1-2 minutos en aparecer
- Usa Ctrl+F5 para limpiar caché del navegador
- Verifica en modo incógnito

## 🎯 Ventajas de esta Arquitectura

✅ **Separación de concerns**: Marketing vs Documentación técnica  
✅ **SEO optimizado**: URLs limpias y descriptivas  
✅ **Auto-actualización**: Docs siempre sincronizadas con código  
✅ **Profesional**: Landing atractivo + docs completas  
✅ **Mantenible**: Editar Markdown es fácil  
✅ **Versionable**: Todo en Git

## 📞 Troubleshooting

### "404 Not Found" en `/docs/`

- Verifica que `gh-pages` tenga el directorio `docs/`
- Revisa GitHub Actions logs
- Asegúrate de que `site_url` termine en `/docs/`

### "Página en blanco" en `/docs/`

- Revisa console del navegador (F12)
- Verifica rutas relativas en `mkdocs.yml`
- Prueba `mkdocs build` localmente

### "Landing no se actualiza"

- Verifica que GitHub Actions copió `index.html`
- Limpia caché del navegador
- Espera 1-2 minutos para propagación DNS

---

**🎉 Resultado Final:**

Una web profesional de dos niveles:

1. **Landing** → Vende el proyecto, atrae usuarios
2. **Docs** → Ayuda a usuarios y desarrolladores

Ambos actualizados automáticamente con cada push a `main`. 🚀

---

# 📦 Publicación de Releases con publish.ps1

Esta sección describe los flujos de trabajo soportados por `scripts/publish.ps1` y las mejores prácticas para publicar releases de Scavengr.

> 📘 **Para documentación completa del script**, consultar [`scripts/README.md`](scripts/README.md)

## 🎯 Flujos de Publicación Soportados

El script `publish.ps1` detecta automáticamente las protecciones de rama y adapta su comportamiento:

### 1️⃣ Flujo con Branch Protection (Producción - ACTUAL)

**Scavengr usa este flujo** porque tiene branch protection activa en `main`.

```
1. Ejecutar: .\scripts\publish.ps1
   ├─ Pre-commit hooks automáticos
   ├─ Commit y tag locales
   └─ Detecta protecciones → Crea release/vX.Y.Z

2. Script pushea rama release y tag
   └─ Muestra URL del PR

3. Crear PR en GitHub (MANUAL)
   └─ Esperar CI/CD checks

4. Aprobar y mergear PR

5. Continuar publicación:
   ├─ git checkout main
   ├─ git pull origin main
   └─ .\scripts\publish.ps1  (build y PyPI)
```

**Ventajas**: ✅ Code review ✅ CI/CD ✅ Auditable ✅ Rollback fácil

### 2️⃣ Flujo sin Branch Protection (Desarrollo)

Para proyectos sin protecciones, el script hace todo en una ejecución:

```
1. Ejecutar: .\scripts\publish.ps1
   └─ Pre-commit → Commit → Tag → Push → Build → PyPI
   
TODO EN UNA SOLA EJECUCIÓN
```

**Ventajas**: ⚡ Rápido  
**Desventajas**: ⚠️ Sin code review

### 3️⃣ Modo BuildOnly (Testing)

Solo construir paquetes sin tocar Git:

```powershell
.\scripts\publish.ps1 -BuildOnly
```

**Útil para**:
- Validar cambios en `pyproject.toml`
- Probar builds antes de release
- Publicar en Test PyPI

---

## 🔒 Configuración de Branch Protection (Actual)

Scavengr tiene configuradas las siguientes protecciones en `main`:

```yaml
✅ Require pull request before merging
   └─ Require approvals: 1

✅ Require status checks to pass:
   - Tests unitarios (pytest)
   - Linting (flake8)
   - Pre-commit hooks
   - Cobertura de código

✅ Require conversation resolution

❌ Allow force pushes: NUNCA
❌ Allow deletions: NUNCA
```

Esta configuración garantiza calidad y seguridad en cada release.

---

## 🛠️ Requisitos para Usar el Script en Otros Proyectos

### ⚠️ Importante: No es Solo Copiar el Script

El proyecto destino **DEBE cumplir** requisitos específicos:

### ✅ Requisitos Obligatorios

#### 1. **pyproject.toml con PEP 517/518**

```toml
[build-system]
requires = ["setuptools>=45", "setuptools-scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "tu-paquete"
dynamic = ["version"]
requires-python = ">=3.8"
```

**¿Por qué?**: El script usa `python -m build` que requiere pyproject.toml.

#### 2. **setuptools-scm para Versionado Automático**

```toml
[tool.setuptools_scm]
write_to = "tu_paquete/_version.py"
version_scheme = "python-simplified-semver"
local_scheme = "no-local-version"
```

**¿Por qué?**: El script NO maneja versiones hardcodeadas, depende de tags Git.

#### 3. **Git Configurado**

- Repositorio inicializado (`git init`)
- Al menos un commit existente
- Remoto configurado (`origin`)
- Credenciales de GitHub

#### 4. **Estructura de Paquete Python Válida**

```
proyecto/
├── pyproject.toml          # OBLIGATORIO
├── README.md               # OBLIGATORIO
├── tu_paquete/            # OBLIGATORIO
│   ├── __init__.py
│   └── ...
└── scripts/
    └── publish.ps1
```

#### 5. **Python 3.8+ con Build Tools**

```powershell
pip install build twine setuptools-scm
```

---

### 🔧 Requisitos Opcionales (Recomendados)

#### Pre-commit Hooks

```powershell
pip install pre-commit
pre-commit install
```

#### PyPI Credentials (`~/.pypirc`)

```ini
[pypi]
username = __token__
password = pypi-XXXXXXXXXX
```

---

### 📋 Checklist de Adaptación

- [ ] Proyecto usa `pyproject.toml` (PEP 517/518)
- [ ] `setuptools-scm` configurado
- [ ] Git inicializado con remoto
- [ ] Python 3.8+ instalado
- [ ] Build tools instalados: `pip install build twine setuptools-scm`
- [ ] Estructura de paquete válida
- [ ] Variables del script editadas:
  ```powershell
  $ProjectName = "nombre-paquete"
  $RepoOwner = "usuario-github"
  $RepoName = "nombre-repo"
  ```
- [ ] Pre-commit instalado (opcional)
- [ ] PyPI credentials en `~/.pypirc`
- [ ] **Repositorio NO en OneDrive/Dropbox** (clonar en carpeta local)

---

### 🧪 Validación Antes del Primer Release

```powershell
# 1. Verificar setuptools-scm
python -c "from setuptools_scm import get_version; print(get_version())"

# 2. Probar build
python -m build

# 3. Verificar paquetes
twine check dist/*

# 4. Probar en Test PyPI
twine upload --repository testpypi dist/*

# 5. Si funciona, probar script
.\scripts\publish.ps1 -BuildOnly

# 6. Release real
.\scripts\publish.ps1
```

---

## 📊 Comparación de Flujos

| Característica | Con Protection | Sin Protection | BuildOnly |
|----------------|---------------|----------------|-----------|
| Code Review | ✅ Obligatorio | ❌ No | N/A |
| CI/CD Checks | ✅ Antes merge | ❌ No | ⚠️ Local |
| Velocidad | 🐢 Lento | ⚡ Rápido | ⚡ Instantáneo |
| Seguridad | 🔒 Alta | ⚠️ Media | ✅ Alta |
| Uso | 🏢 Producción | 🧪 Desarrollo | 🧪 Testing |

---

## 🎓 Recomendaciones por Escenario

### Proyecto Open Source / Producción
```
✅ Flujo con Branch Protection
- Múltiples revisores
- CI/CD completo
- Auditoría completa
```

### Proyecto Personal / Prototipo
```
✅ Flujo sin Branch Protection
- Push directo
- Publicación rápida
```

### Testing de Cambios
```
✅ Modo BuildOnly
- Sin modificar Git
- Validar builds
```

---

## 🆘 Troubleshooting Común

### "remote rejected main (protected branch)"

✅ **Esto es correcto**. El script crea automáticamente la rama `release/vX.Y.Z` y muestra la URL del PR.

### "El script se detiene después del PR"

✅ **Comportamiento esperado**. Después de mergear el PR:

```powershell
git checkout main
git pull origin main
.\scripts\publish.ps1  # Continúa desde build
```

### "No tengo protecciones pero quiero PR"

Configurar branch protection en GitHub: Settings → Branches → Add rule

---

## 📚 Referencias Adicionales

- **Documentación del Script**: [`scripts/README.md`](scripts/README.md)
- **Guía de Recuperación**: Ver sección Rollback en `scripts/README.md`
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Python Packaging (PEP 517)](https://peps.python.org/pep-0517/)
- [setuptools-scm](https://github.com/pypa/setuptools-scm)

---

**Última actualización**: 2025-11-19  
**Autores**: Jason Rivera (JasRockr)
