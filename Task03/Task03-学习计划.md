# Task03 学习计划 - 记忆与检索

**学习日期**: 2025-12-19  
**截止日期**: 2025-12-22  
**当前状态**: 📋 准备中  
**预计用时**: 8-10小时

---

## 📚 学习目标

### 核心目标
1. ✅ 理解Agent的记忆系统设计
2. ✅ 掌握短期记忆与长期记忆机制
3. ✅ 学习RAG（检索增强生成）技术
4. ✅ 实现向量数据库集成
5. ✅ 掌握记忆管理策略

### 能力提升
- Agent记忆系统设计能力
- RAG技术实践能力
- 向量数据库应用能力
- 上下文管理能力

---

## 📖 学习内容概览

### 第八章：记忆与检索

#### **8.1 为什么Agent需要记忆？**
- 传统LLM的局限性
  - 上下文长度限制
  - 无状态性
  - 知识截止日期
- Agent记忆系统的价值
  - 长期对话能力
  - 个性化交互
  - 知识积累

#### **8.2 短期记忆 (Short-term Memory)**
- 对话历史管理
- 滑动窗口策略
- Token优化技术
- 上下文压缩

核心实现：
```python
class ShortTermMemory:
    def __init__(self, max_tokens=4000):
        self.messages = []
        self.max_tokens = max_tokens
    
    def add_message(self, message):
        # 添加消息并管理窗口
        pass
    
    def get_context(self):
        # 返回当前上下文
        pass
```

#### **8.3 长期记忆 (Long-term Memory)**
- 向量数据库
  - ChromaDB
  - Pinecone
  - Weaviate
  - Milvus
- 语义检索
- 相似度搜索
- 记忆存储与召回

核心技术：
- Embedding (文本向量化)
- Vector Search (向量检索)
- Semantic Similarity (语义相似度)

#### **8.4 RAG (Retrieval-Augmented Generation)**
- RAG工作原理
  1. 文档分块 (Chunking)
  2. 向量化 (Embedding)
  3. 存储 (Vector Store)
  4. 检索 (Retrieval)
  5. 增强生成 (Augmented Generation)

- RAG优化技术
  - 分块策略
  - Embedding模型选择
  - 检索策略（Top-K, MMR）
  - Reranking (重排序)

#### **8.5 记忆管理策略**
- 记忆重要性评分
- 记忆遗忘机制
- 记忆整合与总结
- 记忆索引优化

#### **8.6 实战：构建带记忆的Agent**
- MemoryAgent 实现
- RAGAgent 实现
- 记忆工具化 (MemoryTool)
- 实际应用场景

---

## 📝 学习路线图

### 阶段一：理论学习 (2小时)

#### Step 1: 记忆系统基础 (45分钟)
- [ ] 阅读 8.1 章节 - 为什么需要记忆
- [ ] 理解短期记忆 vs 长期记忆
- [ ] 学习记忆系统架构

**关键概念**：
- 上下文窗口
- 无状态 vs 有状态
- 记忆持久化

#### Step 2: RAG技术原理 (45分钟)
- [ ] 阅读 8.4 章节 - RAG原理
- [ ] 理解文档分块策略
- [ ] 学习Embedding技术
- [ ] 理解向量检索

**关键概念**：
- Chunking
- Embedding
- Vector Store
- Semantic Search

#### Step 3: 向量数据库 (30分钟)
- [ ] 了解主流向量数据库
- [ ] ChromaDB vs Pinecone 对比
- [ ] 学习向量检索API

**关键概念**：
- Vector Database
- Similarity Search
- Cosine Similarity
- Top-K Retrieval

---

### 阶段二：环境准备 (1小时)

#### Step 1: 安装依赖
```bash
# 向量数据库
pip install chromadb

# Embedding模型
pip install sentence-transformers

# HelloAgents记忆模块
pip install "hello-agents[memory]==0.1.1"

# 可选：其他向量数据库
# pip install pinecone-client
# pip install weaviate-client
```

#### Step 2: 准备Embedding模型
```python
from sentence_transformers import SentenceTransformer

# 下载中文Embedding模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# 或使用 'all-MiniLM-L6-v2' (英文)
```

#### Step 3: 测试向量数据库
- [ ] 创建ChromaDB实例
- [ ] 测试文档存储
- [ ] 测试向量检索

---

### 阶段三：代码实践 (4-5小时)

#### 实践1: 短期记忆实现 (1小时)
**目标**: 实现对话历史管理

- [ ] 创建 `short_term_memory.py`
- [ ] 实现滑动窗口机制
- [ ] 实现Token计数与优化
- [ ] 测试对话历史管理

**核心功能**:
```python
class ShortTermMemory:
    def add_message(self, role, content)
    def get_recent_messages(self, limit)
    def clear()
    def get_token_count()
```

#### 实践2: 长期记忆实现 (1.5小时)
**目标**: 实现向量数据库集成

- [ ] 创建 `long_term_memory.py`
- [ ] 集成ChromaDB
- [ ] 实现文档存储
- [ ] 实现语义检索
- [ ] 测试记忆召回

**核心功能**:
```python
class LongTermMemory:
    def store(self, content, metadata)
    def search(self, query, top_k=5)
    def delete(self, ids)
    def clear()
```

#### 实践3: RAG系统实现 (1.5小时)
**目标**: 构建完整RAG流程

- [ ] 创建 `rag_system.py`
- [ ] 实现文档分块
- [ ] 实现向量化与存储
- [ ] 实现检索与增强
- [ ] 测试RAG问答

**RAG流程**:
```python
class RAGSystem:
    def ingest_documents(self, documents)  # 文档摄取
    def chunk_document(self, document)     # 文档分块
    def embed_chunks(self, chunks)         # 向量化
    def retrieve(self, query, top_k=5)     # 检索
    def generate(self, query, context)     # 增强生成
```

#### 实践4: MemoryAgent实现 (1小时)
**目标**: 构建带记忆的Agent

- [ ] 创建 `memory_agent.py`
- [ ] 集成短期+长期记忆
- [ ] 实现记忆工具化
- [ ] 测试多轮对话
- [ ] 测试知识问答

**Agent架构**:
```python
class MemoryAgent(Agent):
    def __init__(self, llm, short_term, long_term):
        self.short_term_memory = short_term
        self.long_term_memory = long_term
    
    def run(self, user_input):
        # 1. 从长期记忆检索相关信息
        # 2. 结合短期记忆构建上下文
        # 3. LLM生成回复
        # 4. 更新记忆
        pass
```

---

### 阶段四：习题完成 (2-3小时)

#### 习题1: 记忆系统设计 (理论题, 30分钟)
- [ ] 对比短期记忆vs长期记忆
- [ ] 分析记忆系统的设计权衡
- [ ] 提出记忆优化策略

#### 习题2: RAG系统优化 (实践题, 1小时)
- [ ] 实现不同的分块策略
  - 固定长度分块
  - 句子分块
  - 段落分块
- [ ] 对比不同策略的效果
- [ ] 实现Reranking

#### 习题3: 向量数据库对比 (分析题, 30分钟)
- [ ] 对比ChromaDB vs Pinecone
- [ ] 分析各自的优缺点
- [ ] 选择合适的数据库

#### 习题4: 记忆管理策略 (设计题, 1小时)
- [ ] 设计记忆重要性评分机制
- [ ] 实现记忆遗忘策略
- [ ] 设计记忆整合算法

**挑战**: 实现基于时间衰减的记忆遗忘

#### 习题5: 多模态记忆 (挑战题, 可选)
- [ ] 设计支持图片的记忆系统
- [ ] 实现多模态Embedding
- [ ] 构建多模态RAG

---

## 🎯 重点难点

### 技术难点

#### 1. Embedding模型选择
**常用模型**:
- `all-MiniLM-L6-v2` (英文, 轻量)
- `paraphrase-multilingual-MiniLM-L12-v2` (多语言)
- `text-embedding-ada-002` (OpenAI, 收费)
- `bge-large-zh` (中文, 效果好)

**选择标准**:
- 语言支持
- 模型大小
- 推理速度
- 效果质量

#### 2. 文档分块策略
**常见策略**:
```python
# 1. 固定长度分块
def chunk_by_tokens(text, chunk_size=500):
    # 按token数量分块
    pass

# 2. 句子分块
def chunk_by_sentences(text, sentences_per_chunk=5):
    # 按句子分块
    pass

# 3. 语义分块
def chunk_by_semantics(text):
    # 按语义边界分块
    pass
```

**权衡**:
- 块太小 → 上下文不足
- 块太大 → 检索不精确
- 推荐: 500-1000 tokens

#### 3. 检索策略
**Top-K vs MMR**:
```python
# Top-K: 简单相似度排序
results = vector_store.similarity_search(query, k=5)

# MMR (Maximal Marginal Relevance): 平衡相关性与多样性
results = vector_store.max_marginal_relevance_search(query, k=5)
```

#### 4. 记忆管理
**挑战**:
- 何时存储到长期记忆？
- 如何评估记忆重要性？
- 如何避免记忆冗余？
- 如何实现记忆遗忘？

---

## ✅ 检查清单

### 理论理解
- [ ] 理解短期记忆vs长期记忆
- [ ] 掌握RAG工作原理
- [ ] 理解Embedding技术
- [ ] 了解向量数据库
- [ ] 掌握记忆管理策略

### 代码实践
- [ ] 短期记忆实现并测试
- [ ] 长期记忆实现并测试
- [ ] RAG系统完整实现
- [ ] MemoryAgent实现
- [ ] 多轮对话测试通过
- [ ] 知识问答测试通过

### 习题完成
- [ ] 习题1: 记忆系统设计
- [ ] 习题2: RAG系统优化 ⭐实践
- [ ] 习题3: 向量数据库对比
- [ ] 习题4: 记忆管理策略 ⭐设计
- [ ] 习题5: 多模态记忆 ⭐挑战（可选）

### 文档输出
- [ ] 完整学习笔记
- [ ] 代码注释完善
- [ ] 习题解答文档
- [ ] RAG优化对比分析
- [ ] Task03总结

---

## 📊 时间分配建议

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| 阶段一 | 理论学习 | 2小时 |
| 阶段二 | 环境准备 | 1小时 |
| 阶段三 | 代码实践 | 4-5小时 |
| 阶段四 | 习题完成 | 2-3小时 |
| **总计** | | **9-11小时** |

**建议安排**：
- **Day 1 (2025-12-19)**: 阶段一、二 (3小时)
- **Day 2 (2025-12-20)**: 阶段三 (4-5小时)
- **Day 3 (2025-12-21)**: 阶段四 + 总结 (3小时)

---

## 🎓 学习策略

### 1. 循序渐进
```
理论 → 环境 → 简单实践 → 复杂实践 → 习题
```

### 2. 对比学习
```
短期记忆 ↔ 长期记忆
不同分块策略对比
不同向量数据库对比
```

### 3. 实践驱动
- 每个概念都要动手实现
- 多做实验对比效果
- 理解每个参数的影响

### 4. 工程思维
- 考虑性能优化
- 考虑成本控制
- 考虑可扩展性

---

## 📚 参考资源

### 课程资料
- **第八章文档**: `hello-agents/docs/chapter8/`
- **示例代码**: `hello-agents/code/chapter8/`

### 扩展阅读
- **RAG论文**: Retrieval-Augmented Generation (Lewis et al., 2020)
- **向量数据库**: ChromaDB官方文档
- **Embedding**: SentenceTransformers文档

### 工具文档
- ChromaDB: https://docs.trychroma.com/
- SentenceTransformers: https://www.sbert.net/
- Pinecone: https://docs.pinecone.io/

---

## 🎯 预期成果

### 代码产出
```
Task03/
├── short_term_memory.py      # 短期记忆实现
├── long_term_memory.py       # 长期记忆实现  
├── rag_system.py             # RAG系统
├── memory_agent.py           # 带记忆的Agent
├── chunking_strategies.py    # 分块策略对比
└── tests/                    # 测试文件
```

### 文档产出
```
├── Task03-学习笔记.md        # 完整笔记
├── Task03-习题解答.md        # 习题答案
├── RAG优化对比分析.md        # 分块策略对比
└── Task03-总结.md            # 学习总结
```

### 能力提升
- ✅ 记忆系统设计能力
- ✅ RAG技术实践能力
- ✅ 向量数据库应用能力
- ✅ 上下文管理能力

---

## 💡 学习建议

### 对于有RAG经验的学习者
- 重点关注记忆管理策略
- 尝试实现高级优化技术
- 对比不同向量数据库性能

### 对于初学者
- 先理解基本概念
- 从简单示例开始
- 逐步增加复杂度
- 多做实验对比

### 对于想深入的学习者
- 阅读RAG相关论文
- 实现多模态记忆系统
- 优化检索性能
- 设计创新的记忆管理策略

---

## 🚀 下一步

完成Task03后，你将具备：
1. ✅ Agent记忆系统设计能力
2. ✅ RAG技术完整实现经验
3. ✅ 向量数据库集成能力
4. ✅ 记忆管理优化能力

**Task04预告** (2025-12-24截止):
- 第九章：上下文工程
- Prompt Engineering
- Few-shot Learning
- Chain of Thought

---

**创建时间**: 2025-12-19  
**最后更新**: 2025-12-19  
**版本**: 1.0.0

---

**开始Task03的学习之旅吧！记忆让Agent更智能！** 🧠✨
