from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class PromptTemplateBase(BaseModel):
    name: str
    template_content: str
    description: Optional[str] = None
    variables: Optional[List[str]] = []
    version: int = 1
    is_active: bool = True

class PromptTemplateCreate(PromptTemplateBase):
    pass

class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_content: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

class PromptTemplate(PromptTemplateBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True