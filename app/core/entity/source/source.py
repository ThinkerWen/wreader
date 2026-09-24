from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Source(BaseModel):
    header: Dict[str, Any] = Field(default_factory=dict)
    cookie: Dict[str, Any] = Field(default_factory=dict)
    ruleSearch: Dict[str, Any] = Field(default_factory=dict)
    ruleChapter: Dict[str, Any] = Field(default_factory=dict)
    ruleContent: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[str] = None
    siteName: Optional[str] = None
    host: Optional[str] = None
    author: Optional[str] = None
    contact: Optional[str] = None
    sourceUrl: Optional[str] = None
    remarks: Optional[str] = None
    update: Optional[str] = None

    def __repr__(self):
        return (f"Source(站点名称：{self.siteName}, 主页：{self.host}, 版本：{self.version}, "
                f"作者：{self.author}, 联系方式：{self.contact}, 源URL：{self.sourceUrl}, "
                f"备注：{self.remarks}, 源更新地址：{self.update})")
