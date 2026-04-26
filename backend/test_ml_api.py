"""
Script de test de l'API de prédiction de turnover
Test des 3 endpoints principaux
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def test_health():
    """Test du endpoint health"""
    print("\n" + "="*60)
    print("🏥 TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/predict/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service opérationnel")
            print(f"   Status: {data.get('status')}")
            print(f"   Modèle chargé: {data.get('model_loaded')}")
            print(f"   Features: {data.get('features_count')}")
            print(f"   DWH connecté: {data.get('dwh_connected')}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion: {str(e)}")
        return False


def test_predict_individual(employe_id: int = 1):
    """Test de prédiction individuelle"""
    print("\n" + "="*60)
    print(f"👤 TEST 2: Prédiction Individuelle (Employé {employe_id})")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/predict/turnover/{employe_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prédiction réussie")
            print(f"\n   Employé ID: {data.get('employe_id')}")
            print(f"   Score de risque: {data.get('score')}%")
            print(f"   Niveau: {data.get('niveau')}")
            print(f"   Recommandation: {data.get('recommandation')}")
            
            if 'details' in data:
                print(f"\n   Détails:")
                for key, value in data['details'].items():
                    print(f"     • {key}: {value}")
            
            return True
        else:
            error = response.json()
            print(f"❌ Erreur {response.status_code}: {error.get('detail')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def test_predict_all(limit: int = 10):
    """Test de prédiction globale"""
    print("\n" + "="*60)
    print(f"📊 TEST 3: Prédiction Globale (Top {limit})")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/predict/all?limit={limit}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse réussie: {len(data)} employés")
            
            if data:
                print(f"\n   🔴 TOP 5 EMPLOYÉS À RISQUE:")
                for i, emp in enumerate(data[:5], 1):
                    print(f"   {i}. Employé {emp['employe_id']}: {emp['score']}% ({emp['niveau']})")
            
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def test_simulate_whatif(employe_id: int = 1):
    """Test de simulation what-if"""
    print("\n" + "="*60)
    print(f"🔮 TEST 4: Simulation What-If (Employé {employe_id})")
    print("="*60)
    
    # Modifications à tester
    modifications = {
        "nb_absences": 2,
        "salaire_mensuel": 7000,
        "anciennete_annees": 6
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/predict/simulate",
            json={
                "employe_id": employe_id,
                "modifications": modifications
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simulation réussie")
            print(f"\n   📈 AVANT:")
            print(f"     Score: {data['avant']['score']}%")
            print(f"     Niveau: {data['avant']['niveau']}")
            
            print(f"\n   📉 APRÈS (modifications):")
            for key, value in modifications.items():
                print(f"     • {key}: {value}")
            print(f"     Score: {data['apres']['score']}%")
            print(f"     Niveau: {data['apres']['niveau']}")
            
            print(f"\n   💡 IMPACT:")
            print(f"     Delta: {data['delta']:+.2f}%")
            print(f"     {data['impact']}")
            print(f"     Recommandation: {data['recommandation']}")
            
            return True
        else:
            error = response.json()
            print(f"❌ Erreur {response.status_code}: {error.get('detail')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("🧪 TESTS DE L'API DE PRÉDICTION DE TURNOVER")
    print("="*60)
    print(f"   Base URL: {BASE_URL}")
    print(f"   API Prefix: {API_PREFIX}")
    
    results = {
        'health': test_health(),
        'individual': test_predict_individual(employe_id=1),
        'all': test_predict_all(limit=10),
        'whatif': test_simulate_whatif(employe_id=1)
    }
    
    # Résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"   {emoji} {test_name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\n   Total: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n   🎉 TOUS LES TESTS SONT PASSÉS!")
    else:
        print(f"\n   ⚠️  {total - passed} test(s) échoué(s)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
