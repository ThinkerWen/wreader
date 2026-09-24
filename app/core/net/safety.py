import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

from fastapi import HTTPException

from app.core.configuration.settings import settings


def validate_url(source_id: str, url: str) -> str:
    source = settings.SOURCE_CONFIG.get(source_id)
    if not source:
        raise HTTPException(422, "书源不存在或已禁用")
    if not isinstance(url, str):
        raise HTTPException(422, "不允许的抓取地址")
    try:
        parsed = urlsplit(url)
        allowed = urlsplit(source.source_index or "")
        port = parsed.port
    except ValueError:
        raise HTTPException(422, "不允许的抓取地址") from None
    if (
        len(url) > 2048
        or parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or any(ord(char) < 33 for char in url)
        or port not in (None, 80, 443)
        or (parsed.scheme == "http" and port == 443)
        or (parsed.scheme == "https" and port == 80)
        or allowed.scheme not in ("http", "https")
        or not allowed.hostname
        or parsed.scheme != allowed.scheme
        or parsed.hostname.lower() != allowed.hostname.lower()
    ):
        raise HTTPException(422, "不允许的抓取地址")
    try:
        if not ipaddress.ip_address(parsed.hostname).is_global:
            raise HTTPException(422, "不允许访问内网地址")
    except ValueError:
        pass
    return url


class SafeResolver:
    async def resolve(self, host: str, port: int = 0, family: int = socket.AF_UNSPEC):
        addresses = await asyncio.get_running_loop().getaddrinfo(host, port, family=family, type=socket.SOCK_STREAM)
        records = []
        for address_family, _, proto, _, sockaddr in addresses:
            if not ipaddress.ip_address(sockaddr[0]).is_global:
                raise OSError("不允许访问内网地址")
            records.append(
                {
                    "hostname": host,
                    "host": sockaddr[0],
                    "port": port,
                    "family": address_family,
                    "proto": proto,
                    "flags": socket.AI_NUMERICHOST,
                }
            )
        if not records:
            raise OSError("书源域名没有可用地址")
        return records

    async def close(self):
        pass
