# ============================================================================
# SCRIPT DE LIMPIEZA DE RELEASE ERRÓNEA
# ============================================================================
#
# Este script limpia completamente un release fallido (commit + tag) tanto
# en local como en remoto, dejando el repositorio listo para reintentar.
#
# USO:
#   .\scripts\cleanup-release.ps1 -TagName "vv0.0.4"
#   .\scripts\cleanup-release.ps1 -TagName "v0.0.4" -KeepChanges
#
# PARÁMETROS:
#   -TagName       : Tag a eliminar (requerido)
#   -KeepChanges   : Mantener cambios staged después del reset (opcional)
#   -Force         : No pedir confirmación (opcional, ⚠️ peligroso)
#
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$TagName,

    [Parameter(Mandatory=$false)]
    [switch]$KeepChanges,

    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Colores para output
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorPrompt = "Magenta"

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

function Write-Step {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor $ColorInfo
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $ColorWarning
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ColorError
}

function Confirm-Action {
    param([string]$Message)

    if ($Force) {
        return $true
    }

    Write-Host "`n$Message" -ForegroundColor $ColorPrompt
    $response = Read-Host "Continuar? (s/N)"
    return ($response -eq "s" -or $response -eq "S")
}

# ============================================================================
# VALIDACIONES INICIALES
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $ColorInfo
Write-Host "║  🧹 LIMPIEZA DE RELEASE ERRÓNEA - Scavengr                     ║" -ForegroundColor $ColorInfo
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $ColorInfo

Write-Step "Validando estado del repositorio..."

# Verificar que estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Error-Custom "No se encontró repositorio Git en el directorio actual"
    exit 1
}

# Verificar que no hay cambios sin commitear (excepto si vienen de reset previo)
$status = git status --porcelain
if ($status -and -not $KeepChanges) {
    Write-Warning "Hay cambios sin commitear en el working directory"
    Write-Host "Cambios detectados:" -ForegroundColor Gray
    git status --short

    if (-not (Confirm-Action "¿Continuar de todas formas?")) {
        Write-Host "Operación cancelada por el usuario" -ForegroundColor Gray
        exit 0
    }
}

Write-Success "Repositorio validado"

# ============================================================================
# PASO 1: MOSTRAR ESTADO ACTUAL
# ============================================================================

Write-Step "Estado actual del repositorio:"

Write-Host "`n📊 Últimos commits:" -ForegroundColor Gray
git log --oneline -5 --decorate

Write-Host "`n🏷️  Tags locales:" -ForegroundColor Gray
git tag -l | Select-Object -Last 5

Write-Host "`n🌐 Tags en remoto:" -ForegroundColor Gray
git ls-remote --tags origin | Select-String "refs/tags/" | ForEach-Object {
    $_.Line -replace ".*/", ""
} | Select-Object -Last 5

# ============================================================================
# PASO 2: VERIFICAR QUE EL TAG EXISTE
# ============================================================================

Write-Step "Verificando tag '$TagName'..."

$tagExistsLocal = git tag -l $TagName
$tagExistsRemote = git ls-remote --tags origin "refs/tags/$TagName"

if (-not $tagExistsLocal -and -not $tagExistsRemote) {
    Write-Error-Custom "El tag '$TagName' no existe ni en local ni en remoto"
    exit 1
}

if ($tagExistsLocal) {
    Write-Warning "Tag encontrado en repositorio local"
}

if ($tagExistsRemote) {
    Write-Warning "Tag encontrado en repositorio remoto"
}

# ============================================================================
# PASO 3: CONFIRMAR ACCIÓN
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $ColorWarning
Write-Host "║  ⚠️  ADVERTENCIA: OPERACIÓN DESTRUCTIVA                        ║" -ForegroundColor $ColorWarning
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $ColorWarning

Write-Host "`nSe realizarán las siguientes acciones:" -ForegroundColor $ColorWarning
Write-Host "  1. Eliminar tag '$TagName' del repositorio LOCAL" -ForegroundColor Gray

if ($tagExistsRemote) {
    Write-Host "  2. Eliminar tag '$TagName' del repositorio REMOTO" -ForegroundColor Gray
}

# Determinar si hay commits asociados al tag
$tagCommit = git rev-list -n 1 $TagName 2>$null
$currentCommit = git rev-parse HEAD

if ($tagCommit -and $tagCommit -eq $currentCommit) {
    $resetType = if ($KeepChanges) { "--soft" } else { "--mixed" }
    Write-Host "  3. Hacer reset $resetType HEAD~1 (deshacer último commit)" -ForegroundColor Gray

    if ($KeepChanges) {
        Write-Host "     → Los cambios se mantendrán STAGED" -ForegroundColor Gray
    } else {
        Write-Host "     → Los cambios se mantendrán en WORKING DIRECTORY (unstaged)" -ForegroundColor Gray
    }
}

if (-not (Confirm-Action "`n¿Estás SEGURO de que deseas continuar?")) {
    Write-Host "`nOperación cancelada por el usuario" -ForegroundColor Gray
    exit 0
}

# ============================================================================
# PASO 4: ELIMINAR TAG LOCAL
# ============================================================================

if ($tagExistsLocal) {
    Write-Step "Eliminando tag local '$TagName'..."

    try {
        git tag -d $TagName
        Write-Success "Tag local eliminado correctamente"
    }
    catch {
        Write-Error-Custom "Error al eliminar tag local: $_"
        exit 1
    }
}

# ============================================================================
# PASO 5: ELIMINAR TAG REMOTO
# ============================================================================

if ($tagExistsRemote) {
    Write-Step "Eliminando tag remoto '$TagName'..."

    if (-not (Confirm-Action "¿Confirmar eliminación del tag en REMOTO?")) {
        Write-Warning "Tag remoto NO eliminado (operación cancelada)"
    }
    else {
        try {
            git push origin ":refs/tags/$TagName"
            Write-Success "Tag remoto eliminado correctamente"
        }
        catch {
            Write-Error-Custom "Error al eliminar tag remoto: $_"
            Write-Warning "Puedes eliminarlo manualmente con: git push origin :refs/tags/$TagName"
        }
    }
}

# ============================================================================
# PASO 6: RESET DEL COMMIT (SI CORRESPONDE)
# ============================================================================

if ($tagCommit -and $tagCommit -eq $currentCommit) {
    Write-Step "Deshaciendo último commit..."

    $resetType = if ($KeepChanges) { "--soft" } else { "--mixed" }

    try {
        git reset $resetType HEAD~1

        if ($KeepChanges) {
            Write-Success "Commit deshecho (cambios mantenidos en staged)"
        }
        else {
            Write-Success "Commit deshecho (cambios en working directory, unstaged)"
        }
    }
    catch {
        Write-Error-Custom "Error al hacer reset: $_"
        exit 1
    }
}

# ============================================================================
# PASO 7: VERIFICAR ESTADO REMOTO
# ============================================================================

Write-Step "Verificando estado del branch remoto..."

$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse origin/main 2>$null

if ($localCommit -ne $remoteCommit) {
    Write-Warning "El commit local es diferente al remoto"
    Write-Host "`n  Local:  $localCommit" -ForegroundColor Gray
    Write-Host "  Remoto: $remoteCommit" -ForegroundColor Gray

    # Determinar si estamos adelantados o atrasados
    $ahead = git rev-list --count origin/main..HEAD
    $behind = git rev-list --count HEAD..origin/main

    if ($ahead -gt 0) {
        Write-Warning "Estás $ahead commit(s) ADELANTADO del remoto"
    }

    if ($behind -gt 0) {
        Write-Warning "Estás $behind commit(s) ATRASADO del remoto"
    }

    if ($ahead -gt 0 -and (Confirm-Action "`n¿Deseas hacer FORCE PUSH al remoto para sincronizar?")) {
        Write-Step "Haciendo force push a origin/main..."

        try {
            git push origin main --force
            Write-Success "Repositorio remoto sincronizado"
        }
        catch {
            Write-Error-Custom "Error al hacer force push: $_"
            Write-Warning "Puedes hacerlo manualmente con: git push origin main --force"
        }
    }
}
else {
    Write-Success "Repositorio local y remoto están sincronizados"
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $ColorSuccess
Write-Host "║  ✅ LIMPIEZA COMPLETADA EXITOSAMENTE                          ║" -ForegroundColor $ColorSuccess
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $ColorSuccess

Write-Step "Estado final del repositorio:"

Write-Host "`n📊 Últimos commits:" -ForegroundColor Gray
git log --oneline -3 --decorate

Write-Host "`n🏷️  Tags actuales:" -ForegroundColor Gray
git tag -l | Select-Object -Last 5

Write-Host "`n📋 Estado de cambios:" -ForegroundColor Gray
git status --short

Write-Host "`n✨ El repositorio está limpio y listo para un nuevo release" -ForegroundColor $ColorSuccess
Write-Host "   Puedes ejecutar: .\scripts\publish.ps1" -ForegroundColor Gray

exit 0
