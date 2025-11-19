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
