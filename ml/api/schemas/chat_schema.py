from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(default="default", min_length=1, max_length=128)
    debug: bool = False


class ResetChatRequest(BaseModel):
    session_id: str = Field(default="default", min_length=1, max_length=128)


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    matched_question: Optional[str] = None
    module: Optional[str] = None
    sub_intent: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None
    debug: Optional[str] = None
    session_id: str = "default"


class SuggestionsResponse(BaseModel):
    suggestions: List[str]
