# 调研素材 — GitHub Copilot

> 调研时间：2026年3月27日
> 产品官网：https://github.com/features/copilot

---

## 一、产品概述

GitHub Copilot 是微软旗下GitHub推出的AI结对编程工具，是目前市场占有率最高的AI编程助手。2025年上线Agent Mode，从"代码补全"进化为"AI编程代理"。

## 二、定价方案

| 方案 | 月费 | 核心权益 |
|------|------|---------|
| **Free** | $0 | 50次Agent/月 + 2000次补全 + Haiku 4.5/GPT-5 mini + Copilot CLI |
| **Pro** | $10 | ✅ 无限补全 + 无限GPT-5 mini Agent + Copilot编码代理 + 代码审查 + Claude/Codex访问 + 300次premium请求 |
| **Pro+** | $39 | 所有模型含Opus 4.6 + 5倍premium请求 + GitHub Spark |
| **Business** | $19/人 | 企业级许可证管理+策略管理+IP赔偿 |
| **Enterprise** | $39/人 | Business全部+代码库索引+私有微调模型+深度定制 |

> **10人团队年费最低仅$2,280**，是所有竞品中最便宜的。

## 三、核心能力

### 3.1 代码补全
- **内联建议**：基于上下文预测后续代码
- **无限补全**：Pro及以上计划无限制
- **多语言**：支持主流编程语言

### 3.2 Agent Mode（2025年上线）
- **Copilot编程代理**：后台自主编写代码、创建PR、响应反馈
- **Issue分配**：可将Issue分配给Copilot、Claude或Codex代理处理
- **编辑器Agent**：解释概念、完成代码、提出编辑、验证文件

### 3.3 多模型支持
| 模型 | 提供商 | 计划要求 |
|------|--------|---------|
| GPT-5 mini | OpenAI | Free+ |
| Haiku 4.5 | Anthropic | Free+ |
| Claude Opus 4.6 | Anthropic | Pro+ |
| Codex | OpenAI | Pro+ |

可按速度、准确性或成本需求切换模型。

### 3.4 Workspace功能
- **Copilot Spaces**：团队共享知识库，整合文档和仓库上下文
- **MCP服务器**：支持连接自定义MCP服务器（企业可管控允许列表）
- **企业代码库索引**：Enterprise可索引组织代码，提供更精准建议

### 3.5 集成生态
- **IDE**：VS Code、Visual Studio、JetBrains、Xcode、Neovim
- **GitHub**：PR/Issue深度集成
- **终端**：Copilot CLI，自然语言指挥工作流
- **移动**：GitHub Mobile App
- **聊天**：GitHub.com内原生聊天

## 四、安全与合规
- 企业管理员可从单一控制平面管理代理使用
- 活动日志追踪
- 治理策略执行
- IP赔偿（Enterprise独有）
- 策略管理（Business+）

## 五、关键数据
- 被Coca-Cola、Shopify、Stripe、Duolingo等企业采用
- 市场占有率最高的AI编程工具
- 与GitHub 400M+仓库深度集成

## 六、与CodeBuddy对标

| 维度 | GitHub Copilot | CodeBuddy |
|------|---------------|-----------|
| 定价 | $10-39/月 | 免费 |
| 补全 | ✅ 无限（Pro+） | ✅ |
| Agent | ✅ 可分配Issue | ✅ 多Agent团队 |
| 多模型 | ✅ 4+ | ✅ |
| MCP | ✅ | ✅ |
| 部署 | ❌ | ✅ AnyDev |
| 国内合规 | ⚠️ 有限 | ✅ |
| GitHub集成 | ✅ 原生 | ❌ |
