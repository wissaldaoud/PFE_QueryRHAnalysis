"""
Employee management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from app.db.base import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee, EmploymentStatus
from app.models.user import User, UserRole
from app.models.leave import LeaveRequest
from app.api.deps import get_current_user, require_hr, require_admin
from sqlalchemy import func
from datetime import datetime

router = APIRouter()


@router.post("/fix-contract-types")
async def fix_contract_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Met à jour les employés sans type de contrat avec 'CDI' par défaut
    (Admin uniquement)
    """
    # Compter les employés sans type de contrat
    null_count = db.query(Employee).filter(Employee.contract_type == None).count()
    
    if null_count > 0:
        # Mettre à jour avec CDI
        employees = db.query(Employee).filter(Employee.contract_type == None).all()
        for emp in employees:
            emp.contract_type = "CDI"
        
        db.commit()
        
        return {
            "message": f"{len(employees)} employés mis à jour avec type 'CDI'",
            "updated_count": len(employees)
        }
    else:
        return {
            "message": "Tous les employés ont déjà un type de contrat",
            "updated_count": 0
        }


class AssignEmployeeRequest(BaseModel):
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    job_title: Optional[str] = None


@router.get("/unassigned", response_model=List[EmployeeResponse])
async def list_unassigned_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)  # Only HR can see unassigned
):
    """
    Liste des employés sans département ou manager (pour affectation RH)
    Les managers/admins n'ont besoin que d'un département (pas de manager)
    Les employés simples ont besoin d'un département ET d'un manager
    """
    # Récupérer tous les employés actifs avec leurs comptes utilisateurs
    employees = db.query(Employee).join(
        User, User.employee_id == Employee.id, isouter=True
    ).filter(
        Employee.employment_status == EmploymentStatus.active
    ).all()
    
    unassigned = []
    for emp in employees:
        # Récupérer le compte utilisateur associé
        user = db.query(User).filter(User.employee_id == emp.id).first()
        
        # Toujours vérifier le département
        if emp.department_id is None:
            unassigned.append(emp)
            continue
        
        # Si c'est un employé simple et qu'il n'a pas de manager, il est non assigné
        if user and user.role == UserRole.employee and emp.manager_id is None:
            unassigned.append(emp)
    
    return unassigned


@router.get("/managers", response_model=List[EmployeeResponse])
async def list_managers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)  # Only HR can see managers list
):
    """
    Liste des employés qui peuvent être managers (rôle manager, hr_manager ou admin)
    """
    # Récupérer les employés actifs qui sont des managers
    managers = db.query(Employee).join(
        User, User.employee_id == Employee.id
    ).filter(
        User.role.in_([UserRole.manager, UserRole.hr_manager, UserRole.admin]),
        Employee.employment_status == EmploymentStatus.active
    ).all()
    
    return managers


@router.post("/{employee_id}/assign")
async def assign_employee(
    employee_id: int,
    assignment: AssignEmployeeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)  # Only HR can assign
):
    """
    Affecter un employé à un département et/ou un manager (RH uniquement)
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    if assignment.department_id is not None:
        employee.department_id = assignment.department_id
    
    if assignment.manager_id is not None:
        # Vérifier que le manager existe
        manager = db.query(Employee).filter(Employee.id == assignment.manager_id).first()
        if not manager:
            raise HTTPException(status_code=400, detail="Manager non trouvé")
        employee.manager_id = assignment.manager_id
    
    if assignment.job_title:
        employee.job_title = assignment.job_title
    
    db.commit()
    db.refresh(employee)
    
    return {
        "message": f"Employé {employee.first_name} {employee.last_name} affecté avec succès",
        "employee": employee
    }


@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: Optional[int] = None,
    employment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requires authentication
):
    """
    Retrieve list of employees with pagination and optional filters
    - Admin/HR: tous les employés
    - Manager: uniquement son équipe (même département)
    - Employee: uniquement lui-même
    """
    query = db.query(Employee)
    
    # Filtrer selon le rôle de l'utilisateur
    if current_user.role == UserRole.employee:
        # Employee voit uniquement son propre profil
        if current_user.employee_id:
            query = query.filter(Employee.id == current_user.employee_id)
        else:
            # Si pas lié à un employee, retourner liste vide
            return []
    elif current_user.role == UserRole.manager:
        # Manager voit uniquement les employés de son département
        if current_user.employee_id:
            manager_employee = db.query(Employee).filter(Employee.id == current_user.employee_id).first()
            if manager_employee and manager_employee.department_id:
                query = query.filter(Employee.department_id == manager_employee.department_id)
            else:
                return []
        else:
            return []
    # Admin, HR Manager, Analyst peuvent voir tous les employés
    
    # Apply additional filters if provided
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if employment_status:
        query = query.filter(Employee.employment_status == employment_status)
    
    employees = query.offset(skip).limit(limit).all()
    return employees


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)  # Only HR or Admin can create
):
    """
    Create a new employee (HR Manager or Admin only)
    """
    # Check if email already exists
    existing = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if employee_code already exists
    existing_code = db.query(Employee).filter(Employee.employee_code == employee.employee_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Employee code already exists")
    
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requires authentication
):
    """
    Get employee by ID (Authenticated users)
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)  # Only HR or Admin can update
):
    """
    Update employee information (HR Manager or Admin only)
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_data = employee.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin can delete
):
    """
    Delete an employee (Admin only - soft delete)
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db_employee.employment_status = "terminated"
    db.commit()
    return {"message": "Employee deleted successfully"}


@router.get("/{employee_id}/turnover-data")
async def get_employee_turnover_data(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les données nécessaires pour la prédiction de turnover
    Calcul automatique depuis la base de données
    """
    try:
        # Récupérer l'employé
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Debug: Log les champs de l'employé
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Employee {employee.id}: date_of_birth={employee.date_of_birth}, hire_date={employee.hire_date}")
        
        # Calculer les absences (congés approuvés)
        # Note: On compte les congés approuvés par le manager et ceux approuvés par RH
        from app.models.leave import LeaveStatus
        
        # D'abord, compter TOUS les congés pour debug
        all_leaves = db.query(
            func.count(LeaveRequest.id).label('total'),
            func.coalesce(func.sum(LeaveRequest.days_requested), 0).label('total_days')
        ).filter(
            LeaveRequest.employee_id == employee_id
        ).first()
        
        logger.info(f"Employee {employee_id}: {all_leaves.total if all_leaves else 0} congés au total, {all_leaves.total_days if all_leaves else 0} jours")
        
        # Compter par statut
        status_counts = db.query(
            LeaveRequest.status,
            func.count(LeaveRequest.id),
            func.coalesce(func.sum(LeaveRequest.days_requested), 0)
        ).filter(
            LeaveRequest.employee_id == employee_id
        ).group_by(LeaveRequest.status).all()
        
        for status, count, days in status_counts:
            logger.info(f"  - Status '{status}': {count} congés, {days} jours")
        
        # Maintenant, compter seulement les approuvés
        leave_stats = db.query(
            func.count(LeaveRequest.id).label('nb_absences'),
            func.coalesce(func.sum(LeaveRequest.days_requested), 0).label('total_jours_absence')
        ).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_([LeaveStatus.manager_approved, LeaveStatus.hr_approved])
        ).first()
        
        nb_absences = leave_stats.nb_absences if leave_stats else 0
        total_jours_absence = int(leave_stats.total_jours_absence) if leave_stats else 0
        
        # Calculer âge
        age = 0
        if employee.date_of_birth:
            today = datetime.now().date()
            birth_date = employee.date_of_birth if isinstance(employee.date_of_birth, datetime) else datetime.strptime(str(employee.date_of_birth), "%Y-%m-%d").date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Calculer ancienneté
        anciennete_annees = 0
        duree_presence_jours = 0
        if employee.hire_date:
            today = datetime.now().date()
            hire_date = employee.hire_date if isinstance(employee.hire_date, datetime) else datetime.strptime(str(employee.hire_date), "%Y-%m-%d").date()
            days_diff = (today - hire_date).days
            anciennete_annees = round(days_diff / 365.25, 2)
            duree_presence_jours = days_diff
        
        # Mapper le type de contrat
        type_contrat = "Inconnu"
        contract_type_raw = getattr(employee, 'contract_type', None)
        if contract_type_raw:
            contract = contract_type_raw.upper()
            if "CDI" in contract or "INDETERMINEE" in contract or "INDÉTERMINÉE" in contract:
                type_contrat = "CDI"
            elif "CDD" in contract or "DETERMINEE" in contract or "DÉTERMINÉE" in contract:
                type_contrat = "CDD sur emploi permanent"
            elif "STAGE" in contract or "STAGIAIRE" in contract:
                type_contrat = "Stagiaire"
            elif "APPRENTI" in contract:
                type_contrat = "Apprenti"
            elif "FREELANCE" in contract or "TEMPORAIRE" in contract:
                type_contrat = "Temporaire"
        
        # Déterminer le sexe (à affiner selon vos données)
        sexe = "Masculin"  # Par défaut, à améliorer si vous avez un champ sexe dans votre BD
        
        return {
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": f"{employee.first_name} {employee.last_name}",
            "date_of_birth": employee.date_of_birth.isoformat() if employee.date_of_birth else None,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "age": age,
            "anciennete_annees": anciennete_annees,
            "duree_presence_jours": duree_presence_jours,
            "sexe": sexe,
            "type_contrat": type_contrat,
            "contract_type_raw": contract_type_raw,
            "nb_absences": nb_absences,
            "total_jours_absence": total_jours_absence,
            "salary": float(employee.salary) if employee.salary else None,
            "employment_status": employee.employment_status,
            "department_name": employee.department.name if employee.department else None,
            "data_source": "database",
            "computed_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Erreur dans get_employee_turnover_data pour employee_id={employee_id}: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des données: {str(e)}"
        )
