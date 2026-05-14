import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="GDrive Intelligence",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat_messages
from frontend.utils import handle_user_input

CUSTOM_CSS = """
<style>
    .stApp { background-color: #0f1117; }
    .file-card {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: border-color 0.2s;
    }
    .file-card:hover { border-color: #4f6ef7; }
    .file-type-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

render_sidebar()
render_chat_messages()

prompt = st.chat_input("Ask about your files...")
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    handle_user_input(prompt)
