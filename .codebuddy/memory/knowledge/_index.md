# 📚 经验域索引（Knowledge Domain Index）

> 本文件是经验域的入口，索引所有跨项目通用经验。
> 经验域只存放**去项目化**的通用知识，不包含任何项目特定细节。

---

## 🏷️ 领域分类

### 1. 架构设计模式 (Architecture Patterns)
- [multi-agent-design.md](patterns/multi-agent-design.md) — 多智能体团队设计模式
- [workflow-orchestration.md](patterns/workflow-orchestration.md) — 工作流编排模式

### 2. 文档生成模式 (Document Generation)
- [document-generation.md](patterns/document-generation.md) — 大型文档生成最佳实践

### 3. 经验教训 (Lessons Learned)
- [common-pitfalls.md](lessons/common-pitfalls.md) — 常见陷阱与避坑指南

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| 总经验条目 | 4 文件 |
| 最后更新 | 2026-03-21 |
| 蒸馏来源项目数 | 4 |

---

## 📝 蒸馏规则

1. **频率阈值**：同类经验出现 ≥3 次 → 自动提炼候选
2. **确认机制**：提炼前向用户确认
3. **去项目化**：移除项目名称、具体数据，保留可复用模式
4. **标签标注**：每条经验必须有 `#tags` 便于检索
5. **版本追踪**：每次修改记录原因和日期
