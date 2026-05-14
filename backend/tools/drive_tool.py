import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from backend.config import get_settings

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
