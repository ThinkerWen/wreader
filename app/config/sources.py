import json
import os
import re
from pathlib import Path

import yaml

from app.config.settings import settings
from app.core.models.source_summary import SourceSummary

SOURCE_ID = re.compile(r"[a-f0-9]{32}\Z")


def source_path(source_id: str) -> Path:
    if not SOURCE_ID.fullmatch(source_id):
        raise ValueError("无效书源 ID")
    return settings.SOURCE_PATH / f"{source_id}.json"


async def load_source_config() -> dict[str, SourceSummary]:
    path = settings.CONFIGURATION_PATH / "source_config.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise ValueError("书源配置必须是非空映射")
    result = {}
    for source_id, config in raw.items():
        if (
            not isinstance(source_id, str)
            or not SOURCE_ID.fullmatch(source_id)
            or not isinstance(config, dict)
            or config.get("source_id") != source_id
        ):
            raise ValueError(f"书源配置 ID 不匹配: {source_id}")
        summary = SourceSummary.model_validate(config)
        if not isinstance(config.get("enable"), bool):
            raise ValueError(f"书源启用状态无效: {source_id}")
        source = json.loads(source_path(source_id).read_text(encoding="utf-8"))
        if not isinstance(source, dict) or not source:
            raise ValueError(f"书源 JSON 无效: {source_id}")
        result[source_id] = summary
    return dict(sorted(result.items(), key=lambda item: item[1].priority or 0, reverse=True))


async def save_source_config(source: SourceSummary) -> None:
    await load_source_config()
    path = settings.CONFIGURATION_PATH / "source_config.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw[source.source_id] = source.model_dump()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    os.replace(temporary, path)
