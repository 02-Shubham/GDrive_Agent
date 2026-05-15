import json
import os
import re
import os
from collections.abc import Iterator

import requests

from frontend.errors import friendly_client_error

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def extract_folder_id(url: str) -> str | None:
    """
    Extracts folder ID from any Google Drive folder URL format.
    Returns None if URL is not a valid Drive folder link.
    
    Handles:
    - drive.google.com/drive/folders/ID
    - drive.google.com/drive/u/0/folders/ID
    - drive.google.com/open?id=ID
    """
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'[?&]id=([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def iter_chat_events(prompt: str, session_id: str, folder_id: str | None = None) -> Iterator[dict]:
    """Yield parsed SSE events from the backend chat endpoint."""
    try:
        with requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": prompt, "session_id": session_id, "folder_id": folder_id, "stream": True},
            stream=True,
            timeout=120,
        ) as response:
            if response.status_code != 200:
                yield {
                    "type": "error",
                    "content": friendly_client_error(
                        status_code=response.status_code,
                        body=response.text,
                    ),
                }
                return

            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if not decoded.startswith("data: "):
                    continue
                data_str = decoded[6:]
                if data_str == "[DONE]":
                    break
                try:
                    yield json.loads(data_str)
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.ConnectionError as exc:
        yield {"type": "error", "content": friendly_client_error(exception=exc)}
    except requests.exceptions.Timeout:
        yield {"type": "error", "content": "The request timed out. Please try again."}
    except requests.exceptions.RequestException as exc:
        yield {"type": "error", "content": friendly_client_error(exception=exc)}
