# 🗂️ GDrive Intelligence Agent

GDrive Intelligence is a production-grade, conversational AI agent that enables natural language searching, analyzing, and reasoning over your Google Drive files. Powered by **FastAPI**, **LangGraph**, and **Streamlit**, this intelligent assistant bridges the gap between semantic conversation and secure document retrieval.

## ✨ Why This Tool Stands Out

While standard Google Drive search relies on rigid keyword matching, GDrive Intelligence offers a fundamentally superior experience:

1. **Dynamic Custom Folder Scoping:** 
   Instead of being locked into a single workspace, users can seamlessly switch contexts. By simply pasting a Google Drive folder URL in the sidebar, the backend dynamically extracts the ID, instantly scoping all subsequent LLM searches and reads to that specific folder (and its recursive subfolders).
   
2. **Contextual Conversational Memory:** 
   This isn't a simple QA bot. Using **LangGraph's state management**, the agent maintains session history. You can ask *"Find my GitHub invoice"*, receive the file, and then follow up with *"Can you summarize it?"* or *"What was the total amount?"* without needing to re-specify what you're talking about.

3. **Rich UI with Actionable Direct Links:** 
   When the agent finds your files, it doesn't just return raw text. It streams structured tool outputs via SSE (Server-Sent Events) to a beautiful Streamlit frontend, generating interactive **File Cards**. These cards display metadata (icons, types, modified dates) and provide a direct *"Open in Drive →"* link so you can immediately access your document.

4. **Deep File Reading Capabilities:** 
   The agent doesn't just look at file names. It is equipped with a `drive_read_file` tool capable of downloading and extracting text from PDFs, Google Docs, Sheets, Slides, and plaintext files directly into the LLM's context window for deep summarization and analysis.

---

## 🏗️ Technical Approach & Architecture

### Backend Architecture (FastAPI & LangGraph)
The backend is engineered for scalability and robust state management:
* **LLM Engine:** Powered by Groq (`llama-3.3-70b-versatile`) for lightning-fast inference and reliable tool-calling.
* **Agent Graph:** Built using `LangGraph`, featuring a `StateGraph` that loops between the LLM node and a `ToolNode`. 
* **Tool Calling:**
  * `drive_search`: Translates natural language into optimized Google Drive API `q` parameters. It uses a recursive BFS caching mechanism to safely scope searches strictly to the authorized folder tree.
  * `drive_read_file`: Safely exports and reads file bytes (handling up to 8MB) and parses PDFs using `pypdf`.
* **Streaming Responses:** Exposes an asynchronous `/chat` endpoint using FastAPI `StreamingResponse`. It streams LangGraph `astream_events`, delivering real-time tokens and tool execution states (like "Searching Drive...") directly to the client.

### Frontend Architecture (Streamlit)
* **Custom Styling:** Heavy CSS customization overriding default Streamlit constraints to provide a rich, modern, glass-morphic feel.
* **Event Parsing:** A custom `iter_chat_events` generator parses the Server-Sent Events (SSE) stream, allowing the UI to dynamically show "Thinking...", render file cards immediately upon `on_tool_end`, and seamlessly append text tokens.
* **Session Persistence:** Maintains local session IDs and chat history logic to keep the user experience smooth across reloads.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google Cloud Service Account JSON key (with Drive Read permissions)
- A Groq API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd gdrive_agent
   ```

2. **Set up the environment:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_key
   GOOGLE_SA_JSON_B64=base64_encoded_service_account_json
   DRIVE_FOLDER_ID=default_root_folder_id
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   pip install streamlit requests
   ```

### Running the Application

You need two terminal windows to run the frontend and backend concurrently.

**1. Start the Backend:**
Navigate to the root directory and start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**2. Start the Frontend:**
In a new terminal window, run the Streamlit app:
```bash
python -m streamlit run frontend/app.py
```

Navigate to `http://localhost:8501` to start chatting with your Drive!

---

## 🔒 Security & Privacy

* **Strict Scoping:** The Drive API integration strictly enforces folder boundaries. It computes valid parent IDs recursively to ensure the agent cannot access files outside the user-defined root.
* **Read-Only Access:** The application requires only the `https://www.googleapis.com/auth/drive.readonly` scope, ensuring your Drive files cannot be accidentally modified or deleted by the AI.

## 🤝 Future Enhancements
- Support for extracting data from images using OCR.
- Integration with Google Workspace OAuth for multi-tenant, user-level authentication.
- Implementing an advanced RAG (Retrieval-Augmented Generation) pipeline for semantic similarity search over large document corpora.
