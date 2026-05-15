import json

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

from backend.agent.prompts import build_system_prompt
from backend.agent.state import AgentState
from backend.config import get_settings


def _parse_search_results(content: str) -> list[dict]:
    if not content or content.startswith("No files found") or content.startswith("Drive API error"):
        return []
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


def build_agent_graph(tools):
    settings = get_settings()
    llm = ChatGroq(model=settings.llm_model, api_key=settings.groq_api_key, temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    def call_llm(state: AgentState):
        messages = state.get("messages", [])
        last_results = state.get("last_results") or []
        system = build_system_prompt(last_results)
        non_system = [m for m in messages if not isinstance(m, SystemMessage)]
        messages = [SystemMessage(content=system)] + non_system
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def run_tools(state: AgentState):
        result = tool_node.invoke(state)
        new_messages = result.get("messages", [])
        last_results = list(state.get("last_results") or [])

        for msg in new_messages:
            if not isinstance(msg, ToolMessage):
                continue
            if msg.name == "drive_search":
                parsed = _parse_search_results(msg.content)
                if parsed:
                    last_results = parsed

        return {"messages": new_messages, "last_results": last_results}

    def should_use_tool(state: AgentState):
        messages = state.get("messages", [])
        last = messages[-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tools", run_tools)
    graph.set_entry_point("llm")
    graph.add_conditional_edges("llm", should_use_tool, {"tools": "tools", END: END})
    graph.add_edge("tools", "llm")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
