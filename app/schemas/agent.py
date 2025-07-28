from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    personality: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    temperature: Decimal = Decimal("0.7")
    max_tokens: int = 1000
    top_p: Decimal = Decimal("1.0")
    frequency_penalty: Decimal = Decimal("0.0")
    presence_penalty: Decimal = Decimal("0.0")
    rate_limit_per_minute: int = 10
    is_active: bool = True

class AgentCreate(AgentBase):
    tool_ids: Optional[list[int]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    personality: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[Decimal] = None
    max_tokens: Optional[int] = None
    top_p: Optional[Decimal] = None
    frequency_penalty: Optional[Decimal] = None
    presence_penalty: Optional[Decimal] = None
    rate_limit_per_minute: Optional[int] = None
    is_active: Optional[bool] = None
    tool_ids: Optional[list[int]] = None

class AgentExecute(BaseModel):
    input_message: str
    context: Optional[Dict[str, Any]] = {}

class Agent(AgentBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True