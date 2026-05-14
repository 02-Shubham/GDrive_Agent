import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def render_sidebar():
    with st.sidebar:
        st.title("🗂️ GDrive Agent")
        st.markdown(f"**Session ID**: `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**Searches Performed**: `{st.session_state.search_count}`")
        
        if st.button("New Conversation", use_container_width=True):
            try:
                requests.delete(f"{BACKEND_URL}/session/{st.session_state.session_id}")
            except:
                pass
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.search_count = 0
            st.rerun()

        st.markdown("---")
        st.markdown("### Quick Queries")
        
        if st.button("Find all PDFs", use_container_width=True):
            st.session_state.pending_prompt = "Find all PDFs"
            
        if st.button("Recent documents", use_container_width=True):
            st.session_state.pending_prompt = "Show me recent documents"
            
        if st.button("Search for 'report'", use_container_width=True):
            st.session_state.pending_prompt = "Find files containing 'report'"
