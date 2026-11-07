# GOD OF GAMERZ online one-command starter
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$uri = "https://raw.githubusercontent.com/godofgamerz2013-ui/RAMAGEDON-FIXER/main/domain/manraj.xo.je/scripts/bootstrap.ps1"
$tempScript = Join-Path $env:TEMP ("gog-bootstrap-" + [guid]::NewGuid().ToString("N") + ".ps1")
try {
    Invoke-WebRequest -Uri $uri -OutFile $tempScript -UseBasicParsing
    if (!(Test-Path $tempScript) -or (Get-Item $tempScript).Length -lt 100) {
        throw "Bootstrap download failed or returned an invalid file."
    }
    & $tempScript
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
}
