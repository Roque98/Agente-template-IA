from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    endpoint_template: str
    method_allowed: str = "GET,POST,PUT,DELETE"
    default_headers: Optional[Dict[str, str]] = {}
    requires_auth: bool = False
    cost_per_request: Decimal = Decimal("0.0")
    timeout_seconds: int = 30
    is_active: bool = True

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_template: Optional[str] = None
    method_allowed: Optional[str] = None
    default_headers: Optional[Dict[str, str]] = None
    requires_auth: Optional[bool] = None
    cost_per_request: Optional[Decimal] = None
    timeout_seconds: Optional[int] = None
    is_active: Optional[bool] = None

class Tool(ToolBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True