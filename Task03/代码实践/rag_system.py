"""
RAG (Retrieval-Augmented Generation) 系统实现
完整的RAG流程: 文档分块 → 向量化 → 存储 → 检索 → 增强生成

功能:
1. 文档分块 (Chunking)
2. 向量化存储
3. 语义检索
4. 上下文增强生成

依赖:
pip install chromadb
"""

from typing import List, Dict, Optional, Callable
import re
from long_term_memory import LongTermMemory


class DocumentChunker:
    """
    文档分块器
    支持多种分块策略
    """
    
    @staticmethod
    def chunk_by_tokens(
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50
    ) -> List[str]:
        """
        按Token数量分块（简化版本，使用字符数估算）
        
        Args:
            text: 文本内容
            chunk_size: 块大小（字符数）
            overlap: 重叠大小（字符数）
            
        Returns:
            分块列表
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            
            # 避免在句子中间截断
            if end < text_length:
                # 寻找最近的句子结尾
                last_period = chunk.rfind('。')
                last_exclamation = chunk.rfind('！')
                last_question = chunk.rfind('？')
                
                split_point = max(last_period, last_exclamation, last_question)
                if split_point > chunk_size // 2:  # 确保不会切得太短
                    chunk = chunk[:split_point + 1]
                    end = start + split_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def chunk_by_sentences(
        text: str, 
        sentences_per_chunk: int = 5
    ) -> List[str]:
        """
        按句子分块
        
        Args:
            text: 文本内容
            sentences_per_chunk: 每块包含的句子数
            
        Returns:
            分块列表
        """
        # 分割句子（简单版本）
        sentences = re.split(r'[。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = '。'.join(sentences[i:i + sentences_per_chunk])
            if chunk:
                chunks.append(chunk + '。')
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(text: str) -> List[str]:
        """
        按段落分块
        
        Args:
            text: 文本内容
            
        Returns:
            分块列表
        """
        # 按双换行符分割段落
        paragraphs = text.split('\n\n')
        chunks = [p.strip() for p in paragraphs if p.strip()]
        return chunks
    
    @staticmethod
    def chunk_with_metadata(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict]:
        """
        分块并生成元数据
        
        Args:
            text: 文本内容
            chunk_size: 块大小
            overlap: 重叠大小
            
        Returns:
            包含元数据的分块列表
        """
        chunks = DocumentChunker.chunk_by_tokens(text, chunk_size, overlap)
        
        chunks_with_metadata = []
        for i, chunk in enumerate(chunks):
            chunks_with_metadata.append({
                "content": chunk,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk)
            })
        
        return chunks_with_metadata


class RAGSystem:
    """
    完整的RAG系统
    集成文档处理、向量存储和检索增强生成
    """
    
    def __init__(
        self,
        collection_name: str = "rag_knowledge_base",
        persist_directory: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化RAG系统
        
        Args:
            collection_name: 知识库名称
            persist_directory: 持久化目录
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
        """
        self.memory = LongTermMemory(
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        self.chunker = DocumentChunker()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        print(f"[RAG] 初始化完成: {collection_name}")
    
    def ingest_document(
        self,
        document: str,
        doc_id: str,
        metadata: Optional[Dict] = None,
        chunking_strategy: str = "tokens"
    ):
        """
        摄取文档到知识库
        
        Args:
            document: 文档内容
            doc_id: 文档ID
            metadata: 文档元数据
            chunking_strategy: 分块策略 (tokens/sentences/paragraphs)
        """
        print(f"\n[RAG] 开始摄取文档: {doc_id}")
        print(f"  文档长度: {len(document)} 字符")
        
        # 1. 文档分块
        if chunking_strategy == "tokens":
            chunks = self.chunker.chunk_by_tokens(
                document, self.chunk_size, self.chunk_overlap
            )
        elif chunking_strategy == "sentences":
            chunks = self.chunker.chunk_by_sentences(document)
        elif chunking_strategy == "paragraphs":
            chunks = self.chunker.chunk_by_paragraphs(document)
        else:
            raise ValueError(f"未知的分块策略: {chunking_strategy}")
        
        print(f"  分块数量: {len(chunks)}")
        
        # 2. 存储每个分块
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "doc_id": doc_id,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "chunking_strategy": chunking_strategy
            }
            
            # 合并用户提供的元数据
            if metadata:
                chunk_metadata.update(metadata)
            
            # 生成唯一的chunk ID
            chunk_full_id = f"{doc_id}_chunk_{i}"
            
            # 3. 向量化并存储
            self.memory.store(
                content=chunk,
                metadata=chunk_metadata,
                memory_id=chunk_full_id
            )
        
        print(f"[RAG] 文档摄取完成: {doc_id}")
    
    def ingest_documents(
        self,
        documents: List[Dict],
        chunking_strategy: str = "tokens"
    ):
        """
        批量摄取文档
        
        Args:
            documents: 文档列表，每个文档包含 {id, content, metadata}
            chunking_strategy: 分块策略
        """
        print(f"\n[RAG] 批量摄取 {len(documents)} 个文档...")
        
        for doc in documents:
            self.ingest_document(
                document=doc["content"],
                doc_id=doc["id"],
                metadata=doc.get("metadata"),
                chunking_strategy=chunking_strategy
            )
        
        print(f"\n[RAG] 批量摄取完成！总分块数: {len(self.memory)}")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回数量
            filter_metadata: 元数据过滤
            
        Returns:
            检索结果
        """
        print(f"\n[RAG] 检索查询: {query}")
        results = self.memory.search(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        return results
    
    def generate_context(
        self,
        query: str,
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> str:
        """
        生成增强上下文
        
        Args:
            query: 用户查询
            top_k: 检索数量
            filter_metadata: 元数据过滤
            
        Returns:
            格式化的上下文字符串
        """
        # 检索相关文档
        results = self.retrieve(query, top_k, filter_metadata)
        
        # 构建上下文
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            chunk_id = result['metadata'].get('chunk_id', 'unknown')
            
            context_parts.append(
                f"[参考资料 {i}] (来源: {doc_id}, 分块: {chunk_id})\n"
                f"{result['content']}\n"
            )
        
        context = "\n".join(context_parts)
        return context
    
    def build_rag_prompt(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        构建RAG增强的Prompt
        
        Args:
            query: 用户查询
            system_prompt: 系统提示词
            top_k: 检索数量
            
        Returns:
            完整的RAG Prompt
        """
        # 生成上下文
        context = self.generate_context(query, top_k)
        
        # 构建Prompt
        if system_prompt is None:
            system_prompt = "你是一个知识助手，请基于提供的参考资料回答用户的问题。"
        
        prompt = f"""{system_prompt}

## 参考资料

{context}

## 用户问题

{query}

## 回答

请基于上述参考资料回答用户问题。如果参考资料中没有相关信息，请明确告知用户。
"""
        
        return prompt
    
    def answer_question(
        self,
        query: str,
        llm_function: Optional[Callable] = None,
        top_k: int = 3
    ) -> Dict:
        """
        RAG问答（完整流程）
        
        Args:
            query: 用户问题
            llm_function: LLM调用函数 (如果为None，只返回上下文)
            top_k: 检索数量
            
        Returns:
            包含答案和上下文的字典
        """
        # 1. 检索
        retrieved_docs = self.retrieve(query, top_k)
        
        # 2. 构建Prompt
        rag_prompt = self.build_rag_prompt(query, top_k=top_k)
        
        # 3. 生成答案（如果提供了LLM）
        answer = None
        if llm_function:
            answer = llm_function(rag_prompt)
        
        return {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "prompt": rag_prompt,
            "answer": answer
        }
    
    def clear_knowledge_base(self):
        """清空知识库"""
        self.memory.clear()
        print("[RAG] 知识库已清空")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_chunks": len(self.memory),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "collection_name": self.memory.collection_name
        }
    
    def __str__(self):
        """字符串表示"""
        stats = self.get_stats()
        return f"RAGSystem(chunks={stats['total_chunks']}, collection={stats['collection_name']})"


# 示例使用
if __name__ == "__main__":
    print("=" * 70)
    print("RAG系统测试")
    print("=" * 70)
    
    # 创建RAG系统
    rag = RAGSystem(
        collection_name="demo_knowledge_base",
        chunk_size=200,
        chunk_overlap=30
    )
    
    # 准备测试文档
    documents = [
        {
            "id": "doc1_agent_memory",
            "content": """
Agent的记忆系统是构建智能Agent的关键组件。记忆系统主要分为两种类型：
短期记忆（Short-term Memory）和长期记忆（Long-term Memory）。

短期记忆用于维护当前对话的上下文，通常采用滑动窗口策略来管理有限的上下文长度。
它的特点是临时性、容量有限，但访问速度快。短期记忆的实现通常基于消息队列或列表。

长期记忆则用于持久化存储重要知识和历史信息。它通常使用向量数据库实现，
支持语义检索功能。长期记忆的容量理论上可以无限扩展，但检索速度相对较慢。

两种记忆系统相互配合，使Agent既能保持对话连贯性，又能积累和利用长期知识。
            """,
            "metadata": {"topic": "记忆系统", "source": "教程"}
        },
        {
            "id": "doc2_rag",
            "content": """
RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合检索和生成的技术。
它的核心思想是在生成答案之前，先从知识库中检索相关信息，然后基于检索到的信息生成回答。

RAG的完整流程包括以下步骤：
1. 文档分块（Chunking）：将长文档切分成适合处理的小块
2. 向量化（Embedding）：将文本块转换为向量表示
3. 存储（Storage）：将向量存储到向量数据库
4. 检索（Retrieval）：根据用户查询检索最相关的文本块
5. 增强生成（Augmented Generation）：基于检索结果生成最终答案

RAG相比传统的Fine-tuning方法有几个优势：成本更低、更新更容易、可解释性更强。
它特别适合用于构建问答系统、知识助手等应用。
            """,
            "metadata": {"topic": "RAG", "source": "教程"}
        },
        {
            "id": "doc3_vector_db",
            "content": """
向量数据库是专门用于存储和检索向量数据的数据库系统。它是RAG和长期记忆的基础设施。

主流的向量数据库包括：
- ChromaDB：轻量级、易用，适合开发和小规模应用
- Pinecone：云服务、高性能，适合生产环境
- Weaviate：功能丰富、开源，适合企业应用
- Milvus：分布式、高并发，适合海量数据

向量数据库的核心功能是相似度搜索。它使用特殊的索引结构（如HNSW、IVF）
来实现高效的向量检索。常用的相似度度量方法包括余弦相似度和欧氏距离。

选择向量数据库时，需要考虑数据规模、性能要求、成本预算等因素。
            """,
            "metadata": {"topic": "向量数据库", "source": "教程"}
        }
    ]
    
    # 摄取文档
    print("\n" + "=" * 70)
    print("步骤1: 文档摄取")
    print("=" * 70)
    rag.ingest_documents(documents, chunking_strategy="tokens")
    
    print(f"\n{rag}")
    print(f"\n统计信息: {rag.get_stats()}")
    
    # 测试检索
    print("\n" + "=" * 70)
    print("步骤2: 语义检索")
    print("=" * 70)
    
    test_queries = [
        "什么是短期记忆和长期记忆？",
        "RAG的工作流程是什么？",
        "有哪些向量数据库？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 70)
        
        results = rag.retrieve(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"  来源: {result['metadata']['doc_id']}")
            print(f"  相似度: {1 - result['distance']:.4f}")
            print(f"  内容预览: {result['content'][:100]}...")
    
    # 测试RAG问答
    print("\n" + "=" * 70)
    print("步骤3: RAG增强生成")
    print("=" * 70)
    
    query = "请详细介绍一下RAG技术"
    print(f"\n问题: {query}")
    print("-" * 70)
    
    # 生成RAG Prompt
    rag_prompt = rag.build_rag_prompt(query, top_k=3)
    print("\n生成的RAG Prompt:")
    print(rag_prompt)
    
    # 测试分块策略对比
    print("\n" + "=" * 70)
    print("步骤4: 分块策略对比")
    print("=" * 70)
    
    test_text = """这是测试文本。第一句话。第二句话。第三句话。
第四句话。第五句话。第六句话。第七句话。第八句话。"""
    
    print("\n原文:")
    print(test_text)
    
    print("\n策略1: 按Token分块 (chunk_size=30)")
    tokens_chunks = DocumentChunker.chunk_by_tokens(test_text, 30, 5)
    for i, chunk in enumerate(tokens_chunks):
        print(f"  块{i+1}: {chunk}")
    
    print("\n策略2: 按句子分块 (3句/块)")
    sentence_chunks = DocumentChunker.chunk_by_sentences(test_text, 3)
    for i, chunk in enumerate(sentence_chunks):
        print(f"  块{i+1}: {chunk}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    
    # 清理
    rag.clear_knowledge_base()
