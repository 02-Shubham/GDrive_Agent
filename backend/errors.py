"""Map provider / API failures to user-facing messages."""

import re


def friendly_llm_error(exc: BaseException) -> str:
    raw = str(exc)
    lower = raw.lower()

    if any(
        x in lower
        for x in (
            "insufficient",
            "quota",
            "credit",
            "billing",
            "balance",
            "exceeded your current",
            "usage limit",
        )
    ) or "402" in raw:
        return (
            "The AI service has run out of API credits or hit its usage limit. "
            "Check your Groq account billing and limits, then try again."
        )

    if "429" in raw or "rate limit" in lower or "too many requests" in lower:
        return (
            "The AI service is temporarily rate-limited. "
            "Wait a minute and try again."
        )

    if (
        "401" in raw
        or "invalid api key" in lower
        or "authentication" in lower
        or "unauthorized" in lower
    ):
        return (
            "The Groq API key is missing or invalid. "
            "Update GROQ_API_KEY in your .env file and restart the backend."
        )

    if "403" in raw or "permission" in lower:
        return "The AI service rejected this request. Check your API key permissions."

    if "model" in lower and ("not found" in lower or "decommissioned" in lower):
        return (
            "The configured LLM model is unavailable. "
            "Try a different LLM_MODEL in your .env file."
        )

    if "connection" in lower or "timeout" in lower or "network" in lower:
        return "Could not reach the AI service. Check your network and try again."

    # Strip noisy JSON blobs when possible
    short = re.sub(r"\{.*\}", "", raw, flags=re.DOTALL).strip()
    if len(short) > 200:
        short = short[:200] + "…"
    if short:
        return f"Something went wrong while generating a reply. ({short})"
    return "Something went wrong while generating a reply. Please try again."
