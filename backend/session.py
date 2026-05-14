from backend.agent.graph import build_agent_graph
from backend.tools.drive_tool import DriveSearchTool

_tools = [DriveSearchTool()]
_agent = build_agent_graph(_tools)

def get_agent_for_session(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    return _agent, config

def clear_session_data(session_id: str):
    # LangGraph MemorySaver retains checkpoints in memory
    # Since it's internal to langgraph, we could re-instantiate or just let it be.
    pass
