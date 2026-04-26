"""
Test de création d'offre d'emploi
"""
import sys
sys.path.insert(0, '.')

from app.db.base import SessionLocal
from app.models.job_offer import JobOffer

# Créer une session
db = SessionLocal()

try:
    # Créer l'offre
    job = JobOffer(
        title="Développeur Full Stack Senior - Architecte Logiciel",
        description="Nous recherchons un développeur Full Stack Senior avec une expertise polyvalente pour concevoir et développer des applications web et mobile. Vous travaillerez sur des architectures complexes utilisant Spring Boot, Angular, Flutter et diverses technologies modernes. Une forte capacité en modélisation UML/SysML et maîtrise des pipelines CI/CD est essentielle.",
        category="Full Stack Developer",
        required_skills=["Java 11/17", "Kotlin", "Spring Boot", "Angular", "SQL", "MySQL", "Git", "REST API", "UML", "SysML", "JUnit", "Jenkins", "Gradle"],
        preferred_skills=["Dart", "Flutter", "JavaScript", "Node.js", "PHP", "Symfony", "Oracle", "Firebase", "Magicdraw", "Bitbucket", "SonarQube", "Nexus", "IntelliJ IDEA", "Android Studio", "Postman"],
        required_education=["Master Informatique", "Ingénieur Logiciel"],
        required_experience_years=5.0,
        location="Paris / Remote",
        salary_range="55000-75000 EUR",
        contract_type="CDI",
        department="Engineering",
        is_active=True
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    print(f"✅ Offre créée avec succès!")
    print(f"ID: {job.id}")
    print(f"Titre: {job.title}")
    print(f"Compétences requises: {job.required_skills}")
    
except Exception as e:
    db.rollback()
    print(f"❌ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    db.close()
