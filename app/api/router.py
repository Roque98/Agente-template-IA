from fastapi import APIRouter

from app.api import auth, agents, tools, prompts, metrics, config

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompt-templates"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(config.router, prefix="/config", tags=["configuration"])