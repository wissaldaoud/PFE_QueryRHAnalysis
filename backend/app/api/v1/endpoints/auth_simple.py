"""
Endpoint de login simplifié pour contourner le problème d'encodage
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import psycopg2
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_CHANGE_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database config
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "hr_analytics_db")
DB_USER = os.getenv("POSTGRES_USER", "hr_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hr_password123")

class SimpleLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login-simple", response_model=TokenResponse)
async def login_simple(credentials: SimpleLoginRequest):
    """Login endpoint simplifié sans SQLAlchemy"""
    try:
        # Connexion directe à PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            client_encoding="utf8"
        )
        
        cur = conn.cursor()
        
        # Requête utilisateur
        cur.execute(
            "SELECT id, email, hashed_password, is_active, role FROM users WHERE email = %s OR username = %s",
            (credentials.username, credentials.username)
        )
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects"
            )
        
        user_id, email, hashed_password, is_active, role = user
        
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        # Vérifier le mot de passe
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects"
            )
        
        # Créer le token
        access_token = create_access_token(
            data={
                "sub": str(user_id),
                "email": email,
                "role": role or "employee"
            }
        )
        
        return TokenResponse(access_token=access_token)
        
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
