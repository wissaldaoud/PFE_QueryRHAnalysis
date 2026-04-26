"""
CRUD operations for Notifications
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from typing import Optional


def create_notification(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    link: Optional[str] = None
) -> Notification:
    """Créer une nouvelle notification"""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        link=link
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_leave_notification(
    db: Session,
    leave_request: LeaveRequest,
    notification_type: NotificationType,
    recipient_user_id: int
):
    """Créer une notification pour un changement de statut de congé"""
    
    # Récupérer l'employé pour avoir son nom
    employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Un employé"
    
    # Construire le message selon le type
    titles = {
        NotificationType.leave_request: "Nouvelle demande de congé",
        NotificationType.leave_manager_approved: "Congé approuvé par le manager",
        NotificationType.leave_hr_approved: "Congé approuvé (final)",
        NotificationType.leave_rejected: "Demande de congé refusée"
    }
    
    messages = {
        NotificationType.leave_request: f"{employee_name} a soumis une demande de congé du {leave_request.start_date} au {leave_request.end_date} ({leave_request.days_requested} jours)",
        NotificationType.leave_manager_approved: f"Votre congé du {leave_request.start_date} au {leave_request.end_date} a été approuvé par votre manager. En attente de validation RH.",
        NotificationType.leave_hr_approved: f"Votre congé du {leave_request.start_date} au {leave_request.end_date} a été approuvé par les RH. ✅",
        NotificationType.leave_rejected: f"Votre demande de congé du {leave_request.start_date} au {leave_request.end_date} a été refusée."
    }
    
    title = titles.get(notification_type, "Notification de congé")
    message = messages.get(notification_type, "Mise à jour de statut de congé")
    
    if leave_request.rejection_reason and notification_type == NotificationType.leave_rejected:
        message += f" Raison: {leave_request.rejection_reason}"
    
    return create_notification(
        db=db,
        user_id=recipient_user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        link=f"/leaves/{leave_request.id}"
    )


def notify_leave_to_managers(
    db: Session,
    leave_request: LeaveRequest
):
    """Notifier les managers d'une nouvelle demande de congé"""
    
    # Récupérer l'employé
    employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
    if not employee or not employee.department_id:
        return
    
    # Trouver les managers du même département
    managers_in_dept = db.query(User).join(Employee).filter(
        Employee.department_id == employee.department_id,
        User.role.in_(['manager', 'hr_manager'])
    ).all()
    
    # Créer une notification pour chaque manager
    for manager in managers_in_dept:
        create_leave_notification(
            db=db,
            leave_request=leave_request,
            notification_type=NotificationType.leave_request,
            recipient_user_id=manager.id
        )


def notify_leave_to_hr(
    db: Session,
    leave_request: LeaveRequest
):
    """Notifier les RH qu'une demande a été approuvée par le manager"""
    
    # Trouver tous les utilisateurs RH
    hr_users = db.query(User).filter(
        User.role.in_(['hr_manager', 'admin'])
    ).all()
    
    employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
    employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Un employé"
    
    # Créer une notification pour chaque RH
    for hr_user in hr_users:
        create_notification(
            db=db,
            user_id=hr_user.id,
            notification_type=NotificationType.leave_request,
            title="Demande de congé à valider",
            message=f"{employee_name} - Congé approuvé par le manager. En attente de validation RH ({leave_request.start_date} au {leave_request.end_date}, {leave_request.days_requested} jours)",
            link=f"/leaves/{leave_request.id}"
        )


def notify_employee_leave_status(
    db: Session,
    leave_request: LeaveRequest,
    notification_type: NotificationType
):
    """Notifier l'employé d'un changement de statut de son congé"""
    
    # Récupérer l'employé et son compte user
    employee = db.query(Employee).filter(Employee.id == leave_request.employee_id).first()
    if not employee:
        return
    
    user = db.query(User).filter(User.employee_id == employee.id).first()
    if not user:
        return
    
    create_leave_notification(
        db=db,
        leave_request=leave_request,
        notification_type=notification_type,
        recipient_user_id=user.id
    )
