import json
import base64
import time
from collections import deque

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from backend.config import get_settings
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Google Drive matches only direct parents for `'id' in parents`. We collect every
# folder id under the configured root, then query each parent separately and merge:
# combining multiple `'id' in parents` with `or` reliably returns empty results from the API.
_FOLDER_TREE_CACHE_TTL_SEC = 120.0
_folder_tree_cache: dict[str, tuple[float, list[str]]] = {}


def get_drive_service():
    settings = get_settings()
    sa_json = json.loads(base64.b64decode(settings.google_sa_json_b64))
    creds = service_account.Credentials.from_service_account_info(
        sa_json, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def file_is_in_scope(service, file_id: str) -> bool:
    """True if the file's direct parent folder is in the configured root tree."""
    settings = get_settings()
    folder_ids = set(_cached_folder_tree_ids(service, settings.drive_folder_id))
    meta = (
        service.files()
        .get(fileId=file_id, fields="parents", supportsAllDrives=True)
        .execute()
    )
    parents = meta.get("parents") or []
    return any(parent_id in folder_ids for parent_id in parents)


def _list_kwargs(page_token: str | None = None) -> dict:
    kwargs: dict = {
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
    }
    if page_token:
        kwargs["pageToken"] = page_token
    return kwargs


def _list_subfolder_ids(service, parent_id: str) -> list[str]:
    q = (
        f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    ids: list[str] = []
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=q,
                pageSize=100,
                fields="nextPageToken, files(id)",
                **_list_kwargs(page_token),
            )
            .execute()
        )
        for f in resp.get("files", []):
            ids.append(f["id"])
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return ids


def enumerate_folder_tree_ids(service, root_folder_id: str) -> list[str]:
    """Root id plus every descendant folder id (BFS). Files use one of these as direct parent."""
    ordered: list[str] = [root_folder_id]
    seen: set[str] = {root_folder_id}
    queue: deque[str] = deque([root_folder_id])
    while queue:
        parent_id = queue.popleft()
        for fid in _list_subfolder_ids(service, parent_id):
            if fid not in seen:
                seen.add(fid)
                ordered.append(fid)
                queue.append(fid)
    return ordered


def _cached_folder_tree_ids(service, root_folder_id: str) -> list[str]:
    now = time.monotonic()
    entry = _folder_tree_cache.get(root_folder_id)
    if entry and (now - entry[0]) < _FOLDER_TREE_CACHE_TTL_SEC:
        return entry[1]
    ids = enumerate_folder_tree_ids(service, root_folder_id)
    _folder_tree_cache[root_folder_id] = (now, ids)
    return ids


def _drive_list_once(service, full_q: str, page_size: int) -> list[dict]:
    result = (
        service.files()
        .list(
            q=full_q,
            pageSize=page_size,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink, thumbnailLink)",
            orderBy="modifiedTime desc",
            **_list_kwargs(),
        )
        .execute()
    )
    return result.get("files", [])


def list_files_raw(q: str, folder_id: str | None = None, max_results: int | None = None) -> list[dict]:
    from backend.config import request_folder_id
    service = get_drive_service()
    settings = get_settings()
    if max_results is None:
        max_results = settings.max_results
    
    active_folder = folder_id or request_folder_id.get() or settings.drive_folder_id
    
    try:
        folder_ids = _cached_folder_tree_ids(service, active_folder)

        base = f"({q}) and trashed=false"
        page_size = max(10, min(100, max_results * 5))

        by_id: dict[str, dict] = {}
        for f_id in folder_ids:
            full_q = f"{base} and ('{f_id}' in parents)"
            for f in _drive_list_once(service, full_q, page_size):
                by_id[f["id"]] = f

        merged = sorted(
            by_id.values(),
            key=lambda x: x.get("modifiedTime") or "",
            reverse=True,
        )
        return merged[:max_results]
    except HttpError as e:
        if e.resp.status == 403:
            raise ValueError(
                f"Access denied. Share your folder with: {settings.google_sa_email} (Viewer access)"
            )
        raise


def format_results(files: list[dict]) -> str:
    """Format file results into JSON string for the LLM."""
    return json.dumps(files, default=str)


class DriveSearchInput(BaseModel):
    q: str = Field(description="Google Drive API q parameter string")
    max_results: int = Field(
        default_factory=lambda: get_settings().max_results,
        description="Max files to return",
    )

class DriveSearchTool(BaseTool):
    name: str = "drive_search"
    description: str = """
    Search for files under the configured Drive folder, including any depth of subfolders.
    Input must be a valid Google Drive API 'q' parameter string (name, mimeType, fullText, modifiedTime, etc.).
    Do not add 'in parents' or folder-ID constraints; the backend applies recursive folder scoping.
    
    Examples:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'budget' and modifiedTime > '2024-01-01T00:00:00'
    - name contains 'invoice' and mimeType = 'application/pdf'
    
    Use specific filters. Never use an empty q string.
    """
    args_schema: type[BaseModel] = DriveSearchInput
    
    def _run(self, q: str, max_results: int | None = None) -> str:
        try:
            cap = max_results if max_results is not None else get_settings().max_results
            files = list_files_raw(q, max_results=cap)
            if not files:
                return "No files found matching your query."
            return format_results(files)
        except Exception as e:
            return f"Drive API error: {str(e)}. Try rephrasing your search or using different filters."
    
    async def _arun(self, q: str, max_results: int | None = None) -> str:
        return self._run(q, max_results)
