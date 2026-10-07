from typing import Optional, get_type_hints

from pydantic import BaseModel


class Chapter(BaseModel):
    name: str
    url: str

    def __setattr__(self, name, value):
        hints = get_type_hints(self.__class__)
        if name in hints and hints[name] == Optional[str] and value:
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return f"Chapter(章节名：{self.name}, 地址：{self.url})"
