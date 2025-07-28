from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)
    created_at = Column(DateTime, server_default=func.getutcdate())
    last_used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")