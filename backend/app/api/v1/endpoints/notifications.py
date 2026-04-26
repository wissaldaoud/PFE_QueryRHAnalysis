"""
Notification endpoints for admin alerts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.base import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole
from app.api.deps import get_current_user

router = APIRouter()


# Schemas
class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationCountResponse(BaseModel):
    unread_count: int
    total_count: int


class MarkReadRequest(BaseModel):
    notification_ids: List[int]


# === NOTIFICATION ENDPOINTS ===

@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        NotificationResponse(
            id=n.id,
            type=n.type.value if n.type else "system",
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            link=n.link,
            created_at=n.created_at
        )
        for n in notifications
    ]


@router.get("/count", response_model=NotificationCountResponse)
async def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread and total notifications
    """
    total = db.query(Notification).filter(Notification.user_id == current_user.id).count()
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return NotificationCountResponse(unread_count=unread, total_count=total)


@router.post("/mark-read")
async def mark_notifications_read(
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark specific notifications as read
    """
    updated = db.query(Notification).filter(
        Notification.id.in_(request.notification_ids),
        Notification.user_id == current_user.id
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    return {"message": f"{updated} notifications marquées comme lues"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read
    """
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    return {"message": f"{updated} notifications marquées comme lues"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification supprimée"}


# === HELPER FUNCTION ===

def create_notification_for_admins(
    db: Session,
    notification_type: NotificationType,
    title: str,
    message: str,
    link: Optional[str] = None
):
    """
    Create a notification for all admin users
    """
    admins = db.query(User).filter(User.role == UserRole.admin, User.is_active == True).all()
    
    for admin in admins:
        notification = Notification(
            user_id=admin.id,
            type=notification_type,
            title=title,
            message=message,
            link=link
        )
        db.add(notification)
    
    db.commit()
