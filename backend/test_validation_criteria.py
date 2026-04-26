"""
Script de test des critères d'acceptation des congés
"""
import sys
sys.path.insert(0, r'C:\Users\wdaoud\Desktop\test\backend')

import httpx
from datetime import date, timedelta

API_BASE = "http://127.0.0.1:8000/api/v1"

def login(email, password):
    """Se connecter et obtenir le token"""
    response = httpx.post(
        f"{API_BASE}/auth/login",
        data={"username": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Erreur login: {response.status_code}")
        print(response.text)
        return None

def test_validation_rules(token):
    """Tester l'endpoint des règles de validation"""
    print("\n" + "="*60)
    print("TEST 1: Récupération des règles de validation")
    print("="*60)
    
    response = httpx.get(
        f"{API_BASE}/leaves/validation-rules",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Règles récupérées:")
        for criterion in data["criteria"]:
            print(f"\n{criterion['id']}. {criterion['name']}")
            print(f"   {criterion['description']}")
            print(f"   📋 {criterion['details']}")
        
        print(f"\n⚙️ Configuration:")
        config = data['config']
        print(f"   - Effectif min: {config['min_team_presence_count']} personnes")
        print(f"   - Effectif min %: {config['min_team_presence_percentage']}%")
        print(f"   - Prévenance: {config['advance_notice_days']} jours")
        print(f"   - Jours annuels: {config['annual_leave_allowance']} jours")
        return True
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        return False

def test_validation_api(token):
    """Tester l'API de pré-validation"""
    print("\n" + "="*60)
    print("TEST 2: Pré-validation d'une demande")
    print("="*60)
    
    # Test 1: Demande valide (dans 1 mois)
    start_date = (date.today() + timedelta(days=30)).isoformat()
    end_date = (date.today() + timedelta(days=32)).isoformat()
    
    print(f"\nTest 2.1: Demande valide (dans 30 jours)")
    response = httpx.post(
        f"{API_BASE}/leaves/validate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "annual",
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": 3,
            "reason": "Test validation"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   is_valid: {result['is_valid']}")
        print(f"   can_be_approved: {result['can_be_approved']}")
        if result['errors']:
            print(f"   ❌ Erreurs: {result['errors']}")
        if result['warnings']:
            print(f"   ⚠️ Avertissements: {result['warnings']}")
        if result['is_valid']:
            print("   ✅ Demande valide!")
    else:
        print(f"   ❌ Erreur {response.status_code}: {response.text}")
    
    # Test 2: Demande avec délai court (dans 5 jours)
    start_date = (date.today() + timedelta(days=5)).isoformat()
    end_date = (date.today() + timedelta(days=7)).isoformat()
    
    print(f"\nTest 2.2: Délai de prévenance court (5 jours)")
    response = httpx.post(
        f"{API_BASE}/leaves/validate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "annual",
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": 3,
            "reason": "Test délai court"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   is_valid: {result['is_valid']}")
        if result['errors']:
            for error in result['errors']:
                print(f"   ❌ {error}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"   ⚠️ {warning}")
    else:
        print(f"   ❌ Erreur {response.status_code}")
    
    # Test 3: Période bloquée (fin décembre)
    current_year = date.today().year
    start_date = f"{current_year}-12-22"
    end_date = f"{current_year}-12-24"
    
    print(f"\nTest 2.3: Période bloquée (22-24 décembre)")
    response = httpx.post(
        f"{API_BASE}/leaves/validate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "annual",
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": 3,
            "reason": "Test période bloquée"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   is_valid: {result['is_valid']}")
        if result['errors']:
            for error in result['errors']:
                print(f"   ❌ {error}")
    else:
        print(f"   ❌ Erreur {response.status_code}")

def test_create_with_validation(token):
    """Tester la création avec validation automatique"""
    print("\n" + "="*60)
    print("TEST 3: Création de demande avec validation")
    print("="*60)
    
    # Tentative de création avec délai court
    start_date = (date.today() + timedelta(days=5)).isoformat()
    end_date = (date.today() + timedelta(days=7)).isoformat()
    
    print(f"\nTest 3.1: Création refusée (délai court)")
    response = httpx.post(
        f"{API_BASE}/leaves/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "annual",
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": 3,
            "reason": "Test délai court"
        }
    )
    
    if response.status_code == 400:
        print(f"   ✅ Demande refusée comme prévu")
        print(f"\n   Message d'erreur:")
        error_detail = response.json()['detail']
        for line in error_detail.split('\n'):
            print(f"      {line}")
    elif response.status_code == 201:
        print(f"   ⚠️ Demande acceptée (inattendu)")
    else:
        print(f"   ❌ Erreur {response.status_code}: {response.text}")
    
    # Création valide
    start_date = (date.today() + timedelta(days=30)).isoformat()
    end_date = (date.today() + timedelta(days=32)).isoformat()
    
    print(f"\nTest 3.2: Création acceptée (délai suffisant)")
    response = httpx.post(
        f"{API_BASE}/leaves/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "annual",
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": 3,
            "reason": "Test création valide"
        }
    )
    
    if response.status_code == 201:
        print(f"   ✅ Demande créée avec succès!")
        data = response.json()
        print(f"   ID: {data['id']}")
        print(f"   Statut: {data['status']}")
        if 'validation_warnings' in data:
            print(f"   ⚠️ Avertissements:")
            for warning in data['validation_warnings']:
                print(f"      {warning}")
        return data['id']
    else:
        print(f"   ❌ Erreur {response.status_code}")
        print(f"   {response.text}")
        return None

def main():
    print("="*60)
    print("TEST DES CRITÈRES D'ACCEPTATION DES CONGÉS")
    print("="*60)
    
    # Se connecter en tant qu'employé
    print("\n🔐 Connexion en tant que Fatima (employée)...")
    token = login("fatima.alaoui@soprahr.com", "password123")
    
    if not token:
        print("❌ Impossible de se connecter")
        return
    
    print("✅ Connecté!")
    
    # Exécuter les tests
    test_validation_rules(token)
    test_validation_api(token)
    test_create_with_validation(token)
    
    print("\n" + "="*60)
    print("TESTS TERMINÉS")
    print("="*60)

if __name__ == "__main__":
    main()
