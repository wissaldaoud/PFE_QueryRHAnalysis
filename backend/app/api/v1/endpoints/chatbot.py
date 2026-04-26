"""
HR Chatbot endpoints - Chatbot RH intelligent
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.base import get_db
from app.services.chatbot_service import ChatbotService

router = APIRouter()


class ChatMessage(BaseModel):
    question: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    data: Optional[dict] = None
    suggestions: Optional[list] = None


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Poser une question au chatbot RH
    
    Exemples de questions:
    - "Combien d'employés actifs?"
    - "Quel est le turnover?"
    - "Liste des employés du département IT"
    - "Salaire moyen par département"
    """
    try:
        chatbot_service = ChatbotService(db)
        response = await chatbot_service.process_question(
            question=message.question,
            context=message.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chatbot: {str(e)}")


@router.get("/suggestions")
async def get_suggestions():
    """
    Obtenir des suggestions de questions à poser
    """
    return {
        "suggestions": [
            "Combien d'employés actifs avons-nous?",
            "Quel est le taux de turnover?",
            "Affiche les employés du département IT",
            "Quel est le salaire moyen?",
            "Quels employés risquent de partir?",
            "Montre-moi les statistiques par département",
            "Combien de nouveaux employés ce mois?",
            "Liste des managers"
        ]
    }


@router.get("/health")
async def chatbot_health():
    """Check if chatbot service is available"""
    return {"status": "online", "service": "HR Chatbot"}
