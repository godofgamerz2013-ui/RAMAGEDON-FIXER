$ErrorActionPreference = "Stop"

# ApexRig-AI one-command launcher.
# Run this script from the extracted repository root.

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path (Join-Path $ProjectRoot "requirements.txt")) -or
    -not (Test-Path (Join-Path $ProjectRoot "src\app.py"))) {
    Write-Host "ApexRig-AI source files were not found." -ForegroundColor Red
    Write-Host "Extract the complete project ZIP, then run .\boot.ps1 from the folder containing requirements.txt and src\app.py."
    exit 1
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    Write-Host "Python was not found. Install Python 3.12 (64-bit), then reopen PowerShell." -ForegroundColor Red
    exit 1
}

Write-Host "ApexRig-AI boot sequence" -ForegroundColor Cyan
Write-Host "Using: $(& python --version)"

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[1/3] Creating local virtual environment..."
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
        throw "Could not create .venv. Check Python installation and Windows permissions."
    }
} else {
    Write-Host "[1/3] Reusing existing .venv"
}

Write-Host "[2/3] Installing/checking project dependencies..."
& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Check network access and Windows Application Control policy."
}

Write-Host "[3/3] Launching ApexRig-AI..."
& $VenvPython src\app.py
if ($LASTEXITCODE -ne 0) {
    throw "ApexRig-AI exited with an error (code $LASTEXITCODE)."
}
