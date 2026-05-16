import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.models.request import ChatRequest
from backend.models.session import SessionHistoryResponse, SessionHistoryUpdate
from backend.session import get_agent_for_session, clear_session_data
from backend.session_store import load_session_data, save_session_data
from backend.errors import friendly_llm_error
import json
from langchain_core.messages import HumanMessage
from datetime import datetime

SESSION_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _validate_session_id(session_id: str) -> str:
    if not SESSION_ID_RE.match(session_id):
        raise HTTPException(status_code=400, detail="Invalid session id")
    return session_id

app = FastAPI(title="GDrive Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/chat")
async def chat(request: ChatRequest):
    from backend.config import request_folder_id
    request_folder_id.set(request.folder_id)
    
    agent, config = get_agent_for_session(request.session_id)
    
    augmented_input = f"{request.message}\n\n(System Context: Current date and time is {datetime.now().isoformat()})"
    inputs = {"messages": [HumanMessage(content=augmented_input)], "session_id": request.session_id}

    if not request.stream:
        # Non-streaming response fallback
        res = await agent.ainvoke(inputs, config=config)
        return {"message": res["messages"][-1].content, "session_id": request.session_id}

    async def event_generator():
        try:
            async for event in agent.astream_events(inputs, config=config, version="v1"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                elif kind == "on_tool_start":
                    if event["name"] in ("drive_search", "drive_read_file"):
                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
                elif kind == "on_tool_end":
                    if event["name"] == "drive_search":
                        try:
                            output_obj = event["data"].get("output")
                            output_str = getattr(output_obj, "content", str(output_obj))
                            
                            if isinstance(output_str, str):
                                parsed = json.loads(output_str)
                                if isinstance(parsed, list):
                                    yield f"data: {json.dumps({'type': 'tool_end', 'results': parsed})}\n\n"
                        except Exception:
                            pass
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': friendly_llm_error(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/session/{session_id}", response_model=SessionHistoryResponse)
def get_session_history(session_id: str):
    session_id = _validate_session_id(session_id)
    data = load_session_data(session_id)
    if not data:
        return SessionHistoryResponse(session_id=session_id)
    return SessionHistoryResponse(
        session_id=session_id,
        messages=data.get("messages", []),
        search_count=data.get("search_count", 0),
    )


@app.put("/session/{session_id}", response_model=SessionHistoryResponse)
def save_session_history(session_id: str, body: SessionHistoryUpdate):
    session_id = _validate_session_id(session_id)
    payload = {
        "messages": body.messages,
        "search_count": body.search_count,
    }
    save_session_data(session_id, payload)
    return SessionHistoryResponse(session_id=session_id, **payload)


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    session_id = _validate_session_id(session_id)
    clear_session_data(session_id)
    return {"status": "cleared", "session_id": session_id}
