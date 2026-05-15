# Changelog

All notable changes to GDrive Intelligence are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]
- Deployment to Railway and Streamlit Cloud (Milestone 7)

---

## [0.6.0] — 2026-05-14 — Streamlit Frontend

### Added
- Industry-grade chat UI with dark theme (`#0f1117` background)
- File result cards with type icons (📄 PDF, 📊 Sheet, 📝 Doc, 🖼️ Image), metadata, and Drive links
- Sidebar with session ID display, search count, quick-start query chips, and "New Conversation" button
- Empty state with 3 example query cards on first load
- Real-time streaming token display via Server-Sent Events
- `*(Searching Drive...)*` indicator while agent is processing
- 2-column file card grid layout
- Custom CSS for dark theme and card hover effects

### Fixed
- `ChunkedEncodingError` — backend streaming generator wrapped in `try/except/finally` to guarantee clean connection close
- Streamlit crash on network error — broad exception handler in `utils.py` shows friendly `⚠️` message
- Recursive folder search — removed `in parents` restriction so agent can find files inside subfolders

---

## [0.5.0] — 2026-05-14 — FastAPI Backend

### Added
- `/chat` POST endpoint with `StreamingResponse` for real-time token streaming (SSE)
- `/health` GET endpoint for uptime checks and Railway health probe
- `/session/{id}` DELETE endpoint for conversation reset
- CORS middleware configured for Streamlit cross-origin requests
- `session.py` wrapping LangGraph `MemorySaver` for per-session memory
- Pydantic `ChatRequest` model with validation (`min_length`, `max_length`)
- Pydantic `ChatResponse`, `FileResult` response models
- `astream_events` integration to emit `tool_start`, `tool_end`, and `token` SSE events

---

## [0.4.0] — 2026-05-14 — LangGraph Agent

### Added
- `AgentState` TypedDict with message history, session ID, last results, and search count
- `build_agent_graph()` — LangGraph `StateGraph` with `llm → conditional_edge → tools → llm` loop
- `MemorySaver` checkpointer for multi-turn conversation memory across requests
- System prompt in `prompts.py` with Google Drive `q` parameter guide and 4 few-shot examples
- Date injection — current datetime passed in every message for relative date resolution ("last week")
- `scripts/test_agent.py` for interactive terminal testing

---

## [0.3.0] — 2026-05-14 — DriveSearchTool

### Added
- `query_builder.py` with deterministic `q`-param builder supporting 6 filter types
- `MIME_TYPES` mapping for pdf, doc, sheet, slide, image, folder
- `DriveSearchTool` as a LangChain `BaseTool` with typed `DriveSearchInput` Pydantic schema
- `format_results()` to serialize Drive file dicts to JSON string for the LLM
- Graceful empty-result fallback: returns `"No files found matching your query."`
- `scripts/test_tool.py` with 8 query type coverage (name, pdf, sheets, fullText, date, exact, combined, images)

---

## [0.2.0] — 2026-05-14 — Google Drive API Integration

### Added
- `drive_tool.py` with service account authentication via Base64-encoded JSON env var
- `get_drive_service()` — builds authenticated Google Drive v3 client
- `list_files_raw()` — `files.list` call with fields projection (id, name, mimeType, modifiedTime, size, webViewLink, thumbnailLink)
- Recursive search support (no `in parents` restriction — searches all accessible subfolders)
- `scripts/test_drive_connection.py` for terminal verification of Drive connectivity

---

## [0.1.0] — 2026-05-14 — Project Scaffolding

### Added
- Full directory structure: `backend/`, `frontend/`, `scripts/`, `credentials/`
- `backend/config.py` using Pydantic `BaseSettings` with `@lru_cache` singleton
- `.env.example` with all required environment variable keys documented
- `.gitignore` covering `credentials/`, `.env`, `__pycache__`, `.DS_Store`, `.venv/`
- `backend/requirements.txt` with pinned versions
- `README.md` with setup instructions
- Virtual environment (`.venv`) with all dependencies installed
