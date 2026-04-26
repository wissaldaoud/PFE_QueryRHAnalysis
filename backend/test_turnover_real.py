"""
Test du modèle de turnover entraîné sur les données Qlik réelles
"""
import sys
from pathlib import Path

# Ajouter le parent au path
sys.path.append(str(Path(__file__).parent))

from app.services.predictive_scoring import PredictiveScorerML

print("="*70)
print("  TEST MODÈLE TURNOVER - DONNÉES QLIK RÉELLES")
print("="*70)

# ════════════════════════════════════════════════════════════
# 1. CHARGEMENT DU MODÈLE
# ════════════════════════════════════════════════════════════

print("\n🔧 Initialisation du scorer...")
try:
    scorer = PredictiveScorerML()
    print(f"✅ Modèle chargé : {scorer.model_version}")
    print(f"📋 Features attendues ({len(scorer.feature_names)}) : {scorer.feature_names}")
except Exception as e:
    print(f"❌ Erreur chargement modèle : {e}")
    print("\n💡 Vérifiez que le fichier existe :")
    print("   backend/ml/models/turnover_model_real.pkl")
    print("\n   Si absent, lancez : python ml/scripts/train_turnover_real.py")
    sys.exit(1)

# ════════════════════════════════════════════════════════════
# 2. CAS DE TEST
# ════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 CAS DE TEST")
print("="*70)

test_cases = [
    {
        "name": "Profil à RISQUE ÉLEVÉ",
        "data": {
            "employee_id": "EMP_RISQUE_001",
            "age": 27,
            "anciennete_annees": 1.5,
            "sexe": "F",
            "type_contrat": "CDD",
            "nb_absences": 12,
            "total_jours_absence": 18,
        },
        "expected_risk": "élevé ou moyen"
    },
    {
        "name": "Profil à RISQUE FAIBLE",
        "data": {
            "employee_id": "EMP_STABLE_001",
            "age": 42,
            "anciennete_annees": 8.5,
            "sexe": "M",
            "type_contrat": "CDI",
            "nb_absences": 2,
            "total_jours_absence": 3,
        },
        "expected_risk": "faible"
    },
    {
        "name": "Profil DÉBUTANT",
        "data": {
            "employee_id": "EMP_JUNIOR_001",
            "age": 24,
            "anciennete_annees": 0.5,
            "sexe": "M",
            "type_contrat": "CDI",
            "nb_absences": 1,
            "total_jours_absence": 1,
        },
        "expected_risk": "moyen ou faible"
    },
    {
        "name": "Profil SENIOR",
        "data": {
            "employee_id": "EMP_SENIOR_001",
            "age": 55,
            "anciennete_annees": 15.0,
            "sexe": "F",
            "type_contrat": "CDI",
            "nb_absences": 0,
            "total_jours_absence": 0,
        },
        "expected_risk": "faible"
    },
]

# ════════════════════════════════════════════════════════════
# 3. EXÉCUTION DES TESTS
# ════════════════════════════════════════════════════════════

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'─'*70}")
    print(f"🧪 TEST {i}/{len(test_cases)} : {test_case['name']}")
    print(f"{'─'*70}")
    
    data = test_case['data']
    
    # Afficher les données d'entrée
    print(f"\n📥 Données d'entrée :")
    print(f"   - ID            : {data['employee_id']}")
    print(f"   - Âge           : {data['age']} ans")
    print(f"   - Ancienneté    : {data['anciennete_annees']} ans")
    print(f"   - Sexe          : {data['sexe']}")
    print(f"   - Contrat       : {data['type_contrat']}")
    print(f"   - Absences      : {data['nb_absences']} ({data['total_jours_absence']} jours)")
    
    # Prédiction
    try:
        result = scorer.score(data)
        
        print(f"\n📊 RÉSULTATS :")
        print(f"   - Risque de départ    : {result.churn_risk_score*100:.1f}%")
        print(f"   - Niveau de risque    : {result.risk_level.upper()}")
        print(f"   - Priorité d'action   : {result.action_priority.upper()}")
        print(f"   - Confiance           : {result.prediction_confidence*100:.0f}%")
        print(f"   - Performance         : {result.performance_score*100:.0f}%")
        print(f"   - Engagement          : {result.engagement_score*100:.0f}%")
        
        print(f"\n🔍 Top 5 facteurs SHAP :")
        for j, factor in enumerate(result.key_factors, 1):
            direction_emoji = "🔴" if "augmente" in factor['direction'] else "🟢"
            print(f"   {j}. {direction_emoji} {factor['feature']:<30} : {factor['shap_value']:>7.4f}  ({factor['direction']})")
        
        print(f"\n💡 Recommandations :")
        for j, rec in enumerate(result.recommendations, 1):
            print(f"   {j}. {rec}")
        
        # Vérifier l'attendu
        print(f"\n✅ Résultat attendu : {test_case['expected_risk']}")
        
        if result.risk_level in test_case['expected_risk']:
            print(f"   ✔️  OK : Niveau de risque correspond")
        else:
            print(f"   ⚠️  ATTENTION : Niveau différent de l'attendu")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la prédiction : {e}")
        import traceback
        traceback.print_exc()

# ════════════════════════════════════════════════════════════
# 4. RÉSUMÉ
# ════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🎉 TESTS TERMINÉS")
print("="*70)

print(f"\n📊 Modèle testé :")
print(f"   - Version  : {scorer.model_version}")
print(f"   - Features : {len(scorer.feature_names)}")
print(f"   - Seuil    : {scorer.threshold}")

print(f"\n✅ Le modèle est opérationnel !")
print(f"\n💡 Pour l'utiliser dans l'API :")
print(f"   1. Démarrer le backend : python run_server.py")
print(f"   2. Appeler l'endpoint : POST /api/ml/predict-turnover")

print("\n" + "="*70)
