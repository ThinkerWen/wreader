from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from core.configuration.settings import settings

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    return open(f"{settings.APP_PATH}/app/templates/index.html", 'r').read()
