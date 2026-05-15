import streamlit as st

from frontend.components.file_card import render_file_card
from frontend.persistence import save_session
from frontend.utils import iter_chat_events

SUGGESTIONS = [
    "Find all PDFs in my Drive",
    "Show me recent spreadsheets",
    "Search for files named budget",
]


def _render_message(msg: dict) -> None:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        files = msg.get("files") or []
        if files:
            cols = st.columns(2)
            for i, file in enumerate(files):
                with cols[i % 2]:
                    render_file_card(file)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="hero">
            <p class="hero-eyebrow">Google Drive Agent</p>
            <h1 class="hero-title">Find anything in your Drive</h1>
            <p class="hero-subtitle">
                Ask in plain language — the agent searches your folder and surfaces matching files.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<p class="suggestions-label">Try asking</p>', unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTIONS))
    for col, suggestion in zip(cols, SUGGESTIONS):
        with col:
            if st.button(suggestion, use_container_width=True, key=f"suggest_{suggestion[:20]}"):
                st.session_state.pending_prompt = suggestion


def render_chat_history() -> None:
    if not st.session_state.messages:
        render_empty_state()
        return

    for msg in st.session_state.messages:
        _render_message(msg)


def stream_and_append_assistant(prompt: str) -> None:
    """Stream one assistant reply and append it to session history."""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        files_slot = st.empty()

        status_placeholder.markdown(
            '<span class="status-pill">Thinking…</span>',
            unsafe_allow_html=True,
        )

        full_response = ""
        files_results: list = []
        searches = 0

        for event in iter_chat_events(prompt, st.session_state.session_id):
            event_type = event.get("type")
            if event_type == "token":
                full_response += event.get("content", "")
                message_placeholder.markdown(full_response + "▌")
                status_placeholder.empty()
            elif event_type == "tool_start":
                searches += 1
                tool = event.get("tool", "drive_search")
                label = (
                    "Reading file…"
                    if tool == "drive_read_file"
                    else "Searching Drive…"
                )
                status_placeholder.markdown(
                    f'<span class="status-pill status-pill--search">{label}</span>',
                    unsafe_allow_html=True,
                )
            elif event_type == "tool_end":
                files_results = event.get("results", [])
                status_placeholder.empty()
            elif event_type == "error":
                full_response = event.get("content", "")
                status_placeholder.empty()

        message_placeholder.markdown(full_response or "I couldn't generate a response.")
        status_placeholder.empty()

        if files_results:
            with files_slot.container():
                cols = st.columns(2)
                for i, file in enumerate(files_results):
                    with cols[i % 2]:
                        render_file_card(file)

        if searches:
            st.session_state.search_count = st.session_state.get("search_count", 0) + searches

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "files": files_results,
            }
        )

        save_session()
