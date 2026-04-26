"""
Script de test pour le nouveau endpoint de prédiction de turnover
"""
import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/hr-analytics/predict-turnover"

# Données de test
test_employees = [
    {
        "name": "Employé Jeune CDI",
        "data": {
            "date_naissance": "1995-06-15",
            "date_embauche": "2022-01-10",
            "sexe": "Masculin",
            "type_contrat": "CDI",
            "total_jours_absence": 3,
            "nb_absences": 1
        },
        "expected_risk": "Faible"  # Jeune, récent, peu d'absences
    },
    {
        "name": "Employé Senior CDI",
        "data": {
            "date_naissance": "1975-03-20",
            "date_embauche": "2005-09-01",
            "sexe": "Féminin",
            "type_contrat": "CDI",
            "total_jours_absence": 15,
            "nb_absences": 4
        },
        "expected_risk": "Faible"  # Ancienneté élevée = faible risque
    },
    {
        "name": "Employé CDD récent",
        "data": {
            "date_naissance": "1992-11-08",
            "date_embauche": "2025-06-01",
            "sexe": "Masculin",
            "type_contrat": "CDD",
            "total_jours_absence": 0,
            "nb_absences": 0
        },
        "expected_risk": "Moyen/Élevé"  # CDD = risque plus élevé
    },
    {
        "name": "Employé absences élevées",
        "data": {
            "date_naissance": "1988-07-25",
            "date_embauche": "2018-03-15",
            "sexe": "Féminin",
            "type_contrat": "CDI",
            "total_jours_absence": 45,
            "nb_absences": 12
        },
        "expected_risk": "Moyen/Élevé"  # Beaucoup d'absences
    }
]


def get_access_token():
    """Récupère un token d'accès (à adapter selon votre système)"""
    # Option 1: Si vous avez déjà un token
    # return "YOUR_TOKEN_HERE"
    
    # Option 2: Login automatique
    login_url = f"{BASE_URL}/api/v1/auth/login"
    credentials = {
        "username": "admin@example.com",  # À adapter
        "password": "admin123"  # À adapter
    }
    
    try:
        response = requests.post(login_url, data=credentials)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
    except Exception as e:
        print(f"⚠️ Erreur login: {e}")
    
    return None


def test_prediction(employee_data, token=None):
    """Teste la prédiction pour un employé"""
    url = f"{BASE_URL}{ENDPOINT}"
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(url, json=employee_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def print_result(name, data, result, expected_risk):
    """Affiche joliment le résultat"""
    print("\n" + "="*70)
    print(f"📊 {name}")
    print("="*70)
    
    # Données d'entrée
    age = (datetime.now().date() - datetime.strptime(data['date_naissance'], '%Y-%m-%d').date()).days // 365
    anciennete = (datetime.now().date() - datetime.strptime(data['date_embauche'], '%Y-%m-%d').date()).days / 365.25
    
    print(f"\n📝 Données:")
    print(f"   Âge: {age} ans")
    print(f"   Ancienneté: {anciennete:.1f} ans")
    print(f"   Sexe: {data['sexe']}")
    print(f"   Contrat: {data['type_contrat']}")
    print(f"   Absences: {data['nb_absences']} ({data['total_jours_absence']} jours)")
    
    if result:
        print(f"\n🎯 Résultat:")
        print(f"   Risque: {result['risk_emoji']} {result['risk_level']} ({result['turnover_probability_percent']:.2f}%)")
        print(f"   Prédiction: {'❌ Départ probable' if result['prediction'] == 1 else '✅ Devrait rester'}")
        print(f"   Attendu: {expected_risk}")
        
        # Features détaillées
        features = result.get('features_used', {})
        print(f"\n🔍 Features calculées:")
        for key, value in features.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
    else:
        print("\n❌ Pas de résultat")


def main():
    """Fonction principale"""
    print("🚀 Test du endpoint de prédiction de turnover\n")
    
    # Récupérer le token (optionnel si l'endpoint n'est pas protégé)
    token = get_access_token()
    if token:
        print(f"✅ Token récupéré: {token[:20]}...\n")
    else:
        print("⚠️ Pas de token - test sans authentification\n")
    
    # Tester chaque profil
    for employee in test_employees:
        result = test_prediction(employee['data'], token)
        print_result(
            employee['name'],
            employee['data'],
            result,
            employee['expected_risk']
        )
    
    print("\n" + "="*70)
    print("✅ Tests terminés")
    print("="*70)


if __name__ == "__main__":
    main()
