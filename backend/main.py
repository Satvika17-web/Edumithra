from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend import models

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
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = models.User(name=name, email=email)

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