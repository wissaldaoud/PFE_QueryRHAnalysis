"""
Test dynamique - Ajouter un employé et voir les stats s'incrémenter
"""
import sys
sys.path.insert(0, r'C:\Users\wdaoud\Desktop\test\backend')

import httpx
from datetime import date

API_BASE = "http://127.0.0.1:8000/api/v1"

def login_admin():
    response = httpx.post(
        f"{API_BASE}/auth/login",
        data={"username": "admin@soprahr.com", "password": "admin123456789"}
    )
    return response.json()["access_token"] if response.status_code == 200 else None

def get_stats(token):
    """Récupérer les stats actuelles"""
    response = httpx.get(
        f"{API_BASE}/analytics/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json() if response.status_code == 200 else None

def add_employee(token):
    """Ajouter un nouvel employé"""
    import random
    
    prenoms = ["Mohamed", "Yasmine", "Rachid", "Amina", "Omar", "Salma", "Youssef"]
    noms = ["Benjelloun", "Tazi", "Fassi", "El Amrani", "Chraibi", "Idrissi"]
    
    prenom = random.choice(prenoms)
    nom = random.choice(noms)
    email = f"{prenom.lower()}.{nom.lower()}{random.randint(10,99)}@soprahr.com"
    
    employee_data = {
        "first_name": prenom,
        "last_name": nom,
        "email": email,
        "phone": f"+212 6{random.randint(10000000, 99999999)}",
        "hire_date": "2026-02-23",
        "department_id": random.randint(1, 13),
        "position": random.choice(["Analyste", "Développeur", "Chef de Projet", "Consultant"]),
        "salary": random.randint(8000, 15000),
        "employment_status": "active"
    }
    
    response = httpx.post(
        f"{API_BASE}/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json=employee_data
    )
    
    if response.status_code == 201:
        return response.json(), f"{prenom} {nom}"
    else:
        return None, None

def main():
    print("="*70)
    print("TEST DYNAMIQUE - INCRÉMENTATION DES STATS")
    print("="*70)
    
    # Se connecter en tant qu'admin
    token = login_admin()
    if not token:
        print("❌ Erreur de connexion")
        return
    
    print("✅ Connecté en tant qu'Admin\n")
    
    # 1. Récupérer les stats AVANT
    print("📊 STATS AVANT L'AJOUT:")
    stats_before = get_stats(token)
    if stats_before:
        print(f"   Total Employés: {stats_before.get('total_employees', 0)}")
        print(f"   Employés Actifs: {stats_before.get('active_employees', 0)}")
        print(f"   Départements: {stats_before.get('departments_count', 0)}")
    else:
        print("   ❌ Impossible de récupérer les stats")
        return
    
    # 2. Ajouter un nouvel employé
    print("\n➕ AJOUT D'UN NOUVEL EMPLOYÉ...")
    employee, name = add_employee(token)
    
    if employee:
        print(f"   ✅ Employé ajouté: {name}")
        print(f"   📧 Email: {employee.get('email')}")
        print(f"   💼 Poste: {employee.get('position')}")
        print(f"   🏢 Département ID: {employee.get('department_id')}")
    else:
        print("   ❌ Erreur lors de l'ajout")
        return
    
    # 3. Récupérer les stats APRÈS
    print("\n📊 STATS APRÈS L'AJOUT:")
    stats_after = get_stats(token)
    if stats_after:
        print(f"   Total Employés: {stats_after.get('total_employees', 0)}")
        print(f"   Employés Actifs: {stats_after.get('active_employees', 0)}")
        print(f"   Départements: {stats_after.get('departments_count', 0)}")
    
    # 4. Vérifier l'incrémentation
    print("\n" + "="*70)
    if stats_after and stats_before:
        diff_total = stats_after['total_employees'] - stats_before['total_employees']
        diff_active = stats_after['active_employees'] - stats_before['active_employees']
        
        if diff_total > 0 and diff_active > 0:
            print("✅ LES STATS S'INCRÉMENTENT CORRECTEMENT!")
            print(f"   Total Employés: +{diff_total}")
            print(f"   Employés Actifs: +{diff_active}")
        else:
            print("⚠️ Aucun changement détecté dans les stats")
    
    print("="*70)
    print("\n💡 Actualisez http://localhost:3000/dashboard pour voir les changements!")

if __name__ == "__main__":
    main()
