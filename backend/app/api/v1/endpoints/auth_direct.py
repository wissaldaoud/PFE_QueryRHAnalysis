"""
Endpoint de login alternatif qui bypass SQLAlchemy pour debug
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
import bcrypt
from datetime import datetime, timedelta
from app.core.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login-direct", response_model=LoginResponse)
async def login_direct(credentials: LoginRequest):
    """
    Login alternatif qui utilise psycopg2 directement (bypass SQLAlchemy)
    """
    try:
        # Connexion directe psycopg2
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='hr_analytics_db',
            user='hr_user',
            password='hr_password123',
            client_encoding='utf8'
        )
        
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, hashed_password, is_active FROM users WHERE email = %s OR username = %s",
            (credentials.username, credentials.username)
        )
        
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_id, email, hashed_password, is_active = result
        
        if not is_active:
            raise HTTPException(status_code=401, detail="User inactive")
        
        # Vérifier le mot de passe
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Créer le token
        access_token = create_access_token(
            data={"sub": email},
            expires_delta=timedelta(minutes=30)
        )
        
        return LoginResponse(access_token=access_token)
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")
