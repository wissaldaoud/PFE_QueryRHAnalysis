"""
Advanced Security Module - Enterprise Grade Security
Features:
- Refresh Tokens with rotation
- 2FA (TOTP) - Google Authenticator compatible
- Token Blacklisting
- Audit Logging
- Session Management
- Rate Limiting
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
import secrets
import pyotp
import qrcode
import io
import base64
from app.db.base import Base


# ============================================
# REFRESH TOKEN MODEL
# ============================================
class RefreshToken(Base):
    """Store refresh tokens for token rotation"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by = Column(String(255), nullable=True)  # For token rotation
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationship
    user = relationship("User", backref="refresh_tokens")


# ============================================
# TOKEN BLACKLIST (For logout / revocation)
# ============================================
class TokenBlacklist(Base):
    """Blacklisted JWT tokens (revoked before expiration)"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # When token would have expired
    reason = Column(String(100), nullable=True)  # logout, password_change, admin_revoke


# ============================================
# 2FA (Two-Factor Authentication)
# ============================================
class UserTwoFactor(Base):
    """Store 2FA secrets for users"""
    __tablename__ = "user_two_factor"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    secret_key = Column(String(32), nullable=False)  # TOTP secret
    is_enabled = Column(Boolean, default=False)
    backup_codes = Column(Text, nullable=True)  # JSON list of backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", backref="two_factor")


# ============================================
# AUDIT LOG (Security Events)
# ============================================
class AuditLog(Base):
    """Track all security-related events"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # login, logout, login_failed, 2fa_enabled, etc.
    event_status = Column(String(20), nullable=False)  # success, failure
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)  # JSON with additional details
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="audit_logs")


# ============================================
# USER SESSIONS
# ============================================
class UserSession(Base):
    """Track active user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token_id = Column(Integer, ForeignKey("refresh_tokens.id"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(String(200), nullable=True)
    location = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship
    user = relationship("User", backref="sessions")


# ============================================
# SECURITY HELPER FUNCTIONS
# ============================================

def generate_refresh_token() -> str:
    """Generate a secure random refresh token"""
    return secrets.token_urlsafe(64)


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return secrets.token_urlsafe(32)


def generate_2fa_secret() -> str:
    """Generate a TOTP secret for 2FA"""
    return pyotp.random_base32()


def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA recovery"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 30 seconds tolerance


def generate_qr_code(secret: str, email: str, issuer: str = "HR Analytics") -> str:
    """Generate QR code for 2FA setup (returns base64 image)"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=email, issuer_name=issuer)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


def get_token_jti() -> str:
    """Generate a unique JWT ID"""
    return secrets.token_urlsafe(16)
