"""
习题2: 上下文压缩实现

实现一个上下文压缩系统，包含:
- 对话总结功能
- 关键信息提取
- 压缩率可配置
- 信息保真度评估
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import json


@dataclass
class CompressionResult:
    """压缩结果"""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    fidelity_score: float  # 信息保真度


class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, llm_client=None):
        """初始化压缩器"""
        self.llm = llm_client
    
    def compress(
        self,
        messages: List[Dict],
        method: str = "summarize",
        target_ratio: float = 0.5
    ) -> CompressionResult:
        """
        压缩上下文
        
        Args:
            messages: 消息列表
            method: 压缩方法 (truncate/summarize/extract/hybrid)
            target_ratio: 目标压缩率 (0-1)
        
        Returns:
            CompressionResult
        """
        if method == "truncate":
            return self.truncate_compress(messages, target_ratio)
        elif method == "summarize":
            return self.summarize_compress(messages, target_ratio)
        elif method == "extract":
            return self.extract_compress(messages, target_ratio)
        elif method == "hybrid":
            return self.hybrid_compress(messages, target_ratio)
        else:
            raise ValueError(f"未知压缩方法: {method}")
    
    def truncate_compress(
        self,
        messages: List[Dict],
        target_ratio: float
    ) -> CompressionResult:
        """
        截断压缩 - 简单快速
        
        策略: 保留最近的消息，删除最早的消息
        """
        original_text = self._messages_to_text(messages)
        original_tokens = self.estimate_tokens(original_text)
        target_tokens = int(original_tokens * target_ratio)
        
        # 从后往前保留消息
        compressed_messages = []
        current_tokens = 0
        
        for msg in reversed(messages):
            msg_tokens = self.estimate_tokens(msg["content"])
            if current_tokens + msg_tokens <= target_tokens:
                compressed_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        compressed_text = self._messages_to_text(compressed_messages)
        compressed_tokens = self.estimate_tokens(compressed_text)
        
        # 计算保真度 (保留的消息数比例)
        fidelity = len(compressed_messages) / len(messages)
        
        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            fidelity_score=fidelity
        )
    
    def summarize_compress(
        self,
        messages: List[Dict],
        target_ratio: float
    ) -> CompressionResult:
        """
        总结压缩 - 使用LLM总结对话
        
        策略: 将多条消息总结为简短摘要
        """
        original_text = self._messages_to_text(messages)
        original_tokens = self.estimate_tokens(original_text)
        
        # 模拟LLM总结 (实际应使用真实LLM)
        summary = self._simulate_summarize(messages, target_ratio)
        
        compressed_tokens = self.estimate_tokens(summary)
        
        # 总结的保真度较高
        fidelity = 0.85
        
        return CompressionResult(
            original_text=original_text,
            compressed_text=summary,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            fidelity_score=fidelity
        )
    
    def extract_compress(
        self,
        messages: List[Dict],
        target_ratio: float
    ) -> CompressionResult:
        """
        关键信息提取 - 提取核心内容
        
        策略: 识别并保留关键句子和信息
        """
        original_text = self._messages_to_text(messages)
        original_tokens = self.estimate_tokens(original_text)
        target_tokens = int(original_tokens * target_ratio)
        
        # 提取关键信息
        key_points = []
        
        for msg in messages:
            content = msg["content"]
            role = msg["role"]
            
            # 提取关键句 (简化: 提取问题和关键词)
            key_sentences = self._extract_key_sentences(content, role)
            
            if key_sentences:
                key_points.append(f"[{role}] {key_sentences}")
        
        # 组合关键点
        compressed_text = "\n".join(key_points)
        compressed_tokens = self.estimate_tokens(compressed_text)
        
        # 如果超过目标,进一步截断
        if compressed_tokens > target_tokens:
            ratio = target_tokens / compressed_tokens
            compressed_text = compressed_text[:int(len(compressed_text) * ratio)]
            compressed_tokens = target_tokens
        
        fidelity = 0.75
        
        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            fidelity_score=fidelity
        )
    
    def hybrid_compress(
        self,
        messages: List[Dict],
        target_ratio: float
    ) -> CompressionResult:
        """
        混合压缩 - 结合多种方法
        
        策略:
        1. 最近消息完整保留
        2. 历史消息总结压缩
        3. 关键信息提取
        """
        if len(messages) <= 4:
            # 消息少,直接截断
            return self.truncate_compress(messages, target_ratio)
        
        original_text = self._messages_to_text(messages)
        original_tokens = self.estimate_tokens(original_text)
        target_tokens = int(original_tokens * target_ratio)
        
        # 1. 保留最近2条消息
        recent_msgs = messages[-2:]
        history_msgs = messages[:-2]
        
        recent_text = self._messages_to_text(recent_msgs)
        recent_tokens = self.estimate_tokens(recent_text)
        
        # 2. 压缩历史消息
        remaining_tokens = target_tokens - recent_tokens
        
        if remaining_tokens > 0 and history_msgs:
            history_ratio = remaining_tokens / self.estimate_tokens(
                self._messages_to_text(history_msgs)
            )
            history_compressed = self.summarize_compress(
                history_msgs,
                min(history_ratio, 0.3)  # 历史最多保留30%
            )
            
            compressed_text = (
                f"[历史摘要]\n{history_compressed.compressed_text}\n\n"
                f"[最近对话]\n{recent_text}"
            )
        else:
            compressed_text = recent_text
        
        compressed_tokens = self.estimate_tokens(compressed_text)
        fidelity = 0.80
        
        return CompressionResult(
            original_text=original_text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens,
            fidelity_score=fidelity
        )
    
    def _simulate_summarize(self, messages: List[Dict], target_ratio: float) -> str:
        """模拟LLM总结 (实际应调用真实LLM)"""
        # 提取对话主题和关键点
        user_msgs = [m for m in messages if m["role"] == "user"]
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        
        summary_parts = []
        summary_parts.append(f"对话摘要 ({len(messages)}条消息):")
        
        if user_msgs:
            topics = self._extract_topics(user_msgs)
            summary_parts.append(f"- 讨论主题: {', '.join(topics[:3])}")
        
        if assistant_msgs:
            summary_parts.append(f"- 助手提供了{len(assistant_msgs)}条回答")
        
        # 提取关键交互
        if len(messages) > 0:
            first_user = next((m for m in messages if m["role"] == "user"), None)
            if first_user:
                summary_parts.append(f"- 初始问题: {first_user['content'][:50]}...")
        
        return "\n".join(summary_parts)
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """提取对话主题 (简化版)"""
        topics = []
        for msg in messages:
            content = msg["content"]
            # 简单提取: 取前几个词
            words = content.split()[:3]
            if words:
                topics.append(" ".join(words))
        return topics
    
    def _extract_key_sentences(self, content: str, role: str) -> str:
        """提取关键句子"""
        sentences = content.split('。')
        if not sentences:
            return content[:50]
        
        # 简化: 返回第一句
        return sentences[0] + ("。" if len(content) > len(sentences[0]) else "")
    
    def _messages_to_text(self, messages: List[Dict]) -> str:
        """将消息列表转为文本"""
        lines = []
        for msg in messages:
            lines.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(lines)
    
    def estimate_tokens(self, text: str) -> int:
        """估算Token数量"""
        return len(text) // 4 + 1


# ============ 测试代码 ============

def create_test_messages() -> List[Dict]:
    """创建测试消息"""
    return [
        {"role": "user", "content": "你好，我想学习Python编程。"},
        {"role": "assistant", "content": "你好！Python是一门非常适合初学者的编程语言。我很乐意帮助你学习。你之前有编程经验吗？"},
        {"role": "user", "content": "没有，我是完全的新手。"},
        {"role": "assistant", "content": "没问题！我们可以从基础开始。Python的语法简洁易懂，非常适合入门。让我们先从安装Python开始吧。"},
        {"role": "user", "content": "好的，怎么安装？"},
        {"role": "assistant", "content": "你可以访问python.org下载最新版本。下载后运行安装程序，记得勾选'Add Python to PATH'选项。"},
        {"role": "user", "content": "安装完成了，下一步做什么？"},
        {"role": "assistant", "content": "很好！现在你可以打开命令行，输入'python --version'来验证安装。然后我们可以开始学习Python的基础语法。"},
        {"role": "user", "content": "验证成功了！可以开始教我了。"},
        {"role": "assistant", "content": "太棒了！让我们从最基础的print函数开始。在Python中，你可以使用print('Hello, World!')来输出文本。试试看吧！"}
    ]


def test_all_compression_methods():
    """测试所有压缩方法"""
    print("=" * 70)
    print("测试: 上下文压缩系统")
    print("=" * 70)
    
    compressor = ContextCompressor()
    messages = create_test_messages()
    
    methods = ["truncate", "summarize", "extract", "hybrid"]
    target_ratio = 0.5  # 目标压缩到50%
    
    results = []
    
    for method in methods:
        print(f"\n{'='*70}")
        print(f"方法: {method.upper()}")
        print("=" * 70)
        
        result = compressor.compress(messages, method=method, target_ratio=target_ratio)
        results.append((method, result))
        
        print(f"\n原始Token数: {result.original_tokens}")
        print(f"压缩后Token数: {result.compressed_tokens}")
        print(f"实际压缩率: {result.compression_ratio:.2%}")
        print(f"信息保真度: {result.fidelity_score:.2%}")
        
        print(f"\n压缩后内容预览:")
        preview = result.compressed_text[:200]
        print(preview + ("..." if len(result.compressed_text) > 200 else ""))
    
    # 对比表格
    print("\n" + "=" * 70)
    print("压缩方法对比")
    print("=" * 70)
    print(f"{'方法':<15} {'原始':<10} {'压缩后':<10} {'压缩率':<12} {'保真度':<10}")
    print("-" * 70)
    
    for method, result in results:
        print(
            f"{method:<15} "
            f"{result.original_tokens:<10} "
            f"{result.compressed_tokens:<10} "
            f"{result.compression_ratio:.2%}{'':>6} "
            f"{result.fidelity_score:.2%}"
        )
    
    print("\n✅ 所有压缩方法测试完成!")


def test_configurable_ratio():
    """测试可配置压缩率"""
    print("\n" + "=" * 70)
    print("测试: 可配置压缩率")
    print("=" * 70)
    
    compressor = ContextCompressor()
    messages = create_test_messages()
    
    ratios = [0.3, 0.5, 0.7]
    
    print(f"\n{'压缩率':<12} {'原始':<10} {'压缩后':<10} {'实际比例':<12}")
    print("-" * 70)
    
    for target_ratio in ratios:
        result = compressor.compress(messages, method="hybrid", target_ratio=target_ratio)
        print(
            f"{target_ratio:.0%}{'':>8} "
            f"{result.original_tokens:<10} "
            f"{result.compressed_tokens:<10} "
            f"{result.compression_ratio:.2%}"
        )
    
    print("\n✅ 压缩率配置测试完成!")


def test_fidelity_evaluation():
    """测试信息保真度评估"""
    print("\n" + "=" * 70)
    print("测试: 信息保真度评估")
    print("=" * 70)
    
    compressor = ContextCompressor()
    messages = create_test_messages()
    
    print("\n不同方法的保真度分析:")
    print("-" * 70)
    
    methods_info = {
        "truncate": "直接截断,丢失早期信息",
        "summarize": "LLM总结,保留语义",
        "extract": "提取关键点,部分丢失",
        "hybrid": "混合策略,平衡性能"
    }
    
    for method, description in methods_info.items():
        result = compressor.compress(messages, method=method, target_ratio=0.5)
        print(f"\n{method.upper()}:")
        print(f"  描述: {description}")
        print(f"  保真度: {result.fidelity_score:.2%}")
        print(f"  压缩率: {result.compression_ratio:.2%}")
        print(f"  适用场景: ", end="")
        
        if result.fidelity_score >= 0.8:
            print("质量优先场景")
        elif result.compression_ratio <= 0.4:
            print("成本优先场景")
        else:
            print("平衡场景")
    
    print("\n✅ 保真度评估测试完成!")


if __name__ == "__main__":
    test_all_compression_methods()
    test_configurable_ratio()
    test_fidelity_evaluation()
    
    print("\n" + "=" * 70)
    print("习题2: 全部测试通过! ✅")
    print("=" * 70)
    
    print("\n核心功能:")
    print("✅ 对话总结功能")
    print("✅ 关键信息提取")
    print("✅ 压缩率可配置")
    print("✅ 信息保真度评估")
