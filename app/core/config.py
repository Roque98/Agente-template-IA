from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    secret_key: str
    encryption_key: str
    
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    app_name: str = "Agent System"
    debug: bool = False
    
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()