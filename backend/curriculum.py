from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.auth import get_current_user
from backend.groq_service import generate_ai_response

router = APIRouter()

@router.post("/generate-roadmap")
def generate_roadmap(
    career_path: str,
    skill_level: str,
    study_time: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt = (
        f"Create a comprehensive, structured learning roadmap for a {skill_level} level student "
        f"pursuing a career in {career_path}, with an available study time of {study_time}. "
        f"The AI-generated curriculum MUST include: "
        f"1. Learning phases and topic-wise breakdown, "
        f"2. Hands-on projects for practical application, "
        f"3. Assessments and checkpoints for evaluating progress, "
        f"4. Recommended learning resources and materials, "
        f"5. Structured learning milestones with timelines, "
        f"6. Detailed daily and weekly study schedules."
    )
    
    roadmap_content = generate_ai_response(prompt)
    
    db_roadmap = models.Roadmap(
        user_id=user.id,
        career_path=career_path,
        skill_level=skill_level,
        content=roadmap_content
    )
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    
    return {
        "message": "AI Curriculum and Learning Roadmap generated successfully",
        "career_path": career_path,
        "skill_level": skill_level,
        "study_time": study_time,
        "roadmap": db_roadmap
    }

@router.get("/roadmaps")
def get_roadmaps(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.Roadmap).filter(models.Roadmap.user_id == user.id).all()