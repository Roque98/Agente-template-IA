from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class EncryptedCredentials(Base):
    __tablename__ = "encrypted_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credential_name = Column(String(100), nullable=False)
    encrypted_data = Column(Text, nullable=False)
    credential_type = Column(String(50))
    created_at = Column(DateTime, server_default=func.getutcdate())
    updated_at = Column(DateTime, server_default=func.getutcdate(), onupdate=func.getutcdate())
    
    # Relationships
    user = relationship("User", back_populates="encrypted_credentials")