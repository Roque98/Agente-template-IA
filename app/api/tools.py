from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.tool import Tool
from app.schemas.tool import Tool as ToolSchema, ToolCreate, ToolUpdate

router = APIRouter()

@router.get("/", response_model=List[ToolSchema])
def get_tools(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Admin":
        tools = db.query(Tool).offset(skip).limit(limit).all()
    else:
        tools = db.query(Tool).filter(
            (Tool.created_by == current_user.id) | (Tool.created_by.is_(None))
        ).offset(skip).limit(limit).all()
    
    return tools

@router.post("/", response_model=ToolSchema)
def create_tool(
    tool_data: ToolCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if tool name already exists
    existing_tool = db.query(Tool).filter(Tool.name == tool_data.name).first()
    if existing_tool:
        raise HTTPException(status_code=400, detail="Tool name already exists")
    
    # Create tool
    tool = Tool(
        **tool_data.dict(),
        created_by=current_user.id
    )
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    return tool

@router.get("/{tool_id}", response_model=ToolSchema)
def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check permissions
    if (current_user.role != "Admin" and 
        tool.created_by != current_user.id and 
        tool.created_by is not None):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return tool

@router.put("/{tool_id}", response_model=ToolSchema)
def update_tool(
    tool_id: int,
    tool_update: ToolUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check permissions
    if current_user.role != "Admin" and tool.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check name uniqueness if updating name
    if tool_update.name and tool_update.name != tool.name:
        existing_tool = db.query(Tool).filter(Tool.name == tool_update.name).first()
        if existing_tool:
            raise HTTPException(status_code=400, detail="Tool name already exists")
    
    # Update tool fields
    update_data = tool_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tool, field, value)
    
    db.commit()
    db.refresh(tool)
    
    return tool

@router.delete("/{tool_id}")
def delete_tool(
    tool_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check permissions
    if current_user.role != "Admin" and tool.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(tool)
    db.commit()
    
    return {"message": "Tool deleted successfully"}