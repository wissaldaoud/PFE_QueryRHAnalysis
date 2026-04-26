"""
Service Chatbot Entraîné - Utilise le modèle ML pour classifier les intentions
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.employee import Employee, EmploymentStatus
from app.models.department import Department
from typing import Dict, Any, Optional
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import json
import os


class TrainedChatbotService:
    """Service de chatbot utilisant un modèle ML entraîné"""
    
    def __init__(self, db: Session, model_path='./chatbot_model'):
        self.db = db
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.intent_labels = []
        self._load_model()
    
    def _load_model(self):
        """Charger le modèle entraîné"""
        try:
            if os.path.exists(self.model_path):
                self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
                self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
                
                with open(f'{self.model_path}/intent_labels.json', 'r') as f:
                    self.intent_labels = json.load(f)
                
                print(f"✅ Modèle chatbot chargé depuis {self.model_path}")
            else:
                print(f"⚠️ Modèle non trouvé dans {self.model_path}. Utilisez train_chatbot.py d'abord.")
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
    
    def predict_intent(self, question: str) -> tuple:
        """Prédire l'intention d'une question"""
        if self.model is None:
            return "general_info", 0.0
        
        inputs = self.tokenizer(question, return_tensors='pt', truncation=True, padding=True, max_length=128)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        intent_name = self.intent_labels[predicted_class]
        return intent_name, confidence
    
    async def process_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Traiter une question utilisateur avec le modèle ML entraîné
        """
        # Prédire l'intention
        intent, confidence = self.predict_intent(question)
        
        # Si confiance faible, réponse générique
        if confidence < 0.6:
            return {
                "answer": "Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler?",
                "intent": intent,
                "confidence": float(confidence),
                "suggestions": [
                    "Combien d'employés actifs?",
                    "Quel est le turnover?",
                    "Salaire moyen?",
                    "Liste des départements"
                ]
            }
        
        # Router vers la bonne fonction selon l'intention
        intent_handlers = {
            'count_employees': self._handle_count_employees,
            'turnover_rate': self._handle_turnover,
            'salary_info': self._handle_salary,
            'department_info': self._handle_departments,
            'list_employees': self._handle_list_employees,
            'employee_search': self._handle_search_employee,
            'absence_info': self._handle_absence,
            'manager_info': self._handle_managers,
            'recent_hires': self._handle_recent_hires,
            'general_info': self._handle_general_info,
        }
        
        handler = intent_handlers.get(intent, self._handle_general_info)
        response = await handler(question)
        
        # Ajouter les métadonnées ML
        response['intent'] = intent
        response['confidence'] = float(confidence)
        
        return response
    
    # === HANDLERS POUR CHAQUE INTENTION ===
    
    async def _handle_count_employees(self, question: str) -> Dict[str, Any]:
        """Compter les employés"""
        active_count = self.db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.ACTIVE
        ).count()
        total_count = self.db.query(Employee).count()
        
        return {
            "answer": f"📊 Il y a **{active_count} employés actifs** sur un total de **{total_count} employés**.",
            "data": {
                "active": active_count,
                "total": total_count
            },
            "suggestions": ["Quel est le turnover?", "Répartition par département?"]
        }
    
    async def _handle_turnover(self, question: str) -> Dict[str, Any]:
        """Calculer le turnover"""
        total = self.db.query(Employee).count()
        terminated = self.db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.TERMINATED
        ).count()
        
        turnover_rate = (terminated / total * 100) if total > 0 else 0
        
        return {
            "answer": f"📈 Le taux de turnover est de **{turnover_rate:.1f}%** ({terminated} départs sur {total} employés).",
            "data": {
                "rate": round(turnover_rate, 2),
                "departed": terminated,
                "total": total
            },
            "suggestions": ["Qui risque de partir?", "Nouveaux embauchés?"]
        }
    
    async def _handle_salary(self, question: str) -> Dict[str, Any]:
        """Informations salariales"""
        avg_salary = self.db.query(func.avg(Employee.salary)).scalar()
        
        if avg_salary:
            return {
                "answer": f"💰 Le salaire moyen est de **{avg_salary:,.0f} €**.",
                "data": {"average": round(avg_salary, 2)},
                "suggestions": ["Salaire par département?", "Fourchette de salaire?"]
            }
        return {"answer": "Aucune donnée salariale disponible."}
    
    async def _handle_departments(self, question: str) -> Dict[str, Any]:
        """Informations départements"""
        depts = self.db.query(
            Department.name,
            func.count(Employee.id).label('count')
        ).join(Employee).group_by(Department.name).all()
        
        dept_text = "\n".join([f"- **{name}**: {count} employés" for name, count in depts])
        
        return {
            "answer": f"🏢 **Départements de l'entreprise:**\n{dept_text}",
            "data": {"departments": [{"name": d[0], "count": d[1]} for d in depts]},
            "suggestions": ["Employés du département IT?", "Salaire moyen par département?"]
        }
    
    async def _handle_list_employees(self, question: str) -> Dict[str, Any]:
        """Lister les employés (avec extraction du département)"""
        # Essayer d'extraire le département de la question
        question_lower = question.lower()
        
        # Mapping simple (à améliorer avec NER)
        dept_keywords = {
            'it': 'IT',
            'rh': 'HR',
            'finance': 'Finance',
            'marketing': 'Marketing',
            'vente': 'Sales'
        }
        
        dept_name = None
        for keyword, dept in dept_keywords.items():
            if keyword in question_lower:
                dept_name = dept
                break
        
        if dept_name:
            employees = self.db.query(Employee).join(Department).filter(
                Department.name.ilike(f"%{dept_name}%")
            ).limit(10).all()
            
            emp_list = "\n".join([f"- {e.first_name} {e.last_name} - {e.job_title or 'N/A'}" for e in employees])
            
            return {
                "answer": f"👥 **Employés du département {dept_name}** ({len(employees)}):\n{emp_list}",
                "data": {"department": dept_name, "count": len(employees)}
            }
        
        return {"answer": "Précisez le département (IT, RH, Finance, etc.)"}
    
    async def _handle_search_employee(self, question: str) -> Dict[str, Any]:
        """Chercher un employé spécifique"""
        # Extraction basique du nom (à améliorer avec NER)
        words = question.split()
        
        # Chercher dans la base
        results = self.db.query(Employee).filter(
            (Employee.first_name.ilike(f"%{' '.join(words[-2:])}%")) |
            (Employee.last_name.ilike(f"%{' '.join(words[-2:])}%"))
        ).limit(5).all()
        
        if results:
            emp = results[0]
            return {
                "answer": f"👤 **{emp.first_name} {emp.last_name}**\n" +
                         f"- Poste: {emp.job_title or 'N/A'}\n" +
                         f"- Email: {emp.email}\n" +
                         f"- Statut: {emp.employment_status.value}",
                "data": {
                    "name": f"{emp.first_name} {emp.last_name}",
                    "email": emp.email,
                    "status": emp.employment_status.value
                }
            }
        
        return {"answer": "Employé non trouvé. Essayez avec un autre nom."}
    
    async def _handle_absence(self, question: str) -> Dict[str, Any]:
        """Informations sur les absences"""
        # Placeholder - nécessite table attendance
        return {
            "answer": "📅 Les données d'absence seront disponibles prochainement.",
            "suggestions": ["Taux de présence?", "Qui est en congé?"]
        }
    
    async def _handle_managers(self, question: str) -> Dict[str, Any]:
        """Liste des managers"""
        managers = self.db.query(Employee).filter(
            Employee.id.in_(
                self.db.query(Employee.manager_id).filter(Employee.manager_id.isnot(None))
            )
        ).all()
        
        manager_list = "\n".join([f"- {m.first_name} {m.last_name}" for m in managers[:10]])
        
        return {
            "answer": f"👔 **Managers de l'entreprise** ({len(managers)}):\n{manager_list}",
            "data": {"count": len(managers)}
        }
    
    async def _handle_recent_hires(self, question: str) -> Dict[str, Any]:
        """Nouveaux embauchés"""
        from datetime import datetime, timedelta
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent = self.db.query(Employee).filter(
            Employee.hire_date >= thirty_days_ago
        ).all()
        
        return {
            "answer": f"🆕 **{len(recent)} nouveaux employés** ce mois-ci.",
            "data": {"count": len(recent)},
            "suggestions": ["Détails sur les nouveaux?", "Turnover?"]
        }
    
    async def _handle_general_info(self, question: str) -> Dict[str, Any]:
        """Informations générales"""
        return {
            "answer": "👋 Bonjour! Je suis votre assistant RH. Je peux vous aider avec:\n" +
                     "- Statistiques sur les employés\n" +
                     "- Informations sur les départements\n" +
                     "- Calculs de turnover\n" +
                     "- Recherche d'employés",
            "suggestions": [
                "Combien d'employés?",
                "Liste des départements",
                "Quel est le turnover?",
                "Salaire moyen"
            ]
        }
