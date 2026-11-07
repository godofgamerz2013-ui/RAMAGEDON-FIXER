$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepoZip = "https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/archive/refs/heads/main.zip"
$InstallRoot = Join-Path $env:LOCALAPPDATA "ApexRig-AI"
$VersionsRoot = Join-Path $InstallRoot "versions"
$BuildId = Get-Date -Format "yyyyMMdd-HHmmss"
$VersionFolder = Join-Path $VersionsRoot $BuildId
$ZipPath = Join-Path $env:TEMP "ApexRig-AI-main-$BuildId.zip"
$ExtractRoot = Join-Path $env:TEMP "ApexRig-AI-main-$BuildId"

Write-Host "ApexRig-AI Bootstrap" -ForegroundColor Cyan
Write-Host "[1/4] Downloading latest repository..."
Invoke-WebRequest -Uri $RepoZip -OutFile $ZipPath

Write-Host "[2/4] Extracting repository..."
Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractRoot -Force

$RepoFolder = Join-Path $ExtractRoot "RAMAGEDON-FIXER-main"
$Launcher = Join-Path $RepoFolder "boot.ps1"
if (-not (Test-Path $Launcher)) {
    throw "The downloaded repository does not contain boot.ps1."
}

if (-not (Test-Path (Join-Path $RepoFolder "requirements.txt")) -or
    -not (Test-Path (Join-Path $RepoFolder "src\app.py"))) {
    throw "The repository ZIP is missing requirements.txt or src\app.py. The complete application source must be committed before it can boot."
}

Write-Host "[3/4] Installing into a fresh version folder..."
# Never delete/overwrite the previous install: a running app may have files locked.
New-Item -ItemType Directory -Path $VersionsRoot -Force | Out-Null
New-Item -ItemType Directory -Path $VersionFolder -Force | Out-Null
Copy-Item -Path (Join-Path $RepoFolder "*") -Destination $VersionFolder -Recurse -Force

Write-Host "[4/4] Starting ApexRig-AI from $VersionFolder..."
& (Join-Path $VersionFolder "boot.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "ApexRig-AI launcher exited with code $LASTEXITCODE."
}

Write-Host "Install retained at: $VersionFolder" -ForegroundColor Green
Write-Host "Previous versions were left untouched." -ForegroundColor DarkGray
