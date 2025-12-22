"""
短期记忆系统实现
Short-term Memory for Agent

功能:
1. 对话历史管理
2. 滑动窗口策略
3. Token数量控制
4. 消息重要性管理
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class ShortTermMemory:
    """
    短期记忆系统 - 基础版本
    使用固定消息数量的滑动窗口
    """
    
    def __init__(self, max_messages: int = 10):
        """
        初始化短期记忆
        
        Args:
            max_messages: 最大保存的消息数量
        """
        self.messages: List[Dict] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加消息到记忆
        
        Args:
            role: 消息角色 (user/assistant/system)
            content: 消息内容
            metadata: 可选的元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # 维护滑动窗口
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # 删除最早的消息
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取消息列表
        
        Args:
            limit: 限制返回的消息数量
            
        Returns:
            消息列表
        """
        if limit is None:
            return self.messages.copy()
        return self.messages[-limit:]
    
    def get_conversation_history(self) -> str:
        """
        获取格式化的对话历史
        
        Returns:
            格式化的对话历史字符串
        """
        history = []
        for msg in self.messages:
            history.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(history)
    
    def clear(self):
        """清空所有消息"""
        self.messages = []
    
    def __len__(self):
        """返回当前消息数量"""
        return len(self.messages)
    
    def __str__(self):
        """字符串表示"""
        return f"ShortTermMemory(messages={len(self.messages)}/{self.max_messages})"


class TokenLimitedMemory:
    """
    基于Token数量限制的短期记忆
    更精确地控制上下文长度
    """
    
    def __init__(self, max_tokens: int = 4000):
        """
        初始化Token限制的记忆
        
        Args:
            max_tokens: 最大Token数量
        """
        self.messages: List[Dict] = []
        self.max_tokens = max_tokens
    
    def count_tokens(self, text: str) -> int:
        """
        估算Token数量（简化版本）
        实际应用中应使用tiktoken等专业工具
        
        Args:
            text: 文本内容
            
        Returns:
            估算的token数量
        """
        # 简化估算: 1 token ≈ 4 characters (英文)
        # 中文: 1 token ≈ 2 characters
        # 这里使用混合估算
        return len(text) // 3
    
    def get_total_tokens(self) -> int:
        """
        获取当前所有消息的总Token数
        
        Returns:
            总Token数
        """
        total = 0
        for msg in self.messages:
            total += self.count_tokens(msg["content"])
        return total
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加消息到记忆
        
        Args:
            role: 消息角色
            content: 消息内容
            metadata: 可选的元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tokens": self.count_tokens(content),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # 删除消息直到Token数量满足要求
        while self.get_total_tokens() > self.max_tokens and len(self.messages) > 1:
            removed = self.messages.pop(0)
            print(f"[Memory] 删除消息以控制Token: {removed['role']} ({removed['tokens']} tokens)")
    
    def get_messages(self) -> List[Dict]:
        """获取所有消息"""
        return self.messages.copy()
    
    def get_context_for_llm(self) -> List[Dict]:
        """
        获取适合LLM的消息格式
        
        Returns:
            标准的消息格式列表
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def clear(self):
        """清空所有消息"""
        self.messages = []
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "message_count": len(self.messages),
            "total_tokens": self.get_total_tokens(),
            "max_tokens": self.max_tokens,
            "utilization": f"{self.get_total_tokens() / self.max_tokens * 100:.1f}%"
        }
    
    def __str__(self):
        """字符串表示"""
        stats = self.get_stats()
        return f"TokenLimitedMemory({stats['total_tokens']}/{stats['max_tokens']} tokens, {stats['message_count']} messages)"


class ImportanceBasedMemory:
    """
    基于重要性的短期记忆
    保留重要的消息，删除不重要的
    """
    
    def __init__(self, max_messages: int = 10):
        """
        初始化重要性记忆
        
        Args:
            max_messages: 最大消息数量
        """
        self.messages: List[Dict] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str, importance: float = 1.0, metadata: Optional[Dict] = None):
        """
        添加消息到记忆
        
        Args:
            role: 消息角色
            content: 消息内容
            importance: 重要性分数 (0.0-10.0)
            metadata: 可选的元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "importance": importance,
            "access_count": 0,
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # 如果超过限制，删除最不重要的消息
        if len(self.messages) > self.max_messages:
            self._trim_by_importance()
    
    def _trim_by_importance(self):
        """根据重要性裁剪消息"""
        # 按重要性排序（降序）
        self.messages.sort(key=lambda x: x["importance"], reverse=True)
        # 保留前N条
        self.messages = self.messages[:self.max_messages]
        # 恢复时间顺序
        self.messages.sort(key=lambda x: x["timestamp"])
    
    def get_messages(self, min_importance: float = 0.0) -> List[Dict]:
        """
        获取消息列表
        
        Args:
            min_importance: 最小重要性阈值
            
        Returns:
            符合条件的消息列表
        """
        return [
            msg for msg in self.messages 
            if msg["importance"] >= min_importance
        ]
    
    def update_importance(self, index: int, new_importance: float):
        """
        更新消息的重要性
        
        Args:
            index: 消息索引
            new_importance: 新的重要性分数
        """
        if 0 <= index < len(self.messages):
            self.messages[index]["importance"] = new_importance
    
    def access_message(self, index: int):
        """
        访问消息（增加访问计数）
        
        Args:
            index: 消息索引
        """
        if 0 <= index < len(self.messages):
            self.messages[index]["access_count"] += 1
    
    def clear(self):
        """清空所有消息"""
        self.messages = []
    
    def __str__(self):
        """字符串表示"""
        avg_importance = sum(m["importance"] for m in self.messages) / len(self.messages) if self.messages else 0
        return f"ImportanceBasedMemory({len(self.messages)} messages, avg importance={avg_importance:.2f})"


# 示例使用
if __name__ == "__main__":
    print("=" * 50)
    print("测试1: 基础短期记忆")
    print("=" * 50)
    
    memory = ShortTermMemory(max_messages=5)
    
    # 添加消息
    memory.add_message("user", "你好，我叫张三")
    memory.add_message("assistant", "你好张三！很高兴认识你。")
    memory.add_message("user", "我喜欢编程")
    memory.add_message("assistant", "太好了！你最喜欢什么编程语言？")
    memory.add_message("user", "Python")
    memory.add_message("assistant", "Python是很好的选择！")
    
    print(f"\n{memory}")
    print(f"\n对话历史:\n{memory.get_conversation_history()}")
    
    # 测试滑动窗口
    print("\n添加更多消息测试滑动窗口...")
    memory.add_message("user", "你能教我吗？")
    print(f"\n{memory}")
    print(f"\n最近3条消息:")
    for msg in memory.get_messages(limit=3):
        print(f"  {msg['role']}: {msg['content']}")
    
    print("\n" + "=" * 50)
    print("测试2: Token限制的记忆")
    print("=" * 50)
    
    token_memory = TokenLimitedMemory(max_tokens=100)
    
    token_memory.add_message("user", "这是一条很长的消息，用于测试Token限制功能。" * 5)
    token_memory.add_message("assistant", "我理解了。")
    token_memory.add_message("user", "再添加一条长消息。" * 10)
    
    print(f"\n{token_memory}")
    print(f"\n统计信息: {json.dumps(token_memory.get_stats(), indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 50)
    print("测试3: 重要性记忆")
    print("=" * 50)
    
    imp_memory = ImportanceBasedMemory(max_messages=4)
    
    imp_memory.add_message("user", "你好", importance=5.0)
    imp_memory.add_message("assistant", "你好！", importance=3.0)
    imp_memory.add_message("user", "我的密码是123456", importance=10.0)  # 重要信息
    imp_memory.add_message("assistant", "收到", importance=5.0)
    imp_memory.add_message("user", "今天天气不错", importance=1.0)  # 不重要
    
    print(f"\n{imp_memory}")
    print(f"\n所有消息:")
    for msg in imp_memory.get_messages():
        print(f"  [{msg['importance']}] {msg['role']}: {msg['content']}")
    
    print("\n高重要性消息 (>=5.0):")
    for msg in imp_memory.get_messages(min_importance=5.0):
        print(f"  [{msg['importance']}] {msg['role']}: {msg['content']}")
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)
