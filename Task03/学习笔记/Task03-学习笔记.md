# Task03 学习笔记 - 第八章：记忆与检索

**学习日期**: 2025-12-22  
**章节**: 第八章 - Agent的记忆系统

---

## 📖 8.1 为什么Agent需要记忆？

### 传统LLM的局限性

#### 1. **上下文长度限制**
- GPT-3.5: ~4K tokens
- GPT-4: 8K-32K tokens  
- Claude: 100K tokens
- **问题**: 长对话会超出上下文窗口，丢失历史信息

#### 2. **无状态性**
```python
# 传统LLM每次调用都是独立的
response1 = llm("我叫张三")  # LLM回复：你好张三
response2 = llm("我叫什么名字？")  # LLM回复：我不知道你的名字
# ❌ LLM无法记住上一轮对话
```

#### 3. **知识截止日期**
- 训练数据有时间限制
- 无法获取最新信息
- 无法学习用户特定知识

### Agent记忆系统的价值

#### ✅ **长期对话能力**
- 维护多轮对话上下文
- 记住用户偏好和历史
- 实现连续性交互

#### ✅ **个性化交互**
- 记住用户信息（姓名、偏好等）
- 适应用户习惯
- 提供定制化服务

#### ✅ **知识积累**
- 存储领域知识
- 学习新信息
- 构建知识库

---

## 📝 8.2 短期记忆 (Short-term Memory)

### 概念定义
**短期记忆**: 用于维护当前对话会话的临时上下文信息

### 核心功能
1. **对话历史管理**: 存储最近的对话消息
2. **滑动窗口策略**: 保持固定数量的最近消息
3. **Token优化**: 管理上下文长度，避免超限
4. **上下文压缩**: 总结或删除不重要的信息

### 实现策略

#### 策略1: 固定窗口大小
```python
class ShortTermMemory:
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        # 保持窗口大小
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # 删除最早的消息
```

**优点**: 简单易实现  
**缺点**: 可能删除重要信息

#### 策略2: Token数量限制
```python
class TokenLimitedMemory:
    def __init__(self, max_tokens=4000):
        self.messages = []
        self.max_tokens = max_tokens
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        # 删除消息直到token数量满足要求
        while self.count_tokens() > self.max_tokens:
            self.messages.pop(0)
    
    def count_tokens(self):
        # 计算所有消息的token总数
        return sum(len(msg["content"]) // 4 for msg in self.messages)
```

**优点**: 更精确地控制上下文长度  
**缺点**: 需要token计数工具

#### 策略3: 重要性加权
```python
class ImportanceBasedMemory:
    def add_message(self, role, content, importance=1.0):
        self.messages.append({
            "role": role,
            "content": content,
            "importance": importance
        })
    
    def trim_memory(self):
        # 删除重要性低的消息
        self.messages.sort(key=lambda x: x["importance"], reverse=True)
        self.messages = self.messages[:self.max_messages]
```

**优点**: 保留重要信息  
**缺点**: 需要评估消息重要性

### 使用场景
- ✅ 多轮对话
- ✅ 聊天机器人
- ✅ 客服系统
- ✅ 实时交互

---

## 🗄️ 8.3 长期记忆 (Long-term Memory)

### 概念定义
**长期记忆**: 持久化存储，用于保存长期知识和历史信息

### 核心技术

#### 1. **向量数据库 (Vector Database)**

主流向量数据库对比：

| 数据库 | 类型 | 特点 | 适用场景 |
|--------|------|------|----------|
| **ChromaDB** | 嵌入式 | 轻量、易用、免费 | 开发测试、小规模应用 |
| **Pinecone** | 云服务 | 高性能、托管 | 生产环境、大规模应用 |
| **Weaviate** | 自托管 | 功能丰富、开源 | 企业级应用 |
| **Milvus** | 分布式 | 高并发、可扩展 | 海量数据 |

#### 2. **Embedding (文本向量化)**

```python
from sentence_transformers import SentenceTransformer

# 加载Embedding模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 文本转向量
text = "Agent需要记忆系统来维护长期对话能力"
embedding = model.encode(text)  # 返回 384维向量

print(f"向量维度: {len(embedding)}")  # 384
```

**常用Embedding模型**:
- `all-MiniLM-L6-v2`: 英文，轻量级（384维）
- `paraphrase-multilingual-MiniLM-L12-v2`: 多语言（384维）
- `text-embedding-ada-002`: OpenAI，效果好但收费（1536维）
- `bge-large-zh`: 中文，效果优秀（1024维）

#### 3. **语义检索 (Semantic Search)**

```python
import chromadb

# 创建向量数据库
client = chromadb.Client()
collection = client.create_collection("agent_memory")

# 存储文档
collection.add(
    documents=["Agent需要记忆", "RAG是检索增强生成"],
    ids=["doc1", "doc2"]
)

# 语义检索
results = collection.query(
    query_texts=["什么是记忆系统？"],
    n_results=2
)
```

**工作原理**:
1. 将查询文本转为向量
2. 计算查询向量与数据库中所有向量的相似度
3. 返回最相似的Top-K结果

#### 4. **相似度计算**

常用相似度度量：

**余弦相似度 (Cosine Similarity)**:
```python
import numpy as np

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 值范围: [-1, 1]，越接近1越相似
```

**欧氏距离 (Euclidean Distance)**:
```python
def euclidean_distance(vec1, vec2):
    return np.linalg.norm(vec1 - vec2)

# 值范围: [0, ∞]，越小越相似
```

### 使用场景
- ✅ 知识库问答
- ✅ 文档检索
- ✅ 个性化推荐
- ✅ 历史记录查询

---

## 🔍 8.4 RAG (Retrieval-Augmented Generation)

### 概念定义
**RAG**: 检索增强生成，通过检索相关文档来增强LLM的生成能力

### RAG工作流程

```
用户问题 
  ↓
1. 文档分块 (Chunking)
  ↓
2. 向量化 (Embedding)
  ↓
3. 存储 (Vector Store)
  ↓
4. 检索 (Retrieval) ← 用户查询向量化
  ↓
5. 增强生成 (Augmented Generation)
  ↓
最终答案
```

### 详细步骤

#### Step 1: 文档分块 (Chunking)

**为什么需要分块？**
- 文档太长，无法整体处理
- 需要精确定位相关信息
- 优化检索准确性

**分块策略**:

```python
# 策略1: 固定长度分块
def chunk_by_tokens(text, chunk_size=500, overlap=50):
    tokens = text.split()
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = ' '.join(tokens[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# 策略2: 句子分块
def chunk_by_sentences(text, sentences_per_chunk=5):
    sentences = text.split('。')
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = '。'.join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    return chunks

# 策略3: 段落分块
def chunk_by_paragraphs(text):
    return text.split('\n\n')
```

**分块参数建议**:
- **块大小**: 500-1000 tokens
- **重叠**: 50-100 tokens（避免截断重要信息）
- **权衡**: 块太小→上下文不足；块太大→检索不精确

#### Step 2: 向量化 (Embedding)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

chunks = ["Agent的记忆系统...", "RAG技术原理..."]
embeddings = model.encode(chunks)
```

#### Step 3: 存储到向量数据库

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("knowledge_base")

collection.add(
    documents=chunks,
    embeddings=embeddings.tolist(),
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)
```

#### Step 4: 检索相关文档

```python
# 用户提问
query = "什么是Agent的记忆系统？"

# 检索Top-K相关文档
results = collection.query(
    query_texts=[query],
    n_results=5  # Top-5
)

relevant_docs = results['documents'][0]
```

#### Step 5: 增强生成

```python
# 构建增强的Prompt
context = "\n\n".join(relevant_docs)
prompt = f"""
基于以下上下文回答问题：

上下文:
{context}

问题: {query}

回答:
"""

# 调用LLM生成答案
response = llm(prompt)
```

### RAG优化技术

#### 1. **检索策略优化**

**Top-K检索**:
```python
# 简单的相似度排序
results = collection.query(query_texts=[query], n_results=5)
```

**MMR (Maximal Marginal Relevance)**:
```python
# 平衡相关性和多样性
# 避免检索到重复内容
results = collection.query(
    query_texts=[query],
    n_results=5,
    # 某些向量数据库支持MMR
)
```

#### 2. **Reranking (重排序)**

```python
from sentence_transformers import CrossEncoder

# 使用交叉编码器重排序
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 对初步检索结果重排序
scores = reranker.predict([(query, doc) for doc in relevant_docs])
reranked_docs = [doc for _, doc in sorted(zip(scores, relevant_docs), reverse=True)]
```

#### 3. **混合检索 (Hybrid Search)**

```python
# 结合关键词检索（BM25）和语义检索
# 1. BM25检索
keyword_results = bm25_search(query, top_k=10)

# 2. 向量检索
semantic_results = vector_search(query, top_k=10)

# 3. 融合结果
final_results = reciprocal_rank_fusion(keyword_results, semantic_results)
```

### RAG vs Fine-tuning

| 对比维度 | RAG | Fine-tuning |
|----------|-----|-------------|
| **成本** | 低（无需训练） | 高（需要GPU训练） |
| **更新** | 实时（添加文档即可） | 困难（需要重新训练） |
| **可解释性** | 高（可查看检索文档） | 低（黑盒模型） |
| **准确性** | 依赖检索质量 | 较高 |
| **适用场景** | 知识库问答、文档检索 | 特定任务优化 |

---

## 🧠 8.5 记忆管理策略

### 1. 记忆重要性评分

```python
def calculate_importance(memory):
    """
    评估记忆重要性
    """
    score = 0.0
    
    # 因素1: 时间新鲜度（越新越重要）
    time_score = 1.0 / (1 + time_since_creation(memory))
    
    # 因素2: 访问频率（越常访问越重要）
    access_score = memory.access_count * 0.1
    
    # 因素3: 语义重要性（关键信息）
    semantic_score = llm_evaluate_importance(memory.content)
    
    score = 0.3 * time_score + 0.3 * access_score + 0.4 * semantic_score
    return score
```

### 2. 记忆遗忘机制

#### 策略1: 基于时间衰减
```python
import math
from datetime import datetime, timedelta

def should_forget(memory, decay_rate=0.1):
    """
    基于时间衰减决定是否遗忘
    """
    days_old = (datetime.now() - memory.created_at).days
    retention = math.exp(-decay_rate * days_old)
    
    # 保留概率低于阈值时删除
    return retention < 0.1
```

#### 策略2: 基于访问频率
```python
def prune_memories(memories, keep_ratio=0.7):
    """
    保留最常访问的记忆
    """
    memories.sort(key=lambda m: m.access_count, reverse=True)
    keep_count = int(len(memories) * keep_ratio)
    return memories[:keep_count]
```

### 3. 记忆整合与总结

```python
def consolidate_memories(memories):
    """
    将相似的记忆整合成摘要
    """
    # 1. 聚类相似记忆
    clusters = cluster_similar_memories(memories)
    
    # 2. 为每个聚类生成摘要
    consolidated = []
    for cluster in clusters:
        summary = llm_summarize(cluster)
        consolidated.append(summary)
    
    return consolidated
```

### 4. 记忆索引优化

```python
class MemoryIndex:
    def __init__(self):
        self.time_index = {}      # 时间索引
        self.topic_index = {}     # 主题索引
        self.importance_index = {}  # 重要性索引
    
    def add_memory(self, memory):
        # 多维度索引
        self.time_index[memory.timestamp] = memory
        self.topic_index[memory.topic].append(memory)
        self.importance_index[memory.importance].append(memory)
    
    def search(self, criteria):
        # 快速多维度检索
        pass
```

---

## 💻 8.6 实战：构建带记忆的Agent

### MemoryAgent架构

```python
class MemoryAgent:
    def __init__(self, llm, short_term_memory, long_term_memory):
        self.llm = llm
        self.short_term = short_term_memory  # 对话历史
        self.long_term = long_term_memory    # 知识库
    
    def run(self, user_input):
        # 1. 从长期记忆检索相关信息
        relevant_context = self.long_term.search(user_input, top_k=3)
        
        # 2. 获取短期记忆（对话历史）
        conversation_history = self.short_term.get_recent_messages(limit=5)
        
        # 3. 构建增强的Prompt
        prompt = self.build_prompt(user_input, relevant_context, conversation_history)
        
        # 4. LLM生成回复
        response = self.llm(prompt)
        
        # 5. 更新记忆
        self.short_term.add_message("user", user_input)
        self.short_term.add_message("assistant", response)
        
        # 6. 存储重要信息到长期记忆
        if self.is_important(user_input):
            self.long_term.store(user_input)
        
        return response
    
    def build_prompt(self, query, context, history):
        return f"""
        对话历史:
        {history}
        
        相关知识:
        {context}
        
        用户: {query}
        助手:
        """
```

---

## 🎯 核心要点总结

### 短期记忆
- ✅ 维护对话上下文
- ✅ 滑动窗口管理
- ✅ Token优化
- ✅ 临时存储

### 长期记忆
- ✅ 向量数据库存储
- ✅ 语义检索
- ✅ 持久化知识
- ✅ 知识积累

### RAG技术
- ✅ 文档分块 → 向量化 → 存储 → 检索 → 增强生成
- ✅ 优化：Reranking、混合检索、MMR
- ✅ 适用于知识库问答

### 记忆管理
- ✅ 重要性评分
- ✅ 遗忘机制
- ✅ 记忆整合
- ✅ 索引优化

---

## 📚 下一步学习

1. ✅ 完成代码实践：实现各个模块
2. ✅ 完成习题：巩固理解
3. ✅ 阅读扩展资料：RAG论文、向量数据库文档
4. ✅ 实验对比：不同分块策略、不同Embedding模型

---

**学习笔记创建时间**: 2025-12-22  
**下次更新**: 完成代码实践后补充实战经验
