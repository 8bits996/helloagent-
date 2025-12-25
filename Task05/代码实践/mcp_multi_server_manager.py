"""
多 MCP Server 管理器
统一管理多个 MCP Server,提供工具发现和路由

核心功能:
1. 连接和管理多个 MCP Server
2. 统一的工具发现
3. 自动工具路由
4. 错误处理和重试
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool


@dataclass
class ServerConfig:
    """Server 配置"""
    name: str
    command: str
    args: List[str]
    description: str = ""


class MultiServerManager:
    """多 Server 管理器"""
    
    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tool_map: Dict[str, str] = {}  # tool_name -> server_name
        
    async def connect_server(self, config: ServerConfig) -> bool:
        """
        连接到一个 MCP Server
        
        Args:
            config: Server 配置
            
        Returns:
            是否连接成功
        """
        try:
            print(f"🔌 连接到 {config.name}...")
            
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args
            )
            
            # 创建 stdio 客户端
            read, write = await stdio_client(server_params).__aenter__()
            
            # 创建会话
            session = await ClientSession(read, write).__aenter__()
            
            # 初始化
            await session.initialize()
            
            # 获取工具列表
            tools_response = await session.list_tools()
            tools = tools_response.tools
            
            # 保存 Server 信息
            self.servers[config.name] = {
                'config': config,
                'session': session,
                'tools': tools,
                'read': read,
                'write': write
            }
            
            # 更新工具映射
            for tool in tools:
                self.tool_map[tool.name] = config.name
            
            print(f"✅ {config.name} 连接成功! 发现 {len(tools)} 个工具")
            return True
            
        except Exception as e:
            print(f"❌ {config.name} 连接失败: {e}")
            return False
    
    async def connect_all(self, configs: List[ServerConfig]):
        """
        连接所有 Server
        
        Args:
            configs: Server 配置列表
        """
        print("=" * 80)
        print("🚀 多 Server 管理器启动")
        print("=" * 80)
        print()
        
        for config in configs:
            await self.connect_server(config)
            print()
        
        print(f"📊 总结: 成功连接 {len(self.servers)} 个 Server")
        print(f"🔧 总工具数: {len(self.tool_map)}")
        print()
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        获取所有工具列表
        
        Returns:
            工具列表
        """
        all_tools = []
        for server_name, server_info in self.servers.items():
            for tool in server_info['tools']:
                all_tools.append({
                    'name': tool.name,
                    'description': tool.description,
                    'server': server_name,
                    'schema': tool.inputSchema
                })
        return all_tools
    
    def find_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        查找工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具信息或 None
        """
        if tool_name not in self.tool_map:
            return None
        
        server_name = self.tool_map[tool_name]
        server_info = self.servers[server_name]
        
        for tool in server_info['tools']:
            if tool.name == tool_name:
                return {
                    'name': tool.name,
                    'description': tool.description,
                    'server': server_name,
                    'schema': tool.inputSchema
                }
        return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        调用工具(自动路由到正确的 Server)
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            # 查找工具所属的 Server
            if tool_name not in self.tool_map:
                return f"❌ 工具 '{tool_name}' 不存在"
            
            server_name = self.tool_map[tool_name]
            session = self.servers[server_name]['session']
            
            # 调用工具
            result = await session.call_tool(tool_name, arguments)
            
            # 提取文本内容
            if result.content:
                return result.content[0].text
            return "✅ 工具执行成功(无返回内容)"
            
        except Exception as e:
            return f"❌ 工具调用失败: {str(e)}"
    
    def list_servers(self) -> List[Dict[str, Any]]:
        """
        列出所有 Server
        
        Returns:
            Server 列表
        """
        servers = []
        for name, info in self.servers.items():
            servers.append({
                'name': name,
                'description': info['config'].description,
                'tool_count': len(info['tools']),
                'tools': [t.name for t in info['tools']]
            })
        return servers
    
    def print_summary(self):
        """打印摘要信息"""
        print("=" * 80)
        print("📋 多 Server 管理器摘要")
        print("=" * 80)
        print()
        
        # Server 列表
        print(f"🖥️  已连接 Server: {len(self.servers)}")
        for server in self.list_servers():
            print(f"\n  📦 {server['name']}")
            print(f"     描述: {server['description']}")
            print(f"     工具数: {server['tool_count']}")
            print(f"     工具列表:")
            for tool_name in server['tools']:
                print(f"       - {tool_name}")
        
        print()
        print(f"🔧 总工具数: {len(self.tool_map)}")
        print()
    
    async def close(self):
        """关闭所有连接"""
        print("\n🔌 关闭所有 Server 连接...")
        for server_name in self.servers:
            try:
                # 这里可以添加清理逻辑
                print(f"  ✓ {server_name} 已关闭")
            except Exception as e:
                print(f"  ✗ {server_name} 关闭失败: {e}")


class ToolRouter:
    """工具路由器 - 智能选择合适的工具"""
    
    def __init__(self, manager: MultiServerManager):
        self.manager = manager
    
    def suggest_tools(self, task_description: str) -> List[Dict[str, Any]]:
        """
        根据任务描述推荐工具
        
        Args:
            task_description: 任务描述
            
        Returns:
            推荐的工具列表
        """
        all_tools = self.manager.get_all_tools()
        suggestions = []
        
        # 简单的关键词匹配
        keywords = task_description.lower().split()
        
        for tool in all_tools:
            tool_text = (tool['name'] + ' ' + tool['description']).lower()
            score = sum(1 for keyword in keywords if keyword in tool_text)
            
            if score > 0:
                suggestions.append({
                    **tool,
                    'relevance_score': score
                })
        
        # 按相关性排序
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return suggestions


# 使用示例
async def example_usage():
    """使用示例"""
    
    # 创建管理器
    manager = MultiServerManager()
    
    # 配置多个 Server
    configs = [
        ServerConfig(
            name="file-server",
            command="python",
            args=["mcp_server_file.py"],
            description="文件操作服务器"
        ),
        ServerConfig(
            name="data-server",
            command="python",
            args=["mcp_server_data.py"],
            description="数据分析服务器"
        )
    ]
    
    # 连接所有 Server
    await manager.connect_all(configs)
    
    # 打印摘要
    manager.print_summary()
    
    # 测试工具调用
    print("=" * 80)
    print("🧪 测试工具调用")
    print("=" * 80)
    print()
    
    # 1. 写入文件
    print("1️⃣ 测试文件写入...")
    result = await manager.call_tool(
        "write_file",
        {
            "file_path": "test_output.txt",
            "content": "Hello from Multi-Server Manager!\nThis is a test file."
        }
    )
    print(result)
    print()
    
    # 2. 读取文件
    print("2️⃣ 测试文件读取...")
    result = await manager.call_tool(
        "read_file",
        {"file_path": "test_output.txt"}
    )
    print(result)
    print()
    
    # 3. 分析文本
    print("3️⃣ 测试文本分析...")
    result = await manager.call_tool(
        "analyze_text",
        {"text": "Hello from Multi-Server Manager!\nThis is a test file."}
    )
    print(result)
    print()
    
    # 工具推荐
    print("=" * 80)
    print("🤖 智能工具推荐")
    print("=" * 80)
    print()
    
    router = ToolRouter(manager)
    
    tasks = [
        "读取配置文件",
        "分析日志文件中的错误",
        "计算统计数据"
    ]
    
    for task in tasks:
        print(f"任务: {task}")
        suggestions = router.suggest_tools(task)
        print(f"推荐工具:")
        for tool in suggestions[:3]:
            print(f"  - {tool['name']} (来自 {tool['server']}) - 相关度: {tool['relevance_score']}")
        print()
    
    # 关闭
    await manager.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
