from typing import Union
from urllib.parse import urljoin

from lxml import etree

from core.entity.chapter import Chapter
from core.entity.novel import Novel
from core.net import SingletonClient
from core.parser import ParserFactory
from core.util.net_tool import get_request_params
from core.util.source_tool import get_source


def parse_content(text: str, source: dict) -> str:
    if not text or not source:
        return str()
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    contents = parser.contents(doc, source.get("contents"))
    return "\n".join(contents)


def parse_next_url(text: str, source: dict) -> str:
    if not text or not source:
        return str()
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    return parser.next_page(doc, source.get("next"))


async def fetch_content(novel: Novel, chapter: Chapter, page: Union[str | None] = None) -> dict:
    client = await SingletonClient.get_instance()
    source = await get_source(novel.source_id)
    url = page if page else chapter.url
    async with client.request(**get_request_params(source, "content", url=url)) as response:
        text = await response.text()
        await SingletonClient.close_client()
        next_page = parse_next_url(text, source.get("ruleContent"))
        return {
            "content": parse_content(text, source.get("ruleContent")),
            "next_page": urljoin(chapter.url, next_page) if next_page else str(),
        }
