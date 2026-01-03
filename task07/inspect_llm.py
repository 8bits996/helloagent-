
import sys
from pathlib import Path
# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hello_agents import HelloAgentsLLM

print("Methods of HelloAgentsLLM:")
print(dir(HelloAgentsLLM))

try:
    llm = HelloAgentsLLM(api_key="your_api_key_here")
    print("\nInstance methods:")
    print(dir(llm))
except Exception as e:
    print(f"\nInstantiation failed: {e}")
