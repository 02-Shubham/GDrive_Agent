import asyncio
from langchain_core.messages import HumanMessage
from backend.agent.graph import build_agent_graph
from backend.tools.drive_tool import DriveSearchTool

async def test():
    agent = build_agent_graph([DriveSearchTool()])
    inputs = {"messages": [HumanMessage(content="find all PDFs")], "session_id": "test"}
    config = {"configurable": {"thread_id": "test"}}
    async for event in agent.astream_events(inputs, config=config, version="v1"):
        print(event["event"], event["name"])

asyncio.run(test())
