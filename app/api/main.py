from fastapi import APIRouter, Depends

from app.api.routes import library, novel
from app.config.auth import require_auth

api_router = APIRouter()
api_router.include_router(library.router)
api_router.include_router(novel.router, prefix="/novel", tags=["novel"], dependencies=[Depends(require_auth)])
