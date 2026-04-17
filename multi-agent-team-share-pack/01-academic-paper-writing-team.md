# 📚 学术论文撰写多 Agent 团队（Academic Paper Writing Multi-Agent Team）

> **从一个模糊的研究想法，到一篇可投稿的学术论文** —— 39 个专业化智能体，7 个阶段，全流程覆盖。

---

## 📑 目录

- [一、概述与设计理念](#一概述与设计理念)
- [二、完整架构全景图](#二完整架构全景图)
- [三、管控层：PM + Orchestrator](#三管控层pm--orchestrator)
- [四、Phase 0 ~ Phase 6 详解](#四phase-0研究定位)
- [十一、贯穿型智能体](#十一贯穿型智能体)
- [十二、论文类型适配矩阵](#十二论文类型适配矩阵)
- [十三、质量门控与评分体系](#十三质量门控与评分体系)
- [十四、核心 Agent Prompt 模板](#十四核心-agent-prompt-模板)
- [十五、Agent 间协作协议](#十五agent-间协作协议与数据流)
- [十六、工具生态对接](#十六工具生态对接方案)
- [十七、论文写作状态机](#十七论文写作状态机)

---

## 一、概述与设计理念

### 1.1 原始版 vs 完善版对比

| 维度 | 原始版（16 Agent） | 完善版（39 Agent） |
|------|-------------------|-------------------|
| **Phase 数** | 5 | **7**（新增研究定位 + 方法论设计独立） |
| **文献能力** | 1 个 LitSurvey | **5 个 Agent**（检索策略→系统检索→质量评估→关系映射→综合） |
| **方法论** | 1 个 Method | **4 个 Agent**（方法选择+数据设计+伦理审查+效度信度） |
| **写作粒度** | Abstract+Body | **7 个 Agent**（Intro/LitReview/Method/Results/Discussion/Abstract/Title 各专门化） |
| **投稿支持** | Format+Revision | **7 个 Agent**（内审+润色+查重+格式+选刊+CoverLetter+Rebuttal） |
| **贯穿 Agent** | 无 | **5 个**（导师模拟+学术诚信+一致性+双语+记忆） |
| **论文类型** | 未区分 | **5 种**类型适配（期刊/会议/学位/综述/短论文） |
| **质量门控** | 无 | **7 道 Gate** + 论文质量评分体系 |

### 1.2 核心设计原则

```
┌───────────────────────────────────────────────────────────────┐
│  🎓 学术论文 Agent 团队 8 大设计原则                              │
├───────────────────────────────────────────────────────────────┤
│  1. 学术严谨性优先  — 每个结论必须有证据链支撑                     │
│  2. 章节专门化     — 每个论文章节由专门 Agent 处理                 │
│  3. 文献驱动       — 文献工程作为独立 Phase 深度处理               │
│  4. 反向验证       — CounterArgAgent 持续攻击自身论证              │
│  5. 伦理前置       — 伦理审查在方法论设计阶段即介入                 │
│  6. 导师在环       — MentorAgent 模拟导师反馈贯穿全程              │
│  7. 投稿导向       — 从选题起即考虑目标期刊的 scope 和偏好          │
│  8. 迭代精进       — 支持多轮修改，Revision Loop 内建               │
└───────────────────────────────────────────────────────────────┘
```

---

## 二、完整架构全景图

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                       🎯 PM Agent（导师 / 课题负责人）                      ║
║           研究方向审定 │ 方法论把关 │ 阶段审查 │ 论文终审 │ 投稿决策           ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                │
                                ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                     🔄 Orchestrator（研究协调员）                           ║
║        研究计划管理 │ Agent 调度 │ 进度跟踪 │ 方向微调 │ 冲突仲裁             ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                │
  ┌──────────────┬──────────────┼──────────────┬──────────────┐
  │              │              │              │              │
  ▼              ▼              ▼              ▼              ▼
╔══════════╗ ╔══════════╗ ╔══════════╗ ╔══════════╗ ╔══════════╗
║ Phase 0   ║ ║ Phase 1   ║ ║ Phase 2   ║ ║ Phase 3   ║ ║ Phase 4   ║
║ 🔭研究定位 ║ ║ 📚文献工程 ║ ║ 🔬方法论  ║ ║ ⚗️研究执行 ║ ║ 🏗️论证构建 ║
║          ║ ║          ║ ║   设计    ║ ║          ║ ║          ║
║ A0 Scope ║ ║ A4 Search ║ ║ A9  Meth ║ ║ A13 Data ║ ║ A17 Arg  ║
║ A1 Gap   ║ ║ A5 Lit   ║ ║ A10 Data ║ ║ A14 Quan ║ ║ A18 Cont ║
║ A2 Hypo  ║ ║ A6 Qual  ║ ║ A11 Eth  ║ ║ A15 Qual ║ ║ A19 Limi ║
║ A3 Feas  ║ ║ A7 Map   ║ ║ A12 Vali ║ ║ A16 Vis  ║ ║ A20 Coun ║
║          ║ ║ A8 Synth ║ ║          ║ ║          ║ ║          ║
╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝
 🚪G0│        🚪G1│        🚪G2│        🚪G3│        🚪G4│
     └────────────┴────────────┴────────────┴────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
     ╔═════════════════╗              ╔════════════════════╗
     ║ Phase 5          ║              ║ Phase 6             ║
     ║ ✍️ 论文写作        ║              ║ ✅ 审校与投稿         ║
     ║                  ║              ║                    ║
     ║ A21 Intro        ║              ║ A28 InternalRev    ║
     ║ A22 LitRevWrite  ║              ║ A29 Language       ║
     ║ A23 MethodWrite  ║              ║ A30 Plagiarism     ║
     ║ A24 Result       ║  ──🚪G5──▶   ║ A31 Format         ║
     ║ A25 Discuss      ║              ║ A32 JournalMatch   ║
     ║ A26 Abstract     ║              ║ A33 CoverLetter    ║
     ║ A27 TitleKW      ║              ║ A34 Revision       ║
     ╚═════════════════╝              ╚═════════╤══════════╝
                                                │ 🚪G6
                                                ▼
                                      ╔══════════════════╗
                                      ║  📄 可投稿论文      ║
                                      ║  + Cover Letter   ║
                                      ║  + Highlights     ║
                                      ║  + Supplementary  ║
                                      ╚══════════════════╝

  ═══════════════  贯穿型智能体（Cross-Phase）  ═══════════════

  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ 👨‍🏫 C1 Mentor  │ │ 🛡️ C2 Integr │ │ 🔗 C3 Consist│ │ 🌐 C4 Transl │ │ 🧠 C5 Memory │
  │ 导师模拟器    │ │ 学术诚信监督  │ │ 一致性守护者  │ │ 双语翻译支持  │ │ 研究过程记忆  │
  │ 全程质疑引导  │ │ 全程合规监控  │ │ 术语/符号统一 │ │ 中英学术互译  │ │ 决策/版本追踪 │
  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

  ═══════════════  基础设施层（Infrastructure）  ═══════════════

  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │ 📖 Zotero/   │ │ 📊 SPSS/R/  │ │ 📝 Overleaf/ │ │ 🔍 Scopus/  │ │ 📨 Agent    │
  │ Mendeley     │ │ Python/     │ │ Word/LaTeX  │ │ WoS/Google  │ │ Message Bus │
  │ 文献管理      │ │ STATA       │ │ 排版工具     │ │ Scholar     │ │ 通信总线     │
  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 三、管控层：PM + Orchestrator

### PM Agent（导师/课题负责人）

| 维度 | 定义 |
|------|------|
| **角色** | 模拟学术导师或课题负责人 |
| **核心职责** | 审定研究方向 → 把关方法论 → 审查阶段产出 → 论文终审 → 投稿决策 |
| **介入时机** | Gate 0/1/2/4/5/6（关键里程碑审查） |
| **行为模式** | 苏格拉底式提问 + 批判性审查 + 战略指导 |

### Orchestrator Agent（研究协调员）

**调度策略——Phase 内并行规则：**
```
Phase 0: A0→(A1∥A3)→A2       # A1/A3可并行，A2依赖A1结果
Phase 1: A4→A5→(A6∥A7)→A8   # A6/A7可并行
Phase 2: A9→(A10∥A11∥A12)    # A10/A11/A12可并行
Phase 3: A13→(A14∥A15)→A16   # 定量/定性可并行
Phase 4: A17→A18→(A19∥A20)   # A19/A20可并行
Phase 5: A24→A23→A25→A21→A22→A26→A27  # 推荐写作顺序（非章节排列顺序）
Phase 6: A28→A29→A30→(A31∥A32)→A33    # 部分可并行
```

---

## 四、Phase 0：研究定位（Research Positioning）

> **目标**：将模糊的研究想法转化为聚焦、可研究、有价值的研究问题。

| Agent | 角色 | 核心职责 | 输出 |
|-------|------|---------|------|
| **A0 ScopeAgent** | 研究范围界定师 | 澄清研究兴趣、界定研究范围、识别关键概念与边界 | 研究范围说明书 |
| **A1 GapFinderAgent** | 研究空白发现者 | 快速扫描领域现状，识别理论/实证/方法论/情境/时间空白，评估研究价值 | 研究空白地图（按价值排序） |
| **A2 HypothesisAgent** | 研究假设生成器 | 将研究空白转化为研究问题（RQ），生成可检验假设（H），定义关键变量 | 研究问题集 + 假设集 + 变量定义表 |
| **A3 FeasibilityAgent** | 学术可行性评估师 | 评估数据可得性、方法可行性、时间资源需求、发表潜力 | 可行性评估报告 + Go/No-Go 建议 |

**🚪 Gate 0 检查项**：研究问题是否一句话清晰表述？假设是否可检验/可证伪？预期贡献是否明确？

---

## 五、Phase 1：文献工程（Literature Engineering）

> **目标**：系统性搜集、评估、组织和综合领域文献，构建坚实理论基础。

| Agent | 角色 | 核心职责 | 方法/工具 |
|-------|------|---------|----------|
| **A4 SearchStrategyAgent** | 检索策略设计师 | 设计关键词矩阵（同义词/上下位词）、选择数据库、构建布尔检索式、定义纳入/排除标准 | PICO/PEO 框架 |
| **A5 LitSurveyAgent** | 系统性文献检索员 | 执行数据库检索、雪球法、去重初筛、全文筛选、记录 PRISMA 流程图 | **PRISMA 2020 协议** |
| **A6 QualityAssessAgent** | 文献质量评估师 | 质量评估、偏倚风险评估、文献分级 | CASP/GRADE/Newcastle-Ottawa |
| **A7 LitMapAgent** | 文献关系映射师 | 构建引用网络图、主题聚类、时间线演化、识别核心文献和新兴主题 | 共引分析、书目耦合、Burst Detection |
| **A8 SynthesisAgent** | 文献综合师 | 提取核心发现、跨文献综合、识别一致性/矛盾、构建理论框架初稿 | 主题综合/框架综合/元叙事 |

### PRISMA 系统检索流程

```
识别 → 筛选 → 纳入：
数据库检索(n=xxx) + 其他来源(n=xxx)
    ↓ 去重(n=xxx)
    ↓ 标题+摘要筛选 → 排除(n=xxx, 原因:不相关)
    ↓ 全文筛选 → 排除(n=xxx, 原因:逐条列出)
    ↓ 质量评估(A6) + 关系映射(A7)
    ↓ 最终纳入(n=xx) → 文献综合(A8)
```

**🚪 Gate 1 检查项**：检索策略是否全面（≥3个数据库+雪球法）？PRISMA 流程完整？文献质量评估使用标准化工具？核心文献无遗漏？

---

## 六、Phase 2：方法论设计（Methodology Design）

> **目标**：设计严谨的研究方法，确保结果有效性和可靠性。

| Agent | 角色 | 核心职责 | 关键框架 |
|-------|------|---------|---------|
| **A9 MethodAgent** | 研究方法选择师 | 选择方法论范式（实证/诠释/实用）、选择研究策略、论证选择合理性 | Creswell 决策框架、Saunders 研究洋葱 |
| **A10 DataDesignAgent** | 数据采集方案设计师 | 确定抽样策略、计算样本量、设计采集工具（问卷/量表/访谈提纲） | G*Power、Likert 量表设计 |
| **A11 EthicsAgent** | 伦理审查师 | 知情同意书、数据保护（GDPR合规）、参与者风险评估、IRB 申请材料 | Belmont Report、赫尔辛基宣言 |
| **A12 ValidityAgent** | 效度与信度设计师 | 内容效度/构建效度/准则效度方案、信度方案（Cronbach's α）、编码者间信度（Cohen's κ） | 效度-信度矩阵、Pilot Study |

### 方法论选择决策树

```
研究问题 → "是什么"(描述性) → 案例研究/现象学/叙事 → 定性方法
        → "为什么/如何"(解释性) → 扎根理论/民族志/行动研究 → 定性方法
        → "多少/多大程度"(量化验证) → 调查/实验/准实验 → 定量方法
        → 需要多视角 → 混合方法（顺序解释/顺序探索/并行汇聚）
```

**🚪 Gate 2 检查项**：方法论范式与研究问题匹配？抽样与样本量恰当？效度信度措施完备？伦理审查满足要求？

---

## 七、Phase 3：研究执行（Research Execution）

> **目标**：严格按方法论设计执行研究，产出高质量分析结果。

| Agent | 角色 | 核心职责 | 工具 |
|-------|------|---------|------|
| **A13 DataCollectAgent** | 数据采集执行员 | 按方案采集数据、实时监控质量（缺失/异常）、数据清洗预处理 | SPSS/Excel/NVivo |
| **A14 QuantAnalysisAgent** | 定量分析师 | 描述统计、推断统计（t检验/ANOVA/χ²）、回归/SEM、中介调节效应、稳健性检验 | SPSS/R/Python/AMOS/Mplus/Stata |
| **A15 QualAnalysisAgent** | 定性分析师 | 开放/轴心/选择性编码、主题分析（Braun & Clarke 六步法）、框架分析、编码者间信度 | NVivo/ATLAS.ti/MAXQDA |
| **A16 VisualAgent** | 研究可视化师 | 统计图表、路径图/SEM模型图、概念框架图、编码树状图、APA格式表格 | matplotlib/ggplot2/draw.io |

**定量分析检查链**：缺失值处理 → 异常值检测 → 正态性检验 → 多重共线性（VIF<10）→ 同源方差检验 → 假设检验 → 稳健性检验

**🚪 Gate 3 检查项**：数据采集严格按方案执行？分析方法与数据匹配？稳健性检验通过？编码者间信度达标（κ>0.7）？无 p-hacking 风险？

---

## 八、Phase 4：论证构建（Argumentation）

> **目标**：基于分析结果构建严密学术论证，明确研究贡献。

| Agent | 角色 | 核心职责 | 核心框架 |
|-------|------|---------|---------|
| **A17 ArgumentAgent** | 核心论证架构师 | 提炼论点、按 Toulmin 模型构建论证链（Claim-Data-Warrant-Backing-Qualifier-Rebuttal） | **Toulmin 论证模型** |
| **A18 ContributionAgent** | 贡献定位师 | 明确理论贡献/实践贡献/方法论贡献，定位贡献层次（增量/渐进/突破） | Contribution Typology |
| **A19 LimitationAgent** | 局限性分析师 | 方法论局限/概念局限/范围局限分析，将局限性转化为未来研究方向 | Limitation→Future Research |
| **A20 CounterArgAgent** | 反论证师（🔴红队） | 尝试推翻自身结论、寻找替代解释、检查逻辑谬误、验证因果推断内部效度 | 逻辑谬误清单、反事实推理 |

### Toulmin 论证模型应用

```
Data（证据）───▶ [Qualifier（限定）] ───▶ Claim（主张）
  │                                        ▲
  │                                        │
  └──▶ Warrant（推理保证）──▶ Backing（理论支撑）
                                           │
                              Rebuttal（反驳预案）

示例：
  D: 采用X方法的组织绩效提升23% (p<0.01)
  W: 资源基础理论（RBV）— 独特资源配置是竞争优势来源
  B: Barney(1991) VRIO框架 + 50+后续实证支持
  Q: 在中型制造业企业情境下
  C: X方法通过优化资源配置显著提升组织绩效
  R: 高度动态环境中该效应可能被环境不确定性削弱
```

**🚪 Gate 4 检查项**：每个论点有完整 Toulmin 论证链？无逻辑谬误？替代解释已排除或讨论？贡献清晰有说服力？

---

## 九、Phase 5：论文写作（Paper Writing）

> **目标**：将研究成果转化为结构严谨、语言规范的学术论文。

### 推荐写作顺序（非章节排列顺序！）

```
1️⃣ A24 Results   → 先写结果（最客观，从数据出发）
2️⃣ A23 Method    → 再写方法（描述你做了什么）
3️⃣ A25 Discussion → 然后讨论（结果意味着什么）
4️⃣ A21 Intro     → 再写引言（为什么做这个研究）
5️⃣ A22 LitReview → 完善文献综述（根据讨论需要补充）
6️⃣ A26 Abstract  → 最后写摘要（全文浓缩）
7️⃣ A27 TitleKW   → 最终确定标题和关键词
```

### 各 Agent 详细定义

| Agent | 章节 | 结构框架 | 核心写作规范 |
|-------|------|---------|------------|
| **A21 IntroAgent** | Introduction | **Swales CARS 模型**：Establishing Territory → Establishing Niche → Occupying Niche | 倒三角结构：宏观背景→文献提要→研究空白→研究目的→贡献预告→结构导引 |
| **A22 LitReviewWriteAgent** | Literature Review | 主题式/年代式/方法式组织 | 综合批判而非罗列；每段结尾有综合评述；最终收束到 Research Gap；构建理论框架 |
| **A23 MethodWriteAgent** | Methodology | 研究设计→情境→抽样→数据采集→分析方法→效度信度→伦理 | **可复现性**：读者能据此完全复现你的研究 |
| **A24 ResultAgent** | Results | 定量：样本描述→测量模型→假设检验 / 定性：主题总览→逐主题详述→主题关系 | APA报告规范：*F*(2,147)=5.83, *p*=.004, η²=.07；效应量必报；置信区间优于单纯p值 |
| **A25 DiscussAgent** | Discussion | 发现总结→与文献对话→理论含义→实践启示→局限性→未来方向 | 每个发现与≥2篇文献对话；不一致结果提供解释；实践启示具体可操作 |
| **A26 AbstractAgent** | Abstract | 结构化摘要（150-300词）：Purpose→Design→Findings→Originality | 最后写；不引文献；不用缩写；每句最大信息密度 |
| **A27 TitleKeywordAgent** | Title+Keywords | 标题含关键变量+暗示方法论+体现创新点（10-15词） | 关键词5-7个；参考数据库索引词；兼顾发现性 |

**🚪 Gate 5 检查项**：Introduction 遵循 CARS 模型？Literature Review 综合批判而非罗列？Methodology 可复现？Results 完整报告统计量？Discussion 与文献充分对话？各章节逻辑连贯？

---

## 十、Phase 6：审校与投稿（Review & Submission）

> **目标**：打磨论文至可投稿状态，完成期刊选择和投稿准备。

| Agent | 角色 | 核心职责 |
|-------|------|---------|
| **A28 InternalReviewAgent** | 内部审校师 | 结构审查（章节比例）+ 论据审查（未支撑断言）+ 一致性审查（前后匹配）+ 完整性审查 |
| **A29 LanguageAgent** | 学术语言润色师 | 学术用语规范 + Hedging Language（may/might/suggest）+ 句式多样性 + 时态一致性 + 段间过渡 |
| **A30 PlagiarismAgent** | 查重与原创性检测 | 全文查重（目标<15%，单篇<3%）+ 高相似段改写建议 + AI辅助声明准备 |
| **A31 FormatAgent** | 期刊格式适配师 | 按 Author Guidelines 调整格式 + 参考文献格式 + 图表规范 + 字数限制检查 |
| **A32 JournalMatchAgent** | 期刊选择师 | Scope 匹配 + IF/CiteScore/分区评估 + 审稿周期 + 接受率 → 推荐冲刺/稳妥/保底 3 级梯度 |
| **A33 CoverLetterAgent** | 投稿材料撰写师 | Cover Letter + Highlights + Graphical Abstract指引 + 推荐审稿人 + CRediT声明 |
| **A34 RevisionAgent** | 审稿意见响应师 | 意见分类（Major/Minor/Editorial）→ 策略制定（Accept/Partial/Rebut）→ Rebuttal Letter + 修改追踪 |

### 期刊选择评估矩阵

```
维度              权重    评估方法
───────────────────────────────────────
Scope 匹配度      30%    与期刊 Aim & Scope 比对
Impact Factor     20%    JCR/CiteScore 数据
审稿周期           15%    First Decision Time
接受率             15%    Acceptance Rate
读者群匹配度       10%    目标读者与研究领域重合度
OA/费用           10%    APC 费用评估

策略：推荐 3-5 个期刊，分冲刺🥇→稳妥🥈→保底🥉三档
```

### Rebuttal Letter 核心结构

```markdown
Dear Editor and Reviewers,
Thank you for the constructive comments...

## Response to Reviewer 1
### Comment 1.1 [Major]: "..."
Response: We appreciate this... [action taken]. See Page X, Lines XX-XX.

## Summary of Changes
| Section | Change | Reason | Location |
|---------|--------|--------|----------|
```

**🚪 Gate 6 检查项**：内审问题全解决？查重率<15%？格式完全符合？Cover Letter 针对性定制？AI辅助声明已准备？

---

## 十一、贯穿型智能体（Cross-Phase Agents）

| Agent | 角色 | 核心职责 | 活跃阶段 |
|-------|------|---------|---------|
| **C1 MentorAgent** | 导师模拟器 | 模拟导师反馈风格、关键节点质疑性提问、方向性引导、模拟开题/中期/预答辩 | 全程（每个Gate前） |
| **C2 IntegrityAgent** | 学术诚信监督者 | 引用规范监控、数据报告完整性（无选择性报告）、p-hacking/HARKing 风险监控、AI声明 | 全程 |
| **C3 ConsistencyAgent** | 一致性守护者 | 术语统一 + 符号统一 + 数据前后匹配 + 时态规范 + 格式一致 | Phase 5-6 |
| **C4 TranslationAgent** | 双语翻译支持 | 中↔英学术翻译、术语对照表、双语摘要、跨语言文献整合 | 全程（按需） |
| **C5 MemoryAgent** | 研究过程记忆 | 关键决策记录及理由、论文版本历史、灵感备注收集、跨阶段信息中继 | 全程 |

### MentorAgent 各阶段典型质疑

| 阶段 | 典型质疑 |
|------|---------|
| Phase 0 | "你的 research gap 是真的还是你没查到文献？" "做出来了对谁有用？" |
| Phase 1 | "有没有忽略重要的理论视角？" "文献之间的逻辑关系是什么？" |
| Phase 2 | "为什么用这个方法而不是替代方法？" "样本量够吗？" |
| Phase 3 | "不显著的结果怎么解释？" "换一种方法结果还成立吗？" |
| Phase 4 | "因果推断站得住吗？" "contribution 是 incremental 还是 significant？" |
| Phase 5 | "Introduction 第一段抓不住读者" "Discussion 和 XX 的研究对话了吗？" |
| Phase 6 | "这个期刊的读者群和你的研究匹配吗？" |

---

## 十二、论文类型适配矩阵

```
Agent                   期刊   会议   学位   综述   短论文
────────────────────────────────────────────────────
Phase 0 (4 agents)       ●     ●     ●     ●     ●
Phase 1 (5 agents)       ●     ○     ●●    ●●    ○
Phase 2 (4 agents)       ●     ●     ●     ○     ●
Phase 3 (4 agents)       ●     ●     ●     ◐     ●
Phase 4 (4 agents)       ●     ●     ●     ●     ●
Phase 5 (7 agents)       ●     ●     ●●    ●     ●
Phase 6 (7 agents)       ●     ●     ○     ●     ●
Cross-Phase (5 agents)   ●     ◐     ●●    ◐     ◐
────────────────────────────────────────────────────
激活 Agent 总数:          39    22    39    28    20

●● 加强  ● 标准  ◐ 可选  ○ 通常不需要
```

---

## 十三、质量门控与评分体系

### 论文质量评分卡（满分 100 分）

| 维度（各25分） | 评估项（各5分） |
|---------------|---------------|
| **一、研究设计** | 问题清晰度 / 理论基础 / 方法论严谨度 / 数据质量 / 效度信度 |
| **二、分析论证** | 方法匹配度 / 结果报告完整性 / 论证逻辑性 / 替代解释处理 / 贡献说服力 |
| **三、写作质量** | 结构合理性 / 语言学术性 / 文献综述批判性 / 讨论对话深度 / 图表质量 |
| **四、规范完整** | 引用规范性 / 格式合规 / 原创性(<15%) / 伦理声明 / 摘要标题质量 |

**评级**：90-100🟢可投顶刊 / 80-89🟡小幅修改 / 70-79🟠较大修改 / <70🔴实质性重写

---

## 十四、核心 Agent Prompt 模板

### A1 GapFinderAgent Prompt

```markdown
## 角色：资深学术研究顾问，专精识别研究空白
## 输入：研究领域({domain}) + 关键词({keywords}) + 范围({scope})
## 工作流程：
1. 扫描近5年高被引文献和综述
2. 识别5类空白：理论/实证/方法论/情境/时间
3. 评估每个空白的研究价值和可行性
## 输出：空白描述 + 证据来源 + 价值(H/M/L) + 可行性(H/M/L) + 建议RQ
## 约束：区分"真正空白"vs"没查到"；优先理论意义空白；每个空白引≥2文献
```

### A25 DiscussAgent Prompt

```markdown
## 角色：学术论文讨论章节撰写专家
## 写作结构：
1. 主要发现总结（回应RQ，不重复Results数据）
2. 逐条讨论（陈述发现→与≥2篇文献对话→理论解释→启示）
3. 理论含义（对理论的推进/修正/挑战）
4. 实践启示（具体可操作建议）
5. 局限性（坦诚但不自贬，搭配弥补说明）
6. 未来研究（从局限性推导，具体可执行）
## 语言：hedging language + 理论用现在时 + 自身发现用过去时
## 约束：不引入Results中没有的新数据；每个发现必须与文献对话
```

---

## 十五、Agent 间协作协议与数据流

### 消息协议

```json
{
  "message_id": "MSG-20260321-001",
  "type": "phase_output | query | feedback | gate_result",
  "from": { "agent_id": "A5_LitSurvey", "phase": "Phase1" },
  "to": { "agent_id": "A8_Synthesis", "phase": "Phase1" },
  "payload": {
    "summary": "系统性文献检索完成",
    "key_metrics": { "total": 1247, "dedup": 893, "screened": 156, "included": 67 },
    "artifacts": ["literature.bib", "prisma_flow.md", "screening_log.csv"],
    "quality_flag": "green"
  }
}
```

### 核心数据流

```
A0→A1→A2→A3 →[G0]→ A4→A5→A6/A7→A8 →[G1]→ A9→A10/A11/A12 →[G2]
→ A13→A14/A15→A16 →[G3]→ A17→A18→A19/A20 →[G4]
→ A24→A23→A25→A21→A22→A26→A27 →[G5]
→ A28→A29→A30→A31/A32→A33 →[G6]→ 📄投稿！
                                               │(如收到审稿意见)
                                               └→ A34 Revision → 回溯修改 → 重新投稿
```

---

## 十六、工具生态对接方案

| 工具类别 | 推荐工具 | 对接 Agent |
|---------|---------|-----------|
| **文献管理** | Zotero / Mendeley / EndNote | A4, A5, A12 |
| **数据库检索** | Scopus / Web of Science / PubMed / CNKI / Google Scholar | A4, A5 |
| **文献网络** | Connected Papers / VOSviewer / CiteSpace / Litmaps | A7 |
| **统计分析** | SPSS / R / Python / Stata / AMOS / Mplus | A14 |
| **定性分析** | NVivo / ATLAS.ti / MAXQDA | A15 |
| **可视化** | matplotlib / ggplot2 / Mermaid / draw.io | A16 |
| **排版** | Overleaf (LaTeX) / MS Word | A31 |
| **查重** | Turnitin / iThenticate / CNKI查重 | A30 |
| **AI写作辅助** | Grammarly / Writefull / Paperpal | A29 |
| **项目管理** | Notion / Trello / GitHub Projects | Orchestrator, C5 |

---

## 十七、论文写作状态机

```
[Idea] → [RQ Defined] → [Literature Done] → [Method Designed]
   │          │                │                    │
   └──回退──┘      └──回退──────┘       └──回退──────┘
                                                    │
→ [Data Collected] → [Analysis Done] → [Arguments Built]
         │                │                   │
         └──回退──────────┘      └──回退──────┘
                                              │
→ [Draft Written] → [Internally Reviewed] → [Polished]
         │                  │                   │
         └──回退────────────┘      └──回退──────┘
                                              │
→ [Formatted] → [Submitted] → [Under Review]
                     │              │
                     │    ┌─────────┴──────────┐
                     │    │                    │
                     │  [Accept✅]        [Revise🔄]──→[Revised]──→[Resubmit]
                     │                         │
                     │                    [Reject❌]──→[Reformat]──→[Submit另一期刊]
                     │
                     └──→ [Published🎉]
```

---

## 十八、附录：与原始版对比总结

```
原始版 (16 Agent, 5 Phase)              完善版 (39 Agent, 7 Phase)
─────────────────────                   ──────────────────────────
Phase 1: 选题+文献(3)                   Phase 0: 研究定位(4) ← 新增！
Phase 2: 研究执行(3)                    Phase 1: 文献工程(5) ← 大幅升级！
Phase 3: 论证构建(3)                    Phase 2: 方法论设计(4) ← 独立！
Phase 4: 论文写作(3)                    Phase 3: 研究执行(4)
Phase 5: 审校投稿(4)                    Phase 4: 论证构建(4) ← 新增红队
                                        Phase 5: 论文写作(7) ← 章节专门化！
                                        Phase 6: 审校投稿(7) ← 全面升级！
                                        贯穿型(0→5): 导师+诚信+一致+翻译+记忆
```

---

> 💡 **核心理念**：学术论文写作是一个**高度结构化**的智力活动。通过 39 个专业化 Agent 分工协作、7 道质量门控层层把关、5 个贯穿型 Agent 持续守护，我们构建了一个**真正能够辅助学术研究全流程的多智能体团队**。

---

*文档版本：v1.0 | 基于通用版学术研究架构深度完善 | 2026-03-21*
