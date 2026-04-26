"""
Script de test pour vérifier que le système CV Matching fonctionne
"""
import sys
from pathlib import Path

# Ajouter le backend au path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Tester que tous les imports fonctionnent"""
    print("🔍 Test des imports...")
    
    try:
        from app.services.cv_matching import CVMatcher, CVData, JobOffer, get_cv_matcher
        print("✅ cv_matching importé")
    except Exception as e:
        print(f"❌ Erreur import cv_matching: {e}")
        return False
    
    try:
        from app.models.job_offer import JobOffer as JobOfferModel
        print("✅ job_offer model importé")
    except Exception as e:
        print(f"❌ Erreur import job_offer model: {e}")
        return False
    
    try:
        from app.routes.cv_matching import router
        print("✅ cv_matching routes importées")
    except Exception as e:
        print(f"❌ Erreur import routes: {e}")
        return False
    
    return True


def test_model_loading():
    """Tester le chargement des modèles"""
    print("\n🤖 Test chargement des modèles ML...")
    
    try:
        from app.services.cv_matching import get_cv_matcher
        matcher = get_cv_matcher()
        print(f"✅ Modèle chargé")
        print(f"   - Catégories disponibles: {len(matcher.label_encoder.classes_)}")
        print(f"   - Exemples: {matcher.label_encoder.classes_[:5].tolist()}")
        return True
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        return False


def test_matching():
    """Tester un matching simple"""
    print("\n🎯 Test de matching...")
    
    try:
        from app.services.cv_matching import CVMatcher, CVData, JobOffer, get_cv_matcher
        
        # Créer un CV de test
        cv = CVData(
            skills=["Python", "Machine Learning", "SQL", "Pandas"],
            experiences=["Data Analyst with 3 years experience in ML projects"],
            job_titles=["Data Analyst", "Junior Data Scientist"],
            education=["Master in Data Science"],
            years_of_experience=3.5,
            full_text="Data Analyst with experience in Python, ML, SQL, and Pandas"
        )
        
        # Créer une offre de test
        job = JobOffer(
            title="Data Scientist",
            description="Looking for experienced Data Scientist with ML skills",
            category="Data Science",
            required_skills=["Python", "Machine Learning", "SQL"],
            preferred_skills=["Docker", "AWS"],
            required_education=["Master"],
            required_experience_years=3.0
        )
        
        # Matcher
        matcher = get_cv_matcher()
        result = matcher.match(cv, job)
        
        print(f"✅ Matching réussi!")
        print(f"   - Score global: {result.overall_score:.1f}%")
        print(f"   - Score compétences: {result.skills_score:.1f}%")
        print(f"   - Catégorie prédite: {result.predicted_category}")
        print(f"   - Compétences matching: {result.matching_skills}")
        print(f"   - Recommandations: {len(result.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur matching: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("TEST DU SYSTÈME CV MATCHING")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Chargement modèle
    results.append(("Chargement Modèle", test_model_loading()))
    
    # Test 3: Matching
    results.append(("Matching", test_matching()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 Tous les tests sont passés! Le système est prêt.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
