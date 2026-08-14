from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend import models
from backend.auth import get_current_user
from backend.groq_service import generate_ai_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/ask")
def ask_ai_tutor(
    payload: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Construct a tutor persona prompt for context-aware learning support
    tutor_prompt = (
        f"You are Edumithra AI Tutor, an expert, encouraging, and intelligent 24/7 learning assistant. "
        f"Provide clear concept explanations, answer questions accurately, offer study guidance, "
        f"and assist with technical problem-solving. "
        f"Student query: {payload.message}"
    )
    
    ai_response = generate_ai_response(tutor_prompt)
    
    return {
        "user_query": payload.message,
        "tutor_response": ai_response,
        "status": "success"
    }

@router.get("/test")
def test_chatbot():
    test_prompt = "Explain the core concept of asynchronous programming in Python in simple terms."
    response = generate_ai_response(test_prompt)
    return {
        "capability": "AI Tutor Concept Explanation Test",
        "response": response
    }