# 调研素材 — AWS AI平台（Bedrock + Q Developer）

> 调研时间：2026年3月27日
> 来源：Thinkmove Solutions (2026.3.25)、AWS官方

---

## 一、Amazon Bedrock 2026

### 1.1 产品定位
AWS的全托管AI平台，通过单一统一API让企业无需管理基础设施即可使用顶级AI模型。

### 1.2 支持的模型（~100个）

| 提供商 | 关键模型 | 适用场景 |
|--------|---------|---------|
| Anthropic | Claude Opus 4.6, Sonnet 4.6, 4.5 | 复杂推理、编程、分析 |
| OpenAI | GPT-OSS 20B, 120B | 通用任务、OpenAI兼容 |
| Meta | Llama 4, 3.3 70B | 开放权重任务 |
| Amazon | Nova 2.0, Pro, Lite, Micro | AWS原生、多模态、低延迟 |
| Mistral | Large 3, Ministral 3B/8B/14B | 欧洲合规、多语言 |
| NVIDIA | Nemotron 3 Super, Nano 2 | 高性能推理、编码 |
| DeepSeek | R1, V3.2 | 成本效益深度推理 |
| Google | Gemma 3 | 轻量级多模态 |
| Others | Qwen3 Coder, Kimi K2.5, MiniMax M2 | 专业和多模态 |

### 1.3 核心功能

**智能提示路由**
- 简单查询→轻量模型（便宜）
- 复杂推理→强模型
- 效果：**降本30%**，不影响质量

**模型蒸馏**
- 大模型→小模型，针对特定用例调整
- 效果：**速度+500%，成本-75%**

**Bedrock Guardrails**
- 拦截88%有害内容
- 正确响应识别率99%
- PII检测、主题限制、基础检查

**知识库**
- 连接企业文档/数据库
- 基于企业数据回答，无需自定义检索管道

**AgentCore（2026重点）**
- 构建可执行行动的AI Agent
- 支持浏览网页、查询数据库、调用API、运行代码
- 跨会话记忆、策略控制、权限管理

**Project Mantle**
- OpenAI兼容API端点
- 不改代码结构即可使用Bedrock

**Nova Forge SDK**
- 非ML专家可微调Nova模型

### 1.4 定价
- **按Token计费**，无前期承诺
- 无GPU基础设施成本
- 智能路由和蒸馏进一步降低成本
- 小团队几美元即可原型验证

---

## 二、Amazon Q Developer

### 2.1 产品定位
AWS原生AI编程助手，与AWS服务深度集成。

### 2.2 定价
| 方案 | 月费 | 权益 |
|------|------|------|
| Free Tier | $0 | 有限使用 |
| Pro/Individual | $19/人 | 标准功能 |
| 企业版 | $19/人 | +管理功能 |

### 2.3 核心功能
- **CLI Agent**：终端中直接操作DynamoDB、S3等AWS资源
- **代码补全**：IDE内智能补全
- **安全扫描**：自动检测漏洞
- **文档理解**：理解AWS文档和最佳实践
- **IDE集成**：VS Code、JetBrains

### 2.4 配套产品 — Kiro（2026新增）
- **规格驱动开发**：结构化需求文档→自动代码生成
- **Hooks**：事件驱动自动化（如保存时自动Lint）
- **Steering Files**：项目级指令
- **MCP集成**
- 定价：免费50积分/月，Pro $20/月(1000积分)，团队$40/人/月

---

## 三、与腾讯云AI平台对标

| 维度 | AWS (Bedrock) | 腾讯云 |
|------|--------------|--------|
| 模型数量 | ~100 | 较少 |
| 模型来源 | 多厂商（Anthropic/OpenAI/Meta等） | 自研为主 |
| 智能路由 | ✅ | ❌ |
| 模型蒸馏 | ✅ 速度+500% | ❌ |
| Agent框架 | AgentCore | ADP |
| 安全护栏 | 88%拦截率 | ✅ |
| OpenAI兼容 | ✅ Mantle | ❌ |
| 国内合规 | ❌ | ✅ |
| 成熟度 | 极高 | 成长中 |

---

## 四、关键启示

1. **多模型生态是趋势**：Bedrock汇聚100个模型，"让客户选择而非被绑定"
2. **智能路由降本效果显著**：30-75%的成本节省是强卖点
3. **AgentCore**：将Agent作为平台级能力，与腾讯ADP方向一致但更成熟
4. **Nova Forge**：降低微调门槛，让非ML专家也能定制模型
