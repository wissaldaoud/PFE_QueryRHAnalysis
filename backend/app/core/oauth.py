"""
OAuth2/SAML SSO Configuration for Enterprise Authentication
Supports: Microsoft Azure AD, Google, and SAML providers
"""
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from typing import Optional
import os

# OAuth2 Configuration
oauth = OAuth()

# ============================================
# MICROSOFT AZURE AD (Recommended for SOPRAHR)
# ============================================
# To configure:
# 1. Go to Azure Portal > Azure Active Directory > App registrations
# 2. Create a new application
# 3. Add redirect URI: http://localhost:8000/api/v1/auth/callback/microsoft
# 4. Copy Application (client) ID and create a Client Secret
# 5. Set environment variables below

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")  # or your tenant ID

if MICROSOFT_CLIENT_ID:
    oauth.register(
        name='microsoft',
        client_id=MICROSOFT_CLIENT_ID,
        client_secret=MICROSOFT_CLIENT_SECRET,
        server_metadata_url=f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile User.Read'
        }
    )

# ============================================
# GOOGLE OAUTH2
# ============================================
# To configure:
# 1. Go to Google Cloud Console > APIs & Services > Credentials
# 2. Create OAuth 2.0 Client ID
# 3. Add redirect URI: http://localhost:8000/api/v1/auth/callback/google
# 4. Set environment variables below

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

if GOOGLE_CLIENT_ID:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# ============================================
# SAML CONFIGURATION (For enterprise SSO)
# ============================================
SAML_ENABLED = os.getenv("SAML_ENABLED", "false").lower() == "true"
SAML_IDP_METADATA_URL = os.getenv("SAML_IDP_METADATA_URL", "")
SAML_SP_ENTITY_ID = os.getenv("SAML_SP_ENTITY_ID", "hr-analytics-online")
SAML_ACS_URL = os.getenv("SAML_ACS_URL", "http://localhost:8000/api/v1/auth/saml/acs")

# SAML Settings Dictionary (for python3-saml)
def get_saml_settings() -> dict:
    """Get SAML settings for python3-saml library"""
    return {
        "strict": True,
        "debug": False,
        "sp": {
            "entityId": SAML_SP_ENTITY_ID,
            "assertionConsumerService": {
                "url": SAML_ACS_URL,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{SAML_ACS_URL}/logout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        },
        "idp": {
            "entityId": "",  # Set from metadata
            "singleSignOnService": {
                "url": "",  # Set from metadata
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "singleLogoutService": {
                "url": "",  # Set from metadata
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": ""  # Set from metadata
        }
    }
