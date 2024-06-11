from core.configuration.loader import load_core_config


async def load_server_config():
    pass


async def load_config():
    await load_core_config()
    await load_server_config()