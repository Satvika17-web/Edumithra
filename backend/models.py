from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String)
    streak_count = Column(Integer, default=0)
    last_active_date = Column(String, nullable=True)

    quizzes = relationship("Quiz", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    roadmaps = relationship("Roadmap", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    career_path = Column(String)
    skill_level = Column(String)
    content = Column(String)

    user = relationship("User", back_populates="roadmaps")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    score = Column(Integer, default=0)
    result_status = Column(String, default="Completed")
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="quizzes")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    completion_percentage = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="progress")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="achievements")