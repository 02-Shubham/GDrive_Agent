from pydantic import BaseModel
from datetime import datetime

class FileResult(BaseModel):
    id: str
    name: str
    mime_type: str
    modified_time: datetime | None
    web_view_link: str | None
    type_label: str        # "PDF", "Google Doc", "Image", etc.
    type_icon: str         # emoji icon for the file type

class ChatResponse(BaseModel):
    message: str
    files: list[FileResult] = []
    session_id: str
    search_performed: bool = False
