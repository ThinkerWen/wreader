from urllib.parse import urljoin

from lxml import etree

from core.entity.novel import Novel
from core.net import SingletonClient
from core.parser import ParserFactory
from core.util.net_tool import get_request_params
from core.util.source_tool import get_sources


def parse_novel_list(text: str, source: dict) -> list[dict]:
    if not text or not source:
        return list()
    result = list()
    doc = etree.HTML(text)
    extra = source.get("ruleExtra")
    parser = ParserFactory.get_parser("xpath")
    for book_doc in parser.book_list(doc, source.get("bookList")):
        book = dict()
        book["bookName"] = parser.book_name(book_doc, source.get("bookName"))
        book["bookUrl"] = parser.book_url(book_doc, source.get("bookUrl"))
        book["classify"] = parser.classify(book_doc, extra.get("classify"))
        book["bookAuthor"] = parser.book_auther(book_doc, source.get("bookAuthor"))
        book["bookSize"] = parser.book_size(book_doc, extra.get("bookSize"))
        book["coverUrl"] = parser.cover_url(book_doc, extra.get("coverUrl"))
        book["lastChapterName"] = parser.last_chapter_name(book_doc, extra.get("lastChapterName"))
        book["lastUpdateTime"] = parser.last_update_time(book_doc, extra.get("lastUpdateTime"))
        book["status"] = parser.status(book_doc, extra.get("status"))
        result.append(book)

    return result


async def search_novel(keyword: str, source_ids: list[str]) -> list[Novel]:
    novel_list = list()
    sources = await get_sources(source_ids)
    for source_id in sources:
        source = sources[source_id]
        client = await SingletonClient.get_instance()
        async with client.request(**get_request_params(source, "search", keyword=keyword)) as response:
            text = await response.text()
            for book in parse_novel_list(text, source.get("ruleSearch")):
                novel_list.append(Novel(
                    name=book.get("bookName"),
                    url=urljoin(source.get("ruleSearch").get("url"), book.get("bookUrl")),
                    source_id=source_id,
                    author=book.get("bookAuthor"),
                    cover_url=book.get("coverUrl"),
                    size=book.get("bookSize"),
                    classify=book.get("classify"),
                    introduce=book.get("introduce"),
                    last_chapter_name=book.get("lastChapterName"),
                    last_update_time=book.get("lastUpdateTime"),
                    status=book.get("status")
                ))
    await SingletonClient.close_client()
    return novel_list
