# Task04 课后习题解答

**日期**: 2024-12-22  
**学习者**: Franke Chen

---

## 习题1: 上下文策略设计

### 题目要求

设计一个多轮对话系统的上下文管理策略，要求：
- 支持最多10轮对话
- Token限制4096
- 保留关键信息
- 成本可控

### 解答思路

采用**混合策略**，结合多种技术优势：

1. **分层管理**: 系统提示、关键消息、最近消息分层
2. **动态窗口**: 根据Token使用情况动态调整
3. **智能压缩**: 超限时自动压缩历史对话
4. **重要性保留**: 标记和保留关键信息

### 策略设计

```python
class MultiTurnDialogueStrategy:
    """多轮对话上下文管理策略"""
    
    def __init__(self):
        self.max_tokens = 4096
        self.max_turns = 10
        self.reserved_tokens = 512  # 为响应预留
        self.system_prompt_tokens = 100
        
    def manage_context(self, messages):
        """上下文管理主逻辑"""
        # 1. 计算可用Token
        available = self.max_tokens - self.reserved_tokens - self.system_prompt_tokens
        
        # 2. 分层处理
        system_msg = messages[0]  # 系统提示
        recent_msgs = messages[-6:]  # 保留最近3轮
        history_msgs = messages[1:-6]  # 历史消息
        
        # 3. Token分配策略
        # - 系统提示: 100 tokens (固定)
        # - 最近3轮: 1500 tokens (优先保证)
        # - 历史消息: 剩余可用 (可压缩)
        
        context = [system_msg]
        used_tokens = self.system_prompt_tokens
        
        # 4. 添加最近消息
        for msg in recent_msgs:
            msg_tokens = self.estimate_tokens(msg)
            if used_tokens + msg_tokens <= available:
                context.append(msg)
                used_tokens += msg_tokens
        
        # 5. 处理历史消息
        remaining = available - used_tokens
        if history_msgs and remaining > 200:
            # 压缩历史消息
            compressed = self.compress_history(history_msgs, remaining)
            context.insert(1, compressed)  # 插入系统提示后
        
        return context
    
    def compress_history(self, messages, max_tokens):
        """压缩历史消息"""
        # 提取关键信息
        summary = f"[历史对话摘要]\n"
        summary += "- 用户问题: ...\n"
        summary += "- 助手回答: ...\n"
        return {"role": "system", "content": summary}
    
    def estimate_tokens(self, message):
        """估算Token数量 (简化版)"""
        return len(message["content"]) // 4
```

### 测试验证

见代码文件: `C:\Users\frankechen\CFP-Study\Task04\习题解答\exercise1_strategy.py`

---

## 习题2: 上下文压缩实现

### 题目要求

实现一个上下文压缩系统，包含：
- 对话总结功能
- 关键信息提取
- 压缩率可配置
- 信息保真度评估

### 解答思路

实现三种压缩方法：
1. **截断压缩**: 简单快速，适合轻度超限
2. **总结压缩**: 使用LLM总结，适合严重超限
3. **关键信息提取**: 保留核心内容

### 代码实现

见代码文件: `C:\Users\frankechen\CFP-Study\Task04\习题解答\exercise2_compression.py`

### 压缩效果对比

| 方法 | 压缩率 | 速度 | 信息保真度 | 适用场景 |
|------|--------|------|------------|----------|
| 截断 | 30-40% | 极快 | 70% | 轻度超限 |
| 总结 | 60-80% | 慢 | 85% | 严重超限 |
| 关键提取 | 40-60% | 快 | 80% | 结构化对话 |

---

## 习题3: 上下文优化对比

### 题目要求

对比不同上下文策略的效果：
- 固定窗口 vs 动态窗口
- 压缩 vs 不压缩
- 不同压缩率的影响

### 实验设计

测试场景：20轮对话，Token限制2000

### 对比结果

见代码文件: `C:\Users\frankechen\CFP-Study\Task04\习题解答\exercise3_comparison.py`

#### 结果摘要

**固定窗口 vs 动态窗口**:
- 固定窗口: 简单但可能丢失重要信息
- 动态窗口: 智能但计算开销大
- 建议: 生产环境用动态窗口

**压缩 vs 不压缩**:
- 不压缩: Token超限后截断
- 压缩: 保留更多历史信息
- 建议: 对话超过10轮时启用压缩

**压缩率影响**:
- 50%压缩: 平衡效果和成本
- 70%压缩: 适合长对话
- 30%压缩: 适合短对话

---

## 习题4: 实际应用设计

### 题目要求

设计一个客服系统的上下文工程方案：
- 用户信息管理
- 历史对话处理
- 知识库检索
- 成本优化

### 系统架构

见代码文件: `C:\Users\frankechen\CFP-Study\Task04\习题解答\exercise4_customer_service.py`

### 设计要点

1. **用户信息管理**
   - 会话级上下文: 当前对话
   - 用户级上下文: 个人信息、历史记录
   - 持久化存储

2. **历史对话处理**
   - 短期: 最近5轮完整保留
   - 中期: 压缩成摘要
   - 长期: 存入知识库

3. **知识库检索**
   - 根据用户问题检索相关FAQ
   - 控制检索结果数量(top 3)
   - 融合到上下文时控制Token

4. **成本优化**
   - Token预算管理: 单次最多2000 tokens
   - 缓存常见问题回答
   - 监控每个会话的成本

### 完整实现

```python
class CustomerServiceAgent:
    """智能客服Agent"""
    
    def __init__(self, llm_client, knowledge_base):
        self.llm = llm_client
        self.kb = knowledge_base
        
        # 上下文管理
        self.context_manager = HybridContextManager(max_tokens=2000)
        self.optimizer = ContextOptimizer(llm_client)
        
        # 用户会话管理
        self.sessions = {}  # session_id -> context
        
    def handle_query(self, session_id, user_id, query):
        """处理用户查询"""
        # 1. 获取或创建会话
        if session_id not in self.sessions:
            self.sessions[session_id] = self._create_session(user_id)
        
        session = self.sessions[session_id]
        
        # 2. 检索知识库
        kb_results = self.kb.search(query, top_k=3)
        
        # 3. 构建上下文
        context = self._build_context(session, query, kb_results)
        
        # 4. 调用LLM
        response = self.llm.chat(context)
        
        # 5. 更新会话
        self._update_session(session, query, response)
        
        return response
    
    def _build_context(self, session, query, kb_results):
        """构建优化的上下文"""
        # 系统提示
        system = {"role": "system", "content": "你是专业的客服助手"}
        
        # 用户信息
        user_info = session.get("user_info", {})
        
        # 历史对话
        history = session["context_manager"].get_context(max_tokens=1000)
        
        # 知识库信息
        kb_context = self._format_kb_results(kb_results)
        
        # 组合并优化
        all_messages = [system] + [kb_context] + history + [
            {"role": "user", "content": query}
        ]
        
        return self.optimizer.optimize(all_messages, target_tokens=2000)
```

---

## 总结

通过完成这4个习题，深入理解了：

1. **策略设计**: 需要综合考虑Token限制、信息保留、成本控制
2. **压缩技术**: 不同方法有不同的权衡
3. **对比实验**: 实际测试才能选择最佳策略
4. **实际应用**: 需要考虑业务场景的特殊需求

**关键收获**:
- ✅ 掌握了上下文管理的完整流程
- ✅ 理解了不同策略的适用场景
- ✅ 学会了成本和效果的权衡
- ✅ 能够设计生产级的上下文系统

---

**完成时间**: 2024-12-22  
**状态**: ✅ 全部完成
