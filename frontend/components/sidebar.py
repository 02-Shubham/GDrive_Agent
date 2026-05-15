import streamlit as st

from frontend.persistence import start_new_session

QUICK_QUERIES = [
    ("Find all PDFs", "Find all PDFs in my Drive"),
    ("Recent documents", "Show me recent documents"),
    ("Search for report", "Find files containing report"),
]


def render_sidebar():
    with st.sidebar:
        st.title("GDrive Agent")
        st.caption("Conversational search for your Drive folder")

        st.markdown(
            f"""
            <div class="sidebar-meta">
                <div><strong>Session</strong> · <code>{st.session_state.session_id[:8]}…</code></div>
                <div><strong>Searches</strong> · {st.session_state.search_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("New conversation", use_container_width=True, type="primary"):
            start_new_session()
            st.rerun()

        st.divider()
        st.markdown("**Quick queries**")

        for label, query in QUICK_QUERIES:
            if st.button(label, use_container_width=True, key=f"quick_{label}"):
                st.session_state.pending_prompt = query
                st.rerun()
