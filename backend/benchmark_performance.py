"""
Script de benchmark pour tester les performances du système HR Analytics
Test de charge, latence, throughput
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List
import json


# Données de test
TEST_CV = {
    "skills": ["Python", "FastAPI", "Machine Learning", "Docker", "PostgreSQL"],
    "experiences": [
        "Développeur Backend chez TechCorp - 3 ans",
        "Stage développement chez StartupAI - 6 mois"
    ],
    "job_titles": ["Développeur Backend Python", "Stagiaire ML"],
    "education": ["Master Informatique", "Licence Mathématiques"],
    "years_of_experience": 3.5,
    "full_text": "Développeur passionné avec 3.5 ans d'expérience en Python et ML"
}

TEST_JOB = {
    "title": "Senior Backend Developer",
    "required_skills": ["Python", "FastAPI", "SQL", "Docker", "CI/CD"],
    "preferred_skills": ["Machine Learning", "AWS", "Kubernetes"],
    "experience_required": 3,
    "education_required": ["Master", "Ingénieur"]
}


async def test_single_request(session: aiohttp.ClientSession, url: str, data: dict) -> dict:
    """Test une seule requête"""
    start = time.time()
    try:
        async with session.post(url, json=data) as response:
            result = await response.json()
            duration = time.time() - start
            return {
                "success": response.status == 200,
                "duration": duration,
                "status": response.status
            }
    except Exception as e:
        return {
            "success": False,
            "duration": time.time() - start,
            "error": str(e)
        }


async def benchmark_concurrent_requests(num_requests: int, url: str, data: dict):
    """Teste plusieurs requêtes concurrentes"""
    print(f"\n{'='*60}")
    print(f"🚀 Test de {num_requests} requêtes concurrentes")
    print(f"{'='*60}")
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Créer toutes les tâches
        tasks = [test_single_request(session, url, data) for _ in range(num_requests)]
        
        # Exécuter en parallèle
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Analyser les résultats
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        durations = [r["duration"] for r in successful]
        
        print(f"\n📊 Résultats :")
        print(f"  ✅ Succès : {len(successful)}/{num_requests}")
        print(f"  ❌ Échecs : {len(failed)}")
        print(f"  ⏱️  Temps total : {total_time:.2f}s")
        print(f"  📈 Throughput : {num_requests/total_time:.1f} req/s")
        
        if durations:
            print(f"\n⏱️  Latences :")
            print(f"  Min : {min(durations):.3f}s")
            print(f"  Max : {max(durations):.3f}s")
            print(f"  Moyenne : {statistics.mean(durations):.3f}s")
            print(f"  Médiane : {statistics.median(durations):.3f}s")
            if len(durations) > 1:
                print(f"  Écart-type : {statistics.stdev(durations):.3f}s")
        
        return {
            "total_requests": num_requests,
            "successful": len(successful),
            "failed": len(failed),
            "total_time": total_time,
            "throughput": num_requests/total_time,
            "latency": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "avg": statistics.mean(durations) if durations else 0,
                "median": statistics.median(durations) if durations else 0
            }
        }


async def benchmark_sequential_requests(num_requests: int, url: str, data: dict):
    """Teste des requêtes séquentielles"""
    print(f"\n{'='*60}")
    print(f"📝 Test de {num_requests} requêtes séquentielles")
    print(f"{'='*60}")
    
    async with aiohttp.ClientSession() as session:
        results = []
        start_time = time.time()
        
        for i in range(num_requests):
            result = await test_single_request(session, url, data)
            results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"  Progression : {i+1}/{num_requests}")
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        durations = [r["duration"] for r in successful]
        
        print(f"\n📊 Résultats :")
        print(f"  ✅ Succès : {len(successful)}/{num_requests}")
        print(f"  ⏱️  Temps total : {total_time:.2f}s")
        print(f"  📈 Throughput : {num_requests/total_time:.1f} req/s")
        print(f"  ⏱️  Latence moyenne : {statistics.mean(durations):.3f}s")
        
        return total_time


async def warm_up_model(url: str, data: dict):
    """Warm-up du modèle ML (premier appel)"""
    print(f"\n🔥 Warm-up du modèle ML...")
    async with aiohttp.ClientSession() as session:
        start = time.time()
        async with session.post(url, json=data) as response:
            await response.json()
            duration = time.time() - start
            print(f"  ✅ Warm-up terminé en {duration:.2f}s (incluant chargement modèle)")


async def test_cache_performance(url: str, data: dict):
    """Test l'efficacité du cache"""
    print(f"\n{'='*60}")
    print(f"💾 Test de performance du cache")
    print(f"{'='*60}")
    
    async with aiohttp.ClientSession() as session:
        # Premier appel (cache miss)
        print("\n1️⃣ Premier appel (cache MISS attendu)...")
        start = time.time()
        await test_single_request(session, url, data)
        first_call = time.time() - start
        print(f"  ⏱️  Durée : {first_call:.3f}s")
        
        # Deuxième appel identique (cache hit)
        print("\n2️⃣ Deuxième appel (cache HIT attendu)...")
        start = time.time()
        await test_single_request(session, url, data)
        second_call = time.time() - start
        print(f"  ⏱️  Durée : {second_call:.3f}s")
        
        # Calcul du gain
        speedup = first_call / second_call if second_call > 0 else 0
        print(f"\n🚀 Accélération : ×{speedup:.1f}")
        print(f"   Gain : {(1 - second_call/first_call)*100:.1f}% plus rapide")


async def run_full_benchmark():
    """Exécute tous les benchmarks"""
    BASE_URL = "http://localhost:8000/api/v1/hr-analytics"
    CV_MATCHING_URL = f"{BASE_URL}/cv-matching"
    
    request_data = {
        "cv": TEST_CV,
        "job_offer": TEST_JOB
    }
    
    print(f"\n{'='*60}")
    print(f"🎯 BENCHMARK HR ANALYTICS - CV MATCHING")
    print(f"{'='*60}")
    print(f"URL : {CV_MATCHING_URL}")
    
    # Warm-up
    await warm_up_model(CV_MATCHING_URL, request_data)
    
    # Test cache
    await test_cache_performance(CV_MATCHING_URL, request_data)
    
    # Tests séquentiels
    print(f"\n📝 Baseline : Requêtes séquentielles")
    seq_time = await benchmark_sequential_requests(10, CV_MATCHING_URL, request_data)
    
    # Tests concurrents avec différentes charges
    concurrent_tests = [10, 25, 50, 100]
    results = []
    
    for num in concurrent_tests:
        result = await benchmark_concurrent_requests(num, CV_MATCHING_URL, request_data)
        results.append(result)
        await asyncio.sleep(2)  # Pause entre tests
    
    # Résumé final
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ DES PERFORMANCES")
    print(f"{'='*60}")
    
    print(f"\n🎯 Throughput par niveau de charge :")
    for i, num in enumerate(concurrent_tests):
        print(f"  {num:3d} CVs : {results[i]['throughput']:6.1f} req/s | "
              f"Latence moy : {results[i]['latency']['avg']:.3f}s")
    
    print(f"\n⚡ Performance globale :")
    max_throughput = max([r['throughput'] for r in results])
    print(f"  Throughput max : {max_throughput:.1f} req/s")
    print(f"  Capacité/heure : {max_throughput * 3600:.0f} CVs")
    print(f"  Latence min : {min([r['latency']['min'] for r in results]):.3f}s")
    
    # Vérifier les métriques backend
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/metrics") as response:
                if response.status == 200:
                    metrics = await response.json()
                    print(f"\n📈 Métriques backend :")
                    print(f"  Total requêtes : {metrics.get('total_requests', 'N/A')}")
                    print(f"  Cache hit rate : {metrics.get('cache_hit_rate', 'N/A')}")
    except:
        pass
    
    print(f"\n✅ Benchmark terminés !\n")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🚀 BENCHMARK HR ANALYTICS - SYSTÈME ML DE CV MATCHING    ║
║                                                               ║
║  Ce script mesure les performances du système :              ║
║    • Latence (temps de réponse)                              ║
║    • Throughput (requêtes par seconde)                       ║
║    • Scalabilité (charge concurrente)                        ║
║    • Efficacité du cache                                     ║
║                                                               ║
║  Assurez-vous que le backend tourne sur :                    ║
║    http://localhost:8000                                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(run_full_benchmark())
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
