# GDrive Intelligence 🗂️

> Conversational AI agent for discovering files in Google Drive

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   - `GROQ_API_KEY`: Your Groq API key
   - `LLM_MODEL`: e.g., `llama-3.3-70b-versatile`
   - `GOOGLE_SA_JSON_B64`: Your Google Service Account JSON file, Base64-encoded
   - `DRIVE_FOLDER_ID`: The ID of the folder you want the agent to search in

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
