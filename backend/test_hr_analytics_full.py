"""
Tests pour le module HR Analytics avec données fictives
Tests unitaires et d'intégration
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.hr_analytics import HRAnalyticsService
from app.services.cv_matching import CVData, JobOffer
from app.services.training_recommendation import EmployeeProfile, TrainingCourse
from app.services.predictive_scoring import EmployeeHistory


def test_cv_matching():
    """Test du CV Matching avec données fictives"""
    print("\n" + "="*80)
    print("TEST 1: CV MATCHING")
    print("="*80)
    
    # Données fictives d'un CV
    cv = CVData(
        skills=[
            "Python", "FastAPI", "Machine Learning", "SQL", "Docker",
            "Data Analysis", "Pandas", "Scikit-learn", "Git"
        ],
        experiences=[
            "Développeur Backend avec 3 ans d'expérience en Python et FastAPI",
            "Création d'APIs RESTful et microservices",
            "Développement de modèles ML pour prédiction",
            "Gestion de bases de données PostgreSQL"
        ],
        job_titles=[
            "Développeur Backend Python",
            "Data Scientist Junior",
            "Stagiaire Développement"
        ],
        education=[
            "Master en Informatique et Data Science",
            "Licence en Mathématiques Appliquées"
        ],
        years_of_experience=4.5
    )
    
    # Offre d'emploi fictive
    job = JobOffer(
        required_skills=[
            "Python", "FastAPI", "PostgreSQL", "Docker", "Machine Learning"
        ],
        preferred_skills=[
            "Kubernetes", "MLflow", "React", "CI/CD"
        ],
        job_title="Senior Backend Developer - ML Platform",
        description="Développement d'une plateforme ML avec Python, FastAPI, et Docker. "
                   "Responsabilité de créer des APIs pour modèles ML en production.",
        required_experience_years=3.0,
        required_education=["Master en Informatique ou équivalent"]
    )
    
    # Initialisation du service
    print("\n📦 Initialisation du service HR Analytics...")
    service = HRAnalyticsService(enable_cv_matching=True)
    
    # CV Matching
    print("\n🔍 Matching en cours...\n")
    result = service.match_cv_to_job(cv, job)
    
    print(f"📊 RÉSULTATS DU MATCHING")
    print("-" * 80)
    print(f"Score Global:        {result.overall_score:.1%} {'✅' if result.overall_score >= 0.7 else '⚠️'}")
    print(f"  - Compétences:     {result.skills_score:.1%}")
    print(f"  - Expérience:      {result.experience_score:.1%}")
    print(f"  - Titre de poste:  {result.title_score:.1%}")
    print(f"  - Éducation:       {result.education_score:.1%}")
    
    print(f"\n✅ Compétences correspondantes ({len(result.matching_skills)}):")
    for skill in result.matching_skills[:5]:
        print(f"   • {skill}")
    
    if result.missing_required_skills:
        print(f"\n❌ Compétences requises manquantes ({len(result.missing_required_skills)}):")
        for skill in result.missing_required_skills:
            print(f"   • {skill}")
    
    if result.missing_preferred_skills:
        print(f"\n⚠️  Compétences préférées manquantes ({len(result.missing_preferred_skills)}):")
        for skill in result.missing_preferred_skills[:3]:
            print(f"   • {skill}")
    
    print(f"\n💡 RECOMMANDATIONS:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"   {i}. {rec}")
    
    return service


def test_training_recommendation(service):
    """Test de la recommandation de formation"""
    print("\n" + "="*80)
    print("TEST 2: RECOMMANDATION DE FORMATION")
    print("="*80)
    
    # Profil d'employé fictif
    employee = EmployeeProfile(
        employee_id="EMP001",
        current_skills=[
            "Python", "SQL", "Excel", "PowerPoint", "Microsoft Office"
        ],
        training_history=[
            "Introduction à Python",
            "SQL pour débutants"
        ],
        current_position="Analyste RH Junior",
        target_position="Data Analyst RH",
        interests=["Data Science", "Analytics", "Visualisation de données"],
        department="Ressources Humaines"
    )
    
    # Catalogue de formations fictives
    courses = [
        TrainingCourse(
            course_id="FORM001",
            title="Python Avancé pour Data Science",
            description="Formation avancée en Python couvrant Pandas, NumPy, et analyse de données",
            skills_taught=["Pandas", "NumPy", "Data Analysis", "Python Avancé"],
            level="intermédiaire",
            duration_hours=40,
            category="Data Science",
            prerequisites=["Python de base"]
        ),
        TrainingCourse(
            course_id="FORM002",
            title="Introduction à Machine Learning",
            description="Concepts ML, Scikit-learn, et applications RH",
            skills_taught=["Machine Learning", "Scikit-learn", "ML pour RH"],
            level="intermédiaire",
            duration_hours=35,
            category="Machine Learning",
            prerequisites=["Python", "Statistiques"]
        ),
        TrainingCourse(
            course_id="FORM003",
            title="Visualisation de données avec Tableau",
            description="Créer des dashboards RH interactifs avec Tableau",
            skills_taught=["Tableau", "Data Visualization", "Dashboards"],
            level="débutant",
            duration_hours=20,
            category="Visualisation",
            prerequisites=None
        ),
        TrainingCourse(
            course_id="FORM004",
            title="Analytics RH Prédictif",
            description="Prédiction du churn, analyse de performance avec données RH",
            skills_taught=["HR Analytics", "Predictive Analytics", "Python", "Statistics"],
            level="avancé",
            duration_hours=50,
            category="HR Analytics",
            prerequisites=["Python", "Statistiques", "ML de base"]
        ),
        TrainingCourse(
            course_id="FORM005",
            title="Power BI pour RH",
            description="Création de reportings RH avec Power BI",
            skills_taught=["Power BI", "DAX", "Reporting RH"],
            level="intermédiaire",
            duration_hours=25,
            category="Business Intelligence",
            prerequisites=["Excel avancé"]
        ),
        TrainingCourse(
            course_id="FORM006",
            title="Leadership et Management",
            description="Développement des compétences de leadership",
            skills_taught=["Leadership", "Team Management", "Communication"],
            level="intermédiaire",
            duration_hours=30,
            category="Soft Skills",
            prerequisites=None
        )
    ]
    
    # Mapping des compétences par poste
    required_skills_map = {
        "Data Analyst RH": [
            "Python", "Pandas", "SQL", "Data Visualization",
            "Statistics", "Excel Avancé", "Power BI ou Tableau"
        ],
        "HR Analytics Manager": [
            "Python", "Machine Learning", "HR Analytics",
            "Leadership", "Predictive Analytics", "Statistics"
        ]
    }
    
    print(f"\n👤 Profil de l'employé: {employee.employee_id}")
    print(f"   Poste actuel: {employee.current_position}")
    print(f"   Poste visé: {employee.target_position}")
    print(f"   Compétences actuelles: {', '.join(employee.current_skills[:5])}")
    
    print(f"\n🎓 Génération des recommandations...\n")
    
    recommendations = service.recommend_trainings(
        employee=employee,
        available_courses=courses,
        required_skills_map=required_skills_map,
        top_n=5
    )
    
    print(f"📚 TOP 5 FORMATIONS RECOMMANDÉES")
    print("-" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        priority_emoji = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
        emoji = priority_emoji.get(rec.priority, "⚪")
        
        print(f"\n{i}. {rec.course.title}")
        print(f"   Score de pertinence: {rec.relevance_score:.1%} | Priorité: {emoji} {rec.priority.upper()}")
        print(f"   Durée: {rec.course.duration_hours}h | Niveau: {rec.course.level}")
        
        if rec.skill_gap_addressed:
            print(f"   Compétences manquantes comblées: {', '.join(rec.skill_gap_addressed[:3])}")
        
        print(f"   💡 {rec.reasoning}")


def test_predictive_scoring(service):
    """Test du scoring prédictif"""
    print("\n" + "="*80)
    print("TEST 3: SCORING RH PRÉDICTIF")
    print("="*80)
    
    # Historiques fictifs de plusieurs employés
    employees_data = [
        {
            "employee_id": "EMP101",
            "name": "Marie Dupont",
            "profile": "Risque élevé",
            "history": EmployeeHistory(
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
                remote_work_percentage=20,
                last_salary_increase_months=18,
                feedback_score=3.0,
                engagement_survey_score=3.5
            )
        },
        {
            "employee_id": "EMP102",
            "name": "Ahmed Benali",
            "profile": "Top Performer",
            "history": EmployeeHistory(
                employee_id="EMP102",
                tenure_months=48,
                absences_last_year=3,
                average_performance_score=4.7,
                promotion_count=2,
                training_hours_last_year=45,
                salary_percentile=85,
                department="Engineering",
                manager_changes_count=1,
                overtime_hours_monthly=10,
                team_size=12,
                remote_work_percentage=60,
                last_salary_increase_months=8,
                feedback_score=4.8,
                engagement_survey_score=8.5
            )
        },
        {
            "employee_id": "EMP103",
            "name": "Sophie Martin",
            "profile": "Risque moyen",
            "history": EmployeeHistory(
                employee_id="EMP103",
                tenure_months=28,
                absences_last_year=7,
                average_performance_score=3.8,
                promotion_count=1,
                training_hours_last_year=22,
                salary_percentile=55,
                department="Marketing",
                manager_changes_count=2,
                overtime_hours_monthly=15,
                team_size=6,
                remote_work_percentage=40,
                last_salary_increase_months=14,
                feedback_score=3.9,
                engagement_survey_score=6.0
            )
        }
    ]
    
    print("\n🔮 Calcul des scores prédictifs...\n")
    
    for emp_data in employees_data:
        score = service.calculate_predictive_scores(emp_data["history"])
        
        print(f"👤 {emp_data['name']} ({emp_data['employee_id']}) - {emp_data['profile']}")
        print("-" * 80)
        print(f"📊 SCORES PRÉDICTIFS:")
        print(f"   • Risque de churn:    {score.churn_risk_score:.1%} [{score.risk_level.upper()}]")
        print(f"   • Performance:        {score.performance_score:.1%}")
        print(f"   • Engagement:         {score.engagement_score:.1%}")
        print(f"   • Confiance prédiction: {score.prediction_confidence:.1%}")
        
        if score.key_factors:
            print(f"\n🔑 Facteurs clés:")
            for factor, contribution in score.key_factors[:3]:
                direction = "↑" if contribution > 0 else "↓"
                print(f"   {direction} {factor}: {abs(contribution):.3f}")
        
        if score.recommendations:
            print(f"\n💡 RECOMMANDATIONS:")
            for i, rec in enumerate(score.recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        print()


def test_workforce_analytics(service):
    """Test des analytics globales"""
    print("\n" + "="*80)
    print("TEST 4: ANALYTICS WORKFORCE GLOBALES")
    print("="*80)
    
    # Générer des historiques fictifs pour une équipe
    team_histories = []
    
    base_data = [
        (24, 5, 4.2, 1, 30, 70, 1, 12, 50, 9),
        (36, 8, 3.5, 0, 15, 40, 2, 20, 30, 7),
        (60, 2, 4.8, 3, 50, 90, 0, 5, 70, 5),
        (15, 10, 3.0, 0, 8, 30, 3, 25, 20, 8),
        (42, 6, 4.0, 2, 35, 75, 1, 15, 60, 6),
        (28, 4, 4.5, 1, 40, 80, 1, 8, 65, 4),
        (18, 12, 2.8, 0, 5, 25, 4, 35, 10, 9),
        (50, 3, 4.6, 2, 45, 85, 1, 10, 70, 5),
    ]
    
    departments = ["IT", "HR", "Sales", "Marketing", "Finance", "Operations", "Engineering", "Support"]
    
    for i, (tenure, absences, perf, promos, training, salary, mgr_changes, overtime, remote, team_size) in enumerate(base_data):
        team_histories.append(
            EmployeeHistory(
                employee_id=f"EMP{200+i}",
                tenure_months=tenure,
                absences_last_year=absences,
                average_performance_score=perf,
                promotion_count=promos,
                training_hours_last_year=training,
                salary_percentile=salary,
                department=departments[i],
                manager_changes_count=mgr_changes,
                overtime_hours_monthly=overtime,
                team_size=team_size,
                remote_work_percentage=remote,
                last_salary_increase_months=max(6, tenure // 3),
                feedback_score=perf + 0.1,
                engagement_survey_score=perf * 1.8
            )
        )
    
    print(f"\n📈 Analyse de {len(team_histories)} employés...\n")
    
    analytics = service.generate_workforce_analytics(team_histories)
    
    print(f"📊 ANALYTICS GLOBALES")
    print("-" * 80)
    print(f"Total employés analysés:      {analytics['total_employees']}")
    print(f"\n🎯 MOYENNES:")
    print(f"   • Risque de churn moyen:   {analytics['average_churn_risk']:.1%}")
    print(f"   • Performance moyenne:     {analytics['average_performance']:.1%}")
    print(f"   • Engagement moyen:        {analytics['average_engagement']:.1%}")
    
    print(f"\n⚠️  DISTRIBUTION DES RISQUES:")
    print(f"   • Risque élevé (≥60%):     {analytics['high_risk_count']} employés")
    print(f"   • Risque moyen (40-60%):   {analytics['medium_risk_count']} employés")
    print(f"   • Risque faible (<40%):    {analytics['low_risk_count']} employés")
    
    print(f"\n⭐ PERFORMANCES:")
    print(f"   • Top performers (≥80%):   {analytics['top_performers_count']} employés")
    print(f"   • Engagement faible (<40%): {analytics['low_engagement_count']} employés")
    
    print(f"\n📊 Distribution détaillée:")
    for level, count in analytics['risk_distribution'].items():
        percentage = (count / analytics['total_employees']) * 100
        bar = "█" * int(percentage / 5)
        print(f"   {level.capitalize():10s}: {bar} {count} ({percentage:.1f}%)")


def main():
    """Fonction principale pour exécuter tous les tests"""
    print("\n" + "="*80)
    print("🚀 TESTS DU MODULE HR ANALYTICS AVANCÉ")
    print("="*80)
    print("\nCe script teste les 3 fonctionnalités principales:")
    print("1. CV Matching avec NLP")
    print("2. Recommandation de formation personnalisée")
    print("3. Scoring RH prédictif (churn, performance, engagement)")
    
    try:
        # Test 1: CV Matching
        service = test_cv_matching()
        
        # Test 2: Training Recommendation
        test_training_recommendation(service)
        
        # Test 3: Predictive Scoring
        test_predictive_scoring(service)
        
        # Test 4: Workforce Analytics
        test_workforce_analytics(service)
        
        print("\n" + "="*80)
        print("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
        print("="*80)
        print("\n💡 Le module HR Analytics est prêt à être utilisé!")
        print("   - Intégrez-le dans votre API FastAPI")
        print("   - Connectez-le à votre base de données RH")
        print("   - Déployez avec MLflow pour le suivi des modèles")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
