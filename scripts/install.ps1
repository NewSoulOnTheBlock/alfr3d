#requires -Version 5.1
#
# Alfr3d installer for Windows PowerShell
# https://github.com/NewSoulOnTheBlock/alfr3d
#
# One-liner (after this file is hosted publicly):
#   irm https://YOUR_DOMAIN/install.ps1 | iex
#
# GitHub raw (works today once pushed to main):
#   irm https://raw.githubusercontent.com/NewSoulOnTheBlock/alfr3d/main/scripts/install.ps1 | iex
#
# Options via environment variables (reliable with irm | iex):
#   $env:ALFR3D_REPO        = "https://github.com/NewSoulOnTheBlock/alfr3d.git"
#   $env:ALFR3D_REF         = "main"          # branch, tag, or commit
#   $env:ALFR3D_INSTALL_DIR = "$env:USERPROFILE\.alfr3d\app"
#   $env:ALFR3D_BIN_DIR     = "$env:USERPROFILE\.alfr3d\bin"
#   $env:ALFR3D_SKIP_DEPS   = "1"             # skip pip install -r requirements.txt
#
# Param form (when not piping):
#   & ([scriptblock]::Create((irm https://.../install.ps1))) -Ref main
#

param(
    [string]$Ref = "",
    [string]$InstallDir = "",
    [string]$BinDir = "",
    [string]$Repo = ""
)

$ErrorActionPreference = "Stop"

# PS 5.1 defaults can use TLS 1.0; modern hosts require TLS 1.2+.
[Net.ServicePointManager]::SecurityProtocol = `
    [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$ProgressPreference = "SilentlyContinue"

# Windows-only installer.
if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne "Win32NT") {
    Write-Error "This installer is for Windows. On macOS/Linux use:`n  curl -fsSL https://YOUR_DOMAIN/install.sh | bash"
    exit 1
}

# --- Resolve options (env wins for irm | iex convenience) ---

if (-not $Repo) {
    $Repo = if ($env:ALFR3D_REPO) { $env:ALFR3D_REPO } else { "https://github.com/NewSoulOnTheBlock/alfr3d.git" }
}
if (-not $Ref) {
    $Ref = if ($env:ALFR3D_REF) { $env:ALFR3D_REF } else { "main" }
}
if (-not $InstallDir) {
    $InstallDir = if ($env:ALFR3D_INSTALL_DIR) {
        $env:ALFR3D_INSTALL_DIR
    } else {
        Join-Path $env:USERPROFILE ".alfr3d\app"
    }
}
if (-not $BinDir) {
    $BinDir = if ($env:ALFR3D_BIN_DIR) {
        $env:ALFR3D_BIN_DIR
    } else {
        Join-Path $env:USERPROFILE ".alfr3d\bin"
    }
}

$SkipDeps = $env:ALFR3D_SKIP_DEPS -in @("1", "true", "yes", "on")

function Write-Step([string]$Message) {
    Write-Host "  $Message" -ForegroundColor DarkGray
}

function Write-Title([string]$Message) {
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Ok([string]$Message) {
    Write-Host $Message -ForegroundColor Green
}

function Write-Warn([string]$Message) {
    Write-Host $Message -ForegroundColor Yellow
}

function Assert-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "Required command not found: $Name`n  $Hint"
        exit 1
    }
}

function Get-PythonCommand {
    foreach ($candidate in @("python", "py", "python3")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        try {
            if ($candidate -eq "py") {
                $ver = & py -3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')" 2>$null
                if ($LASTEXITCODE -eq 0 -and $ver) {
                    return @{ Exe = "py"; Args = @("-3"); Version = $ver.Trim() }
                }
            } else {
                $ver = & $candidate -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')" 2>$null
                if ($LASTEXITCODE -eq 0 -and $ver) {
                    return @{ Exe = $candidate; Args = @(); Version = $ver.Trim() }
                }
            }
        } catch {
            continue
        }
    }
    return $null
}

function Test-PythonVersion([string]$VersionText) {
    $parts = $VersionText.Split(".")
    if ($parts.Count -lt 2) { return $false }
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    return ($major -gt 3) -or ($major -eq 3 -and $minor -ge 9)
}

function Ensure-Git {
    if (Get-Command git -ErrorAction SilentlyContinue) { return }
    Write-Warn "Git not found. Attempting install via winget..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        & winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [Environment]::GetEnvironmentVariable("Path", "User")
    }
    Assert-Command "git" "Install Git from https://git-scm.com/download/win then re-run this installer."
}

function Ensure-Python {
    $py = Get-PythonCommand
    if ($py -and (Test-PythonVersion $py.Version)) {
        Write-Step "Python $($py.Version) found."
        return $py
    }

    Write-Warn "Python 3.9+ not found. Attempting install via winget..."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        & winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [Environment]::GetEnvironmentVariable("Path", "User")
        # Fresh installs often need the user Scripts path immediately.
        $localPrograms = Join-Path $env:LOCALAPPDATA "Programs\Python"
        if (Test-Path $localPrograms) {
            Get-ChildItem $localPrograms -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $env:Path = "$($_.FullName);$($_.FullName)\Scripts;$env:Path"
            }
        }
    }

    $py = Get-PythonCommand
    if (-not $py -or -not (Test-PythonVersion $py.Version)) {
        Write-Error "Python 3.9+ is required.`n  Install from https://www.python.org/downloads/ (check 'Add python.exe to PATH') and re-run."
        exit 1
    }
    Write-Step "Python $($py.Version) ready."
    return $py
}

function Invoke-Python($PythonInfo, [string[]]$PyArgs) {
    $all = @()
    $all += $PythonInfo.Args
    $all += $PyArgs
    & $PythonInfo.Exe @all
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($PythonInfo.Exe) $($all -join ' ')"
    }
}

function Install-Or-Update-Repo {
    New-Item -ItemType Directory -Path (Split-Path $InstallDir -Parent) -Force | Out-Null

    if (Test-Path (Join-Path $InstallDir ".git")) {
        Write-Step "Updating existing install at $InstallDir ..."
        Push-Location $InstallDir
        try {
            & git fetch --tags --force origin 2>$null
            & git checkout $Ref 2>$null
            # If Ref is a branch, pull latest.
            & git pull --ff-only origin $Ref 2>$null
        } finally {
            Pop-Location
        }
    } else {
        if (Test-Path $InstallDir) {
            Write-Step "Removing incomplete install directory..."
            Remove-Item -Recurse -Force $InstallDir
        }
        Write-Step "Cloning $Repo ($Ref) ..."
        & git clone --depth 1 --branch $Ref $Repo $InstallDir
        if ($LASTEXITCODE -ne 0) {
            # Branch might not support --branch on shallow for tags; fallback.
            & git clone $Repo $InstallDir
            if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
            Push-Location $InstallDir
            try {
                & git checkout $Ref
                if ($LASTEXITCODE -ne 0) { throw "git checkout $Ref failed" }
            } finally {
                Pop-Location
            }
        }
    }
}

function Install-PythonPackage($PythonInfo) {
    Write-Step "Installing Alfr3d package (editable)..."
    Invoke-Python $PythonInfo @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
    if (-not $SkipDeps) {
        $req = Join-Path $InstallDir "requirements.txt"
        # Prefer lean core deps; full channel extras are optional.
        $reqCore = Join-Path $InstallDir "requirements-core.txt"
        if (Test-Path $reqCore) {
            Write-Step "Installing core dependencies (lean install)..."
            Invoke-Python $PythonInfo @("-m", "pip", "install", "-r", $reqCore)
        } elseif (Test-Path $req) {
            Write-Step "Installing product dependencies (this may take a few minutes)..."
            Invoke-Python $PythonInfo @("-m", "pip", "install", "-r", $req)
        }
    }
    Invoke-Python $PythonInfo @("-m", "pip", "install", "-e", $InstallDir)
}

function Write-Shim($PythonInfo) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null

    # Resolve where pip put the console script, if available.
    $scriptsDir = & $PythonInfo.Exe @($PythonInfo.Args + @("-c", "import sysconfig; print(sysconfig.get_path('scripts'))")) 2>$null
    $scriptsDir = if ($scriptsDir) { $scriptsDir.Trim() } else { "" }

    $shimCmd = Join-Path $BinDir "alfr3d.cmd"
    $shimPs1 = Join-Path $BinDir "alfr3d.ps1"

    if ($scriptsDir -and (Test-Path (Join-Path $scriptsDir "alfr3d.exe"))) {
        $target = Join-Path $scriptsDir "alfr3d.exe"
        @"
@echo off
"$target" %*
"@ | Set-Content -Path $shimCmd -Encoding ASCII

        @"
& "$target" @args
if (`$null -ne `$LASTEXITCODE) { exit `$LASTEXITCODE }
"@ | Set-Content -Path $shimPs1 -Encoding UTF8
        Write-Step "Shim points at $target"
    } else {
        # Fallback: run the module from the install tree.
        $pyExe = (Get-Command $PythonInfo.Exe).Source
        $pyArgs = ($PythonInfo.Args -join " ")
        @"
@echo off
set "PYTHONPATH=$InstallDir"
"$pyExe" $pyArgs -m cli %*
"@ | Set-Content -Path $shimCmd -Encoding ASCII
        Write-Step "Shim falls back to python -m cli"
    }
}

function Ensure-UserPath([string]$Directory) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $entries = @()
    if ($userPath) {
        $entries = $userPath -split ";" | Where-Object { $_ -ne "" }
    }
    if ($entries -contains $Directory) {
        Write-Step "PATH already includes $Directory"
    } else {
        $newPath = (@($Directory) + $entries) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Step "Added $Directory to your User PATH."
    }
    if ($env:Path -notlike "*$Directory*") {
        $env:Path = "$Directory;$env:Path"
    }
}

function Ensure-Config {
    $configPath = Join-Path $InstallDir "config.json"
    $template = Join-Path $InstallDir "config-template.json"
    if (-not (Test-Path $configPath) -and (Test-Path $template)) {
        Copy-Item $template $configPath
        Write-Step "Created config.json from product template."
    }
}

# --- Main ---

Write-Host ""
Write-Title "Alfr3d installer"
Write-Step "Repo: $Repo"
Write-Step "Ref:  $Ref"
Write-Step "Dir:  $InstallDir"
Write-Host ""

Ensure-Git
$pythonInfo = Ensure-Python
Install-Or-Update-Repo
Install-PythonPackage $pythonInfo
Write-Shim $pythonInfo
Ensure-UserPath $BinDir
# Also prefer Python Scripts so `alfr3d` resolves even without the shim.
try {
    $scriptsDir = & $pythonInfo.Exe @($pythonInfo.Args + @("-c", "import sysconfig; print(sysconfig.get_path('scripts'))")) 2>$null
    if ($scriptsDir) {
        Ensure-UserPath $scriptsDir.Trim()
    }
} catch {}
Ensure-Config

Write-Host ""
Write-Ok "Alfr3d installed."
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open a new terminal (so PATH updates apply)"
Write-Host "  2. Run setup (API keys + why you're here):"
Write-Host "       alfr3d setup"
Write-Host "  3. Talk to Alfr3d:"
Write-Host "       alfr3d chat"
Write-Host "       alfr3d `"What should I focus on this week?`""
Write-Host "  4. Or start the full service (web console):"
Write-Host "       alfr3d start"
Write-Host ""
Write-Host "Help:  alfr3d help" -ForegroundColor DarkGray
Write-Host ""
