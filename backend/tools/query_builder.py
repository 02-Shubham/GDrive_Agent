from datetime import datetime, timedelta

MIME_TYPES = {
    "pdf": "application/pdf",
    "doc": "application/vnd.google-apps.document",
    "docs": "application/vnd.google-apps.document",
    "sheet": "application/vnd.google-apps.spreadsheet",
    "sheets": "application/vnd.google-apps.spreadsheet",
    "slide": "application/vnd.google-apps.presentation",
    "slides": "application/vnd.google-apps.presentation",
    "image": "image/jpeg",   # will be OR'd with png in complex queries, or just use contains
    "photo": "image/jpeg",
    "folder": "application/vnd.google-apps.folder",
}

def build_q_param(
    name_contains: str | None = None,
    name_exact: str | None = None,
    mime_type_key: str | None = None,
    full_text: str | None = None,
    modified_after: str | None = None,   # ISO string
    modified_before: str | None = None,
) -> str:
    """Construct a Google Drive API q parameter from structured inputs."""
    clauses = []
    if name_exact:
        clauses.append(f"name = '{name_exact}'")
    if name_contains:
        clauses.append(f"name contains '{name_contains}'")
    if mime_type_key and mime_type_key.lower() in MIME_TYPES:
        clauses.append(f"mimeType = '{MIME_TYPES[mime_type_key.lower()]}'")
    if full_text:
        clauses.append(f"fullText contains '{full_text}'")
    if modified_after:
        clauses.append(f"modifiedTime > '{modified_after}'")
    if modified_before:
        clauses.append(f"modifiedTime < '{modified_before}'")
    return " and ".join(clauses) if clauses else ""
