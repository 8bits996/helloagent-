# Task05 学习计划 - MCP协议讲解

**制定日期**: 2024-12-24  
**预计完成**: 2024-12-26  
**学习时长**: 8-10 小时

---

## 📋 学习目标

### 核心目标
1. **深入理解 MCP 协议** - 设计理念、架构、核心组件
2. **掌握 MCP Server 开发** - 实现 Resources/Tools/Prompts
3. **掌握 MCP Client 使用** - 连接和调用 Server
4. **集成到 Agent 系统** - 将 MCP 工具集成到 ReAct Agent
5. **实践开源生态** - 使用和贡献 MCP Servers

### 能力目标
- 从"使用 MCP Server"转变为"开发 MCP Server"
- 能够为特定领域开发 MCP 工具
- 理解标准化协议在 AI 生态中的价值
- 掌握异步编程和 JSON-RPC 协议

---

## 📚 学习资源

### 主要资源
1. **Hello Agents 第十章** - MCP 协议讲解
   - 网址: https://datawhalechina.github.io/hello-agents

2. **MCP 官方文档**
   - 网址: https://modelcontextprotocol.io/
   - 重点: Core Concepts, Server Development, Client Development

3. **MCP Python SDK**
   - GitHub: https://github.com/modelcontextprotocol/python-sdk
   - 文档: 查看示例代码

4. **MCP Servers 集合**
   - GitHub: https://github.com/modelcontextprotocol/servers
   - 学习现有 Server 的实现

### 辅助资源
- JSON-RPC 2.0 规范
- Python asyncio 文档
- Pydantic 文档(数据验证)

---

## 🗓️ 学习时间表

### Day 1: MCP 协议基础 (3-4小时)

#### 上午 (1.5-2小时): 理论学习
- [ ] **10.1 MCP 协议概述** (30分钟)
  - 什么是 MCP?
  - 为什么需要 MCP?
  - MCP vs 传统 API
  - MCP 生态系统

- [ ] **10.2 MCP 架构** (30分钟)
  - Server-Client 架构
  - Transport 层(stdio/SSE/WebSocket)
  - JSON-RPC 2.0 协议
  - 核心组件(Resources/Tools/Prompts/Sampling)

- [ ] **10.3 MCP 核心概念** (30分钟)
  - Resources: 资源管理
  - Tools: 工具调用
  - Prompts: 提示词模板
  - Sampling: LLM 采样

- [ ] **记录学习笔记** (30分钟)
  - 整理核心概念
  - 画出架构图
  - 记录疑问点

#### 下午 (1.5-2小时): 环境准备 + 官方示例
- [ ] **环境配置** (30分钟)
  ```bash
  # 安装 MCP Python SDK
  pip install mcp
  
  # 验证已安装的 MCP Servers
  # - filesystem
  # - puppeteer
  # - chrome-devtools
  # - sequential-thinking
  # - metaso
  ```

- [ ] **运行官方示例** (1小时)
  - 克隆 MCP Python SDK 示例
  - 运行 weather Server 示例
  - 运行 Client 示例
  - 理解代码流程

- [ ] **记录运行结果** (30分钟)
  - 截图运行过程
  - 记录观察结果
  - 总结工作流程

---

### Day 2: MCP Server 开发 (3-4小时)

#### 上午 (2小时): 基础 Server
- [ ] **10.4 Server 基础结构** (30分钟)
  - Server 初始化
  - 注册工具
  - 处理请求
  - 返回响应

- [ ] **实践1: 最简 Server** (1小时)
  - 创建 `mcp_server_basic.py`
  - 实现1个简单工具(如 calculator)
  - 测试工具调用
  - 记录代码和结果

- [ ] **代码审查** (30分钟)
  - 对比官方示例
  - 理解关键代码
  - 优化实现

#### 下午 (1.5-2小时): 高级 Server
- [ ] **实践2: 多工具 Server** (1小时)
  - 添加多个工具
  - 实现 Resources
  - 实现 Prompts
  - 测试完整功能

- [ ] **实践3: 领域 Server** (1小时)
  - 设计一个领域 Server(如:文件操作/数据查询)
  - 实现核心工具
  - 添加错误处理
  - 编写测试用例

- [ ] **总结经验** (30分钟)
  - 记录最佳实践
  - 整理常见问题
  - 优化代码结构

---

### Day 3: Client 开发 + Agent 集成 (2-3小时)

#### 上午 (1-1.5小时): MCP Client
- [ ] **10.5 Client 开发** (30分钟)
  - Client 连接管理
  - 调用 Server 工具
  - 处理响应
  - 错误处理

- [ ] **实践4: Client 实现** (30分钟)
  - 创建 `mcp_client.py`
  - 连接到 Server
  - 调用工具
  - 测试完整流程

- [ ] **多 Server 管理** (30分钟)
  - 连接多个 Server
  - 工具发现
  - 工具路由

#### 下午 (1-1.5小时): Agent 集成
- [ ] **10.6 MCP 与 Agent 集成** (30分钟)
  - 理解集成方案
  - MCP 工具适配
  - Agent 工具系统扩展

- [ ] **实践5: MCP Agent** (1小时)
  - 创建 `mcp_agent.py`
  - 集成 MCP Client 到 ReAct Agent
  - 使用 MCP 工具完成任务
  - 测试多工具协作

- [ ] **性能优化** (30分钟)
  - 异步调用优化
  - 连接池管理
  - 缓存策略

---

### Day 4: 习题 + 总结 (2小时)

#### 习题练习 (1小时)
- [ ] **习题1**: MCP 协议理解
  - 对比 MCP vs REST API
  - 分析适用场景

- [ ] **习题2**: Server 开发
  - 设计一个实用的 MCP Server
  - 实现核心功能

- [ ] **习题3**: Agent 集成
  - 将多个 MCP Server 集成到 Agent
  - 实现工具协作场景

- [ ] **习题4**: 开源贡献
  - 改进现有 MCP Server
  - 或开发新的 Server

#### 总结文档 (1小时)
- [ ] **编写学习总结**
  - 核心知识点回顾
  - 实践经验总结
  - 代码示例整理
  - 遇到的问题和解决方案

- [ ] **准备打卡材料**
  - 整理学习成果
  - 准备代码截图
  - 编写打卡文案

---

## 🎯 核心学习点

### 1. MCP 协议理念
```
为什么需要 MCP?
┌────────────────────────────────┐
│  传统方式: 每个工具不同的接口    │
│  ├─ API A: REST                │
│  ├─ API B: GraphQL             │
│  └─ API C: RPC                 │
│  问题: 集成困难,维护成本高       │
└────────────────────────────────┘

┌────────────────────────────────┐
│  MCP 方式: 统一的标准协议       │
│  ├─ Tool 1: MCP Server         │
│  ├─ Tool 2: MCP Server         │
│  └─ Tool 3: MCP Server         │
│  优势: 即插即用,易于扩展         │
└────────────────────────────────┘
```

### 2. MCP 架构
```
┌─────────────────────────────────┐
│        LLM Application          │
│   (Agent / IDE / Chat App)      │
└────────────┬────────────────────┘
             │
             │ MCP Protocol (JSON-RPC 2.0)
             │
┌────────────▼────────────────────┐
│      MCP Client / Host          │
│  - 工具发现                      │
│  - 调用管理                      │
│  - 响应处理                      │
└────────────┬────────────────────┘
             │
             ├──► MCP Server 1 (Filesystem)
             │    ├─ list_directory
             │    ├─ read_file
             │    └─ write_file
             │
             ├──► MCP Server 2 (Database)
             │    ├─ query
             │    ├─ insert
             │    └─ update
             │
             └──► MCP Server 3 (Browser)
                  ├─ navigate
                  ├─ screenshot
                  └─ click
```

### 3. MCP Server 结构
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# 1. 创建 Server
server = Server("my-server")

# 2. 注册工具
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="calculator",
            description="Perform math calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        )
    ]

# 3. 实现工具
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "calculator":
        result = eval(arguments["expression"])
        return [TextContent(text=str(result))]

# 4. 运行 Server
async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)
```

### 4. MCP Client 使用
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. 创建 Client
params = StdioServerParameters(
    command="python",
    args=["mcp_server_basic.py"]
)

async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        # 2. 初始化
        await session.initialize()
        
        # 3. 列出工具
        tools = await session.list_tools()
        
        # 4. 调用工具
        result = await session.call_tool(
            name="calculator",
            arguments={"expression": "2 + 2"}
        )
        print(result)
```

### 5. 集成到 Agent
```python
class MCPAgent:
    def __init__(self, llm, mcp_servers):
        self.llm = llm
        self.mcp_sessions = []
        
        # 连接所有 MCP Servers
        for server_config in mcp_servers:
            session = self.connect_mcp_server(server_config)
            self.mcp_sessions.append(session)
    
    async def get_all_tools(self):
        """从所有 MCP Servers 获取工具"""
        all_tools = []
        for session in self.mcp_sessions:
            tools = await session.list_tools()
            all_tools.extend(tools)
        return all_tools
    
    async def execute_tool(self, tool_name, arguments):
        """执行工具(自动路由到正确的 Server)"""
        for session in self.mcp_sessions:
            tools = await session.list_tools()
            if tool_name in [t.name for t in tools]:
                return await session.call_tool(tool_name, arguments)
```

---

## 📊 学习检查清单

### 理论理解 ✓
- [ ] 理解 MCP 的设计理念和价值
- [ ] 掌握 MCP 架构的核心组件
- [ ] 理解 JSON-RPC 2.0 协议
- [ ] 掌握 Resources/Tools/Prompts/Sampling 的区别
- [ ] 理解 Transport 层的选择(stdio vs SSE)

### Server 开发 ✓
- [ ] 能够创建基础 MCP Server
- [ ] 能够注册和实现工具
- [ ] 能够实现 Resources 和 Prompts
- [ ] 掌握错误处理和日志
- [ ] 理解异步编程模式

### Client 使用 ✓
- [ ] 能够连接 MCP Server
- [ ] 能够列出和调用工具
- [ ] 能够管理多个 Server
- [ ] 掌握工具发现和路由
- [ ] 理解连接生命周期管理

### Agent 集成 ✓
- [ ] 能够将 MCP 集成到 ReAct Agent
- [ ] 能够使用 MCP 工具完成任务
- [ ] 理解工具适配和转换
- [ ] 掌握多 Server 协作
- [ ] 能够优化性能和错误处理

### 实践能力 ✓
- [ ] 完成至少 1 个自定义 MCP Server
- [ ] 完成 MCP Client 实现
- [ ] 完成 MCP Agent 集成
- [ ] 完成所有课后习题
- [ ] 编写完整的学习总结

---

## 💡 学习建议

### 学习策略
1. **先理解"为什么"**
   - MCP 解决了什么问题?
   - 与传统 API 有什么不同?
   - 为什么使用 JSON-RPC 2.0?

2. **再学习"是什么"**
   - MCP 的架构是怎样的?
   - 核心组件有哪些?
   - 协议细节是什么?

3. **最后实践"怎么做"**
   - 如何开发 Server?
   - 如何使用 Client?
   - 如何集成到 Agent?

### 重点关注
- **工具描述的重要性** - 影响 LLM 的选择
- **异步编程** - MCP 基于 asyncio
- **错误处理** - 网络通信的稳定性
- **性能优化** - 连接池、缓存

### 实践建议
1. **从简单开始**
   - 先实现1个工具的 Server
   - 逐步增加复杂度

2. **参考官方示例**
   - 学习最佳实践
   - 理解代码结构

3. **测试驱动**
   - 先写测试用例
   - 再实现功能

4. **实际应用**
   - 思考实际使用场景
   - 开发有用的工具

---

## 🎓 预期成果

### 代码成果
1. **mcp_server_basic.py** - 基础 MCP Server
2. **mcp_client.py** - MCP Client 实现
3. **mcp_tools.py** - 自定义工具集
4. **mcp_agent.py** - 集成 MCP 的 Agent
5. **tests/** - 完整的测试用例

### 文档成果
1. **Task05-学习笔记.md** - 详细学习笔记
2. **Task05-习题解答.md** - 习题解答
3. **Task05-学习总结.md** - 学习总结
4. **Task05-打卡.md** - 打卡内容

### 能力提升
- 从"使用 MCP"到"开发 MCP"
- 理解标准化协议的价值
- 掌握异步编程和 RPC
- 提升系统设计能力

---

## 📅 时间分配

| 阶段 | 内容 | 时间 | 优先级 |
|------|------|------|--------|
| Day 1 上午 | MCP 理论学习 | 2h | ⭐⭐⭐⭐⭐ |
| Day 1 下午 | 环境+示例 | 2h | ⭐⭐⭐⭐⭐ |
| Day 2 上午 | Server 基础 | 2h | ⭐⭐⭐⭐⭐ |
| Day 2 下午 | Server 高级 | 2h | ⭐⭐⭐⭐ |
| Day 3 上午 | Client 开发 | 1.5h | ⭐⭐⭐⭐⭐ |
| Day 3 下午 | Agent 集成 | 1.5h | ⭐⭐⭐⭐⭐ |
| Day 4 | 习题+总结 | 2h | ⭐⭐⭐⭐ |

**总计**: 8-10 小时

---

## 🔗 相关资源链接

### 官方资源
- [MCP 官网](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers 集合](https://github.com/modelcontextprotocol/servers)

### 教程资源
- [Hello Agents 第十章](https://datawhalechina.github.io/hello-agents)
- [MCP 快速入门](https://modelcontextprotocol.io/quickstart)
- [MCP 核心概念](https://modelcontextprotocol.io/docs/concepts/architecture)

### 技术文档
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Pydantic](https://docs.pydantic.dev/)

---

## 🎯 成功标准

### 必须完成 (Must Have)
- ✅ 完成 Hello Agents 第十章学习
- ✅ 实现至少 1 个 MCP Server
- ✅ 实现 MCP Client
- ✅ 将 MCP 集成到 Agent
- ✅ 完成所有课后习题

### 应该完成 (Should Have)
- ✅ 开发 2-3 个不同的 MCP Server
- ✅ 实现多 Server 管理
- ✅ 编写完整测试用例
- ✅ 优化性能和错误处理

### 可以完成 (Could Have)
- 贡献开源 MCP Server
- 开发领域特定的 Server
- 编写详细的技术博客

---

**制定人**: frankechen  
**创建时间**: 2024-12-24  
**最后更新**: 2024-12-24  

---

准备开始学习! 🚀
