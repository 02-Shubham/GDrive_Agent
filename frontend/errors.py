"""User-facing error messages for the Streamlit client."""

import json
import re


def friendly_client_error(
    *,
    status_code: int | None = None,
    body: str = "",
    exception: BaseException | None = None,
) -> str:
    text = body or (str(exception) if exception else "")
    lower = text.lower()

    if status_code == 401:
        return "The backend rejected the request (unauthorized). Check server configuration."

    if status_code == 429:
        return "Too many requests. Wait a moment and try again."

    if status_code in (402, 403) or any(
        x in lower
        for x in ("insufficient", "quota", "credit", "billing", "usage limit")
    ):
        return (
            "The AI service has run out of API credits or hit its usage limit. "
            "Check your Groq account, then try again."
        )

    if "rate limit" in lower or "429" in text:
        return "The AI service is temporarily rate-limited. Wait a minute and try again."

    if "invalid api key" in lower or "401" in text or "unauthorized" in lower:
        return (
            "The Groq API key is missing or invalid. "
            "Update GROQ_API_KEY in your .env and restart the backend."
        )

    if isinstance(exception, ConnectionError) or "connection" in lower:
        return (
            "Could not connect to the backend. "
            "Make sure it is running (e.g. uvicorn on port 8000)."
        )

    # Backend may return JSON detail
    try:
        payload = json.loads(body)
        detail = payload.get("detail") or payload.get("message") or ""
        if isinstance(detail, str) and detail:
            return friendly_client_error(body=detail)
    except (json.JSONDecodeError, TypeError):
        pass

    if text and len(text) < 280:
        return text
    return "Something went wrong. Please try again."
