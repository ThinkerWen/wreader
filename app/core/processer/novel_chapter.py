from urllib.parse import urljoin

from lxml import etree

from app.core.models.chapter import Chapter
from app.core.models.novel import Novel
from app.core.processer.client import fetch_page
from app.core.processer.safety import validate_url
from app.core.parser import ParserFactory
from app.core.utils.net_tool import get_request_params
from app.core.utils.source_tool import get_source


def parse_chapter(text: str, source: dict) -> list[Chapter]:
    if not text or not source:
        return []
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    return [
        Chapter(name=parser.chapter_name(item, source.get("chapterName")), url=parser.chapter_url(item, source.get("chapterUrl")))
        for item in parser.chapter_list(doc, source.get("chapterList"))
    ]


def parse_extra(text: str, source: dict) -> dict:
    if not text or not source:
        return {}
    book = {}
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    extra = source.get("ruleExtra") or {}
    book["bookSize"] = parser.book_size(doc, extra.get("bookSize"))
    book["classify"] = parser.classify(doc, extra.get("classify"))
    book["coverUrl"] = parser.cover_url(doc, extra.get("coverUrl"))
    book["introduce"] = parser.introduce(doc, extra.get("introduce"))
    book["lastChapterName"] = parser.last_chapter_name(doc, extra.get("lastChapterName"))
    book["lastUpdateTime"] = parser.last_update_time(doc, extra.get("lastUpdateTime"))
    book["status"] = parser.status(doc, extra.get("status"))
    return book


def parse_next_url(text: str, source: dict) -> str:
    if not text or not source or not source.get("next"):
        return ""
    return ParserFactory.get_parser("xpath").next_page(etree.HTML(text), source["next"])


async def fetch_chapter(novel: Novel, page: str | None = None) -> dict:
    validate_url(novel.source_id, novel.url)
    source = await get_source(novel.source_id)
    url = page or novel.url
    text = await fetch_page(novel.source_id, get_request_params(source, "chapter", url=url))
    chapters = []
    for chapter in parse_chapter(text, source.get("ruleChapter")):
        if chapter.url:
            chapter.url = validate_url(novel.source_id, urljoin(url, chapter.url))
            chapters.append(chapter)
    extra = parse_extra(text, source.get("ruleChapter"))
    novel.size = extra.get("bookSize")
    novel.classify = extra.get("classify")
    novel.cover_url = extra.get("coverUrl")
    novel.introduce = extra.get("introduce")
    novel.last_chapter_name = extra.get("lastChapterName")
    novel.last_update_time = extra.get("lastUpdateTime")
    novel.status = extra.get("status")
    next_page = parse_next_url(text, source.get("ruleChapter"))
    return {"chapter_list": chapters, "next_page": validate_url(novel.source_id, urljoin(url, next_page)) if next_page else ""}
