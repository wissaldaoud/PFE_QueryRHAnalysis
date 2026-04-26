"""
Système de cache pour optimiser les performances
Cache des embeddings ML pour éviter les recalculs
"""

import hashlib
import pickle
from typing import Optional, Any
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Cache en mémoire simple pour les embeddings
    Pour production : remplacer par Redis
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live en secondes
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, text: str) -> str:
        """Génère une clé unique pour le texte"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        key = self._generate_key(text)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Vérifier TTL
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                logger.debug(f"Cache HIT: {key[:8]}...")
                return value
            else:
                # Expiré
                del self.cache[key]
        
        self.misses += 1
        logger.debug(f"Cache MISS: {key[:8]}...")
        return None
    
    def set(self, text: str, value: Any):
        """Stocke une valeur dans le cache"""
        # Si cache plein, supprimer le plus ancien
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
        
        key = self._generate_key(text)
        self.cache[key] = (value, time.time())
        logger.debug(f"Cache SET: {key[:8]}...")
    
    def clear(self):
        """Vide le cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total
        }


# Instance globale du cache
embedding_cache = SimpleCache(max_size=500, ttl=3600)  # 500 CVs, 1h


def cache_embedding(func):
    """
    Décorateur pour cacher les embeddings
    
    Usage:
        @cache_embedding
        def encode_text(text: str):
            return model.encode(text)
    """
    @wraps(func)
    def wrapper(text: str, *args, **kwargs):
        # Vérifier cache
        cached_result = embedding_cache.get(text)
        if cached_result is not None:
            return cached_result
        
        # Calculer
        start = time.time()
        result = func(text, *args, **kwargs)
        duration = time.time() - start
        
        logger.debug(f"Embedding calculated in {duration:.3f}s")
        
        # Stocker
        embedding_cache.set(text, result)
        
        return result
    
    return wrapper


class PerformanceMetrics:
    """Collecte des métriques de performance"""
    
    def __init__(self):
        self.requests = 0
        self.total_time = 0.0
        self.errors = 0
        self.endpoint_stats = {}
    
    def record_request(self, endpoint: str, duration: float, error: bool = False):
        """Enregistre une requête"""
        self.requests += 1
        self.total_time += duration
        
        if error:
            self.errors += 1
        
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "errors": 0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += duration
        if error:
            stats["errors"] += 1
    
    def get_stats(self) -> dict:
        """Retourne les statistiques"""
        avg_time = (self.total_time / self.requests) if self.requests > 0 else 0
        error_rate = (self.errors / self.requests * 100) if self.requests > 0 else 0
        
        endpoint_details = {}
        for endpoint, stats in self.endpoint_stats.items():
            avg = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            err_rate = (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0
            
            endpoint_details[endpoint] = {
                "requests": stats["count"],
                "avg_time": f"{avg:.3f}s",
                "error_rate": f"{err_rate:.1f}%"
            }
        
        return {
            "total_requests": self.requests,
            "total_errors": self.errors,
            "error_rate": f"{error_rate:.1f}%",
            "avg_response_time": f"{avg_time:.3f}s",
            "uptime": f"{self.total_time:.1f}s",
            "endpoints": endpoint_details
        }
    
    def reset(self):
        """Reset des métriques"""
        self.requests = 0
        self.total_time = 0.0
        self.errors = 0
        self.endpoint_stats = {}


# Instance globale des métriques
performance_metrics = PerformanceMetrics()


def track_performance(endpoint: str):
    """
    Décorateur pour tracker la performance d'un endpoint
    
    Usage:
        @track_performance("cv-matching")
        async def match_cv():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            error = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                duration = time.time() - start
                performance_metrics.record_request(endpoint, duration, error)
        
        return wrapper
    return decorator
