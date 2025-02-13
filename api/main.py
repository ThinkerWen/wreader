from fastapi import APIRouter

from api.routes import novel

api_router = APIRouter()
api_router.include_router(novel.router, prefix="/novel", tags=["novel"])
