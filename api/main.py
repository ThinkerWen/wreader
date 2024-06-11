from fastapi import APIRouter

from api.routes import index, novel

api_router = APIRouter()
api_router.include_router(index.router, tags=["index"])
api_router.include_router(novel.router, prefix="/novel", tags=["novel"])
