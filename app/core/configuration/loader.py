from app.core.configuration.settings import settings
from app.core.util.source_tool import load_source_config


async def load_core_config():
    # 加载源列表
    settings.SOURCE_CONFIG = await load_source_config()
