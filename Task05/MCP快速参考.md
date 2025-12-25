# MCP 快速参考手册

快速查阅 MCP 协议的关键信息

---

## 🎯 MCP 核心概念

### 什么是 MCP?

**Model Context Protocol (MCP)** 是一个标准化协议,用于 AI 应用(如 Agent)与外部工具/服务的通信。

**关键特性**:
- 📦 **标准化接口** - 统一的工具调用方式
- 🔌 **即插即用** - 轻松集成新工具
- 🔄 **上下文共享** - 共享 Model Context
- 🎨 **可组合** - 多个 Server 可组合使用

---

## 🏗️ MCP 架构

```
┌─────────────────┐
│  AI Application │  (Agent/IDE/Chat)
│   (Host/Client) │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC 2.0)
         │
    ┌────▼────┐
    │  Tools  │
    ├─────────┤
    │ Server1 │ ◄── Filesystem
    │ Server2 │ ◄── Database
    │ Server3 │ ◄── Browser
    └─────────┘
```

---

## 🔧 核心组件

### 1. Resources (资源)
- **作用**: 提供静态或动态内容
- **示例**: 文件内容、数据库记录、API 响应
- **特点**: 只读访问

### 2. Tools (工具)
- **作用**: 执行操作,改变状态
- **示例**: 写文件、发送邮件、执行命令
- **特点**: 可执行,有副作用

### 3. Prompts (提示词)
- **作用**: 预定义的提示词模板
- **示例**: 代码审查模板、翻译模板
- **特点**: 可参数化

### 4. Sampling (采样)
- **作用**: 请求 LLM 推理
- **示例**: 让 LLM 生成内容
- **特点**: Server 调用 Client

---

## 💻 代码速查

### Server 基础结构

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 1. 创建 Server
server = Server("my-server")

# 2. 注册工具列表
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tool_name",
            description="工具描述",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        )
    ]

# 3. 实现工具
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "tool_name":
        result = do_something(arguments["param"])
        return [TextContent(text=result)]

# 4. 运行
async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, 
                        server.create_initialization_options())
```

### Client 基础使用

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. 配置 Server
params = StdioServerParameters(
    command="python",
    args=["server.py"]
)

# 2. 连接和使用
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        # 初始化
        await session.initialize()
        
        # 列出工具
        tools = await session.list_tools()
        
        # 调用工具
        result = await session.call_tool(
            name="tool_name",
            arguments={"param": "value"}
        )
```

---

## 🔀 Transport 层

### stdio (标准输入输出)
```python
from mcp.server.stdio import stdio_server

async with stdio_server() as (read, write):
    await server.run(read, write, options)
```

**优点**: 简单,适合本地进程  
**缺点**: 不支持远程  
**适用**: 本地工具,CLI 应用

### SSE (Server-Sent Events)
```python
from mcp.server.sse import sse_server

async with sse_server() as (read, write):
    await server.run(read, write, options)
```

**优点**: 支持远程,单向推送  
**缺点**: 只支持 Server→Client  
**适用**: 监控,通知

### WebSocket
```python
# 双向通信
```

**优点**: 支持远程,双向通信  
**缺点**: 复杂度高  
**适用**: 实时交互

---

## 📋 常用 Schema 定义

### 字符串参数
```json
{
  "type": "string",
  "description": "参数描述"
}
```

### 数字参数
```json
{
  "type": "number",
  "description": "数字参数",
  "minimum": 0,
  "maximum": 100
}
```

### 枚举参数
```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"],
  "description": "选择一个选项"
}
```

### 对象参数
```json
{
  "type": "object",
  "properties": {
    "field1": {"type": "string"},
    "field2": {"type": "number"}
  },
  "required": ["field1"]
}
```

### 数组参数
```json
{
  "type": "array",
  "items": {"type": "string"},
  "description": "字符串数组"
}
```

---

## 🐛 调试技巧

### 1. 启用日志
```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### 2. 打印请求/响应
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    print(f"Tool: {name}, Args: {arguments}")
    # ... 处理
```

### 3. 错误处理
```python
try:
    result = await session.call_tool(name, args)
except Exception as e:
    print(f"错误: {e}")
```

---

## ⚡ 性能优化

### 1. 连接池
```python
# 复用连接,避免频繁创建
class MCPConnectionPool:
    def __init__(self):
        self.connections = {}
    
    async def get_connection(self, server_name):
        if server_name not in self.connections:
            # 创建新连接
            pass
        return self.connections[server_name]
```

### 2. 缓存结果
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_result(key):
    # 返回缓存结果
    pass
```

### 3. 异步并发
```python
# 并发调用多个工具
results = await asyncio.gather(
    session.call_tool("tool1", args1),
    session.call_tool("tool2", args2),
    session.call_tool("tool3", args3)
)
```

---

## 🔐 安全建议

### 1. 输入验证
```python
def validate_input(arguments: dict) -> bool:
    # 验证参数
    if "path" in arguments:
        path = arguments["path"]
        # 防止路径遍历
        if ".." in path:
            return False
    return True
```

### 2. 权限控制
```python
ALLOWED_OPERATIONS = ["read", "list"]

def check_permission(operation: str) -> bool:
    return operation in ALLOWED_OPERATIONS
```

### 3. 速率限制
```python
from time import time

class RateLimiter:
    def __init__(self, max_calls: int, window: int):
        self.max_calls = max_calls
        self.window = window
        self.calls = []
    
    def allow(self) -> bool:
        now = time()
        # 清除过期记录
        self.calls = [t for t in self.calls if now - t < self.window]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

---

## 📚 常见错误及解决

### 错误1: "Server not responding"
**原因**: Server 未启动或连接失败  
**解决**: 检查 Server 进程,验证 stdio 配置

### 错误2: "Tool not found"
**原因**: 工具名称错误或未注册  
**解决**: 检查工具名称拼写,确认已注册

### 错误3: "Invalid arguments"
**原因**: 参数不符合 Schema  
**解决**: 检查参数类型和必填字段

### 错误4: "Timeout"
**原因**: 工具执行时间过长  
**解决**: 优化工具实现,增加超时时间

---

## 🔗 有用的链接

- [MCP 官网](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Python SDK 文档](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers 集合](https://github.com/modelcontextprotocol/servers)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)

---

## 💡 最佳实践

1. **工具描述要清晰**
   - 让 LLM 能准确理解工具用途
   - 包含参数说明和示例

2. **错误处理要完善**
   - 捕获所有异常
   - 返回有意义的错误信息

3. **参数验证要严格**
   - 验证类型和范围
   - 防止注入攻击

4. **日志记录要详细**
   - 记录所有关键操作
   - 便于调试和审计

5. **文档要完整**
   - README 包含使用示例
   - 注释说明关键逻辑

---

**最后更新**: 2024-12-24  
**版本**: 1.0
