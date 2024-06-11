from typing import Union, List

from fastapi import APIRouter, Body

from core.configuration.settings import settings
from core.entity.chapter import Chapter
from core.entity.novel import Novel
from core.net.novel import search_novel
from core.net.novel_chapter import fetch_chapter
from core.net.novel_content import fetch_content

router = APIRouter()


@router.get("/search", response_model=List[Novel])
async def api_search(keyword: str, source_id: Union[str | None] = None) -> List[Novel]:
    if source_id:
        return await search_novel(keyword, [source_id])
    return await search_novel(keyword, [x for x in settings.SOURCE_CONFIG])


@router.post("/chapter")
async def api_chapter(novel: Novel, next_page: Union[str | None] = Body(None)) -> dict:
    return await fetch_chapter(novel, next_page)


@router.post("/content")
async def api_content(novel: Novel, chapter: Chapter, next_page: Union[str | None] = Body(None)) -> dict:
    return await fetch_content(novel, chapter, next_page)
