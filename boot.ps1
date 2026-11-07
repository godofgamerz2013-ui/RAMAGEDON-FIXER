$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

foreach ($required in @("requirements.txt", "src\app.py", "src\engine.py")) {
    if (-not (Test-Path (Join-Path $ProjectRoot $required))) {
        throw "Missing project file: $required"
    }
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "Python 3.12 (64-bit) was not found on PATH. Install Python and reopen PowerShell."
}

Write-Host "ApexRig-AI TEMP boot | $(& python --version)" -ForegroundColor Cyan
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[1/3] Creating isolated TEMP virtual environment..."
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
        throw "Could not create the temporary virtual environment."
    }
} else {
    Write-Host "[1/3] Reusing temporary virtual environment."
}

Write-Host "[2/3] Installing/checking dependencies..."
& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed. Check internet access and Windows Application Control."
}

Write-Host "[3/3] Starting ApexRig-AI..."
& $VenvPython src\app.py
if ($LASTEXITCODE -ne 0) {
    throw "ApexRig-AI exited with code $LASTEXITCODE."
}
