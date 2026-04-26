"""
🧪 Test Script for NL2SQL v2.0 Improvements

Tests the new intelligent features:
1. Semantic similarity
2. RAG with threshold
3. Auto-learning
4. SQL explanation
5. Metrics tracking
6. Bilingual support
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.query_engine_service import QueryEngineService, expand_with_synonyms
from sqlalchemy.orm import Session


class MockDB:
    """Mock database session for testing"""
    pass


async def test_semantic_similarity():
    """Test 1: Semantic Similarity"""
    print("\n" + "="*70)
    print("🧪 TEST 1: SEMANTIC SIMILARITY")
    print("="*70)
    
    engine = QueryEngineService(MockDB())
    
    if not engine.semantic_model:
        print("⚠️  Semantic model not available, skipping test")
        return
    
    test_pairs = [
        ("Combien d'employés actifs ?", "How many active employees?"),
        ("Quel est le salaire moyen ?", "What is the average salary?"),
        ("Liste des absents", "Who is absent today?"),
        ("Taux de turnover", "Employee attrition rate"),
    ]
    
    for q1, q2 in test_pairs:
        sim = engine.compute_cosine_similarity(q1, q2)
        status = "✅" if sim > 0.6 else "❌"
        print(f"{status} '{q1}' <-> '{q2}': {sim:.3f}")


async def test_synonym_expansion():
    """Test 2: Synonym Expansion"""
    print("\n" + "="*70)
    print("🧪 TEST 2: SYNONYM EXPANSION (Bilingual)")
    print("="*70)
    
    test_queries = [
        "What is the average salary?",
        "Combien d'employés actifs ?",
        "Liste des absents",
    ]
    
    for query in test_queries:
        expanded = expand_with_synonyms(query)
        print(f"\n📝 Original: {query}")
        print(f"   Expanded: {expanded[:100]}...")


async def test_rag_threshold():
    """Test 3: RAG with Similarity Threshold"""
    print("\n" + "="*70)
    print("🧪 TEST 3: RAG SIMILARITY THRESHOLD")
    print("="*70)
    
    engine = QueryEngineService(MockDB())
    
    if not engine.semantic_model:
        print("⚠️  Semantic model not available, skipping test")
        return
    
    # Test with questions similar to examples
    test_queries = [
        "Combien d'employés actifs ?",  # Exact match in DB
        "How many active employees?",    # English version
        "Nombre d'employés en activité", # Paraphrase
    ]
    
    for query in test_queries:
        examples, max_sim = engine._retrieve_similar_examples(query, top_k=1)
        threshold_met = "✅ REUSED" if max_sim >= 0.75 else "❌ LLM NEEDED"
        print(f"\n📋 Query: {query}")
        print(f"   Similarity: {max_sim:.3f} → {threshold_met}")
        if examples:
            print(f"   Best match: {examples[0]['question']}")


async def test_sql_explanation():
    """Test 4: SQL Explanation"""
    print("\n" + "="*70)
    print("🧪 TEST 4: SQL EXPLANATION")
    print("="*70)
    
    engine = QueryEngineService(MockDB())
    
    test_sqls = [
        "SELECT COUNT(*) FROM dim.dim_employe WHERE flag_employe_actif = 1;",
        "SELECT AVG(salaire_mensuel) FROM fait.fait_contrat;",
        "SELECT * FROM fait.fait_absence WHERE date_debut_absence = CURRENT_DATE LIMIT 50;",
    ]
    
    for sql in test_sqls:
        print(f"\n📝 SQL: {sql[:60]}...")
        explanation = engine.explain_sql(sql)
        print(f"\n{explanation}\n")


async def test_metrics():
    """Test 5: Metrics Tracking"""
    print("\n" + "="*70)
    print("🧪 TEST 5: METRICS TRACKING")
    print("="*70)
    
    engine = QueryEngineService(MockDB())
    
    # Simulate some queries
    engine.metrics["nltk_used"] = 45
    engine.metrics["ollama_used"] = 12
    engine.metrics["rag_reused"] = 33
    engine.metrics["total_queries"] = 90
    engine.metrics["successful_queries"] = 87
    engine.metrics["failed_queries"] = 3
    engine.metrics["total_response_time"] = 45.3
    engine.metrics["learned_queries_count"] = 23
    
    metrics = engine.get_metrics()
    
    print("\n📊 SYSTEM METRICS:")
    print(f"   Total Queries: {metrics['total_queries']}")
    print(f"   Success Rate: {metrics['success_rate']}%")
    print(f"   Avg Response Time: {metrics['avg_response_time']}s")
    print(f"\n🎯 ENGINE USAGE:")
    print(f"   NLTK: {metrics['nltk_used']} ({metrics['nltk_pct']}%)")
    print(f"   Ollama LLM: {metrics['ollama_used']} ({metrics['ollama_pct']}%)")
    print(f"   RAG Reused: {metrics['rag_reused']} ({metrics['rag_reused_pct']}%)")
    print(f"\n🎓 AUTO-LEARNING:")
    print(f"   Learned Queries: {metrics['learned_queries_count']}")


async def test_auto_learning():
    """Test 6: Auto-Learning System"""
    print("\n" + "="*70)
    print("🧪 TEST 6: AUTO-LEARNING SYSTEM")
    print("="*70)
    
    engine = QueryEngineService(MockDB())
    
    if not engine.semantic_model:
        print("⚠️  Semantic model not available, skipping test")
        return
    
    # Test saving a learned query
    test_question = "Combien de développeurs seniors actifs ?"
    test_sql = "SELECT COUNT(*) FROM employees WHERE role='Senior Developer';"
    
    print(f"\n💾 Saving learned query...")
    print(f"   Question: {test_question}")
    print(f"   SQL: {test_sql}")
    
    initial_count = len(engine.learned_queries)
    engine._save_learned_query(test_question, test_sql)
    
    if len(engine.learned_queries) > initial_count:
        print(f"   ✅ Query saved! Total learned: {len(engine.learned_queries)}")
        
        # Try to save again (should be rejected as duplicate)
        engine._save_learned_query(test_question, test_sql)
        if len(engine.learned_queries) == initial_count + 1:
            print(f"   ✅ Duplicate detection working!")
    
    # Test learned queries summary
    summary = engine.get_learned_queries_summary()
    print(f"\n📚 Learned Queries Summary:")
    print(f"   Total: {summary['total_learned']}")
    if summary['recent_queries']:
        print(f"   Recent:")
        for q in summary['recent_queries'][-3:]:
            print(f"      - {q['question']}")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 NL2SQL v2.0 - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Semantic Similarity", test_semantic_similarity),
        ("Synonym Expansion", test_synonym_expansion),
        ("RAG Threshold", test_rag_threshold),
        ("SQL Explanation", test_sql_explanation),
        ("Metrics Tracking", test_metrics),
        ("Auto-Learning", test_auto_learning),
    ]
    
    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    print("🧪 Starting NL2SQL v2.0 Test Suite...")
    asyncio.run(run_all_tests())
    print("\n✨ Test suite finished!\n")
