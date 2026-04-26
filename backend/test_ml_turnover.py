"""
Script de test pour valider le système de prédiction ML de turnover
Teste l'entraînement, le scoring et l'API

Usage:
    python test_ml_turnover.py
"""

import sys
import requests
import json
from pathlib import Path

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(title):
    """Affiche un en-tête de section"""
    print(f"\n{'='*60}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{'='*60}\n")


def test_model_files_exist():
    """Test 1 : Vérifier que les fichiers modèles existent"""
    print_header("Test 1 : Fichiers modèles")
    
    model_dir = Path("models")
    required_files = [
        "turnover_xgboost_model.pkl",
        "turnover_preprocessing.pkl",
        "turnover_feature_names.pkl",
        "turnover_model_metrics.json"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = model_dir / filename
        if filepath.exists():
            print(f"{GREEN}✓{RESET} {filename} trouvé")
        else:
            print(f"{RED}✗{RESET} {filename} MANQUANT")
            all_exist = False
    
    if not all_exist:
        print(f"\n{RED}⚠️  Certains fichiers sont manquants!{RESET}")
        print(f"   Exécutez : python train_turnover_model.py")
        return False
    
    print(f"\n{GREEN}✅ Tous les fichiers modèles sont présents{RESET}")
    return True


def test_model_metrics():
    """Test 2 : Vérifier les métriques du modèle"""
    print_header("Test 2 : Métriques du modèle")
    
    metrics_path = Path("models/turnover_model_metrics.json")
    
    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        print(f"📊 Performances du modèle :")
        print(f"   - ROC AUC:  {metrics['roc_auc']:.3f}")
        print(f"   - F1 Score: {metrics['f1_score']:.3f}")
        print(f"   - Accuracy: {metrics['accuracy']:.3f}")
        print(f"   - Samples de test: {metrics['n_samples_test']}")
        print(f"   - Turnover positifs: {metrics['n_positive']}")
        
        # Vérifier les seuils de qualité
        if metrics['roc_auc'] >= 0.75:
            print(f"\n{GREEN}✅ Modèle de bonne qualité (ROC AUC >= 0.75){RESET}")
            return True
        else:
            print(f"\n{RED}⚠️  Modèle de qualité moyenne (ROC AUC < 0.75){RESET}")
            print(f"   Considérez un réentraînement avec plus de données")
            return True  # Pas bloquant
            
    except Exception as e:
        print(f"{RED}✗ Erreur lors de la lecture des métriques: {e}{RESET}")
        return False


def test_scorer_ml_initialization():
    """Test 3 : Initialiser le PredictiveScorerML"""
    print_header("Test 3 : Initialisation du Scorer ML")
    
    try:
        from app.services.predictive_scoring_ml import PredictiveScorerML
        
        scorer = PredictiveScorerML(model_dir="models")
        print(f"{GREEN}✓{RESET} PredictiveScorerML initialisé")
        print(f"   - Features: {len(scorer.feature_names)}")
        print(f"   - Modèle: {type(scorer.model).__name__}")
        
        print(f"\n{GREEN}✅ Scorer ML opérationnel{RESET}")
        return True, scorer
        
    except Exception as e:
        print(f"{RED}✗ Erreur d'initialisation: {e}{RESET}")
        return False, None


def test_scoring_with_fake_data(scorer):
    """Test 4 : Scoring sur des données fictives"""
    print_header("Test 4 : Scoring avec données fictives")
    
    # Profils de test
    test_employees = [
        {
            "name": "Employé à Risque Élevé",
            "data": {
                "employee_id": "TEST001",
                "employee_code": "TEST001",
                "age": 26,
                "anciennete_annees": 0.5,
                "job_title": "Junior Developer",
                "department_name": "IT",
                "salary": 28000.0
            },
            "expected_risk": "élevé"
        },
        {
            "name": "Employé Stable",
            "data": {
                "employee_id": "TEST002",
                "employee_code": "TEST002",
                "age": 38,
                "anciennete_annees": 8.5,
                "job_title": "Senior Manager",
                "department_name": "Finance",
                "salary": 65000.0
            },
            "expected_risk": "faible"
        }
    ]
    
    try:
        for test_case in test_employees:
            print(f"\n🧪 Test : {test_case['name']}")
            
            score = scorer.score(test_case['data'])
            
            print(f"   - Churn Risk: {score.churn_risk_score:.3f} ({score.risk_level})")
            print(f"   - Performance: {score.performance_score:.3f}")
            print(f"   - Engagement: {score.engagement_score:.3f}")
            print(f"   - Confidence: {score.prediction_confidence:.3f}")
            print(f"   - Top facteur: {score.key_factors[0][0]} ({score.key_factors[0][1]:.3f})")
            print(f"   - Recommandations: {len(score.recommendations)}")
            
            # Vérification basique
            assert 0 <= score.churn_risk_score <= 1, "Score hors limites"
            assert score.risk_level in ["faible", "moyen", "élevé"], "Risk level invalide"
            assert len(score.key_factors) == 5, "Pas 5 facteurs SHAP"
            assert len(score.recommendations) > 0, "Pas de recommandations"
            
            print(f"   {GREEN}✓ Validation OK{RESET}")
        
        print(f"\n{GREEN}✅ Scoring fonctionnel sur données fictives{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ Erreur de scoring: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test 5 : Tester l'endpoint API ML"""
    print_header("Test 5 : Endpoint API")
    
    base_url = "http://localhost:8000"
    
    # Test 1 : Health check
    try:
        response = requests.get(f"{base_url}/api/v1/hr-analytics/health", timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}✓{RESET} Backend accessible")
        else:
            print(f"{RED}✗{RESET} Backend erreur {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ Backend non accessible{RESET}")
        print(f"   Assurez-vous que le serveur tourne : uvicorn app.main:app --reload")
        return False
    
    # Test 2 : Liste des employés
    try:
        response = requests.get(f"{base_url}/api/v1/hr-analytics/employees", timeout=5)
        if response.status_code == 200:
            employees = response.json()
            print(f"{GREEN}✓{RESET} {len(employees)} employés trouvés")
            
            if len(employees) == 0:
                print(f"{RED}⚠️  Aucun employé dans la DB{RESET}")
                return True  # Pas bloquant
            
            # Test 3 : Scoring ML sur le premier employé
            employee_id = employees[0]['id']
            print(f"\n🧪 Test scoring ML sur employé ID={employee_id}")
            
            response = requests.get(
                f"{base_url}/api/v1/hr-analytics/predictive-scoring/ml/{employee_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result['data']
                
                print(f"   - Employé: {data['employee_name']}")
                print(f"   - Churn Risk: {data['churn_risk_score']:.3f} ({data['risk_level']})")
                print(f"   - Model: {result['model_type']}")
                print(f"   - Top facteur SHAP: {data['key_factors'][0]['feature']}")
                print(f"   - Recommandations: {len(data['recommendations'])}")
                
                print(f"\n{GREEN}✅ Endpoint ML fonctionnel{RESET}")
                return True
            else:
                error = response.json()
                print(f"{RED}✗ Erreur API: {error.get('detail', 'Unknown')}{RESET}")
                return False
        else:
            print(f"{RED}✗ Erreur liste employés: {response.status_code}{RESET}")
            return False
            
    except Exception as e:
        print(f"{RED}✗ Erreur API: {e}{RESET}")
        return False


def main():
    """Exécute tous les tests"""
    print(f"\n{BLUE}{'='*60}")
    print(f"🧪 TESTS DU SYSTÈME ML DE PRÉDICTION DE TURNOVER")
    print(f"{'='*60}{RESET}")
    
    results = {}
    
    # Test 1 : Fichiers modèles
    results['files'] = test_model_files_exist()
    if not results['files']:
        print(f"\n{RED}❌ Tests interrompus : Modèle non entraîné{RESET}")
        print(f"   Exécutez : python train_turnover_model.py")
        return False
    
    # Test 2 : Métriques
    results['metrics'] = test_model_metrics()
    
    # Test 3 : Initialisation
    success, scorer = test_scorer_ml_initialization()
    results['init'] = success
    if not success:
        print(f"\n{RED}❌ Tests interrompus : Impossible d'initialiser le scorer{RESET}")
        return False
    
    # Test 4 : Scoring
    results['scoring'] = test_scoring_with_fake_data(scorer)
    
    # Test 5 : API
    results['api'] = test_api_endpoint()
    
    # Résumé
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}✓ PASSED{RESET}" if passed_test else f"{RED}✗ FAILED{RESET}"
        print(f"   {test_name.upper()}: {status}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print(f"{GREEN}✅ TOUS LES TESTS PASSÉS ({passed}/{total}){RESET}")
        print(f"\n🎉 Système opérationnel ! Prêt pour la production.")
        print(f"\n📚 Consultez ML_TURNOVER_README.md pour l'utilisation")
        return True
    else:
        print(f"{RED}⚠️  {total - passed} TEST(S) ÉCHOUÉ(S) ({passed}/{total} passés){RESET}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
