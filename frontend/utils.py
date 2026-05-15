import streamlit as st
import requests
import json
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def handle_user_input(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt, "files": []})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        full_response = ""
        files_results = []
        
        try:
            with requests.post(
                f"{BACKEND_URL}/chat", 
                json={"message": prompt, "session_id": st.session_state.session_id, "stream": True}, 
                stream=True
            ) as r:
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str == "[DONE]":
                                break
                                
                            try:
                                event = json.loads(data_str)
                                event_type = event.get("type")
                                
                                if event_type == "token":
                                    full_response += event.get("content", "")
                                    message_placeholder.markdown(full_response + "▌")
                                elif event_type == "tool_start":
                                    status_placeholder.markdown("*(Searching Drive...)*")
                                    st.session_state.search_count += 1
                                elif event_type == "tool_end":
                                    files_results = event.get("results", [])
                                    status_placeholder.empty()
                                elif event_type == "error":
                                    full_response = event.get("content", "An error occurred.")
                                    status_placeholder.empty()
                            except json.JSONDecodeError:
                                pass
        except requests.exceptions.ConnectionError:
            full_response = "⚠️ Could not connect to the backend server. Is it running on port 8000?"
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response, "files": []})
            return
        except Exception:
            # Catch ChunkedEncodingError and any other network-level errors
            if not full_response:
                full_response = "⚠️ The connection was interrupted. Please try again."
            status_placeholder.empty()
            
        message_placeholder.markdown(full_response)
        
        if files_results:
            cols = st.columns(2)
            from frontend.components.file_card import render_file_card
            for i, f in enumerate(files_results):
                with cols[i % 2]:
                    render_file_card(f)
                    
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "files": files_results
        })
