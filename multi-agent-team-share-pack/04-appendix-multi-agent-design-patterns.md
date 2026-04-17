# 🏗️ 多智能体团队设计模式

> 标签：#multi-agent #architecture #team-design
> 蒸馏来源：multi-agent-framework 项目（6+版本设计经验）
> 创建：2026-03-21 | 验证次数：4

---

## 核心模式

### 模式 1: 三层管控架构

```
PM Agent（战略层）
  └→ Orchestrator Agent（调度层）
       └→ GateKeeper Agent（质量层）
            └→ 执行 Agent 群（执行层）
```

**适用场景**：任何需要多Agent协作的复杂任务
**核心原则**：
- PM 只管方向和最终验收，不参与具体执行
- Orchestrator 负责任务分解、调度、冲突仲裁
- GateKeeper 在每个 Phase 结束时进行质量门控

---

### 模式 2: 阶段流水线（Phase Pipeline）

**通用五阶段**：
```
Phase 1: 采集（收集信息/数据/需求）
Phase 2: 分析（多维深度分析）
Phase 3: 综合（洞察提炼 + 策略生成）
Phase 4: 验证（批判审查 + 事实核查）
Phase 5: 交付（专业化输出）
```

**经验法则**：
- 每阶段内的 Agent 可并行执行
- 阶段间通过质量门控串行推进
- 验证失败可回溯至任意前序阶段

---

### 模式 3: 贯穿型 Agent（Cross-Phase Agents）

**黄金配比**：贯穿型 Agent ≤ 5 个（避免通信复杂度爆炸）

**推荐的 5 类贯穿角色**：
1. **理论验证者**（TheoryAgent）— 全程用第一性原理校准
2. **前沿追踪者**（ExplorerAgent）— 持续引入新视角
3. **记忆管理者**（MemoryAgent）— 维护上下文和中间成果
4. **一致性守护者**（ConsistencyAgent）— 保障术语/风格统一
5. **质量监督者**（IntegrityAgent）— 全程合规/诚信监控

---

### 模式 4: 场景映射（Scenario Mapping）

**设计一套通用骨架，按场景替换角色**：

| 通用角色 | 调研报告 | 技术选型 | 学术论文 |
|---------|---------|---------|---------|
| SearchAgent | LitReviewAgent | TechScoutAgent | LitSurveyAgent |
| CompareAgent | CompetitorAgent | BenchmarkAgent | ComparativeAgent |
| WriterAgent | ReportWriterAgent | DocAgent | PaperWriterAgent |
| CriticAgent | PeerReviewAgent | SecurityAgent | InternalReviewAgent |

---

## 设计反模式（Anti-Patterns）

### ❌ Agent 过载
- **问题**：单个 Phase 超过 7 个 Agent → 通信复杂度 O(n²)
- **解决**：拆分为子 Phase 或合并职责相近的 Agent

### ❌ 缺少采集层
- **问题**：直接从分析开始，数据来源不明
- **解决**：始终从 Phase 1 信息采集开始

### ❌ 单向管道
- **问题**：没有反馈循环，验证发现问题无法修正
- **解决**：Phase 4 验证失败必须支持回溯

### ❌ 无记忆设计
- **问题**：Agent 之间没有共享上下文，重复工作
- **解决**：MemoryAgent 维护全局知识图谱

---

## 经验数据

| 指标 | 推荐范围 |
|------|---------|
| 总 Agent 数 | 14~44 |
| 每 Phase Agent 数 | 2~7 |
| 贯穿型 Agent 数 | 3~5 |
| Phase 数 | 5~7 |
| 质量门控数 | = Phase 数 |
