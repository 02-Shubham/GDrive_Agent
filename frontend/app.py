import streamlit as st

from frontend.components.chat import render_chat_history, stream_and_append_assistant
from frontend.components.sidebar import render_sidebar
from frontend.persistence import init_session_state, save_session

st.set_page_config(
    page_title="GDrive Intelligence",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
    }

    /* —— Light main area —— */
    .stApp,
    [data-testid="stAppViewContainer"] > section.main {
        background: linear-gradient(180deg, #f7f8fc 0%, #f0f2f8 100%);
        color: #1a1d26;
    }

    section.main .block-container {
        padding-top: 1.5rem;
        max-width: 920px;
    }

    section.main p, section.main li, section.main span {
        color: #3d4454;
    }

    /* Streamlit top bar */
    [data-testid="stHeader"] {
        background: #ffffff !important;
        border-bottom: 1px solid #e8ebf2;
    }
    [data-testid="stHeader"] * {
        color: #1a1d26 !important;
    }

    .app-header {
        background: #ffffff;
        padding: 1rem 1.25rem 1.1rem;
        border: 1px solid #e8ebf2;
        border-radius: 12px;
        margin-top: 1.5rem;
        box-shadow: 0 1px 3px rgba(26, 29, 38, 0.05);
    }

    .app-header h2 {
        margin: 0;
        padding: 0 !important;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1a1d26 !important;
        letter-spacing: -0.02em;
    }

    .app-header p {
        margin: 0.35rem 0 0;
        font-size: 0.85rem;
        color: #3d4454 !important;
    }

    .hero { text-align: center; padding: 2.5rem 1rem 1.5rem; }
    .hero-eyebrow {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4f6ef7;
        margin: 0 0 0.5rem;
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1d26;
        margin: 0 0 0.5rem;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        color: #6b7289;
        font-size: 0.95rem;
        max-width: 420px;
        margin: 0 auto;
        line-height: 1.5;
    }

    .suggestions-label {
        text-align: center;
        color: #8b93a8;
        font-size: 0.8rem;
        margin: 1.5rem 0 0.5rem;
    }

    section.main .stButton > button {
        background: #ffffff !important;
        border: 1px solid #dde2ec !important;
        color: #3d4454 !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        box-shadow: 0 1px 2px rgba(26, 29, 38, 0.04) !important;
        transition: border-color 0.15s, box-shadow 0.15s !important;
    }
    section.main .stButton > button:hover {
        border-color: #4f6ef7 !important;
        color: #1a1d26 !important;
        box-shadow: 0 2px 8px rgba(79, 110, 247, 0.12) !important;
    }

    section.main [data-testid="stChatMessage"] {
        background: transparent !important;
        margin-top: 1.5rem;
        border: none !important;
    }

    section.main [data-testid="stChatMessageContent"] {
        background: #ffffff;
        border: 1px solid #e8ebf2;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        box-shadow: 0 1px 3px rgba(26, 29, 38, 0.04);
        color: #1a1d26;
        margin-bottom: 1.5rem;
    }

    section.main [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: #f0f4ff;
        border-color: #d4ddf8;
    }

    .status-pill {
        display: inline-block;
        font-size: 0.8rem;
        color: #6b7289;
        padding: 0.35rem 0.75rem;
        background: #f3f5fa;
        border-radius: 999px;
        border: 1px solid #e2e6ef;
    }
    .status-pill--search {
        color: #4f6ef7;
        background: #eef2ff;
        border-color: #c7d4fc;
    }

    .file-card {
        background: #ffffff;
        border: 1px solid #e2e6ef;
        border-radius: 12px;
        padding: 16px;
        margin: 6px 0;
        box-shadow: 0 1px 3px rgba(26, 29, 38, 0.05);
        transition: border-color 0.2s, box-shadow 0.15s, transform 0.15s;
    }
    .file-card:hover {
        border-color: #4f6ef7;
        box-shadow: 0 4px 12px rgba(79, 110, 247, 0.1);
        transform: translateY(-1px);
    }
    .file-card .file-name { font-weight: 600; margin: 10px 0 4px; font-size: 14px; color: #1a1d26; }
    .file-card .file-meta { color: #6b7289; font-size: 12px; }
    .file-card .file-link {
        color: #4f6ef7;
        text-decoration: none;
        font-size: 13px;
        font-weight: 500;
        display: inline-block;
        margin-top: 12px;
    }
    .file-type-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    section.main [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        border: 1px solid #dde2ec !important;
        border-radius: 12px !important;
        color: #1a1d26 !important;
        box-shadow: 0 1px 3px rgba(26, 29, 38, 0.04) !important;
    }
    section.main [data-testid="stChatInput"] textarea:focus {
        border-color: #4f6ef7 !important;
        box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.12) !important;
    }

    /* —— Subtle dark sidebar —— */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2a2f3d 0%, #252a36 100%) !important;
        border-right: 1px solid #353b4a;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    [data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f0f2f7 !important;
    }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #a8b0c4 !important;
    }

    [data-testid="stSidebar"] strong {
        color: #e2e6f0 !important;
    }

    [data-testid="stSidebar"] code {
        background: rgba(255, 255, 255, 0.08);
        color: #c8d0e4;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.78rem;
    }

    [data-testid="stSidebar"] hr {
        border-color: #3a4152;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid #3d4454 !important;
        color: #e2e6f0 !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: #5a6380 !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
        background: #4f6ef7 !important;
        border-color: #4f6ef7 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #3d5ce6 !important;
        border-color: #3d5ce6 !important;
    }

    [data-testid="stSidebar"] .sidebar-meta {
        font-size: 0.8rem;
        color: #9aa3b8;
        line-height: 1.7;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

init_session_state()

render_sidebar()

# st.markdown(
#     """
#     # <div class="app-header">
#     #     <h2>GDrive Intelligence</h2>
#     #     <p>Search your Drive folder with natural language</p>
#     # </div>
#     """,
#     unsafe_allow_html=True,
# )

prompt = st.chat_input("Ask about your files…")
if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

# Append user turn once, then render history, then stream assistant (single render path)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "files": []})
    save_session()

render_chat_history()

if prompt:
    stream_and_append_assistant(prompt)
