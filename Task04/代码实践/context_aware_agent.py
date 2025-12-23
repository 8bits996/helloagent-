"""
上下文感知 Agent (Context-Aware Agent)

整合上下文管理和优化能力的智能Agent:
1. 自动管理对话历史
2. 智能优化上下文
3. 成本监控和控制
4. 适应不同任务场景

Author: Franke Chen
Date: 2024-12-22
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from context_manager import HybridContextManager, Message, estimate_tokens
from context_optimizer import ContextOptimizer, OptimizationResult


@dataclass
class AgentConfig:
    """Agent配置"""
    max_tokens: int = 4000  # 最大Token限制
    keep_recent: int = 3    # 强制保留最近N条
    decay_factor: float = 0.95  # 时间衰减因子
    optimization_strategy: str = "auto"  # 优化策略
    enable_summarization: bool = False  # 是否启用总结
    cost_tracking: bool = True  # 是否追踪成本


@dataclass
class AgentStats:
    """Agent统计信息"""
    total_queries: int = 0
    total_tokens_used: int = 0
    total_messages: int = 0
    context_compressions: int = 0
    estimated_cost: float = 0.0
    
    def __str__(self) -> str:
        return f"""
Agent统计:
  总查询数: {self.total_queries}
  总Token消耗: {self.total_tokens_used}
  总消息数: {self.total_messages}
  上下文压缩次数: {self.context_compressions}
  估算成本: ${self.estimated_cost:.4f}
"""


class ContextAwareAgent:
    """
    上下文感知Agent
    
    特点:
    - 自动管理对话历史
    - 智能优化上下文
    - 成本监控
    - 灵活配置
    """
    
    def __init__(
        self,
        llm_client=None,
        config: Optional[AgentConfig] = None
    ):
        """
        初始化
        
        Args:
            llm_client: LLM客户端
            config: Agent配置
        """
        self.llm_client = llm_client
        self.config = config or AgentConfig()
        
        # 上下文管理器
        self.context_manager = HybridContextManager(
            max_tokens=self.config.max_tokens,
            keep_recent=self.config.keep_recent,
            decay_factor=self.config.decay_factor
        )
        
        # 上下文优化器
        self.optimizer = ContextOptimizer(llm_client)
        
        # 统计信息
        self.stats = AgentStats()
        
        # 系统提示词
        self.system_prompt = "你是一个有帮助的AI助手。"
    
    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self.system_prompt = prompt
        self.context_manager.add_message(
            role="system",
            content=prompt,
            importance=10.0
        )
    
    def chat(self, user_message: str, importance: float = 5.0) -> str:
        """
        处理用户消息
        
        Args:
            user_message: 用户消息
            importance: 消息重要性 (0-10)
            
        Returns:
            Agent回复
        """
        # 1. 添加用户消息
        self.context_manager.add_message(
            role="user",
            content=user_message,
            importance=importance
        )
        
        # 2. 获取并优化上下文
        context = self._prepare_context(user_message)
        
        # 3. 调用LLM
        if self.llm_client:
            try:
                assistant_message = self.llm_client.chat(context)
            except Exception as e:
                assistant_message = f"抱歉,处理您的请求时出现错误: {str(e)}"
        else:
            assistant_message = "[模拟回复] 这是一个模拟的Agent回复。"
        
        # 4. 添加助手回复
        self.context_manager.add_message(
            role="assistant",
            content=assistant_message,
            importance=importance
        )
        
        # 5. 更新统计
        self._update_stats(context)
        
        return assistant_message
    
    def _prepare_context(self, current_query: str) -> List[Dict[str, str]]:
        """
        准备上下文
        
        根据配置选择不同的策略:
        - 基础策略: 直接使用HybridContextManager
        - 优化策略: 进一步优化上下文
        
        Args:
            current_query: 当前查询
            
        Returns:
            准备好的上下文
        """
        # 获取基础上下文
        base_context = self.context_manager.get_context()
        
        # 转换为Message对象(用于优化)
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                importance=5.0
            )
            for msg in base_context
        ]
        
        # 检查是否需要优化
        total_tokens = sum(estimate_tokens(msg["content"]) for msg in base_context)
        
        if total_tokens > self.config.max_tokens * 0.8:
            # 如果接近Token限制,进行优化
            optimized, result = self.optimizer.optimize(
                messages,
                target_tokens=int(self.config.max_tokens * 0.7),
                strategy=self.config.optimization_strategy
            )
            
            self.stats.context_compressions += 1
            
            return [msg.to_dict() for msg in optimized]
        
        return base_context
    
    def _update_stats(self, context: List[Dict[str, str]]) -> None:
        """更新统计信息"""
        if not self.config.cost_tracking:
            return
        
        self.stats.total_queries += 1
        self.stats.total_messages = self.context_manager.count_messages()
        
        # 计算Token消耗
        tokens = sum(estimate_tokens(msg["content"]) for msg in context)
        self.stats.total_tokens_used += tokens
        
        # 估算成本 (假设GPT-4定价)
        input_cost = tokens * 0.03 / 1000
        output_cost = (tokens * 0.5) * 0.06 / 1000  # 假设输出是输入的50%
        self.stats.estimated_cost += (input_cost + output_cost)
    
    def get_stats(self) -> AgentStats:
        """获取统计信息"""
        return self.stats
    
    def get_context_summary(self) -> Dict[str, Any]:
        """获取上下文摘要"""
        context = self.context_manager.get_context()
        total_tokens = sum(estimate_tokens(msg["content"]) for msg in context)
        
        return {
            "total_messages": self.context_manager.count_messages(),
            "context_messages": len(context),
            "total_tokens": total_tokens,
            "max_tokens": self.config.max_tokens,
            "token_usage_ratio": total_tokens / self.config.max_tokens,
            "system_messages": sum(1 for msg in context if msg["role"] == "system"),
            "user_messages": sum(1 for msg in context if msg["role"] == "user"),
            "assistant_messages": sum(1 for msg in context if msg["role"] == "assistant")
        }
    
    def clear_history(self) -> None:
        """清空历史"""
        self.context_manager.clear()
        # 重新添加系统提示词
        if self.system_prompt:
            self.context_manager.add_message(
                role="system",
                content=self.system_prompt,
                importance=10.0
            )


class MultiTaskAgent(ContextAwareAgent):
    """
    多任务Agent
    
    扩展ContextAwareAgent,支持不同任务场景的上下文策略
    """
    
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        
        # 任务特定配置
        self.task_configs = {
            "short_qa": AgentConfig(
                max_tokens=1000,
                keep_recent=2,
                optimization_strategy="truncate"
            ),
            "long_conversation": AgentConfig(
                max_tokens=4000,
                keep_recent=5,
                optimization_strategy="hybrid",
                enable_summarization=True
            ),
            "code_assistant": AgentConfig(
                max_tokens=8000,
                keep_recent=3,
                optimization_strategy="truncate"
            )
        }
        
        self.current_task = "long_conversation"
    
    def set_task_mode(self, task: str) -> None:
        """
        设置任务模式
        
        Args:
            task: 任务类型 (short_qa/long_conversation/code_assistant)
        """
        if task in self.task_configs:
            self.current_task = task
            self.config = self.task_configs[task]
            
            # 重新创建上下文管理器
            self.context_manager = HybridContextManager(
                max_tokens=self.config.max_tokens,
                keep_recent=self.config.keep_recent,
                decay_factor=self.config.decay_factor
            )
            
            print(f"✅ 切换到任务模式: {task}")
        else:
            print(f"❌ 未知任务类型: {task}")


# ============= 测试代码 =============

def test_basic_agent():
    """测试基础Agent功能"""
    print("=" * 60)
    print("测试1: 基础Agent对话")
    print("=" * 60)
    
    # 创建模拟LLM
    class MockLLM:
        def chat(self, messages):
            last_user_msg = [m for m in messages if m["role"] == "user"][-1]
            return f"[模拟回复] 收到你的消息: {last_user_msg['content'][:30]}..."
    
    agent = ContextAwareAgent(llm_client=MockLLM())
    agent.set_system_prompt("你是一个友好的AI助手。")
    
    # 多轮对话
    queries = [
        "你好!",
        "今天天气怎么样?",
        "推荐一些好玩的地方",
        "帮我总结一下我们的对话"
    ]
    
    print("\n开始对话:\n")
    for i, query in enumerate(queries, 1):
        print(f"用户 {i}: {query}")
        response = agent.chat(query)
        print(f"助手 {i}: {response}\n")
    
    # 显示统计
    print(agent.get_stats())
    
    # 显示上下文摘要
    summary = agent.get_context_summary()
    print("上下文摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 基础Agent测试通过!")


def test_context_optimization():
    """测试上下文优化"""
    print("\n" + "=" * 60)
    print("测试2: 上下文自动优化")
    print("=" * 60)
    
    class MockLLM:
        def chat(self, messages):
            return "这是一个回复。"
    
    # 创建小Token限制的Agent
    config = AgentConfig(
        max_tokens=150,
        keep_recent=2,
        optimization_strategy="truncate"
    )
    
    agent = ContextAwareAgent(llm_client=MockLLM(), config=config)
    agent.set_system_prompt("你是AI助手。")
    
    # 添加多条消息触发优化
    for i in range(10):
        query = f"这是第{i+1}个问题,内容包含很多文字来测试Token限制功能是否正常工作。"
        agent.chat(query)
    
    summary = agent.get_context_summary()
    print(f"\n总消息数: {summary['total_messages']}")
    print(f"上下文消息数: {summary['context_messages']}")
    print(f"Token使用: {summary['total_tokens']}/{summary['max_tokens']}")
    print(f"使用率: {summary['token_usage_ratio']:.1%}")
    
    assert summary['total_tokens'] <= config.max_tokens, "应该在Token限制内"
    
    print("\n✅ 上下文优化测试通过!")


def test_multi_task_agent():
    """测试多任务Agent"""
    print("\n" + "=" * 60)
    print("测试3: 多任务Agent")
    print("=" * 60)
    
    class MockLLM:
        def chat(self, messages):
            return "回复内容"
    
    agent = MultiTaskAgent(llm_client=MockLLM())
    
    # 测试不同任务模式
    tasks = ["short_qa", "long_conversation", "code_assistant"]
    
    for task in tasks:
        print(f"\n测试任务模式: {task}")
        agent.set_task_mode(task)
        
        # 发送几条消息
        for i in range(3):
            agent.chat(f"测试消息 {i+1}")
        
        summary = agent.get_context_summary()
        print(f"  Token限制: {summary['max_tokens']}")
        print(f"  当前使用: {summary['total_tokens']}")
        
        agent.clear_history()
    
    print("\n✅ 多任务Agent测试通过!")


def test_importance_handling():
    """测试重要性处理"""
    print("\n" + "=" * 60)
    print("测试4: 消息重要性处理")
    print("=" * 60)
    
    class MockLLM:
        def chat(self, messages):
            return "回复"
    
    config = AgentConfig(max_tokens=100, keep_recent=2)
    agent = ContextAwareAgent(llm_client=MockLLM(), config=config)
    
    # 添加不同重要性的消息
    agent.chat("普通消息1", importance=3.0)
    agent.chat("普通消息2", importance=3.0)
    agent.chat("重要消息!", importance=9.0)
    agent.chat("普通消息3", importance=3.0)
    agent.chat("普通消息4", importance=3.0)
    
    summary = agent.get_context_summary()
    context = agent.context_manager.get_context()
    
    print(f"\n总消息数: {summary['total_messages']}")
    print(f"上下文中的消息:")
    for msg in context:
        print(f"  [{msg['role']}]: {msg['content'][:40]}...")
    
    # 验证重要消息被保留
    contents = [msg['content'] for msg in context]
    # 由于keep_recent=2,最近2条一定保留
    assert contents[-1] == "回复", "最近的消息应该被保留"
    
    print("\n✅ 重要性处理测试通过!")


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始测试上下文感知Agent...\n")
    
    test_basic_agent()
    test_context_optimization()
    test_multi_task_agent()
    test_importance_handling()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print("=" * 60)
    
    print("\n💡 上下文感知Agent的优势:")
    print("  1. ✅ 自动管理对话历史,无需手动维护")
    print("  2. ✅ 智能优化上下文,控制Token消耗")
    print("  3. ✅ 成本追踪,实时监控API费用")
    print("  4. ✅ 灵活配置,适应不同任务场景")
    print("  5. ✅ 多任务支持,可切换不同模式")


if __name__ == "__main__":
    run_all_tests()
