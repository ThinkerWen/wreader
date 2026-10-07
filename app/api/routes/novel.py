from fastapi import APIRouter, Body, HTTPException

from app.config.settings import settings
from app.core.models.chapter import Chapter
from app.core.models.novel import Novel
from app.core.processer.novel import search_novel
from app.core.processer.novel_chapter import fetch_chapter
from app.core.processer.novel_content import fetch_content

router = APIRouter()


@router.get("/search", response_model=list[Novel])
async def api_search(keyword: str, source_id: str | None = None) -> list[Novel]:
    if source_id and source_id not in settings.SOURCE_CONFIG:
        raise HTTPException(422, "书源不存在或已禁用")
    sources = [source_id] if source_id else list(settings.SOURCE_CONFIG)
    return await search_novel(keyword, sources)


@router.post("/chapter")
async def api_chapter(novel: Novel, next_page: str | None = Body(None)) -> dict:
    return await fetch_chapter(novel, next_page)


@router.post("/content")
async def api_content(novel: Novel, chapter: Chapter, next_page: str | None = Body(None)) -> dict:
    return await fetch_content(novel, chapter, next_page)
