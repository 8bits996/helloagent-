"""
MCP Client 实现
实现一个 MCP Client,用于连接和调用 MCP Server

学习目标:
1. 理解 MCP Client 的连接管理
2. 掌握工具发现和调用
3. 理解响应处理
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """MCP Client 实现"""
    
    def __init__(self, server_script: str):
        """
        初始化 MCP Client
        
        Args:
            server_script: MCP Server 脚本路径
        """
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_script]
        )
        self.session = None
    
    async def connect(self):
        """连接到 MCP Server"""
        print(f"正在连接到 Server: {self.server_params.args[0]}")
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                
                # 初始化连接
                await session.initialize()
                print("✓ 连接成功")
                
                return session
    
    async def list_tools(self, session: ClientSession):
        """列出所有可用工具"""
        print("\n获取可用工具列表...")
        
        tools_result = await session.list_tools()
        tools = tools_result.tools
        
        print(f"\n可用工具 ({len(tools)} 个):")
        for i, tool in enumerate(tools, 1):
            print(f"\n{i}. {tool.name}")
            print(f"   描述: {tool.description}")
            print(f"   参数: {tool.inputSchema}")
        
        return tools
    
    async def call_tool(self, session: ClientSession, tool_name: str, arguments: dict):
        """调用工具"""
        print(f"\n调用工具: {tool_name}")
        print(f"参数: {arguments}")
        
        try:
            result = await session.call_tool(tool_name, arguments)
            print(f"\n结果:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(f"  {content.text}")
            return result
        except Exception as e:
            print(f"❌ 调用失败: {str(e)}")
            return None
    
    async def run_demo(self):
        """运行演示"""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化
                await session.initialize()
                print("✓ 已连接到 MCP Server\n")
                
                # 列出工具
                tools = await self.list_tools(session)
                
                # 测试工具
                print("\n" + "="*50)
                print("测试 1: Calculator 工具")
                print("="*50)
                await self.call_tool(
                    session,
                    "calculator",
                    {"expression": "2 + 2"}
                )
                
                await self.call_tool(
                    session,
                    "calculator",
                    {"expression": "10 * 5 + 3"}
                )
                
                print("\n" + "="*50)
                print("测试 2: Add 工具")
                print("="*50)
                await self.call_tool(
                    session,
                    "add",
                    {"a": 15, "b": 27}
                )
                
                print("\n" + "="*50)
                print("测试 3: Echo 工具")
                print("="*50)
                await self.call_tool(
                    session,
                    "echo",
                    {"message": "Hello MCP!"}
                )
                
                # 测试资源
                print("\n" + "="*50)
                print("测试 4: 读取资源")
                print("="*50)
                try:
                    from pydantic import AnyUrl
                    resources = await session.list_resources()
                    print(f"\n可用资源: {[r.uri for r in resources.resources]}")
                    
                    # 读取问候资源
                    resource_content = await session.read_resource(
                        AnyUrl("greeting://Alice")
                    )
                    from mcp import types
                    content_block = resource_content.contents[0]
                    if isinstance(content_block, types.TextContent):
                        print(f"\n资源内容: {content_block.text}")
                except Exception as e:
                    print(f"读取资源失败: {e}")
                
                # 测试提示词
                print("\n" + "="*50)
                print("测试 5: 获取提示词")
                print("="*50)
                try:
                    prompts = await session.list_prompts()
                    print(f"\n可用提示词: {[p.name for p in prompts.prompts]}")
                    
                    if prompts.prompts:
                        prompt = await session.get_prompt(
                            "math_helper",
                            arguments={"problem": "求解方程 2x + 5 = 15"}
                        )
                        print(f"\n提示词内容:")
                        print(prompt.messages[0].content.text)
                except Exception as e:
                    print(f"获取提示词失败: {e}")
                
                print("\n" + "="*50)
                print("演示完成!")
                print("="*50)


async def main():
    """主函数"""
    # 创建 Client
    client = MCPClient("mcp_server_basic.py")
    
    # 运行演示
    await client.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
