from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Cost(Base):
    __tablename__ = "costs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    tool_id = Column(Integer, ForeignKey("tools.id"))
    execution_id = Column(Integer, ForeignKey("executions.id"))
    cost_type = Column(String(50), nullable=False)  # 'llm_call', 'tool_call', 'storage', etc.
    amount = Column(Numeric(10, 6), nullable=False)
    currency = Column(String(3), default="USD")
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.getutcdate())
    
    # Relationships
    user = relationship("User")
    agent = relationship("Agent")
    tool = relationship("Tool")
    execution = relationship("Execution", back_populates="costs")