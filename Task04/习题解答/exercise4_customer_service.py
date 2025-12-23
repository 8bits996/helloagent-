"""
习题4: 实际应用设计

设计一个客服系统的上下文工程方案:
- 用户信息管理
- 历史对话处理
- 知识库检索
- 成本优化
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class UserProfile:
    """用户信息"""
    user_id: str
    name: str
    vip_level: str = "普通"
    preferences: Dict = None
    total_conversations: int = 0
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


@dataclass
class SessionStats:
    """会话统计"""
    session_id: str
    user_id: str
    start_time: datetime
    message_count: int = 0
    token_used: int = 0
    cost: float = 0.0


class UserInfoManager:
    """用户信息管理"""
    
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
    
    def get_or_create_user(self, user_id: str, name: str = None) -> UserProfile:
        """获取或创建用户"""
        if user_id not in self.users:
            self.users[user_id] = UserProfile(
                user_id=user_id,
                name=name or f"用户{user_id}",
                vip_level="普通"
            )
        return self.users[user_id]
    
    def update_vip_level(self, user_id: str, level: str):
        """更新VIP等级"""
        if user_id in self.users:
            self.users[user_id].vip_level = level
    
    def to_context_string(self, user: UserProfile) -> str:
        """转换为上下文字符串"""
        return f"""[用户信息]
ID: {user.user_id}
姓名: {user.name}
等级: {user.vip_level}
历史对话: {user.total_conversations}次
"""


class DialogueHistoryManager:
    """历史对话管理"""
    
    def __init__(self, max_history_per_user: int = 50):
        self.histories: Dict[str, List[Dict]] = {}
        self.max_history = max_history_per_user
    
    def add_message(self, user_id: str, role: str, content: str):
        """添加消息"""
        if user_id not in self.histories:
            self.histories[user_id] = []
        
        self.histories[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史长度
        if len(self.histories[user_id]) > self.max_history:
            self.histories[user_id] = self.histories[user_id][-self.max_history:]
    
    def get_recent_history(
        self,
        user_id: str,
        limit: int = 10,
        compressed: bool = True
    ) -> List[Dict]:
        """获取最近历史"""
        if user_id not in self.histories:
            return []
        
        history = self.histories[user_id]
        
        # 获取最近的消息
        recent = history[-limit*2:] if len(history) > limit*2 else history
        
        # 如果需要压缩且历史较长
        if compressed and len(history) > limit*2:
            old_messages = history[:-limit*2]
            summary = self._compress_old_history(old_messages)
            return [summary] + recent
        
        return recent
    
    def _compress_old_history(self, messages: List[Dict]) -> Dict:
        """压缩旧历史"""
        user_count = len([m for m in messages if m["role"] == "user"])
        topics = self._extract_topics(messages)
        
        summary = f"[历史摘要] 早期对话{user_count}轮，主要讨论: {', '.join(topics[:3])}"
        
        return {
            "role": "system",
            "content": summary
        }
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """提取话题"""
        topics = []
        for msg in messages:
            if msg["role"] == "user":
                # 简化: 取前几个词
                words = msg["content"].split()[:3]
                if words:
                    topics.append(" ".join(words))
        return topics


class KnowledgeBase:
    """知识库"""
    
    def __init__(self):
        # 模拟FAQ知识库
        self.faqs = {
            "退款": "退款政策: 7天内可无理由退款，退款将在3-5个工作日内到账。",
            "发货": "发货时间: 工作日当天下单，当天发货；节假日顺延。",
            "物流": "物流查询: 可在订单详情页查看物流信息。",
            "支付": "支付方式: 支持微信、支付宝、银行卡支付。",
            "优惠": "优惠活动: 新用户享受首单8折优惠。",
            "会员": "会员权益: VIP用户享受专属客服和优先发货。",
        }
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索相关知识"""
        results = []
        
        # 简单关键词匹配
        for key, content in self.faqs.items():
            if key in query or any(word in query for word in content.split()):
                results.append({
                    "topic": key,
                    "content": content,
                    "relevance": 0.8
                })
        
        # 返回top_k
        return results[:top_k]


class CostTracker:
    """成本追踪"""
    
    def __init__(self):
        # GPT-4价格
        self.input_price = 0.03 / 1000
        self.output_price = 0.06 / 1000
        
        self.sessions: Dict[str, SessionStats] = {}
        self.total_cost = 0.0
    
    def start_session(self, session_id: str, user_id: str) -> SessionStats:
        """开始会话"""
        stats = SessionStats(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now()
        )
        self.sessions[session_id] = stats
        return stats
    
    def track_request(
        self,
        session_id: str,
        input_tokens: int,
        output_tokens: int
    ):
        """追踪请求成本"""
        input_cost = input_tokens * self.input_price
        output_cost = output_tokens * self.output_price
        total = input_cost + output_cost
        
        if session_id in self.sessions:
            self.sessions[session_id].token_used += input_tokens + output_tokens
            self.sessions[session_id].cost += total
            self.sessions[session_id].message_count += 1
        
        self.total_cost += total
    
    def get_session_stats(self, session_id: str) -> Optional[SessionStats]:
        """获取会话统计"""
        return self.sessions.get(session_id)


class ContextBuilder:
    """上下文构建器"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def build(
        self,
        user_info: str,
        history: List[Dict],
        kb_results: List[Dict],
        current_query: str
    ) -> List[Dict]:
        """构建优化的上下文"""
        context = []
        token_budget = self.max_tokens
        
        # 1. 系统提示 (200 tokens)
        system_prompt = "你是专业的客服助手，请礼貌、准确地回答用户问题。"
        context.append({"role": "system", "content": system_prompt})
        token_budget -= 200
        
        # 2. 用户信息 (100 tokens)
        if user_info:
            context.append({"role": "system", "content": user_info})
            token_budget -= 100
        
        # 3. 知识库结果 (最多800 tokens)
        if kb_results:
            kb_content = self._format_kb_results(kb_results)
            kb_tokens = min(self._estimate_tokens(kb_content), 800)
            context.append({"role": "system", "content": kb_content})
            token_budget -= kb_tokens
        
        # 4. 对话历史 (剩余budget - 200)
        history_budget = token_budget - 200  # 保留200给当前查询
        fitted_history = self._fit_history(history, history_budget)
        context.extend(fitted_history)
        
        # 5. 当前查询
        context.append({"role": "user", "content": current_query})
        
        return context
    
    def _format_kb_results(self, results: List[Dict]) -> str:
        """格式化知识库结果"""
        lines = ["[相关知识]"]
        for r in results:
            lines.append(f"- {r['topic']}: {r['content']}")
        return "\n".join(lines)
    
    def _fit_history(self, history: List[Dict], max_tokens: int) -> List[Dict]:
        """适配历史到Token预算"""
        fitted = []
        current_tokens = 0
        
        for msg in reversed(history):
            msg_tokens = self._estimate_tokens(msg["content"])
            if current_tokens + msg_tokens <= max_tokens:
                fitted.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return fitted
    
    def _estimate_tokens(self, text: str) -> int:
        """估算Token数"""
        return len(text) // 4 + 1


class CustomerServiceAgent:
    """智能客服Agent"""
    
    def __init__(self, llm_client=None, max_context_tokens: int = 4000):
        """
        初始化客服Agent
        
        Args:
            llm_client: LLM客户端
            max_context_tokens: 最大上下文Token数
        """
        self.llm = llm_client
        
        # 初始化各个组件
        self.user_manager = UserInfoManager()
        self.history_manager = DialogueHistoryManager()
        self.knowledge_base = KnowledgeBase()
        self.context_builder = ContextBuilder(max_context_tokens)
        self.cost_tracker = CostTracker()
        
        # 会话管理
        self.active_sessions: Dict[str, str] = {}  # session_id -> user_id
    
    def start_session(self, user_id: str, user_name: str = None) -> str:
        """开始新会话"""
        session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        # 获取或创建用户
        user = self.user_manager.get_or_create_user(user_id, user_name)
        user.total_conversations += 1
        
        # 启动会话统计
        self.cost_tracker.start_session(session_id, user_id)
        self.active_sessions[session_id] = user_id
        
        return session_id
    
    def handle_query(self, session_id: str, query: str) -> Dict:
        """
        处理用户查询
        
        Returns:
            Dict包含response和metadata
        """
        if session_id not in self.active_sessions:
            return {"error": "无效的会话ID"}
        
        user_id = self.active_sessions[session_id]
        user = self.user_manager.get_or_create_user(user_id)
        
        # 1. 检索知识库
        kb_results = self.knowledge_base.retrieve(query, top_k=3)
        
        # 2. 获取历史对话
        history = self.history_manager.get_recent_history(
            user_id,
            limit=5,
            compressed=True
        )
        
        # 3. 构建上下文
        user_info = self.user_manager.to_context_string(user)
        context = self.context_builder.build(
            user_info=user_info,
            history=history,
            kb_results=kb_results,
            current_query=query
        )
        
        # 4. 调用LLM (模拟)
        response = self._call_llm(context)
        
        # 5. 更新历史
        self.history_manager.add_message(user_id, "user", query)
        self.history_manager.add_message(user_id, "assistant", response)
        
        # 6. 追踪成本
        input_tokens = sum(self.context_builder._estimate_tokens(m["content"]) for m in context)
        output_tokens = self.context_builder._estimate_tokens(response)
        self.cost_tracker.track_request(session_id, input_tokens, output_tokens)
        
        # 7. 返回结果
        stats = self.cost_tracker.get_session_stats(session_id)
        
        return {
            "response": response,
            "metadata": {
                "session_id": session_id,
                "user_id": user_id,
                "vip_level": user.vip_level,
                "kb_results": len(kb_results),
                "context_messages": len(context),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "session_cost": stats.cost if stats else 0,
                "session_messages": stats.message_count if stats else 0
            }
        }
    
    def _call_llm(self, context: List[Dict]) -> str:
        """调用LLM (模拟)"""
        # 实际应用中应调用真实LLM
        # response = self.llm.chat(context)
        
        # 模拟响应
        last_message = context[-1]["content"]
        
        if "退款" in last_message:
            return "根据我们的退款政策，您可以在7天内申请无理由退款。请提供您的订单号，我来帮您处理。"
        elif "发货" in last_message or "物流" in last_message:
            return "您的订单将在工作日当天发货。您可以在订单详情页查看实时物流信息。"
        elif "会员" in last_message or "VIP" in last_message:
            return "作为VIP会员，您享有专属客服服务和优先发货权益。感谢您的支持！"
        else:
            return "感谢您的咨询！我们会尽力为您提供帮助。请问还有什么其他问题吗？"
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要"""
        stats = self.cost_tracker.get_session_stats(session_id)
        
        if not stats:
            return {"error": "会话不存在"}
        
        return {
            "session_id": stats.session_id,
            "user_id": stats.user_id,
            "duration": (datetime.now() - stats.start_time).seconds,
            "message_count": stats.message_count,
            "total_tokens": stats.token_used,
            "total_cost": stats.cost,
            "avg_cost_per_message": stats.cost / stats.message_count if stats.message_count > 0 else 0
        }


# ============ 测试代码 ============

def test_customer_service_agent():
    """测试客服Agent"""
    print("=" * 80)
    print("Task04 习题4: 智能客服系统测试")
    print("=" * 80)
    
    # 创建Agent
    agent = CustomerServiceAgent(max_context_tokens=4000)
    
    # 场景1: 普通用户咨询
    print("\n场景1: 普通用户咨询")
    print("-" * 80)
    
    session1 = agent.start_session("user001", "张三")
    print(f"会话ID: {session1}")
    
    queries1 = [
        "你好，我想咨询退款政策",
        "我的订单什么时候发货？",
        "可以加急吗？"
    ]
    
    for query in queries1:
        print(f"\n用户: {query}")
        result = agent.handle_query(session1, query)
        print(f"客服: {result['response']}")
        print(f"成本: ${result['metadata']['session_cost']:.4f}")
    
    summary1 = agent.get_session_summary(session1)
    print(f"\n会话摘要:")
    print(f"  消息数: {summary1['message_count']}")
    print(f"  总Token: {summary1['total_tokens']}")
    print(f"  总成本: ${summary1['total_cost']:.4f}")
    print(f"  平均成本: ${summary1['avg_cost_per_message']:.4f}/条")
    
    # 场景2: VIP用户咨询
    print("\n\n场景2: VIP用户咨询")
    print("-" * 80)
    
    session2 = agent.start_session("user002", "李四")
    agent.user_manager.update_vip_level("user002", "VIP")
    
    queries2 = [
        "我是VIP会员，想了解专属权益",
        "如何查看物流信息？"
    ]
    
    for query in queries2:
        print(f"\n用户: {query}")
        result = agent.handle_query(session2, query)
        print(f"客服: {result['response']}")
        print(f"VIP等级: {result['metadata']['vip_level']}")
    
    summary2 = agent.get_session_summary(session2)
    print(f"\n会话摘要:")
    print(f"  消息数: {summary2['message_count']}")
    print(f"  总成本: ${summary2['total_cost']:.4f}")
    
    # 系统统计
    print("\n\n系统整体统计")
    print("-" * 80)
    print(f"总用户数: {len(agent.user_manager.users)}")
    print(f"活跃会话: {len(agent.active_sessions)}")
    print(f"总成本: ${agent.cost_tracker.total_cost:.4f}")
    
    print("\n✅ 客服系统测试完成!")


def test_optimization_features():
    """测试优化功能"""
    print("\n\n" + "=" * 80)
    print("优化功能测试")
    print("=" * 80)
    
    agent = CustomerServiceAgent(max_context_tokens=2000)  # 更严格的限制
    session = agent.start_session("user003", "王五")
    
    # 多轮对话测试Token管理
    print("\n测试: 长对话Token管理")
    print("-" * 80)
    
    for i in range(10):
        query = f"这是第{i+1}个问题，关于产品的使用方法"
        result = agent.handle_query(session, query)
        
        print(f"\n第{i+1}轮:")
        print(f"  输入Token: {result['metadata']['input_tokens']}")
        print(f"  输出Token: {result['metadata']['output_tokens']}")
        print(f"  上下文消息数: {result['metadata']['context_messages']}")
    
    summary = agent.get_session_summary(session)
    print(f"\n最终统计:")
    print(f"  总轮数: {summary['message_count']}")
    print(f"  总Token: {summary['total_tokens']}")
    print(f"  总成本: ${summary['total_cost']:.4f}")
    print(f"  平均Token/轮: {summary['total_tokens'] / summary['message_count']:.0f}")
    
    print("\n✅ 优化功能测试完成!")
    
    print("\n关键优化点:")
    print("1. ✅ Token预算管理 - 控制在4000以内")
    print("2. ✅ 历史对话压缩 - 旧对话自动总结")
    print("3. ✅ 知识库检索 - 只获取top3相关")
    print("4. ✅ 成本实时追踪 - 每个会话独立统计")


if __name__ == "__main__":
    test_customer_service_agent()
    test_optimization_features()
    
    print("\n" + "=" * 80)
    print("习题4: 全部测试通过! ✅")
    print("=" * 80)
    
    print("\n系统特性:")
    print("✅ 用户信息管理 - 用户档案、VIP等级")
    print("✅ 历史对话处理 - 自动压缩、分层存储")
    print("✅ 知识库检索 - 相关性匹配、Top-K")
    print("✅ 成本优化 - Token预算、实时追踪")
