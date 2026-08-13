from datetime import date
from groq import Groq
from backend.auth import get_current_user
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend import models
from backend.auth import get_password_hash, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EDUMITHRA")


@app.get("/")
def home():
    return {"message": "Welcome to EDUMITHRA"}


@app.get("/health")
def health_check():
    return {"status": "EDUMITHRA is running"}


# CREATE USER
@app.post("/users")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = get_password_hash(password)
    user = models.User(name=name, email=email, hashed_password=hashed_pw)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# READ USERS
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# UPDATE USER
@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    name: str,
    email: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = name
    user.email = email

    db.commit()
    db.refresh(user)

    return user


# DELETE USER
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


# LOGIN USER
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


# PROTECTED ROUTE TEST
@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"message": "You have successfully accessed a protected route!", "user": current_user}


# INITIALIZE GROQ CLIENT
groq_client = Groq(api_key=GROQ_API_KEY)


# GENERATE AI ROADMAP
@app.post("/generate-roadmap")
def generate_roadmap(
    career_path: str,
    skill_level: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    prompt = (
        f"Create a detailed, structured learning roadmap for a {skill_level} level student "
        f"pursuing a career in {career_path}. "
        f"The roadmap MUST include: "
        f"1. Learning phases and organized topics, "
        f"2. Recommended educational resources, "
        f"3. A structured daily and weekly learning plan, "
        f"4. Specific learning milestones and timelines."
    )
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        roadmap_content = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
    
    db_roadmap = models.Roadmap(
        user_id=user.id,
        career_path=career_path,
        skill_level=skill_level,
        content=roadmap_content
    )
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    
    return db_roadmap


# GET USER ROADMAPS
@app.get("/roadmaps")
def get_roadmaps(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    roadmaps = db.query(models.Roadmap).filter(models.Roadmap.user_id == user.id).all()
    return roadmaps

from datetime import date

# UPDATE PROGRESS & TRACK DAILY LEARNING STREAKS
@app.post("/progress")
def update_progress(
    topic: str,
    completion_percentage: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Monitor learning streaks and daily activities
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
                user.streak_count = 1  # Reset streak if a day was missed
        user.last_active_date = today_str

    # Update or create module progress
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


# RECORD QUIZ SCORES AND RESULTS
@app.post("/quizzes")
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


# GENERATE PROGRESS REPORTS & DASHBOARD ANALYTICS
@app.get("/progress/dashboard")
def get_progress_dashboard(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress_list = db.query(models.Progress).filter(models.Progress.user_id == user.id).all()
    quizzes = db.query(models.Quiz).filter(models.Quiz.user_id == user.id).all()
    
    # Calculate overall course completion percentage
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

# CREATE ACHIEVEMENT (CRUD)
@app.post("/achievements")
def create_achievement(
    title: str,
    description: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievement = models.Achievement(
        title=title,
        description=description,
        user_id=user.id
    )
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return achievement


# GET USER ACHIEVEMENTS (CRUD)
@app.get("/achievements")
def get_achievements(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.achievements