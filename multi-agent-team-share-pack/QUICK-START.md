# 🚀 快速上手指南（3 分钟开始）

---

## Step 1：选择你的场景

| 我要做的事 | 使用哪个文件 | 对 AI 说什么 |
|-----------|------------|-------------|
| 行业调研/竞品分析/咨询报告 | `00-framework-overview.md`（第三章） | "参考咨询报告版本，帮我调研[课题]" |
| 技术选型/架构评审 | `00-framework-overview.md`（第四章） | "参考技术选型版本，评估[技术A vs 技术B]" |
| 产品规划/需求分析 | `00-framework-overview.md`（第五章） | "参考产品规划版本，规划[产品名称]" |
| 商业计划书/融资BP | `00-framework-overview.md`（第七章） | "参考商业计划版本，写[项目]BP" |
| **学术论文** | `01-academic-paper-writing-team.md` | "参考学术论文团队，从[研究方向]开始" |
| **专利申请** | `02-patent-application-team.md` | "参考专利申请团队，对[技术方案]进行专利挖掘" |
| **漫剧创作** | `03-comic-drama-creation-team.md` | "参考漫剧团队，创作关于[主题]的漫剧" |
| 不确定 | `00-framework-overview.md`（第二章） | "参考通用版架构，帮我分析[任务]" |

---

## Step 2：在 CodeBuddy 中使用

### 最简用法（复制粘贴即可）

**写调研报告**：
```
请参考 @00-framework-overview.md 中「调研与咨询报告版本」的多Agent架构，
帮我完成一个关于「中国新能源汽车出海东南亚市场」的深度调研报告。
按 Phase 1→Phase 5 的流程逐步推进，每个 Phase 结束后等我确认再继续。
```

**写学术论文**：
```
请参考 @01-academic-paper-writing-team.md 的 39 Agent 架构，
帮我从「大语言模型在教育领域的应用」这个方向开始学术论文写作流程。
先执行 Phase 0（研究定位），识别研究空白和可行的研究问题。
```

**专利申请**：
```
请参考 @02-patent-application-team.md 的专利申请架构，
对以下技术方案进行专利挖掘：[粘贴你的技术方案描述]
遵循 2026 年最新审查指南标准，按 Phase 0 开始评估专利性。
```

**漫剧创作**：
```
请参考 @03-comic-drama-creation-team.md 的漫剧创作架构，
帮我创作一部关于「程序员第一次带娃」的搞笑漫剧。
目标平台：微信公众号，8格条漫，日系Q版画风。
使用方案A（最经济，¥0）。
```

---

## Step 3：理解协作流程

所有团队都遵循相同的基本流程：

```
1️⃣ PM Agent 确认方向
    ↓
2️⃣ Orchestrator 分解任务、调度 Agent
    ↓
3️⃣ Phase 0 → Phase N 逐步推进
    ↓  （每个 Phase 结束有 Gate 质量检查）
4️⃣ 贯穿型 Agent 持续守护（一致性/记忆/理论验证）
    ↓
5️⃣ 最终交付物 → PM 终审
```

**关键点**：
- 🚪 **Gate 不通过** → 回退到之前的 Phase 修正
- 🔄 **反馈循环** → 后续阶段发现问题可回溯
- 🧠 **MemoryAgent** → 全程记住已做的决策和中间成果

---

## 💡 进阶技巧

1. **分步执行**：告诉 AI "每个 Phase 做完后暂停等我确认"，这样你可以在过程中调整方向
2. **指定模型**：对质量要求高的任务，可以说 "管控层用 Claude-Opus-4.6"
3. **并行加速**：同 Phase 内的 Agent 可以并行，告诉 AI "Phase 2 的 A5-A9 可以并行执行"
4. **自定义 Agent**：你可以根据需要增减 Agent，框架是灵活的
5. **提取 Prompt**：文档中的 Prompt 模板可以单独用于任何 AI 工具

---

## ❓ FAQ

**Q: 必须用 CodeBuddy 吗？**
A: 不必须。文档中的 Agent 定义和 Prompt 模板可以用于任何 AI 工具（ChatGPT、Claude、Gemini 等），但 CodeBuddy 支持文件引用（@符号），使用最方便。

**Q: 模型费用多少？**
A: 默认使用 CodeBuddy 内置国产模型，**完全免费**。详见 `00-framework-overview.md` 第十章。

**Q: 漫剧创作需要 GPU 吗？**
A: 方案 A（CodeBuddy image_gen）不需要，方案 B（SD+InstantID 人像克隆）需要 NVIDIA 8GB+ GPU。

**Q: 专利文档适用哪个国家？**
A: 主要适配中国 CNIPA 标准（含 2026 年最新审查指南），PCT 国际申请也有覆盖。

---

*开始你的多智能体之旅吧！🚀*
