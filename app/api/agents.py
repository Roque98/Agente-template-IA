from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.agent import Agent
from app.models.agent_tools import AgentTool
from app.schemas.agent import Agent as AgentSchema, AgentCreate, AgentUpdate, AgentExecute
from app.schemas.execution import Execution as ExecutionSchema
from app.services.agent_service import AgentService

router = APIRouter()

@router.get("/", response_model=List[AgentSchema])
def get_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Admin":
        agents = db.query(Agent).offset(skip).limit(limit).all()
    else:
        agents = db.query(Agent).filter(Agent.created_by == current_user.id).offset(skip).limit(limit).all()
    
    return agents

@router.post("/", response_model=AgentSchema)
def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Create agent
    agent = Agent(
        **agent_data.dict(exclude={"tool_ids"}),
        created_by=current_user.id
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Add tools to agent
    if agent_data.tool_ids:
        for tool_id in agent_data.tool_ids:
            agent_tool = AgentTool(
                agent_id=agent.id,
                tool_id=tool_id
            )
            db.add(agent_tool)
    
    db.commit()
    db.refresh(agent)
    
    return agent

@router.get("/{agent_id}", response_model=AgentSchema)
def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check permissions
    if current_user.role != "Admin" and agent.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return agent

@router.put("/{agent_id}", response_model=AgentSchema)
def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check permissions
    if current_user.role != "Admin" and agent.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update agent fields
    update_data = agent_update.dict(exclude_unset=True, exclude={"tool_ids"})
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    # Update tools if provided
    if agent_update.tool_ids is not None:
        # Remove existing tool associations
        db.query(AgentTool).filter(AgentTool.agent_id == agent_id).delete()
        
        # Add new tool associations
        for tool_id in agent_update.tool_ids:
            agent_tool = AgentTool(
                agent_id=agent.id,
                tool_id=tool_id
            )
            db.add(agent_tool)
    
    db.commit()
    db.refresh(agent)
    
    return agent

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check permissions
    if current_user.role != "Admin" and agent.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(agent)
    db.commit()
    
    return {"message": "Agent deleted successfully"}

@router.post("/{agent_id}/execute", response_model=ExecutionSchema)
def execute_agent(
    agent_id: int,
    execution_data: AgentExecute,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check permissions
    if current_user.role != "Admin" and agent.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Execute agent
    agent_service = AgentService(db)
    try:
        execution = agent_service.execute_agent(
            agent_id=agent_id,
            user=current_user,
            input_message=execution_data.input_message,
            context=execution_data.context
        )
        return execution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))