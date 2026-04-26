"""
Script de test rapide pour vérifier l'intégration du module HR Analytics
Exécuter : python test_integration.py
"""

import httpx
import asyncio
import json


async def test_health_check():
    """Test du health check"""
    print("\n" + "="*80)
    print("TEST 1 : Health Check du service HR Analytics")
    print("="*80)
    
    url = "http://localhost:8000/api/v1/hr-analytics/health"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Service HR Analytics opérationnel")
                print(f"   Status: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Impossible de contacter le serveur: {e}")
        print("\n💡 Assurez-vous que le serveur est démarré :")
        print("   uvicorn app.main:app --reload")
        return False


async def test_cv_matching():
    """Test du CV matching"""
    print("\n" + "="*80)
    print("TEST 2 : CV Matching")
    print("="*80)
    
    url = "http://localhost:8000/api/v1/hr-analytics/cv-matching"
    
    payload = {
        "cv": {
            "skills": ["Python", "FastAPI", "Machine Learning", "SQL"],
            "experiences": ["3 ans de développement Backend avec Python et FastAPI"],
            "job_titles": ["Développeur Backend"],
            "education": ["Master en Informatique"],
            "years_of_experience": 3.0
        },
        "job_offer": {
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "job_title": "Senior Backend Developer",
            "description": "Développement d'APIs RESTful avec Python et FastAPI",
            "required_experience_years": 3.0
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ CV Matching réussi")
                print(f"   Score global: {data['data']['overall_score']:.1%}")
                print(f"   Compétences: {data['data']['skills_score']:.1%}")
                print(f"   Expérience: {data['data']['experience_score']:.1%}")
                print(f"   Matching skills: {len(data['data']['matching_skills'])}")
                print(f"   Missing skills: {len(data['data']['missing_required_skills'])}")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


async def test_predictive_scoring():
    """Test du scoring prédictif"""
    print("\n" + "="*80)
    print("TEST 3 : Scoring Prédictif")
    print("="*80)
    
    url = "http://localhost:8000/api/v1/hr-analytics/predictive-scoring"
    
    payload = {
        "employee_id": "TEST001",
        "tenure_months": 18,
        "absences_last_year": 8,
        "average_performance_score": 3.5,
        "promotion_count": 1,
        "training_hours_last_year": 25,
        "salary_percentile": 60,
        "department": "IT",
        "manager_changes_count": 1,
        "overtime_hours_monthly": 15,
        "team_size": 8,
        "remote_work_percentage": 50
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Scoring Prédictif réussi")
                print(f"   Risque de churn: {data['scores']['churn_risk']:.1%} [{data['risk_level'].upper()}]")
                print(f"   Performance: {data['scores']['performance']:.1%}")
                print(f"   Engagement: {data['scores']['engagement']:.1%}")
                print(f"   Recommandations: {len(data['recommendations'])} générées")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


async def main():
    """Exécuter tous les tests"""
    print("\n" + "="*80)
    print("🧪 TEST D'INTÉGRATION DU MODULE HR ANALYTICS ML")
    print("="*80)
    print("\nVérification de l'intégration dans la plateforme...")
    
    results = []
    
    # Test 1 : Health check
    result = await test_health_check()
    results.append(("Health Check", result))
    
    if not result:
        print("\n❌ Le service n'est pas disponible. Arrêt des tests.")
        return
    
    # Attendre un peu entre les tests
    await asyncio.sleep(1)
    
    # Test 2 : CV Matching
    result = await test_cv_matching()
    results.append(("CV Matching", result))
    
    await asyncio.sleep(1)
    
    # Test 3 : Scoring Prédictif
    result = await test_predictive_scoring()
    results.append(("Scoring Prédictif", result))
    
    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*80)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_success = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n{total_success}/{total_tests} tests réussis ({total_success/total_tests*100:.0f}%)")
    
    if total_success == total_tests:
        print("\n🎉 Tous les tests sont passés ! Le module HR Analytics est bien intégré.")
        print("\n💡 Prochaines étapes :")
        print("   1. Ouvrir http://localhost:8000/docs pour tester tous les endpoints")
        print("   2. Exécuter python test_hr_analytics_full.py pour des tests approfondis")
        print("   3. Consulter INTEGRATION_HR_ANALYTICS.md pour la documentation")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifier :")
        print("   1. Le serveur est bien démarré (uvicorn app.main:app --reload)")
        print("   2. Les dépendances ML sont installées (pip install -r requirements.txt)")
        print("   3. Le modèle Sentence Transformer est téléchargé")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
