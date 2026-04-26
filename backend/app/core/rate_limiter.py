"""
Rate Limiting Middleware using SlowAPI
Protection contre les attaques brute force
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],  # Global default
    storage_uri="memory://",  # In-memory storage (use Redis in production)
    strategy="fixed-window"  # or "moving-window"
)

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "login": "5 per minute",        # Prevent brute force
    "register": "3 per minute",     # Prevent spam registration
    "2fa_verify": "10 per minute",  # 2FA code attempts
    "password_reset": "3 per hour", # Password reset requests
    "api_general": "100 per minute", # General API calls
}


def setup_rate_limiting(app):
    """
    Configure rate limiting for the FastAPI application
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    return limiter
