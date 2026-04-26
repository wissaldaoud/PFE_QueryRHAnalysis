from fastapi import APIRouter
from app.api.v1.endpoints import (
    employees, auth, auth_direct, auth_simple, analytics, qlik, chatbot, departments,
    users, auth_advanced, auth_keycloak, leaves, notifications, query_engine
)
from app.api.v1.endpoints import hr_analytics
from app.routes import prediction, cv_matching, cv_ranking  # ← une seule ligne
from app.routes.prediction import router as ml_router

# DEBUG
print("="*80)
print("DEBUG: hr_analytics import check")
print(f"hr_analytics module: {hr_analytics}")
print(f"hr_analytics has router: {hasattr(hr_analytics, 'router')}")
if hasattr(hr_analytics, 'router'):
    print(f"hr_analytics router: {hr_analytics.router}")
    print(f"hr_analytics routes count: {len(hr_analytics.router.routes)}")
print("="*80)

api_router = APIRouter()

api_router.include_router(auth_simple.router, prefix="/auth", tags=["Authentication 🔐"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication 🔐"])
api_router.include_router(auth_direct.router, prefix="/auth", tags=["Authentication 🔐"])
api_router.include_router(auth_advanced.router, prefix="/auth", tags=["Advanced Security 🛡️"])
api_router.include_router(auth_keycloak.router, prefix="/auth", tags=["Keycloak SSO 🔑"])
api_router.include_router(users.router, prefix="/users", tags=["User Management 👤"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications 🔔"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["Leave Management 📅"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(qlik.router, prefix="/qlik", tags=["Qlik Sense Integration"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["HR Chatbot 🤖"])
api_router.include_router(query_engine.router, prefix="/query", tags=["Query Engine 🔍"])
api_router.include_router(hr_analytics.router, prefix="/hr-analytics", tags=["HR Analytics 📊"])
print(f"✅ HR Analytics router added to api_router. Total routes: {len(api_router.routes)}")
api_router.include_router(cv_matching.router, tags=["CV Matching 📄"])
api_router.include_router(cv_ranking.router, tags=["CV Ranking 🏆"])  # ← ajouté
api_router.include_router(prediction.router, tags=["Prédictions ML 🤖"])
api_router.include_router(ml_router, tags=["Prédictions ML XGBoost 🧠"])