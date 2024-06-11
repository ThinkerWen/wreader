from lxml.etree import _Element as Element

from core.interceptor.exception.xpath_error_handler import xpath_error_handler
from core.interceptor.js_interceptor import js_interceptor
from core.parser.parser import IParser


class XPathParser(IParser):

    @js_interceptor
    @xpath_error_handler
    def book_size(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def cover_url(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def introduce(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def last_update_time(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def last_chapter_name(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def status(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def classify(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    def book_list(self, node: Element, exp: str) -> list[Element]:
        return node.xpath(exp)

    @js_interceptor
    @xpath_error_handler
    def book_name(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def book_url(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def book_auther(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    def chapter_list(self, node: Element, exp: str) -> list[Element]:
        return node.xpath(exp)

    @js_interceptor
    @xpath_error_handler
    def chapter_name(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def chapter_url(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @js_interceptor
    @xpath_error_handler
    def next_page(self, node: Element, exp: str) -> str:
        return node.xpath(exp).pop()

    @xpath_error_handler
    def contents(self, node: Element, exp: str) -> list[Element]:
        return node.xpath(exp)
