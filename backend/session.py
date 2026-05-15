from backend.agent.graph import build_agent_graph
from backend.session_store import delete_session_data
from backend.tools.drive_read_tool import DriveReadFileTool
from backend.tools.drive_tool import DriveSearchTool

_tools = [DriveSearchTool(), DriveReadFileTool()]
_agent = build_agent_graph(_tools)


def get_agent_for_session(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    return _agent, config


def clear_session_data(session_id: str) -> None:
    delete_session_data(session_id)
