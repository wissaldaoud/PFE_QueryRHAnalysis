# Script PowerShell pour mettre à jour les types de contrats
$env:PGPASSWORD = "hranalytics2026"

Write-Host "Mise a jour des types de contrats..." -ForegroundColor Yellow

psql -h localhost -U hranalytics -d hr_analytics_db -c "UPDATE employees SET contract_type = 'CDI' WHERE contract_type IS NULL;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Mise a jour reussie!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verification:" -ForegroundColor Cyan
    psql -h localhost -U hranalytics -d hr_analytics_db -c "SELECT contract_type, COUNT(*) FROM employees GROUP BY contract_type;"
} else {
    Write-Host "Erreur lors de la mise a jour" -ForegroundColor Red
}
