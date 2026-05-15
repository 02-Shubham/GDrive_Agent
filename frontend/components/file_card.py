import streamlit as st
from datetime import datetime

FILE_TYPE_CONFIG = {
    "application/pdf": {"icon": "📄", "label": "PDF", "color": "#ff6b6b"},
    "application/vnd.google-apps.document": {"icon": "📝", "label": "Doc", "color": "#74b9ff"},
    "application/vnd.google-apps.spreadsheet": {"icon": "📊", "label": "Sheet", "color": "#55efc4"},
    "application/vnd.google-apps.presentation": {"icon": "🎞️", "label": "Slides", "color": "#fdcb6e"},
    "image/jpeg": {"icon": "🖼️", "label": "Image", "color": "#a29bfe"},
    "image/png": {"icon": "🖼️", "label": "Image", "color": "#a29bfe"},
    "application/vnd.google-apps.folder": {"icon": "📁", "label": "Folder", "color": "#fdcb6e"},
}


def format_date(date_str):
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str


def render_file_card(file: dict):
    mime = file.get("mimeType", "")
    config = FILE_TYPE_CONFIG.get(mime, {"icon": "📁", "label": "File", "color": "#dfe6e9"})
    name = file.get("name", "Unnamed")
    link = file.get("webViewLink", "#")

    html = f"""
    <div class="file-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:22px">{config['icon']}</span>
            <span class="file-type-badge" style="background:{config['color']}22; color:{config['color']}">
                {config['label']}
            </span>
        </div>
        <div class="file-name">{name}</div>
        <div class="file-meta">Modified {format_date(file.get('modifiedTime'))}</div>
        <a href="{link}" target="_blank" rel="noopener" class="file-link">Open in Drive →</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
