
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Mock HelloAgentsLLM before importing UniversalAgent
import hello_agents

class MockResponse:
    def __init__(self, content):
        self.content = content

class MockLLM:
    def __init__(self, *args, **kwargs):
        print("MockLLM initialized.")
    
    def invoke(self, messages, tools=None, **kwargs):
        print(f"\n[MockLLM] Received messages: {messages}")
        last_msg = messages[-1]['content'] if isinstance(messages, list) else str(messages)
        
        if "pwd" in last_msg.lower():
            response_text = "[TOOL_CALL:terminal_exec:pwd]"
        elif "search" in last_msg.lower():
            response_text = "[TOOL_CALL:browser_search:Python news]"
        else:
            response_text = "I am a mock agent. I can help you run commands or search."
            
        print(f"[MockLLM] Returning: {response_text}")
        return response_text

# Patch the class
hello_agents.HelloAgentsLLM = MockLLM

from src.agents.agent_universal import UniversalAgent

def main():
    print("🤖 Starting Mock UniversalAgent...")
    print("Note: This is a simulation without the real LLM.")
    print("Supported commands for mock: 'pwd', 'search ...'")
    
    try:
        agent = UniversalAgent()
        
        while True:
            try:
                user_input = input("\n请输入您的问题 (输入 'exit' 退出): ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ["exit", "quit"]:
                    print("\n👋 再见！")
                    break
                    
                response = agent.run(user_input)
                print(f"\nAI >\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except EOFError:
                break
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
