from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from api.main import api_router
from config.loader import load_config
from core.configuration.settings import settings


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    await load_config()
    yield


app = FastAPI(title="WReader", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.APP_PATH = Path(__file__).parent
settings.SOURCE_PATH = settings.APP_PATH / "_sources"
settings.CONFIGURATION_PATH = settings.APP_PATH / "_configurations"
if not settings.SOURCE_PATH.exists():
    settings.SOURCE_PATH.mkdir()

app.include_router(api_router)
app.mount("/", StaticFiles(directory=f"{settings.APP_PATH}/app", html=True), name="static")
