# Task04 学习笔记 - 第九章:上下文工程

**学习日期**: 2024-12-22  
**学习者**: Franke Chen

---

## 📚 第一部分:上下文工程概述

### 1.1 什么是上下文工程?

**定义**:
上下文工程(Context Engineering)是指在与大语言模型(LLM)交互时,有策略地构建、管理和优化输入上下文的技术和方法,以提高模型输出质量、降低成本并满足Token限制。

**核心目标**:
1. **质量优化**: 提供最相关的上下文信息
2. **成本控制**: 在Token限制内传递最多有效信息
3. **性能提升**: 减少不必要的Token消耗
4. **效果保证**: 确保模型获得足够的上下文

### 1.2 上下文工程 vs Prompt Engineering

| 维度 | Prompt Engineering | Context Engineering |
|------|-------------------|---------------------|
| **关注点** | 如何表达指令 | 如何组织上下文 |
| **优化对象** | 提示词本身 | 整个输入内容 |
| **主要技术** | 指令设计、Few-shot | 窗口管理、压缩 |
| **应用场景** | 单次调用 | 多轮对话、长文本 |
| **Token关注** | 提示词Token | 全部输入Token |

**关系**:
- Prompt Engineering是上下文工程的一部分
- 上下文工程包含更广泛的技术
- 两者相辅相成,共同优化LLM性能

### 1.3 上下文在Agent中的作用

```
┌─────────────────────────────────────────┐
│            Agent 系统                    │
├─────────────────────────────────────────┤
│                                         │
│  用户输入                                │
│      ↓                                  │
│  ┌──────────────────────────────────┐  │
│  │      上下文构建(Context Build)    │  │
│  ├──────────────────────────────────┤  │
│  │ • 系统指令(System Prompt)         │  │
│  │ • 对话历史(Conversation History)  │  │
│  │ • 检索信息(Retrieved Info)        │  │
│  │ • 工具输出(Tool Outputs)          │  │
│  └──────────────────────────────────┘  │
│      ↓                                  │
│  ┌──────────────────────────────────┐  │
│  │    上下文优化(Context Optimize)   │  │
│  ├──────────────────────────────────┤  │
│  │ • Token控制                       │  │
│  │ • 相关性过滤                      │  │
│  │ • 信息压缩                        │  │
│  └──────────────────────────────────┘  │
│      ↓                                  │
│  ┌──────────────────────────────────┐  │
│  │         LLM 处理                  │  │
│  └──────────────────────────────────┘  │
│      ↓                                  │
│  输出结果                                │
│                                         │
└─────────────────────────────────────────┘
```

### 1.4 上下文的组成部分

#### 1. 系统指令(System Prompt)
```python
system_prompt = """
你是一个专业的AI助手。
你的回答应该:
- 准确、专业
- 结构清晰
- 简洁明了
"""
```

**特点**:
- 固定不变
- 定义Agent角色和行为
- Token消耗相对固定

#### 2. 对话历史(Conversation History)
```python
history = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好!有什么可以帮助你的?"},
    {"role": "user", "content": "告诉我关于Python的信息"},
    # ...更多历史消息
]
```

**特点**:
- 动态增长
- 保持对话连贯性
- 是主要的Token消耗源

#### 3. 检索信息(Retrieved Information)
```python
retrieved_info = """
相关文档1: Python是一种高级编程语言...
相关文档2: Python的特点包括...
相关文档3: Python常用于...
"""
```

**特点**:
- 来自RAG系统
- 提供外部知识
- 需要相关性过滤

#### 4. 工具输出(Tool Outputs)
```python
tool_outputs = [
    "搜索结果: ...",
    "天气信息: 北京今天晴天,20°C",
    "计算结果: 1234 + 5678 = 6912"
]
```

**特点**:
- 动态生成
- 任务相关
- 需要格式化

### 1.5 上下文工程的挑战

#### 挑战1: Token限制
```python
# 不同模型的Token限制
model_limits = {
    "gpt-3.5-turbo": 4096,
    "gpt-4": 8192,
    "gpt-4-turbo": 128000,
    "claude-3": 200000,
}
```

**问题**:
- 上下文太长会超出限制
- 需要智能截断或压缩
- 不同模型限制不同

**解决思路**:
- 窗口管理
- 上下文压缩
- 动态选择

#### 挑战2: 信息过载
```python
# 信息过多的问题
too_much_info = """
- 100轮对话历史
- 50个检索结果
- 20个工具输出
- 各种系统指令
→ LLM处理效率下降
→ 关键信息被淹没
→ 成本显著增加
"""
```

**问题**:
- 信息太多,LLM难以聚焦
- "Lost in the Middle"现象
- 响应质量下降

**解决思路**:
- 相关性排序
- 信息过滤
- 分层管理

#### 挑战3: 相关性判断
```python
# 如何判断哪些历史是相关的?
query = "今天天气怎么样?"

# 相关历史
relevant = [
    "我在北京",  # 相关!
    "帮我查天气",  # 相关!
]

# 不相关历史
irrelevant = [
    "1+1等于几?",  # 不相关
    "讲个笑话",  # 不相关
]
```

**问题**:
- 难以自动判断相关性
- 需要语义理解
- 计算成本

**解决思路**:
- 向量相似度
- LLM辅助判断
- 启发式规则

#### 挑战4: 成本控制
```python
# Token成本计算
def calculate_cost(tokens, model="gpt-4"):
    prices = {
        "gpt-3.5-turbo": {"input": 0.0015/1000, "output": 0.002/1000},
        "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
    }
    
    # 假设输入输出比例1:1
    cost = tokens * (prices[model]["input"] + prices[model]["output"]) / 2
    return cost

# 10000 tokens的成本
print(calculate_cost(10000, "gpt-4"))  # $0.45
```

**问题**:
- Token越多,成本越高
- 长对话成本累积
- 需要在质量和成本间平衡

**解决思路**:
- Token预算管理
- 压缩技术
- 模型选择

---

## 📚 第二部分:上下文窗口管理

### 2.1 固定窗口策略

#### 策略1: 滑动窗口(Sliding Window)

**原理**:
```python
# 保持固定数量的消息
max_messages = 10

history = []
for message in all_messages:
    history.append(message)
    if len(history) > max_messages:
        history.pop(0)  # 移除最早的消息
```

**可视化**:
```
初始状态: []
添加M1:   [M1]
添加M2:   [M1, M2]
...
添加M10:  [M1, M2, ..., M10]
添加M11:  [M2, M3, ..., M11]  ← M1被移除
添加M12:  [M3, M4, ..., M12]  ← M2被移除
```

**优点**:
- ✅ 实现简单
- ✅ Token数量可控
- ✅ 计算效率高

**缺点**:
- ❌ 可能丢失重要信息
- ❌ 无法处理长期依赖
- ❌ 缺乏灵活性

**适用场景**:
- 简单对话系统
- Token限制严格
- 对历史依赖不强

#### 策略2: 固定Token窗口

**原理**:
```python
def keep_within_token_limit(messages, max_tokens=2000):
    """保持Token数量在限制内"""
    result = []
    total_tokens = 0
    
    # 从最新消息开始
    for msg in reversed(messages):
        msg_tokens = count_tokens(msg["content"])
        if total_tokens + msg_tokens <= max_tokens:
            result.insert(0, msg)
            total_tokens += msg_tokens
        else:
            break
    
    return result
```

**优点**:
- ✅ Token控制精确
- ✅ 利用率高

**缺点**:
- ❌ 需要Token计数工具
- ❌ 计算开销较大

#### 策略3: 截断策略

**头部截断**:
```python
# 保留最新的N条消息
recent_history = messages[-10:]
```

**尾部截断**:
```python
# 保留最早的N条消息(罕见)
early_history = messages[:5]
```

**中间截断**:
```python
# 保留开头和结尾,移除中间
context = messages[:3] + ["..."] + messages[-5:]
```

### 2.2 动态窗口策略

#### 策略1: 基于重要性

**原理**:
```python
def score_importance(message):
    """评估消息重要性"""
    score = 0
    
    # 规则1: 用户消息更重要
    if message["role"] == "user":
        score += 5
    
    # 规则2: 包含关键词
    keywords = ["重要", "必须", "关键"]
    if any(kw in message["content"] for kw in keywords):
        score += 3
    
    # 规则3: 长消息可能更重要
    if len(message["content"]) > 100:
        score += 2
    
    return score

def keep_important_messages(messages, max_count=10):
    """保留最重要的消息"""
    # 添加重要性分数
    scored = [(msg, score_importance(msg)) for msg in messages]
    
    # 按重要性排序
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # 保留top-k
    important = [msg for msg, _ in scored[:max_count]]
    
    return important
```

**优点**:
- ✅ 保留关键信息
- ✅ 更智能的选择

**缺点**:
- ❌ 重要性判断困难
- ❌ 可能打乱时间顺序

#### 策略2: 基于相关性

**原理**:
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def filter_relevant_messages(messages, current_query, top_k=5):
    """基于语义相关性过滤消息"""
    
    # 获取当前查询的向量
    query_embedding = model.encode(current_query)
    
    # 计算每条消息的相关性
    scored = []
    for msg in messages:
        msg_embedding = model.encode(msg["content"])
        similarity = np.dot(query_embedding, msg_embedding)
        scored.append((msg, similarity))
    
    # 按相关性排序
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # 返回最相关的消息
    return [msg for msg, _ in scored[:top_k]]
```

**优点**:
- ✅ 语义级别匹配
- ✅ 高度相关

**缺点**:
- ❌ 计算开销大
- ❌ 需要Embedding模型

#### 策略3: 基于时间衰减

**原理**:
```python
import time

def time_weighted_filter(messages, current_time, decay_factor=0.9):
    """基于时间衰减的消息过滤"""
    
    scored = []
    for msg in messages:
        # 计算时间差(小时)
        time_diff = (current_time - msg["timestamp"]) / 3600
        
        # 时间衰减因子
        time_weight = decay_factor ** time_diff
        
        # 基础重要性
        base_score = score_importance(msg)
        
        # 最终得分
        final_score = base_score * time_weight
        
        scored.append((msg, final_score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [msg for msg, _ in scored[:10]]
```

**公式**:
```
score(t) = base_score × decay_factor^(time_diff)

例如:
- 1小时前的消息: score × 0.9^1 = score × 0.9
- 2小时前的消息: score × 0.9^2 = score × 0.81
- 10小时前的消息: score × 0.9^10 ≈ score × 0.35
```

**优点**:
- ✅ 自然符合人类记忆
- ✅ 渐进式遗忘

**缺点**:
- ❌ 需要时间戳
- ❌ 可能丢失旧但重要的信息

### 2.3 混合策略

**原理**: 结合多种策略的优点

```python
class HybridContextManager:
    """混合上下文管理策略"""
    
    def __init__(self, max_messages=20, max_tokens=4000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def manage_context(self, messages, current_query):
        """混合策略管理上下文"""
        
        # 步骤1: 保留系统消息和最近3条
        system_msgs = [m for m in messages if m["role"] == "system"]
        recent_msgs = messages[-3:]
        must_keep = system_msgs + recent_msgs
        
        # 步骤2: 从剩余消息中按相关性选择
        remaining = [m for m in messages if m not in must_keep]
        relevant = self.filter_by_relevance(remaining, current_query, top_k=10)
        
        # 步骤3: 合并并按Token限制
        combined = must_keep + relevant
        final = self.keep_within_tokens(combined, self.max_tokens)
        
        return final
    
    def filter_by_relevance(self, messages, query, top_k):
        """基于相关性过滤"""
        # (实现如前所述)
        pass
    
    def keep_within_tokens(self, messages, max_tokens):
        """Token限制"""
        # (实现如前所述)
        pass
```

**优点**:
- ✅ 综合多种策略优点
- ✅ 灵活性高
- ✅ 效果好

**缺点**:
- ❌ 实现复杂
- ❌ 计算开销大

---

## 📚 第三部分:上下文压缩技术

### 3.1 总结压缩(Summarization)

#### 原理

使用LLM对长文本进行总结,保留关键信息,减少Token数量。

#### 实现

```python
def summarize_conversation(messages, llm_client):
    """总结对话历史"""
    
    # 将消息格式化
    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg['role']}: {msg['content']}\n"
    
    # 构建总结提示
    summary_prompt = f"""
请总结以下对话的要点:

{conversation_text}

总结要求:
1. 提取关键信息
2. 保持时间顺序
3. 不超过200字
"""
    
    # 调用LLM总结
    summary = llm_client.chat([
        {"role": "user", "content": summary_prompt}
    ])
    
    return summary
```

#### 渐进式总结

```python
class ProgressiveSummarizer:
    """渐进式总结器"""
    
    def __init__(self, llm_client, chunk_size=10):
        self.llm_client = llm_client
        self.chunk_size = chunk_size
        self.summaries = []
    
    def add_messages(self, messages):
        """添加消息"""
        if len(messages) >= self.chunk_size:
            # 总结这批消息
            summary = self.summarize(messages)
            self.summaries.append(summary)
            return []  # 清空
        return messages
    
    def get_context(self):
        """获取压缩后的上下文"""
        # 返回所有总结 + 当前未总结的消息
        return "\n".join(self.summaries)
```

#### 优缺点

**优点**:
- ✅ 压缩率高(可达10:1)
- ✅ 保留关键信息
- ✅ 可读性好

**缺点**:
- ❌ 需要额外LLM调用(成本)
- ❌ 可能丢失细节
- ❌ 有延迟

### 3.2 向量压缩(Vector Compression)

#### 原理

将文本转换为向量表示,存储向量而非原始文本,需要时重建或检索。

#### 实现

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorMemory:
    """基于向量的记忆系统"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectors = []
        self.metadata = []
    
    def store(self, text, meta=None):
        """存储文本的向量表示"""
        vector = self.model.encode(text)
        self.vectors.append(vector)
        self.metadata.append(meta or {})
    
    def retrieve(self, query, top_k=3):
        """检索最相关的记忆"""
        query_vec = self.model.encode(query)
        
        # 计算相似度
        similarities = [
            np.dot(query_vec, vec) 
            for vec in self.vectors
        ]
        
        # 获取top-k索引
        top_indices = np.argsort(similarities)[-top_k:]
        
        # 返回元数据
        return [self.metadata[i] for i in top_indices]
```

#### 优缺点

**优点**:
- ✅ 存储空间小
- ✅ 检索高效
- ✅ 语义保留

**缺点**:
- ❌ 无法完全重建原文
- ❌ 需要Embedding模型
- ❌ 仅适合检索场景

### 3.3 混合压缩

#### 策略: 关键信息保留 + 其余总结

```python
class HybridCompressor:
    """混合压缩器"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def compress(self, messages, keep_recent=3):
        """混合压缩策略"""
        
        # 1. 保留最近N条消息(完整)
        recent = messages[-keep_recent:]
        
        # 2. 总结更早的消息
        old_messages = messages[:-keep_recent]
        if old_messages:
            summary = self.summarize(old_messages)
            compressed = [
                {"role": "system", "content": f"历史对话总结:\n{summary}"}
            ]
        else:
            compressed = []
        
        # 3. 合并
        return compressed + recent
    
    def summarize(self, messages):
        """总结消息"""
        # (实现如前所述)
        pass
```

---

## 📚 第四部分:实践代码框架

### 4.1 ContextManager实现

```python
# 详见 代码实践/context_manager.py
```

### 4.2 ContextOptimizer实现

```python
# 详见 代码实践/context_optimizer.py
```

### 4.3 ContextAwareAgent实现

```python
# 详见 代码实践/context_aware_agent.py
```

---

## 💡 关键要点总结

### 核心概念
1. 上下文工程是优化LLM输入的系统性方法
2. 需要平衡质量、成本和效率
3. 不同场景需要不同策略

### 技术要点
1. **窗口管理**: 控制上下文大小
2. **压缩技术**: 减少Token消耗
3. **相关性过滤**: 保留重要信息
4. **动态调整**: 根据任务优化

### 最佳实践
1. 优先使用简单策略(滑动窗口)
2. 根据需求逐步引入高级技术
3. 监控Token消耗和成本
4. A/B测试不同策略效果

---

**学习时间**: [待填写]  
**完成度**: 进行中  
**下一步**: 开始代码实践
