import asyncio

import aiohttp

from app.core.processer.safety import SafeResolver, validate_url


class SingletonClient:
    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None or cls._instance.closed:
            async with cls._lock:
                if cls._instance is None or cls._instance.closed:
                    connector = aiohttp.TCPConnector(resolver=SafeResolver(), use_dns_cache=False)
                    cls._instance = aiohttp.ClientSession(connector=connector, trust_env=False, timeout=aiohttp.ClientTimeout(total=15))
        return cls._instance

    @classmethod
    async def close_client(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def fetch_page(source_id: str, params: dict) -> str:
    validate_url(source_id, params["url"])
    client = await SingletonClient.get_instance()
    async with client.request(**params, allow_redirects=False) as response:
        if 300 <= response.status < 400:
            raise ValueError("书源发生重定向，已拒绝抓取")
        response.raise_for_status()
        chunks = bytearray()
        async for chunk in response.content.iter_chunked(65536):
            chunks.extend(chunk)
            if len(chunks) > 2_000_000:
                raise ValueError("书源响应过大")
        return chunks.decode(response.charset or "utf-8", errors="replace")
