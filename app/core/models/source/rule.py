from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Rule(BaseModel):
    header: Dict[str, Any] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)
    mode: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    engine: Optional[str] = None
    request: Optional[str] = None
    requestEncode: Optional[str] = None
    response: Optional[str] = None
    responseEncode: Optional[str] = None
    ruleExtra: Dict[str, Any] = Field(default_factory=dict)
