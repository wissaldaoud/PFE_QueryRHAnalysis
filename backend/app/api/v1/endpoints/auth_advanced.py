"""
Advanced Authentication Endpoints
Features: Refresh tokens, 2FA, Session management, Audit logging
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import json

from app.db.base import get_db
from app.models.user import User, UserRole
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.advanced_security import (
    RefreshToken, TokenBlacklist, UserTwoFactor, AuditLog, UserSession,
    generate_refresh_token, generate_session_id, generate_2fa_secret,
    generate_backup_codes, verify_totp, generate_qr_code, get_token_jti
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None  # For 2FA


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 encoded QR code
    backup_codes: List[str]


class Verify2FARequest(BaseModel):
    code: str


class SessionInfo(BaseModel):
    session_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[str]
    created_at: datetime
    last_activity: datetime
    is_current: bool


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_audit_log(
    db: Session,
    user_id: Optional[int],
    event_type: str,
    event_status: str,
    request: Request,
    details: Optional[dict] = None
):
    """Create an audit log entry"""
    audit = AuditLog(
        user_id=user_id,
        event_type=event_type,
        event_status=event_status,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        details=json.dumps(details) if details else None
    )
    db.add(audit)
    db.commit()


def create_user_session(
    db: Session,
    user_id: int,
    refresh_token_id: int,
    request: Request
) -> UserSession:
    """Create a new user session"""
    session = UserSession(
        session_id=generate_session_id(),
        user_id=user_id,
        refresh_token_id=refresh_token_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        device_info=parse_device_info(request.headers.get("user-agent")),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def parse_device_info(user_agent: Optional[str]) -> str:
    """Parse user agent to get device info"""
    if not user_agent:
        return "Unknown"
    
    if "Windows" in user_agent:
        return "Windows PC"
    elif "Macintosh" in user_agent:
        return "Mac"
    elif "iPhone" in user_agent:
        return "iPhone"
    elif "Android" in user_agent:
        return "Android"
    elif "Linux" in user_agent:
        return "Linux"
    else:
        return "Unknown Device"


# ============================================
# ADVANCED LOGIN (with 2FA support)
# ============================================

@router.post("/login/secure", response_model=TokenResponse)
async def secure_login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Secure login with optional 2FA support
    """
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        create_audit_log(db, None, "login", "failure", request, {"email": login_data.email, "reason": "invalid_credentials"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        create_audit_log(db, user.id, "login", "failure", request, {"reason": "account_inactive"})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Check 2FA
    two_factor = db.query(UserTwoFactor).filter(
        UserTwoFactor.user_id == user.id,
        UserTwoFactor.is_enabled == True
    ).first()
    
    if two_factor:
        if not login_data.totp_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="2FA code required",
                headers={"X-2FA-Required": "true"}
            )
        
        if not verify_totp(two_factor.secret_key, login_data.totp_code):
            create_audit_log(db, user.id, "login", "failure", request, {"reason": "invalid_2fa_code"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
        
        # Update 2FA last used
        two_factor.last_used_at = datetime.utcnow()
    
    # Generate tokens
    jti = get_token_jti()
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "jti": jti}
    )
    
    # Create refresh token
    refresh_token_str = generate_refresh_token()
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    
    # Create session
    create_user_session(db, user.id, refresh_token.id, request)
    
    # Audit log
    create_audit_log(db, user.id, "login", "success", request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "has_2fa": two_factor is not None
        }
    }


# ============================================
# REFRESH TOKEN
# ============================================

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
    data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token (with rotation)
    """
    # Find refresh token
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.revoked == False
    ).first()
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    if refresh_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Token rotation: revoke old token and create new one
    refresh_token.revoked = True
    refresh_token.revoked_at = datetime.utcnow()
    
    new_refresh_token_str = generate_refresh_token()
    new_refresh_token = RefreshToken(
        token=new_refresh_token_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    refresh_token.replaced_by = new_refresh_token_str
    
    db.add(new_refresh_token)
    db.commit()
    
    # Generate new access token
    jti = get_token_jti()
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "jti": jti}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_str,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value
        }
    }


# ============================================
# SECURE LOGOUT (Blacklist token)
# ============================================

@router.post("/logout/secure")
async def secure_logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Secure logout - blacklist all tokens and end all sessions
    """
    # Revoke all refresh tokens for this user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True, "revoked_at": datetime.utcnow()})
    
    # Deactivate all sessions
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    # Audit log
    create_audit_log(db, current_user.id, "logout", "success", request)
    
    return {"message": "Successfully logged out from all devices"}


# ============================================
# 2FA SETUP
# ============================================

@router.post("/2fa/setup", response_model=Enable2FAResponse)
async def setup_2fa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Setup 2FA for current user - returns QR code and backup codes
    """
    # Check if already enabled
    existing = db.query(UserTwoFactor).filter(
        UserTwoFactor.user_id == current_user.id
    ).first()
    
    if existing and existing.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Generate secret and backup codes
    secret = generate_2fa_secret()
    backup_codes = generate_backup_codes()
    qr_code = generate_qr_code(secret, current_user.email)
    
    # Save (but not enabled yet)
    if existing:
        existing.secret_key = secret
        existing.backup_codes = json.dumps(backup_codes)
        existing.is_enabled = False
    else:
        two_factor = UserTwoFactor(
            user_id=current_user.id,
            secret_key=secret,
            backup_codes=json.dumps(backup_codes),
            is_enabled=False
        )
        db.add(two_factor)
    
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "backup_codes": backup_codes
    }


@router.post("/2fa/verify")
async def verify_and_enable_2fa(
    data: Verify2FARequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify TOTP code and enable 2FA
    """
    two_factor = db.query(UserTwoFactor).filter(
        UserTwoFactor.user_id == current_user.id
    ).first()
    
    if not two_factor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not setup. Call /2fa/setup first"
        )
    
    if not verify_totp(two_factor.secret_key, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    two_factor.is_enabled = True
    two_factor.last_used_at = datetime.utcnow()
    db.commit()
    
    create_audit_log(db, current_user.id, "2fa_enabled", "success", request)
    
    return {"message": "2FA enabled successfully"}


@router.delete("/2fa/disable")
async def disable_2fa(
    data: Verify2FARequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Disable 2FA (requires current TOTP code)
    """
    two_factor = db.query(UserTwoFactor).filter(
        UserTwoFactor.user_id == current_user.id,
        UserTwoFactor.is_enabled == True
    ).first()
    
    if not two_factor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    if not verify_totp(two_factor.secret_key, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    db.delete(two_factor)
    db.commit()
    
    create_audit_log(db, current_user.id, "2fa_disabled", "success", request)
    
    return {"message": "2FA disabled successfully"}


# ============================================
# SESSION MANAGEMENT
# ============================================

@router.get("/sessions", response_model=List[SessionInfo])
async def get_active_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active sessions for current user
    """
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).order_by(UserSession.last_activity.desc()).all()
    
    current_ip = request.client.host if request.client else None
    current_ua = request.headers.get("user-agent")
    
    return [
        SessionInfo(
            session_id=s.session_id,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            device_info=s.device_info,
            created_at=s.created_at,
            last_activity=s.last_activity,
            is_current=(s.ip_address == current_ip and s.user_agent == current_ua)
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a specific session
    """
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    
    # Also revoke associated refresh token
    if session.refresh_token_id:
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.id == session.refresh_token_id
        ).first()
        if refresh_token:
            refresh_token.revoked = True
            refresh_token.revoked_at = datetime.utcnow()
    
    db.commit()
    
    create_audit_log(db, current_user.id, "session_revoked", "success", request, {"session_id": session_id})
    
    return {"message": "Session revoked successfully"}


# ============================================
# AUDIT LOGS (Admin only)
# ============================================

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs (Admin only)
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = db.query(AuditLog)
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "event_type": log.event_type,
            "event_status": log.event_status,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "details": json.loads(log.details) if log.details else None,
            "created_at": log.created_at
        }
        for log in logs
    ]
