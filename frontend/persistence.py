import uuid

import requests
import streamlit as st

from frontend.utils import BACKEND_URL


def _query_session_id() -> str | None:
    raw = st.query_params.get("session_id")
    if isinstance(raw, list):
        return raw[0] if raw else None
    return raw or None


def load_session_from_backend(session_id: str) -> dict | None:
    try:
        response = requests.get(f"{BACKEND_URL}/session/{session_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def save_session() -> None:
    try:
        requests.put(
            f"{BACKEND_URL}/session/{st.session_state.session_id}",
            json={
                "messages": st.session_state.messages,
                "search_count": st.session_state.get("search_count", 0),
            },
            timeout=5,
        )
    except requests.RequestException:
        pass


def init_session_state() -> None:
    if st.session_state.get("_session_initialized"):
        return

    query_id = _query_session_id()
    if query_id:
        st.session_state.session_id = query_id
    else:
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "search_count" not in st.session_state:
        st.session_state.search_count = 0

    stored = load_session_from_backend(st.session_state.session_id)
    if stored:
        st.session_state.messages = stored.get("messages", [])
        st.session_state.search_count = stored.get("search_count", 0)

    st.session_state._session_initialized = True


def start_new_session() -> None:
    try:
        requests.delete(
            f"{BACKEND_URL}/session/{st.session_state.session_id}",
            timeout=5,
        )
    except requests.RequestException:
        pass

    new_id = str(uuid.uuid4())
    st.session_state.session_id = new_id
    st.session_state.messages = []
    st.session_state.search_count = 0
    st.query_params["session_id"] = new_id
    st.session_state.pop("pending_prompt", None)
    st.session_state._session_initialized = True
