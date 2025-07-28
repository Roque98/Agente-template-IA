from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="User")  # Admin, User, Viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="created_by_user", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="user", cascade="all, delete-orphan")
    encrypted_credentials = relationship("EncryptedCredentials", back_populates="user", cascade="all, delete-orphan")
    prompt_templates = relationship("PromptTemplate", back_populates="created_by_user", cascade="all, delete-orphan")
    tools = relationship("Tool", back_populates="created_by_user", cascade="all, delete-orphan")