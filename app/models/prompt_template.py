from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    template_content = Column(Text, nullable=False)
    description = Column(String(500))
    variables = Column(Text)  # JSON array of variable names
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    created_by_user = relationship("User", back_populates="prompt_templates")