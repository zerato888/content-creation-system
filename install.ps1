# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
# Content kit installer (Windows). Source: https://github.com/zerato888/content-creation-system
# Run (policy bypass applies to this one process only):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 install --target "C:\ruta\proyecto"
# Alternative: Unblock-File .\install.ps1   or   Set-ExecutionPolicy -Scope Process Bypass
# Commands: install [--core|--module X] [--target DIR] [--yes] [--answers FILE] [--dry-run]
#           update [--to TAG] | uninstall | status | rollback | service on|off|status | cache-clean | migrate-brands
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$candidates = @(@('py', '-3'), @('python'), @('python3'))
$exe = $null; $pre = @()
foreach ($c in $candidates) {
    if (Get-Command $c[0] -ErrorAction SilentlyContinue) {
        $extra = @($c | Select-Object -Skip 1)
        & $c[0] @extra -c "import sys; sys.exit(sys.version_info < (3, 11))" 2>$null
        if ($LASTEXITCODE -eq 0) { $exe = $c[0]; $pre = $extra; break }
    }
}
if (-not $exe) {
    Write-Error "Hace falta Python 3.11 o más nuevo y no lo encontré. Instalalo desde https://www.python.org/downloads/ (marcá 'Add python.exe to PATH') y volvé a correr este comando." -ErrorAction Continue
    exit 127
}
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$here;$env:PYTHONPATH" } else { $here }
$env:PYTHONUTF8 = '1'
& $exe @pre -m installer @args
exit $LASTEXITCODE
