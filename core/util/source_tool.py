import asyncio
import json
import os.path
from typing import Dict, Optional
from uuid import uuid4

import aiofiles
import yaml

from core.configuration.settings import settings
from core.entity.source_summary import SourceSummary


async def load_source_config() -> Dict[str, SourceSummary]:
    source_config = dict()
    async with aiofiles.open(os.path.join(settings.CONFIGURATION_PATH, "source_config.yaml"), 'r', encoding="utf-8") as file:
        yaml_str = await file.read()
        source_config_dict = yaml.safe_load(yaml_str)
        def sort_by_priority(x): return source_config_dict[x].get("priority", 0)

        for source_id in sorted(source_config_dict, key=sort_by_priority, reverse=True):
            source_config[source_id] = SourceSummary(**source_config_dict[source_id])
        return source_config


async def save_source_config(source: SourceSummary) -> None:
    source_config = await load_source_config()
    source_config[source.source_id] = source
    async with aiofiles.open(os.path.join(settings.CONFIGURATION_PATH, "source_config.yaml"), 'w', encoding="utf-8") as file:
        await file.write(yaml.dump(source_config))


async def get_source(source_id: str) -> dict:
    try:
        async with aiofiles.open(os.path.join(settings.SOURCE_PATH, f"{source_id}.json"), 'r', encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return dict()


async def save_source(source: dict, source_id: Optional[str]) -> None:
    if not source_id:
        source_id = str(uuid4()).replace("-", "")
    async with aiofiles.open(os.path.join(settings.SOURCE_PATH, f"{source_id}.json"), 'w', encoding="utf-8") as f:
        await f.write(json.dumps(source))


async def get_sources(source_ids: list) -> dict[str, dict]:
    sources = dict()
    tasks = [asyncio.create_task(get_source(source_id)) for source_id in source_ids]

    results = await asyncio.gather(*tasks)

    for source_id, result in zip(source_ids, results):
        sources[source_id] = result

    return sources
