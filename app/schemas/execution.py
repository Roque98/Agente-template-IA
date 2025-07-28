from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ExecutionBase(BaseModel):
    agent_id: int
    input_data: str
    output_data: Optional[str] = None
    status: str = "pending"
    execution_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost: Decimal = Decimal("0.0")
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class ExecutionCreate(BaseModel):
    agent_id: int
    input_data: str

class Execution(ExecutionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True