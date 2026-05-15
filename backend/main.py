from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.models.request import ChatRequest
from backend.session import get_agent_for_session, clear_session_data
import json
from langchain_core.messages import HumanMessage, AIMessageChunk
from datetime import datetime

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
                    if event["name"] == "drive_search":
                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
                elif kind == "on_tool_end":
                    if event["name"] == "drive_search":
                        try:
                            output_str = event["data"].get("output", "[]")
                            if isinstance(output_str, str):
                                parsed = json.loads(output_str)
                                if isinstance(parsed, list):
                                    yield f"data: {json.dumps({'type': 'tool_end', 'results': parsed})}\n\n"
                        except Exception:
                            pass
        except Exception as e:
            # Never drop the connection — send the error as a structured event
            yield f"data: {json.dumps({'type': 'error', 'content': f'Something went wrong: {str(e)}'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    clear_session_data(session_id)
    return {"status": "cleared", "session_id": session_id}
