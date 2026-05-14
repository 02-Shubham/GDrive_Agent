import sys
sys.path.insert(0, ".")
from backend.agent.graph import build_agent_graph
from backend.tools.drive_tool import DriveSearchTool
from langchain_core.messages import HumanMessage
from datetime import datetime

def main():
    tools = [DriveSearchTool()]
    agent = build_agent_graph(tools)
    
    print("Welcome to GDrive Intelligence Agent (Terminal Test)")
    print("Type 'quit' to exit.")
    
    thread_id = "test_thread"
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        augmented_input = f"{user_input}\n\n(System Context: Current date and time is {datetime.now().isoformat()})"
        inputs = {"messages": [HumanMessage(content=augmented_input)], "session_id": thread_id}
        
        for event in agent.stream(inputs, config=config, stream_mode="values"):
            message = event["messages"][-1]
            if isinstance(message, HumanMessage):
                continue
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    print(f"  [Tool Call]: {tc['name']}({tc['args']})")
            elif message.content:
                print(f"Agent: {message.content}")

if __name__ == "__main__":
    main()
