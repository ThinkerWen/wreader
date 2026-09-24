from app.core.configuration.settings import settings
from app.core.util.source_tool import load_source_config


async def load_core_config():
    # 加载源列表
    settings.ALL_SOURCES = await load_source_config()
    settings.SOURCE_CONFIG = {key: source for key, source in settings.ALL_SOURCES.items() if source.enable}
