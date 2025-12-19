# Task02: 构建你的Agent框架

**开始日期**: 2025-12-19  
**截止日期**: 2025-12-20  
**状态**: 📋 准备中

---

## 📚 本章概述

第七章将带你从"使用者"转变为"构建者"，亲手构建一个轻量级的Agent框架 - **HelloAgents**。

### 核心主题
1. 框架设计理念 - 轻量级、教学友好、万物皆工具
2. 统一的LLM接口 - 支持多Provider自动检测
3. 核心基础组件 - Message、Config、Agent基类
4. 四种Agent范式框架化 - Simple、ReAct、Reflection、PlanAndSolve
5. 工具系统构建 - 注册、调用、链式、并发

---

## 🎯 学习目标

### 知识目标
- [ ] 理解主流框架的四大局限性
- [ ] 掌握"万物皆工具"设计理念
- [ ] 理解三大设计模式（单例、模板方法、注册表）
- [ ] 掌握Provider自动检测机制
- [ ] 理解工具系统架构

### 能力目标
- [ ] 能够设计轻量级框架架构
- [ ] 能够实现四种Agent范式
- [ ] 能够开发自定义工具
- [ ] 能够扩展新的Provider
- [ ] 能够进行框架级设计

---

## 📖 章节结构

```
第七章 构建你的Agent框架
│
├─ 7.1 框架整体架构设计
│   ├─ 为何需要自建Agent框架
│   ├─ HelloAgents框架的设计理念
│   └─ 本章学习目标
│
├─ 7.2 HelloAgentsLLM - 统一的模型接口
│   ├─ 多模型供应商支持
│   ├─ 本地模型支持
│   └─ 自动检测机制
│
├─ 7.3 核心基础组件
│   ├─ Message类
│   ├─ Config类（单例模式）
│   └─ Agent基类（模板方法模式）
│
├─ 7.4 四种Agent范式的框架化实现
│   ├─ SimpleAgent
│   ├─ ReActAgent
│   ├─ ReflectionAgent
│   └─ PlanAndSolveAgent
│
└─ 7.5 工具系统构建
    ├─ BaseTool抽象类
    ├─ ToolRegistry（注册表模式）
    ├─ 内置工具（Calculator、Search）
    ├─ ToolChain
    └─ AsyncToolExecutor
```

---

## 🚀 快速开始

### 1. 安装框架

```bash
# 基础安装
pip install "hello-agents==0.1.1"

# 包含搜索工具
pip install "hello-agents[search]==0.1.1"
```

### 2. 环境配置

复制Task01的`.env`文件或创建新的：

```bash
# LLM配置（使用Task01的配置）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=your_base_url_here
LLM_MODEL=your_model_name_here
```

### 3. 30秒快速体验

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建LLM实例
llm = HelloAgentsLLM()

# 创建Agent
agent = SimpleAgent(
    name="AI助手",
    llm=llm,
    system_prompt="你是一个有用的AI助手"
)

# 运行对话
response = agent.run("你好！请介绍一下自己")
print(response)
```

---

## 📝 本章习题（共6题）

### 习题1: 框架设计分析 ⭐⭐
- 分析主流框架的局限性
- 评估"万物皆工具"设计
- 对比框架化改进

### 习题2: 多模型支持扩展 ⭐⭐⭐ (实践题)
- 添加新Provider支持
- 分析优先级检测机制
- 对比本地模型方案

### 习题3: 核心组件分析 ⭐⭐
- Pydantic的优势
- 模板方法模式
- 单例模式的必要性

### 习题4: Agent范式扩展 ⭐⭐⭐⭐ (实践题)
- 对比ReAct改进点
- 实现质量评分机制
- **挑战**: 实现Tree-of-Thought Agent

### 习题5: 工具系统设计 ⭐⭐⭐
- 统一接口的重要性
- 设计3工具串联场景
- 分析并行执行场景

### 习题6: 框架扩展设计 ⭐⭐⭐⭐ (挑战题)
- 设计流式输出功能
- 设计多轮对话管理
- **挑战**: 设计插件系统

---

## 📂 文件结构

```
Task02/
├── README.md                      # 本文件
├── simple_agent.py                # SimpleAgent实现
├── react_agent.py                 # ReAct框架化
├── reflection_agent.py            # Reflection + 质量评分
├── plan_solve_agent.py            # PlanAndSolve框架化
├── tot_agent.py                   # Tree-of-Thought (挑战)
├── custom_tools.py                # 自定义工具
├── gemini_provider.py             # 新Provider扩展
├── tests/                         # 测试文件
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_providers.py
└── docs/                          # 文档
    ├── 学习笔记.md
    ├── 习题解答.md
    ├── 对比分析.md
    └── 框架设计思考.md
```

---

## 🎓 学习建议

### 对比学习法

**Task01 vs Task02 对比**：

| 方面 | Task01（从零实现） | Task02（框架化） |
|------|-------------------|-----------------|
| 代码组织 | 单文件，过程式 | 多模块，面向对象 |
| 工具调用 | 硬编码 | 注册表动态管理 |
| 错误处理 | 基础try-catch | 完善的异常体系 |
| 可复用性 | 低 | 高 |
| 可测试性 | 中 | 高 |
| 可扩展性 | 低 | 高 |

### 学习步骤

1. **先体验**：安装框架，运行示例代码
2. **再理解**：阅读文档，理解设计理念
3. **后实现**：跟随章节，从零实现每个组件
4. **最后对比**：对比Task01代码，总结改进

### 重点关注

#### 设计模式
- **单例模式**: Config类为什么需要单例？
- **模板方法模式**: Agent基类的`run()`和`_execute()`
- **注册表模式**: ToolRegistry如何管理工具？

#### 架构设计
- **分层解耦**: 核心层、实现层、工具层
- **职责单一**: 每个类只做一件事
- **接口统一**: 统一的工具接口设计
- **依赖倒置**: 依赖抽象而非具体实现

---

## 💡 关键概念

### 1. "万物皆工具"设计理念

在HelloAgents中，除了核心的Agent类，一切皆为Tools：
- Memory（记忆） → 工具
- RAG（检索） → 工具
- MCP（协议） → 工具
- 外部API → 工具

**优势**：
- 统一抽象，降低学习成本
- 简化架构，减少概念层次
- 易于扩展，添加新功能简单

**思考**：这种设计有什么局限性？

### 2. Provider自动检测机制

优先级顺序：
1. **显式指定** - 代码中指定provider
2. **环境变量检测** - 按优先级检测API key
3. **默认配置** - 使用默认provider

**为什么这样设计？**
- 灵活性：支持多种配置方式
- 便捷性：自动检测，无需手动指定
- 可预测：明确的优先级规则

### 3. 框架化带来的改进

对比Task01从零实现：

**代码结构**：
```
Task01:                    Task02:
react_agent.py            hello_agents/
  └─ 所有代码                ├─ core/
                             │   ├─ agent.py
                             │   ├─ llm.py
                             │   ├─ message.py
                             │   └─ config.py
                             ├─ agents/
                             │   └─ react_agent.py
                             └─ tools/
                                 └─ registry.py
```

**工具调用**：
```python
# Task01: 硬编码
def search(query):
    # 直接实现搜索逻辑
    ...

# Task02: 注册表
registry = ToolRegistry()
registry.register(SearchTool())
result = registry.execute_tool("search", query)
```

**错误处理**：
```python
# Task01: 基础
try:
    result = tool.execute()
except Exception as e:
    print(f"Error: {e}")

# Task02: 完善
try:
    result = tool.execute()
except ToolExecutionError as e:
    logger.error(f"Tool failed: {e}")
    self._handle_tool_error(e)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    self._handle_validation_error(e)
```

---

## 🔗 相关资源

### 课程资料
- **章节文档**: `hello-agents/docs/chapter7/`
- **示例代码**: `hello-agents/code/chapter7/`
- **源码仓库**: https://github.com/jjyaoao/helloagents

### 设计模式参考
- **单例模式**: 确保类只有一个实例
- **模板方法模式**: 定义算法骨架，延迟具体步骤
- **注册表模式**: 动态注册和查找对象

### Python最佳实践
- **Pydantic**: 数据验证和序列化
- **ABC**: 抽象基类，定义接口
- **Type Hints**: 类型注解，提升代码可读性

---

## ✅ 检查清单

### 环境准备
- [ ] 安装hello-agents框架
- [ ] 配置环境变量
- [ ] 测试快速开始代码
- [ ] 验证工具调用功能

### 理论学习
- [ ] 理解四大框架局限性
- [ ] 理解"万物皆工具"理念
- [ ] 掌握三大设计模式
- [ ] 理解Provider自动检测

### 代码实践
- [ ] SimpleAgent实现
- [ ] ReActAgent框架化
- [ ] ReflectionAgent + 评分
- [ ] PlanAndSolveAgent框架化
- [ ] 自定义工具开发
- [ ] 新Provider扩展

### 习题完成
- [ ] 习题1: 框架设计分析
- [ ] 习题2: 多模型支持 ⭐实践
- [ ] 习题3: 核心组件分析
- [ ] 习题4: Agent扩展 ⭐实践
- [ ] 习题5: 工具系统设计
- [ ] 习题6: 框架扩展 ⭐挑战

---

## 📊 预计时间

| 部分 | 预计时间 |
|------|----------|
| 理论学习 | 2小时 |
| 环境准备 | 0.5小时 |
| 代码实践 | 3-4小时 |
| 习题完成 | 2-3小时 |
| **总计** | **7.5-9.5小时** |

---

## 🎯 学习成果

完成Task02后，你将：
1. ✅ 掌握Agent框架设计能力
2. ✅ 理解常用设计模式应用
3. ✅ 具备系统架构思维
4. ✅ 完成从使用者到构建者的转变
5. ✅ 为后续高级章节打下坚实基础

---

**开始时间**: _____  
**完成时间**: _____  
**学习笔记**: [学习笔记.md](docs/学习笔记.md)  
**习题解答**: [习题解答.md](docs/习题解答.md)

---

**Good luck! 从使用者到构建者，这是重要的一步！** 🚀
