from pydantic import BaseModel, Field


class SessionHistoryUpdate(BaseModel):
    messages: list[dict] = Field(default_factory=list)
    search_count: int = 0


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[dict] = Field(default_factory=list)
    search_count: int = 0
