from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.auth import get_current_user

router = APIRouter()

@router.post("/")
def record_quiz(
    title: str,
    score: int,
    result_status: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    quiz_record = models.Quiz(
        title=title,
        score=score,
        result_status=result_status,
        user_id=user.id
    )
    db.add(quiz_record)
    db.commit()
    db.refresh(quiz_record)
    return quiz_record