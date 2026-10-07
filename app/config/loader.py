from app.config.settings import settings
from app.config.sources import load_source_config


async def load_config() -> None:
    settings.ALL_SOURCES = await load_source_config()
    settings.SOURCE_CONFIG = {key: source for key, source in settings.ALL_SOURCES.items() if source.enable}
