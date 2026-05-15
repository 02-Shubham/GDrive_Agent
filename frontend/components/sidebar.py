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
                
        st.divider()
        st.markdown("### 🗂️ Search Location")

        use_custom = st.toggle("Use custom folder", value=False)

        if use_custom:
            url = st.text_input(
                "Drive folder URL",
                placeholder="https://drive.google.com/drive/folders/..."
            )
            if url:
                from frontend.utils import extract_folder_id
                fid = extract_folder_id(url)
                if fid:
                    st.session_state["folder_id"] = fid
                    st.success("✅ Folder connected")
                    st.caption(f"`{fid[:24]}...`")
                else:
                    st.session_state["folder_id"] = None
                    st.error("❌ Paste a valid Drive folder URL")
            else:
                st.session_state["folder_id"] = None
                
            st.markdown("""
            ---
            ### 📌 How to search your own folder

            **Step 1 — Get your folder URL**
            Open your Google Drive folder in browser and copy the URL from the address bar.
            Looks like: `drive.google.com/drive/folders/XXXXXX`

            **Step 2 — Enable custom folder**
            Toggle ON "Custom folder" above and paste your URL.

            **Step 3 — Share with service account** *(one-time)*
            If you see ❌ Access Denied, share your folder with:
            """)
            
            from backend.config import get_settings
            settings = get_settings()
            st.code(settings.google_sa_email, language=None)

            st.markdown("""
            Give it **Viewer** access. Takes 10 seconds.

            **Step 4 — Start searching**
            Type naturally in the chat. Examples:

            | What you want | What to type |
            |---|---|
            | Find by name | *"find the budget file"* |
            | Find by type | *"show all PDFs"* |
            | Search inside files | *"files mentioning revenue"* |
            | Filter by date | *"files from last week"* |
            | Combine filters | *"PDFs about Q3 from last month"* |

            ---
            *Default folder is always available as fallback.*
            """)
        else:
            # toggle OFF — clear any custom folder, use default
            st.session_state["folder_id"] = None
            st.caption("Using default folder")
