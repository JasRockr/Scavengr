# 🔄 Guía de Recuperación de Release Erróneo

## Situación Actual

**Problema**: Se creó y pusheó el tag `vv0.0.4` (con doble 'v') en lugar de `v0.0.4`.

**Estado del Repositorio**:

- ✅ **Local**: Limpio (reset --soft ya ejecutado, HEAD en `81ea31e`)
- ⚠️ **Remoto**: Tag `vv0.0.4` existe y apunta al commit `21dd63c`
- ✅ **Cambios**: 84+ archivos staged listos para re-commit

---

## Opción 1: Limpieza Rápida Manual (Recomendado)

```powershell
# 1. Eliminar tag del remoto
git push origin :refs/tags/vv0.0.4

# 2. Verificar que se eliminó
git ls-remote --tags origin | Select-String "vv0.0.4"
# (no debe mostrar resultados)

# 3. Eliminar tag local (si existe)
git tag -d vv0.0.4

# 4. Verificar estado limpio
git status
git log --oneline -3
```

**Tiempo estimado**: 1 minuto

---

## Opción 2: Script Automatizado Completo

```powershell
# Ejecutar script de limpieza con todas las validaciones
.\scripts\cleanup-release.ps1 -TagName "vv0.0.4" -KeepChanges

# El script automáticamente:
# ✅ Valida estado del repositorio
# ✅ Elimina tag local y remoto
# ✅ Verifica sincronización
# ✅ Mantiene cambios staged
# ✅ Muestra resumen final
```

**Tiempo estimado**: 2-3 minutos (incluye confirmaciones interactivas)

---

## Opción 3: Usar publish.ps1 en Modo Rollback

```powershell
# Rollback automático del último tag
.\scripts\publish.ps1 -Rollback

# O especificar tag manualmente
.\scripts\publish.ps1 -RollbackTag "vv0.0.4"

# El script:
# ✅ Detecta automáticamente el último tag
# ✅ Elimina tag local y remoto
# ✅ Hace reset --soft del commit
# ✅ Mantiene cambios staged
```

**Tiempo estimado**: 2 minutos

---

## Después de la Limpieza: Crear Release Correcto

```powershell
# 1. Verificar que todo está limpio
git status
# Debe mostrar: "On branch main, Changes to be committed: ..."

# 2. Ejecutar publish.ps1 normalmente
.\scripts\publish.ps1

# 3. Cuando pida la versión, ingresar SIN el prefijo 'v':
#    Entrada correcta: 0.0.4
#    (El script agregará automáticamente el 'v' → v0.0.4)

# 4. El script ahora tiene validaciones que previenen:
#    ❌ vv0.0.4 (doble v) → detectado y rechazado
#    ❌ v0.0.4 (con v manual) → detectado y corregido
#    ✅ 0.0.4 (sin v) → aceptado y convertido a v0.0.4
```

---

## Nuevas Características de publish.ps1

### 1. Validación de Formato de Tag

- **Detecta doble 'v'**: Rechaza versiones como `vv0.0.4` automáticamente
- **Valida semver**: Advierte si no sigue formato `X.Y.Z`
- **Corrección automática**: Limpia prefijos 'v' duplicados

### 2. Modo Rollback Integrado

```powershell
# Deshacer último release
.\scripts\publish.ps1 -Rollback

# Deshacer release específico
.\scripts\publish.ps1 -RollbackTag "v0.0.3"
```

### 3. Confirmaciones de Seguridad

- Pide confirmación antes de eliminar tags remotos
- Muestra resumen de cambios antes de operaciones destructivas
- Opción de cancelar en cualquier momento

---

## Prevención de Errores Futuros

**Buenas Prácticas**:

1. **Siempre ingresar versión SIN prefijo 'v'**:

   ```text
   ✅ Correcto: 0.0.4
   ❌ Incorrecto: v0.0.4
   ❌ Incorrecto: vv0.0.4
   ```

2. **Revisar el tag antes de confirmar**:
   - El script muestra el tag que se creará
   - Verificar antes de continuar

3. **Usar el modo rollback si hay error**:

   ```powershell
   .\scripts\publish.ps1 -Rollback
   ```

4. **Hacer dry-run local antes de pushear** (futuro):

   ```powershell
   # Crear tag local sin pushear
   git tag -a "v0.0.4" -m "Release v0.0.4"
   
   # Verificar que está correcto
   git tag -l
   
   # Si está mal, eliminarlo antes de pushear
   git tag -d "v0.0.4"
   ```

---

## Comandos de Verificación Útiles

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
```

---

## Resumen Ejecutivo

**Para limpiar el error actual (vv0.0.4)**:

```powershell
# Opción más rápida (1 comando)
git push origin :refs/tags/vv0.0.4

# Opción más segura (script con validaciones)
.\scripts\cleanup-release.ps1 -TagName "vv0.0.4" -KeepChanges

# Opción integrada en publish.ps1
.\scripts\publish.ps1 -Rollback
```

**Para crear el release correcto**:

```powershell
# Ejecutar normalmente
.\scripts\publish.ps1

# Cuando pida versión, ingresar: 0.0.4
# (sin 'v', el script lo agrega automáticamente)
```

---

## Solución de Problemas

**Error: "remote ref does not exist"**  

- El tag ya fue eliminado del remoto
- Verificar con: `git ls-remote --tags origin`

**Error: "tag not found"**  

- El tag no existe localmente
- Verificar con: `git tag -l`

**Error: "Updates were rejected"**  

- Alguien más modificó el remoto
- Hacer: `git fetch origin` y reintentar

**Los cambios desaparecieron después del reset**  

- Verificar con: `git status`
- Si usaste `--soft`, deben estar en staged
- Si usaste `--mixed`, están en working directory (unstaged)
- Si usaste `--hard`, se perdieron (usar `git reflog` para recuperar)

---

## Contacto y Soporte

Si tienes problemas con la recuperación:

1. **No hacer `git push --force` sin consultar**
2. **Guardar salida de `git status` y `git log`**
3. **Consultar esta guía antes de ejecutar comandos destructivos**
4. **Usar el flag `-WhatIf` en PowerShell para simular (cuando esté disponible)**
