from typing import Optional, get_type_hints

from pydantic import BaseModel


class Novel(BaseModel):
    name: str
    url: str
    source_id: Optional[str] = None
    size: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    cover_url: Optional[str] = None
    classify: Optional[str] = None
    introduce: Optional[str] = None
    last_update_time: Optional[str] = None
    last_chapter_name: Optional[str] = None

    def __setattr__(self, name, value):
        hints = get_type_hints(self.__class__)
        hint = hints.get(name)
        if hint == Optional[str]:
            if value is not None and isinstance(value, str) and value:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        return (f"Novel(书名：{self.name}, 封面：{self.cover_url}, 地址：{self.url}, "
                f"大小：{self.size}, 作者：{self.author}, 连载状态：{self.status}, 书籍分类：{self.classify}, "
                f"介绍：{self.introduce}, 最新更新时间：{self.last_update_time}, 最新章节名：{self.last_chapter_name})")
