from typing import Optional

from app.core.models.source.rule import Rule


class RuleContent(Rule):
    contents: Optional[str] = None
    next: Optional[str] = None
    cleaner: Optional[str] = None
