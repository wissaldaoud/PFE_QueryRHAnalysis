"""
API endpoints for Leave Management
7 endpoints as per cahier des charges V2 + Workflow hiérarchique
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.base import get_db
from app.api.deps import (
    get_current_user,
    require_hr,
    require_manager
)
from app.models.user import User, UserRole
from app.models.leave import LeaveStatus, LeaveType
from app.models.employee import Employee
from app.models.notification import NotificationType
from app.crud import leave as leave_crud
from app.crud import notification as notification_crud
from app.schemas.leave import (
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestResponse,
    LeaveRequestList,
    LeaveApproval,
    LeaveRejection,
    LeaveBalance,
    LeaveStatistics
)
from app.services.email_service import send_leave_approved_email, send_leave_rejected_email
from app.services.leave_validation_service import LeaveValidationService

router = APIRouter()


def enrich_leave_response(leave_request, db: Session) -> dict:
    """Enrichir la réponse avec les noms"""
    from app.models.employee import Employee
    
    data = {
        "id": leave_request.id,
        "employee_id": leave_request.employee_id,
        "leave_type": leave_request.leave_type,
        "start_date": leave_request.start_date,
        "end_date": leave_request.end_date,
        "days_requested": leave_request.days_requested,
        "reason": leave_request.reason,
        "status": leave_request.status,
        "approved_by": leave_request.approved_by,
        "approval_date": leave_request.approval_date,
        "rejection_reason": leave_request.rejection_reason,
        "created_at": leave_request.created_at,
        "updated_at": leave_request.updated_at,
    }
    
    # Ajouter le nom de l'employé
    employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
    if employee:
        data["employee_name"] = f"{employee.first_name} {employee.last_name}"
    
    # Ajouter le nom de l'approbateur
    if leave_request.approved_by:
        approver = db.query(User).filter(User.id == leave_request.approved_by).first()
        if approver:
            data["approver_name"] = approver.full_name
    
    return data


# ============================================================
# ENDPOINT 1: Créer une demande de congé
# ============================================================
@router.post("/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    request: LeaveRequestCreate,
    employee_id: int = Query(None, description="ID de l'employé demandeur (optionnel pour les employés)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer une nouvelle demande de congé.
    
    - Un employé ne peut demander que pour lui-même (employee_id ignoré)
    - HR/Admin peut créer pour n'importe quel employé
    """
    # Déterminer l'employee_id selon le rôle
    if current_user.role == UserRole.employee:
        # Un employé ne peut demander que pour lui-même
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Votre compte n'est pas lié à un employé. Contactez les RH."
            )
        employee_id = current_user.employee_id
    elif employee_id is None:
        # HR/Admin doit spécifier l'employé
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez spécifier l'employé (employee_id)"
        )
    
    # Vérifier que les dates sont dans le futur
    if request.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de début doit être dans le futur"
        )
    
    # ✅ CRITÈRES D'ACCEPTATION - Validation automatique
    validation_service = LeaveValidationService(db)
    validation_result = validation_service.validate_leave_request(
        employee_id=employee_id,
        start_date=request.start_date,
        end_date=request.end_date,
        leave_type=request.leave_type
    )
    
    # Si la validation échoue, retourner les erreurs
    if not validation_result.is_valid:
        error_message = "Demande de congé refusée:\n" + "\n".join(
            [f"❌ {error}" for error in validation_result.errors]
        )
        if validation_result.warnings:
            error_message += "\n\nAvertissements:\n" + "\n".join(
                [f"⚠️ {warning}" for warning in validation_result.warnings]
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    leave = leave_crud.create_leave_request(db, request, employee_id)
    
    # Notifier les managers de la nouvelle demande
    notification_crud.notify_leave_to_managers(db=db, leave_request=leave)
    
    # Enrichir la réponse avec les avertissements si présents
    response_data = enrich_leave_response(leave, db)
    if validation_result.warnings:
        response_data["validation_warnings"] = validation_result.warnings
    
    return response_data


# ============================================================
# ENDPOINT 2: Lister les demandes (avec filtres)
# ============================================================
@router.get("/", response_model=LeaveRequestList)
async def list_leave_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[int] = None,
    status: Optional[LeaveStatus] = None,
    leave_type: Optional[LeaveType] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lister les demandes de congés avec filtres et pagination.
    
    - HR/Admin: Voir toutes les demandes
    - Manager: Voir les demandes de son équipe
    - Employee: Voir uniquement ses demandes
    """
    skip = (page - 1) * page_size
    employee_ids_filter = None  # Liste d'IDs pour filtrer (utilisé par manager)
    
    # Filtrage selon le rôle
    if current_user.role == UserRole.employee:
        # Un employé ne voit que ses propres demandes
        if current_user.employee_id:
            employee_id = current_user.employee_id
        else:
            # L'utilisateur n'est pas lié à un employé, retourner liste vide
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    elif current_user.role == UserRole.manager:
        # Un manager voit les demandes des employés dont il est le manager direct
        if current_user.employee_id:
            # Récupérer les IDs des employés gérés par ce manager
            team_employees = db.query(Employee.id).filter(
                Employee.manager_id == current_user.employee_id
            ).all()
            team_ids = [emp.id for emp in team_employees]
            
            if not team_ids:
                # Aucun employé sous ce manager
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0
                }
            
            # Si employee_id est spécifié, vérifier qu'il fait partie de l'équipe
            if employee_id and employee_id not in team_ids:
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0
                }
            # Si pas d'employee_id spécifié, on utilisera team_ids pour filtrer
            if not employee_id:
                employee_ids_filter = team_ids
            else:
                employee_ids_filter = None
        else:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    # Admin, HR Manager, Analyst peuvent voir toutes les demandes
    
    items, total = leave_crud.get_leave_requests(
        db, skip=skip, limit=page_size,
        employee_id=employee_id, 
        employee_ids=employee_ids_filter,  # Filtrer par équipe pour manager
        status=status,
        leave_type=leave_type, year=year
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": [enrich_leave_response(item, db) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


# ============================================================
# ENDPOINT: Règles de validation
# ============================================================
@router.get("/validation-rules")
async def get_validation_rules(
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les critères d'acceptation des demandes de congé.
    
    Retourne les règles de validation configurées.
    """
    return {
        "criteria": [
            {
                "id": 1,
                "name": "Effectif minimum garanti",
                "description": "L'équipe doit avoir assez de personnes présentes",
                "details": f"Minimum {LeaveValidationService.DEFAULT_MIN_TEAM_PRESENCE_COUNT} personnes ou {LeaveValidationService.DEFAULT_MIN_TEAM_PRESENCE_PERCENTAGE}% de l'équipe"
            },
            {
                "id": 2,
                "name": "Pas de chevauchement excessif",
                "description": "Vérification des congés simultanés dans l'équipe",
                "details": "Le système avertit en cas de congés simultanés"
            },
            {
                "id": 3,
                "name": "Délai de prévenance respecté",
                "description": "Demande suffisamment à l'avance",
                "details": f"Congé annuel: {LeaveValidationService.DEFAULT_ADVANCE_NOTICE_DAYS} jours minimum (exceptions: maladie, urgence)"
            },
            {
                "id": 4,
                "name": "Solde de congés suffisant",
                "description": "L'employé a assez de jours disponibles",
                "details": "30 jours annuels par défaut"
            },
            {
                "id": 5,
                "name": "Période non bloquée",
                "description": "Pas de période de clôture ou deadline critique",
                "details": "Clôtures trimestrielles (25-31 mars/juin/sept) et annuelle (20-31 déc)"
            }
        ],
        "config": {
            "min_team_presence_count": LeaveValidationService.DEFAULT_MIN_TEAM_PRESENCE_COUNT,
            "min_team_presence_percentage": LeaveValidationService.DEFAULT_MIN_TEAM_PRESENCE_PERCENTAGE,
            "advance_notice_days": LeaveValidationService.DEFAULT_ADVANCE_NOTICE_DAYS,
            "annual_leave_allowance": 30
        }
    }


# ============================================================
# ENDPOINT: Pré-validation d'une demande
# ============================================================
@router.post("/validate")
async def validate_leave_request_preview(
    request: LeaveRequestCreate,
    employee_id: int = Query(None, description="ID de l'employé (optionnel pour les employés)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pré-valider une demande de congé sans la créer.
    
    Retourne les erreurs et avertissements selon les critères d'acceptation:
    1. Effectif minimum garanti
    2. Pas de chevauchement
    3. Délai de prévenance respecté
    4. Solde de congés suffisant
    5. Période non bloquée
    """
    # Déterminer l'employee_id selon le rôle
    if current_user.role == UserRole.employee:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Votre compte n'est pas lié à un employé"
            )
        employee_id = current_user.employee_id
    elif employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez spécifier l'employé (employee_id)"
        )
    
    # Valider la demande
    validation_service = LeaveValidationService(db)
    validation_result = validation_service.validate_leave_request(
        employee_id=employee_id,
        start_date=request.start_date,
        end_date=request.end_date,
        leave_type=request.leave_type
    )
    
    return validation_service.get_validation_summary(validation_result)


# ============================================================
# ENDPOINT 3: Obtenir une demande par ID
# ============================================================
@router.get("/{request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les détails d'une demande de congé"""
    leave = leave_crud.get_leave_request(db, request_id)
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Un employé ne peut voir que ses propres demandes
    if current_user.role == UserRole.employee:
        if current_user.employee_id != leave.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas accès à cette demande"
            )
    
    return enrich_leave_response(leave, db)


# ============================================================
# ENDPOINT 4: Approuver une demande (HR/Manager)
# ============================================================
@router.post("/{request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
    request_id: int,
    approval: LeaveApproval = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Approuver une demande de congé.
    
    Accessible uniquement aux: Admin, HR Manager, Manager
    """
    leave = leave_crud.approve_leave_request(db, request_id, current_user.id)
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'approuver cette demande (non trouvée ou déjà traitée)"
        )
    
    # Envoyer email de notification à l'employé
    employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
    if employee and employee.email:
        send_leave_approved_email(
            to_email=employee.email,
            employee_name=f"{employee.first_name} {employee.last_name}",
            leave_type=leave.leave_type.value,
            start_date=leave.start_date.strftime("%d/%m/%Y"),
            end_date=leave.end_date.strftime("%d/%m/%Y"),
            approved_by=current_user.full_name
        )
    
    return enrich_leave_response(leave, db)


# ============================================================
# ENDPOINT 5: Rejeter une demande (HR/Manager)
# ============================================================
@router.post("/{request_id}/reject", response_model=LeaveRequestResponse)
async def reject_leave_request(
    request_id: int,
    rejection: LeaveRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Rejeter une demande de congé.
    
    Accessible uniquement aux: Admin, HR Manager, Manager
    """
    leave = leave_crud.reject_leave_request(
        db, request_id, current_user.id, rejection.rejection_reason
    )
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de rejeter cette demande (non trouvée ou déjà traitée)"
        )
    
    # Envoyer email de notification à l'employé
    employee = db.query(Employee).filter(Employee.id == leave.employee_id).first()
    if employee and employee.email:
        send_leave_rejected_email(
            to_email=employee.email,
            employee_name=f"{employee.first_name} {employee.last_name}",
            leave_type=leave.leave_type.value,
            start_date=leave.start_date.strftime("%d/%m/%Y"),
            end_date=leave.end_date.strftime("%d/%m/%Y"),
            rejected_by=current_user.full_name,
            reason=rejection.rejection_reason
        )
    
    return enrich_leave_response(leave, db)


# ============================================================
# ENDPOINT 6: Annuler sa propre demande
# ============================================================
@router.post("/{request_id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave_request(
    request_id: int,
    employee_id: int = Query(None, description="ID de l'employé (optionnel pour employés)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Annuler sa propre demande de congé.
    
    Possible seulement si la demande est pending ou approved.
    - Employé: peut annuler uniquement ses propres demandes
    - HR/Admin: peut annuler n'importe quelle demande
    """
    # Déterminer l'employee_id selon le rôle
    if current_user.role == UserRole.employee:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Votre compte n'est pas lié à un employé"
            )
        employee_id = current_user.employee_id
    elif employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez spécifier l'employé (employee_id)"
        )
    
    leave = leave_crud.cancel_leave_request(db, request_id, employee_id)
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'annuler cette demande"
        )
    
    return enrich_leave_response(leave, db)


# ============================================================
# ENDPOINT 7: Solde de congés d'un employé
# ============================================================
@router.get("/balance/{employee_id}", response_model=LeaveBalance)
async def get_leave_balance(
    employee_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir le solde de congés d'un employé.
    
    - Congés annuels: 25 jours par défaut
    - Affiche les jours utilisés et restants
    - Employé: peut voir uniquement son propre solde
    - HR/Admin: peut voir le solde de tout le monde
    """
    # Un employé ne peut voir que son propre solde
    if current_user.role == UserRole.employee:
        if current_user.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez voir que votre propre solde de congés"
            )
    
    balance = leave_crud.get_employee_leave_balance(db, employee_id, year)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employé non trouvé"
        )
    
    return balance


# ============================================================
# BONUS: Statistiques globales (HR/Admin)
# ============================================================
@router.get("/stats/global", response_model=LeaveStatistics)
async def get_leave_statistics(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """
    Statistiques globales des congés.
    
    Accessible uniquement aux: Admin, HR Manager
    """
    stats = leave_crud.get_leave_statistics(db, year)
    return stats


# ============================================================
# WORKFLOW HIÉRARCHIQUE - Nouveaux endpoints
# ============================================================

@router.post("/{request_id}/manager-approve", response_model=LeaveRequestResponse)
async def manager_approve_leave(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approuver une demande de congé en tant que manager (étape 1).
    
    - Accessible aux: Manager, HR Manager, Admin
    - Change le statut de PENDING → MANAGER_APPROVED
    - Notifie l'employé et les RH
    """
    # Vérifier que l'utilisateur a le rôle manager ou supérieur
    if current_user.role not in [UserRole.manager, UserRole.hr_manager, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les managers peuvent approuver des demandes"
        )
    
    # Récupérer la demande
    leave_request = leave_crud.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Vérifier que la demande est en attente
    if leave_request.status != LeaveStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette demande ne peut pas être approuvée (statut actuel: {leave_request.status.value})"
        )
    
    # Si c'est un manager (pas admin/hr_manager), vérifier qu'il gère cet employé
    if current_user.role == UserRole.manager:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte n'est pas lié à un employé"
            )
        
        # Vérifier que le manager gère cet employé (via manager_id)
        leave_employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
        
        if not leave_employee or leave_employee.manager_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez approuver que les demandes de votre équipe"
            )
    
    # Approuver la demande
    updated_leave = leave_crud.manager_approve_leave_request(db, request_id, current_user.id)
    
    if not updated_leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'approuver cette demande"
        )
    
    # Notifier l'employé
    notification_crud.notify_employee_leave_status(
        db=db,
        leave_request=updated_leave,
        notification_type=NotificationType.leave_manager_approved
    )
    
    # Notifier les RH
    notification_crud.notify_leave_to_hr(db=db, leave_request=updated_leave)
    
    return enrich_leave_response(updated_leave, db)


@router.post("/{request_id}/manager-reject")
async def manager_reject_leave(
    request_id: int,
    rejection: LeaveRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rejeter une demande de congé en tant que manager.
    
    - Accessible aux: Manager, HR Manager, Admin
    - Change le statut de PENDING → REJECTED
    - Notifie l'employé
    """
    # Vérifier que l'utilisateur a le rôle manager ou supérieur
    if current_user.role not in [UserRole.manager, UserRole.hr_manager, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les managers peuvent rejeter des demandes"
        )
    
    # Récupérer la demande
    leave_request = leave_crud.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Vérifier que la demande est en attente
    if leave_request.status != LeaveStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette demande ne peut pas être rejetée (statut actuel: {leave_request.status.value})"
        )
    
    # Si c'est un manager (pas admin/hr_manager), vérifier qu'il gère cet employé
    if current_user.role == UserRole.manager:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte n'est pas lié à un employé"
            )
        
        # Vérifier que le manager gère cet employé (via manager_id)
        leave_employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
        
        if not leave_employee or leave_employee.manager_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez rejeter que les demandes de votre équipe"
            )
    
    # Rejeter la demande
    updated_leave = leave_crud.manager_reject_leave_request(
        db=db,
        request_id=request_id,
        manager_id=current_user.id,
        rejection_reason=rejection.rejection_reason
    )
    
    if not updated_leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de rejeter cette demande"
        )
    
    # Notifier l'employé
    notification_crud.notify_employee_leave_status(
        db=db,
        leave_request=updated_leave,
        notification_type=NotificationType.leave_rejected
    )
    
    return enrich_leave_response(updated_leave, db)


@router.post("/{request_id}/hr-approve", response_model=LeaveRequestResponse)
async def hr_approve_leave(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """
    Approuver une demande de congé en tant que RH (étape finale).
    
    - Accessible aux: HR Manager, Admin
    - Change le statut de MANAGER_APPROVED → HR_APPROVED
    - Notifie l'employé (approbation finale)
    """
    # Récupérer la demande
    leave_request = leave_crud.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Vérifier que la demande a été approuvée par le manager
    if leave_request.status != LeaveStatus.manager_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette demande doit d'abord être approuvée par le manager (statut actuel: {leave_request.status.value})"
        )
    
    # Approuver par RH
    updated_leave = leave_crud.hr_approve_leave_request(db, request_id, current_user.id)
    
    if not updated_leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'approuver cette demande"
        )
    
    # Notifier l'employé (approbation finale)
    notification_crud.notify_employee_leave_status(
        db=db,
        leave_request=updated_leave,
        notification_type=NotificationType.leave_hr_approved
    )
    
    return enrich_leave_response(updated_leave, db)


@router.post("/{request_id}/hr-reject")
async def hr_reject_leave(
    request_id: int,
    rejection: LeaveRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hr)
):
    """
    Rejeter une demande de congé en tant que RH.
    
    - Accessible aux: HR Manager, Admin
    - Change le statut de MANAGER_APPROVED → REJECTED
    - Notifie l'employé
    """
    # Récupérer la demande
    leave_request = leave_crud.get_leave_request(db, request_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Vérifier que la demande a été approuvée par le manager
    if leave_request.status != LeaveStatus.manager_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette demande doit être en attente RH (statut actuel: {leave_request.status.value})"
        )
    
    # Rejeter par RH
    updated_leave = leave_crud.hr_reject_leave_request(
        db=db,
        request_id=request_id,
        hr_user_id=current_user.id,
        rejection_reason=rejection.rejection_reason
    )
    
    if not updated_leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de rejeter cette demande"
        )
    
    # Notifier l'employé
    notification_crud.notify_employee_leave_status(
        db=db,
        leave_request=updated_leave,
        notification_type=NotificationType.leave_rejected
    )
    
    return enrich_leave_response(updated_leave, db)
