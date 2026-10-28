# 📦 Script de Publicación Universal - publish.ps1

## 🎯 Propósito

`publish.ps1` es un script **universal** de publicación para proyectos Python que automatiza todo el proceso de release:

- ✅ Validaciones pre-commit automáticas
- ✅ Versionado automático con `setuptools-scm`
- ✅ Detección inteligente de protecciones de rama
- ✅ Creación automática de Pull Requests cuando es necesario
- ✅ Build y publicación en PyPI
- ✅ Rollback de releases
- ✅ Compatible con múltiples flujos de trabajo

---

## 🚀 Características Principales

### 1. **Detección Automática de Protecciones**

El script detecta automáticamente si tu rama `main` tiene protecciones activas en GitHub:

- **Con protecciones**: Crea rama `release/vX.Y.Z` y te guía para crear un PR
- **Sin protecciones**: Push directo a `main` y publicación inmediata

### 2. **Modos de Operación**

```powershell
# Modo normal (detecta protecciones automáticamente)
.\scripts\publish.ps1

# Solo build (sin modificar Git)
.\scripts\publish.ps1 -BuildOnly

# Forzar push directo (NO RECOMENDADO)
.\scripts\publish.ps1 -SkipBranchProtection

# Rollback de último release
.\scripts\publish.ps1 -Rollback

# Rollback de release específico
.\scripts\publish.ps1 -RollbackTag "v0.0.4"
```

### 3. **Versionado Automático**

Usa `setuptools-scm` para calcular la versión automáticamente basado en:

- **Tags existentes**: Lee el último tag y sugiere siguiente versión
- **Commits**: Cuenta commits desde el último tag
- **Tipo de release**: Patch (0.0.X), Minor (0.X.0), Major (X.0.0)

### 4. **Pre-commit Hooks Integrados**

Ejecuta automáticamente:

- `black` - Formateo de código
- `isort` - Ordenamiento de imports
- `flake8` - Linting
- `check-yaml` - Validación de YAML
- Otros hooks configurados en `.pre-commit-config.yaml`

---

## 📋 Requisitos Previos

### Software Necesario

```powershell
# Python 3.8+
python --version

# Git configurado
git --version

# Twine (para publicación)
pip install twine

# Build tools
pip install build

# Pre-commit (opcional pero recomendado)
pip install pre-commit
pre-commit install
```

### Configuración de PyPI

Crear archivo `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXX

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Configuración de GitHub

Si tu proyecto usa branch protection:

1. Settings → Branches → Add rule para `main`
2. Activar:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

---

## 🔧 Configuración del Script

### Variables del Proyecto

Editar las líneas 67-71 en `publish.ps1`:

```powershell
# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL PROYECTO (EDITAR SEGÚN TU PROYECTO)
# ═══════════════════════════════════════════════════════════
$ProjectName = "tu-paquete"        # ⬅️ CAMBIAR: Nombre del paquete Python
$RepoOwner = "tu-usuario"          # ⬅️ CAMBIAR: Usuario/Org de GitHub
$RepoName = "Tu-Repositorio"       # ⬅️ CAMBIAR: Nombre del repo
$TwineVersion = "6.0.1"            # Opcional: versión específica de Twine
```

### Ejemplo para un Proyecto Diferente

Si tu proyecto se llama `awesome-lib`:

```powershell
$ProjectName = "awesome-lib"       # Debe coincidir con setup.py/pyproject.toml
$RepoOwner = "MiUsuario"           # Tu usuario de GitHub
$RepoName = "awesome-lib"          # Nombre del repositorio
$TwineVersion = "6.0.1"
```

---

## 📖 Guía de Uso

### Flujo Completo con Branch Protection (Recomendado)

```powershell
# PASO 1: Ejecutar script
.\scripts\publish.ps1

# El script:
# ✅ Ejecuta pre-commit hooks
# ✅ Crea commit local
# ✅ Crea tag local
# ✅ Detecta protecciones
# ✅ Crea rama release/vX.Y.Z
# ✅ Pushea rama y tag
# ✅ Muestra URL del PR

# PASO 2: Crear Pull Request en GitHub
# (El script muestra la URL exacta)

# PASO 3: Esperar CI/CD checks
# - Tests
# - Linting
# - Coverage

# PASO 4: Aprobar y mergear PR

# PASO 5: Continuar publicación
git checkout main
git pull origin main
.\scripts\publish.ps1  # ⬅️ Continúa desde build/publish
```

### Flujo Rápido sin Branch Protection

```powershell
# Ejecutar script (TODO EN UNO)
.\scripts\publish.ps1

# El script automáticamente:
# ✅ Pre-commit hooks
# ✅ Commit
# ✅ Tag
# ✅ Push a main
# ✅ Build
# ✅ Publicación en PyPI
```

### Solo Testing de Build

```powershell
# Solo construir paquetes sin tocar Git
.\scripts\publish.ps1 -BuildOnly

# Útil para:
# - Validar setup.py/pyproject.toml
# - Probar builds
# - Publicar en Test PyPI
```

---

## 🔄 Proceso del Script (Paso a Paso)

### PASO 0: Verificación de Entorno

- Valida que estás en la raíz del proyecto
- Verifica que exista `pyproject.toml` o `setup.py`
- Comprueba que Git esté limpio (no hay cambios sin commitear)

### PASO 1: Validación con Pre-commit

```
→ Ejecutando pre-commit hooks...
   ✅ black (formateo)
   ✅ isort (imports)
   ✅ flake8 (linting)
   ✅ check-yaml
   ✅ Otros hooks
```

### PASO 2: Commit y Tag

```
→ Versión actual: 0.0.3
→ Tipo de release: [p]atch / [m]inor / [M]ajor
→ Nueva versión: 0.0.4

→ Creando commit...
   ✅ Commit creado

→ Creando tag v0.0.4...
   ✅ Tag creado
```

### PASO 3: Detección de Protecciones

```
→ Verificando protecciones de rama...

OPCIÓN A: CON PROTECCIONES
   ⚠️  Rama 'main' protegida - se requiere Pull Request
   → Creando rama release/v0.0.4
   → Pusheando rama y tag
   
   📝 SIGUIENTE PASO: CREAR PULL REQUEST
   URL: https://github.com/Usuario/Repo/compare/release/v0.0.4
   
   [Script se detiene aquí]

OPCIÓN B: SIN PROTECCIONES
   ✅ Push directo permitido
   → Pusheando a main...
   → Pusheando tag...
   
   [Continúa al paso 4]
```

### PASO 4: Build

```
→ Limpiando dist/ y metadatos...
→ Ejecutando python -m build...
   ✅ Distribución construida
→ Verificando con twine...
   ✅ Paquetes válidos
```

### PASO 5: Publicación

```
→ Publicando en PyPI...
→ twine upload dist/*
   ✅ Publicado exitosamente
   
📦 Paquete disponible en:
   https://pypi.org/project/tu-paquete/0.0.4/
```

---

## 🛡️ Seguridad y Mejores Prácticas

### ✅ Recomendado

```powershell
# 1. Usar branch protection en producción
# 2. Dejar que el script detecte automáticamente
.\scripts\publish.ps1

# 3. Code review obligatorio vía PR
# 4. CI/CD checks antes del merge
```

### ⚠️ No Recomendado

```powershell
# Bypass de protecciones (solo emergencias)
.\scripts\publish.ps1 -SkipBranchProtection
```

### 🔒 Checklist de Seguridad

- [ ] Branch protection activa en `main`
- [ ] Require PR before merging
- [ ] Require status checks (tests, lint)
- [ ] Pre-commit hooks configurados
- [ ] PyPI token (no password) en `~/.pypirc`
- [ ] Signed commits (opcional)

---

## 🐛 Troubleshooting

### Problema: "remote rejected main (protected branch)"

**Respuesta**: Esto es correcto. El script debe crear un PR.

```
✅ ESPERADO: El script crea release/vX.Y.Z y muestra URL del PR
❌ ERROR: Si no creó la rama, revisar logs
```

### Problema: "No se puede pushear directamente"

**Solución**: Verificar protecciones en GitHub

```powershell
# Opción 1: Crear PR (recomendado)
# El script lo hace automáticamente

# Opción 2: Deshabilitar protecciones temporalmente
# (En Settings → Branches → Edit rule)
```

### Problema: "Pre-commit hooks fallan"

**Solución**: Corregir los problemas antes de continuar

```powershell
# Ver errores específicos
pre-commit run --all-files

# Formatear código
black .
isort .

# Re-ejecutar script
.\scripts\publish.ps1
```

### Problema: "Twine upload falla (401 Unauthorized)"

**Solución**: Verificar credenciales de PyPI

```powershell
# Verificar ~/.pypirc
cat ~/.pypirc

# Regenerar token en PyPI
# https://pypi.org/manage/account/token/

# Actualizar ~/.pypirc con nuevo token
```

### Problema: "Script se detiene en Step X"

**Solución**: El script es interactivo

```
→ Presiona [c] para continuar
→ Presiona [s] para saltar
→ Presiona [q] para salir
```

---

## 🔄 Rollback y Recuperación de Releases

### Deshacer Último Release

```powershell
.\scripts\publish.ps1 -Rollback

# Esto:
# - Elimina el último tag local y remoto
# - Hace reset del último commit
# - Mantiene cambios staged para re-release
# - NO elimina el paquete de PyPI (imposible)
```

### Deshacer Release Específico

```powershell
.\scripts\publish.ps1 -RollbackTag "v0.0.4"

# Útil si quieres eliminar un tag específico
```

### ⚠️ Limitaciones del Rollback

- ✅ Elimina tags de Git (local y remoto)
- ✅ Revierte commits locales (reset --soft)
- ✅ Mantiene cambios en staging area
- ❌ **NO puede eliminar paquetes de PyPI** (política de PyPI)

---

### 🆘 Recuperación de Errores en Releases

#### Caso 1: Tag con Formato Incorrecto (ej: `vv0.0.4`)

**Problema**: Se creó tag con doble 'v' o formato incorrecto.

**Solución Rápida**:

```powershell
# Eliminar tag del remoto
git push origin :refs/tags/vv0.0.4

# Eliminar tag local
git tag -d vv0.0.4

# Verificar limpieza
git ls-remote --tags origin | Select-String "vv0.0.4"
# (no debe mostrar resultados)
```

**Solución con Script**:

```powershell
# Usar rollback integrado
.\scripts\publish.ps1 -RollbackTag "vv0.0.4"

# El script automáticamente:
# ✅ Elimina tag local y remoto
# ✅ Hace reset --soft del commit
# ✅ Mantiene cambios staged
# ✅ Muestra resumen de limpieza
```

#### Caso 2: Commit Pusheado por Error

**Problema**: Se hizo commit y push pero quieres rehacerlo.

**Solución**:

```powershell
# 1. Rollback completo
.\scripts\publish.ps1 -Rollback

# 2. Verificar estado
git status
# Debe mostrar: "Changes to be committed: ..."

# 3. Re-ejecutar release
.\scripts\publish.ps1
```

#### Caso 3: Release Incompleto (Interrupción)

**Problema**: El script se interrumpió a mitad de proceso.

**Estado Común**: Commit local existe, pero no se pusheó.

**Solución**:

```powershell
# Verificar estado
git status
git log --oneline -1

# Si hay commit local no pusheado:
# Opción A: Continuar manualmente
git push origin main
git push origin v0.0.X

# Opción B: Rollback y reintentar
.\scripts\publish.ps1 -Rollback
.\scripts\publish.ps1
```

---

### 🛡️ Prevención de Errores

#### Validaciones Integradas en el Script

El script `publish.ps1` incluye validaciones automáticas:

1. **Detección de doble 'v'**: Rechaza versiones como `vv0.0.4`
2. **Validación semver**: Advierte si no sigue formato `X.Y.Z`
3. **Confirmaciones de seguridad**: Pide confirmación antes de eliminar tags remotos

#### Buenas Prácticas

1. **Siempre ingresar versión SIN prefijo 'v'**:
   ```
   ✅ Correcto: 0.0.4
   ❌ Incorrecto: v0.0.4
   ❌ Incorrecto: vv0.0.4
   ```

2. **Revisar el tag antes de confirmar**:
   - El script muestra el tag que creará
   - Verificar antes de continuar

3. **Usar `-BuildOnly` para testing**:
   ```powershell
   # Probar sin modificar Git
   .\scripts\publish.ps1 -BuildOnly
   ```

---

### 📋 Comandos de Verificación Útiles

```powershell
# Ver tags locales
git tag -l

# Ver tags remotos
git ls-remote --tags origin

# Ver último commit
git log --oneline -1

# Ver estado de cambios
git status --short

# Ver diferencias staged
git diff --cached --stat

# Ver historial de tags
git log --tags --simplify-by-decoration --pretty="format:%ai %d"
```

---

### 🔄 Flujo Completo de Recuperación

**Ejemplo**: Recuperarse de un tag `vv0.0.4` erróneo y crear `v0.0.4` correcto:

```powershell
# PASO 1: Limpiar error
.\scripts\publish.ps1 -RollbackTag "vv0.0.4"

# PASO 2: Verificar limpieza
git status
# Debe mostrar cambios staged listos

# PASO 3: Crear release correcto
.\scripts\publish.ps1

# PASO 4: Cuando pida versión, ingresar: 0.0.4
# (SIN 'v', el script lo agrega automáticamente)

# PASO 5: Seguir flujo normal según protecciones de rama
```

---

### ⚠️ Errores Comunes y Soluciones

#### Error: "remote ref does not exist"

**Causa**: El tag ya fue eliminado del remoto.

**Solución**: Verificar con `git ls-remote --tags origin` y continuar.

#### Error: "tag not found"

**Causa**: El tag no existe localmente.

**Solución**: Verificar con `git tag -l` o eliminar solo del remoto.

#### Error: "Updates were rejected"

**Causa**: Alguien más modificó el remoto.

**Solución**:
```powershell
git fetch origin
# Revisar cambios y reintentar
```

#### Los cambios desaparecieron después del reset

**Causa**: Se usó `--hard` en lugar de `--soft`.

**Solución**:
```powershell
# Recuperar desde reflog
git reflog
git reset --soft HEAD@{1}
```

---

### 🎯 Alternativa: Si Necesitas "Borrar" Release de PyPI

PyPI **NO permite eliminar** paquetes publicados. Alternativas:

**Opción 1: Publicar Versión Corregida (Recomendado)**

```powershell
# Si publicaste 0.0.4 con error, publica 0.0.5
.\scripts\publish.ps1
# Seleccionar: [p]atch
```

**Opción 2: Yanking (Ocultar Versión)**

Desde PyPI web interface:
1. Ir a tu paquete → Manage → Releases
2. Seleccionar versión errónea
3. Click "Options" → "Yank release"
4. La versión queda oculta (pip no la instala por defecto)

**Opción 3: Contactar PyPI Support**

Solo para casos excepcionales (contenido sensible, violación de políticas).

---

## 📚 Recursos Adicionales

### Documentación Relacionada

- [Mejores Prácticas de Publicación](../docs/PUBLISH_BEST_PRACTICES.md)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

### Comandos Útiles

```powershell
# Ver tags
git tag

# Ver último tag
git describe --tags --abbrev=0

# Ver commits desde último tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Ver archivos en dist/
ls dist/

# Verificar paquete
twine check dist/*

# Publicar en Test PyPI
twine upload --repository testpypi dist/*
```

---

## 🎓 Adaptación a Tu Proyecto

### Checklist de Configuración

- [ ] Clonar este script en `scripts/publish.ps1`
- [ ] Editar variables de configuración (líneas 67-71)
- [ ] Configurar `setuptools-scm` en `pyproject.toml`
- [ ] Configurar pre-commit hooks (`.pre-commit-config.yaml`)
- [ ] Configurar PyPI credentials (`~/.pypirc`)
- [ ] Probar con `-BuildOnly` primero
- [ ] Hacer release de prueba en Test PyPI
- [ ] Configurar branch protection en GitHub
- [ ] Hacer primer release oficial

### Validación

```powershell
# 1. Probar build
.\scripts\publish.ps1 -BuildOnly

# 2. Probar en Test PyPI
twine upload --repository testpypi dist/*

# 3. Instalar desde Test PyPI
pip install --index-url https://test.pypi.org/simple/ tu-paquete

# 4. Si todo funciona, release oficial
.\scripts\publish.ps1
```

---

## 📝 Notas Importantes

### Sobre OneDrive/Cloud Storage

⚠️ **NO ejecutar scripts de publicación desde carpetas sincronizadas con OneDrive, Dropbox, etc.**

**Problema**:
- Los servicios de nube pueden interferir con operaciones de Git
- Posibles conflictos con locks de archivos
- Sincronización puede causar inconsistencias

**Solución**:
```powershell
# Clonar repo fuera de carpetas sincronizadas
cd C:\Projects  # O cualquier carpeta NO sincronizada
git clone https://github.com/Usuario/Repo.git
cd Repo
.\scripts\publish.ps1
```

### Sobre PowerShell Core

El script es compatible con:

- ✅ PowerShell Core (pwsh) - **Recomendado**
- ✅ Windows PowerShell (powershell.exe)
- ✅ PowerShell en Linux/Mac

### Sobre Permisos de Ejecución

Si recibes error de permisos en Windows:

```powershell
# Permitir ejecución de scripts (ejecutar como Admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🤝 Contribuciones

Si mejoras el script, por favor:

1. Documenta los cambios
2. Mantén la compatibilidad con flujos existentes
3. Agrega tests si es posible
4. Actualiza este README

---

## 📄 Licencia

Este script es parte del proyecto Scavengr y sigue la misma licencia (MIT).

---

**Última actualización**: 2025-11-19  
**Versión**: 1.0  
**Autor**: Jason Rivera (JasRockr)  
