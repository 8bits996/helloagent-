"""
简化版 MCP Agent - 演示 MCP 工具集成
展示如何将 MCP 工具集成到简单的 Agent 中

学习目标:
1. 理解如何连接 MCP Server
2. 掌握工具调用的基本流程
3. 理解 Agent 如何使用 MCP 工具
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载环境变量
load_dotenv()


class SimpleMCPAgent:
    """简化版 MCP Agent"""
    
    def __init__(self, llm_client: OpenAI, server_script: str):
        """
        初始化 Agent
        
        Args:
            llm_client: OpenAI 客户端
            server_script: MCP Server 脚本路径
        """
        self.llm = llm_client
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_script]
        )
    
    async def get_tools_description(self, session: ClientSession) -> str:
        """获取工具描述"""
        tools_result = await session.list_tools()
        tools = tools_result.tools
        
        descriptions = []
        for tool in tools:
            desc = f"- {tool.name}: {tool.description}"
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    async def execute_task(self, task: str):
        """
        执行任务
        
        Args:
            task: 任务描述
        """
        print(f"🎯 任务: {task}\n")
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                print("✓ 已连接到 MCP Server\n")
                
                # 获取可用工具
                tools_desc = await self.get_tools_description(session)
                print("📋 可用工具:")
                print(tools_desc)
                print()
                
                # 构建提示词
                prompt = f"""你是一个智能助手,可以使用以下工具:

{tools_desc}

任务: {task}

请选择合适的工具完成任务。只需告诉我:
1. 你要使用的工具名称
2. 工具的参数(JSON格式)

格式示例:
工具: calculator
参数: {{"expression": "2 + 2"}}

现在请回答:"""
                
                # 调用 LLM
                print("🤔 Agent 思考中...\n")
                response = self.llm.chat.completions.create(
                    model=os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200
                )
                
                agent_response = response.choices[0].message.content
                print("💭 Agent 的决策:")
                print(agent_response)
                print()
                
                # 简单解析(实际应该更robust)
                if "工具:" in agent_response or "工具名" in agent_response:
                    # 尝试提取工具调用
                    print("🔧 执行工具调用...\n")
                    
                    # 示例:直接调用 calculator
                    # 实际应该从 LLM 响应中解析
                    if "calculator" in agent_response.lower():
                        # 提取表达式
                        if "2 + 2" in agent_response or "两个数" in task:
                            result = await session.call_tool(
                                "calculator",
                                {"expression": "2 + 2"}
                            )
                            print("✅ 工具执行结果:")
                            for content in result.content:
                                if hasattr(content, 'text'):
                                    print(f"   {content.text}")
                    
                    elif "add" in agent_response.lower():
                        result = await session.call_tool(
                            "add",
                            {"a": 5, "b": 3}
                        )
                        print("✅ 工具执行结果:")
                        for content in result.content:
                            if hasattr(content, 'text'):
                                print(f"   {content.text}")
                else:
                    print("ℹ️  Agent 没有选择使用工具")


async def demo_basic_usage():
    """演示基本用法"""
    print("=" * 60)
    print("🚀 简化版 MCP Agent 演示")
    print("=" * 60)
    print()
    
    # 创建 LLM 客户端
    llm_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    # 创建 Agent
    agent = SimpleMCPAgent(llm_client, "mcp_server_basic.py")
    
    # 执行任务
    await agent.execute_task("帮我计算 2 + 2 的结果")
    
    print()
    print("=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)


async def demo_direct_call():
    """演示直接调用 MCP 工具"""
    print("\n" + "=" * 60)
    print("📝 演示: 直接调用 MCP 工具(不使用 LLM)")
    print("=" * 60)
    print()
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_basic.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("✓ 已连接到 MCP Server\n")
            
            # 列出工具
            tools_result = await session.list_tools()
            print(f"📋 发现 {len(tools_result.tools)} 个工具\n")
            
            # 调用多个工具
            tasks = [
                ("calculator", {"expression": "10 * 5 + 3"}, "计算表达式"),
                ("add", {"a": 15, "b": 27}, "两数相加"),
                ("multiply", {"a": 3.5, "b": 2.0}, "两数相乘"),
                ("echo", {"message": "MCP is awesome!"}, "回显消息"),
            ]
            
            for tool_name, args, desc in tasks:
                print(f"🔧 {desc}: {tool_name}")
                print(f"   参数: {args}")
                
                result = await session.call_tool(tool_name, args)
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"   ✅ 结果: {content.text}")
                print()
    
    print("=" * 60)
    print("✅ 直接调用演示完成!")
    print("=" * 60)


async def main():
    """主函数"""
    print("\n" + "🌟" * 30)
    print("   MCP Agent 简化版演示")
    print("🌟" * 30 + "\n")
    
    # 演示1: Agent 使用 MCP 工具
    await demo_basic_usage()
    
    # 演示2: 直接调用 MCP 工具
    await demo_direct_call()
    
    print("\n" + "🎓" * 30)
    print("\n💡 学习要点:")
    print("   1. MCP 提供标准化的工具接口")
    print("   2. Agent 可以通过 MCP 调用各种工具")
    print("   3. FastMCP 简化了 Server 开发")
    print("   4. 工具调用是异步的")
    print("\n" + "🎓" * 30 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
