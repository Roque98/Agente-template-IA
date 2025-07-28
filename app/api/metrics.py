from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.models.user import User
from app.models.execution import Execution
from app.models.cost import Cost
from app.schemas.execution import Execution as ExecutionSchema
from app.schemas.cost import Cost as CostSchema
from app.services.cost_service import CostService

router = APIRouter()

class CostSummary(BaseModel):
    total_amount: float
    total_tokens_input: int
    total_tokens_output: int
    total_entries: int
    by_type: dict

class UsageMetrics(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    total_tokens_used: int
    total_cost: float

@router.get("/costs", response_model=CostSummary)
def get_costs(
    cost_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    cost_service = CostService(db)
    
    # Admin can see all costs, users can only see their own
    if current_user.role == "Admin":
        # For admin, get overall costs (would need to modify cost_service method)
        # For now, return user's own costs
        costs = cost_service.get_user_costs(
            user_id=current_user.id,
            cost_type=cost_type,
            start_date=start_date,
            end_date=end_date
        )
    else:
        costs = cost_service.get_user_costs(
            user_id=current_user.id,
            cost_type=cost_type,
            start_date=start_date,
            end_date=end_date
        )
    
    return CostSummary(**costs)

@router.get("/usage", response_model=UsageMetrics)
def get_usage_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Execution)
    
    # Filter by user (admins can see all)
    if current_user.role != "Admin":
        query = query.filter(Execution.user_id == current_user.id)
    
    # Apply date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Execution.started_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Execution.started_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    executions = query.all()
    
    if not executions:
        return UsageMetrics(
            total_executions=0,
            successful_executions=0,
            failed_executions=0,
            average_execution_time=0.0,
            total_tokens_used=0,
            total_cost=0.0
        )
    
    # Calculate metrics
    total_executions = len(executions)
    successful_executions = len([e for e in executions if e.status == "completed"])
    failed_executions = len([e for e in executions if e.status == "failed"])
    
    # Calculate average execution time (only for completed executions)
    completed_executions = [e for e in executions if e.execution_time_ms is not None]
    if completed_executions:
        average_execution_time = sum(e.execution_time_ms for e in completed_executions) / len(completed_executions)
    else:
        average_execution_time = 0.0
    
    total_tokens_used = sum(e.tokens_used or 0 for e in executions)
    total_cost = sum(float(e.cost or 0) for e in executions)
    
    return UsageMetrics(
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        average_execution_time=average_execution_time,
        total_tokens_used=total_tokens_used,
        total_cost=total_cost
    )

@router.get("/executions", response_model=List[ExecutionSchema])
def get_executions(
    skip: int = Query(0),
    limit: int = Query(100),
    status: Optional[str] = Query(None),
    agent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Execution)
    
    # Filter by user (admins can see all)
    if current_user.role != "Admin":
        query = query.filter(Execution.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Execution.status == status)
    
    if agent_id:
        query = query.filter(Execution.agent_id == agent_id)
    
    # Order by most recent first
    query = query.order_by(Execution.started_at.desc())
    
    # Apply pagination
    executions = query.offset(skip).limit(limit).all()
    
    return executions

@router.get("/costs/detailed", response_model=List[CostSchema])
def get_detailed_costs(
    skip: int = Query(0),
    limit: int = Query(100),
    cost_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Build query
    query = db.query(Cost)
    
    # Filter by user (admins can see all)
    if current_user.role != "Admin":
        query = query.filter(Cost.user_id == current_user.id)
    
    # Apply filters
    if cost_type:
        query = query.filter(Cost.cost_type == cost_type)
    
    # Order by most recent first
    query = query.order_by(Cost.created_at.desc())
    
    # Apply pagination
    costs = query.offset(skip).limit(limit).all()
    
    return costs