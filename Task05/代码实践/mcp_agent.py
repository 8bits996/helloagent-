"""
MCP Agent 实现
将 MCP 工具集成到 ReAct Agent 中

学习目标:
1. 理解 MCP 与 Agent 的集成方案
2. 掌握工具适配和转换
3. 实现多 MCP Server 管理
"""

import asyncio
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载环境变量
load_dotenv()


class MCPAgent:
    """集成 MCP 的 ReAct Agent"""
    
    def __init__(self, llm_client: OpenAI, mcp_servers: List[Dict[str, Any]]):
        """
        初始化 MCP Agent
        
        Args:
            llm_client: OpenAI 客户端
            mcp_servers: MCP Server 配置列表
                [{"script": "server.py", "name": "server-name"}, ...]
        """
        self.llm = llm_client
        self.mcp_servers_config = mcp_servers
        self.tools = []
        self.sessions = []
    
    async def initialize(self):
        """初始化所有 MCP Server 连接"""
        print("正在连接 MCP Servers...")
        
        for server_config in self.mcp_servers_config:
            script = server_config["script"]
            name = server_config.get("name", script)
            
            print(f"  - 连接 {name}...")
            
            # 这里简化处理,实际应该保持连接
            # 在实际使用时需要重构为长连接管理
            params = StdioServerParameters(
                command="python",
                args=[script]
            )
            
            self.sessions.append({
                "name": name,
                "params": params
            })
        
        print("✓ 所有 MCP Servers 连接完成\n")
    
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """从所有 MCP Server 获取工具列表"""
        all_tools = []
        
        for session_config in self.sessions:
            params = session_config["params"]
            server_name = session_config["name"]
            
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tools_result = await session.list_tools()
                    for tool in tools_result.tools:
                        # 转换为 Agent 可用的格式
                        all_tools.append({
                            "server": server_name,
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                            "mcp_tool": tool
                        })
        
        return all_tools
    
    async def execute_tool(self, server_name: str, tool_name: str, arguments: dict) -> str:
        """
        执行 MCP 工具
        
        Args:
            server_name: Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        # 找到对应的 Server
        session_config = None
        for config in self.sessions:
            if config["name"] == server_name:
                session_config = config
                break
        
        if not session_config:
            return f"错误: 找不到 Server {server_name}"
        
        # 执行工具
        params = session_config["params"]
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                try:
                    result = await session.call_tool(tool_name, arguments)
                    # 提取文本结果
                    text_results = []
                    for content in result.content:
                        if hasattr(content, 'text'):
                            text_results.append(content.text)
                    return "\n".join(text_results)
                except Exception as e:
                    return f"工具执行错误: {str(e)}"
    
    def format_tools_for_llm(self, tools: List[Dict[str, Any]]) -> str:
        """将工具列表格式化为 LLM 可理解的描述"""
        tool_descriptions = []
        for tool in tools:
            desc = f"- {tool['name']} (来自 {tool['server']}): {tool['description']}"
            tool_descriptions.append(desc)
        return "\n".join(tool_descriptions)
    
    async def run(self, task: str, max_iterations: int = 5) -> str:
        """
        运行 Agent 完成任务
        
        Args:
            task: 任务描述
            max_iterations: 最大迭代次数
            
        Returns:
            任务结果
        """
        # 获取所有工具
        tools = await self.get_all_tools()
        tools_desc = self.format_tools_for_llm(tools)
        
        print(f"任务: {task}\n")
        print(f"可用工具:\n{tools_desc}\n")
        print("="*50)
        
        # ReAct 循环
        history = []
        for i in range(max_iterations):
            print(f"\n迭代 {i+1}:")
            
            # 构建提示词
            prompt = self._build_prompt(task, tools_desc, history)
            
            # LLM 推理
            response = self.llm.chat.completions.create(
                model=os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            thought_action = response.choices[0].message.content
            print(f"Thought & Action:\n{thought_action}")
            
            # 解析动作
            action = self._parse_action(thought_action)
            
            if action["type"] == "finish":
                print(f"\n✓ 任务完成!")
                return action["content"]
            
            elif action["type"] == "use_tool":
                # 执行工具
                server = action["server"]
                tool_name = action["tool"]
                args = action["arguments"]
                
                print(f"\n执行工具: {tool_name}")
                print(f"参数: {args}")
                
                observation = await self.execute_tool(server, tool_name, args)
                print(f"Observation: {observation}")
                
                history.append({
                    "thought_action": thought_action,
                    "observation": observation
                })
            
            else:
                print("无法解析动作,继续...")
        
        return "达到最大迭代次数,任务未完成"
    
    def _build_prompt(self, task: str, tools: str, history: List[Dict]) -> str:
        """构建 ReAct 提示词"""
        prompt = f"""你是一个智能助手,可以使用以下工具来完成任务:

{tools}

任务: {task}

请使用 ReAct (Reasoning + Acting) 模式思考和行动:
1. Thought: 思考当前应该做什么
2. Action: 选择一个工具并指定参数,格式: USE_TOOL: <server>:<tool_name> <arguments>
3. 如果任务完成,使用: FINISH: <最终答案>

"""
        
        # 添加历史
        if history:
            prompt += "\n之前的思考和行动:\n"
            for h in history:
                prompt += f"\n{h['thought_action']}\n"
                prompt += f"Observation: {h['observation']}\n"
        
        prompt += "\n现在请继续思考和行动:"
        return prompt
    
    def _parse_action(self, text: str) -> Dict[str, Any]:
        """解析 LLM 输出的动作"""
        if "FINISH:" in text:
            content = text.split("FINISH:", 1)[1].strip()
            return {"type": "finish", "content": content}
        
        elif "USE_TOOL:" in text:
            # 解析工具调用: USE_TOOL: server:tool_name {"arg": "value"}
            parts = text.split("USE_TOOL:", 1)[1].strip()
            
            # 简化解析(实际应该更robust)
            try:
                tool_part, args_part = parts.split(" ", 1)
                server, tool_name = tool_part.split(":", 1)
                
                # 简单解析参数(实际应该用JSON)
                import json
                arguments = json.loads(args_part)
                
                return {
                    "type": "use_tool",
                    "server": server,
                    "tool": tool_name,
                    "arguments": arguments
                }
            except:
                return {"type": "unknown"}
        
        return {"type": "unknown"}


async def main():
    """主函数"""
    # 创建 LLM 客户端
    llm_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    # 配置 MCP Servers
    mcp_servers = [
        {
            "script": "mcp_server_basic.py",
            "name": "basic-server"
        }
    ]
    
    # 创建 Agent
    agent = MCPAgent(llm_client, mcp_servers)
    
    # 初始化
    await agent.initialize()
    
    # 执行任务
    result = await agent.run("计算 (10 + 5) * 2 的结果")
    
    print(f"\n\n最终结果:\n{result}")


if __name__ == "__main__":
    asyncio.run(main())
