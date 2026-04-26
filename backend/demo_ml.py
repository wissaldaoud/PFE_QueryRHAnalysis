"""
Demo rapide du système ML - Test avec un employé réel
"""
from app.services.predictive_scoring_ml import PredictiveScorerML
from app.db.base import SessionLocal
from app.models.employee import Employee
from app.models.department import Department  # Import explicite requis
from datetime import datetime
import json

# Charger le scorer ML
scorer = PredictiveScorerML(model_dir="models")

# Charger un employé réel de la DB
db = SessionLocal()
employee = db.query(Employee).filter(Employee.id == 282).first()

if employee:
    # Calculer âge et ancienneté
    today = datetime.now().date()
    age = (today - employee.date_of_birth).days // 365 if employee.date_of_birth else 30
    anciennete = (today - employee.hire_date).days / 365.25
    
    # Préparer les données
    employee_data = {
        "employee_id": str(employee.id),
        "employee_code": employee.employee_code,
        "age": age,
        "anciennete_annees": anciennete,
        "job_title": employee.job_title or "Unknown",
        "department_name": employee.department.name if employee.department else "Unknown",
        "salary": employee.salary
    }
    
    # Scorer avec ML
    score = scorer.score(employee_data)
    
    # Afficher le résultat
    print("=" * 70)
    print("🤖 DÉMONSTRATION DU SYSTÈME ML - PRÉDICTION DE TURNOVER")
    print("=" * 70)
    print(f"\n📋 EMPLOYÉ: {employee.first_name} {employee.last_name}")
    print(f"   Code: {employee.employee_code}")
    print(f"   Poste: {employee.job_title or 'N/A'}")
    print(f"   Département: {employee.department.name if employee.department else 'N/A'}")
    print(f"   Âge: {age} ans")
    print(f"   Ancienneté: {anciennete:.1f} ans")
    
    print(f"\n🎯 SCORES PRÉDICTIFS ML:")
    print(f"   • Risque de Churn: {score.churn_risk_score:.1%} ({score.risk_level.upper()})")
    print(f"   • Performance: {score.performance_score:.1%}")
    print(f"   • Engagement: {score.engagement_score:.1%}")
    print(f"   • Confiance: {score.prediction_confidence:.1%}")
    
    print(f"\n🔍 TOP 5 FACTEURS SHAP (Explicabilité):")
    for i, (feature, shap_val) in enumerate(score.key_factors, 1):
        direction = "⬆️ Augmente" if shap_val > 0 else "⬇️ Diminue"
        print(f"   {i}. {feature:30s} {direction:15s} risque ({shap_val:+.3f})")
    
    print(f"\n💡 RECOMMANDATIONS RH:")
    for i, rec in enumerate(score.recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\n📊 MODÈLE: {score.model_version}")
    print("=" * 70)
    
else:
    print("Employé 282 non trouvé dans la base de données")

db.close()
