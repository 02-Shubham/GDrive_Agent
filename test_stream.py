import asyncio
from backend.agent.graph import build_agent_graph
from backend.tools.drive_tool import DriveSearchTool
from backend.tools.drive_read_tool import DriveReadFileTool
from langchain_core.messages import HumanMessage
import json

async def main():
    agent = build_agent_graph([DriveSearchTool(), DriveReadFileTool()])
    inputs = {"messages": [HumanMessage(content="find github invoice")]}
    config = {"configurable": {"thread_id": "test"}}
    async for event in agent.astream_events(inputs, config=config, version="v1"):
        if event["event"] == "on_tool_end":
            output = event["data"].get("output")
            print("on_tool_end output type:", type(output))
            print("on_tool_end output:", output)

asyncio.run(main())
