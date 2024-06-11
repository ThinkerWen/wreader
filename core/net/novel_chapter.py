from typing import Union
from urllib.parse import urljoin

from lxml import etree

from core.entity.chapter import Chapter
from core.entity.novel import Novel
from core.net import SingletonClient
from core.parser import ParserFactory
from core.util.source_tool import get_source


def parse_chapter(text: str, source: dict) -> list[Chapter]:
    result = list()
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    for chapter_doc in parser.chapter_list(doc, source.get("chapterList")):
        result.append(Chapter(
            name=parser.chapter_name(chapter_doc, source.get("chapterName")),
            url=parser.chapter_url(chapter_doc, source.get("chapterUrl"))
        ))

    return result


def parse_extra(text: str, source: dict) -> dict:
    book = dict()
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    extra = source.get("ruleExtra")
    book["bookSize"] = parser.book_size(doc, extra.get("bookSize"))
    book["classify"] = parser.classify(doc, extra.get("classify"))
    book["coverUrl"] = parser.cover_url(doc, extra.get("coverUrl"))
    book["introduce"] = parser.introduce(doc, extra.get("introduce"))
    book["lastChapterName"] = parser.last_chapter_name(doc, extra.get("lastChapterName"))
    book["lastUpdateTime"] = parser.last_update_time(doc, extra.get("lastUpdateTime"))
    book["status"] = parser.status(doc, extra.get("status"))
    return book


def parse_next_url(text, source) -> str:
    doc = etree.HTML(text)
    parser = ParserFactory.get_parser("xpath")
    return parser.next_page(doc, source.get("next"))


async def fetch_chapter(novel: Novel, page: Union[str | None] = None) -> dict:
    chapter_list = list()
    client = await SingletonClient.get_instance()
    source = await get_source(novel.source_id)
    source = source.get("ruleChapter")
    url = page if page else novel.url
    async with client.request(method=source.get("method"), url=url) as response:
        text = await response.text()
        for chapter in parse_chapter(text, source):
            chapter.url = urljoin(novel.url, chapter.url)
            chapter_list.append(chapter)
        extra = parse_extra(text, source)
        novel.size = extra.get("bookSize")
        novel.classify = extra.get("classify")
        novel.cover_url = extra.get("coverUrl")
        novel.introduce = extra.get("introduce")
        novel.last_chapter_name = extra.get("lastChapterName")
        novel.last_update_time = extra.get("lastUpdateTime")
        novel.status = extra.get("status")
    await SingletonClient.close_client()
    next_page = parse_next_url(text, source)
    return {
        "chapter_list": chapter_list,
        "next_page": urljoin(chapter.url, next_page) if next_page else str(),
    }
