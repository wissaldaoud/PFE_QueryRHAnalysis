"""
HR Chatbot Service - Intelligence conversationnelle pour les RH
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.employee import Employee, EmploymentStatus
from app.models.department import Department
from typing import Dict, Any, Optional
import re


class ChatbotService:
    """Service de chatbot RH intelligent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Traiter une question utilisateur et retourner une réponse
        """
        question_lower = question.lower()
        
        # Détection d'intention (intent detection)
        if any(keyword in question_lower for keyword in ["combien", "nombre", "total"]):
            if "employé" in question_lower or "employee" in question_lower:
                return await self._count_employees(question_lower)
        
        if "turnover" in question_lower or "départ" in question_lower:
            return await self._calculate_turnover()
        
        if "salaire" in question_lower or "salary" in question_lower:
            if "moyen" in question_lower or "average" in question_lower:
                return await self._average_salary(question_lower)
        
        if "département" in question_lower or "department" in question_lower:
            if "liste" in question_lower or "affiche" in question_lower:
                return await self._list_by_department(question_lower)
            else:
                return await self._department_stats()
        
        if "manager" in question_lower:
            return await self._list_managers()
        
        if "nouveau" in question_lower or "récent" in question_lower:
            return await self._recent_hires()
        
        # Réponse par défaut si intention non reconnue
        return {
            "answer": "Je n'ai pas compris votre question. Essayez : 'Combien d'employés actifs?' ou 'Quel est le turnover?'",
            "suggestions": [
                "Combien d'employés actifs?",
                "Quel est le turnover?",
                "Salaire moyen par département?",
                "Liste des managers"
            ]
        }
    
    async def _count_employees(self, question: str) -> Dict[str, Any]:
        """Compter les employés (actifs, total, etc.)"""
        if "actif" in question:
            count = self.db.query(Employee).filter(
                Employee.employment_status == EmploymentStatus.ACTIVE
            ).count()
            status = "actifs"
        else:
            count = self.db.query(Employee).count()
            status = "au total"
        
        return {
            "answer": f"Il y a **{count} employés {status}** dans l'entreprise.",
            "data": {
                "count": count,
                "status": status
            },
            "suggestions": [
                "Quel est le turnover?",
                "Salaire moyen?",
                "Répartition par département?"
            ]
        }
    
    async def _calculate_turnover(self) -> Dict[str, Any]:
        """Calculer le taux de turnover"""
        total_employees = self.db.query(Employee).count()
        terminated = self.db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.TERMINATED
        ).count()
        
        if total_employees > 0:
            turnover_rate = (terminated / total_employees) * 100
        else:
            turnover_rate = 0
        
        return {
            "answer": f"Le taux de turnover est de **{turnover_rate:.1f}%** ({terminated} départs sur {total_employees} employés).",
            "data": {
                "turnover_rate": round(turnover_rate, 2),
                "terminated": terminated,
                "total": total_employees
            },
            "suggestions": [
                "Quels employés risquent de partir?",
                "Statistiques par département?",
                "Nouveaux employés?"
            ]
        }
    
    async def _average_salary(self, question: str) -> Dict[str, Any]:
        """Calculer le salaire moyen"""
        
        # Vérifier si demande par département
        dept_match = re.search(r'département\s+(\w+)', question)
        if dept_match:
            dept_name = dept_match.group(1)
            avg_salary = self.db.query(func.avg(Employee.salary)).join(
                Department
            ).filter(
                Department.name.ilike(f"%{dept_name}%")
            ).scalar()
            
            if avg_salary:
                return {
                    "answer": f"Le salaire moyen du département {dept_name} est de **{avg_salary:,.0f} €**.",
                    "data": {"average_salary": round(avg_salary, 2), "department": dept_name}
                }
        
        # Salaire moyen global
        avg_salary = self.db.query(func.avg(Employee.salary)).scalar()
        
        if avg_salary:
            return {
                "answer": f"Le salaire moyen dans l'entreprise est de **{avg_salary:,.0f} €**.",
                "data": {"average_salary": round(avg_salary, 2)},
                "suggestions": ["Salaire par département?", "Employés les mieux payés?"]
            }
        
        return {"answer": "Aucune donnée salariale disponible."}
    
    async def _list_by_department(self, question: str) -> Dict[str, Any]:
        """Lister les employés par département"""
        dept_match = re.search(r'département\s+(\w+)', question)
        
        if dept_match:
            dept_name = dept_match.group(1)
            employees = self.db.query(Employee).join(Department).filter(
                Department.name.ilike(f"%{dept_name}%")
            ).all()
            
            employee_list = [
                f"{emp.first_name} {emp.last_name} - {emp.job_title or 'N/A'}"
                for emp in employees
            ]
            
            return {
                "answer": f"**{len(employees)} employés** dans le département {dept_name}:\n" + 
                         "\n".join([f"- {emp}" for emp in employee_list[:10]]),
                "data": {
                    "department": dept_name,
                    "count": len(employees),
                    "employees": [{"name": f"{e.first_name} {e.last_name}", "title": e.job_title} for e in employees]
                }
            }
        
        return {"answer": "Précisez le département (ex: IT, HR, Finance)"}
    
    async def _department_stats(self) -> Dict[str, Any]:
        """Statistiques par département"""
        stats = self.db.query(
            Department.name,
            func.count(Employee.id).label('count')
        ).join(Employee).group_by(Department.name).all()
        
        stats_text = "\n".join([f"- **{dept}**: {count} employés" for dept, count in stats])
        
        return {
            "answer": f"**Répartition par département:**\n{stats_text}",
            "data": {
                "departments": [{"name": dept, "count": count} for dept, count in stats]
            },
            "suggestions": ["Salaire moyen par département?", "Liste des employés IT?"]
        }
    
    async def _list_managers(self) -> Dict[str, Any]:
        """Lister les managers"""
        managers = self.db.query(Employee).filter(
            Employee.id.in_(
                self.db.query(Employee.manager_id).filter(Employee.manager_id.isnot(None))
            )
        ).all()
        
        manager_list = [f"{m.first_name} {m.last_name} - {m.job_title or 'Manager'}" for m in managers]
        
        return {
            "answer": f"**{len(managers)} managers** dans l'entreprise:\n" + 
                     "\n".join([f"- {m}" for m in manager_list]),
            "data": {
                "count": len(managers),
                "managers": [{"name": f"{m.first_name} {m.last_name}", "title": m.job_title} for m in managers]
            }
        }
    
    async def _recent_hires(self) -> Dict[str, Any]:
        """Employés récemment embauchés"""
        from datetime import datetime, timedelta
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent = self.db.query(Employee).filter(
            Employee.hire_date >= thirty_days_ago
        ).all()
        
        return {
            "answer": f"**{len(recent)} nouveaux employés** ce mois-ci.",
            "data": {
                "count": len(recent),
                "employees": [{"name": f"{e.first_name} {e.last_name}", "hire_date": str(e.hire_date)} for e in recent]
            },
            "suggestions": ["Voir les détails?", "Turnover?"]
        }
