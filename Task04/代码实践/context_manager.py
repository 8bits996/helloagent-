"""
上下文管理器 (Context Manager)

实现多种上下文窗口管理策略:
1. 滑动窗口 (Sliding Window)
2. Token限制窗口 (Token-Limited Window)
3. 重要性排序窗口 (Importance-Based Window)
4. 混合策略窗口 (Hybrid Strategy)

Author: Franke Chen
Date: 2024-12-22
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
import time


@dataclass
class Message:
    """消息数据类"""
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    timestamp: float = None
    importance: float = 5.0  # 重要性评分 0-10
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "role": self.role,
            "content": self.content
        }


def estimate_tokens(text: str) -> int:
    """
    估算文本的Token数量
    
    简化版: 英文约4字符=1token, 中文约1.5字符=1token
    生产环境建议使用tiktoken库
    
    Args:
        text: 输入文本
        
    Returns:
        估算的token数量
    """
    # 统计中英文字符
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    english_chars = len(text) - chinese_chars
    
    # 估算token数
    tokens = chinese_chars / 1.5 + english_chars / 4
    
    return int(tokens)


class BaseContextManager:
    """上下文管理器基类"""
    
    def __init__(self, max_messages: int = 20):
        """
        初始化
        
        Args:
            max_messages: 最大消息数量
        """
        self.max_messages = max_messages
        self.messages: List[Message] = []
    
    def add_message(
        self, 
        role: str, 
        content: str,
        importance: float = 5.0,
        metadata: Dict = None
    ) -> None:
        """
        添加消息
        
        Args:
            role: 角色 (system/user/assistant/tool)
            content: 消息内容
            importance: 重要性评分 (0-10)
            metadata: 元数据
        """
        message = Message(
            role=role,
            content=content,
            importance=importance,
            metadata=metadata or {}
        )
        self.messages.append(message)
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文 (需要子类实现)
        
        Returns:
            消息列表
        """
        raise NotImplementedError
    
    def clear(self) -> None:
        """清空所有消息"""
        self.messages.clear()
    
    def count_messages(self) -> int:
        """获取消息数量"""
        return len(self.messages)


class SlidingWindowManager(BaseContextManager):
    """
    滑动窗口管理器
    
    策略: 保持固定数量的最新消息
    优点: 简单、高效、Token可控
    缺点: 可能丢失重要历史信息
    """
    
    def __init__(self, max_messages: int = 10):
        """
        初始化
        
        Args:
            max_messages: 窗口大小(保留最近N条消息)
        """
        super().__init__(max_messages)
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文: 返回最新的N条消息
        
        Returns:
            最新的消息列表
        """
        # 保留最后max_messages条消息
        recent_messages = self.messages[-self.max_messages:]
        
        return [msg.to_dict() for msg in recent_messages]
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """重写add_message以自动清理旧消息"""
        super().add_message(role, content, **kwargs)
        
        # 如果超过限制,移除最早的消息
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)


class TokenLimitedManager(BaseContextManager):
    """
    Token限制管理器
    
    策略: 保持Token数量在限制内
    优点: 精确控制Token消耗
    缺点: 需要Token计数,计算开销大
    """
    
    def __init__(self, max_tokens: int = 2000):
        """
        初始化
        
        Args:
            max_tokens: 最大Token数量
        """
        super().__init__()
        self.max_tokens = max_tokens
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文: 返回Token数在限制内的消息
        
        Returns:
            Token数量受限的消息列表
        """
        result = []
        total_tokens = 0
        
        # 从最新消息开始,向前累加
        for msg in reversed(self.messages):
            msg_tokens = estimate_tokens(msg.content)
            
            if total_tokens + msg_tokens <= self.max_tokens:
                result.insert(0, msg.to_dict())
                total_tokens += msg_tokens
            else:
                break
        
        return result
    
    def get_token_count(self) -> int:
        """获取当前上下文的Token总数"""
        context = self.get_context()
        return sum(estimate_tokens(msg["content"]) for msg in context)


class ImportanceBasedManager(BaseContextManager):
    """
    基于重要性的管理器
    
    策略: 保留重要性最高的消息
    优点: 保留关键信息
    缺点: 可能打乱时间顺序,重要性判断困难
    """
    
    def __init__(self, max_messages: int = 10, keep_recent: int = 3):
        """
        初始化
        
        Args:
            max_messages: 最大消息数量
            keep_recent: 强制保留最近N条消息
        """
        super().__init__(max_messages)
        self.keep_recent = keep_recent
    
    def score_importance(self, message: Message) -> float:
        """
        评估消息重要性
        
        规则:
        1. 用户消息基础分+2
        2. 系统消息基础分+3
        3. 包含关键词+1
        4. 长消息(>100字符)+1
        5. 使用设置的importance值
        
        Args:
            message: 消息对象
            
        Returns:
            重要性分数
        """
        score = message.importance
        
        # 角色加分
        if message.role == "user":
            score += 2
        elif message.role == "system":
            score += 3
        
        # 关键词加分
        keywords = ["重要", "必须", "关键", "注意", "警告", "错误"]
        if any(kw in message.content for kw in keywords):
            score += 1
        
        # 长度加分
        if len(message.content) > 100:
            score += 1
        
        return score
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文: 返回重要性最高的消息
        
        Returns:
            按重要性排序的消息列表
        """
        # 1. 强制保留最近的消息
        recent = self.messages[-self.keep_recent:]
        remaining = self.messages[:-self.keep_recent]
        
        # 2. 对剩余消息按重要性排序
        scored = [(msg, self.score_importance(msg)) for msg in remaining]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 3. 选择top-k
        top_k = self.max_messages - len(recent)
        important = [msg for msg, _ in scored[:top_k]]
        
        # 4. 合并并按时间排序
        all_messages = important + recent
        all_messages.sort(key=lambda x: x.timestamp)
        
        return [msg.to_dict() for msg in all_messages]


class TimeDecayManager(BaseContextManager):
    """
    时间衰减管理器
    
    策略: 基于时间衰减的重要性评分
    优点: 符合人类记忆规律
    缺点: 可能丢失旧但重要的信息
    """
    
    def __init__(self, max_messages: int = 10, decay_factor: float = 0.9):
        """
        初始化
        
        Args:
            max_messages: 最大消息数量
            decay_factor: 时间衰减因子(0-1),越大衰减越慢
        """
        super().__init__(max_messages)
        self.decay_factor = decay_factor
    
    def calculate_score(self, message: Message) -> float:
        """
        计算带时间衰减的分数
        
        公式: score = base_score × decay_factor^(hours_passed)
        
        Args:
            message: 消息对象
            
        Returns:
            时间衰减后的分数
        """
        # 基础重要性
        base_score = message.importance
        
        # 计算时间差(小时)
        current_time = time.time()
        hours_passed = (current_time - message.timestamp) / 3600
        
        # 时间衰减
        time_weight = self.decay_factor ** hours_passed
        
        return base_score * time_weight
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文: 返回时间衰减分数最高的消息
        
        Returns:
            按衰减分数排序的消息列表
        """
        # 计算每条消息的衰减分数
        scored = [(msg, self.calculate_score(msg)) for msg in self.messages]
        
        # 按分数排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 选择top-k
        top_messages = [msg for msg, _ in scored[:self.max_messages]]
        
        # 按时间排序
        top_messages.sort(key=lambda x: x.timestamp)
        
        return [msg.to_dict() for msg in top_messages]


class HybridContextManager(BaseContextManager):
    """
    混合策略管理器
    
    策略: 结合多种策略的优点
    1. 系统消息总是保留
    2. 最近N条消息强制保留
    3. 其余消息按重要性+时间衰减选择
    4. 整体Token数量受限
    """
    
    def __init__(
        self, 
        max_tokens: int = 4000,
        keep_recent: int = 3,
        decay_factor: float = 0.95
    ):
        """
        初始化
        
        Args:
            max_tokens: 最大Token数量
            keep_recent: 强制保留最近N条消息
            decay_factor: 时间衰减因子
        """
        super().__init__()
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent
        self.decay_factor = decay_factor
    
    def calculate_score(self, message: Message) -> float:
        """
        计算综合分数 = 重要性 × 时间衰减
        
        Args:
            message: 消息对象
            
        Returns:
            综合分数
        """
        # 基础重要性
        base_score = message.importance
        
        # 角色加分
        if message.role == "user":
            base_score += 2
        elif message.role == "system":
            base_score += 5  # 系统消息非常重要
        
        # 时间衰减
        hours_passed = (time.time() - message.timestamp) / 3600
        time_weight = self.decay_factor ** hours_passed
        
        return base_score * time_weight
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        获取上下文: 混合策略
        
        步骤:
        1. 提取系统消息(总是保留)
        2. 提取最近N条消息(强制保留)
        3. 对剩余消息按综合分数排序
        4. 在Token限制内选择最多消息
        
        Returns:
            优化后的消息列表
        """
        # 步骤1: 分离系统消息
        system_msgs = [msg for msg in self.messages if msg.role == "system"]
        non_system = [msg for msg in self.messages if msg.role != "system"]
        
        # 步骤2: 强制保留最近N条
        recent = non_system[-self.keep_recent:] if len(non_system) >= self.keep_recent else non_system
        remaining = non_system[:-self.keep_recent] if len(non_system) > self.keep_recent else []
        
        # 步骤3: 对剩余消息评分并排序
        scored = [(msg, self.calculate_score(msg)) for msg in remaining]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 步骤4: 在Token限制内选择消息
        selected = system_msgs + recent
        total_tokens = sum(estimate_tokens(msg.content) for msg in selected)
        
        for msg, score in scored:
            msg_tokens = estimate_tokens(msg.content)
            if total_tokens + msg_tokens <= self.max_tokens:
                selected.append(msg)
                total_tokens += msg_tokens
            else:
                break
        
        # 按时间排序
        selected.sort(key=lambda x: x.timestamp)
        
        return [msg.to_dict() for msg in selected]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        context = self.get_context()
        return {
            "total_messages": len(self.messages),
            "context_messages": len(context),
            "total_tokens": sum(estimate_tokens(msg["content"]) for msg in context),
            "max_tokens": self.max_tokens,
            "token_usage": sum(estimate_tokens(msg["content"]) for msg in context) / self.max_tokens
        }


# ============= 测试代码 =============

def test_sliding_window():
    """测试滑动窗口管理器"""
    print("=" * 50)
    print("测试1: 滑动窗口管理器")
    print("=" * 50)
    
    manager = SlidingWindowManager(max_messages=5)
    
    # 添加10条消息
    for i in range(10):
        manager.add_message("user", f"消息{i+1}")
    
    context = manager.get_context()
    print(f"\n添加10条消息后,保留了{len(context)}条:")
    for msg in context:
        print(f"  - {msg['content']}")
    
    assert len(context) == 5, "应该只保留5条消息"
    assert context[0]['content'] == "消息6", "应该保留最新的5条"
    print("\n✅ 滑动窗口测试通过!")


def test_token_limited():
    """测试Token限制管理器"""
    print("\n" + "=" * 50)
    print("测试2: Token限制管理器")
    print("=" * 50)
    
    manager = TokenLimitedManager(max_tokens=100)
    
    # 添加不同长度的消息
    manager.add_message("user", "短消息")  # ~3 tokens
    manager.add_message("assistant", "这是一条中等长度的消息,包含一些内容")  # ~20 tokens
    manager.add_message("user", "这是一条很长很长的消息,包含大量的文字内容,用来测试Token限制功能是否正常工作,应该会占用比较多的Token数量")  # ~50 tokens
    
    context = manager.get_context()
    token_count = manager.get_token_count()
    
    print(f"\nToken限制: {manager.max_tokens}")
    print(f"实际使用: {token_count} tokens")
    print(f"保留消息: {len(context)}条")
    
    for msg in context:
        tokens = estimate_tokens(msg['content'])
        print(f"  - [{msg['role']}] ({tokens}t): {msg['content'][:30]}...")
    
    assert token_count <= manager.max_tokens, "Token数应在限制内"
    print("\n✅ Token限制测试通过!")


def test_importance_based():
    """测试重要性管理器"""
    print("\n" + "=" * 50)
    print("测试3: 重要性管理器")
    print("=" * 50)
    
    manager = ImportanceBasedManager(max_messages=5, keep_recent=2)
    
    # 添加不同重要性的消息
    manager.add_message("system", "你是一个AI助手", importance=10)
    manager.add_message("user", "普通问题1", importance=3)
    manager.add_message("user", "普通问题2", importance=3)
    manager.add_message("user", "重要问题!", importance=9)
    manager.add_message("assistant", "普通回答", importance=4)
    manager.add_message("user", "最近消息1", importance=5)
    manager.add_message("assistant", "最近消息2", importance=5)
    
    context = manager.get_context()
    
    print(f"\n总消息数: {manager.count_messages()}")
    print(f"保留消息: {len(context)}条")
    print("\n保留的消息:")
    for msg in context:
        print(f"  - [{msg['role']}] {msg['content']}")
    
    # 验证最近2条消息被保留
    assert context[-1]['content'] == "最近消息2", "应该保留最近的消息"
    assert context[-2]['content'] == "最近消息1", "应该保留最近的消息"
    
    print("\n✅ 重要性测试通过!")


def test_hybrid_manager():
    """测试混合策略管理器"""
    print("\n" + "=" * 50)
    print("测试4: 混合策略管理器")
    print("=" * 50)
    
    manager = HybridContextManager(
        max_tokens=200,
        keep_recent=2,
        decay_factor=0.9
    )
    
    # 添加多种消息
    manager.add_message("system", "你是一个专业的AI助手", importance=10)
    time.sleep(0.1)
    manager.add_message("user", "第一个问题", importance=5)
    time.sleep(0.1)
    manager.add_message("assistant", "第一个回答,包含详细的解释说明", importance=5)
    time.sleep(0.1)
    manager.add_message("user", "重要问题!", importance=9)
    time.sleep(0.1)
    manager.add_message("assistant", "重要回答", importance=9)
    time.sleep(0.1)
    manager.add_message("user", "最近问题1", importance=5)
    time.sleep(0.1)
    manager.add_message("assistant", "最近回答1", importance=5)
    
    context = manager.get_context()
    stats = manager.get_stats()
    
    print(f"\n统计信息:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  保留消息: {stats['context_messages']}")
    print(f"  Token使用: {stats['total_tokens']}/{stats['max_tokens']}")
    print(f"  使用率: {stats['token_usage']:.1%}")
    
    print(f"\n保留的消息:")
    for msg in context:
        tokens = estimate_tokens(msg['content'])
        print(f"  - [{msg['role']}] ({tokens}t): {msg['content']}")
    
    assert stats['total_tokens'] <= stats['max_tokens'], "Token应在限制内"
    assert any(msg['role'] == 'system' for msg in context), "应该保留系统消息"
    
    print("\n✅ 混合策略测试通过!")


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始测试上下文管理器...\n")
    
    test_sliding_window()
    test_token_limited()
    test_importance_based()
    test_hybrid_manager()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
