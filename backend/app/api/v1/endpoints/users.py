"""
User management endpoints for Admin
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.db.base import get_db
from app.models.user import User, UserRole
from app.api.deps import get_current_user, require_admin
from app.core.security import get_password_hash, verify_password
import os
import uuid
from fastapi import UploadFile, File

router = APIRouter()


# Schemas
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.employee


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserActivation(BaseModel):
    is_active: bool


# === PROFILE SCHEMAS ===
class ProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    profile_picture: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    List all users (Admin only)
    """
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Create a new user (Admin only)
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current logged-in user information
    """
    return current_user


# === PROFILE ENDPOINTS ===

@router.get("/profile", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed profile of current user
    """
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        profile_picture=getattr(current_user, 'profile_picture', None),
        created_at=str(current_user.created_at) if current_user.created_at else None
    )


@router.put("/profile", response_model=ProfileResponse)
async def update_my_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    if profile.username:
        # Check if username is taken by another user
        existing = db.query(User).filter(
            User.username == profile.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
        current_user.username = profile.username
    
    if profile.full_name is not None:
        current_user.full_name = profile.full_name
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        profile_picture=getattr(current_user, 'profile_picture', None),
        created_at=str(current_user.created_at) if current_user.created_at else None
    )


@router.post("/profile/change-password")
async def change_password(
    passwords: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password
    """
    # Verify current password
    if not verify_password(passwords.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Validate new password
    if len(passwords.new_password) < 6:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 6 caractères")
    
    # Update password
    current_user.hashed_password = get_password_hash(passwords.new_password)
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}


@router.post("/profile/upload-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload profile picture
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WebP")
    
    # Create uploads directory if not exists
    upload_dir = "uploads/profile_pictures"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update user's profile picture path
    # Note: We'll store the relative path
    picture_url = f"/uploads/profile_pictures/{filename}"
    
    # Add profile_picture column if not exists (we'll handle this gracefully)
    try:
        current_user.profile_picture = picture_url
        db.commit()
    except Exception:
        # If column doesn't exist, just return the URL
        pass
    
    return {"message": "Photo de profil mise à jour", "url": picture_url}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Get user by ID (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Update user information (Admin only)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def toggle_user_activation(
    user_id: int,
    activation: UserActivation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Activate or deactivate a user account (Admin only)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if db_user.id == current_user.id and not activation.is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    db_user.is_active = activation.is_active
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Delete a user account (Admin only)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
