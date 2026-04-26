"""
Test de la question: Évolution des embauches
"""
import sys
import asyncio
sys.path.insert(0, 'C:\\Users\\wdaoud\\Desktop\\test\\backend')

from app.services.query_engine_service import QueryEngineService

# Initialiser le service (sans DB pour test NLP uniquement)
service = QueryEngineService(db=None)

# Tester la question
question = "Évolution des embauches"
print(f"\n🔍 TEST: {question}")
print("=" * 60)

async def test_query():
    try:
        result = await service.process_query(question, user_id=1)
        print(f"\n✅ Intent détecté: {result.get('intent', 'AUCUN')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"✅ Entities: {result.get('entities', {})}")
        print(f"✅ Filters: {result.get('filters', {})}")
        
        if result.get('sql'):
            print(f"\n📊 SQL généré:")
            print(result['sql'])
        
        if result.get('suggestions'):
            print(f"\n💡 Suggestions:")
            for s in result['suggestions']:
                print(f"  - {s}")
        
        if result.get('message'):
            print(f"\n📝 Message: {result['message']}")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

# Exécuter le test
asyncio.run(test_query())
