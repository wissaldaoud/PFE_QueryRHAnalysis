"""
Test du nouvel endpoint dashboard-stats pour Karim
"""
import sys
sys.path.insert(0, r'C:\Users\wdaoud\Desktop\test\backend')

import httpx

API_BASE = "http://127.0.0.1:8000/api/v1"

def login(email, password):
    response = httpx.post(
        f"{API_BASE}/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"] if response.status_code == 200 else None

def test_karim_dashboard():
    print("="*60)
    print("TEST DASHBOARD - KARIM (Manager)")
    print("="*60)
    
    # Se connecter en tant que Karim
    token = login("karim.alaoui@soprahr.com", "password123")
    
    if not token:
        print("❌ Erreur de connexion")
        return
    
    print("✅ Connecté en tant que Karim\n")
    
    # Appeler le nouveau endpoint
    response = httpx.get(
        f"{API_BASE}/analytics/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 STATISTIQUES DU DASHBOARD:")
        print(f"   Rôle: {data.get('role', 'N/A')}")
        print(f"   Total Employés: {data.get('total_employees', 0)}")
        print(f"   Employés Actifs: {data.get('active_employees', 0)}")
        print(f"   Congés en attente: {data.get('pending_leaves', 0)}")
        print(f"   Départements: {data.get('departments_count', 0)}")
        
        if 'team_employee_ids' in data:
            print(f"\n   👥 IDs des membres de l'équipe: {data['team_employee_ids']}")
        
        print("\n✅ Dashboard stats récupérées avec succès!")
    else:
        print(f"\n❌ Erreur {response.status_code}")
        print(response.text)

def test_admin_dashboard():
    print("\n" + "="*60)
    print("TEST DASHBOARD - ADMIN")
    print("="*60)
    
    token = login("admin@soprahr.com", "admin123456789")
    
    if not token:
        print("❌ Erreur de connexion")
        return
    
    print("✅ Connecté en tant qu'Admin\n")
    
    response = httpx.get(
        f"{API_BASE}/analytics/dashboard-stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 STATISTIQUES DU DASHBOARD:")
        print(f"   Rôle: {data.get('role', 'N/A')}")
        print(f"   Total Employés: {data.get('total_employees', 0)}")
        print(f"   Employés Actifs: {data.get('active_employees', 0)}")
        print(f"   Employés Terminés: {data.get('terminated_employees', 0)}")
        print(f"   Congés en attente: {data.get('pending_leaves', 0)}")
        print(f"   Congés RH en attente: {data.get('hr_pending_leaves', 0)}")
        print(f"   Départements: {data.get('departments_count', 0)}")
        
        print("\n✅ Stats globales récupérées avec succès!")
    else:
        print(f"\n❌ Erreur {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_karim_dashboard()
    test_admin_dashboard()
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60)
