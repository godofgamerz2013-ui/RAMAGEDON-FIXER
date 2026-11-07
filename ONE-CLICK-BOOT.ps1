$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepoZip = "https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/archive/refs/heads/main.zip"
$InstallRoot = Join-Path $env:LOCALAPPDATA "ApexRig-AI"
$ZipPath = Join-Path $env:TEMP "ApexRig-AI-main.zip"
$ExtractRoot = Join-Path $env:TEMP "ApexRig-AI-main"

Write-Host "ApexRig-AI Bootstrap" -ForegroundColor Cyan
Write-Host "[1/4] Downloading latest repository..."
Invoke-WebRequest -Uri $RepoZip -OutFile $ZipPath

Write-Host "[2/4] Extracting repository..."
if (Test-Path $ExtractRoot) { Remove-Item $ExtractRoot -Recurse -Force }
Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractRoot -Force

$RepoFolder = Join-Path $ExtractRoot "RAMAGEDON-FIXER-main"
$Launcher = Join-Path $RepoFolder "boot.ps1"
if (-not (Test-Path $Launcher)) {
    throw "The downloaded repository does not contain boot.ps1."
}

if (-not (Test-Path (Join-Path $RepoFolder "requirements.txt")) -or
    -not (Test-Path (Join-Path $RepoFolder "src\app.py"))) {
    throw "The repository ZIP is missing requirements.txt or src\app.py. The application source must be committed before it can boot."
}

Write-Host "[3/4] Installing project files..."
if (Test-Path $InstallRoot) { Remove-Item $InstallRoot -Recurse -Force }
New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
Copy-Item -Path (Join-Path $RepoFolder "*") -Destination $InstallRoot -Recurse -Force

Write-Host "[4/4] Starting ApexRig-AI..."
& (Join-Path $InstallRoot "boot.ps1")
