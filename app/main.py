import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.main import api_router
from app.config.data import prepare_data
from app.config.loader import load_config
from app.core.processer.client import SingletonClient
from app.repository.library import initialize
from app.service.auth import load_credentials, secret


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    secret()
    prepare_data()
    load_credentials()
    await load_config()
    initialize()
    try:
        yield
    finally:
        await SingletonClient.close_client()


app = FastAPI(title="WReader", lifespan=lifespan)
if origin := os.getenv("WREADER_CORS_ORIGIN"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
app.include_router(api_router)
static = Path(__file__).resolve().parent.parent / "web" / "dist"
if static.is_dir():
    app.mount("/", StaticFiles(directory=static, html=True), name="static")
