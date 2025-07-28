import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
    PromptTemplate as PromptTemplateSchema, 
    PromptTemplateCreate, 
    PromptTemplateUpdate
)
from app.services.prompt_service import PromptService

router = APIRouter()

class RenderRequest(BaseModel):
    variables: Dict[str, Any]

class RenderResponse(BaseModel):
    rendered_content: str

class ValidateResponse(BaseModel):
    is_valid: bool
    variables: List[str]
    variable_count: int
    issues: List[str]

@router.get("/", response_model=List[PromptTemplateSchema])
def get_prompt_templates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "Admin":
        templates = db.query(PromptTemplate).offset(skip).limit(limit).all()
    else:
        templates = db.query(PromptTemplate).filter(
            PromptTemplate.created_by == current_user.id
        ).offset(skip).limit(limit).all()
    
    return templates

@router.post("/", response_model=PromptTemplateSchema)
def create_prompt_template(
    template_data: PromptTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate template
    prompt_service = PromptService(db)
    validation = prompt_service.validate_template(template_data.template_content)
    
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid template: {', '.join(validation['issues'])}"
        )
    
    # Create template
    template = PromptTemplate(
        name=template_data.name,
        template_content=template_data.template_content,
        description=template_data.description,
        variables=json.dumps(validation["variables"]),
        version=template_data.version,
        is_active=template_data.is_active,
        created_by=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template

@router.get("/{template_id}", response_model=PromptTemplateSchema)
def get_prompt_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if current_user.role != "Admin" and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return template

@router.put("/{template_id}", response_model=PromptTemplateSchema)
def update_prompt_template(
    template_id: int,
    template_update: PromptTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if current_user.role != "Admin" and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate new template content if provided
    if template_update.template_content:
        prompt_service = PromptService(db)
        validation = prompt_service.validate_template(template_update.template_content)
        
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid template: {', '.join(validation['issues'])}"
            )
        
        # Update variables
        template_update.variables = validation["variables"]
    
    # Update template fields
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "variables" and value is not None:
            setattr(template, field, json.dumps(value))
        else:
            setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template

@router.delete("/{template_id}")
def delete_prompt_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if current_user.role != "Admin" and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}

@router.post("/{template_id}/render", response_model=RenderResponse)
def render_template(
    template_id: int,
    render_request: RenderRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if current_user.role != "Admin" and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        prompt_service = PromptService(db)
        rendered_content = prompt_service.render_template(
            template_id, 
            render_request.variables
        )
        return RenderResponse(rendered_content=rendered_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{template_id}/validate", response_model=ValidateResponse)
def validate_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if current_user.role != "Admin" and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    prompt_service = PromptService(db)
    validation = prompt_service.validate_template(template.template_content)
    
    return ValidateResponse(**validation)