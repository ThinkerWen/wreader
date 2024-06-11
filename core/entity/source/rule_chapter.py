from typing import Optional

from core.entity.source.rule import Rule


class RuleChapter(Rule):
    chapterList: Optional[str] = None
    chapterName: Optional[str] = None
    chapterUrl: Optional[str] = None
    next: Optional[str] = None
