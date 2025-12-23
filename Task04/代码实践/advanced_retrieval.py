"""
高级检索技术 (Advanced Retrieval)

实现高级上下文检索功能:
1. 向量相似度检索
2. BM25关键词检索
3. 混合检索策略
4. 重排序优化

注意: 需要安装依赖
pip install sentence-transformers rank-bm25 jieba numpy

Author: Franke Chen
Date: 2024-12-22
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import time

# 尝试导入可选依赖
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("⚠️  sentence-transformers未安装,向量检索功能将被禁用")
    print("   安装命令: pip install sentence-transformers")

try:
    from rank_bm25 import BM25Okapi
    import jieba
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("⚠️  rank-bm25或jieba未安装,BM25检索功能将被禁用")
    print("   安装命令: pip install rank-bm25 jieba")


@dataclass
class SearchResult:
    """检索结果"""
    document: str
    score: float
    method: str  # 'vector', 'bm25', 'hybrid'
    metadata: Dict[str, Any] = None
    
    def __repr__(self) -> str:
        return f"SearchResult(score={self.score:.3f}, method={self.method}, doc={self.document[:50]}...)"


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    计算余弦相似度
    
    Args:
        vec1: 向量1
        vec2: 向量2
    
    Returns:
        相似度 (-1到1)
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


class VectorRetriever:
    """
    向量检索器
    
    使用Sentence-BERT进行语义检索
    """
    
    def __init__(
        self,
        documents: List[str],
        model_name: str = 'all-MiniLM-L6-v2'
    ):
        """
        初始化
        
        Args:
            documents: 文档列表
            model_name: Embedding模型名称
        """
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("需要安装sentence-transformers")
        
        self.documents = documents
        self.model = SentenceTransformer(model_name)
        
        # 预先计算所有文档的向量
        print(f"正在为{len(documents)}个文档生成向量...")
        self.doc_vectors = self.model.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        print("✅ 向量生成完成!")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        向量检索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            min_score: 最低相似度分数
        
        Returns:
            检索结果列表
        """
        # 查询向量化
        query_vector = self.model.encode([query], convert_to_numpy=True)[0]
        
        # 计算与所有文档的相似度
        similarities = []
        for i, doc_vec in enumerate(self.doc_vectors):
            sim = cosine_similarity(query_vector, doc_vec)
            if sim >= min_score:
                similarities.append((i, sim))
        
        # 排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for idx, score in similarities[:top_k]:
            results.append(SearchResult(
                document=self.documents[idx],
                score=float(score),
                method='vector'
            ))
        
        return results


class BM25Retriever:
    """
    BM25检索器
    
    基于关键词的检索,擅长精确匹配
    """
    
    def __init__(self, documents: List[str], language: str = 'zh'):
        """
        初始化
        
        Args:
            documents: 文档列表
            language: 语言 ('zh'中文, 'en'英文)
        """
        if not HAS_BM25:
            raise ImportError("需要安装rank-bm25和jieba")
        
        self.documents = documents
        self.language = language
        
        # 分词
        print(f"正在为{len(documents)}个文档分词...")
        if language == 'zh':
            self.tokenized_docs = [
                list(jieba.cut(doc))
                for doc in documents
            ]
        else:
            self.tokenized_docs = [
                doc.lower().split()
                for doc in documents
            ]
        
        # 创建BM25索引
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print("✅ BM25索引创建完成!")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        BM25检索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            min_score: 最低分数
        
        Returns:
            检索结果列表
        """
        # 分词
        if self.language == 'zh':
            tokenized_query = list(jieba.cut(query))
        else:
            tokenized_query = query.lower().split()
        
        # BM25评分
        scores = self.bm25.get_scores(tokenized_query)
        
        # 筛选和排序
        scored_docs = [
            (i, score)
            for i, score in enumerate(scores)
            if score >= min_score
        ]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for idx, score in scored_docs[:top_k]:
            results.append(SearchResult(
                document=self.documents[idx],
                score=float(score),
                method='bm25'
            ))
        
        return results


class HybridRetriever:
    """
    混合检索器
    
    结合向量检索和BM25检索的优势
    """
    
    def __init__(
        self,
        documents: List[str],
        vector_model: str = 'all-MiniLM-L6-v2',
        language: str = 'zh'
    ):
        """
        初始化
        
        Args:
            documents: 文档列表
            vector_model: 向量模型名称
            language: 语言
        """
        self.documents = documents
        
        # 初始化两个检索器
        if HAS_SENTENCE_TRANSFORMERS:
            self.vector_retriever = VectorRetriever(documents, vector_model)
        else:
            self.vector_retriever = None
            print("⚠️  向量检索不可用")
        
        if HAS_BM25:
            self.bm25_retriever = BM25Retriever(documents, language)
        else:
            self.bm25_retriever = None
            print("⚠️  BM25检索不可用")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5,
        use_rrf: bool = True
    ) -> List[SearchResult]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            alpha: 向量检索权重 (0-1), BM25权重为1-alpha
            use_rrf: 是否使用RRF(Reciprocal Rank Fusion)
        
        Returns:
            检索结果列表
        """
        results = []
        
        # 向量检索
        if self.vector_retriever:
            vector_results = self.vector_retriever.search(query, top_k=top_k*2)
            results.append(('vector', vector_results))
        
        # BM25检索
        if self.bm25_retriever:
            bm25_results = self.bm25_retriever.search(query, top_k=top_k*2)
            results.append(('bm25', bm25_results))
        
        if not results:
            return []
        
        # 合并结果
        if use_rrf:
            return self._merge_with_rrf(results, top_k)
        else:
            return self._merge_with_weighted_sum(results, top_k, alpha)
    
    def _merge_with_weighted_sum(
        self,
        results: List[Tuple[str, List[SearchResult]]],
        top_k: int,
        alpha: float
    ) -> List[SearchResult]:
        """
        加权求和合并
        
        Args:
            results: [(method, search_results), ...]
            top_k: 返回数量
            alpha: 向量权重
        
        Returns:
            合并后的结果
        """
        # 归一化分数
        normalized_results = []
        
        for method, search_results in results:
            if not search_results:
                continue
            
            scores = [r.score for r in search_results]
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score == min_score:
                norm_scores = [1.0] * len(scores)
            else:
                norm_scores = [
                    (score - min_score) / (max_score - min_score)
                    for score in scores
                ]
            
            for result, norm_score in zip(search_results, norm_scores):
                normalized_results.append((method, result.document, norm_score))
        
        # 加权合并
        doc_scores = {}
        for method, doc, score in normalized_results:
            weight = alpha if method == 'vector' else (1 - alpha)
            if doc in doc_scores:
                doc_scores[doc] += weight * score
            else:
                doc_scores[doc] = weight * score
        
        # 排序
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 构建结果
        final_results = []
        for doc, score in sorted_docs[:top_k]:
            final_results.append(SearchResult(
                document=doc,
                score=score,
                method='hybrid'
            ))
        
        return final_results
    
    def _merge_with_rrf(
        self,
        results: List[Tuple[str, List[SearchResult]]],
        top_k: int,
        k: int = 60
    ) -> List[SearchResult]:
        """
        使用RRF(Reciprocal Rank Fusion)合并
        
        RRF公式: score = Σ 1/(k + rank)
        
        Args:
            results: [(method, search_results), ...]
            top_k: 返回数量
            k: RRF参数 (默认60)
        
        Returns:
            合并后的结果
        """
        doc_scores = {}
        
        for method, search_results in results:
            for rank, result in enumerate(search_results, start=1):
                doc = result.document
                rrf_score = 1.0 / (k + rank)
                
                if doc in doc_scores:
                    doc_scores[doc] += rrf_score
                else:
                    doc_scores[doc] = rrf_score
        
        # 排序
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 构建结果
        final_results = []
        for doc, score in sorted_docs[:top_k]:
            final_results.append(SearchResult(
                document=doc,
                score=score,
                method='hybrid_rrf'
            ))
        
        return final_results


# ============= 测试代码 =============

def create_test_documents() -> List[str]:
    """创建测试文档"""
    return [
        "Python是一种高级编程语言,适合初学者学习",
        "机器学习是人工智能的一个重要分支",
        "深度学习使用神经网络来解决复杂问题",
        "自然语言处理(NLP)处理人类语言",
        "计算机视觉让机器能够理解图像",
        "强化学习通过奖励来训练智能体",
        "数据科学结合统计学和编程技能",
        "云计算提供按需的计算资源",
        "区块链是一种分布式账本技术",
        "物联网连接物理设备到互联网"
    ]


def test_vector_retrieval():
    """测试向量检索"""
    if not HAS_SENTENCE_TRANSFORMERS:
        print("⚠️  跳过向量检索测试(缺少依赖)")
        return
    
    print("=" * 60)
    print("测试1: 向量检索")
    print("=" * 60)
    
    documents = create_test_documents()
    retriever = VectorRetriever(documents)
    
    # 测试查询
    query = "如何学习人工智能?"
    print(f"\n查询: {query}")
    
    results = retriever.search(query, top_k=3)
    
    print(f"\n找到{len(results)}个相关文档:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [分数: {result.score:.3f}]")
        print(f"   {result.document}")
    
    print("\n✅ 向量检索测试完成!")


def test_bm25_retrieval():
    """测试BM25检索"""
    if not HAS_BM25:
        print("⚠️  跳过BM25检索测试(缺少依赖)")
        return
    
    print("\n" + "=" * 60)
    print("测试2: BM25检索")
    print("=" * 60)
    
    documents = create_test_documents()
    retriever = BM25Retriever(documents)
    
    # 测试查询
    query = "机器学习 深度学习"
    print(f"\n查询: {query}")
    
    results = retriever.search(query, top_k=3)
    
    print(f"\n找到{len(results)}个相关文档:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [分数: {result.score:.3f}]")
        print(f"   {result.document}")
    
    print("\n✅ BM25检索测试完成!")


def test_hybrid_retrieval():
    """测试混合检索"""
    if not (HAS_SENTENCE_TRANSFORMERS and HAS_BM25):
        print("⚠️  跳过混合检索测试(缺少依赖)")
        return
    
    print("\n" + "=" * 60)
    print("测试3: 混合检索")
    print("=" * 60)
    
    documents = create_test_documents()
    retriever = HybridRetriever(documents)
    
    # 测试查询
    query = "学习编程和机器学习"
    print(f"\n查询: {query}")
    
    # 测试加权求和
    print("\n方法1: 加权求和 (alpha=0.5)")
    results_weighted = retriever.search(query, top_k=3, alpha=0.5, use_rrf=False)
    
    print(f"\n找到{len(results_weighted)}个相关文档:")
    for i, result in enumerate(results_weighted, 1):
        print(f"\n{i}. [分数: {result.score:.3f}, 方法: {result.method}]")
        print(f"   {result.document}")
    
    # 测试RRF
    print("\n方法2: RRF融合")
    results_rrf = retriever.search(query, top_k=3, use_rrf=True)
    
    print(f"\n找到{len(results_rrf)}个相关文档:")
    for i, result in enumerate(results_rrf, 1):
        print(f"\n{i}. [分数: {result.score:.3f}, 方法: {result.method}]")
        print(f"   {result.document}")
    
    print("\n✅ 混合检索测试完成!")


def test_comparison():
    """对比三种检索方法"""
    if not (HAS_SENTENCE_TRANSFORMERS and HAS_BM25):
        print("⚠️  跳过对比测试(缺少依赖)")
        return
    
    print("\n" + "=" * 60)
    print("测试4: 检索方法对比")
    print("=" * 60)
    
    documents = create_test_documents()
    
    # 创建三种检索器
    vector_retriever = VectorRetriever(documents)
    bm25_retriever = BM25Retriever(documents)
    hybrid_retriever = HybridRetriever(documents)
    
    # 测试查询
    query = "Python编程"
    print(f"\n查询: {query}\n")
    
    # 向量检索
    print("向量检索结果:")
    vector_results = vector_retriever.search(query, top_k=3)
    for result in vector_results:
        print(f"  {result.score:.3f} - {result.document[:40]}...")
    
    # BM25检索
    print("\nBM25检索结果:")
    bm25_results = bm25_retriever.search(query, top_k=3)
    for result in bm25_results:
        print(f"  {result.score:.3f} - {result.document[:40]}...")
    
    # 混合检索
    print("\n混合检索结果:")
    hybrid_results = hybrid_retriever.search(query, top_k=3)
    for result in hybrid_results:
        print(f"  {result.score:.3f} - {result.document[:40]}...")
    
    print("\n✅ 对比测试完成!")


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始测试高级检索系统...\n")
    
    test_vector_retrieval()
    test_bm25_retrieval()
    test_hybrid_retrieval()
    test_comparison()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成!")
    print("=" * 60)
    
    print("\n💡 总结:")
    print("  - 向量检索: 擅长语义理解")
    print("  - BM25检索: 擅长关键词匹配")
    print("  - 混合检索: 结合两者优势,效果最佳")


if __name__ == "__main__":
    run_all_tests()
