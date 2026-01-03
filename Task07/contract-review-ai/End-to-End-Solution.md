# 端到端合同评审AI系统方案

## 1. 方案概述

本项目提供一个完整的、端到端的合同评审AI系统。系统采用微服务架构，前端使用Streamlit提供用户交互界面，后端基于FastAPI构建，核心评审逻辑由多Agent协作系统驱动�?
本方案已移除对本�?`codebuddy cli` 的依赖，转而使用标准的OpenAI兼容API（支持接入OpenAI、DeepSeek、Qwen等模型服务）或内置的Mock模式进行独立运行�?
## 2. 系统架构

```mermaid
graph TD
    User[用户] --> Frontend[Streamlit前端]
    Frontend --> Backend[FastAPI后端]
    
    subgraph "后端服务 (app/)"
        Backend --> Orchestrator[Agent编排器]
        Backend --> DocParser[文档解析服务 (MarkItDown)]
        Backend --> ReportGen[报告生成服务]
        Backend --> KBManager[知识库管理]
    end
    
    subgraph "Agent协作网络 (app/agents/)"
        Orchestrator --> ClauseAgent[条款分析专家]
        Orchestrator --> RiskAgent[风险评估专家]
        Orchestrator --> CompAgent[合规检查专家]
        Orchestrator --> ReportAgent[首席评审官]
    end
    
    subgraph "基础设施"
        LLMProvider[LLM接入�?(OpenAI兼容)] --> ExternalLLM[外部LLM服务 (DeepSeek/Qwen)]
        KBManager --> KBStorage[本地知识�?(CSV/Excel)]
    end
```

### 2.1 核心组件

1.  **Frontend (Streamlit)**: 提供文件上传、任务监控、结果展示和报告下载功能�?2.  **Backend (FastAPI)**: 处理API请求，管理任务生命周期�?3.  **Orchestrator (Agent编排�?**: 协调多个Agent按顺�?并行执行任务�?4.  **LLM Provider**: 封装LLM调用，支持OpenAI兼容接口，内置Mock回退机制�?5.  **Agents**:
    *   **条款分析专家**: 提取信息，检查完整性�?    *   **风险评估专家**: 识别并量化风险�?    *   **合规检查专�?*: 对照SOP进行合规审查�?    *   **首席评审�?*: 汇总意见，生成最终报告�?
## 3. 部署与运�?
### 3.1 环境要求

*   Python 3.10+
*   Windows/Linux/MacOS

### 3.2 安装依赖

```bash
cd /path/to/contract-review-ai
pip install -r requirements.txt
```

### 3.3 配置

修改 `.env` 文件或直接在 `app/config.py` 中配置LLM参数�?
```python
# app/config.py
LLM_API_KEY = "sk-xxxxxxxx"  # 您的API Key
LLM_BASE_URL = "https://api.deepseek.com/v1"  # 或其他兼容地址
LLM_MODEL = "deepseek-chat"
```

### 3.4 启动服务

**方式 1: 使用启动脚本 (推荐)**

```bash
# 启动后端和前�?python run_services.py
```

**方式 2: 分别启动**

启动后端:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

启动前端:
```bash
streamlit run app/frontend.py --server.port 8501
```

## 4. 关键代码说明

### 4.1 LLM接入�?(`app/agents/llm_provider.py`)

移除了对 `codebuddy cli` 的依赖，使用 `httpx` 实现标准�?`chat/completions` 调用�?
```python
class LLMProvider:
    def __init__(self, api_key, base_url, model, use_mock=False):
        # ... 初始�?httpx client ...
        pass

    async def generate(self, prompt, ...):
        # ... 调用 API ...
        # 如果失败，自动回退�?_generate_mock
        pass
```

### 4.2 Agent编排 (`app/services/agent_orchestrator.py`)

负责加载配置并执行Review Workflow�?
1.  **Clause Analysis** (串行)
2.  **Risk Assessment** + **Compliance Check** (并行)
3.  **Report Generation** (汇�?

### 4.3 任务入口 (`app/main.py`)

`start_review` 接口现在直接初始�?`AgentOrchestrator` 并执行，不再通过CLI子进程调用�?
## 5. 测试验证

系统包含完整的测试脚�?`test_agents.py`，用于验证端到端流程�?
运行测试:
```bash
python test_agents.py
```

测试将模拟一个合同文本，通过Orchestrator调用各个Agent（如果没有配置有效API Key，会自动回退到Mock模式），并输出最终的JSON报告�?
## 6. 总结

本方案实现了一个解耦、轻量化且易于扩展的智能合同评审系统。通过移除专有CLI依赖，系统可以轻松部署到任何支持Python的环境，并灵活对接各种大模型服务�?