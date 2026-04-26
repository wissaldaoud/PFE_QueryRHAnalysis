"""
TEST : Vérifier le nouvel endpoint /employees-dwh
"""
import requests

BASE_URL = "http://localhost:8000/api/v1/hr-analytics"

print("=" * 80)
print("TEST 1 : Charger employés depuis DWH")
print("=" * 80)

try:
    response = requests.get(f"{BASE_URL}/employees-dwh?limit=5")
    print(f"\nStatut: {response.status_code}")
    
    if response.status_code == 200:
        employees = response.json()
        print(f"✅ {len(employees)} employés chargés\n")
        
        for emp in employees[:3]:
            print(f"ID: {emp['id']:10} | {emp['full_name']:30} | {emp['age']:2} ans | Ancienneté: {emp['anciennete_annees']:5.1f} ans")
        
        # Tester prédiction sur le 1er employé
        if employees:
            nudoss = employees[0]['id']
            print(f"\n{'=' * 80}")
            print(f"TEST 2 : Prédiction pour employé {nudoss}")
            print("=" * 80)
            
            response2 = requests.get(f"{BASE_URL}/predictive-scoring/ml/{nudoss}")
            print(f"\nStatut: {response2.status_code}")
            
            if response2.status_code == 200:
                score = response2.json()
                print(f"\n✅ PRÉDICTION RÉUSSIE")
                print(f"   Employé: {score['employee_name']}")
                print(f"   Risque: {score['churn_risk_percent']}%")
                print(f"   Niveau: {score['risk_level']}")
                print(f"\n   Features utilisées:")
                for k, v in score['features_used'].items():
                    print(f"      - {k}: {v}")
                print(f"\n   Top 3 facteurs SHAP:")
                for factor in score['key_factors'][:3]:
                    print(f"      - {factor['feature']}: {factor['shap_value']:.4f}")
            else:
                print(f"❌ Erreur prédiction: {response2.text}")
    else:
        print(f"❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\n💡 Assurez-vous que le backend est démarré : python run_server.py")

print("\n" + "=" * 80)
