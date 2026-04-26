"""
Integration Service - Lien entre Moteur de Requêtes et Qlik Sense
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import json


class QlikIntegrationService:
    """Service d'intégration entre le moteur de requêtes et Qlik Sense"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_query_results_to_qlik(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transformer les résultats du moteur de requêtes au format Qlik
        """
        if not query_result.get("success"):
            return {"error": "Query failed"}
        
        # Extraire les données
        data = query_result.get("data", {})
        
        # Format Qlik-compatible
        qlik_data = {
            "query_time": query_result.get("query_time", ""),
            "dataset_name": f"query_result_{hash(str(data))}",
            "fields": [],
            "rows": []
        }
        
        # Déterminer les données à exporter
        if "employees" in data:
            qlik_data["fields"] = list(data["employees"][0].keys()) if data["employees"] else []
            qlik_data["rows"] = data["employees"]
        elif "departments" in data:
            qlik_data["fields"] = list(data["departments"][0].keys()) if data["departments"] else []
            qlik_data["rows"] = data["departments"]
        elif "rows" in data:
            qlik_data["fields"] = list(data["rows"][0].keys()) if data["rows"] else []
            qlik_data["rows"] = data["rows"]
        
        return qlik_data
    
    def create_qlik_embed_url(self, dashboard_id: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Générer une URL d'embedding Qlik Sense avec filtres
        """
        base_url = "http://localhost:4848/single"  # Qlik Sense local
        
        # Construire les paramètres de filtre
        filter_params = []
        if filters:
            for field, value in filters.items():
                filter_params.append(f"select={field},{value}")
        
        filter_string = "&".join(filter_params) if filter_params else ""
        
        embed_url = f"{base_url}/?appid={dashboard_id}"
        if filter_string:
            embed_url += f"&{filter_string}"
        
        return embed_url
    
    def get_dashboard_recommendations(self, query_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Recommander des dashboards Qlik basés sur le type de requête
        """
        query_type = query_result.get("query_type", "")
        
        # Mapping entre types de requêtes et dashboards
        recommendations = []
        
        if query_type in ["count_employees", "employee_list"]:
            recommendations.append({
                "dashboard": "Employee Analytics",
                "description": "Vue complète des employés avec pyramide des âges, répartition par département",
                "url": self.create_qlik_embed_url("employee_dashboard")
            })
        
        if query_type in ["salary_stats", "department_stats"]:
            recommendations.append({
                "dashboard": "HR KPIs Dashboard", 
                "description": "KPIs RH, masse salariale, budgets par département",
                "url": self.create_qlik_embed_url("kpi_dashboard")
            })
        
        if query_type == "turnover_analysis":
            recommendations.append({
                "dashboard": "Turnover & Retention",
                "description": "Analyse détaillée du turnover avec prédictions ML",
                "url": self.create_qlik_embed_url("turnover_dashboard")
            })
        
        # Toujours proposer le dashboard global
        if not recommendations:
            recommendations.append({
                "dashboard": "Global HR Dashboard",
                "description": "Vue d'ensemble de tous les indicateurs RH",
                "url": self.create_qlik_embed_url("main_dashboard")
            })
        
        return recommendations
    
    def export_to_qlik_format(self, data: List[Dict[str, Any]]) -> str:
        """
        Exporter au format QVD-like (JSON structure compatible Qlik)
        """
        if not data:
            return json.dumps({"fields": [], "records": []})
        
        # Extraire les champs
        fields = [{"name": key, "type": self._infer_type(value)} 
                  for key, value in data[0].items()]
        
        qlik_export = {
            "TableName": "QueryEngineExport",
            "Fields": fields,
            "Records": data,
            "RecordCount": len(data),
            "Metadata": {
                "ExportDate": str(datetime.now()),
                "Source": "Query Engine"
            }
        }
        
        return json.dumps(qlik_export, indent=2, default=str)
    
    def _infer_type(self, value: Any) -> str:
        """Inférer le type de données pour Qlik"""
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "DOUBLE"
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, (datetime, date)):
            return "TIMESTAMP"
        else:
            return "STRING"
    
    def get_available_dashboards(self) -> List[Dict[str, Any]]:
        """
        Liste des dashboards Qlik disponibles
        """
        return [
            {
                "id": "employee_dashboard",
                "name": "📊 Employee Analytics",
                "description": "Analyse complète des employés : pyramide des âges, répartition géographique, ancienneté",
                "metrics": ["Effectif total", "Pyramide des âges", "Répartition départements"],
                "url": "/qlik/employee-analytics"
            },
            {
                "id": "kpi_dashboard",
                "name": "📈 HR KPIs Dashboard",
                "description": "Indicateurs clés RH : masse salariale, budget formation, performance",
                "metrics": ["Masse salariale", "Budget/Département", "KPIs mensuels"],
                "url": "/qlik/kpi-dashboard"
            },
            {
                "id": "turnover_dashboard",
                "name": "🔄 Turnover & Retention",
                "description": "Analyse du turnover avec prédictions ML et analyse des départs",
                "metrics": ["Taux de turnover", "Prédictions ML", "Raisons de départ"],
                "url": "/qlik/turnover-dashboard"
            }
        ]


from datetime import datetime
