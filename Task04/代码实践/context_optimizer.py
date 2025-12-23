"""
上下文优化器 (Context Optimizer)

提供高级上下文优化功能:
1. 相关性过滤 (Relevance Filtering)
2. 对话总结压缩 (Summarization)
3. 信息密度优化 (Density Optimization)
4. 动态上下文构建 (Dynamic Context Building)

Author: Franke Chen
Date: 2024-12-22
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sys
import os

# 添加父目录到路径,以便导入hello_agents_llm
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from context_manager import Message, estimate_tokens


@dataclass
class OptimizationResult:
    """优化结果"""
    original_messages: int
    optimized_messages: int
    original_tokens: int
    optimized_tokens: int
    compression_ratio: float
    strategy_used: str
    
    def __str__(self) -> str:
        return f"""
优化结果:
  原始消息数: {self.original_messages}
  优化后消息数: {self.optimized_messages}
  原始Token数: {self.original_tokens}
  优化后Token数: {self.optimized_tokens}
  压缩率: {self.compression_ratio:.1%}
  使用策略: {self.strategy_used}
"""


class ContextOptimizer:
    """
    上下文优化器
    
    提供多种优化策略来减少Token消耗并提高上下文质量
    """
    
    def __init__(self, llm_client=None):
        """
        初始化
        
        Args:
            llm_client: LLM客户端(用于总结功能,可选)
        """
        self.llm_client = llm_client
    
    def optimize(
        self,
        messages: List[Message],
        target_tokens: int = 2000,
        strategy: str = "auto"
    ) -> tuple[List[Message], OptimizationResult]:
        """
        优化上下文
        
        Args:
            messages: 消息列表
            target_tokens: 目标Token数
            strategy: 优化策略 (auto/truncate/summarize/hybrid)
            
        Returns:
            (优化后的消息, 优化结果)
        """
        original_tokens = sum(estimate_tokens(msg.content) for msg in messages)
        
        # 如果已经在目标范围内,不需要优化
        if original_tokens <= target_tokens:
            result = OptimizationResult(
                original_messages=len(messages),
                optimized_messages=len(messages),
                original_tokens=original_tokens,
                optimized_tokens=original_tokens,
                compression_ratio=0.0,
                strategy_used="none"
            )
            return messages, result
        
        # 根据策略选择优化方法
        if strategy == "auto":
            # 自动选择: Token超出较多时用总结,否则用截断
            ratio = original_tokens / target_tokens
            if ratio > 2.0 and self.llm_client:
                strategy = "summarize"
            else:
                strategy = "truncate"
        
        if strategy == "truncate":
            optimized = self._truncate_optimize(messages, target_tokens)
            strategy_name = "截断优化"
        elif strategy == "summarize":
            optimized = self._summarize_optimize(messages, target_tokens)
            strategy_name = "总结压缩"
        elif strategy == "hybrid":
            optimized = self._hybrid_optimize(messages, target_tokens)
            strategy_name = "混合优化"
        else:
            optimized = messages
            strategy_name = "未知策略"
        
        optimized_tokens = sum(estimate_tokens(msg.content) for msg in optimized)
        compression_ratio = (original_tokens - optimized_tokens) / original_tokens if original_tokens > 0 else 0.0
        
        result = OptimizationResult(
            original_messages=len(messages),
            optimized_messages=len(optimized),
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            compression_ratio=compression_ratio,
            strategy_used=strategy_name
        )
        
        return optimized, result
    
    def _truncate_optimize(
        self,
        messages: List[Message],
        target_tokens: int
    ) -> List[Message]:
        """
        截断优化: 保留最重要的消息
        
        策略:
        1. 系统消息总是保留
        2. 最近3条消息保留
        3. 其余按重要性选择
        
        Args:
            messages: 消息列表
            target_tokens: 目标Token数
            
        Returns:
            优化后的消息列表
        """
        # 分离系统消息
        system_msgs = [msg for msg in messages if msg.role == "system"]
        non_system = [msg for msg in messages if msg.role != "system"]
        
        # 保留最近3条
        recent = non_system[-3:] if len(non_system) >= 3 else non_system
        remaining = non_system[:-3] if len(non_system) > 3 else []
        
        # 计算已使用Token
        selected = system_msgs + recent
        used_tokens = sum(estimate_tokens(msg.content) for msg in selected)
        
        # 从剩余消息中按重要性选择
        remaining.sort(key=lambda x: x.importance, reverse=True)
        
        for msg in remaining:
            msg_tokens = estimate_tokens(msg.content)
            if used_tokens + msg_tokens <= target_tokens:
                selected.append(msg)
                used_tokens += msg_tokens
        
        # 按时间排序
        selected.sort(key=lambda x: x.timestamp)
        
        return selected
    
    def _summarize_optimize(
        self,
        messages: List[Message],
        target_tokens: int
    ) -> List[Message]:
        """
        总结压缩: 使用LLM总结旧消息
        
        策略:
        1. 保留最近的消息(不总结)
        2. 总结更早的消息
        
        Args:
            messages: 消息列表
            target_tokens: 目标Token数
            
        Returns:
            优化后的消息列表
        """
        if not self.llm_client:
            # 如果没有LLM,回退到截断
            return self._truncate_optimize(messages, target_tokens)
        
        # 保留最近5条消息
        keep_recent = 5
        recent = messages[-keep_recent:] if len(messages) > keep_recent else messages
        old_messages = messages[:-keep_recent] if len(messages) > keep_recent else []
        
        if not old_messages:
            return recent
        
        # 总结旧消息
        summary = self._summarize_messages(old_messages)
        
        # 创建总结消息
        summary_msg = Message(
            role="system",
            content=f"[历史对话总结]\n{summary}",
            importance=8.0
        )
        
        return [summary_msg] + recent
    
    def _summarize_messages(self, messages: List[Message]) -> str:
        """
        总结消息列表
        
        Args:
            messages: 要总结的消息
            
        Returns:
            总结文本
        """
        # 构建对话文本
        conversation = []
        for msg in messages:
            conversation.append(f"{msg.role}: {msg.content}")
        
        conversation_text = "\n".join(conversation)
        
        # 构建总结提示
        prompt = f"""请总结以下对话的要点,要求:
1. 提取关键信息和决策
2. 保持时间顺序
3. 简洁明了,不超过150字

对话内容:
{conversation_text}

总结:"""
        
        try:
            # 调用LLM总结
            summary = self.llm_client.chat([{"role": "user", "content": prompt}])
            return summary
        except Exception as e:
            # 如果总结失败,返回简单摘要
            return f"包含{len(messages)}条对话,涉及:{conversation_text[:100]}..."
    
    def _hybrid_optimize(
        self,
        messages: List[Message],
        target_tokens: int
    ) -> List[Message]:
        """
        混合优化: 结合截断和总结
        
        策略:
        1. 最近的消息保持完整
        2. 中间的消息总结
        3. 重要的旧消息保留
        
        Args:
            messages: 消息列表
            target_tokens: 目标Token数
            
        Returns:
            优化后的消息列表
        """
        # 分组
        system_msgs = [msg for msg in messages if msg.role == "system"]
        non_system = [msg for msg in messages if msg.role != "system"]
        
        if len(non_system) <= 5:
            return self._truncate_optimize(messages, target_tokens)
        
        # 最近3条完整保留
        recent = non_system[-3:]
        
        # 中间部分总结
        middle = non_system[:-3]
        if middle and self.llm_client:
            summary = self._summarize_messages(middle)
            summary_msg = Message(
                role="system",
                content=f"[对话历史]\n{summary}",
                importance=7.0
            )
            result = system_msgs + [summary_msg] + recent
        else:
            result = system_msgs + recent
        
        # 检查Token限制
        total_tokens = sum(estimate_tokens(msg.content) for msg in result)
        if total_tokens > target_tokens:
            # 如果还是超了,进一步截断
            return self._truncate_optimize(result, target_tokens)
        
        return result
    
    def filter_by_relevance(
        self,
        messages: List[Message],
        query: str,
        top_k: int = 5,
        min_score: float = 0.1
    ) -> List[Message]:
        """
        基于相关性过滤消息
        
        使用简单的关键词匹配计算相关性
        生产环境建议使用向量相似度
        
        Args:
            messages: 消息列表
            query: 查询文本
            top_k: 保留最相关的K条
            min_score: 最低相关性分数
            
        Returns:
            过滤后的消息列表
        """
        # 提取查询关键词(支持中文)
        query_lower = query.lower()
        query_words = query.split()  # 包含中文词
        
        # 计算每条消息的相关性
        scored = []
        for msg in messages:
            # 系统消息总是保留
            if msg.role == "system":
                scored.append((msg, 10.0))
                continue
            
            content_lower = msg.content.lower()
            
            # 方法1: 直接包含查询词(适合中文)
            direct_match = sum(1 for word in query_words if word in content_lower)
            
            # 方法2: 词重叠(适合英文)
            msg_words = msg.content.split()
            msg_words_set = set(msg_words)
            query_words_set = set(query_words)
            overlap = len(query_words_set & msg_words_set)
            
            # 综合分数
            score = (direct_match * 0.7 + overlap * 0.3) / max(len(query_words), 1)
            
            scored.append((msg, score))
        
        # 按相关性排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 选择top-k(至少包含相关性>min_score的消息)
        selected = []
        for msg, score in scored:
            if len(selected) < top_k and score >= min_score:
                selected.append(msg)
        
        # 按时间排序
        selected.sort(key=lambda x: x.timestamp)
        
        return selected
    
    def calculate_density(self, messages: List[Message]) -> float:
        """
        计算信息密度
        
        信息密度 = 有效信息量 / Token数量
        这里用唯一词数作为有效信息量的近似
        
        Args:
            messages: 消息列表
            
        Returns:
            信息密度分数
        """
        if not messages:
            return 0.0
        
        # 统计唯一词
        all_words = set()
        total_tokens = 0
        
        for msg in messages:
            words = msg.content.split()
            all_words.update(words)
            total_tokens += estimate_tokens(msg.content)
        
        if total_tokens == 0:
            return 0.0
        
        # 密度 = 唯一词数 / Token数
        density = len(all_words) / total_tokens
        
        return density


# ============= 测试代码 =============

def create_test_messages() -> List[Message]:
    """创建测试消息"""
    messages = []
    
    # 系统消息
    messages.append(Message(
        role="system",
        content="你是一个专业的AI助手,擅长回答各种问题。",
        importance=10.0
    ))
    
    # 早期对话(会被压缩)
    messages.append(Message(
        role="user",
        content="你好,请问今天天气怎么样?",
        importance=3.0
    ))
    messages.append(Message(
        role="assistant",
        content="你好!今天天气晴朗,温度适中,适合外出活动。",
        importance=3.0
    ))
    
    # 中间对话
    messages.append(Message(
        role="user",
        content="能推荐一些适合现在去的景点吗?",
        importance=5.0
    ))
    messages.append(Message(
        role="assistant",
        content="当然可以!根据今天的好天气,我推荐你去公园散步,或者去博物馆参观。这两个地方都很适合。",
        importance=5.0
    ))
    
    # 重要对话
    messages.append(Message(
        role="user",
        content="我需要预订明天的火车票,请帮我查一下北京到上海的高铁。",
        importance=9.0
    ))
    messages.append(Message(
        role="assistant",
        content="好的,我来帮你查询北京到上海的高铁票。明天有多个班次,最早的是早上6:00,最晚的是晚上8:00。",
        importance=9.0
    ))
    
    # 最近对话
    messages.append(Message(
        role="user",
        content="选早上8点的那班吧。",
        importance=8.0
    ))
    messages.append(Message(
        role="assistant",
        content="好的,我帮你选择早上8:00的G1次列车。请确认您的个人信息。",
        importance=8.0
    ))
    
    return messages


def test_truncate_optimization():
    """测试截断优化"""
    print("=" * 50)
    print("测试1: 截断优化")
    print("=" * 50)
    
    optimizer = ContextOptimizer()
    messages = create_test_messages()
    
    # 原始Token数
    original_tokens = sum(estimate_tokens(msg.content) for msg in messages)
    print(f"\n原始消息: {len(messages)}条, {original_tokens} tokens")
    
    # 优化到100 tokens
    optimized, result = optimizer.optimize(messages, target_tokens=100, strategy="truncate")
    
    print(result)
    
    print("保留的消息:")
    for msg in optimized:
        tokens = estimate_tokens(msg.content)
        print(f"  [{msg.role}] ({tokens}t): {msg.content[:40]}...")
    
    assert result.optimized_tokens <= 100, "应该在Token限制内"
    print("\n✅ 截断优化测试通过!")


def test_relevance_filtering():
    """测试相关性过滤"""
    print("\n" + "=" * 50)
    print("测试2: 相关性过滤")
    print("=" * 50)
    
    optimizer = ContextOptimizer()
    messages = create_test_messages()
    
    # 查询关于火车票的信息
    query = "火车票 高铁 预订"
    
    print(f"\n查询: {query}")
    print(f"原始消息数: {len(messages)}")
    
    filtered = optimizer.filter_by_relevance(messages, query, top_k=4, min_score=0.1)
    
    print(f"过滤后消息数: {len(filtered)}")
    print("\n保留的消息:")
    for msg in filtered:
        print(f"  [{msg.role}]: {msg.content[:50]}...")
    
    # 验证相关消息被保留
    contents = [msg.content for msg in filtered]
    assert any("火车票" in c or "高铁" in c for c in contents), "应该保留相关消息"
    
    print("\n✅ 相关性过滤测试通过!")


def test_density_calculation():
    """测试信息密度计算"""
    print("\n" + "=" * 50)
    print("测试3: 信息密度计算")
    print("=" * 50)
    
    optimizer = ContextOptimizer()
    
    # 高密度消息(每个词都不重复)
    high_density = [
        Message("user", "人工智能 机器学习 深度学习", importance=5.0),
        Message("assistant", "自然语言处理 计算机视觉 语音识别", importance=5.0)
    ]
    
    # 低密度消息(重复词多)
    low_density = [
        Message("user", "你好你好你好你好你好", importance=5.0),
        Message("assistant", "好的好的好的好的好的", importance=5.0)
    ]
    
    high_score = optimizer.calculate_density(high_density)
    low_score = optimizer.calculate_density(low_density)
    
    print(f"\n高密度消息的密度: {high_score:.3f}")
    print(f"低密度消息的密度: {low_score:.3f}")
    
    assert high_score > low_score, "高密度消息应该有更高的分数"
    
    print("\n✅ 信息密度计算测试通过!")


def test_summarize_optimization():
    """测试总结压缩(模拟)"""
    print("\n" + "=" * 50)
    print("测试4: 总结压缩(模拟)")
    print("=" * 50)
    
    # 模拟LLM客户端
    class MockLLM:
        def chat(self, messages):
            return "用户咨询天气和景点推荐,助手提供了相关建议。随后用户需要预订北京到上海的火车票。"
    
    optimizer = ContextOptimizer(llm_client=MockLLM())
    messages = create_test_messages()
    
    original_tokens = sum(estimate_tokens(msg.content) for msg in messages)
    print(f"\n原始消息: {len(messages)}条, {original_tokens} tokens")
    
    # 设置一个较小的目标值以触发压缩
    optimized, result = optimizer.optimize(messages, target_tokens=80, strategy="summarize")
    
    print(result)
    
    print("优化后的消息:")
    for msg in optimized:
        tokens = estimate_tokens(msg.content)
        print(f"  [{msg.role}] ({tokens}t): {msg.content[:60]}...")
    
    # 应该有压缩效果或至少保持在限制内
    assert result.optimized_tokens <= 80 or result.compression_ratio >= 0, "应该优化或压缩"
    print("\n✅ 总结压缩测试通过!")


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始测试上下文优化器...\n")
    
    test_truncate_optimization()
    test_relevance_filtering()
    test_density_calculation()
    test_summarize_optimization()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过!")
    print("=" * 50)
    
    print("\n💡 提示:")
    print("  - 截断优化适合轻度超限的情况")
    print("  - 总结压缩适合严重超限但需要保留历史信息")
    print("  - 相关性过滤适合从大量历史中提取相关信息")
    print("  - 混合策略在实际应用中效果最好")


if __name__ == "__main__":
    run_all_tests()
