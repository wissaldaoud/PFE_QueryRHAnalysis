"""
🚀 GUIDE DE DÉMARRAGE RAPIDE - Module HR Analytics
==================================================

Ce script démontre comment utiliser le module HR Analytics en 5 minutes.
"""

# ============================================================================
# ÉTAPE 1 : Installation
# ============================================================================
print("""
ÉTAPE 1 : INSTALLATION
----------------------

Ouvrez un terminal et exécutez :

    cd backend
    pip install -r requirements-hr-analytics.txt

⏱️  Temps estimé : 2-3 minutes
💾 Espace disque : ~2 GB (modèle + dépendances)

Le modèle Sentence Transformer sera téléchargé automatiquement au premier usage.
""")

# ============================================================================
# ÉTAPE 2 : Import et initialisation
# ============================================================================
print("""
ÉTAPE 2 : IMPORT ET INITIALISATION
-----------------------------------
""")

from app.services.hr_analytics import HRAnalyticsService
from app.services.cv_matching import CVData, JobOffer
from app.services.training_recommendation import EmployeeProfile, TrainingCourse
from app.services.predictive_scoring import EmployeeHistory

print("✅ Imports réussis")

# Initialiser le service (télécharge le modèle si nécessaire)
print("\n📦 Initialisation du service HR Analytics...")
service = HRAnalyticsService()
print("✅ Service initialisé avec succès!\n")

# ============================================================================
# ÉTAPE 3 : Test CV Matching (30 secondes)
# ============================================================================
print("""
ÉTAPE 3 : TEST CV MATCHING
--------------------------
Comparons un CV avec une offre d'emploi...
""")

cv = CVData(
    skills=["Python", "FastAPI", "Machine Learning", "SQL"],
    experiences=["3 ans Backend Development avec Python et FastAPI"],
    job_titles=["Développeur Backend"],
    education=["Master Informatique"],
    years_of_experience=3.0
)

job = JobOffer(
    required_skills=["Python", "FastAPI", "PostgreSQL"],
    preferred_skills=["Docker", "Kubernetes"],
    job_title="Senior Backend Developer",
    description="Développement d'APIs RESTful avec Python",
    required_experience_years=3.0
)

result = service.match_cv_to_job(cv, job)

print(f"📊 Score de matching : {result.overall_score:.1%}")
print(f"   - Compétences    : {result.skills_score:.1%}")
print(f"   - Expérience     : {result.experience_score:.1%}")
print(f"✅ Compétences qui matchent : {len(result.matching_skills)}")
print(f"❌ Compétences manquantes   : {len(result.missing_required_skills)}")

# ============================================================================
# ÉTAPE 4 : Test Recommandation de Formation (30 secondes)
# ============================================================================
print("""

ÉTAPE 4 : TEST RECOMMANDATION DE FORMATION
-------------------------------------------
Recommandons des formations à un employé...
""")

employee = EmployeeProfile(
    employee_id="EMP001",
    current_skills=["Python", "SQL", "Excel"],
    training_history=[],
    current_position="Analyste RH",
    target_position="Data Analyst RH"
)

courses = [
    TrainingCourse(
        course_id="F1",
        title="Python Avancé pour Data Science",
        description="Pandas, NumPy, analyse de données",
        skills_taught=["Pandas", "NumPy", "Data Analysis"],
        level="intermédiaire",
        duration_hours=40,
        category="Data Science"
    ),
    TrainingCourse(
        course_id="F2",
        title="Power BI pour RH",
        description="Dashboards et reporting RH",
        skills_taught=["Power BI", "Data Visualization"],
        level="débutant",
        duration_hours=25,
        category="Business Intelligence"
    )
]

skills_map = {
    "Data Analyst RH": ["Python", "Pandas", "SQL", "Power BI"]
}

recs = service.recommend_trainings(
    employee=employee,
    available_courses=courses,
    required_skills_map=skills_map,
    top_n=2
)

print(f"📚 Top {len(recs)} formations recommandées :")
for i, rec in enumerate(recs, 1):
    print(f"   {i}. {rec.course.title}")
    print(f"      Pertinence: {rec.relevance_score:.1%} | Priorité: {rec.priority}")

# ============================================================================
# ÉTAPE 5 : Test Scoring Prédictif (30 secondes)
# ============================================================================
print("""

ÉTAPE 5 : TEST SCORING PRÉDICTIF
---------------------------------
Calculons les scores de risque de churn...
""")

history = EmployeeHistory(
    employee_id="EMP101",
    tenure_months=18,
    absences_last_year=12,
    average_performance_score=3.2,
    promotion_count=0,
    training_hours_last_year=5,
    salary_percentile=25,
    department="IT",
    manager_changes_count=3,
    overtime_hours_monthly=35,
    team_size=8,
    remote_work_percentage=20
)

score = service.calculate_predictive_scores(history)

print(f"👤 Employé {score.employee_id}")
print(f"🔮 Risque de churn  : {score.churn_risk_score:.1%} [{score.risk_level.upper()}]")
print(f"📊 Performance      : {score.performance_score:.1%}")
print(f"💪 Engagement       : {score.engagement_score:.1%}")
print(f"📝 {len(score.recommendations)} recommandations RH générées")

# ============================================================================
# ÉTAPE 6 : Lancer l'API REST (optionnel)
# ============================================================================
print("""

ÉTAPE 6 : LANCER L'API REST (OPTIONNEL)
----------------------------------------

Pour utiliser le module via API REST :

1. Démarrer le serveur :
   
   uvicorn app_hr_analytics_example:app --reload

2. Ouvrir la documentation interactive :
   
   http://localhost:8000/docs

3. Tester les endpoints avec les exemples dans :
   
   hr_analytics_api_examples.json

""")

# ============================================================================
# ÉTAPE 7 : Prochaines étapes
# ============================================================================
print("""
ÉTAPE 7 : PROCHAINES ÉTAPES
----------------------------

✅ Intégrer dans votre application FastAPI existante
✅ Connecter à votre base de données RH
✅ Personnaliser les poids et seuils selon vos besoins
✅ Ajouter des dashboards de visualisation
✅ Déployer en production avec Docker

📚 Documentation complète : HR_ANALYTICS_README.md
🧪 Tests complets         : python test_hr_analytics_full.py
📖 Exemples API          : hr_analytics_api_examples.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 FÉLICITATIONS ! Vous êtes prêt à utiliser HR Analytics ! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions ? Consultez HR_ANALYTICS_README.md
""")
