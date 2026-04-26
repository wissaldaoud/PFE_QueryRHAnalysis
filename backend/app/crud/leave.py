"""
CRUD operations for Leave Requests
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from typing import Optional, List

from app.models.leave import LeaveRequest, LeaveType, LeaveStatus
from app.models.employee import Employee
from app.models.user import User
from app.schemas.leave import LeaveRequestCreate, LeaveRequestUpdate


def calculate_days(start_date: date, end_date: date) -> int:
    """Calcule le nombre de jours ouvrés entre deux dates"""
    delta = end_date - start_date
    return delta.days + 1  # Inclut le jour de début


def create_leave_request(
    db: Session, 
    request: LeaveRequestCreate, 
    employee_id: int
) -> LeaveRequest:
    """Créer une nouvelle demande de congé"""
    days = calculate_days(request.start_date, request.end_date)
    
    db_request = LeaveRequest(
        employee_id=employee_id,
        leave_type=request.leave_type,
        start_date=request.start_date,
        end_date=request.end_date,
        days_requested=days,
        reason=request.reason,
        status=LeaveStatus.pending
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_leave_request(db: Session, request_id: int) -> Optional[LeaveRequest]:
    """Récupérer une demande par ID"""
    return db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()


def get_leave_requests(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    employee_id: Optional[int] = None,
    employee_ids: Optional[List[int]] = None,  # Pour filtrer par équipe (manager)
    status: Optional[LeaveStatus] = None,
    leave_type: Optional[LeaveType] = None,
    year: Optional[int] = None
) -> tuple[List[LeaveRequest], int]:
    """Récupérer les demandes avec filtres et pagination"""
    query = db.query(LeaveRequest)
    
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    elif employee_ids:
        # Filtrer par liste d'IDs (pour manager qui voit son équipe)
        query = query.filter(LeaveRequest.employee_id.in_(employee_ids))
    if status:
        query = query.filter(LeaveRequest.status == status)
    if leave_type:
        query = query.filter(LeaveRequest.leave_type == leave_type)
    if year:
        query = query.filter(extract('year', LeaveRequest.start_date) == year)
    
    total = query.count()
    items = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    return items, total


def get_pending_requests_for_manager(
    db: Session,
    manager_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[LeaveRequest], int]:
    """Récupérer les demandes en attente pour un manager (ses subordonnés)"""
    query = db.query(LeaveRequest).join(Employee).filter(
        Employee.manager_id == manager_id,
        LeaveRequest.status == LeaveStatus.pending
    )
    
    total = query.count()
    items = query.order_by(LeaveRequest.created_at.asc()).offset(skip).limit(limit).all()
    
    return items, total


def update_leave_request(
    db: Session,
    request_id: int,
    update_data: LeaveRequestUpdate
) -> Optional[LeaveRequest]:
    """Mettre à jour une demande (seulement si pending)"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.pending:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_request, key, value)
    
    # Recalculer les jours si les dates ont changé
    if 'start_date' in update_dict or 'end_date' in update_dict:
        db_request.days_requested = calculate_days(
            db_request.start_date, 
            db_request.end_date
        )
    
    db.commit()
    db.refresh(db_request)
    return db_request


def approve_leave_request(
    db: Session,
    request_id: int,
    approver_id: int
) -> Optional[LeaveRequest]:
    """Approuver une demande de congé"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.pending:
        return None
    
    db_request.status = LeaveStatus.approved
    db_request.approved_by = approver_id
    db_request.approval_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_request)
    return db_request


def reject_leave_request(
    db: Session,
    request_id: int,
    approver_id: int,
    rejection_reason: str
) -> Optional[LeaveRequest]:
    """Rejeter une demande de congé"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.pending:
        return None
    
    db_request.status = LeaveStatus.rejected
    db_request.approved_by = approver_id
    db_request.approval_date = datetime.utcnow()
    db_request.rejection_reason = rejection_reason
    
    db.commit()
    db.refresh(db_request)
    return db_request


def cancel_leave_request(
    db: Session,
    request_id: int,
    employee_id: int
) -> Optional[LeaveRequest]:
    """Annuler sa propre demande de congé"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.employee_id != employee_id:
        return None
    
    if db_request.status not in [LeaveStatus.pending, LeaveStatus.approved]:
        return None
    
    db_request.status = LeaveStatus.cancelled
    
    db.commit()
    db.refresh(db_request)
    return db_request


def get_employee_leave_balance(
    db: Session,
    employee_id: int,
    year: int = None
) -> dict:
    """Calculer le solde de congés d'un employé"""
    if year is None:
        year = date.today().year
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return None
    
    # Récupérer les congés approuvés de l'année
    approved_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_([LeaveStatus.hr_approved]),  # Seulement les approuvés par RH (final)
        extract('year', LeaveRequest.start_date) == year
    ).all()
    
    annual_used = sum(l.days_requested for l in approved_leaves if l.leave_type == LeaveType.annual)
    sick_used = sum(l.days_requested for l in approved_leaves if l.leave_type == LeaveType.sick)
    unpaid_used = sum(l.days_requested for l in approved_leaves if l.leave_type == LeaveType.unpaid)
    
    annual_total = 25  # Jours par défaut (pourrait être dans les paramètres)
    
    return {
        "employee_id": employee_id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "year": year,
        "annual_total": annual_total,
        "annual_used": annual_used,
        "annual_remaining": annual_total - annual_used,
        "sick_used": sick_used,
        "unpaid_used": unpaid_used
    }


def get_leave_statistics(db: Session, year: int = None) -> dict:
    """Statistiques globales des congés"""
    if year is None:
        year = date.today().year
    
    base_query = db.query(LeaveRequest).filter(
        extract('year', LeaveRequest.start_date) == year
    )
    
    total = base_query.count()
    pending = base_query.filter(LeaveRequest.status == LeaveStatus.pending).count()
    manager_approved = base_query.filter(LeaveRequest.status == LeaveStatus.manager_approved).count()
    approved = base_query.filter(LeaveRequest.status == LeaveStatus.hr_approved).count()
    rejected = base_query.filter(LeaveRequest.status == LeaveStatus.rejected).count()
    
    # Par type
    by_type = {}
    for leave_type in LeaveType:
        count = base_query.filter(LeaveRequest.leave_type == leave_type).count()
        by_type[leave_type.value] = count
    
    return {
        "year": year,
        "total_requests": total,
        "pending_count": pending,
        "manager_approved_count": manager_approved,
        "approved_count": approved,
        "rejected_count": rejected,
        "by_type": by_type
    }


# ============================================================
# WORKFLOW HIÉRARCHIQUE - Nouveau système
# ============================================================

def manager_approve_leave_request(
    db: Session,
    request_id: int,
    manager_id: int
) -> Optional[LeaveRequest]:
    """Approuver une demande de congé par le manager (étape 1)"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.pending:
        return None
    
    db_request.status = LeaveStatus.manager_approved
    db_request.manager_approved_by = manager_id
    db_request.manager_approval_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_request)
    return db_request


def manager_reject_leave_request(
    db: Session,
    request_id: int,
    manager_id: int,
    rejection_reason: str
) -> Optional[LeaveRequest]:
    """Rejeter une demande de congé par le manager"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.pending:
        return None
    
    db_request.status = LeaveStatus.rejected
    db_request.rejected_by = manager_id
    db_request.rejection_date = datetime.utcnow()
    db_request.rejection_reason = rejection_reason
    
    db.commit()
    db.refresh(db_request)
    return db_request


def hr_approve_leave_request(
    db: Session,
    request_id: int,
    hr_user_id: int
) -> Optional[LeaveRequest]:
    """Approuver une demande de congé par RH (étape finale)"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.manager_approved:
        return None
    
    db_request.status = LeaveStatus.hr_approved
    db_request.hr_approved_by = hr_user_id
    db_request.hr_approval_date = datetime.utcnow()
    
    # Rétrocompatibilité
    db_request.approved_by = hr_user_id
    db_request.approval_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_request)
    return db_request


def hr_reject_leave_request(
    db: Session,
    request_id: int,
    hr_user_id: int,
    rejection_reason: str
) -> Optional[LeaveRequest]:
    """Rejeter une demande de congé par RH"""
    db_request = get_leave_request(db, request_id)
    
    if not db_request or db_request.status != LeaveStatus.manager_approved:
        return None
    
    db_request.status = LeaveStatus.rejected
    db_request.rejected_by = hr_user_id
    db_request.rejection_date = datetime.utcnow()
    db_request.rejection_reason = rejection_reason
    
    db.commit()
    db.refresh(db_request)
    return db_request
