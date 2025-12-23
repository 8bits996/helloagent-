# Task04 深入学习 - 9.6章节 高级上下文工程

**学习日期**: 2024-12-22  
**学习者**: Franke Chen

---

## 📚 第9.6章 高级上下文工程技术

### 概述

基础的上下文管理已经掌握,现在深入学习更高级的技术:

1. **向量相似度检索** - 精确的语义匹配
2. **递归总结技术** - 处理超长文档
3. **动态Few-shot学习** - 智能示例选择
4. **上下文缓存优化** - 降低API成本
5. **混合检索策略** - BM25 + 向量
6. **上下文重排序** - 优化信息顺序

---

## 🎯 1. 向量相似度检索

### 1.1 为什么需要向量检索?

**问题**:
- 关键词匹配太粗糙
- 无法理解语义
- 同义词无法匹配

**示例**:
```python
query = "如何学习编程?"

# 关键词匹配
keyword_match("学习Python的最佳方法")  # ❌ 没有"编程"关键词
keyword_match("编程入门指南")          # ✅ 有"编程"

# 向量匹配
vector_match("学习Python的最佳方法")   # ✅ 语义相似
vector_match("编程入门指南")           # ✅ 语义相似
vector_match("今天天气很好")           # ❌ 语义不相关
```

### 1.2 工作原理

```
文本 → Embedding模型 → 向量 → 相似度计算
```

**流程**:
1. **文本向量化**: 使用Embedding模型将文本转为向量
2. **相似度计算**: 计算查询向量与候选向量的相似度
3. **排序选择**: 选择最相似的top-k条

**常用模型**:
- `sentence-transformers/all-MiniLM-L6-v2` (轻量级,快速)
- `sentence-transformers/all-mpnet-base-v2` (高质量)
- `OpenAI text-embedding-ada-002` (商业,效果好)
- `BAAI/bge-large-zh-v1.5` (中文优化)

### 1.3 相似度度量

#### 余弦相似度 (最常用)

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """
    计算余弦相似度
    
    值范围: -1 到 1
    1: 完全相同
    0: 正交(无关)
    -1: 完全相反
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
```

#### 欧氏距离

```python
def euclidean_distance(vec1, vec2):
    """
    计算欧氏距离
    
    值范围: 0 到 ∞
    0: 完全相同
    值越大: 越不相似
    """
    return np.linalg.norm(vec1 - vec2)
```

#### 点积相似度

```python
def dot_product_similarity(vec1, vec2):
    """
    计算点积相似度
    
    归一化向量的点积 = 余弦相似度
    """
    return np.dot(vec1, vec2)
```

### 1.4 实践应用

**场景1: 对话历史检索**
```python
# 从100条历史对话中找到与当前查询最相关的5条
query = "如何优化Python代码性能?"

# 向量化所有历史
history_vectors = [embed(msg) for msg in history]
query_vector = embed(query)

# 计算相似度
similarities = [
    cosine_similarity(query_vector, h_vec) 
    for h_vec in history_vectors
]

# 选择top-5
top_5_indices = np.argsort(similarities)[-5:]
relevant_history = [history[i] for i in top_5_indices]
```

**场景2: 智能示例选择**
```python
# 从示例库中选择与当前任务最相关的示例
task = "写一个快速排序算法"

# 示例库
examples = [
    "冒泡排序实现",
    "快速排序详解",
    "归并排序算法",
    "数据结构基础"
]

# 选择最相关的2个示例
relevant_examples = select_by_similarity(task, examples, top_k=2)
# 返回: ["快速排序详解", "归并排序算法"]
```

---

## 🎯 2. 递归总结技术

### 2.1 问题背景

**挑战**: 如何总结超长文档?

```
100页文档 → 直接总结 → ❌ 超出Token限制

解决方案: 递归总结
100页 → 分10组 → 每组总结 → 得到10个摘要 → 再总结 → 最终摘要
```

### 2.2 递归总结算法

```python
def recursive_summarize(text, llm, max_chunk_size=2000):
    """
    递归总结长文本
    
    Args:
        text: 要总结的文本
        llm: LLM客户端
        max_chunk_size: 每块最大字符数
    
    Returns:
        最终总结
    """
    # 基础情况: 文本足够短,直接总结
    if len(text) <= max_chunk_size:
        return llm.summarize(text)
    
    # 递归情况: 分块总结,再总结摘要
    chunks = split_into_chunks(text, max_chunk_size)
    
    # 总结每一块
    summaries = [llm.summarize(chunk) for chunk in chunks]
    
    # 合并所有摘要
    combined = "\n".join(summaries)
    
    # 递归总结摘要
    return recursive_summarize(combined, llm, max_chunk_size)
```

### 2.3 MapReduce总结

```python
def map_reduce_summarize(documents, llm):
    """
    MapReduce风格的总结
    
    Map阶段: 并行总结每个文档
    Reduce阶段: 合并所有摘要
    """
    # Map: 并行总结
    summaries = parallel_map(llm.summarize, documents)
    
    # Reduce: 合并摘要
    while len(summaries) > 1:
        # 两两合并
        pairs = chunk_list(summaries, 2)
        summaries = [
            llm.summarize(f"{s1}\n{s2}") 
            for s1, s2 in pairs
        ]
    
    return summaries[0]
```

### 2.4 分层总结

```
原文档 (100页)
  ↓
第1层总结 (每10页→1页, 得到10页)
  ↓
第2层总结 (每10页→1页, 得到1页)
  ↓
最终摘要 (1页)
```

**优点**:
- 保留层次结构
- 可以查看中间结果
- 更好的信息保留

---

## 🎯 3. 动态Few-shot示例选择

### 3.1 什么是Few-shot学习?

**定义**: 通过提供少量示例来引导LLM完成任务

**传统方式** (静态示例):
```python
prompt = """
请将以下句子翻译成英文:

示例1:
中文: 你好
英文: Hello

示例2:
中文: 谢谢
英文: Thank you

现在翻译:
中文: 早上好
英文:
"""
```

**问题**:
- 示例是固定的
- 可能与当前任务不相关
- 浪费Token

### 3.2 动态示例选择

**原理**: 根据当前任务,从示例库中选择最相关的示例

```python
class DynamicFewShotSelector:
    """动态Few-shot示例选择器"""
    
    def __init__(self, example_pool, embedding_model):
        """
        Args:
            example_pool: 示例池
            embedding_model: Embedding模型
        """
        self.examples = example_pool
        
        # 预先计算所有示例的向量
        self.example_vectors = [
            embedding_model.encode(ex['input'])
            for ex in example_pool
        ]
        
        self.embedding_model = embedding_model
    
    def select_examples(self, query, k=3):
        """
        选择最相关的k个示例
        
        Args:
            query: 当前查询
            k: 选择数量
        
        Returns:
            最相关的k个示例
        """
        # 计算查询向量
        query_vector = self.embedding_model.encode(query)
        
        # 计算与所有示例的相似度
        similarities = [
            cosine_similarity(query_vector, ex_vec)
            for ex_vec in self.example_vectors
        ]
        
        # 选择top-k
        top_k_indices = np.argsort(similarities)[-k:]
        
        return [self.examples[i] for i in top_k_indices]
```

### 3.3 使用示例

```python
# 准备示例池
example_pool = [
    {
        "input": "如何排序列表?",
        "output": "使用list.sort()或sorted()函数"
    },
    {
        "input": "如何读取文件?",
        "output": "使用open()函数配合with语句"
    },
    {
        "input": "如何处理异常?",
        "output": "使用try-except块"
    },
    # ... 更多示例
]

# 创建选择器
selector = DynamicFewShotSelector(example_pool, embedding_model)

# 当前任务
query = "如何写入文件?"

# 选择最相关的2个示例
relevant_examples = selector.select_examples(query, k=2)
# 可能返回: ["如何读取文件?", "如何处理异常?"]

# 构建Prompt
prompt = build_prompt_with_examples(query, relevant_examples)
```

### 3.4 多样性选择

**问题**: 只按相似度选择可能导致示例过于相似

**解决**: MMR (Maximal Marginal Relevance)

```python
def select_diverse_examples(query, examples, k=3, lambda_param=0.5):
    """
    选择既相关又多样的示例
    
    Args:
        query: 查询
        examples: 候选示例
        k: 选择数量
        lambda_param: 相关性vs多样性权重 (0-1)
    
    Returns:
        选择的示例
    """
    query_vec = embed(query)
    example_vecs = [embed(ex) for ex in examples]
    
    selected = []
    selected_vecs = []
    
    for _ in range(k):
        best_score = -float('inf')
        best_idx = None
        
        for i, (ex, ex_vec) in enumerate(zip(examples, example_vecs)):
            if ex in selected:
                continue
            
            # 相关性分数
            relevance = cosine_similarity(query_vec, ex_vec)
            
            # 多样性分数 (与已选示例的最大相似度)
            if selected_vecs:
                max_sim = max(
                    cosine_similarity(ex_vec, s_vec)
                    for s_vec in selected_vecs
                )
                diversity = 1 - max_sim
            else:
                diversity = 1.0
            
            # MMR分数
            score = lambda_param * relevance + (1 - lambda_param) * diversity
            
            if score > best_score:
                best_score = score
                best_idx = i
        
        selected.append(examples[best_idx])
        selected_vecs.append(example_vecs[best_idx])
    
    return selected
```

---

## 🎯 4. 上下文缓存优化

### 4.1 问题背景

**成本问题**:
```python
# 每次请求都发送完整上下文
request_1: system_prompt (500 tokens) + history (1000 tokens)
request_2: system_prompt (500 tokens) + history (1200 tokens)
request_3: system_prompt (500 tokens) + history (1500 tokens)

# system_prompt重复发送,浪费成本!
```

### 4.2 缓存策略

#### 策略1: 系统提示词缓存

```python
class CachedContextManager:
    """带缓存的上下文管理器"""
    
    def __init__(self):
        self.system_prompt_cache = None
        self.system_prompt = None
    
    def set_system_prompt(self, prompt):
        """设置系统提示词"""
        if prompt != self.system_prompt:
            self.system_prompt = prompt
            # 调用API缓存系统提示词
            self.system_prompt_cache = cache_prompt(prompt)
    
    def get_context(self):
        """获取上下文,使用缓存的系统提示词"""
        return {
            "system_cache_id": self.system_prompt_cache,  # 使用缓存
            "messages": self.history
        }
```

#### 策略2: 前缀缓存

**原理**: 对话的前半部分通常不变,可以缓存

```python
# 请求1
context_1 = [msg1, msg2, msg3, msg4, msg5]
# 缓存前3条: cache_id = "abc123"

# 请求2 (只需发送新消息)
context_2 = {
    "cache_prefix": "abc123",  # 复用缓存
    "new_messages": [msg6, msg7]
}
```

**节省**:
- 减少发送的Token数
- 降低API成本
- 提高响应速度

### 4.3 缓存失效策略

```python
class SmartCache:
    """智能缓存管理"""
    
    def __init__(self, ttl=3600):
        """
        Args:
            ttl: Time To Live (秒)
        """
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        """获取缓存"""
        if key in self.cache:
            item = self.cache[key]
            
            # 检查是否过期
            if time.time() - item['timestamp'] < self.ttl:
                return item['value']
            else:
                # 过期,删除
                del self.cache[key]
        
        return None
    
    def set(self, key, value):
        """设置缓存"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def invalidate(self, pattern):
        """失效匹配模式的缓存"""
        keys_to_delete = [
            key for key in self.cache
            if pattern in key
        ]
        for key in keys_to_delete:
            del self.cache[key]
```

### 4.4 多级缓存

```
L1缓存 (内存) - 极快,小容量
   ↓ miss
L2缓存 (Redis) - 快,中容量
   ↓ miss
L3缓存 (数据库) - 慢,大容量
   ↓ miss
重新生成
```

---

## 🎯 5. 混合检索策略 (BM25 + 向量)

### 5.1 为什么需要混合检索?

**向量检索的局限**:
- 语义相似但关键词不匹配: ❌
- 专有名词匹配: ❌

**BM25的优势**:
- 精确关键词匹配: ✅
- 专有名词: ✅
- 不需要训练: ✅

**混合检索**: 结合两者优势

### 5.2 BM25算法

```python
from rank_bm25 import BM25Okapi
import jieba  # 中文分词

class BM25Retriever:
    """BM25检索器"""
    
    def __init__(self, documents):
        """
        Args:
            documents: 文档列表
        """
        # 分词
        tokenized_docs = [
            list(jieba.cut(doc))
            for doc in documents
        ]
        
        # 创建BM25索引
        self.bm25 = BM25Okapi(tokenized_docs)
        self.documents = documents
    
    def search(self, query, top_k=5):
        """
        检索最相关的文档
        
        Args:
            query: 查询
            top_k: 返回数量
        
        Returns:
            相关文档及分数
        """
        # 分词
        tokenized_query = list(jieba.cut(query))
        
        # BM25评分
        scores = self.bm25.get_scores(tokenized_query)
        
        # 排序
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        return [
            {
                'document': self.documents[i],
                'score': scores[i]
            }
            for i in top_indices
        ]
```

### 5.3 混合检索实现

```python
class HybridRetriever:
    """混合检索器: BM25 + 向量"""
    
    def __init__(self, documents, embedding_model):
        self.bm25 = BM25Retriever(documents)
        self.vector = VectorRetriever(documents, embedding_model)
        self.documents = documents
    
    def search(self, query, top_k=5, alpha=0.5):
        """
        混合检索
        
        Args:
            query: 查询
            top_k: 返回数量
            alpha: BM25权重 (0-1), 向量权重为1-alpha
        
        Returns:
            检索结果
        """
        # BM25检索
        bm25_results = self.bm25.search(query, top_k=top_k*2)
        
        # 向量检索
        vector_results = self.vector.search(query, top_k=top_k*2)
        
        # 归一化分数
        bm25_scores = self._normalize_scores(
            [r['score'] for r in bm25_results]
        )
        vector_scores = self._normalize_scores(
            [r['score'] for r in vector_results]
        )
        
        # 合并分数
        combined_scores = {}
        
        for i, result in enumerate(bm25_results):
            doc = result['document']
            combined_scores[doc] = alpha * bm25_scores[i]
        
        for i, result in enumerate(vector_results):
            doc = result['document']
            if doc in combined_scores:
                combined_scores[doc] += (1-alpha) * vector_scores[i]
            else:
                combined_scores[doc] = (1-alpha) * vector_scores[i]
        
        # 排序
        sorted_docs = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [doc for doc, score in sorted_docs[:top_k]]
    
    def _normalize_scores(self, scores):
        """归一化分数到0-1"""
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]
```

### 5.4 自适应权重

```python
def adaptive_hybrid_search(query, documents):
    """
    自适应混合检索
    
    根据查询特点动态调整BM25和向量的权重
    """
    # 分析查询特点
    has_keywords = contains_specific_terms(query)
    is_semantic = is_semantic_query(query)
    
    # 动态调整权重
    if has_keywords and not is_semantic:
        alpha = 0.8  # 偏重BM25
    elif is_semantic and not has_keywords:
        alpha = 0.2  # 偏重向量
    else:
        alpha = 0.5  # 均衡
    
    return hybrid_search(query, documents, alpha=alpha)
```

---

## 🎯 6. 上下文重排序 (Reranking)

### 6.1 为什么需要重排序?

**问题**: 初始检索可能不够精确

```
检索阶段: 快速,召回率高,但可能不精确
  ↓ 返回top-100
重排序阶段: 慢,但更精确
  ↓ 返回top-10
最终结果: 精确且相关
```

### 6.2 基于LLM的重排序

```python
class LLMReranker:
    """使用LLM重排序"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def rerank(self, query, candidates, top_k=5):
        """
        重排序候选文档
        
        Args:
            query: 查询
            candidates: 候选文档列表
            top_k: 返回数量
        
        Returns:
            重排序后的文档
        """
        scored = []
        
        for doc in candidates:
            # 让LLM评分相关性
            score = self._score_relevance(query, doc)
            scored.append((doc, score))
        
        # 按分数排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored[:top_k]]
    
    def _score_relevance(self, query, document):
        """
        LLM评分文档相关性
        
        Returns:
            相关性分数 (0-10)
        """
        prompt = f"""
请评估以下文档与查询的相关性,打分0-10:

查询: {query}

文档: {document}

相关性分数(只返回数字):"""
        
        response = self.llm.chat(prompt)
        
        try:
            score = float(response.strip())
            return max(0, min(10, score))  # 限制在0-10
        except:
            return 5.0  # 默认中等相关
```

### 6.3 交叉编码器重排序

```python
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    """交叉编码器重排序"""
    
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query, candidates, top_k=5):
        """
        重排序
        
        交叉编码器会同时编码query和document,
        比分别编码更精确
        """
        # 准备输入对
        pairs = [[query, doc] for doc in candidates]
        
        # 预测分数
        scores = self.model.predict(pairs)
        
        # 排序
        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored[:top_k]]
```

### 6.4 两阶段检索

```python
def two_stage_retrieval(query, documents, k1=100, k2=10):
    """
    两阶段检索
    
    阶段1: 快速检索,召回top-100
    阶段2: 精确重排序,返回top-10
    
    Args:
        query: 查询
        documents: 所有文档
        k1: 第一阶段召回数量
        k2: 最终返回数量
    
    Returns:
        最相关的k2个文档
    """
    # 阶段1: 快速向量检索
    stage1_results = vector_search(query, documents, top_k=k1)
    
    # 阶段2: 交叉编码器重排序
    reranker = CrossEncoderReranker()
    final_results = reranker.rerank(query, stage1_results, top_k=k2)
    
    return final_results
```

---

## 📊 性能对比

### 检索策略对比

| 策略 | 召回率 | 精确度 | 速度 | 成本 |
|------|--------|--------|------|------|
| 关键词 | 60% | 70% | ⚡⚡⚡ | 💰 |
| BM25 | 70% | 75% | ⚡⚡⚡ | 💰 |
| 向量 | 85% | 80% | ⚡⚡ | 💰💰 |
| 混合 | 90% | 85% | ⚡⚡ | 💰💰 |
| 混合+重排序 | 90% | 95% | ⚡ | 💰💰💰 |

### 压缩技术对比

| 技术 | 压缩率 | 信息保留 | 速度 | 成本 |
|------|--------|----------|------|------|
| 截断 | 30% | ⭐⭐⭐ | ⚡⚡⚡ | 💰 |
| 总结 | 70% | ⭐⭐⭐⭐ | ⚡ | 💰💰💰 |
| 递归总结 | 90% | ⭐⭐⭐⭐⭐ | ⚡ | 💰💰💰💰 |

---

## 💡 最佳实践建议

### 1. 选择合适的技术栈

**小规模应用** (< 1000文档):
- 简单向量检索
- 基础压缩
- 不需要缓存

**中规模应用** (1000-10000文档):
- 混合检索
- 递归总结
- Redis缓存

**大规模应用** (> 10000文档):
- 混合检索 + 重排序
- 分布式缓存
- 专用向量数据库

### 2. 成本优化

```python
# 优先级排序
priorities = [
    "1. 使用缓存 (节省40-60%)",
    "2. 上下文压缩 (节省30-50%)",
    "3. 批处理请求 (节省20-30%)",
    "4. 选择合适模型 (节省10-20%)"
]
```

### 3. 质量保证

```python
# 监控指标
metrics = {
    "召回率": "检索到的相关文档 / 所有相关文档",
    "精确度": "检索到的相关文档 / 检索到的所有文档",
    "MRR": "Mean Reciprocal Rank",
    "NDCG": "Normalized Discounted Cumulative Gain"
}
```

---

## 🚀 下一步实践

在下一部分,我们将实现这些高级技术的完整代码:

1. ✅ 向量相似度检索器
2. ✅ 递归总结引擎
3. ✅ 动态Few-shot选择器
4. ✅ 智能缓存系统
5. ✅ 混合检索引擎
6. ✅ 重排序优化器

---

**学习时间**: [进行中]  
**完成度**: 理论学习 100%  
**下一步**: 开始高级代码实践
