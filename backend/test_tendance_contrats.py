"""
Test: Tendance des contrats par année
"""
import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\wdaoud\\Desktop\\test\\backend')

from app.services.query_engine_service import QueryEngineService

service = QueryEngineService(db=None)

async def test():
    question = "Tendance des contrats par année"
    print(f"\n🔍 TEST: {question}")
    print("=" * 70)
    
    try:
        result = await service.process_query(question, user_id=1)
        
        print(f"\n✅ Intent: {result.get('intent', 'AUCUN')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"✅ Entities: {result.get('entities', {})}")
        
        if result.get('sql'):
            sql = result['sql']
            print(f"\n📊 SQL:")
            print(sql)
            
            # Compter les colonnes dans SELECT
            if 'SELECT' in sql:
                select_part = sql.split('FROM')[0].replace('SELECT', '').strip()
                columns = [c.strip() for c in select_part.split(',')]
                print(f"\n📋 Colonnes SELECT ({len(columns)}):")
                for col in columns:
                    print(f"   - {col}")
            
            # Vérifier GROUP BY
            if 'GROUP BY' in sql:
                groupby_part = sql.split('GROUP BY')[1].split('ORDER')[0].strip() if 'ORDER' in sql else sql.split('GROUP BY')[1].strip()
                print(f"\n📦 GROUP BY:")
                print(f"   {groupby_part}")
        
        if result.get('data'):
            print(f"\n💾 Nombre de lignes retournées: {len(result['data'])}")
        
        if result.get('visualization'):
            print(f"\n📈 Visualisation: {result['visualization'].get('type', 'AUCUNE')}")
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
