# 系统架构文档 (Architecture Design)

## 1. 整体架构概览

智能合同评审系统采用微服务分层架构，核心驱动力来�?**Multi-Agent（多智能体）** 协作系统�?
```mermaid
graph TD
    User((用户))
    
    subgraph Frontend [前端层]
        UI[Streamlit Web UI]
        Monitor[任务监控面板]
    end
    
    subgraph Backend [后端服务层]
        API[FastAPI Gateway]
        Queue[后台任务队列]
        Parser[MarkItDown 解析服务]
        Orchestrator[Agent 编排器]
    end
    
    subgraph AI_Core [AI 核心层]
        LLM_Provider[LLM Provider接口]
        CodeBuddy[CodeBuddy Headless]
        
        subgraph Agents [Agent 团队]
            CA[条款分析 Agent]
            RA[风险评估 Agent]
            CC[合规检�?Agent]
            RG[报告生成 Agent]
        end
    end
    
    subgraph Storage [数据与知识层]
        KB[专业知识�?(CSV)]
        DB[任务数据�?(SQLite)]
        FileStore[文件存储]
    end
    
    User --> UI
    UI --> API
    API --> Queue
    Queue --> Parser
    Queue --> Orchestrator
    
    Orchestrator --> CA
    Orchestrator --> RA
    Orchestrator --> CC
    Orchestrator --> RG
    
    CA & RA & CC & RG --> LLM_Provider
    LLM_Provider --> CodeBuddy
    
    Agents -.-> KB
    API -.-> DB
    Parser -.-> FileStore
```

## 2. Agent 设计理念

每个 Agent 都遵�?`BaseAgent` 定义的统一接口，包含以下核心要素：

1.  **Role (角色)**: 明确的身份定义（�?资深风险评估专家"）�?2.  **Capabilities (能力)**: 定义 Agent 能做什么（�?风险量化"）�?3.  **Knowledge Base (知识�?**: 专属的领域知识（�?风险矩阵"）�?4.  **Tools (工具)**: 辅助 Agent 完成任务的代码逻辑�?
### Agent 交互模式

系统采用 **"顺序+并行"** 的混合编排模式：

1.  **Phase 1 (串行)**: `ClauseAnalysisAgent` 首先执行，建立对合同的基础理解和结构化数据�?2.  **Phase 2 (并行)**: `RiskAssessmentAgent` �?`ComplianceCheckAgent` 同时基于 Phase 1 的结果进行分析，提高效率�?3.  **Phase 3 (串行)**: `ReportGenerationAgent` 汇总所有分析结果，进行综合决策并生成报告�?
## 3. 关键模块说明

### 3.1 Agent Orchestrator (编排�?
- 负责实例化和管理 Agent 生命周期�?- 控制工作流执行顺序（串行/并行）�?- 管理 Agent 间的上下文传�?(Context Passing)�?- 错误处理和重试机制�?
### 3.2 LLM Provider
- 封装底层的模型调用接口�?- 支持 `CodeBuddyClient` (HTTP) �?Mock 模式�?- 提供统一�?`generate` 接口，屏蔽底层差异�?- 处理 Prompt 构建和结果解析�?
### 3.3 Document Parser (MarkItDown)
- 统一的文档解析入口�?- �?PDF/Word/Excel 等格式转换为标准 Markdown�?- 保留文档结构（标题、表格），便�?LLM 理解�?
## 4. 数据流设�?
1.  **输入**: 用户上传文件 -> MarkItDown 解析 -> Markdown 文本
2.  **处理**: 
    - Markdown -> **ClauseAnalysisAgent** -> 结构化条款数�?    - 结构化条款数�?+ 知识�?-> **RiskAgent** -> 风险列表
    - 结构化条款数�?+ 知识�?-> **ComplianceAgent** -> 合规检查表
    - 所有中间结�?-> **ReportAgent** -> 最�?JSON 报告
3.  **输出**: JSON 报告 -> ReportGenerator -> HTML/Excel/PDF

## 5. 扩展性设�?
系统设计支持轻松添加新的 Agent�?1.  �?`app/agents/` 创建新的 Agent 类继�?`BaseAgent`�?2.  �?`app/agents/tools/` 定义所需工具�?3.  �?`config/agents/` 添加配置�?4.  �?`AgentOrchestrator` 中注册新 Agent 并更新工作流�?