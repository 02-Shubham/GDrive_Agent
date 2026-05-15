import json
from pathlib import Path

SESSIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "sessions"


def _path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def save_session_data(session_id: str, data: dict) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    _path(session_id).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_session_data(session_id: str) -> dict | None:
    path = _path(session_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def delete_session_data(session_id: str) -> None:
    path = _path(session_id)
    if path.is_file():
        path.unlink()
