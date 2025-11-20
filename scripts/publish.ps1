# -----------------------------------------------------------
# SCRIPT: publish.ps1
# DESCRIPCIÓN: Script universal de publicación para proyectos Python
#              Compatible con protecciones de rama y flujos CI/CD
# AUTOR: Json Rivera
# FECHA: 2025-11-19
# ENTORNO: Windows/Linux/Mac - PowerShell Core
# REQUISITOS: Python, pip, twine, git en PATH
# NOTA: Ejecutar en la raíz del proyecto (donde está pyproject.toml)
#
# EJEMPLOS DE USO:
#   .\scripts\publish.ps1                              # Publicación normal (detecta protecciones)
#   .\scripts\publish.ps1 -SkipBranchProtection        # Forzar push directo (NO RECOMENDADO)
#   .\scripts\publish.ps1 -BuildOnly                   # Solo build (sin commit/tag/push)
#   .\scripts\publish.ps1 -Rollback                    # Deshacer último release
#   .\scripts\publish.ps1 -RollbackTag "v0.0.4"        # Deshacer release específico
#
# CONFIGURACIÓN DEL PROYECTO:
# ===========================
# Editar estas variables para adaptar a tu proyecto:
#   - $ProjectName: Nombre del paquete Python
#   - $RepoOwner: Propietario del repositorio GitHub
#   - $RepoName: Nombre del repositorio GitHub
#
# FLUJOS SOPORTADOS:
# ==================
# 1. CON PROTECCIÓN DE RAMA (Producción - RECOMENDADO):
#    - Detecta protecciones automáticamente
#    - Crea rama release/vX.Y.Z
#    - Pushea rama y tag
#    - Requiere PR manual y aprobación
#    - Después del merge: volver a ejecutar para build/PyPI
#
# 2. SIN PROTECCIÓN DE RAMA (Desarrollo):
#    - Push directo a main
#    - Tag automático
#    - Build y publicación inmediata
#
# 3. BUILD MANUAL (Testing):
#    - Usar flag -BuildOnly
#    - Solo construye paquetes sin modificar Git
#
# IMPORTANTE - VERSIONADO:
# ========================
# La versión se gestiona mediante setuptools-scm (tags de Git)
# NO editar manualmente _version.py (es auto-generado)
# -----------------------------------------------------------

# Parámetros del script
param(
    [Parameter(Mandatory=$false)]
    [switch]$Rollback,

    [Parameter(Mandatory=$false)]
    [string]$RollbackTag,

    [Parameter(Mandatory=$false)]
    [switch]$SkipBranchProtection,

    [Parameter(Mandatory=$false)]
    [switch]$BuildOnly
)

# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL PROYECTO (EDITAR SEGÚN TU PROYECTO)
# ═══════════════════════════════════════════════════════════
$ProjectName = "scavengr"              # Nombre del paquete Python
$RepoOwner = "JasRockr"                # Propietario del repo (GitHub)
$RepoName = "Scavengr"                 # Nombre del repositorio
$TwineVersion = "6.0.1"                # Versión de Twine (opcional)
$RequiresPR = $true                    # ¿Requiere PR por defecto? (true/false)

# Variables globales
$ErrorActionPreference = "Continue"

# -----------------------------------------------------------
# MODO ROLLBACK: Deshacer último release
# -----------------------------------------------------------
if ($Rollback -or $RollbackTag) {
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  🔄 MODO ROLLBACK: Deshacer Release                            ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red

    # Si no se especificó tag, obtener el último
    if (-not $RollbackTag) {
        Write-Host "`n📋 Consultando último tag en remoto..." -ForegroundColor Cyan

        $RemoteTags = git ls-remote --tags origin | ForEach-Object {
            if ($_ -match 'refs/tags/(.*)') {
                $Matches[1] -replace '\^\{\}', ''
            }
        } | Where-Object { $_ -match '^v\d+\.\d+\.\d+' } | Sort-Object -Unique

        if (-not $RemoteTags) {
            Write-Host "❌ No se encontraron tags en el repositorio remoto" -ForegroundColor Red
            exit 1
        }

        $RollbackTag = $RemoteTags | Select-Object -Last 1
        Write-Host "🏷️  Último tag detectado: $RollbackTag" -ForegroundColor Yellow
    }

    # Validar que el tag existe
    $TagExistsRemote = git ls-remote --tags origin "refs/tags/$RollbackTag"
    $TagExistsLocal = git tag -l $RollbackTag

    if (-not $TagExistsRemote -and -not $TagExistsLocal) {
        Write-Host "❌ El tag '$RollbackTag' no existe ni en local ni en remoto" -ForegroundColor Red
        exit 1
    }

    # Confirmar acción
    Write-Host "`n⚠️  ADVERTENCIA: Esta acción eliminará:" -ForegroundColor Yellow
    if ($TagExistsLocal) {
        Write-Host "   • Tag '$RollbackTag' del repositorio LOCAL" -ForegroundColor Gray
    }
    if ($TagExistsRemote) {
        Write-Host "   • Tag '$RollbackTag' del repositorio REMOTO" -ForegroundColor Gray
    }
    Write-Host "   • El commit asociado al tag se deshará (reset --soft)" -ForegroundColor Gray
    Write-Host "   • Los cambios se mantendrán STAGED para modificar y re-commitear" -ForegroundColor Gray

    Write-Host "`n💡 Tip: Usa el script cleanup-release.ps1 para más opciones de limpieza" -ForegroundColor Cyan

    $Confirm = Read-Host "`n¿Estás SEGURO de continuar? (s/N)"
    if ($Confirm -ne "s" -and $Confirm -ne "S") {
        Write-Host "Operación cancelada por el usuario" -ForegroundColor Gray
        exit 0
    }

    # Eliminar tag local
    if ($TagExistsLocal) {
        Write-Host "`n🗑️  Eliminando tag local..." -ForegroundColor Yellow
        git tag -d $RollbackTag
        Write-Host "✅ Tag local eliminado" -ForegroundColor Green
    }

    # Eliminar tag remoto
    if ($TagExistsRemote) {
        Write-Host "`n🌐 Eliminando tag remoto..." -ForegroundColor Yellow
        $ConfirmRemote = Read-Host "¿Confirmar eliminación del tag en REMOTO? (s/N)"

        if ($ConfirmRemote -eq "s" -or $ConfirmRemote -eq "S") {
            git push origin ":refs/tags/$RollbackTag"
            Write-Host "✅ Tag remoto eliminado" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Tag remoto NO eliminado (cancelado)" -ForegroundColor Yellow
        }
    }

    # Verificar si necesitamos reset
    $TagCommit = git rev-list -n 1 $RollbackTag 2>$null
    $CurrentCommit = git rev-parse HEAD

    if ($TagCommit -and $TagCommit -eq $CurrentCommit) {
        Write-Host "`n🔄 Deshaciendo commit (reset --soft HEAD~1)..." -ForegroundColor Yellow
        git reset --soft HEAD~1
        Write-Host "✅ Commit deshecho (cambios mantenidos en staged)" -ForegroundColor Green
    }

    # Resumen final
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ ROLLBACK COMPLETADO                                       ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

    Write-Host "`n📊 Estado actual:" -ForegroundColor Cyan
    git log --oneline -3 --decorate

    Write-Host "`n📋 Cambios staged:" -ForegroundColor Cyan
    git status --short

    Write-Host "`n✨ Puedes volver a ejecutar este script para crear el release correcto" -ForegroundColor Green

    exit 0
}

# -----------------------------------------------------------
# FUNCIÓN DE LECTURA INTERACTIVA
# -----------------------------------------------------------
function Get-UserChoice {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt
    )
    Write-Host "`n=========================================================" -ForegroundColor Yellow
    Write-Host "$Prompt" -ForegroundColor Cyan
    Write-Host " [c] Continuar | [s] Saltar este paso | [q] Salir" -ForegroundColor Gray
    Write-Host "=========================================================" -ForegroundColor Yellow
    $Choice = Read-Host "Elige una opción (c/s/q)"
    return $Choice.ToLower()
}

# -----------------------------------------------------------
# FUNCIÓN DE LECTURA MULTILÍNEA
# -----------------------------------------------------------
function Get-MultiLineInput {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt
    )
    Write-Host "$Prompt (Termina con una línea en blanco y ENTER):" -ForegroundColor Green
    $InputLines = @()
    while ($true) {
        $Line = Read-Host
        if ([string]::IsNullOrEmpty($Line)) {
            break
        }
        $InputLines += $Line
    }
    return $InputLines -join "`n"
}

# -----------------------------------------------------------
# MODO BUILD ONLY: Solo construir paquetes sin Git
# Modo BuildOnly: Solo build, sin Git operations
if ($BuildOnly) {
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  🔨 MODO BUILD ONLY: Solo construcción de paquetes           ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n📦 Este modo solo construirá los paquetes sin modificar Git" -ForegroundColor Yellow
    Write-Host "   (No se creará commit, tag, ni se pusheará nada)" -ForegroundColor Gray
    Write-Host ""

    # Ir directamente a la sección de build (después del bloque else)
} else {

# -----------------------------------------------------------
# PASO 1: Verificación de Entorno y Versión de Twine (Solo si NO es BuildOnly)
# -----------------------------------------------------------
$Step = 1
$Choice = Get-UserChoice -Prompt "$Step. [VERIFICACIÓN DE ENTORNO] Presiona [c] para verificar la versión de Twine y dependencias."

if ($Choice -eq "c") {
    Write-Host "-> Verificando versión de Twine..." -ForegroundColor Yellow
    try {
        $InstalledTwine = (pip show twine | Select-String "Version: (\d+\.\d+\.\d+)").Matches.Groups[1].Value
        if ($InstalledTwine -ne $TwineVersion) {
            Write-Host "⚠️ Twine detectado: $InstalledTwine. Se requiere la versión $TwineVersion para evitar el error de licencia." -ForegroundColor Red
            Read-Host "Presiona ENTER para instalar la versión $TwineVersion (Ctrl+C para cancelar)"
            pip install "twine==$TwineVersion" -ErrorAction Stop
            Write-Host "✅ Twine actualizado a $TwineVersion." -ForegroundColor Green
        } else {
            Write-Host "✅ Twine $TwineVersion ya está instalado." -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Error al verificar/instalar Twine. Asegúrate de que Python y pip estén en tu PATH. Detalles: $($_.Exception.Message)" -ForegroundColor Red
    }
} elseif ($Choice -eq "q") { exit }

# -----------------------------------------------------------
# PASO 2: Git Commit & Tag
# -----------------------------------------------------------
$Step = 2
$Choice = Get-UserChoice -Prompt "$Step. [GIT] Presiona [c] para confirmar cambios, ingresar la version y crear el Tag."

if ($Choice -eq "c") {

    # 2.0 Validación preventiva de pre-commit hooks (OPCIONAL)
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  🔍 VALIDACIÓN PREVENTIVA (Recomendado)                        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`nAntes de crear el commit, se recomienda ejecutar las validaciones" -ForegroundColor Yellow
    Write-Host "de pre-commit hooks para detectar y corregir errores automáticamente." -ForegroundColor Yellow
    Write-Host "`nEsto incluye:" -ForegroundColor Gray
    Write-Host "  • Formateo de código (black, isort)" -ForegroundColor Gray
    Write-Host "  • Linting (flake8)" -ForegroundColor Gray
    Write-Host "  • Validaciones de archivos (YAML, TOML, JSON)" -ForegroundColor Gray
    Write-Host "  • Corrección de espacios y saltos de línea" -ForegroundColor Gray

    $RunPreCommit = Read-Host "`n¿Ejecutar validaciones preventivas? (S/n)"

    if ($RunPreCommit -ne "n" -and $RunPreCommit -ne "N") {
        Write-Host "`n🔄 Ejecutando pre-commit hooks en todos los archivos..." -ForegroundColor Cyan
        Write-Host "   (Esto puede tomar unos segundos...)" -ForegroundColor Gray

        # Verificar si pre-commit está instalado
        $PreCommitInstalled = Get-Command pre-commit -ErrorAction SilentlyContinue

        if (-not $PreCommitInstalled) {
            Write-Host "`n⚠️  pre-commit no está instalado en el sistema" -ForegroundColor Yellow
            Write-Host "   Instálalo con: pip install pre-commit" -ForegroundColor Gray
            Write-Host "   Luego ejecuta: pre-commit install" -ForegroundColor Gray
            $ContinueAnyway = Read-Host "`n¿Continuar sin validación preventiva? (s/N)"
            if ($ContinueAnyway -ne "s" -and $ContinueAnyway -ne "S") {
                Write-Host "Operación cancelada. Instala pre-commit y vuelve a ejecutar." -ForegroundColor Gray
                exit 0
            }
        } else {
            # Ejecutar pre-commit en todos los archivos
            & pre-commit run --all-files

            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n⚠️  Los hooks de pre-commit encontraron problemas" -ForegroundColor Yellow
                Write-Host "`nOpciones:" -ForegroundColor Cyan
                Write-Host "  [c] Continuar de todas formas (los hooks volverán a ejecutarse en el commit)" -ForegroundColor Gray
                Write-Host "  [r] Revisar cambios automáticos y volver a validar" -ForegroundColor Gray
                Write-Host "  [q] Cancelar y revisar manualmente" -ForegroundColor Gray

                $PreCommitChoice = Read-Host "`nElige una opción (c/r/q)"

                if ($PreCommitChoice -eq "r") {
                    Write-Host "`n📋 Revisa los cambios que hicieron los hooks automáticos" -ForegroundColor Cyan
                    Write-Host "   Ejecuta: git diff" -ForegroundColor Gray
                    Write-Host "`nCuando estés listo, vuelve a ejecutar: .\scripts\publish.ps1" -ForegroundColor White
                    exit 0
                } elseif ($PreCommitChoice -eq "q") {
                    Write-Host "Operación cancelada por el usuario" -ForegroundColor Gray
                    exit 0
                }
                # Si elige 'c', continúa con el flujo normal
            } else {
                Write-Host "`n✅ Todas las validaciones pasaron correctamente" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "`n⚠️  Validación preventiva omitida" -ForegroundColor Yellow
        Write-Host "   Los hooks se ejecutarán automáticamente durante el commit" -ForegroundColor Gray
    }

    # 2.1 Consultar último tag en remoto
    Write-Host "`n-> Consultando último tag en el repositorio remoto..." -ForegroundColor Yellow
    try {
        $RemoteTags = git ls-remote --tags origin | ForEach-Object { $_.Split('/')[-1] } | Where-Object { $_ -match '^v\d+\.\d+\.\d+$' } | Sort-Object -Descending
        if ($RemoteTags) {
            $LastTag = $RemoteTags[0]
            Write-Host "   Último tag remoto: $LastTag" -ForegroundColor Cyan

            # Sugerir siguiente versión
            if ($LastTag -match 'v(\d+)\.(\d+)\.(\d+)') {
                $Major = [int]$Matches[1]
                $Minor = [int]$Matches[2]
                $Patch = [int]$Matches[3]
                $SuggestedPatch = "v$Major.$Minor.$($Patch + 1)"
                $SuggestedMinor = "v$Major.$($Minor + 1).0"
                $SuggestedMajor = "v$($Major + 1).0.0"
                Write-Host "   Sugerencias:" -ForegroundColor Green
                Write-Host "     - Patch: $SuggestedPatch" -ForegroundColor Gray
                Write-Host "     - Minor: $SuggestedMinor" -ForegroundColor Gray
                Write-Host "     - Major: $SuggestedMajor" -ForegroundColor Gray
            }
        } else {
            Write-Host "   No se encontraron tags previos. Esta será la primera versión." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ No se pudo consultar tags remotos. Continuando..." -ForegroundColor Yellow
    }

    # 2.2 Obtener la nueva versión
    $NewVersion = Read-Host "-> Ingresa la NUEVA versión (e.g., x.y.Z)"
    if ([string]::IsNullOrEmpty($NewVersion)) {
        Write-Host "❌ Versión vacía. Saltando Git y continuando." -ForegroundColor Red
        $Choice = "s"
    } else {
        # VALIDACIÓN: Verificar formato del tag (evitar errores como vv0.0.4)
        $TagName = "v$NewVersion"

        # Validar que no tenga doble 'v' (vv)
        if ($TagName -match '^v{2,}') {
            Write-Host "`n❌ ERROR: El tag '$TagName' tiene formato incorrecto (doble 'v')" -ForegroundColor Red
            Write-Host "   Versión ingresada: $NewVersion" -ForegroundColor Gray
            Write-Host "   Tag generado: $TagName (❌ incorrecto)" -ForegroundColor Red
            Write-Host "   Tag esperado: v$($NewVersion -replace '^v+', '') (✅ correcto)" -ForegroundColor Green
            Write-Host "`n💡 Tip: Ingresa la versión SIN el prefijo 'v' (ejemplo: 0.0.4)" -ForegroundColor Cyan
            $Choice = "s"
        }
        # Validar formato semver estándar
        elseif ($NewVersion -notmatch '^\d+\.\d+\.\d+$') {
            Write-Host "`n⚠️  ADVERTENCIA: La versión '$NewVersion' no sigue formato semver estándar (X.Y.Z)" -ForegroundColor Yellow
            Write-Host "   Tag que se creará: $TagName" -ForegroundColor Gray
            $Confirm = Read-Host "`n¿Continuar de todos formas? (s/N)"
            if ($Confirm -ne "s" -and $Confirm -ne "S") {
                Write-Host "Operación cancelada. Ajusta la versión y vuelve a ejecutar." -ForegroundColor Gray
                $Choice = "s"
            }
        }

        # Si pasó validaciones, continuar con mensajes
        if ($Choice -eq "c") {
            # 2.2 Obtener el mensaje de commit
            $CommitMessage = Get-MultiLineInput -Prompt "-> Ingresa el mensaje de Commit"
            $TagMessage = Get-MultiLineInput -Prompt "-> Ingresa el mensaje del Tag (puede ser igual al Commit)"
            if ([string]::IsNullOrEmpty($CommitMessage)) {
                Write-Host "❌ Mensaje de commit vacío. Saltando Git y continuando." -ForegroundColor Red
                $Choice = "s"
            } elseif ([string]::IsNullOrEmpty($TagMessage)) {
                Write-Host "❌ Mensaje de tag vacío. Saltando Git y continuando." -ForegroundColor Red
                $Choice = "s"
            }
        }
    }

    # Si la elección no ha cambiado a saltar
    if ($Choice -eq "c") {
        # Definir un archivo temporal
        $TempFile = "temp_git_message.txt"
        $TempFileTag = "temp_tag_message.txt"

        Write-Host "-> Escribiendo mensajes en archivo temporal '$TempFile'..." -ForegroundColor Yellow
        try {
            # Escribir el mensaje multilínea al archivo temporal
            $CommitMessage | Out-File -FilePath $TempFile -Encoding UTF8 -Force
            $TagMessage | Out-File -FilePath $TempFileTag -Encoding UTF8 -Force

            Write-Host "-> Ejecutando 'git add .' y 'git commit -F $TempFile'..." -ForegroundColor Yellow

            # 2.3 Ejecutar Git commands

            # Git Add
            Write-Host "`n1️⃣  Staging archivos (git add .)..." -ForegroundColor Cyan
            & git add .
            if ($LASTEXITCODE -ne 0) {
                throw "Error al ejecutar 'git add .'. Código de salida: $LASTEXITCODE"
            }

            # Git Commit (con validación de pre-commit hooks)
            Write-Host "`n2️⃣  Ejecutando commit con validación de pre-commit hooks..." -ForegroundColor Cyan
            & git commit -F $TempFile

            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n❌ ERROR: El commit falló (probablemente por hooks de pre-commit)" -ForegroundColor Red
                Write-Host "`n📋 Los hooks de pre-commit validaron y encontraron problemas:" -ForegroundColor Yellow
                Write-Host "   • Errores de flake8 (linting)" -ForegroundColor Gray
                Write-Host "   • Problemas de formato (black/isort)" -ForegroundColor Gray
                Write-Host "   • Validaciones YAML/TOML/JSON" -ForegroundColor Gray
                Write-Host "   • Trailing whitespace o mixed line endings" -ForegroundColor Gray

                Write-Host "`n🔧 SOLUCIONES:" -ForegroundColor Cyan
                Write-Host "   1. Revisar la salida de los hooks arriba para ver errores específicos" -ForegroundColor White
                Write-Host "   2. Corregir los errores reportados manualmente" -ForegroundColor White
                Write-Host "   3. O ejecutar: pre-commit run --all-files  (para auto-corregir lo posible)" -ForegroundColor White
                Write-Host "   4. Luego volver a ejecutar: .\scripts\publish.ps1" -ForegroundColor White

                Write-Host "`n⚠️  IMPORTANTE: No se creó el commit ni el tag. Los cambios siguen staged." -ForegroundColor Yellow
                Write-Host "   Puedes verificar con: git status" -ForegroundColor Gray

                throw "Commit abortado por validaciones de pre-commit hooks"
            }

            Write-Host "✅ Commit creado exitosamente (hooks pasaron)" -ForegroundColor Green

            # Git Tag (etiqueta usando el mensaje del tag)
            Write-Host "`n3️⃣  Creando tag v$NewVersion..." -ForegroundColor Cyan
            & git tag -a "v$NewVersion" -F $TempFileTag

            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n❌ ERROR: No se pudo crear el tag" -ForegroundColor Red
                Write-Host "   El commit se creó pero el tag falló." -ForegroundColor Yellow
                Write-Host "   Puedes crear el tag manualmente: git tag -a 'v$NewVersion' -m 'Release v$NewVersion'" -ForegroundColor Gray
                throw "Error al crear el tag v$NewVersion"
            }

            Write-Host "✅ Tag v$NewVersion creado exitosamente" -ForegroundColor Green

            # Detectar si la rama main tiene protecciones (requiere PR)
            Write-Host "`n4️⃣  Verificando protecciones de rama..." -ForegroundColor Cyan

            $CurrentBranch = git rev-parse --abbrev-ref HEAD
            $NeedsPR = $false

            # Verificar si se debe omitir la detección de protecciones
            if ($SkipBranchProtection) {
                Write-Host "   ⚠️  FLAG -SkipBranchProtection activo" -ForegroundColor Yellow
                Write-Host "   → Se intentará push directo ignorando protecciones" -ForegroundColor Gray
                Write-Host "   ⚠️  ADVERTENCIA: Esto puede fallar si hay protecciones de rama" -ForegroundColor Red
                $NeedsPR = $false
            } else {
                # Intentar push para detectar protecciones
                Write-Host "   Verificando si se requiere Pull Request..." -ForegroundColor Gray
                $TestPush = git push origin $CurrentBranch --dry-run 2>&1

                if ($TestPush -match "protected" -or $TestPush -match "rule violations" -or $TestPush -match "pull request") {
                    $NeedsPR = $true
                    Write-Host "   ⚠️  Rama '$CurrentBranch' protegida - se requiere Pull Request" -ForegroundColor Yellow
                } else {
                    Write-Host "   ✅ Push directo permitido" -ForegroundColor Green
                }
            }

            # Si se requiere PR, crear rama release
            if ($NeedsPR) {
                $ReleaseBranch = "release/v$NewVersion"

                Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
                Write-Host "║  ⚠️  FLUJO DE PULL REQUEST REQUERIDO                          ║" -ForegroundColor Yellow
                Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "📋 Se creará una rama '$ReleaseBranch' para el PR" -ForegroundColor Cyan
                Write-Host ""

                # Crear rama release
                Write-Host "   Creando rama $ReleaseBranch..." -ForegroundColor Gray
                & git checkout -b $ReleaseBranch

                if ($LASTEXITCODE -ne 0) {
                    Write-Host "`n❌ ERROR: No se pudo crear la rama de release" -ForegroundColor Red
                    throw "Error al crear rama $ReleaseBranch"
                }

                # Pushear rama release
                Write-Host "   Pusheando $ReleaseBranch a origin..." -ForegroundColor Gray
                & git push -u origin $ReleaseBranch

                if ($LASTEXITCODE -ne 0) {
                    Write-Host "`n❌ ERROR: No se pudo pushear la rama de release" -ForegroundColor Red
                    throw "Error al pushear $ReleaseBranch"
                }

                Write-Host "✅ Rama $ReleaseBranch creada y pusheada" -ForegroundColor Green

                # Pushear tag
                Write-Host "`n   Pusheando tag v$NewVersion a origin..." -ForegroundColor Gray
                & git push origin "v$NewVersion"

                if ($LASTEXITCODE -ne 0) {
                    Write-Host "`n❌ ERROR: No se pudo pushear el tag" -ForegroundColor Red
                    throw "Error al pushear tag v$NewVersion"
                }

                Write-Host "✅ Tag v$NewVersion pusheado" -ForegroundColor Green
                Write-Host ""
                Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
                Write-Host "║  📝 SIGUIENTE PASO: CREAR PULL REQUEST                        ║" -ForegroundColor Green
                Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
                Write-Host ""
                Write-Host "1️⃣  Ir a GitHub y crear un Pull Request:" -ForegroundColor Cyan
                Write-Host "   URL: https://github.com/$RepoOwner/$RepoName/compare/$ReleaseBranch" -ForegroundColor White
                Write-Host ""
                Write-Host "2️⃣  Configurar el PR:" -ForegroundColor Cyan
                Write-Host "   Base: main ← Compare: $ReleaseBranch" -ForegroundColor White
                Write-Host "   Título: Release v$NewVersion" -ForegroundColor White
                Write-Host ""
                Write-Host "3️⃣  Esperar a que pasen los checks de CI/CD:" -ForegroundColor Cyan
                Write-Host "   - Tests unitarios (pytest)" -ForegroundColor Gray
                Write-Host "   - Linting (flake8)" -ForegroundColor Gray
                Write-Host "   - Pre-commit hooks" -ForegroundColor Gray
                Write-Host "   - Cobertura de código" -ForegroundColor Gray
                Write-Host ""
                Write-Host "4️⃣  Aprobar y mergear el Pull Request" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "5️⃣  Después del merge, continuar con la publicación:" -ForegroundColor Cyan
                Write-Host "   git checkout main" -ForegroundColor White
                Write-Host "   git pull origin main" -ForegroundColor White
                Write-Host "   .\scripts\publish.ps1" -ForegroundColor White
                Write-Host ""
                Write-Host "⚠️  El script se detendrá aquí hasta que se complete el PR" -ForegroundColor Yellow
                Write-Host ""

                exit 0
            }

            # Si NO se requiere PR, push directo
            Write-Host "`n4️⃣  Pusheando commits a origin/$CurrentBranch..." -ForegroundColor Cyan
            & git push origin $CurrentBranch

            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n❌ ERROR: No se pudo pushear commits" -ForegroundColor Red
                Write-Host "   El commit y tag existen localmente pero no se pushearon." -ForegroundColor Yellow
                Write-Host "   Puedes pushear manualmente: git push origin $CurrentBranch" -ForegroundColor Gray
                throw "Error al pushear commits a origin/$CurrentBranch"
            }

            Write-Host "✅ Commits pusheados a origin/$CurrentBranch" -ForegroundColor Green

            # Git Push (tags)
            Write-Host "`n5️⃣  Pusheando tag v$NewVersion a origin..." -ForegroundColor Cyan
            & git push origin "v$NewVersion"

            if ($LASTEXITCODE -ne 0) {
                Write-Host "`n❌ ERROR: No se pudo pushear el tag" -ForegroundColor Red
                Write-Host "   El tag existe localmente pero no se pusheó al remoto." -ForegroundColor Yellow
                Write-Host "   Puedes pushear manualmente: git push origin v$NewVersion" -ForegroundColor Gray
                throw "Error al pushear tag v$NewVersion"
            }

            Write-Host "✅ Tag v$NewVersion pusheado a origin" -ForegroundColor Green

            Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
            Write-Host "║  ✅ GIT: COMMIT Y TAG COMPLETADOS EXITOSAMENTE                ║" -ForegroundColor Green
            Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
            Write-Host "   Versión: v$NewVersion" -ForegroundColor White
            Write-Host "   Commit: $(git rev-parse --short HEAD)" -ForegroundColor White

            $LastVersion = $NewVersion
        } catch {
            Write-Host "❌ ERROR en Git. El proceso no continuará hasta que se resuelva." -ForegroundColor Red
            Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Red
            exit
        } finally {
            # 2.4 Limpiar el archivo temporal
            Remove-Item -Path $TempFile -ErrorAction SilentlyContinue
            Remove-Item -Path $TempFileTag -ErrorAction SilentlyContinue
        }
    }

} elseif ($Choice -eq "q") { exit }

}  # Fin del bloque else (NO BuildOnly)

# -----------------------------------------------------------
# PASO 3: Construcción de Distribución (Build)
# -----------------------------------------------------------
$Step = 3
if ($BuildOnly) {
    # En modo BuildOnly, ejecutar directamente sin preguntar
    $Choice = "c"
} else {
    $Choice = Get-UserChoice -Prompt "$Step. [BUILD] Presiona [c] para limpiar 'dist/', metadatos y construir los nuevos paquetes."
}

if ($Choice -eq "c") {
    Write-Host "-> Limpiando dist/, egg-info y _version.py para asegurar la version correcta..." -ForegroundColor Yellow
    try {
        # 3.1 Limpiar directorios de metadatos (CLAVE)
        Remove-Item -Path "dist" -Force -Recurse -ErrorAction SilentlyContinue
        Remove-Item -Path "$ProjectName.egg-info" -Force -Recurse -ErrorAction SilentlyContinue

        # Opcional: Si el archivo _version.py es generado por setuptools_scm, también debe eliminarse.
        # Usando setuptools_scm, normalmente no se maneja _version.py manualmente.
        # Si existe, la siguiente línea lo limpiará.
        Remove-Item -Path "$ProjectName\_version.py" -Force -ErrorAction SilentlyContinue

        Write-Host "-> Ejecutando 'python -m build'..." -ForegroundColor Yellow

        # 3.2 Construir: Usamos el operador '&' para llamar al ejecutable Python.
        & python -m build

        Write-Host "✅ Distribución construida exitosamente en 'dist/'." -ForegroundColor Green

        # 3.3 Verificar con Twine:
        Write-Host "-> Verificando paquetes con 'twine check dist/*'..." -ForegroundColor Yellow
        & twine check dist/*
        Write-Host "✅ Verificación de Twine completada (PASSED)." -ForegroundColor Green

        # Si es modo BuildOnly, terminar aquí
        if ($BuildOnly) {
            Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
            Write-Host "║  ✅ BUILD COMPLETADO EXITOSAMENTE                             ║" -ForegroundColor Green
            Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
            Write-Host "`n📦 Paquetes creados en dist/:" -ForegroundColor Cyan
            Get-ChildItem -Path "dist" | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor White }
            Write-Host "`n💡 Para publicar a PyPI, ejecuta:" -ForegroundColor Yellow
            Write-Host "   twine upload dist/*" -ForegroundColor White
            Write-Host ""
            exit 0
        }

    } catch {
        Write-Host "❌ ERROR durante el Build o Check de Twine. El proceso no continuará." -ForegroundColor Red
        Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Red
        exit
    }
} elseif ($Choice -eq "q") { exit }

# -----------------------------------------------------------
# PASO 4: Subida a PyPI (Twine Upload)
# -----------------------------------------------------------
$Step = 4
$Choice = Get-UserChoice -Prompt "$Step. [PUBLICAR] Presiona [c] para subir a PyPI/TestPyPI."

if ($Choice -eq "c") {

    $PypiChoice = Read-Host "-> ¿Subir a [t] TestPyPI o [p] PyPI (Producción)? (t/p)"

    if ($PypiChoice.ToLower() -eq "t") {
        $Repo = "testpypi"
        Write-Host "-> Subiendo a TestPyPI..." -ForegroundColor Yellow
    } elseif ($PypiChoice.ToLower() -eq "p") {
        $Repo = "pypi"
        Write-Host "-> Subiendo a PyPI (Producción)... ¡ATENCIÓN!" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Elección inválida. Saltando subida a PyPI." -ForegroundColor Red
        $Choice = "s"
    }

    if ($Choice -eq "c") {
        try {
            # twine upload --repository $Repo dist/* -ErrorAction Stop
            & twine upload --repository $Repo dist/*

            Write-Host "🎉 ¡ÉXITO! Paquete subido a $Repo correctamente." -ForegroundColor Green
            Write-Host "   Verifica tu paquete en https://$Repo.org/project/$RepoName/" -ForegroundColor Green
        } catch {
            Write-Host "❌ ERROR al subir con Twine. Verifica tu archivo .pypirc y token de API." -ForegroundColor Red
            Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} elseif ($Choice -eq "q") { exit }

Write-Host "`n---------------------------------------------------------" -ForegroundColor DarkYellow
Write-Host "               FIN DEL SCRIPT. GRACIAS.                  " -ForegroundColor DarkYellow
Write-Host "---------------------------------------------------------" -ForegroundColor DarkYellow
