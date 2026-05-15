from pydantic import BaseModel, Field
import uuid

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    folder_id: str | None = None
    stream: bool = True
