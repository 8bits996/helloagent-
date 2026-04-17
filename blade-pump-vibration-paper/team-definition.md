# 叶片泵论文重写多Agent团队定义

> 基于 academic-paper-writing-team.md（39 Agent）框架，针对现有论文进行系统重写。
> 论文：叶片泵-电机组机脚振动特性分析及减振结构优化设计
> 类型：工程应用研究（期刊论文）
> 目标期刊：机床与液压 / 液压与气动

---

## 团队配置

### 管控层
- **PM Agent**：振动工程领域资深审稿人，模拟期刊副主编角色
- **Orchestrator**：研究协调员，管理39个Agent的调度与Gate检查

### Phase 0: 论文诊断与重新定位（重写模式特有）
| Agent | 角色 | 任务 | 输出 |
|-------|------|------|------|
| A0 ScopeAgent | 研究范围审查师 | 审查现有论文的研究范围是否清晰、边界是否合理 | 研究范围评估报告 |
| A1 GapFinderAgent | 研究空白重新发现者 | 对照现有文献重新评估论文声称的研究空白是否成立 | 更新后的研究空白地图 |
| A2 HypothesisAgent | 研究假设审查师 | 检查研究假设是否明确、可检验、与结论匹配 | 假设审查报告 |
| A3 FeasibilityAgent | 学术可行性再评估师 | 评估论文结论的可靠性和工程应用价值 | 可行性评估更新 |

### Phase 1: 文献工程增强
| Agent | 角色 | 任务 | 输出 |
|-------|------|------|------|
| A4 SearchStrategyAgent | 检索策略审查师 | 审查现有18篇参考文献的覆盖面，补充检索策略 | 补充检索策略 |
| A5 LitSurveyAgent | 文献补充检索员 | 补充近5年相关文献，特别关注流固耦合、黏弹性模型方向 | 补充文献清单 |
| A6 QualityAssessAgent | 文献质量评估师 | 评估现有引用文献的质量和权威性 | 文献质量评估 |
| A7 LitMapAgent | 文献关系映射师 | 构建文献引用网络，识别缺失的核心文献 | 文献关系图 |
| A8 SynthesisAgent | 文献综合更新师 | 基于补充文献更新文献综述综合 | 更新后的文献综合 |

### Phase 2: 方法论增强
| Agent | 角色 | 任务 | 输出 |
|-------|------|------|------|
| A9 MethodAgent | 方法论审查师 | 审查FEA建模方法、网格收敛性、RSM方法的合理性 | 方法论审查报告 |
| A10 DataDesignAgent | 数据方案审查师 | 检查试验设计（Box-Behnken）、参数范围、样本量合理性 | 数据方案评估 |
| A11 EthicsAgent | 伦理/规范审查师 | 检查是否需要声明AI辅助、数据真实性、标准引用规范 | 合规审查报告 |
| A12 ValidityAgent | 效度信度审查师 | 评估仿真结果效度、试验验证可信度 | 效度评估报告 |

### Phase 3: 结果验证与增强
| Agent | 角色 | 任务 | 输出 |
|-------|------|------|------|
| A13 DataCollectAgent | 数据完整性审查员 | 检查数据报告完整性、统计量是否规范 | 数据完整性报告 |
| A14 QuantAnalysisAgent | 定量分析审查师 | 审查统计方法、效应量报告、置信区间 | 定量分析审查 |
| A15 QualAnalysisAgent | 定性分析审查师 | 审查振型描述、机理分析的说服力 | 定性分析审查 |
| A16 VisualAgent | 可视化审查师 | 评估图表质量、建议补充可视化内容 | 可视化建议 |

### Phase 4: 论证构建增强
| Agent | 角色 | 任务 | 输出 |
|-------|------|------|------|
| A17 ArgumentAgent | 核心论证审查师 | 按Toulmin模型检查论证链完整性 | 论证结构审查 |
| A18 ContributionAgent | 贡献定位审查师 | 重新评估论文贡献的层次和表述 | 贡献定位更新 |
| A19 LimitationAgent | 局限性审查师 | 检查局限性分析是否坦诚、全面 | 局限性评估 |
| A20 CounterArgAgent | 反论证师（红队） | 尝试攻击论文结论、寻找替代解释 | 反论证报告 |

### Phase 5: 论文重写（按推荐顺序）
| Agent | 章节 | 重写重点 |
|-------|------|---------|
| A24 ResultAgent | Results（第3-6节） | 增强统计规范、补充效应量、完善数据展示 |
| A23 MethodWriteAgent | Methodology（第2节） | 提高可复现性、补充建模细节 |
| A25 DiscussAgent | Discussion（第7节） | 深化文献对话、完善理论解释 |
| A21 IntroAgent | Introduction（第0节） | 按CARS模型重构、突出创新点 |
| A22 LitReviewWriteAgent | Literature Review | 整合到引言中、增强批判性 |
| A26 AbstractAgent | Abstract | 全文浓缩、结构化摘要 |
| A27 TitleKeywordAgent | Title+Keywords | 优化标题含关键词、选择最佳关键词 |

### Phase 6: 审校与投稿
| Agent | 角色 | 任务 |
|-------|------|------|
| A28 InternalReviewAgent | 内审师 | 全面结构+论据审查 |
| A29 LanguageAgent | 语言润色师 | 学术用语规范、hedging、过渡 |
| A30 PlagiarismAgent | 查重审查师 | 引用规范、AI辅助声明 |
| A31 FormatAgent | 格式适配师 | 目标期刊格式适配 |
| A32 JournalMatchAgent | 期刊选择师 | 评估机床与液压/液压与气动匹配度 |
| A33 CoverLetterAgent | 投稿材料师 | Cover Letter + Highlights |
| A34 RevisionAgent | 修订响应师 | 预判审稿意见并准备答复 |

### 贯穿型Agent
| Agent | 角色 | 全程职责 |
|-------|------|---------|
| C1 MentorAgent | 导师模拟器 | 每个Gate前进行质疑性审查 |
| C2 IntegrityAgent | 学术诚信监督 | 监控引用规范、数据报告完整性 |
| C3 ConsistencyAgent | 一致性守护 | 术语/符号/数据前后统一 |
| C4 TranslationAgent | 双语翻译 | 中英文摘要/术语对照 |
| C5 MemoryAgent | 过程记忆 | 记录关键决策和版本历史 |

---

## Gate 检查清单（重写模式）

### G0: 论文诊断完成
- [ ] 研究空白是否仍然成立
- [ ] 假设与结论是否一致
- [ ] 现有论文的主要弱点已识别

### G1: 文献增强完成
- [ ] 参考文献是否覆盖近5年核心文献
- [ ] 文献综述是否有批判性
- [ ] 缺失的重要文献已补充

### G2: 方法论审查完成
- [ ] FEA方法描述充分可复现
- [ ] 试验设计合理
- [ ] 数据报告规范完整

### G3: 结果验证完成
- [ ] 统计方法正确
- [ ] 效应量/置信区间已报告
- [ ] 误差分析充分

### G4: 论证增强完成
- [ ] Toulmin论证链完整
- [ ] 反论证已处理
- [ ] 贡献定位准确

### G5: 重写初稿完成
- [ ] 各章节遵循写作规范
- [ ] 整体逻辑连贯
- [ ] 中英文摘要对应

### G6: 终稿就绪
- [ ] 查重率<15%
- [ ] 格式符合目标期刊
- [ ] Cover Letter + Highlights 就绪

---

## 执行策略

### Wave 1（并行）: Phase 0-1 诊断与文献
- A0 ScopeAgent ∥ A1 GapFinder ∥ A4 SearchStrategy
- 完成后 → A5 LitSurvey → A6 ∥ A7 → A8 Synthesis

### Wave 2（并行）: Phase 2-3 方法与结果审查
- A9 MethodAgent ∥ A12 ValidityAgent
- A10 DataDesign ∥ A13 DataCollect
- A14 QuantAnalysis ∥ A15 QualAnalysis ∥ A16 VisualAgent

### Wave 3（并行）: Phase 4 论证增强
- A17 ArgumentAgent → A18 Contribution ∥ A19 Limitation ∥ A20 CounterArg

### Wave 4（顺序）: Phase 5 论文重写
- A24 Results → A23 Method → A25 Discussion → A21 Intro → A22 LitReview → A26 Abstract → A27 Title

### Wave 5（并行）: Phase 6 审校
- A28 InternalReview → A29 Language → A30 ∥ A31 ∥ A32 → A33

---

*版本: v1.0 | 2026-03-21 | 基于academic-paper-writing-team.md 39 Agent框架*
