from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import get_current_admin_user
from app.core.database import get_db
from app.models.user import User
from app.models.system_config import SystemConfig
from app.services.config_service import config_service

router = APIRouter()

class ConfigItem(BaseModel):
    config_key: str
    config_value: str
    description: str = None
    is_encrypted: bool = False

class ConfigUpdate(BaseModel):
    config_value: str
    description: str = None
    is_encrypted: bool = False

class ConfigCreate(BaseModel):
    config_key: str
    config_value: str
    description: str = None
    is_encrypted: bool = False

@router.get("/", response_model=List[ConfigItem])
def get_all_configs(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all system configuration (admin only)"""
    configs = db.query(SystemConfig).all()
    
    result = []
    for config in configs:
        # Don't return encrypted values directly
        value = config.config_value
        if config.is_encrypted:
            value = "*** ENCRYPTED ***"
        
        result.append(ConfigItem(
            config_key=config.config_key,
            config_value=value,
            description=config.description,
            is_encrypted=config.is_encrypted
        ))
    
    return result

@router.get("/{config_key}")
def get_config(
    config_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific configuration value (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Return decrypted value for admin
    value = config_service.get_config(config_key)
    
    return {
        "config_key": config.config_key,
        "config_value": value,
        "description": config.description,
        "is_encrypted": config.is_encrypted
    }

@router.post("/", response_model=ConfigItem)
def create_config(
    config_data: ConfigCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new configuration (admin only)"""
    
    # Check if config already exists
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == config_data.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Configuration already exists")
    
    # Use config service to set the value
    success = config_service.set_config(
        key=config_data.config_key,
        value=config_data.config_value,
        description=config_data.description,
        encrypt=config_data.is_encrypted
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create configuration")
    
    # Return created config (mask encrypted values)
    value = config_data.config_value if not config_data.is_encrypted else "*** ENCRYPTED ***"
    
    return ConfigItem(
        config_key=config_data.config_key,
        config_value=value,
        description=config_data.description,
        is_encrypted=config_data.is_encrypted
    )

@router.put("/{config_key}", response_model=ConfigItem)
def update_config(
    config_key: str,
    config_update: ConfigUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a configuration (admin only)"""
    
    # Check if config exists
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Use config service to update the value
    success = config_service.set_config(
        key=config_key,
        value=config_update.config_value,
        description=config_update.description,
        encrypt=config_update.is_encrypted
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update configuration")
    
    # Return updated config (mask encrypted values)
    value = config_update.config_value if not config_update.is_encrypted else "*** ENCRYPTED ***"
    
    return ConfigItem(
        config_key=config_key,
        config_value=value,
        description=config_update.description,
        is_encrypted=config_update.is_encrypted
    )

@router.delete("/{config_key}")
def delete_config(
    config_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a configuration (admin only)"""
    
    success = config_service.delete_config(config_key)
    
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration deleted successfully"}

@router.post("/reload")
def force_reload_config(
    current_user: User = Depends(get_current_admin_user)
):
    """Force reload configuration cache (admin only)"""
    
    config_service.reload_config()
    
    return {"message": "Configuration reloaded successfully"}

@router.get("/status/hot-reload")
def get_hot_reload_status(
    current_user: User = Depends(get_current_admin_user)
):
    """Get hot reload status (admin only)"""
    
    return {
        "hot_reload_enabled": config_service.is_hot_reload_enabled(),
        "last_reload": config_service._last_reload,
        "reload_interval": config_service._reload_interval,
        "running": config_service._running
    }