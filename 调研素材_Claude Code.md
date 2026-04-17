# 调研素材 — Claude Code（Anthropic）

> 调研时间：2026年3月27日
> 产品官网：https://claude.com/product/claude-code

---

## 一、产品概述

Claude Code 是 Anthropic 推出的终端原生AI编程代理（非IDE插件），于2025年发布后迅速成为AI编程工具市场的头部产品。上线6个月 ARR 达 $1B，推动 Anthropic 整体 ARR 达 $14B。

## 二、核心能力

### 2.1 基础能力
- **代码入库**：智能搜索，几秒内映射和解释整个代码库
- **多文件编辑**：基于对代码库和依赖项的深度理解，执行有效的多文件协同更改
- **模型**：Opus 4.6 / Sonnet 4.6

### 2.2 Agent能力
- **后台Agent**：配合Git Worktree，每个Agent在代码独立副本中工作
- **/loop定时任务**：类似Cron，自然语言描述任务和间隔
  - 示例：`/loop 5m check if the staging deployment was successful`
  - 限制：每会话最多50个并发任务，3天后自动过期
- **Auto Mode**（2026.3新增）：介于"每个操作都批准"和"完全跳过权限"之间的安全模式

### 2.3 独特能力
- **Computer Use**：直接控制macOS桌面，像人类一样操作鼠标、点击、浏览网页
  - 仅限Pro和Max计划的研究预览版
  - 目前仅支持macOS
- **Voice Mode**：20种语言Push-to-Talk
- **Remote Control**：通过Web/iOS/Android远程控制本地终端会话
- **1M Token上下文**：Max/Team/Enterprise计划支持

## 三、平台支持

| 平台 | 支持方式 |
|------|---------|
| 桌面端 | Claude桌面应用，多任务管理、可视化diff、PR监控 |
| 终端 | 原生命令行，直接与模型API通信 |
| IDE | VS Code扩展（含Cursor/Windsurf）、JetBrains扩展 |
| Web | claude.ai/code（研究预览） |
| iOS | Claude App远程控制 |
| Slack | Slack应用集成 |

## 四、定价方案

| 方案 | 月费 | 年付月费 | 核心权益 |
|------|------|---------|---------|
| Pro | $20 | $17 | Claude Code，小代码库短期冲刺，Sonnet 4.6+Opus 4.6 |
| Max (5x) | $100 | — | 大代码库日常使用 |
| Max (20x) | $200 | — | 最大用量 |
| API | 按量 | — | 无席位费，标准API定价 |
| Team | $20/人 | — | 标准版+高级席位，自助管理 |
| Enterprise | 定制 | — | 高级安全+数据管理 |

**快速模式**：Opus 4.6高速配置，2.5倍速度，$30/$150 per million tokens。

## 五、安全架构
- **本地运行**：终端本地运行，直接与模型API通信
- **无需后端**：不需要后端服务器或远程代码索引
- **权限控制**：未经明确批准从不修改文件
- **数据不离开**：Remote Control仅传输聊天消息，代码始终本地

## 六、关键数据
- 部署频率提升 **7.6倍**
- 周环比部署增长 **14%**
- 交付功能和修复速度 **2倍**
- 员工AI采用率 **89%**

## 七、与CodeBuddy对标

| 维度 | Claude Code | CodeBuddy |
|------|-------------|-----------|
| 定价 | $20-200/月 | 免费（含IDE） |
| 上下文 | 1M Token | 标准 |
| Agent | 单Agent+后台 | 多Agent团队 |
| 终端 | 原生 | 支持 |
| IDE | 插件式 | 原生内置 |
| 多模型 | Anthropic only | 多模型 |
| 部署 | ❌ | ✅ AnyDev |
| 国内合规 | ❌ | ✅ |
