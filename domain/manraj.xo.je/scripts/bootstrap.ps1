[CmdletBinding()]
param(
    [string]$RepositoryZip = "https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/archive/refs/heads/main.zip",
    [switch]$KeepFiles
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    $workRoot = Join-Path $env:TEMP ("GOD-OF-GAMERZ-" + [guid]::NewGuid().ToString("N"))
    $zipPath = Join-Path $workRoot "repository.zip"
    $extractPath = Join-Path $workRoot "source"
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null

    Write-Host "[GOG] Downloading repository..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $RepositoryZip -OutFile $zipPath -UseBasicParsing
    if (!(Test-Path $zipPath) -or (Get-Item $zipPath).Length -lt 1000) {
        throw "Repository download is missing or unexpectedly small."
    }

    Write-Host "[GOG] Extracting files..." -ForegroundColor Cyan
    Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath -Force

    $repoRoot = Get-ChildItem -LiteralPath $extractPath -Directory | Select-Object -First 1
    if (!$repoRoot) { throw "The downloaded ZIP did not contain a repository folder." }

    # Select the intended launcher by name, preferring common root-level entry points.
    $preferredNames = @("GOG-BOOT.ps1", "BOOT.ps1", "START.ps1", "Install.ps1", "Run.ps1")
    $launcher = $null
    foreach ($name in $preferredNames) {
        $candidate = Get-ChildItem -LiteralPath $repoRoot.FullName -Filter $name -File -Recurse |
            Sort-Object { $_.FullName.Length } | Select-Object -First 1
        if ($candidate) { $launcher = $candidate; break }
    }

    if (!$launcher) {
        $scripts = @(Get-ChildItem -LiteralPath $repoRoot.FullName -Filter "*.ps1" -File -Recurse |
            Where-Object { $_.Name -notin @("bootstrap.ps1", "online.ps1") } |
            Sort-Object FullName)
        if ($scripts.Count -eq 1) { $launcher = $scripts[0] }
        elseif ($scripts.Count -gt 1) {
            Write-Host "PowerShell files found:" -ForegroundColor Yellow
            $scripts | ForEach-Object { Write-Host (" - " + $_.FullName) }
            throw "Multiple scripts found and no recognised launcher name. Rename the intended entry point to GOG-BOOT.ps1."
        }
    }

    if (!$launcher) {
        throw "No PowerShell launcher was found in the repository. Add GOG-BOOT.ps1 to the repository root."
    }

    Write-Host ("[GOG] Running " + $launcher.Name) -ForegroundColor Green
    & $launcher.FullName
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Launcher returned exit code $LASTEXITCODE."
    }
    Write-Host "[GOG] Launcher finished." -ForegroundColor Green

    if (!$KeepFiles) {
        Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host ("Files retained at: " + $workRoot) -ForegroundColor DarkGray
    }
}
catch {
    Write-Error ("[GOG] " + $_.Exception.Message)
    exit 1
}
