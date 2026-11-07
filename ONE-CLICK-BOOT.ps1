$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepoZip = "https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/archive/refs/heads/main.zip"
$TempBase = Join-Path $env:TEMP "ApexRig-AI"
$RunId = [guid]::NewGuid().ToString("N")
$RunRoot = Join-Path $TempBase "run-$RunId"
$ZipPath = Join-Path $RunRoot "main.zip"
$ExtractRoot = Join-Path $RunRoot "extract"

Write-Host "ApexRig-AI | TEMP bootstrap" -ForegroundColor Cyan

# Recover folders left behind by an unexpected shutdown. Ignore files currently locked by a live process.
New-Item -ItemType Directory -Path $TempBase -Force | Out-Null
Get-ChildItem -LiteralPath $TempBase -Directory -Filter "run-*" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -ne $RunRoot } |
    ForEach-Object {
        try { Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop } catch {}
    }

try {
    New-Item -ItemType Directory -Path $RunRoot -Force | Out-Null
    Write-Host "[1/4] Downloading latest GitHub main branch..."
    Invoke-WebRequest -Uri $RepoZip -OutFile $ZipPath

    Write-Host "[2/4] Extracting into Windows TEMP..."
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractRoot -Force
    $RepoFolder = Join-Path $ExtractRoot "RAMAGEDON-FIXER-main"

    foreach ($required in @("boot.ps1", "requirements.txt", "src\app.py", "src\engine.py")) {
        if (-not (Test-Path (Join-Path $RepoFolder $required))) {
            throw "Repository is missing required file: $required"
        }
    }

    Write-Host "[3/4] Launching from TEMP (no permanent application install)..."
    & (Join-Path $RepoFolder "boot.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "ApexRig-AI exited with code $LASTEXITCODE"
    }
}
finally {
    Write-Host "[4/4] Removing temporary application files..."
    try { Remove-Item -LiteralPath $RunRoot -Recurse -Force -ErrorAction Stop }
    catch { Write-Warning "Some TEMP files are still locked. They will be retried on the next launch." }
}
