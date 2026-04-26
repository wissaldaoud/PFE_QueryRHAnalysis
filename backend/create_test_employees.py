"""
Créer des employés de test pour tester les prédictions
"""
import sys
import os
from pathlib import Path

# Ajouter le backend au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Enum
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import random

# Connexion directe (adapter selon votre config)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hr_analytics")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Données de test
names = [
    ("Ahmed", "Benali"), ("Fatima", "El Idrissi"), ("Karim", "Alami"),
    ("Salma", "Berrada"), ("Youssef", "Tazi"), ("Nadia", "Fassi"),
    ("Omar", "Hakimi"), ("Leila", "Bennani"), ("Mehdi", "Tounsi"),
    ("Amina", "Chraibi"), ("Samir", "Lahlou"), ("Hayat", "Ziani"),
]

jobs = ["Développeur", "Chef de Projet", "Analyste", "Manager", "Consultant", "Technicien"]

print("Création de 12 employés de test...")
print(f"Connexion à : {DATABASE_URL}")

for i, (first, last) in enumerate(names, 1):
    # Date d'embauche aléatoire (entre 6 mois et 10 ans)
    hire_days_ago = random.randint(180, 3650)
    hire_date = date.today() - timedelta(days=hire_days_ago)
    
    # Date de naissance (entre 25 et 55 ans)
    age_years = random.randint(25, 55)
    birth_date = date.today() - timedelta(days=age_years * 365)
    
    # Requête SQL directe
    db.execute(f"""
        INSERT INTO employees 
        (employee_code, first_name, last_name, email, date_of_birth, hire_date, 
         job_title, employment_status, salary, department_id, created_at, updated_at)
        VALUES 
        ('EMP{1000 + i}', '{first}', '{last}', '{first.lower()}.{last.lower()}@company.com',
         '{birth_date}', '{hire_date}', '{random.choice(jobs)}', 'active', 
         {random.randint(40000, 90000)}, 1, NOW(), NOW())
        ON CONFLICT (employee_code) DO NOTHING
    """)
    
    print(f"  ✅ {first} {last} (embauché il y a {hire_days_ago // 365} ans)")

db.commit()
print(f"\n✅ {len(names)} employés créés !")
print("\n➡️  Allez sur http://localhost:3000/hr-analytics/predictive-scoring")
print("    Vous verrez maintenant vos employés avec leurs prédictions !")

