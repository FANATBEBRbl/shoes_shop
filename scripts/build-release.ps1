$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonExe = Join-Path $projectRoot '.venv-build/Scripts/python.exe'
if (!(Test-Path -LiteralPath $pythonExe)) {
    throw 'Create .venv-build and install requirements-build.txt first.'
}
& $pythonExe -m PyInstaller --clean --noconfirm ShoeStore.spec
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
$releaseRoot = Join-Path $projectRoot ('output/ShoeStore-release-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force "$releaseRoot/application", "$releaseRoot/deployment/database", "$releaseRoot/deployment/docker" | Out-Null
Copy-Item -LiteralPath 'dist/ShoeStore' -Destination "$releaseRoot/application" -Recurse
Copy-Item -LiteralPath 'compose.yaml', '.env.example' -Destination "$releaseRoot/deployment"
Copy-Item -LiteralPath 'docker/db-check' -Destination "$releaseRoot/deployment/docker" -Recurse
Copy-Item -LiteralPath 'database/shoe_store.sql' -Destination "$releaseRoot/deployment/database"
Copy-Item -LiteralPath 'README.md', 'INSTALL.md', 'config.ini.example' -Destination $releaseRoot
$forbidden = Get-ChildItem -LiteralPath $releaseRoot -Recurse -Force | Where-Object {
    $_.Name -in @('.env', 'config.ini', '.git', '.venv', '.venv-build', 'backups', '__pycache__')
}
if ($forbidden) { throw 'Release contains local files; packaging stopped.' }
Compress-Archive -LiteralPath $releaseRoot -DestinationPath "$releaseRoot.zip"
Write-Output "Release: $releaseRoot.zip"
