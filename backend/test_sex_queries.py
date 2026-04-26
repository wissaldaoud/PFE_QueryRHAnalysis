"""Test des requêtes avec filtre sexe après correction du bug"""
import asyncio
import sys
sys.path.append(".")

from app.services.query_engine_service import QueryEngineService

async def test_queries():
    query_engine = QueryEngineService()
    await query_engine.initialize()
    
    questions = [
        "Combien d'hommes actifs ?",
        "Combien de femmes actives ?",
        "Répartition des employés par sexe",
        "Liste des femmes en CDI",
        "Moyenne d'âge des hommes"
    ]
    
    for question in questions:
        print(f"\n{'='*80}")
        print(f"❓ Question: {question}")
        print('='*80)
        
        result = await query_engine.process_query(question, user_id=1)
        
        print(f"✅ Success: {result.get('success', False)}")
        print(f"💬 Answer: {result.get('answer', 'N/A')[:200]}")
        if 'sql_query' in result:
            print(f"🗄️  SQL: {result['sql_query'][:300]}")
        if 'data' in result and result['data']:
            print(f"📊 Data count: {len(result['data'])}")
        print()

if __name__ == "__main__":
    asyncio.run(test_queries())
