# 🔍 AI产品竞品调研分析团队（Competitive Research & Analysis Team）

> **从一个调研需求，到一份可用于战略规划的深度竞品分析报告** —— 可复用、可周期性执行的多Agent竞品调研框架。
> 
> **提炼自**：华为AI专业服务调研实战（2026-03-27，5 Agent并行，产出5份文档）
> **适用对象**：Claude Code / 火山引擎 / 阿里云 / AWS / Google Cloud / 任意ToB竞品

---

## 一、设计理念与复盘总结

### 1.1 实战复盘：华为调研过程

```
Step 1: 读取已有调研素材（华为调研.txt + 目录下其他文件）
Step 2: 创建team，规划5个并行Agent分工
Step 3: 4个文件调研Agent并行启动（产品体系/平台生态/交付方法论/生态培养）
Step 4: 1个网页浏览Agent启动（Chrome DevTools浏览13个华为云页面）
Step 5: 主Agent同时进行网络搜索（最新新闻、战略发布、产品更新）
Step 6: 汇总所有Agent成果 + 网络搜索信息 → 生成4份中间文档 + 1份最终报告
Step 7: Agent提交补充信息后更新文档（定价/SKU/内部数据/方法论细节）
```

### 1.2 实战经验提炼

| 经验 | 说明 | 框架化方法 |
|------|------|-----------|
| **并行是核心** | 5个Agent并行比串行快5倍 | 按调研维度拆分Agent，Phase1全并行 |
| **素材先行** | 已有文件提供60%信息 | Phase0读取所有已有素材 |
| **网页浏览补全** | 官网页面提供精确定价/SKU | 专设web-researcher浏览官网 |
| **网络搜索补新** | 最新发布会/新闻补时效性 | 主Agent或Explorer补充最新信息 |
| **中间文档保留** | 分维度MD便于后续深入分析 | 每个维度独立输出MD |
| **团队消息汇总** | Agent间协作补充交叉发现 | 允许Agent间send_message补充 |
| **定价是关键** | 竞品定价信息决策价值最高 | 专门采集定价/SKU/套餐信息 |

### 1.3 核心设计原则

```
┌──────────────────────────────────────────────────────────┐
│  竞品调研团队 6 大设计原则                                   │
├──────────────────────────────────────────────────────────┤
│  1. 并行采集  — 按调研维度拆分Agent，Phase1内全部并行执行    │
│  2. 多源交叉  — 文件+网页+搜索+知识库，≥3个独立信息源       │
│  3. 维度MECE — 产品/平台/交付/生态/定价，完全穷尽不重叠     │
│  4. 中间保留  — 每个维度输出独立MD，便于后续深入和周期对比    │
│  5. 对标导向  — 始终对标自身产品，输出差距/机会/建议         │
│  6. 可复用    — 替换目标公司名即可复用，支持周期性执行        │
└──────────────────────────────────────────────────────────┘
```

---

## 二、架构全景图

```
╔══════════════════════════════════════════════════════════════════════╗
║                   🎯 PM Agent（调研负责人/Main）                      ║
║        调研目标确认 │ 维度规划 │ 信息汇总 │ 报告审核 │ 建议输出         ║
╚═════════════════════════════╤════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║              Phase 0: 素材准备与调研规划（串行，PM执行）                ║
║    读取已有素材 │ 确定调研范围 │ 规划Agent分工 │ 创建Team              ║
╚═════════════════════════════╤════════════════════════════════════════╝
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
╔══════════════════════════════════════════════════════════════════════╗
║              Phase 1: 多维并行信息采集（全部并行！）                    ║
║                                                                    ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               ║
║  │ A1 产品体系   │ │ A2 平台生态   │ │ A3 交付方法论  │               ║
║  │ Researcher   │ │ Researcher   │ │ Researcher   │               ║
║  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘               ║
║         │                │                │                        ║
║  ┌──────┴───────┐ ┌──────┴───────┐ ┌──────┴───────┐               ║
║  │ A4 生态人才   │ │ A5 网页浏览   │ │ PM: 网络搜索  │               ║
║  │ Researcher   │ │ Web-Reader   │ │ (最新动态补充) │               ║
║  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘               ║
║         └────────────────┼────────────────┘                        ║
╚═════════════════════════════╤════════════════════════════════════════╝
                              │  🚪Gate1: 信息覆盖率检查
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║              Phase 2: 分析与对标（PM汇总+结构化）                      ║
║                                                                    ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               ║
║  │ 产品矩阵对标  │ │ 能力差距分析  │ │ 定价对标分析  │               ║
║  └──────────────┘ └──────────────┘ └──────────────┘               ║
╚═════════════════════════════╤════════════════════════════════════════╝
                              │  🚪Gate2: 分析完整性检查
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║              Phase 3: 报告生成（PM执行）                              ║
║                                                                    ║
║  中间文档生成（4-5份维度MD） + 最终综合报告生成（1份总报告）           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 三、Agent角色定义

### 3.1 管控层（PM = Main Agent）

PM即主对话Agent本身，负责：
- Phase 0: 读取素材、规划分工
- Phase 1: 同步进行网络搜索补充最新信息
- Phase 2: 汇总所有Agent成果进行分析
- Phase 3: 生成最终报告和中间文档

### 3.2 Phase 1 并行采集Agent

| Agent | 角色 | 调研维度 | 核心任务 | subagent_name |
|-------|------|---------|---------|---------------|
| **A1** | 产品体系研究员 | 专业服务/产品目录 | 服务分类、服务内容、定价、SKU、交付标准 | `code-explorer` |
| **A2** | 平台生态研究员 | 平台产品/工具链 | 核心平台产品功能、技术架构、产品路线图 | `code-explorer` |
| **A3** | 交付方法论研究员 | 交付模式/方法论 | 服务交付流程、方法论体系、组织架构 | `code-explorer` |
| **A4** | 生态人才研究员 | 生态/培训/合作 | 人才培养、合作伙伴、客户运营、案例 | `code-explorer` |
| **A5** | 网页浏览研究员 | 官网页面精确信息 | 通过Chrome DevTools浏览官网获取详细内容 | `code-explorer` |

---

## 四、可复用的Command模板

### 4.1 创建团队

```
team_create: {target}-ai-research
description: {target}AI类产品专业服务解决方案深度调研团队
```

### 4.2 Agent Prompt 模板

#### A1: 产品体系研究员

```markdown
你是{target}AI专业服务产品体系调研专家。

## 背景
我们正在为腾讯云AI产品（CodeBuddy、ADP）的专业服务规划做竞品调研，
需要深入了解{target}AI类专业服务的完整产品体系。

## 已有信息
文件 {input_file} 中包含已有调研信息和关键URL。

## 调研维度
1. 完整的AI专业服务产品目录和分类体系
2. 每个产品的服务内容、适用客户、交付模式
3. 定价信息（人天价格、套餐价格）
4. 服务分级（基础版/标准版/专业版等）
5. 与平台产品的配套关系

## 你的任务
1. 读取 {input_file} 获取已有信息
2. 读取目录下其他相关文件
3. 整理完整产品目录、分类、定价
4. 完成后将报告发送给main
```

#### A2: 平台生态研究员

```markdown
你是{target}AI平台产品与工具链调研专家。

## 调研维度
1. 核心AI开发平台（对标ModelArts/TI平台）
2. AI编程工具（对标CodeBuddy）
3. 大模型战略（对标混元）
4. 智能体开发平台（对标ADP/元器）
5. AI基础设施（算力、芯片）
6. "平台+专业服务"结合模式
7. 与腾讯云CodeBuddy/ADP的对标关系

## 你的任务
1. 读取已有素材
2. 整理平台产品全景图
3. 分析"平台+服务"结合模式
4. 输出与腾讯云对标分析
```

#### A3: 交付方法论研究员

```markdown
你是{target}AI专业服务交付模式与方法论调研专家。

## 调研维度
1. 标准交付流程（从咨询到运营）
2. 核心服务方法论（人机协同、知识封装等）
3. 模型优化方法论
4. 交付组织架构与关键角色
5. 分层服务策略（大客户vs中小客户）
6. 知识沉淀和复用机制

## 你的任务
1. 读取已有素材
2. 整理交付模式、方法论体系
3. 分析对腾讯云FDE团队的借鉴意义
```

#### A4: 生态人才研究员

```markdown
你是{target}AI生态与人才培养体系调研专家。

## 调研维度
1. 人才培养体系（培训、认证、大赛）
2. 合作伙伴生态（ISV/SI/开发者）
3. 客户运营模式（内容、案例、活动）
4. 降低AI门槛的策略
5. Marketplace/生态市场
6. 对腾讯云的借鉴意义

## 你的任务
1. 读取已有素材
2. 整理生态与人才培养完整体系
3. 输出借鉴建议
```

#### A5: 网页浏览研究员

```markdown
你是网络调研专家。请通过Chrome DevTools浏览{target}关键网页。

## 需要浏览的URL列表
{url_list}

## 你的任务
对每个网页：
1. 使用navigate_page打开URL
2. 使用take_snapshot获取页面文本内容
3. 提取关键信息（服务名称、描述、定价、场景等）

## 输出格式
### [服务名称]
- URL: xxx
- 服务定位: xxx
- 服务内容: xxx
- 适用客户: xxx
- 定价: xxx
- 亮点: xxx
```

### 4.3 PM网络搜索模板

PM在Phase 1同步执行的搜索：

```
搜索1: {target} AI专业服务 2025 2026 产品体系 最新动态
搜索2: {target} 大模型 智能体 2026 专业服务 解决方案
搜索3: {target} AI编程 开发平台 专业服务 2025 2026
搜索4: {target} AI生态 人才培养 合作伙伴 认证
```

### 4.4 网页深度获取模板

对搜索结果中有价值的URL执行web_fetch：

```
web_fetch: {url} → 获取{target}AI相关详细内容
```

---

## 五、输出文档模板

### 5.1 中间文档结构（每个维度一份）

```markdown
# {target} {维度名称} 调研

> 调研时间：{date}
> 数据截止：{date}

## 一、{维度}总览
## 二、详细分析
## 三、关键数据
## 四、与腾讯云对标分析
## 五、关键启示

*数据来源：xxx*
```

### 5.2 最终报告结构

```markdown
# {target} AI类产品专业服务解决方案深度调研报告

> 报告类型：竞品分析调研报告
> 调研时间：{date}

## 目录
## 摘要（核心发现 + 对腾讯云建议）
## 第一章 {target} AI战略全景
## 第二章 AI专业服务产品体系
## 第三章 AI平台产品生态
## 第四章 交付模式与方法论
## 第五章 生态与人才培养体系
## 第六章 竞品对标分析（{target} vs 腾讯云）
## 第七章 对腾讯云的启示与建议（P0/P1/P2分级）
## 附录（URL汇总、定价表、关键数据）
```

---

## 六、各竞品调研实例化配置

### 6.1 火山引擎（字节跳动）

```yaml
target: 火山引擎
team_name: volcengine-ai-research
input_file: d:\AI\DSTE\洞察和调研\火山AI专业服务*.txt
key_products:
  - 火山方舟(大模型平台)
  - MarsCode(AI编程) → 对标CodeBuddy
  - 扣子/Coze(Agent平台) → 对标ADP
  - 豆包(大模型)
  - HiAgent(企业Agent工作站)
key_urls:
  - https://www.volcengine.com/product/ark
  - https://www.marscode.cn/
  - https://www.coze.cn/
  - https://www.volcengine.com/solutions/ai
search_keywords:
  - "火山引擎 AI专业服务 方舟 2026"
  - "MarsCode 企业版 专业服务 交付"
  - "火山引擎 Coze 智能体 企业服务"
  - "字节跳动 AI ToB 专业服务 生态"
focus_analysis:
  - MarsCode vs CodeBuddy 功能/生态/企业版对比
  - 火山方舟 vs TI平台 对比
  - 字节内部研发实践对外输出模式
  - 火山引擎交付服务（PS）体系
```

### 6.2 阿里云

```yaml
target: 阿里云
team_name: alicloud-ai-research
input_file: d:\AI\DSTE\洞察和调研\*阿里*.txt
key_products:
  - 百炼(大模型平台)
  - 通义灵码(AI编程) → 对标CodeBuddy
  - PAI(ML平台)
  - 通义千问/Qwen(大模型)
  - 智能体开发
key_urls:
  - https://bailian.console.aliyun.com/
  - https://tongyi.aliyun.com/lingma
  - https://www.aliyun.com/product/ai
  - https://help.aliyun.com/product/2400256.html
search_keywords:
  - "阿里云 AI专业服务 百炼 通义 2026"
  - "通义灵码 企业版 专业服务 交付"
  - "阿里云 PAI 专家服务 咨询"
  - "阿里云 AI 培训 认证 合作伙伴"
focus_analysis:
  - 通义灵码 vs CodeBuddy 功能/生态/企业版对比
  - 百炼 vs TI平台 对比
  - 阿里云专家服务体系（最成熟的国内对标）
  - PAI平台+专业服务结合模式
```

### 6.3 AWS

```yaml
target: AWS
team_name: aws-ai-research
input_file: d:\AI\DSTE\洞察和调研\*aws*.txt
key_products:
  - SageMaker(ML平台)
  - Amazon Q Developer(AI编程) → 对标CodeBuddy
  - Bedrock(大模型平台)
  - AWS Professional Services
  - Amazon Q Business(企业Agent)
key_urls:
  - https://aws.amazon.com/professional-services/
  - https://aws.amazon.com/q/developer/
  - https://aws.amazon.com/bedrock/
  - https://aws.amazon.com/sagemaker/
search_keywords:
  - "AWS AI Professional Services 2026"
  - "Amazon Q Developer enterprise"
  - "AWS Bedrock professional services delivery"
  - "AWS AI training certification partner"
focus_analysis:
  - Amazon Q Developer vs CodeBuddy 对比
  - AWS Professional Services完整服务目录
  - AWS AI/ML认证体系
  - AWS合作伙伴网络(APN)中的AI专项
```

### 6.4 Claude Code (Anthropic)

```yaml
target: Anthropic Claude
team_name: claude-ai-research
input_file: null  # 无本地文件，主要靠网络搜索
key_products:
  - Claude Code(AI编程CLI) → 直接竞品
  - Claude API/Enterprise
  - Claude for Work
  - MCP(Model Context Protocol)
key_urls:
  - https://docs.anthropic.com/en/docs/claude-code
  - https://www.anthropic.com/enterprise
  - https://www.anthropic.com/claude
  - https://modelcontextprotocol.io/
search_keywords:
  - "Claude Code enterprise features 2026"
  - "Anthropic professional services enterprise"
  - "Claude Code vs Cursor vs CodeBuddy"
  - "MCP Model Context Protocol ecosystem"
focus_analysis:
  - Claude Code vs CodeBuddy 功能/体验/生态对比
  - MCP协议生态 vs CodeBuddy Skills
  - Anthropic企业版服务（有无专业服务？）
  - Claude Code的定价与商业模式
```

---

## 七、周期性执行方案

### 7.1 执行频率建议

| 类型 | 频率 | 触发条件 |
|------|------|---------|
| 全量调研 | 每季度1次 | Q1/Q2/Q3/Q4首月 |
| 增量更新 | 每月1次 | 每月第一个工作日 |
| 热点追踪 | 即时 | 竞品发布会/重大产品更新/融资事件 |

### 7.2 增量更新模式

增量更新时不需要全量调研，只需：
1. 搜索最近30天的竞品新闻和产品更新
2. 浏览竞品官网检查新产品/功能发布
3. 与上一期报告对比，标注变化点
4. 更新中间文档中变化的部分
5. 在最终报告中增加"本期更新"章节

### 7.3 自动化Automation配置

```toml
# 季度全量调研
name = "竞品AI全量调研"
prompt = "执行竞品全量调研，目标：华为/火山/阿里/AWS/Claude。读取上期报告作为基线，按竞品调研框架执行，生成更新后的调研报告。"
rrule = "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0"  # 需手动调整为季度首周
status = "PAUSED"

# 月度增量更新
name = "竞品AI月度追踪"
prompt = "执行竞品月度增量追踪，搜索最近30天华为/火山/阿里/AWS/Claude的AI产品和专业服务动态，与上期报告对比，输出变化摘要。"
rrule = "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0"  # 每月第一个周一
status = "PAUSED"
```

---

## 八、质量检查清单

```
┌──────────────────────────────────────────────────────────┐
│  🚪 竞品调研质量门控                                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Gate 1（信息采集完整性）                                  │
│  ☐ 产品目录覆盖完整（无遗漏核心产品）                       │
│  ☐ 信息来源≥3个独立渠道（官网+文档+新闻）                   │
│  ☐ 包含最新信息（≤30天内的动态）                           │
│  ☐ 关键定价/SKU信息已采集                                  │
│                                                          │
│  Gate 2（分析对标完整性）                                  │
│  ☐ 每个维度都有与腾讯云的对标                              │
│  ☐ 差距分析具体可量化                                     │
│  ☐ 建议按P0/P1/P2分优先级                                 │
│  ☐ 无主观臆断（区分事实与推测）                            │
│                                                          │
│  Gate 3（报告质量）                                       │
│  ☐ 中间文档（4-5份）全部生成                              │
│  ☐ 最终报告结构完整（7章+附录）                           │
│  ☐ 关键URL已汇总                                         │
│  ☐ 数据来源已标注                                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 九、Quick Start（快速启动指南）

### 一句话启动命令

```
对{target}AI类产品专业服务解决方案进行深度调研，基于{input_file}，
网页可通过chromedev浏览，所有中间内容保留单独md，
最终生成详尽的调研报告用于竞品分析和为腾讯云AI产品专业服务规划提供输入（CodeBuddy、ADP）。
```

### 变量替换表

| 变量 | 华为 | 火山 | 阿里 | AWS | Claude |
|------|------|------|------|-----|--------|
| `{target}` | 华为云 | 火山引擎 | 阿里云 | AWS | Anthropic Claude |
| `{team_name}` | huawei-ai-research | volcengine-ai-research | alicloud-ai-research | aws-ai-research | claude-ai-research |
| `{input_file}` | 华为调研.txt | 火山AI专业服务*.txt | *阿里*.txt | *aws*.txt | (无，纯网络) |
| `{output_dir}` | 华为AI专业服务调研/ | 火山AI专业服务调研/ | 阿里AI专业服务调研/ | AWS-AI专业服务调研/ | Claude-AI调研/ |

### 完整执行命令示例（火山引擎）

```
生成一个ai teams，规划对火山引擎AI类产品专业服务解决方案的调研，
最终生成详尽的调研报告用于竞品分析和为腾讯云AI产品专业服务规划提供输入（CodeBuddy、ADP），
基于d:\AI\DSTE\洞察和调研\火山AI专业服务*.txt，
重点对比MarsCode vs CodeBuddy、Coze/扣子 vs ADP，
网页可通过chromedev去打开和浏览具体内容，所有中间内容保留单独md后续进一步分析
```

---

## 十、与通用框架的关系

本框架是 `multi-agent-research-framework` 中 **"咨询报告版本"** 的竞品调研特化：

| 通用框架Agent | 本框架映射 | 说明 |
|-------------|-----------|------|
| PM Agent | Main Agent | 主对话直接充当PM |
| A5 MarketAgent | A1 产品体系 | 聚焦产品目录而非市场规模 |
| A6 IndustryAgent | A2 平台生态 | 聚焦技术平台而非产业链 |
| A7 CompetitorAgent | A3 交付方法论 | 聚焦交付模式而非SWOT |
| A12 BenchmarkAgent | A4 生态人才 | 聚焦生态建设而非标杆案例 |
| A3 DataMiningAgent | A5 Web-Reader | 通过Chrome浏览器采集 |
| ExplorerAgent | PM网络搜索 | 主Agent兼任前沿追踪 |
| WriterAgent | PM | 主Agent直接生成报告 |

**简化原因**：CodeBuddy Team模式下，Agent数量受限（推荐≤6），故将通用框架的19个Agent压缩为5个并行Agent+1个PM，通过提高单Agent的Prompt质量弥补数量不足。

---

*框架版本：v1.0*
*提炼自：华为AI专业服务调研实战（2026-03-27）*
*适用范围：任意ToB AI竞品的专业服务调研分析*
*作者：multi-agent-research-framework扩展*
