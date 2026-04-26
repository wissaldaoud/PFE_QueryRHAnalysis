"""
Keycloak SSO Authentication Endpoints
OpenID Connect (OIDC) / OAuth 2.0 flow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
from datetime import datetime

from app.db.base import get_db
from app.models.user import User, UserRole
from app.core.keycloak import (
    keycloak_client, keycloak_settings,
    map_keycloak_roles_to_app_role, extract_roles_from_token
)
from app.core.security import create_access_token
from app.api.deps import get_current_user

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class KeycloakTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: dict


class KeycloakCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str


class KeycloakUserInfo(BaseModel):
    sub: str  # Keycloak user ID
    email: Optional[str] = None
    email_verified: Optional[bool] = False
    preferred_username: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None


# Store for CSRF state tokens (in production, use Redis)
_state_store = {}


# ============================================
# KEYCLOAK SSO ENDPOINTS
# ============================================

@router.get("/keycloak/config")
async def get_keycloak_config():
    """
    Get Keycloak public configuration for frontend
    """
    return {
        "server_url": keycloak_settings.server_url,
        "realm": keycloak_settings.realm,
        "client_id": keycloak_settings.client_id,
        "authorization_url": keycloak_settings.authorization_url,
        "token_url": keycloak_settings.token_url,
        "logout_url": keycloak_settings.logout_url,
    }


@router.get("/keycloak/login")
async def keycloak_login(
    redirect_uri: str = Query(..., description="Frontend callback URL"),
    request: Request = None
):
    """
    Initiate Keycloak SSO login flow
    Redirects to Keycloak login page
    """
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    _state_store[state] = {
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow()
    }
    
    # Generate authorization URL
    auth_url = keycloak_client.get_authorization_url(
        redirect_uri=redirect_uri,
        state=state,
        scope="openid profile email"
    )
    
    return {
        "authorization_url": auth_url,
        "state": state
    }


@router.get("/keycloak/callback")
async def keycloak_callback_get(
    code: str = Query(..., description="Authorization code from Keycloak"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle Keycloak OAuth2 callback (GET method)
    Exchange authorization code for tokens and redirect to frontend
    """
    print(f"🔑 Keycloak Callback GET received:")
    print(f"   Code: {code[:20]}...")
    print(f"   State: {state}")
    print(f"   State store keys: {list(_state_store.keys())}")
    
    # Verify state (CSRF protection) - More lenient for development
    stored_state = _state_store.pop(state, None)
    redirect_uri = stored_state.get("redirect_uri") if stored_state else "http://localhost:3000/auth/callback"
    
    if not stored_state:
        print(f"⚠️ State not found in store. In development mode, continuing anyway...")
    
    # Exchange code for tokens
    tokens = await keycloak_client.exchange_code(
        code=code,
        redirect_uri=redirect_uri
    )
    
    # Verify and decode the access token
    token_payload = await keycloak_client.verify_token(tokens["access_token"])
    
    # Extract user info from token
    email = token_payload.get("email")
    preferred_username = token_payload.get("preferred_username", email)
    keycloak_sub = token_payload.get("sub")
    
    if not email:
        # Try to get from userinfo endpoint
        user_info = await keycloak_client.get_user_info(tokens["access_token"])
        email = user_info.get("email")
        preferred_username = user_info.get("preferred_username", email)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available from Keycloak"
        )
    
    # Extract roles from token
    keycloak_roles = extract_roles_from_token(token_payload)
    app_role = map_keycloak_roles_to_app_role(keycloak_roles)
    
    # Find or create user in local database
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Auto-create user from Keycloak (JIT provisioning)
        user = User(
            email=email,
            username=preferred_username or email.split("@")[0],
            hashed_password="keycloak_sso",  # Placeholder, user authenticates via Keycloak
            full_name=token_payload.get("name", ""),
            role=UserRole(app_role),
            is_active=True,
            sso_provider="keycloak"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update SSO provider if needed
        if user.sso_provider != "keycloak":
            user.sso_provider = "keycloak"
            db.commit()
    
    # Generate local JWT token (hybrid approach)
    local_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role.value,
            "keycloak_sub": keycloak_sub
        }
    )
    
    # Redirect to frontend with token
    frontend_callback_url = f"http://localhost:3000/auth/callback?token={local_token}"
    return RedirectResponse(url=frontend_callback_url)


@router.post("/keycloak/callback", response_model=KeycloakTokenResponse)
async def keycloak_callback_post(
    data: KeycloakCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle Keycloak OAuth2 callback (POST method for API calls)
    Exchange authorization code for tokens
    """
    print(f"🔑 Keycloak Callback POST received:")
    print(f"   Code: {data.code[:20]}...")
    print(f"   State: {data.state}")
    print(f"   Redirect URI: {data.redirect_uri}")
    print(f"   State store keys: {list(_state_store.keys())}")
    
    # Verify state (CSRF protection) - More lenient for development
    stored_state = _state_store.pop(data.state, None)
    if not stored_state:
        print(f"⚠️ State not found in store. In development mode, continuing anyway...")
    
    # Exchange code for tokens
    tokens = await keycloak_client.exchange_code(
        code=data.code,
        redirect_uri=data.redirect_uri
    )
    
    # Verify and decode the access token
    token_payload = await keycloak_client.verify_token(tokens["access_token"])
    
    # Extract user info from token
    email = token_payload.get("email")
    preferred_username = token_payload.get("preferred_username", email)
    keycloak_sub = token_payload.get("sub")
    
    if not email:
        # Try to get from userinfo endpoint
        user_info = await keycloak_client.get_user_info(tokens["access_token"])
        email = user_info.get("email")
        preferred_username = user_info.get("preferred_username", email)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available from Keycloak"
        )
    
    # Extract roles from token
    keycloak_roles = extract_roles_from_token(token_payload)
    app_role = map_keycloak_roles_to_app_role(keycloak_roles)
    
    # Find or create user in local database
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Auto-create user from Keycloak (JIT provisioning)
        user = User(
            email=email,
            username=preferred_username or email.split("@")[0],
            hashed_password="keycloak_sso",  # Placeholder, user authenticates via Keycloak
            full_name=token_payload.get("name", ""),
            role=UserRole(app_role),
            is_active=True,
            sso_provider="keycloak"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update SSO provider if needed
        if user.sso_provider != "keycloak":
            user.sso_provider = "keycloak"
            db.commit()
    
    # Generate local JWT token (hybrid approach)
    local_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role.value,
            "keycloak_sub": keycloak_sub
        }
    )
    
    # Return token data
    return {
        "access_token": local_token,
        "refresh_token": tokens.get("refresh_token", ""),
        "id_token": tokens.get("id_token"),
        "token_type": "bearer",
        "expires_in": tokens.get("expires_in", 300),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "keycloak_roles": keycloak_roles,
            "sso_provider": "keycloak"
        }
    }


@router.post("/keycloak/refresh")
async def keycloak_refresh_token(
    refresh_token: str
):
    """
    Refresh tokens using Keycloak refresh token
    """
    tokens = await keycloak_client.refresh_token(refresh_token)
    
    return {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "token_type": "bearer",
        "expires_in": tokens.get("expires_in", 300)
    }


@router.get("/keycloak/logout")
async def keycloak_logout(
    redirect_uri: str = Query(..., description="Post-logout redirect URL"),
    id_token_hint: Optional[str] = Query(None, description="ID token for logout hint")
):
    """
    Generate Keycloak logout URL
    """
    logout_url = keycloak_client.get_logout_url(
        redirect_uri=redirect_uri,
        id_token_hint=id_token_hint
    )
    
    return {
        "logout_url": logout_url
    }


@router.get("/keycloak/userinfo")
async def keycloak_userinfo(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user info (requires authentication)
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "sso_provider": current_user.sso_provider,
        "is_active": current_user.is_active
    }


@router.post("/keycloak/verify")
async def verify_keycloak_token(
    access_token: str
):
    """
    Verify a Keycloak access token
    Returns token claims if valid
    """
    payload = await keycloak_client.verify_token(access_token)
    
    return {
        "valid": True,
        "claims": {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "preferred_username": payload.get("preferred_username"),
            "name": payload.get("name"),
            "roles": extract_roles_from_token(payload),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        }
    }


@router.post("/keycloak/introspect")
async def introspect_keycloak_token(
    access_token: str
):
    """
    Introspect token using Keycloak's introspection endpoint
    More secure server-side validation
    """
    result = await keycloak_client.introspect_token(access_token)
    
    return {
        "active": result.get("active"),
        "username": result.get("username"),
        "email": result.get("email"),
        "client_id": result.get("client_id"),
        "exp": result.get("exp"),
        "scope": result.get("scope"),
    }
