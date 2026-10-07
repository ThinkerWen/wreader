import asyncio
import json
import os
from uuid import uuid4

from app.config.settings import settings
from app.config.sources import source_path


async def get_source(source_id: str) -> dict:
    if source_id not in settings.SOURCE_CONFIG:
        raise ValueError("书源不存在或已禁用")
    source = json.loads(source_path(source_id).read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not source:
        raise ValueError("书源 JSON 无效")
    return source


async def save_source(source: dict, source_id: str | None) -> None:
    source_id = source_id or uuid4().hex
    path = source_path(source_id)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, path)


async def get_sources(source_ids: list[str]) -> dict[str, dict]:
    return dict(zip(source_ids, await asyncio.gather(*(get_source(source_id) for source_id in source_ids)), strict=True))
