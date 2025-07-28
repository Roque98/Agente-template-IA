from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class CostBase(BaseModel):
    cost_type: str
    amount: Decimal
    currency: str = "USD"
    tokens_input: int = 0
    tokens_output: int = 0
    description: Optional[str] = None

class CostCreate(CostBase):
    user_id: int
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    execution_id: Optional[int] = None

class Cost(CostBase):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    execution_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True