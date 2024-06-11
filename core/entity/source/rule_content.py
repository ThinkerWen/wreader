from typing import Optional

from core.entity.source.rule import Rule


class RuleContent(Rule):
    contents: Optional[str] = None
    next: Optional[str] = None
    cleaner: Optional[str] = None
