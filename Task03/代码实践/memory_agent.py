"""
MemoryAgent - 带记忆的智能Agent
整合短期记忆、长期记忆和RAG系统

功能:
1. 短期记忆：维护对话上下文
2. 长期记忆：持久化重要信息
3. RAG检索：增强知识问答
4. 智能记忆管理

依赖:
pip install chromadb
"""

from typing import List, Dict, Optional, Callable
from short_term_memory import ShortTermMemory, TokenLimitedMemory
from long_term_memory import LongTermMemory
from rag_system import RAGSystem
from datetime import datetime


class MemoryAgent:
    """
    带记忆的Agent
    集成短期记忆和长期记忆
    """
    
    def __init__(
        self,
        agent_name: str = "MemoryAgent",
        short_term_max_messages: int = 10,
        long_term_collection: str = "agent_long_term_memory",
        persist_directory: Optional[str] = None,
        llm_function: Optional[Callable] = None
    ):
        """
        初始化MemoryAgent
        
        Args:
            agent_name: Agent名称
            short_term_max_messages: 短期记忆最大消息数
            long_term_collection: 长期记忆集合名
            persist_directory: 持久化目录
            llm_function: LLM调用函数
        """
        self.agent_name = agent_name
        
        # 初始化短期记忆
        self.short_term = ShortTermMemory(max_messages=short_term_max_messages)
        
        # 初始化长期记忆
        self.long_term = LongTermMemory(
            collection_name=long_term_collection,
            persist_directory=persist_directory
        )
        
        # LLM函数
        self.llm = llm_function
        
        print(f"[{self.agent_name}] 初始化完成")
        print(f"  短期记忆容量: {short_term_max_messages}")
        print(f"  长期记忆数量: {len(self.long_term)}")
    
    def run(
        self,
        user_input: str,
        use_long_term: bool = True,
        store_to_long_term: bool = False,
        retrieve_top_k: int = 3
    ) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            use_long_term: 是否使用长期记忆检索
            store_to_long_term: 是否存储到长期记忆
            retrieve_top_k: 检索数量
            
        Returns:
            Agent回复
        """
        print(f"\n[{self.agent_name}] 收到用户输入: {user_input}")
        
        # 1. 从长期记忆检索相关信息
        relevant_context = ""
        if use_long_term and len(self.long_term) > 0:
            print(f"[{self.agent_name}] 从长期记忆检索相关信息...")
            memories = self.long_term.search(user_input, top_k=retrieve_top_k)
            
            if memories:
                context_parts = [f"- {m['content']}" for m in memories]
                relevant_context = "\n".join(context_parts)
                print(f"[{self.agent_name}] 检索到 {len(memories)} 条相关记忆")
        
        # 2. 获取短期记忆（对话历史）
        conversation_history = self.short_term.get_conversation_history()
        
        # 3. 构建Prompt
        prompt = self._build_prompt(user_input, relevant_context, conversation_history)
        
        # 4. 生成回复
        if self.llm:
            response = self.llm(prompt)
        else:
            # 模拟回复（用于测试）
            response = f"[模拟回复] 我理解了您的问题：{user_input}"
            if relevant_context:
                response += f"\n\n相关信息：\n{relevant_context}"
        
        # 5. 更新短期记忆
        self.short_term.add_message("user", user_input)
        self.short_term.add_message("assistant", response)
        
        # 6. 存储重要信息到长期记忆
        if store_to_long_term:
            self._store_important_info(user_input, response)
        
        return response
    
    def _build_prompt(
        self,
        user_input: str,
        relevant_context: str,
        conversation_history: str
    ) -> str:
        """
        构建完整的Prompt
        
        Args:
            user_input: 用户输入
            relevant_context: 相关上下文
            conversation_history: 对话历史
            
        Returns:
            完整Prompt
        """
        prompt_parts = []
        
        # 系统提示
        prompt_parts.append(f"你是{self.agent_name}，一个具有记忆能力的智能助手。")
        
        # 相关上下文
        if relevant_context:
            prompt_parts.append(f"\n相关知识：\n{relevant_context}")
        
        # 对话历史
        if conversation_history:
            prompt_parts.append(f"\n对话历史：\n{conversation_history}")
        
        # 当前问题
        prompt_parts.append(f"\n当前问题：{user_input}")
        prompt_parts.append("\n请回答：")
        
        return "\n".join(prompt_parts)
    
    def _store_important_info(self, user_input: str, response: str):
        """
        存储重要信息到长期记忆
        
        Args:
            user_input: 用户输入
            response: Agent回复
        """
        # 简单策略：用户输入较长或包含关键词时存储
        keywords = ["记住", "重要", "密码", "偏好", "名字", "喜欢"]
        
        should_store = len(user_input) > 20 or any(kw in user_input for kw in keywords)
        
        if should_store:
            self.long_term.store(
                content=f"用户: {user_input}\n回复: {response}",
                metadata={
                    "type": "conversation",
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"[{self.agent_name}] 信息已存储到长期记忆")
    
    def store_knowledge(self, knowledge: str, metadata: Optional[Dict] = None):
        """
        手动存储知识到长期记忆
        
        Args:
            knowledge: 知识内容
            metadata: 元数据
        """
        self.long_term.store(knowledge, metadata)
        print(f"[{self.agent_name}] 知识已存储")
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term.clear()
        print(f"[{self.agent_name}] 短期记忆已清空")
    
    def clear_long_term(self):
        """清空长期记忆"""
        self.long_term.clear()
        print(f"[{self.agent_name}] 长期记忆已清空")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "agent_name": self.agent_name,
            "short_term_messages": len(self.short_term),
            "long_term_memories": len(self.long_term)
        }
    
    def __str__(self):
        """字符串表示"""
        stats = self.get_stats()
        return f"{stats['agent_name']}(短期: {stats['short_term_messages']}, 长期: {stats['long_term_memories']})"


class RAGAgent:
    """
    基于RAG的知识助手Agent
    专门用于知识库问答
    """
    
    def __init__(
        self,
        agent_name: str = "RAGAgent",
        collection_name: str = "rag_knowledge_base",
        persist_directory: Optional[str] = None,
        llm_function: Optional[Callable] = None
    ):
        """
        初始化RAGAgent
        
        Args:
            agent_name: Agent名称
            collection_name: 知识库名称
            persist_directory: 持久化目录
            llm_function: LLM调用函数
        """
        self.agent_name = agent_name
        
        # 初始化RAG系统
        self.rag = RAGSystem(
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        
        # 短期记忆（对话历史）
        self.conversation_memory = ShortTermMemory(max_messages=5)
        
        # LLM函数
        self.llm = llm_function
        
        print(f"[{self.agent_name}] 初始化完成")
    
    def load_documents(self, documents: List[Dict]):
        """
        加载文档到知识库
        
        Args:
            documents: 文档列表
        """
        print(f"\n[{self.agent_name}] 加载文档到知识库...")
        self.rag.ingest_documents(documents)
        print(f"[{self.agent_name}] 知识库加载完成，共 {len(self.rag.memory)} 个分块")
    
    def ask(self, question: str, top_k: int = 3) -> str:
        """
        向Agent提问
        
        Args:
            question: 用户问题
            top_k: 检索数量
            
        Returns:
            回答
        """
        print(f"\n[{self.agent_name}] 收到问题: {question}")
        
        # 1. 检索相关文档
        retrieved_docs = self.rag.retrieve(question, top_k=top_k)
        
        if not retrieved_docs:
            answer = "抱歉，我在知识库中没有找到相关信息。"
        else:
            # 2. 构建RAG Prompt
            context = self.rag.generate_context(question, top_k=top_k)
            
            # 3. 获取对话历史
            history = self.conversation_memory.get_conversation_history()
            
            # 4. 生成回答
            if self.llm:
                prompt = f"""基于以下参考资料回答问题。

对话历史:
{history}

参考资料:
{context}

问题: {question}

回答:"""
                answer = self.llm(prompt)
            else:
                # 模拟回答
                answer = f"基于知识库的回答：\n\n参考资料：\n{context}\n\n这些是我找到的相关信息。"
        
        # 5. 更新对话记忆
        self.conversation_memory.add_message("user", question)
        self.conversation_memory.add_message("assistant", answer)
        
        return answer
    
    def clear_knowledge_base(self):
        """清空知识库"""
        self.rag.clear_knowledge_base()
    
    def clear_conversation(self):
        """清空对话历史"""
        self.conversation_memory.clear()
    
    def __str__(self):
        """字符串表示"""
        return f"{self.agent_name}(知识块: {len(self.rag.memory)}, 对话: {len(self.conversation_memory)})"


# 示例使用
if __name__ == "__main__":
    print("=" * 70)
    print("MemoryAgent 测试")
    print("=" * 70)
    
    # 创建MemoryAgent
    agent = MemoryAgent(agent_name="小智", short_term_max_messages=5)
    
    # 先存储一些知识到长期记忆
    print("\n存储知识到长期记忆...")
    agent.store_knowledge(
        "用户名叫张三，喜欢编程，特别是Python语言",
        metadata={"type": "user_profile"}
    )
    agent.store_knowledge(
        "Agent的记忆系统分为短期记忆和长期记忆",
        metadata={"type": "knowledge"}
    )
    
    print(f"\n{agent}")
    
    # 测试对话
    print("\n" + "=" * 70)
    print("对话测试")
    print("=" * 70)
    
    conversations = [
        "你好，我是张三",
        "我喜欢什么？",  # 测试长期记忆检索
        "什么是记忆系统？",  # 测试知识检索
        "你还记得我的名字吗？"  # 测试短期+长期记忆
    ]
    
    for user_msg in conversations:
        print(f"\n👤 用户: {user_msg}")
        response = agent.run(
            user_msg,
            use_long_term=True,
            store_to_long_term=True
        )
        print(f"🤖 小智: {response}")
    
    print(f"\n\n对话结束后的状态: {agent}")
    
    # 测试RAGAgent
    print("\n\n" + "=" * 70)
    print("RAGAgent 测试")
    print("=" * 70)
    
    rag_agent = RAGAgent(agent_name="知识助手")
    
    # 加载知识库
    knowledge_docs = [
        {
            "id": "python_intro",
            "content": """
Python是一种高级编程语言，由Guido van Rossum于1991年创建。
Python的设计哲学强调代码的可读性和简洁性。它支持多种编程范式，
包括面向对象、命令式、函数式和过程式编程。Python广泛应用于
Web开发、数据科学、人工智能、自动化等领域。
            """,
            "metadata": {"topic": "Python", "category": "编程语言"}
        },
        {
            "id": "agent_memory",
            "content": """
Agent的记忆系统是实现智能对话的关键。短期记忆负责维护当前对话上下文，
而长期记忆则用于存储重要知识和历史信息。RAG技术通过检索增强生成，
能够让Agent基于知识库回答问题，而不仅仅依赖预训练知识。
            """,
            "metadata": {"topic": "Agent", "category": "AI"}
        }
    ]
    
    rag_agent.load_documents(knowledge_docs)
    
    print(f"\n{rag_agent}")
    
    # 测试问答
    questions = [
        "Python是什么时候创建的？",
        "Agent的记忆系统有哪些类型？",
        "Python可以用于哪些领域？"
    ]
    
    for q in questions:
        print(f"\n❓ 问题: {q}")
        answer = rag_agent.ask(q, top_k=2)
        print(f"💡 回答: {answer}")
    
    print("\n" + "=" * 70)
    print("所有测试完成！")
    print("=" * 70)
    
    # 清理
    agent.clear_long_term()
    rag_agent.clear_knowledge_base()
