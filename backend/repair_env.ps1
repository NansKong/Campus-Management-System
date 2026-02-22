param(
    [string]$PythonPath = "C:\Users\ASUS\AppData\Local\Python\bin\python.exe"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$venvDir = Join-Path $backendDir "venv"
$tmpDir = Join-Path $repoRoot ".tmp"

if (!(Test-Path $PythonPath)) {
    throw "Python not found at: $PythonPath"
}

Write-Host "Using Python:" $PythonPath

if (Test-Path $venvDir) {
    Remove-Item -Recurse -Force $venvDir
}

& $PythonPath -m venv $venvDir

if (!(Test-Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir | Out-Null
}

$env:TEMP = $tmpDir
$env:TMP = $tmpDir

$venvPython = Join-Path $venvDir "Scripts\python.exe"

Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

Write-Host "Installing backend requirements..."
& $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt")

Write-Host "Running DB checks..."
Push-Location $backendDir
try {
    & $venvPython test_db_connection.py
    & $venvPython diagnose.py
}
finally {
    Pop-Location
}

Write-Host "Environment repair complete."
