import io
import json

from googleapiclient.http import MediaIoBaseDownload
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from backend.config import get_settings
from backend.tools.drive_tool import file_is_in_scope, get_drive_service

MAX_READ_CHARS = 24_000
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024

GOOGLE_EXPORT_MIME = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}

READABLE_TEXT_MIMES = (
    "text/",
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-python",
    "application/rtf",
)


def _download_bytes(service, file_id: str) -> bytes:
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    data = buf.getvalue()
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError("File is too large to read (max 8 MB).")
    return data


def _export_google_file(service, file_id: str, export_mime: str) -> str:
    request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue().decode("utf-8", errors="replace")


def _extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF support is not installed on the server.") from exc

    reader = PdfReader(io.BytesIO(data))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def read_file_text(file_id: str) -> dict:
    service = get_drive_service()
    if not file_is_in_scope(service, file_id):
        raise ValueError("That file is not in the configured Drive folder.")

    meta = (
        service.files()
        .get(
            fileId=file_id,
            fields="id, name, mimeType, size",
            supportsAllDrives=True,
        )
        .execute()
    )
    mime = meta.get("mimeType", "")
    name = meta.get("name", "Unnamed")
    size = int(meta.get("size") or 0)
    if size > MAX_DOWNLOAD_BYTES and mime not in GOOGLE_EXPORT_MIME:
        raise ValueError("File is too large to read (max 8 MB).")

    if mime in GOOGLE_EXPORT_MIME:
        text = _export_google_file(service, file_id, GOOGLE_EXPORT_MIME[mime])
    elif mime == "application/pdf":
        text = _extract_pdf_text(_download_bytes(service, file_id))
    elif mime.startswith(READABLE_TEXT_MIMES):
        text = _download_bytes(service, file_id).decode("utf-8", errors="replace")
    else:
        raise ValueError(
            f"Cannot read '{name}' ({mime}). Supported: Google Docs/Sheets/Slides, PDF, and plain text files."
        )

    truncated = False
    if len(text) > MAX_READ_CHARS:
        text = text[:MAX_READ_CHARS]
        truncated = True

    return {
        "file_id": file_id,
        "name": name,
        "mimeType": mime,
        "content": text,
        "truncated": truncated,
    }


def format_read_result(payload: dict) -> str:
    note = "\n[Content truncated for length.]" if payload.get("truncated") else ""
    return (
        f"File: {payload['name']} (id: {payload['file_id']})\n"
        f"Type: {payload['mimeType']}\n\n"
        f"{payload['content']}{note}"
    )


class DriveReadInput(BaseModel):
    file_id: str = Field(
        description="Google Drive file id from drive_search or Active file context"
    )


class DriveReadFileTool(BaseTool):
    name: str = "drive_read_file"
    description: str = """
    Read and return the text content of a file in the configured Drive folder.
    Use after drive_search when the user wants to summarize, explain, or analyze a specific file.
    Requires the exact file_id from search results or Active file context — never invent an id.
    Supports Google Docs, Sheets, Slides (exported as text), PDFs, and plain text files.
    """
    args_schema: type[BaseModel] = DriveReadInput

    def _run(self, file_id: str) -> str:
        try:
            payload = read_file_text(file_id.strip())
            return format_read_result(payload)
        except Exception as e:
            return f"Could not read file: {e}"

    async def _arun(self, file_id: str) -> str:
        return self._run(file_id)
