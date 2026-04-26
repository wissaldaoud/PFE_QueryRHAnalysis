# Migration Script - Activer le nouveau moteur de requêtes avec Claude API
# Ce script backup les anciens fichiers et active les nouveaux

Write-Host "🔄 MIGRATION MOTEUR DE REQUÊTES - Claude API + DWH" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1: Backup anciens fichiers
Write-Host "📦 Étape 1: Backup anciens fichiers..." -ForegroundColor Yellow

$backupFolder = "C:\Users\wdaoud\Desktop\test\backend\backup_old_query_engine"
if (!(Test-Path $backupFolder)) {
    New-Item -ItemType Directory -Path $backupFolder | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Backup service
$oldService = "C:\Users\wdaoud\Desktop\test\backend\app\services\query_engine_service.py"
if (Test-Path $oldService) {
    Copy-Item $oldService "$backupFolder\query_engine_service_$timestamp.py"
    Write-Host "  ✅ Backup: query_engine_service.py" -ForegroundColor Green
}

# Backup router
$oldRouter = "C:\Users\wdaoud\Desktop\test\backend\app\api\v1\endpoints\query_engine.py"
if (Test-Path $oldRouter) {
    Copy-Item $oldRouter "$backupFolder\query_engine_$timestamp.py"
    Write-Host "  ✅ Backup: query_engine.py (router)" -ForegroundColor Green
}

Write-Host ""

# Étape 2: Remplacer par nouveaux fichiers
Write-Host "🔀 Étape 2: Activation nouveaux fichiers..." -ForegroundColor Yellow

# Remplacer service
$newService = "C:\Users\wdaoud\Desktop\test\backend\app\services\query_engine_service_new.py"
if (Test-Path $newService) {
    Remove-Item $oldService -Force -ErrorAction SilentlyContinue
    Move-Item $newService $oldService
    Write-Host "  ✅ Activé: query_engine_service.py (Claude API + DWH)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Fichier manquant: query_engine_service_new.py" -ForegroundColor Red
}

# Remplacer router
$newRouter = "C:\Users\wdaoud\Desktop\test\backend\app\api\v1\endpoints\query_engine_new.py"
if (Test-Path $newRouter) {
    Remove-Item $oldRouter -Force -ErrorAction SilentlyContinue
    Move-Item $newRouter $oldRouter
    Write-Host "  ✅ Activé: query_engine.py (nouveau router)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Fichier manquant: query_engine_new.py" -ForegroundColor Red
}

Write-Host ""

# Étape 3: Vérifier .env
Write-Host "🔍 Étape 3: Vérification configuration..." -ForegroundColor Yellow

$envFile = "C:\Users\wdaoud\Desktop\test\backend\.env"
$envContent = Get-Content $envFile -Raw

$checks = @(
    @{Name="DWH_HOST"; Required=$true},
    @{Name="DWH_PORT"; Required=$true},
    @{Name="DWH_DB"; Required=$true},
    @{Name="DWH_USER"; Required=$true},
    @{Name="DWH_PASSWORD"; Required=$true},
    @{Name="ANTHROPIC_API_KEY"; Required=$true}
)

$allValid = $true

foreach ($check in $checks) {
    if ($envContent -match "$($check.Name)=(.+)") {
        $value = $matches[1].Trim()
        if ($value -and $value -ne "") {
            Write-Host "  ✅ $($check.Name) configuré" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $($check.Name) vide!" -ForegroundColor Red
            $allValid = $false
        }
    } else {
        Write-Host "  ❌ $($check.Name) manquant!" -ForegroundColor Red
        $allValid = $false
    }
}

Write-Host ""

# Étape 4: Test connexion DWH
Write-Host "🔌 Étape 4: Test connexion DWH..." -ForegroundColor Yellow

$testScript = @"
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DWH_HOST', 'localhost'),
        port=os.getenv('DWH_PORT', '5432'),
        database=os.getenv('DWH_DB', 'hr_datawarehouse'),
        user=os.getenv('DWH_USER', 'hr_user'),
        password=os.getenv('DWH_PASSWORD', 'hr_password123')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT current_database()')
    db_name = cursor.fetchone()[0]
    print(f'✅ Connexion DWH réussie: {db_name}')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Erreur connexion DWH: {e}')
"@

Set-Content -Path "C:\Users\wdaoud\Desktop\test\backend\test_dwh_connection.py" -Value $testScript
C:\Users\wdaoud\Desktop\test\backend\env\Scripts\python.exe C:\Users\wdaoud\Desktop\test\backend\test_dwh_connection.py

Write-Host ""

# Résumé
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ DE LA MIGRATION" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Anciens fichiers sauvegardés dans:" -ForegroundColor Green
Write-Host "   $backupFolder" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Nouveaux fichiers activés:" -ForegroundColor Green
Write-Host "   - query_engine_service.py (Claude API + DWH)" -ForegroundColor Gray
Write-Host "   - query_engine.py (nouveau router)" -ForegroundColor Gray
Write-Host ""

if ($allValid) {
    Write-Host "✅ Configuration .env complète" -ForegroundColor Green
} else {
    Write-Host "⚠️  Configuration .env incomplète - ajoutez les variables manquantes!" -ForegroundColor Red
}

Write-Host ""
Write-Host "📖 Documentation: backend/QUERY_ENGINE_README.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 PROCHAINES ÉTAPES:" -ForegroundColor Cyan
Write-Host "   1. Ajoutez votre ANTHROPIC_API_KEY dans .env" -ForegroundColor White
Write-Host "   2. Vérifiez que hr_datawarehouse existe et contient des données" -ForegroundColor White
Write-Host "   3. Redémarrez le backend" -ForegroundColor White
Write-Host "   4. Testez: POST /api/v1/query/execute" -ForegroundColor White
Write-Host ""
Write-Host "✨ Migration terminée!" -ForegroundColor Green
