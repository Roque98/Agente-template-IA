from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    input_data = Column(Text)
    output_data = Column(Text)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost = Column(Numeric(10, 6), default=0.0)
    error_message = Column(Text)
    execution_metadata = Column(Text)  # JSON with additional execution info
    started_at = Column(DateTime, server_default=func.getutcdate())
    completed_at = Column(DateTime)
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")
    user = relationship("User", back_populates="executions")
    costs = relationship("Cost", back_populates="execution", cascade="all, delete-orphan")