from app.services.ml_service import MLService
from app.db.base import SessionLocal
import json
import traceback

print("="*70)
print("TEST DE PREDICTION TURNOVER")
print("="*70)

db = SessionLocal()
try:
    print("\n1. Création de MLService...")
    ml = MLService(db)
    print(f"   ✅ MLService créé: {ml.model_name}, threshold={ml.threshold}")
    
    # Récupérer quelques employés
    print("\n2. Récupération d'employés depuis DWH...")
    if ml.dwh_engine:
        from sqlalchemy import text
        with ml.dwh_engine.connect() as conn:
            result = conn.execute(text('SELECT nudoss, nom, prenom FROM dim.dim_employe LIMIT 5'))
            employees = [(row[0], f"{row[1]} {row[2]}") for row in result]
            
        if employees:
            print(f"   ✅ {len(employees)} employés trouvés")
            for nudoss, name in employees:
                print(f"      - ID {nudoss}: {name}")
            
            # Tester avec le premier
            test_id = str(employees[0][0])
            print(f"\n3. Test de prédiction pour l'employé ID={test_id}...")
            result = ml.predict_from_dwh(test_id)
            
            print("\n" + "="*70)
            print("RÉSULTAT:")
            print("="*70)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("="*70)
        else:
            print("   ❌ Aucun employé trouvé")
    else:
        print("   ❌ Pas de connexion DWH")
        
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    traceback.print_exc()
finally:
    db.close()
