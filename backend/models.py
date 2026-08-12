from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    quizzes = relationship("Quiz", back_populates="user")
    progress = relationship("Progress", back_populates="user")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    score = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="quizzes")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    completion_percentage = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="progress")