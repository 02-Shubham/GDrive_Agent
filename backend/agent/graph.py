from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from backend.agent.state import AgentState
from backend.agent.prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from backend.config import get_settings

def build_agent_graph(tools):
    settings = get_settings()
    llm = ChatGroq(model=settings.llm_model, api_key=settings.groq_api_key, temperature=0)
    
    llm_with_tools = llm.bind_tools(tools)
    
    def call_llm(state: AgentState):
        messages = state.get("messages", [])
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_use_tool(state: AgentState):
        messages = state.get("messages", [])
        last = messages[-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END
    
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("llm")
    graph.add_conditional_edges("llm", should_use_tool, {"tools": "tools", END: END})
    graph.add_edge("tools", "llm")
    
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
