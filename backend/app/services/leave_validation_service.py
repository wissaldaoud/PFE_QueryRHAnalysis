"""
Service de validation des demandes de congé selon les critères d'acceptation
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.leave import LeaveRequest, LeaveStatus, LeaveType
from app.models.employee import Employee
from app.models.department import Department


class LeaveValidationResult:
    """Résultat de validation d'une demande de congé"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)
    
    def add_warning(self, message: str):
        self.warnings.append(message)


class LeaveValidationService:
    """Service de validation des demandes de congé"""
    
    # Configuration par défaut
    DEFAULT_MIN_TEAM_PRESENCE_PERCENTAGE = 40  # 40% de l'équipe doit être présente
    DEFAULT_MIN_TEAM_PRESENCE_COUNT = 2  # Au minimum 2 personnes
    DEFAULT_ADVANCE_NOTICE_DAYS = 14  # 2 semaines
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_leave_request(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        leave_type: LeaveType
    ) -> LeaveValidationResult:
        """
        Valider une demande de congé selon tous les critères d'acceptation.
        
        Retourne un LeaveValidationResult avec:
        - is_valid: True si la demande peut être approuvée
        - errors: Liste des erreurs bloquantes
        - warnings: Liste des avertissements non-bloquants
        """
        result = LeaveValidationResult(is_valid=True)
        
        # Calculer le nombre de jours
        days_requested = (end_date - start_date).days + 1
        
        # Récupérer l'employé
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            result.add_error("Employé introuvable")
            return result
        
        # 1. Vérifier le solde de congés
        self._validate_leave_balance(employee, days_requested, leave_type, result)
        
        # 2. Vérifier le délai de prévenance (sauf pour maladie)
        if leave_type != LeaveType.sick:
            self._validate_advance_notice(start_date, leave_type, result)
        
        # 3. Vérifier les chevauchements avec d'autres congés de l'équipe
        if employee.department_id:
            self._validate_team_availability(
                employee.department_id,
                employee_id,
                start_date,
                end_date,
                result
            )
        
        # 4. Vérifier les périodes bloquées
        self._validate_blocked_periods(start_date, end_date, result)
        
        return result
    
    def _validate_leave_balance(
        self,
        employee: Employee,
        days_requested: int,
        leave_type: LeaveType,
        result: LeaveValidationResult
    ):
        """Critère 4: Solde de congés suffisant"""
        if leave_type == LeaveType.annual:
            # Calculer le solde disponible
            current_year = datetime.now().year
            
            # Nombre de jours pris cette année (approuvés ou en attente)
            days_taken = self.db.query(func.sum(LeaveRequest.days_requested)).filter(
                and_(
                    LeaveRequest.employee_id == employee.id,
                    LeaveRequest.leave_type == LeaveType.annual,
                    LeaveRequest.status.in_([
                        LeaveStatus.pending,
                        LeaveStatus.manager_approved,
                        LeaveStatus.hr_approved
                    ]),
                    func.extract('year', LeaveRequest.start_date) == current_year
                )
            ).scalar() or 0
            
            # Solde annuel (par défaut 30 jours)
            annual_allowance = 30
            available_days = annual_allowance - days_taken
            
            if days_requested > available_days:
                result.add_error(
                    f"Solde de congés insuffisant. Disponible: {available_days} jours, "
                    f"Demandé: {days_requested} jours"
                )
            elif days_requested > available_days * 0.8:
                result.add_warning(
                    f"Attention: Vous utilisez {days_requested}/{available_days} jours disponibles"
                )
    
    def _validate_advance_notice(
        self,
        start_date: date,
        leave_type: LeaveType,
        result: LeaveValidationResult
    ):
        """Critère 3: Délai de prévenance respecté"""
        days_until_start = (start_date - date.today()).days
        
        if leave_type == LeaveType.annual:
            if days_until_start < self.DEFAULT_ADVANCE_NOTICE_DAYS:
                result.add_error(
                    f"Délai de prévenance insuffisant. Les congés annuels doivent être "
                    f"demandés au moins {self.DEFAULT_ADVANCE_NOTICE_DAYS} jours à l'avance. "
                    f"Délai actuel: {days_until_start} jours"
                )
        elif leave_type == LeaveType.unpaid:
            # Congé sans solde: même règle que congé annuel
            if days_until_start < self.DEFAULT_ADVANCE_NOTICE_DAYS:
                result.add_warning(
                    f"Délai de prévenance court pour un congé sans solde ({days_until_start} jours)"
                )
    
    def _validate_team_availability(
        self,
        department_id: int,
        requesting_employee_id: int,
        start_date: date,
        end_date: date,
        result: LeaveValidationResult
    ):
        """
        Critères 1 & 2: Effectif minimum et pas de chevauchement
        """
        # Compter le nombre total d'employés dans le département
        total_employees = self.db.query(func.count(Employee.id)).filter(
            Employee.department_id == department_id
        ).scalar() or 0
        
        if total_employees == 0:
            return  # Pas d'équipe à vérifier
        
        # Trouver les employés en congé sur la période demandée
        overlapping_leaves = self.db.query(LeaveRequest).join(
            Employee, LeaveRequest.employee_id == Employee.id
        ).filter(
            and_(
                Employee.department_id == department_id,
                LeaveRequest.employee_id != requesting_employee_id,
                LeaveRequest.status.in_([
                    LeaveStatus.pending,
                    LeaveStatus.manager_approved,
                    LeaveStatus.hr_approved
                ]),
                or_(
                    # La demande existante chevauche la nouvelle demande
                    and_(
                        LeaveRequest.start_date <= end_date,
                        LeaveRequest.end_date >= start_date
                    )
                )
            )
        ).all()
        
        employees_on_leave = len(set([leave.employee_id for leave in overlapping_leaves]))
        employees_present = total_employees - employees_on_leave - 1  # -1 pour le demandeur
        
        # Critère 1: Effectif minimum
        min_required_count = max(
            self.DEFAULT_MIN_TEAM_PRESENCE_COUNT,
            int(total_employees * self.DEFAULT_MIN_TEAM_PRESENCE_PERCENTAGE / 100)
        )
        
        if employees_present < min_required_count:
            result.add_error(
                f"Effectif minimum non garanti. L'équipe a {total_employees} personnes, "
                f"{employees_on_leave} déjà en congé sur cette période. "
                f"Minimum requis: {min_required_count} personnes présentes, "
                f"Disponibles si approuvé: {employees_present} personnes"
            )
        elif employees_present < min_required_count + 1:
            result.add_warning(
                f"Effectif limite: {employees_present} personnes présentes si approuvé "
                f"(minimum: {min_required_count})"
            )
        
        # Critère 2: Informer des chevauchements
        if overlapping_leaves:
            employee_names = []
            for leave in overlapping_leaves[:3]:  # Limiter à 3 noms
                emp = self.db.query(Employee).filter(Employee.id == leave.employee_id).first()
                if emp:
                    employee_names.append(f"{emp.first_name} {emp.last_name}")
            
            if len(overlapping_leaves) > 3:
                employee_names.append(f"et {len(overlapping_leaves) - 3} autres")
            
            result.add_warning(
                f"Congés simultanés: {', '.join(employee_names)} "
                f"({len(overlapping_leaves)} personne(s))"
            )
    
    def _validate_blocked_periods(
        self,
        start_date: date,
        end_date: date,
        result: LeaveValidationResult
    ):
        """Critère 5: Période non bloquée"""
        # Périodes de clôture comptable (par exemple fin de mois, fin d'année)
        blocked_periods = self._get_blocked_periods(start_date.year)
        
        for period_name, period_start, period_end in blocked_periods:
            # Vérifier si la demande chevauche une période bloquée
            if not (end_date < period_start or start_date > period_end):
                result.add_error(
                    f"Période bloquée: {period_name} "
                    f"({period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')}). "
                    f"Aucun congé n'est autorisé pendant cette période."
                )
    
    def _get_blocked_periods(self, year: int) -> List[Tuple[str, date, date]]:
        """
        Retourner les périodes bloquées pour une année donnée.
        Format: [(nom, date_début, date_fin), ...]
        """
        blocked = []
        
        # Clôture annuelle (20-31 décembre)
        blocked.append((
            "Clôture annuelle",
            date(year, 12, 20),
            date(year, 12, 31)
        ))
        
        # Clôtures trimestrielles (dernière semaine de chaque trimestre)
        quarters = [
            ("Clôture Q1", 3, 25, 31),
            ("Clôture Q2", 6, 25, 30),
            ("Clôture Q3", 9, 25, 30),
        ]
        
        for name, month, start_day, end_day in quarters:
            blocked.append((
                name,
                date(year, month, start_day),
                date(year, month, end_day)
            ))
        
        return blocked
    
    def get_validation_summary(self, result: LeaveValidationResult) -> Dict:
        """Retourner un résumé de la validation pour l'API"""
        return {
            "is_valid": result.is_valid,
            "can_be_approved": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings)
        }
