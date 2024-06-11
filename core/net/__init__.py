import asyncio
import signal

import aiohttp


class SingletonClient:
    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = await cls._create_client()
                    signal.signal(signal.SIGINT, cls._signal_handler)
                    signal.signal(signal.SIGTERM, cls._signal_handler)
        return cls._instance

    @staticmethod
    async def _create_client():
        return aiohttp.ClientSession()

    @classmethod
    def _signal_handler(cls, signum, frame):
        asyncio.run(cls.close_client())

    @classmethod
    async def close_client(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
