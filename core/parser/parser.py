from abc import ABCMeta, abstractmethod
from typing import Any


class IParser(metaclass=ABCMeta):

    # Book Extra rules
    @abstractmethod
    def book_size(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def cover_url(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def introduce(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def last_update_time(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def last_chapter_name(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def status(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def classify(self, node: Any, exp: str) -> str:
        pass

    # BookList rules
    @abstractmethod
    def book_list(self, node: Any, exp: str) -> list[Any]:
        pass

    @abstractmethod
    def book_name(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def book_url(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def book_auther(self, node: Any, exp: str) -> str:
        pass

    # Chapter rules
    @abstractmethod
    def chapter_list(self, node: Any, exp: str) -> list[Any]:
        pass

    @abstractmethod
    def chapter_name(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def chapter_url(self, node: Any, exp: str) -> str:
        pass

    @abstractmethod
    def next_page(self, node: Any, exp: str) -> str:
        pass

    # Content rules
    @abstractmethod
    def contents(self, node: Any, exp: str) -> list[Any]:
        pass
