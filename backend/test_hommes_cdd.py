"""
Test: Combien d'employés hommes en CDD
"""
import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\wdaoud\\Desktop\\test\\backend')

from app.services.query_engine_service import QueryEngineService

service = QueryEngineService(db=None)

async def test():
    question = "Combien d'employés hommes en CDD"
    print(f"\n{'='*70}")
    print(f"🔍 TEST: {question}")
    print('='*70)
    
    try:
        result = await service.process_query(question, user_id=1)
        
        print(f"\n✅ Intent: {result.get('intent', 'AUCUN')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"✅ Entities: {result.get('entities', {})}")
        print(f"✅ Filters: {result.get('filters', {})}")
        
        if result.get('sql'):
            print(f"\n📊 SQL généré:")
            print(result['sql'])
            print()
            
            # Analyser le SQL
            sql = result['sql']
            if "WHERE" in sql:
                where_part = sql.split("WHERE")[1].split("GROUP BY")[0] if "GROUP BY" in sql else sql.split("WHERE")[1]
                print("📋 Conditions WHERE:")
                conditions = [c.strip() for c in where_part.replace("AND", "\n  AND").split("\n")]
                for cond in conditions:
                    if cond.strip():
                        print(f"  {cond}")
        
        if result.get('data'):
            print(f"\n💾 Résultat: {result['data']}")
        
        if result.get('message'):
            print(f"\n📝 Message: {result['message']}")
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
