from typing import Optional

from core.entity.source.rule import Rule


class RuleSearch(Rule):
    bookList: Optional[str] = None
    bookName: Optional[str] = None
    bookUrl: Optional[str] = None
    bookAuthor: Optional[str] = None
