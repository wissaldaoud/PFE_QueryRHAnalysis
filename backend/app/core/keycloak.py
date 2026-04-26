"""
Keycloak SSO Integration
Enterprise Identity and Access Management (IAM)
Supports: SAML 2.0, OpenID Connect (OIDC), OAuth 2.0
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
import json

from app.core.config import settings


# ============================================
# KEYCLOAK CONFIGURATION
# ============================================

class KeycloakSettings(BaseModel):
    """Keycloak server configuration"""
    server_url: str = "http://localhost:8080"  # Keycloak server URL
    realm: str = "hr-analytics"  # Realm name
    client_id: str = "hr-analytics-app"  # Client ID
    client_secret: str = ""  # Client secret (for confidential clients)
    admin_username: str = "admin"
    admin_password: str = "admin"
    
    @property
    def issuer(self) -> str:
        return f"{self.server_url}/realms/{self.realm}"
    
    @property
    def authorization_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/auth"
    
    @property
    def token_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"
    
    @property
    def userinfo_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
    
    @property
    def logout_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/logout"
    
    @property
    def jwks_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/certs"
    
    @property
    def introspection_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token/introspect"


# Load from environment or use defaults
keycloak_settings = KeycloakSettings(
    server_url=getattr(settings, 'KEYCLOAK_SERVER_URL', 'http://localhost:8080'),
    realm=getattr(settings, 'KEYCLOAK_REALM', 'hr-analytics'),
    client_id=getattr(settings, 'KEYCLOAK_CLIENT_ID', 'hr-analytics-app'),
    client_secret=getattr(settings, 'KEYCLOAK_CLIENT_SECRET', ''),
)


# ============================================
# KEYCLOAK CLIENT
# ============================================

class KeycloakClient:
    """
    Keycloak client for authentication and authorization
    """
    
    def __init__(self, settings: KeycloakSettings):
        self.settings = settings
        self._jwks_cache: Optional[Dict] = None
    
    async def get_jwks(self) -> Dict:
        """Get JSON Web Key Set for token verification"""
        if self._jwks_cache:
            return self._jwks_cache
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.settings.jwks_url)
            if response.status_code == 200:
                self._jwks_cache = response.json()
                return self._jwks_cache
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch Keycloak JWKS"
            )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a Keycloak access token
        """
        try:
            # Get JWKS for verification
            jwks = await self.get_jwks()
            
            # Get the signing key
            unverified_header = jwt.get_unverified_header(token)
            
            rsa_key = {}
            for key in jwks.get("keys", []):
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # Decode and verify token
            # Note: Keycloak doesn't always include audience in access tokens
            # We verify issuer and signature, audience check is optional
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=self.settings.client_id,
                    issuer=self.settings.issuer,
                    options={"verify_aud": False}  # Make audience verification optional
                )
            except JWTError:
                # Try without audience verification
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    issuer=self.settings.issuer,
                    options={"verify_aud": False}
                )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
    
    async def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Introspect token using Keycloak's introspection endpoint
        More secure but requires server call
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.introspection_url,
                data={
                    "token": token,
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("active", False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token is not active"
                    )
                return result
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token introspection failed"
            )
    
    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        
        # Debug logging
        print(f"[Keycloak] Exchange code request:")
        print(f"  - Token URL: {self.settings.token_url}")
        print(f"  - Client ID: {self.settings.client_id}")
        print(f"  - Client Secret: {self.settings.client_secret[:10]}...")
        print(f"  - Redirect URI: {redirect_uri}")
        print(f"  - Code: {code[:20]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            print(f"[Keycloak] Response status: {response.status_code}")
            print(f"[Keycloak] Response: {response.text[:200]}")
            
            if response.status_code == 200:
                return response.json()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code: {response.text}"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.token_url,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "refresh_token": refresh_token,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                return response.json()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user info from Keycloak
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.settings.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info"
            )
    
    def get_authorization_url(self, redirect_uri: str, state: str, scope: str = "openid profile email") -> str:
        """
        Generate authorization URL for login redirect
        """
        params = {
            "client_id": self.settings.client_id,
            "response_type": "code",
            "scope": scope,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.settings.authorization_url}?{query}"
    
    def get_logout_url(self, redirect_uri: str, id_token_hint: Optional[str] = None) -> str:
        """
        Generate logout URL
        """
        params = {
            "client_id": self.settings.client_id,
            "post_logout_redirect_uri": redirect_uri,
        }
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.settings.logout_url}?{query}"


# ============================================
# KEYCLOAK ROLE MAPPING
# ============================================

def map_keycloak_roles_to_app_role(keycloak_roles: list) -> str:
    """
    Map Keycloak realm/client roles to application roles
    """
    # Priority mapping
    role_mapping = {
        "admin": "admin",
        "hr-admin": "admin",
        "hr_manager": "hr_manager",
        "hr-manager": "hr_manager",
        "analyst": "analyst",
        "hr-analyst": "analyst",
        "employee": "employee",
        "user": "employee",
    }
    
    for kc_role in keycloak_roles:
        if kc_role.lower() in role_mapping:
            return role_mapping[kc_role.lower()]
    
    # Default role
    return "employee"


def extract_roles_from_token(token_payload: Dict) -> list:
    """
    Extract roles from Keycloak token
    Keycloak stores roles in different places
    """
    roles = []
    
    # Realm roles
    realm_access = token_payload.get("realm_access", {})
    roles.extend(realm_access.get("roles", []))
    
    # Client-specific roles
    resource_access = token_payload.get("resource_access", {})
    for client_id, access in resource_access.items():
        roles.extend(access.get("roles", []))
    
    return roles


# Global Keycloak client instance
keycloak_client = KeycloakClient(keycloak_settings)
