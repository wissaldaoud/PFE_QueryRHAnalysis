"""
Test de création d'offre via API
"""
import requests
import json

url = "http://localhost:8000/api/v1/cv-matching/jobs"

data = {
    "title": "Développeur Full Stack Senior - Architecte Logiciel",
    "description": "Nous recherchons un développeur Full Stack Senior avec une expertise polyvalente pour concevoir et développer des applications web et mobile. Vous travaillerez sur des architectures complexes utilisant Spring Boot, Angular, Flutter et diverses technologies modernes. Une forte capacité en modélisation UML/SysML et maîtrise des pipelines CI/CD est essentielle.",
    "category": "Full Stack Developer",
    "required_skills": ["Java 11/17", "Kotlin", "Spring Boot", "Angular", "SQL", "MySQL", "Git", "REST API", "UML", "SysML", "JUnit", "Jenkins", "Gradle"],
    "preferred_skills": ["Dart", "Flutter", "JavaScript", "Node.js", "PHP", "Symfony", "Oracle", "Firebase", "Magicdraw", "Bitbucket", "SonarQube", "Nexus", "IntelliJ IDEA", "Android Studio", "Postman"],
    "required_education": ["Master Informatique", "Ingénieur Logiciel"],
    "required_experience_years": 5.0,
    "location": "Paris / Remote",
    "salary_range": "55000-75000 EUR",
    "contract_type": "CDI",
    "department": "Engineering",
    "is_active": True
}

print("Envoi de la requête...")
print(json.dumps(data, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, json=data)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("\n✅ Offre créée avec succès!")
        result = response.json()
        print(f"ID: {result['id']}")
        print(f"Titre: {result['title']}")
    else:
        print(f"\n❌ Erreur {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}: {e}")
