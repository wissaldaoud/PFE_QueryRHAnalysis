"""
Query HR Analytics Online - Main FastAPI Application  
Secured with: JWT, OAuth2 SSO, 2FA (TOTP), RBAC, Rate Limiting, Audit Logs
"""

# CRITICAL: Patch UTF-8 AVANT tout autre import
from app.core.utf8_patch import *

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.rate_limiter import setup_rate_limiting
import os


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## 🔐 Query HR Analytics Online - Enterprise HR Platform

### Security Features:
- **JWT Authentication** with refresh tokens
- **OAuth2 SSO** (Microsoft Azure AD / Google)
- **2FA (TOTP)** - Two-Factor Authentication
- **RBAC** - Role-Based Access Control (Admin, HR Manager, Analyst, Employee)
- **Rate Limiting** - Brute force protection
- **Audit Logging** - Security event tracking
- **Session Management** - Multi-device support

### API Features:
- Employee Management
- Department Analytics
- HR KPIs & Dashboards
- Natural Language Chatbot
- Qlik Sense Integration
""",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# -----------------------------
# Configure CORS (must be first!)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# -----------------------------
# Global Exception Handler
# -----------------------------
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and return JSON error.
    This helps debug the 500 errors and shows the real message.
    """
    # Get origin from request for CORS
    origin = request.headers.get("origin")
    headers = {}
    if origin in settings.BACKEND_CORS_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers
    )


# -----------------------------
# Setup Rate Limiting
# -----------------------------
setup_rate_limiting(app)


# -----------------------------
# Initialize HR Analytics Service
# -----------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize HR Analytics ML models on startup"""
    print("="*80)
    print("STARTUP EVENT CALLED!")
    print("="*80)
    try:
        from app.api.v1.endpoints.hr_analytics import initialize_hr_analytics_service
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🚀 Initialisation du service HR Analytics ML...")
        print("About to initialize HR Analytics...")
        initialize_hr_analytics_service()
        print("HR Analytics initialized successfully!")
        logger.info("✅ Service HR Analytics initialisé avec succès")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        print(f"ERROR in startup: {e}")
        logger.warning(f"⚠️  Service HR Analytics non disponible: {e}")
        # Ne pas bloquer le démarrage si le service ML n'est pas disponible


# -----------------------------
# Include API router
# -----------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)


# -----------------------------
# Serve uploaded files (profile pictures, etc.)
# -----------------------------
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# -----------------------------
# Health check endpoints
# -----------------------------
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Query HR Analytics Online API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}
