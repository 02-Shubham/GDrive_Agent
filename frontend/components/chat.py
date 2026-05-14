import streamlit as st
from frontend.components.file_card import render_file_card

def render_chat_messages():
    if not st.session_state.messages:
        # Empty state
        st.markdown("<h3 style='text-align: center; margin-top: 2rem;'>Welcome to GDrive Intelligence 🗂️</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Ask me to find anything in your Drive.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("Find all PDFs")
        with col2:
            st.info("Show me recent spreadsheets")
        with col3:
            st.info("Search for 'budget' in docs")
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "files" in msg and msg["files"]:
                cols = st.columns(2)
                for i, f in enumerate(msg["files"]):
                    with cols[i % 2]:
                        render_file_card(f)
