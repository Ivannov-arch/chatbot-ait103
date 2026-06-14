from pydantic import BaseModel
from typing import Optional, Dict, List


class ChatRequest(BaseModel):
    message: str
    debug: bool = False


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    matched_question: Optional[str] = None
    module: Optional[str] = None
    sub_intent: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None
    debug: Optional[str] = None


class SuggestionsResponse(BaseModel):
    suggestions: List[str]
