from pydantic import BaseModel
from typing import List, Optional, Any


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str]
    message: str
    convo_id: Optional[str]


class ChatResponse(BaseModel):
    convo_id: Optional[str]
    reply: str
    metadata: Optional[Any] = None


class ChatStreamChunk(BaseModel):
    delta: str
    done: bool = False
