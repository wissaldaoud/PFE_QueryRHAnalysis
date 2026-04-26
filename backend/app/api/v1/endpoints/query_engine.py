"""
Query Engine API Endpoints - Moteur de requêtes RH
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.base import get_db
from app.services.query_engine_service import QueryEngineService
from app.services.qlik_integration_service import QlikIntegrationService
from app.api.deps import get_current_active_user
from app.models.user import User
import pandas as pd
from io import StringIO, BytesIO

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    export_format: Optional[str] = None  # csv, excel, json


class QueryResponse(BaseModel):
    success: bool
    answer: str
    query_type: str
    data: Optional[dict] = None
    sql_query: Optional[str] = None
    visualization: Optional[dict] = None
    error: Optional[str] = None


class QueryHistoryResponse(BaseModel):
    history: List[dict]


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Exécuter une requête RH en langage naturel
    
    Exemples:
    - "Combien d'employés actifs?"
    - "Liste des employés du département IT"
    - "Salaire moyen par département"
    - "Quel est le taux de turnover?"
    - "SELECT * FROM employees LIMIT 10"
    """
    try:
        query_service = QueryEngineService(db)
        result = await query_service.process_query(
            question=request.query,
            user_id=current_user.id
        )
        
        # Ajouter les recommandations de dashboards Qlik
        if result.get("success"):
            qlik_service = QlikIntegrationService(db)
            result["qlik_dashboards"] = qlik_service.get_dashboard_recommendations(result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution: {str(e)}")


@router.post("/execute/export")
async def execute_and_export(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Exécuter une requête et exporter les résultats
    Formats: csv, excel, json
    """
    try:
        query_service = QueryEngineService(db)
        result = await query_service.process_query(
            question=request.query,
            user_id=current_user.id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Query failed"))
        
        # Extraire les données
        data = result.get("data", {})
        
        # Déterminer quelle donnée exporter
        if "employees" in data:
            df = pd.DataFrame(data["employees"])
        elif "departments" in data:
            df = pd.DataFrame(data["departments"])
        elif "rows" in data:
            df = pd.DataFrame(data["rows"])
        elif "by_department" in data:
            df = pd.DataFrame(data["by_department"])
        else:
            # Données simples (count, stats, etc.)
            df = pd.DataFrame([data])
        
        # Export selon format
        export_format = request.export_format or "csv"
        
        if export_format == "csv":
            output = StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=query_result.csv"}
            )
        
        elif export_format == "excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            output.seek(0)
            return Response(
                content=output.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=query_result.xlsx"}
            )
        
        elif export_format == "json":
            return Response(
                content=df.to_json(orient='records', indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=query_result.json"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Format non supporté. Utilisez: csv, excel, json")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'export: {str(e)}")


@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupérer l'historique des requêtes de l'utilisateur
    """
    try:
        query_service = QueryEngineService(db)
        history = query_service.get_history(current_user.id, limit=limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur historique: {str(e)}")


@router.get("/suggestions")
async def get_query_suggestions():
    """
    Obtenir des suggestions de requêtes
    """
    return {
        "suggestions": [
            {
                "category": "Statistiques Employés",
                "queries": [
                    "Combien d'employés actifs?",
                    "Liste des employés du département IT",
                    "Affiche les 10 meilleurs salaires",
                    "Nombre d'employés par département"
                ]
            },
            {
                "category": "Analyse Salariale",
                "queries": [
                    "Salaire moyen par département",
                    "Quel est le salaire maximum?",
                    "Distribution des salaires",
                    "Évolution salariale moyenne"
                ]
            },
            {
                "category": "Turnover & Performance",
                "queries": [
                    "Quel est le taux de turnover?",
                    "Combien de départs ce mois?",
                    "Turnover par département",
                    "Analyse des départs"
                ]
            },
            {
                "category": "Congés & Absences",
                "queries": [
                    "Statistiques des congés",
                    "Demandes de congés en attente",
                    "Taux d'absentéisme",
                    "Congés par département"
                ]
            },
            {
                "category": "Requêtes SQL",
                "queries": [
                    "SELECT * FROM employees LIMIT 10",
                    "SELECT department, COUNT(*) as count FROM employees GROUP BY department",
                    "SELECT AVG(salary) as avg_salary FROM employees WHERE employment_status = 'ACTIVE'"
                ]
            }
        ]
    }


@router.get("/schema")
async def get_database_schema():
    """
    Obtenir le schéma de la base de données pour aide SQL
    """
    return {
        "tables": [
            {
                "name": "employees",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "full_name", "type": "VARCHAR"},
                    {"name": "email", "type": "VARCHAR"},
                    {"name": "job_title", "type": "VARCHAR"},
                    {"name": "department_id", "type": "INTEGER"},
                    {"name": "salary", "type": "NUMERIC"},
                    {"name": "hire_date", "type": "DATE"},
                    {"name": "employment_status", "type": "ENUM(ACTIVE, TERMINATED, ON_LEAVE)"}
                ]
            },
            {
                "name": "departments",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "manager_id", "type": "INTEGER"}
                ]
            },
            {
                "name": "leave_requests",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "employee_id", "type": "INTEGER"},
                    {"name": "leave_type", "type": "VARCHAR"},
                    {"name": "start_date", "type": "DATE"},
                    {"name": "end_date", "type": "DATE"},
                    {"name": "status", "type": "ENUM(PENDING, APPROVED, REJECTED)"}
                ]
            }
        ],
        "example_queries": [
            "SELECT * FROM employees WHERE employment_status = 'ACTIVE'",
            "SELECT d.name, COUNT(e.id) as employee_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.name",
            "SELECT AVG(salary) as avg_salary, department_id FROM employees GROUP BY department_id"
        ]
    }


@router.get("/qlik/dashboards")
async def get_qlik_dashboards(db: Session = Depends(get_db)):
    """
    Liste des dashboards Qlik Sense disponibles avec intégration
    """
    qlik_service = QlikIntegrationService(db)
    return {
        "dashboards": qlik_service.get_available_dashboards()
    }
