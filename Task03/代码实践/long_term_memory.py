"""
长期记忆系统实现
Long-term Memory for Agent

功能:
1. 向量数据库集成 (ChromaDB)
2. 语义检索
3. 文档存储与召回
4. 记忆持久化

依赖:
pip install chromadb sentence-transformers
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import uuid
import os


class LongTermMemory:
    """
    长期记忆系统
    使用ChromaDB实现向量存储和语义检索
    """
    
    def __init__(
        self, 
        collection_name: str = "agent_memory",
        persist_directory: Optional[str] = None,
        embedding_function: Optional[any] = None
    ):
        """
        初始化长期记忆
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录（None则使用内存模式）
            embedding_function: 自定义Embedding函数
        """
        self.collection_name = collection_name
        
        # 创建ChromaDB客户端
        if persist_directory:
            # 持久化模式
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            # 内存模式（仅用于测试）
            self.client = chromadb.Client()
        
        # 创建或获取集合
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            print(f"[LongTermMemory] 加载已存在的集合: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            print(f"[LongTermMemory] 创建新集合: {collection_name}")
    
    def store(
        self, 
        content: str, 
        metadata: Optional[Dict] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        存储记忆到长期存储
        
        Args:
            content: 记忆内容
            metadata: 元数据（标签、时间戳等）
            memory_id: 记忆ID（不提供则自动生成）
            
        Returns:
            记忆ID
        """
        if not memory_id:
            memory_id = str(uuid.uuid4())
        
        # 添加默认元数据
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = metadata.get("timestamp", datetime.now().isoformat())
        metadata["access_count"] = metadata.get("access_count", 0)
        
        # 存储到向量数据库
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        print(f"[LongTermMemory] 存储记忆: {memory_id[:8]}... ({len(content)} chars)")
        return memory_id
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        语义检索记忆
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            filter_metadata: 元数据过滤条件
            
        Returns:
            检索结果列表
        """
        # 执行检索
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_metadata
        )
        
        # 格式化结果
        memories = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                memory = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                }
                memories.append(memory)
        
        print(f"[LongTermMemory] 检索到 {len(memories)} 条记忆")
        return memories
    
    def get_by_id(self, memory_id: str) -> Optional[Dict]:
        """
        根据ID获取记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆内容，不存在则返回None
        """
        try:
            results = self.collection.get(
                ids=[memory_id]
            )
            
            if results['ids']:
                return {
                    "id": results['ids'][0],
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0] if results['metadatas'] else {}
                }
        except Exception as e:
            print(f"[LongTermMemory] 获取记忆失败: {e}")
        
        return None
    
    def update(self, memory_id: str, content: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        更新记忆
        
        Args:
            memory_id: 记忆ID
            content: 新内容（None则不更新）
            metadata: 新元数据（None则不更新）
        """
        update_dict = {"ids": [memory_id]}
        
        if content is not None:
            update_dict["documents"] = [content]
        
        if metadata is not None:
            update_dict["metadatas"] = [metadata]
        
        self.collection.update(**update_dict)
        print(f"[LongTermMemory] 更新记忆: {memory_id[:8]}...")
    
    def delete(self, memory_ids: List[str]):
        """
        删除记忆
        
        Args:
            memory_ids: 记忆ID列表
        """
        self.collection.delete(ids=memory_ids)
        print(f"[LongTermMemory] 删除 {len(memory_ids)} 条记忆")
    
    def clear(self):
        """清空所有记忆"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[LongTermMemory] 清空集合: {self.collection_name}")
        except Exception as e:
            print(f"[LongTermMemory] 清空失败: {e}")
    
    def count(self) -> int:
        """
        获取记忆总数
        
        Returns:
            记忆数量
        """
        return self.collection.count()
    
    def get_all_memories(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取所有记忆
        
        Args:
            limit: 限制数量
            
        Returns:
            记忆列表
        """
        count = self.count()
        if limit is None or limit > count:
            limit = count
        
        if limit == 0:
            return []
        
        results = self.collection.get(
            limit=limit
        )
        
        memories = []
        for i in range(len(results['ids'])):
            memory = {
                "id": results['ids'][i],
                "content": results['documents'][i],
                "metadata": results['metadatas'][i] if results['metadatas'] else {}
            }
            memories.append(memory)
        
        return memories
    
    def __len__(self):
        """返回记忆数量"""
        return self.count()
    
    def __str__(self):
        """字符串表示"""
        return f"LongTermMemory(collection={self.collection_name}, count={self.count()})"


class MemoryWithImportance(LongTermMemory):
    """
    带重要性管理的长期记忆
    支持记忆重要性评分和自动清理
    """
    
    def store_with_importance(
        self,
        content: str,
        importance: float = 5.0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        存储记忆并设置重要性
        
        Args:
            content: 记忆内容
            importance: 重要性分数 (0.0-10.0)
            metadata: 额外元数据
            
        Returns:
            记忆ID
        """
        if metadata is None:
            metadata = {}
        
        metadata["importance"] = importance
        
        return self.store(content, metadata)
    
    def prune_by_importance(self, min_importance: float = 3.0):
        """
        删除低重要性记忆
        
        Args:
            min_importance: 最低重要性阈值
        """
        all_memories = self.get_all_memories()
        
        to_delete = []
        for memory in all_memories:
            importance = memory['metadata'].get('importance', 5.0)
            if importance < min_importance:
                to_delete.append(memory['id'])
        
        if to_delete:
            self.delete(to_delete)
            print(f"[MemoryWithImportance] 清理了 {len(to_delete)} 条低重要性记忆")
    
    def get_most_important(self, top_k: int = 10) -> List[Dict]:
        """
        获取最重要的记忆
        
        Args:
            top_k: 返回数量
            
        Returns:
            重要记忆列表
        """
        all_memories = self.get_all_memories()
        
        # 按重要性排序
        all_memories.sort(
            key=lambda x: x['metadata'].get('importance', 0),
            reverse=True
        )
        
        return all_memories[:top_k]


# 示例使用
if __name__ == "__main__":
    print("=" * 60)
    print("测试1: 基础长期记忆")
    print("=" * 60)
    
    # 创建长期记忆（内存模式，仅测试用）
    memory = LongTermMemory(collection_name="test_memory")
    
    print(f"\n{memory}")
    
    # 存储知识
    print("\n存储知识...")
    memory.store(
        content="Agent的记忆系统分为短期记忆和长期记忆两种",
        metadata={"topic": "记忆系统", "category": "理论"}
    )
    
    memory.store(
        content="RAG是Retrieval-Augmented Generation的缩写，即检索增强生成",
        metadata={"topic": "RAG", "category": "技术"}
    )
    
    memory.store(
        content="ChromaDB是一个轻量级的向量数据库，适合开发和测试",
        metadata={"topic": "ChromaDB", "category": "工具"}
    )
    
    memory.store(
        content="短期记忆用于维护对话上下文，长期记忆用于持久化知识",
        metadata={"topic": "记忆系统", "category": "理论"}
    )
    
    memory.store(
        content="Embedding技术将文本转换为向量，用于语义检索",
        metadata={"topic": "Embedding", "category": "技术"}
    )
    
    print(f"\n当前记忆数量: {len(memory)}")
    
    # 语义检索
    print("\n" + "=" * 60)
    print("测试2: 语义检索")
    print("=" * 60)
    
    query = "什么是记忆系统？"
    print(f"\n查询: {query}")
    results = memory.search(query, top_k=3)
    
    print(f"\n检索结果:")
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  内容: {result['content']}")
        print(f"  主题: {result['metadata'].get('topic', 'N/A')}")
        print(f"  相似度距离: {result['distance']:.4f}")
    
    # 按元数据过滤
    print("\n" + "=" * 60)
    print("测试3: 元数据过滤")
    print("=" * 60)
    
    query2 = "技术"
    print(f"\n查询技术相关的内容:")
    results2 = memory.search(
        query2, 
        top_k=5,
        filter_metadata={"category": "技术"}
    )
    
    print(f"\n找到 {len(results2)} 条技术相关记忆:")
    for result in results2:
        print(f"  - {result['content'][:50]}...")
    
    # 重要性记忆
    print("\n" + "=" * 60)
    print("测试4: 重要性记忆管理")
    print("=" * 60)
    
    imp_memory = MemoryWithImportance(collection_name="important_memory")
    
    imp_memory.store_with_importance(
        content="用户的密码是secret123",
        importance=10.0,
        metadata={"category": "敏感信息"}
    )
    
    imp_memory.store_with_importance(
        content="今天天气不错",
        importance=2.0,
        metadata={"category": "闲聊"}
    )
    
    imp_memory.store_with_importance(
        content="用户偏好使用Python编程",
        importance=8.0,
        metadata={"category": "用户偏好"}
    )
    
    imp_memory.store_with_importance(
        content="随便说说",
        importance=1.0,
        metadata={"category": "闲聊"}
    )
    
    print(f"\n当前记忆数量: {len(imp_memory)}")
    
    print("\n最重要的3条记忆:")
    important = imp_memory.get_most_important(top_k=3)
    for mem in important:
        print(f"  [{mem['metadata']['importance']}] {mem['content']}")
    
    print("\n清理低重要性记忆（importance < 3.0）...")
    imp_memory.prune_by_importance(min_importance=3.0)
    
    print(f"\n清理后记忆数量: {len(imp_memory)}")
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    
    # 清理测试数据
    memory.clear()
    imp_memory.clear()
