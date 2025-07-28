from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    endpoint_template = Column(Text, nullable=False)
    method_allowed = Column(String(100), default="GET,POST,PUT,DELETE")
    default_headers = Column(Text)  # JSON
    requires_auth = Column(Boolean, default=False)
    cost_per_request = Column(Numeric(10, 6), default=0.0)
    timeout_seconds = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    created_by_user = relationship("User", back_populates="tools")
    agent_tools = relationship("AgentTool", back_populates="tool", cascade="all, delete-orphan")