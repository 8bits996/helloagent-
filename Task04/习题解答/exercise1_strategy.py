"""
习题1: 上下文策略设计

设计一个多轮对话系统的上下文管理策略
要求:
- 支持最多10轮对话
- Token限制4096
- 保留关键信息
- 成本可控
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Message:
    """消息数据类"""
    role: str
    content: str
    importance: float = 5.0  # 重要性评分 1-10
    timestamp: float = 0.0
    tokens: int = 0


class MultiTurnDialogueStrategy:
    """多轮对话上下文管理策略"""
    
    def __init__(
        self,
        max_tokens: int = 4096,
        max_turns: int = 10,
        reserved_tokens: int = 512
    ):
        """
        初始化策略
        
        Args:
            max_tokens: 最大Token限制
            max_turns: 最多对话轮数
            reserved_tokens: 为LLM响应预留的Token
        """
        self.max_tokens = max_tokens
        self.max_turns = max_turns
        self.reserved_tokens = reserved_tokens
        
        # Token分配策略
        self.system_prompt_tokens = 100  # 系统提示固定预留
        self.recent_turns_tokens = 1500  # 最近消息优先保证
        
        # 消息存储
        self.messages: List[Message] = []
        self.system_prompt: Message = None
        
    def set_system_prompt(self, content: str):
        """设置系统提示"""
        tokens = self.estimate_tokens(content)
        self.system_prompt = Message(
            role="system",
            content=content,
            importance=10.0,  # 最高重要性
            tokens=tokens
        )
    
    def add_message(self, role: str, content: str, importance: float = 5.0):
        """添加消息"""
        tokens = self.estimate_tokens(content)
        msg = Message(
            role=role,
            content=content,
            importance=importance,
            tokens=tokens
        )
        self.messages.append(msg)
        
        # 限制对话轮数 (user + assistant = 1轮)
        if len([m for m in self.messages if m.role == "user"]) > self.max_turns:
            self._trim_old_messages()
    
    def get_context(self) -> List[Dict]:
        """获取优化后的上下文"""
        # 1. 计算可用Token
        available_tokens = self.max_tokens - self.reserved_tokens
        
        if self.system_prompt:
            available_tokens -= self.system_prompt.tokens
        
        # 2. 应用分层策略
        context = []
        
        # 添加系统提示
        if self.system_prompt:
            context.append({
                "role": self.system_prompt.role,
                "content": self.system_prompt.content
            })
        
        # 3. 处理对话消息
        optimized_msgs = self._optimize_messages(available_tokens)
        
        for msg in optimized_msgs:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    def _optimize_messages(self, available_tokens: int) -> List[Message]:
        """优化消息列表"""
        if not self.messages:
            return []
        
        # 策略: 三层管理
        # 1. 最近3轮 (6条消息) - 完整保留
        # 2. 重要消息 - 根据importance保留
        # 3. 历史消息 - 压缩或丢弃
        
        recent_count = 6  # 最近3轮对话
        recent_msgs = self.messages[-recent_count:] if len(self.messages) >= recent_count else self.messages
        history_msgs = self.messages[:-recent_count] if len(self.messages) > recent_count else []
        
        result = []
        used_tokens = 0
        
        # 1. 首先添加最近消息
        for msg in recent_msgs:
            if used_tokens + msg.tokens <= available_tokens:
                result.append(msg)
                used_tokens += msg.tokens
            else:
                # Token不足,截断消息内容
                remaining = available_tokens - used_tokens
                if remaining > 50:  # 至少保留50 tokens
                    truncated_msg = self._truncate_message(msg, remaining)
                    result.append(truncated_msg)
                    used_tokens += truncated_msg.tokens
                break
        
        # 2. 如果还有空间,添加重要的历史消息
        remaining_tokens = available_tokens - used_tokens
        if history_msgs and remaining_tokens > 200:
            important_msgs = self._select_important_messages(
                history_msgs,
                remaining_tokens
            )
            # 插入到最前面 (系统提示之后)
            result = important_msgs + result
        
        return result
    
    def _select_important_messages(
        self,
        messages: List[Message],
        max_tokens: int
    ) -> List[Message]:
        """选择重要的历史消息"""
        # 按重要性排序
        sorted_msgs = sorted(messages, key=lambda m: m.importance, reverse=True)
        
        selected = []
        used_tokens = 0
        
        for msg in sorted_msgs:
            if used_tokens + msg.tokens <= max_tokens:
                selected.append(msg)
                used_tokens += msg.tokens
            else:
                break
        
        # 按时间顺序返回
        return sorted(selected, key=lambda m: messages.index(m))
    
    def _truncate_message(self, msg: Message, max_tokens: int) -> Message:
        """截断消息内容"""
        # 简化: 按字符比例截断
        ratio = max_tokens / msg.tokens
        max_chars = int(len(msg.content) * ratio)
        
        truncated_content = msg.content[:max_chars] + "..."
        
        return Message(
            role=msg.role,
            content=truncated_content,
            importance=msg.importance,
            tokens=max_tokens
        )
    
    def _trim_old_messages(self):
        """删除最老的一轮对话"""
        # 找到第一个user消息和对应的assistant消息
        for i, msg in enumerate(self.messages):
            if msg.role == "user":
                # 删除这个user和可能的assistant回复
                if i + 1 < len(self.messages) and self.messages[i + 1].role == "assistant":
                    del self.messages[i:i+2]
                else:
                    del self.messages[i]
                break
    
    def estimate_tokens(self, text: str) -> int:
        """估算Token数量 (简化版: 1 token ≈ 4 chars)"""
        return len(text) // 4 + 1
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_tokens = sum(msg.tokens for msg in self.messages)
        if self.system_prompt:
            total_tokens += self.system_prompt.tokens
        
        user_msgs = [m for m in self.messages if m.role == "user"]
        
        return {
            "total_messages": len(self.messages),
            "total_turns": len(user_msgs),
            "total_tokens": total_tokens,
            "system_tokens": self.system_prompt.tokens if self.system_prompt else 0,
            "available_tokens": self.max_tokens - self.reserved_tokens,
            "token_usage": f"{total_tokens}/{self.max_tokens}",
            "usage_rate": f"{total_tokens / self.max_tokens * 100:.1f}%"
        }


# ============ 测试代码 ============

def test_multi_turn_strategy():
    """测试多轮对话策略"""
    print("=" * 60)
    print("测试: 多轮对话上下文管理策略")
    print("=" * 60)
    
    # 创建策略
    strategy = MultiTurnDialogueStrategy(
        max_tokens=4096,
        max_turns=10,
        reserved_tokens=512
    )
    
    # 设置系统提示
    strategy.set_system_prompt("你是一个专业的AI助手，能够进行多轮对话。")
    
    # 模拟10轮对话
    conversations = [
        ("你好！", "你好！很高兴为你服务。"),
        ("今天天气怎么样？", "抱歉，我无法获取实时天气信息。"),
        ("那你能做什么？", "我可以回答问题、提供建议、进行对话等。", 8.0),  # 重要消息
        ("给我讲个笑话", "为什么程序员喜欢黑暗？因为光太刺眼了！"),
        ("哈哈哈", "很高兴能逗你开心！"),
        ("你知道Python吗？", "是的，Python是一种高级编程语言。", 9.0),  # 重要消息
        ("能教我Python吗？", "当然！我们可以从基础开始学习。", 9.0),  # 重要消息
        ("先从变量开始", "好的！在Python中，变量不需要声明类型...", 8.0),
        ("很棒！", "谢谢！还有什么想学的吗？"),
        ("今天先到这里", "好的，随时欢迎回来继续学习！")
    ]
    
    # 添加对话
    for i, conv in enumerate(conversations, 1):
        user_msg = conv[0]
        assistant_msg = conv[1]
        importance = conv[2] if len(conv) > 2 else 5.0
        
        # 添加用户消息
        strategy.add_message("user", user_msg, importance=importance)
        # 添加助手消息
        strategy.add_message("assistant", assistant_msg, importance=importance)
        
        print(f"\n第 {i} 轮对话:")
        print(f"  User: {user_msg}")
        print(f"  Assistant: {assistant_msg}")
    
    # 获取优化后的上下文
    print("\n" + "=" * 60)
    print("优化后的上下文:")
    print("=" * 60)
    
    context = strategy.get_context()
    
    for i, msg in enumerate(context, 1):
        role = msg["role"]
        content = msg["content"]
        preview = content if len(content) <= 50 else content[:50] + "..."
        print(f"{i}. [{role}] {preview}")
    
    # 显示统计
    print("\n" + "=" * 60)
    print("统计信息:")
    print("=" * 60)
    
    stats = strategy.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 测试完成!")
    print("\n关键设计特点:")
    print("1. 最近3轮对话完整保留")
    print("2. 重要消息优先保留 (importance >= 8.0)")
    print("3. Token限制在4096以内")
    print("4. 系统提示始终保留")


def test_token_limit():
    """测试Token限制功能"""
    print("\n" + "=" * 60)
    print("测试: Token限制")
    print("=" * 60)
    
    strategy = MultiTurnDialogueStrategy(max_tokens=500)  # 严格限制
    strategy.set_system_prompt("你是AI助手。")
    
    # 添加大量对话
    for i in range(20):
        strategy.add_message("user", f"这是第{i+1}个用户问题，需要占用一定的Token空间。")
        strategy.add_message("assistant", f"这是第{i+1}个助手回答，包含详细的解释和说明。")
    
    context = strategy.get_context()
    stats = strategy.get_stats()
    
    print(f"\n总消息数: {stats['total_messages']}")
    print(f"上下文中消息数: {len(context) - 1}")  # 减去system
    print(f"Token使用: {stats['token_usage']}")
    print(f"使用率: {stats['usage_rate']}")
    
    # 计算实际上下文Token
    total_context_tokens = sum(
        strategy.estimate_tokens(msg["content"]) for msg in context
    )
    print(f"实际上下文Token: {total_context_tokens}")
    
    assert total_context_tokens <= strategy.max_tokens, "超出Token限制！"
    print("\n✅ Token限制测试通过!")


if __name__ == "__main__":
    test_multi_turn_strategy()
    test_token_limit()
    
    print("\n" + "=" * 60)
    print("习题1: 全部测试通过! ✅")
    print("=" * 60)
