from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AgentTool(Base):
    __tablename__ = "agent_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)
    configuration = Column(Text)  # JSON configuration for this specific agent-tool combination
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.getutcdate())
    
    # Relationships
    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")