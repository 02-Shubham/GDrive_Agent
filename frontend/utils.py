import json
import os
from collections.abc import Iterator

import requests

from frontend.errors import friendly_client_error

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def iter_chat_events(prompt: str, session_id: str) -> Iterator[dict]:
    """Yield parsed SSE events from the backend chat endpoint."""
    try:
        with requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": prompt, "session_id": session_id, "stream": True},
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
