from urllib.parse import urljoin

from lxml import etree

from app.core.entity.chapter import Chapter
from app.core.entity.novel import Novel
from app.core.net import fetch_page
from app.core.net.safety import validate_url
from app.core.parser import ParserFactory
from app.core.util.net_tool import get_request_params
from app.core.util.source_tool import get_source


def parse_content(text: str, source: dict) -> str:
    if not text or not source:
        return ""
    return "\n".join(ParserFactory.get_parser("xpath").contents(etree.HTML(text), source.get("contents")))


def parse_next_url(text: str, source: dict) -> str:
    if not text or not source or not source.get("next"):
        return ""
    return ParserFactory.get_parser("xpath").next_page(etree.HTML(text), source["next"])


async def fetch_content(novel: Novel, chapter: Chapter, page: str | None = None) -> dict:
    validate_url(novel.source_id, novel.url)
    validate_url(novel.source_id, chapter.url)
    source = await get_source(novel.source_id)
    url = page or chapter.url
    text = await fetch_page(novel.source_id, get_request_params(source, "content", url=url))
    next_page = parse_next_url(text, source.get("ruleContent"))
    return {
        "content": parse_content(text, source.get("ruleContent")),
        "next_page": validate_url(novel.source_id, urljoin(url, next_page)) if next_page else "",
    }
