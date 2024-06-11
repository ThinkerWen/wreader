from typing import Optional, get_type_hints

from pydantic import BaseModel


class SourceSummary(BaseModel):
    source_id: str
    source_name: str
    priority: Optional[int] = 0
    source_author: Optional[str] = None
    source_index: Optional[str] = None

    def __setattr__(self, name, value):
        hints = get_type_hints(self.__class__)
        if name in hints and hints[name] == Optional[str] and value:
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return (f"SourceSummary(书源id={self.source_id}, 书源名={self.source_name}, 优先级={self.priority}, "
                f"书源作者={self.source_author}, 书源主页={self.source_index})")
