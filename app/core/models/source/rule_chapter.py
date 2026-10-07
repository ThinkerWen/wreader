from typing import Optional

from app.core.models.source.rule import Rule


class RuleChapter(Rule):
    chapterList: Optional[str] = None
    chapterName: Optional[str] = None
    chapterUrl: Optional[str] = None
    next: Optional[str] = None
