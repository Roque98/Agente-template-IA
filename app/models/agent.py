from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    system_prompt = Column(Text)
    personality = Column(Text)
    model_name = Column(String(50), default="gpt-3.5-turbo")
    temperature = Column(Numeric(3, 2), default=0.7)
    max_tokens = Column(Integer, default=1000)
    top_p = Column(Numeric(3, 2), default=1.0)
    frequency_penalty = Column(Numeric(3, 2), default=0.0)
    presence_penalty = Column(Numeric(3, 2), default=0.0)
    rate_limit_per_minute = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    created_by_user = relationship("User", back_populates="agents")
    executions = relationship("Execution", back_populates="agent", cascade="all, delete-orphan")
    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")