# ═══════════════════════════════════════════════════════════════
# SCRIPT COMPLET D'ENTRAÎNEMENT MODÈLE TURNOVER
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ENTRAÎNEMENT MODÈLE TURNOVER - DONNÉES QLIK RÉELLES" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Vérifier qu'on est dans le bon dossier
if (-not (Test-Path "scripts\extract_qlik_data.py")) {
    Write-Host "❌ Erreur : Lancez ce script depuis backend/" -ForegroundColor Red
    Write-Host "   cd backend" -ForegroundColor Yellow
    Write-Host "   .\ml\scripts\run_training.ps1" -ForegroundColor Yellow
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1 : EXTRACTION DES DONNÉES
# ═══════════════════════════════════════════════════════════════

Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ ÉTAPE 1/3 : EXTRACTION DES DONNÉES DEPUIS POSTGRESQL   │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

try {
    python scripts\extract_qlik_data.py
    if ($LASTEXITCODE -ne 0) {
        throw "Extraction échouée"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors de l'extraction des données" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vérifiez :" -ForegroundColor Yellow
    Write-Host "   1. PostgreSQL est démarré" -ForegroundColor White
    Write-Host "   2. dwh_connection.py contient les bons credentials" -ForegroundColor White
    Write-Host "   3. Les tables dim.dim_employe, fait.fait_contrat existent" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ Extraction terminée" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2 : ENTRAÎNEMENT DU MODÈLE
# ═══════════════════════════════════════════════════════════════

Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ ÉTAPE 2/3 : ENTRAÎNEMENT DU MODÈLE XGBOOST             │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

try {
    python ml\scripts\train_turnover_real.py
    if ($LASTEXITCODE -ne 0) {
        throw "Entraînement échoué"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors de l'entraînement" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vérifiez :" -ForegroundColor Yellow
    Write-Host "   1. Le fichier ml/data/employes_qlik_historique.csv existe" -ForegroundColor White
    Write-Host "   2. Il contient au moins 100 lignes" -ForegroundColor White
    Write-Host "   3. xgboost est installé : pip install xgboost" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ Entraînement terminé" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3 : TEST DU MODÈLE
# ═══════════════════════════════════════════════════════════════

Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ ÉTAPE 3/3 : TEST DU MODÈLE                             │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

try {
    python test_turnover_real.py
    if ($LASTEXITCODE -ne 0) {
        throw "Test échoué"
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors du test" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Vérifiez :" -ForegroundColor Yellow
    Write-Host "   1. Le fichier ml/models/turnover_model_real.pkl existe" -ForegroundColor White
    Write-Host "   2. shap est installé : pip install shap" -ForegroundColor White
    Write-Host ""
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  🎉 PROCESSUS TERMINÉ AVEC SUCCÈS !" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Fichiers générés :" -ForegroundColor Cyan
Write-Host "   ✅ ml/data/employes_qlik_historique.csv" -ForegroundColor White
Write-Host "   ✅ ml/models/turnover_model_real.pkl" -ForegroundColor White
Write-Host "   ✅ ml/models/turnover_features.pkl" -ForegroundColor White

Write-Host ""
Write-Host "💡 Le modèle est maintenant opérationnel !" -ForegroundColor Yellow
Write-Host "   Il sera automatiquement utilisé par predictive_scoring.py" -ForegroundColor White

Write-Host ""
Write-Host "➡️  Prochaine étape : Démarrer le backend" -ForegroundColor Cyan
Write-Host "   python run_server.py" -ForegroundColor White

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
