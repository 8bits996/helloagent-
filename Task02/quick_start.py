"""
Task02 - HelloAgents 框架快速体验
30秒快速开始代码
"""
from hello_agents import SimpleAgent, HelloAgentsLLM
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建LLM实例 - 框架自动检测provider
print("正在创建 LLM 实例...")
llm = HelloAgentsLLM()

# 创建SimpleAgent
print("正在创建 SimpleAgent...")
agent = SimpleAgent(
    name="AI助手",
    llm=llm,
    system_prompt="你是一个有用的AI助手"
)

# 基础对话
print("\n" + "="*50)
print("测试1: 基础对话")
print("="*50)
response = agent.run("你好!请介绍一下自己")
print(f"Agent回复: {response}")

# 添加工具功能(可选)
print("\n" + "="*50)
print("测试2: 使用计算器工具")
print("="*50)
from hello_agents.tools import CalculatorTool
calculator = CalculatorTool()

# 注意: 需要实现7.4.1的MySimpleAgent进行调用,后续章节会支持此类调用方式
# agent.add_tool(calculator)

# 现在可以使用工具了
response = agent.run("请帮我计算 2 + 3 * 4")
print(f"Agent回复: {response}")

# 查看对话历史
print("\n" + "="*50)
print("对话历史")
print("="*50)
print(f"历史消息数: {len(agent.get_history())}")
for i, msg in enumerate(agent.get_history()):
    # Message是Pydantic模型,使用属性访问而不是get()
    role = msg.role if hasattr(msg, 'role') else 'unknown'
    content = msg.content if hasattr(msg, 'content') else ''
    content_preview = content[:50] if len(content) > 50 else content
    print(f"消息 {i+1}: role={role}, content={content_preview}...")
