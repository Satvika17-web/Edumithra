from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend import models
from backend.auth import get_current_user

router = APIRouter()

@router.post("/")
def update_progress(
    topic: str,
    completion_percentage: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    today_str = str(date.today())
    if user.last_active_date != today_str:
        if user.last_active_date is None:
            user.streak_count = 1
        else:
            last_date = date.fromisoformat(user.last_active_date)
            delta_days = (date.today() - last_date).days
            if delta_days == 1:
                user.streak_count += 1
            elif delta_days > 1:
                user.streak_count = 1
        user.last_active_date = today_str

    progress_item = db.query(models.Progress).filter(
        models.Progress.user_id == user.id,
        models.Progress.topic == topic
    ).first()
    
    if progress_item:
        progress_item.completion_percentage = completion_percentage
    else:
        progress_item = models.Progress(
            user_id=user.id,
            topic=topic,
            completion_percentage=completion_percentage
        )
        db.add(progress_item)
        
    db.commit()
    db.refresh(user)
    db.refresh(progress_item)
    return {
        "message": "Progress and streak updated successfully", 
        "progress": progress_item, 
        "current_streak": user.streak_count
    }

@router.get("/dashboard")
def get_progress_dashboard(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress_list = db.query(models.Progress).filter(models.Progress.user_id == user.id).all()
    quizzes = db.query(models.Quiz).filter(models.Quiz.user_id == user.id).all()
    
    total_topics = len(progress_list)
    avg_completion = sum(p.completion_percentage for p in progress_list) / total_topics if total_topics > 0 else 0
    
    return {
        "learner_name": user.name,
        "learning_streak": user.streak_count,
        "last_active_date": user.last_active_date,
        "overall_completion_percentage": round(avg_completion, 2),
        "tracked_modules_count": total_topics,
        "modules_progress": progress_list,
        "quiz_results": quizzes
    }

@router.post("/achievements")
def create_achievement(
    title: str,
    description: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievement = models.Achievement(title=title, description=description, user_id=user.id)
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement

@router.get("/achievements")
def get_achievements(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.achievements