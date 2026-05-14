import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from backend.config import get_settings
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    settings = get_settings()
    sa_json = json.loads(base64.b64decode(settings.google_sa_json_b64))
    creds = service_account.Credentials.from_service_account_info(
        sa_json, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def list_files_raw(q: str, max_results: int = 10) -> list[dict]:
    service = get_drive_service()
    settings = get_settings()
    # Add folder scope and ensure trashed files are excluded
    full_q = f"({q}) and '{settings.drive_folder_id}' in parents and trashed=false"
    
    result = service.files().list(
        q=full_q,
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, size, webViewLink, thumbnailLink)",
        orderBy="modifiedTime desc"
    ).execute()
    
    return result.get("files", [])

def format_results(files: list[dict]) -> str:
    """Format file results into JSON string for the LLM."""
    return json.dumps(files, default=str)

class DriveSearchInput(BaseModel):
    q: str = Field(description="Google Drive API q parameter string")
    max_results: int = Field(default=10, description="Max files to return")

class DriveSearchTool(BaseTool):
    name: str = "drive_search"
    description: str = """
    Search for files in the designated Google Drive folder.
    Input must be a valid Google Drive API 'q' parameter string.
    
    Examples:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'budget' and modifiedTime > '2024-01-01T00:00:00'
    - name contains 'invoice' and mimeType = 'application/pdf'
    
    Always scope searches to relevant terms. Never use an empty q string.
    """
    args_schema: type[BaseModel] = DriveSearchInput
    
    def _run(self, q: str, max_results: int = 10) -> str:
        files = list_files_raw(q, max_results)
        if not files:
            return "No files found matching your query."
        return format_results(files)
    
    async def _arun(self, q: str, max_results: int = 10) -> str:
        return self._run(q, max_results)
