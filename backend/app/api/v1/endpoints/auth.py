"""
Authentication endpoints with OAuth2 SSO Support
Supports: Local login, Microsoft Azure AD, Google OAuth2, SAML
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.base import get_db
from app.models.user import User, UserRole, AccountStatus
from app.models.employee import Employee, EmploymentStatus
from app.core.security import verify_password, create_access_token, get_password_hash
import random
import string
from app.core.oauth import oauth, MICROSOFT_CLIENT_ID, GOOGLE_CLIENT_ID
from app.services.email_service import (
    send_account_pending_email,
    send_account_approved_email,
    send_account_rejected_email,
    send_new_account_notification_to_admin
)

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class SSOProvidersResponse(BaseModel):
    providers: list
    local_login: bool


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str


class RegisterResponse(BaseModel):
    message: str
    status: str


# ============================================
# REGISTRATION (Inscription)
# ============================================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur.
    Le compte sera en attente de validation par un admin.
    """
    from app.models.notification import Notification, NotificationType
    
    # Vérifier si l'email existe déjà
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Vérifier si le username existe déjà
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # Valider le mot de passe
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins 8 caractères"
        )
    
    # Créer l'utilisateur avec statut "pending"
    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=UserRole.employee,
        is_active=True,
        account_status=AccountStatus.pending
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Envoyer email à l'utilisateur (désactivé temporairement pour performance)
    # send_account_pending_email(request.email, request.full_name)
    
    # Notifier les admins (désactivé temporairement pour performance)
    # admins = db.query(User).filter(User.role == UserRole.admin).all()
    # for admin in admins:
    #     send_new_account_notification_to_admin(admin.email, request.full_name, request.email)
    #     notification = Notification(
    #         user_id=admin.id,
    #         type=NotificationType.new_account,
    #         title="Nouvelle demande de compte",
    #         message=f"{request.full_name} ({request.email}) demande un compte",
    #         link="/admin/accounts"
    #     )
    #     db.add(notification)
    # db.commit()
    
    return {
        "message": "Inscription réussie ! Votre compte est en attente de validation par un administrateur.",
        "status": "pending"
    }


# ============================================
# LOCAL AUTHENTICATION
# ============================================

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login (local authentication)
    """
    try:
        # Chercher l'utilisateur par email ou username
        user = db.query(User).filter(
            (User.email == form_data.username) | (User.username == form_data.username)
        ).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except UnicodeDecodeError as e:
        # Erreur d'encodage spécifique
        import traceback
        error_details = traceback.format_exc()
        print(f"[ENCODAGE ERROR] {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database encoding error. Please check PostgreSQL configuration. Error: {str(e)}"
        )
    except Exception as e:
        # Autres erreurs
        import traceback
        error_details = traceback.format_exc()
        print(f"[LOGIN ERROR] {error_details}")
        raise
    
    # Vérifier le statut du compte
    if hasattr(user, 'account_status') and user.account_status:
        if user.account_status == AccountStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre compte est en attente de validation par un administrateur"
            )
        elif user.account_status == AccountStatus.rejected:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre demande de compte a été refusée"
            )
    
    # Créer le token JWT
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Successfully logged out"}


# ============================================
# SSO PROVIDERS INFO
# ============================================

@router.get("/sso/providers", response_model=SSOProvidersResponse)
async def get_sso_providers():
    """
    Get available SSO providers
    """
    providers = []
    
    if MICROSOFT_CLIENT_ID:
        providers.append({
            "name": "microsoft",
            "display_name": "Microsoft (Azure AD)",
            "login_url": "/api/v1/auth/sso/microsoft",
            "icon": "microsoft"
        })
    
    if GOOGLE_CLIENT_ID:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "login_url": "/api/v1/auth/sso/google",
            "icon": "google"
        })
    
    return {
        "providers": providers,
        "local_login": True
    }


# ============================================
# MICROSOFT AZURE AD SSO
# ============================================

@router.get("/sso/microsoft")
async def login_microsoft(request: Request):
    """
    Initiate Microsoft Azure AD SSO login
    """
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft SSO not configured"
        )
    
    redirect_uri = str(request.url_for('auth_microsoft_callback'))
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@router.get("/callback/microsoft")
async def auth_microsoft_callback(request: Request, db: Session = Depends(get_db)):
    """
    Microsoft Azure AD callback - creates/updates user and returns JWT
    """
    if not MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Microsoft SSO not configured")
    
    try:
        token = await oauth.microsoft.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Extract user data from Microsoft
        email = user_info.get('email') or user_info.get('preferred_username')
        name = user_info.get('name', '')
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user from SSO
            user = User(
                email=email,
                username=email.split('@')[0],
                full_name=name,
                hashed_password=get_password_hash("sso_user_no_password"),
                role=UserRole.employee,  # Default role for SSO users
                is_active=True,
                sso_provider="microsoft"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
        
        # Redirect to frontend with token (adjust URL for your frontend)
        frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SSO Error: {str(e)}")


# ============================================
# GOOGLE SSO
# ============================================

@router.get("/sso/google")
async def login_google(request: Request):
    """
    Initiate Google OAuth2 SSO login
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google SSO not configured"
        )
    
    redirect_uri = str(request.url_for('auth_google_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback/google")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Google OAuth2 callback - creates/updates user and returns JWT
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google SSO not configured")
    
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Extract user data from Google
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user from SSO
            user = User(
                email=email,
                username=email.split('@')[0],
                full_name=name,
                hashed_password=get_password_hash("sso_user_no_password"),
                role=UserRole.employee,  # Default role for SSO users
                is_active=True,
                sso_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SSO Error: {str(e)}")


# ============================================
# ADMIN: GESTION DES COMPTES EN ATTENTE
# ============================================

class ApproveAccountRequest(BaseModel):
    user_id: int
    role: Optional[str] = "employee"  # employee, manager, hr_manager


class RejectAccountRequest(BaseModel):
    user_id: int
    reason: Optional[str] = None


@router.get("/pending-accounts")
async def get_pending_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Will be replaced with proper auth
):
    """
    Récupérer la liste des comptes en attente de validation (Admin/HR only)
    """
    from app.api.deps import get_current_user, require_admin
    
    # Get token from request
    from fastapi import Request
    
    pending = db.query(User).filter(User.account_status == AccountStatus.pending).all()
    
    return {
        "items": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in pending
        ],
        "total": len(pending)
    }


@router.post("/approve-account")
async def approve_account(
    request: ApproveAccountRequest,
    db: Session = Depends(get_db)
):
    """
    Approuver un compte en attente (Admin/HR only)
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.account_status != AccountStatus.pending:
        raise HTTPException(status_code=400, detail="Ce compte n'est pas en attente de validation")
    
    # Définir le rôle choisi par l'admin
    role_mapping = {
        "employee": UserRole.employee,
        "manager": UserRole.manager,
        "hr_manager": UserRole.hr_manager,
        "analyst": UserRole.analyst
    }
    
    if request.role and request.role in role_mapping:
        user.role = role_mapping[request.role]
    
    user.account_status = AccountStatus.approved
    user.verified_at = datetime.utcnow()
    
    # === AUTO-CRÉATION DE L'EMPLOYÉ ===
    # Vérifier si un Employee existe déjà pour cet email
    existing_employee = db.query(Employee).filter(Employee.email == user.email).first()
    
    if not existing_employee:
        # Générer un code employé unique
        def generate_employee_code():
            while True:
                code = "EMP-" + ''.join(random.choices(string.digits, k=5))
                if not db.query(Employee).filter(Employee.employee_code == code).first():
                    return code
        
        # Parser le nom complet
        name_parts = user.full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else "Inconnu"
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Créer l'Employee
        new_employee = Employee(
            employee_code=generate_employee_code(),
            first_name=first_name,
            last_name=last_name,
            email=user.email,
            hire_date=datetime.utcnow().date(),
            employment_status=EmploymentStatus.active,
            job_title="À définir",
            department_id=None,  # L'admin peut le définir plus tard
            manager_id=None,     # L'admin peut le définir plus tard
            salary=None  # L'admin peut le définir plus tard
        )
        db.add(new_employee)
        db.flush()  # Obtenir l'ID de l'employé
        
        # Lier le User à l'Employee
        user.employee_id = new_employee.id
    else:
        # Si l'Employee existe déjà, lier le User
        user.employee_id = existing_employee.id
    
    db.commit()
    db.refresh(user)
    
    # Envoyer email de confirmation avec le rôle
    role_labels = {
        UserRole.employee: "Employé",
        UserRole.manager: "Manager",
        UserRole.hr_manager: "Responsable RH",
        UserRole.analyst: "Analyste"
    }
    role_label = role_labels.get(user.role, "Employé")
    
    # Envoi email désactivé temporairement pour performance
    # send_account_approved_email(user.email, user.full_name)
    
    return {
        "message": f"Compte de {user.full_name} approuvé avec succès",
        "role": user.role.value,
        "role_label": role_label
    }


@router.post("/reject-account")
async def reject_account(
    request: RejectAccountRequest,
    db: Session = Depends(get_db)
):
    """
    Rejeter un compte en attente (Admin/HR only)
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.account_status != AccountStatus.pending:
        raise HTTPException(status_code=400, detail="Ce compte n'est pas en attente de validation")
    
    user.account_status = AccountStatus.rejected
    user.rejection_reason = request.reason
    user.verified_at = datetime.utcnow()
    db.commit()
    
    # Envoyer email de refus (désactivé temporairement pour performance)
    # send_account_rejected_email(user.email, user.full_name, request.reason or "")
    
    return {"message": f"Compte de {user.full_name} refusé"}

