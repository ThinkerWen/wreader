from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.main import api_router
from config.loader import load_config
from core.configuration.settings import settings

app = FastAPI(title="WReader")
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


@app.on_event("startup")
async def startup_event():
    # 在应用启动时加载全局配置文件
    await load_config()

app.include_router(api_router)
