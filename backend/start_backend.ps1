# Script de démarrage backend avec encodage UTF-8 propre
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  DEMARRAGE BACKEND (UTF-8 SAFE)" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Nettoyer les variables d'environnement PostgreSQL qui peuvent interférer
$env:PGAPPNAME = $null
$env:PGDATABASE = $null
$env:PGHOST = $null
$env:PGPORT = $null
$env:PGUSER = $null
$env:PGPASSWORD = $null
$env:PGPASSFILE = $null
$env:PGSERVICE = $null
$env:PGSERVICEFILE = $null
$env:PGSYSCONFDIR = $null
$env:PGOPTIONS = $null

# 2. Forcer l'encodage UTF-8 partout
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PGCLIENTENCODING = "UTF8"
$env:LC_ALL = "en_US.UTF-8"
$env:LANG = "en_US.UTF-8"

# 3. Définir le PYTHONPATH
$env:PYTHONPATH = "C:\Users\wdaoud\Desktop\test\backend"

# 4. Changer de répertoire
Set-Location "C:\Users\wdaoud\Desktop\test\backend"

Write-Host "`n Environment configuré:" -ForegroundColor Green
Write-Host "  - PYTHONUTF8: $env:PYTHONUTF8"
Write-Host "  - PGCLIENTENCODING: $env:PGCLIENTENCODING"
Write-Host "  - PYTHONPATH: $env:PYTHONPATH"

Write-Host "`n Démarrage du serveur..." -ForegroundColor Yellow

# 5. Lancer le serveur
C:\Users\wdaoud\Desktop\test\backend\env\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
