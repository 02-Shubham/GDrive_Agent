import streamlit as st
from datetime import datetime

FILE_TYPE_CONFIG = {
    "application/pdf": {"icon": "📄", "label": "PDF", "color": "#ff6b6b"},
    "application/vnd.google-apps.document": {"icon": "📝", "label": "Doc", "color": "#74b9ff"},
    "application/vnd.google-apps.spreadsheet": {"icon": "📊", "label": "Sheet", "color": "#55efc4"},
    "application/vnd.google-apps.presentation": {"icon": "🎞️", "label": "Slides", "color": "#fdcb6e"},
    "image/jpeg": {"icon": "🖼️", "label": "Image", "color": "#a29bfe"},
    "image/png": {"icon": "🖼️", "label": "Image", "color": "#a29bfe"},
    "application/vnd.google-apps.folder": {"icon": "📁", "label": "Folder", "color": "#fdcb6e"}
}

def format_date(date_str):
    if not date_str: return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str

def render_file_card(file: dict):
    mime = file.get("mimeType", "")
    config = FILE_TYPE_CONFIG.get(mime, {"icon": "📁", "label": "File", "color": "#dfe6e9"})
    
    html = f"""
    <div class="file-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:24px">{config['icon']}</span>
            <span class="file-type-badge" style="background:{config['color']}22; color:{config['color']}">
                {config['label']}
            </span>
        </div>
        <div style="font-weight:600; margin:8px 0 4px; font-size:14px; color: #fff;">{file.get('name', 'Unnamed')}</div>
        <div style="color:#888; font-size:12px">Modified: {format_date(file.get('modifiedTime'))}</div>
        <a href="{file.get('webViewLink','#')}" target="_blank" style="color: #4f6ef7; text-decoration: none; font-size: 13px; font-weight: 500; display: inline-block; margin-top: 12px;">Open in Drive &rarr;</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
