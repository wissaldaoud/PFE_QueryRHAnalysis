"""
Test: Vérifier que COUNT sans GROUP BY ne génère pas ORDER BY e.age
"""
import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\wdaoud\\Desktop\\test\\backend')

from app.services.query_engine_service import QueryEngineService

service = QueryEngineService(db=None)

async def test():
    questions = [
        "Combien d'employés hommes en CDD",
        "Nombre total d'employés",
        "Combien de femmes actives"
    ]
    
    for q in questions:
        print(f"\n{'='*70}")
        print(f"🔍 TEST: {q}")
        print('='*70)
        
        try:
            result = await service.process_query(q, user_id=1)
            
            intent = result.get('intent', 'AUCUN')
            sql = result.get('sql', '')
            
            print(f"✅ Intent: {intent}")
            
            if sql:
                print(f"\n📊 SQL généré:")
                print(sql)
                
                # Vérifier si ORDER BY e.age existe (ne devrait PAS exister pour COUNT simple)
                if 'ORDER BY e.age' in sql and 'GROUP BY' not in sql:
                    print(f"\n❌ ERREUR: ORDER BY e.age trouvé sans GROUP BY!")
                elif 'ORDER BY e.age' not in sql:
                    print(f"\n✅ OK: Pas de ORDER BY e.age (correct pour COUNT simple)")
                    
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")

asyncio.run(test())
