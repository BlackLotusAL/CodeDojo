from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class LevelEnum(str, enum.Enum):
    entry = "entry"
    work = "work"
    pro = "pro"

class SubjectEnum(int, enum.Enum):
    algorithm = 1
    language = 2
    standard = 3
    design = 4

class TypeEnum(str, enum.Enum):
    single = "single"
    multiple = "multiple"
    judge = "judge"
    subjective = "subjective"

class User(Base):
    __tablename__ = "users"
    
    ip = Column(String, primary_key=True, index=True)
    nickname = Column(String, default="")
    is_admin = Column(Boolean, default=False)
    default_level = Column(SQLEnum(LevelEnum), default=LevelEnum.entry)
    
    answer_records = relationship("AnswerRecord", back_populates="user")
    wrong_book = relationship("WrongBook", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, index=True)
    level = Column(SQLEnum(LevelEnum), nullable=False)
    subject = Column(SQLEnum(SubjectEnum), nullable=False)
    type = Column(SQLEnum(TypeEnum), nullable=False)
    content = Column(String, nullable=False)
    options = Column(JSON, nullable=True)
    answer = Column(String, nullable=False)
    explanation = Column(String, nullable=True)
    
    answer_records = relationship("AnswerRecord", back_populates="question")
    wrong_book = relationship("WrongBook", back_populates="question")

class AnswerRecord(Base):
    __tablename__ = "answer_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_ip = Column(String, ForeignKey("users.ip"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    exam_session = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="answer_records")
    question = relationship("Question", back_populates="answer_records")

class WrongBook(Base):
    __tablename__ = "wrong_book"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_ip = Column(String, ForeignKey("users.ip"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    wrong_count = Column(Integer, default=1)
    mastered = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="wrong_book")
    question = relationship("Question", back_populates="wrong_book")
