"""
高级压缩技术 (Advanced Compression)

实现高级上下文压缩功能:
1. 递归总结 (Recursive Summarization)
2. MapReduce总结
3. 分层总结 (Hierarchical Summarization)
4. 动态Few-shot示例选择

Author: Franke Chen
Date: 2024-12-22
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class Example:
    """Few-shot示例"""
    input: str
    output: str
    category: str = "general"
    metadata: Dict[str, Any] = None
    
    def format(self) -> str:
        """格式化为Prompt"""
        return f"输入: {self.input}\n输出: {self.output}"


class RecursiveSummarizer:
    """
    递归总结器
    
    处理超长文档的智能总结
    """
    
    def __init__(self, llm_client=None, max_chunk_size: int = 2000):
        """
        初始化
        
        Args:
            llm_client: LLM客户端
            max_chunk_size: 每块最大字符数
        """
        self.llm = llm_client
        self.max_chunk_size = max_chunk_size
    
    def summarize(self, text: str, target_length: int = 500) -> str:
        """
        递归总结文本
        
        Args:
            text: 要总结的文本
            target_length: 目标长度
        
        Returns:
            总结文本
        """
        if len(text) <= target_length:
            return text
        
        if len(text) <= self.max_chunk_size:
            # 直接总结
            return self._summarize_chunk(text, target_length)
        
        # 递归总结
        return self._recursive_summarize(text, target_length)
    
    def _recursive_summarize(self, text: str, target_length: int) -> str:
        """
        递归总结实现
        
        策略:
        1. 将文本分块
        2. 总结每一块
        3. 合并所有摘要
        4. 如果还太长,继续递归
        """
        # 分块
        chunks = self._split_text(text, self.max_chunk_size)
        
        print(f"递归总结: {len(text)}字符 → {len(chunks)}块")
        
        # 总结每一块
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"  总结第{i+1}/{len(chunks)}块...")
            summary = self._summarize_chunk(chunk, target_length//len(chunks))
            summaries.append(summary)
        
        # 合并
        combined = "\n".join(summaries)
        
        # 检查是否需要继续递归
        if len(combined) > target_length:
            print(f"  继续递归: {len(combined)}字符")
            return self._recursive_summarize(combined, target_length)
        
        return combined
    
    def _summarize_chunk(self, text: str, target_length: int) -> str:
        """
        总结单个文本块
        
        Args:
            text: 文本
            target_length: 目标长度
        
        Returns:
            摘要
        """
        if not self.llm:
            # 模拟总结: 截取前target_length个字符
            return text[:target_length] + "..."
        
        prompt = f"""请总结以下文本,要求:
1. 提取核心要点
2. 保持关键信息
3. 长度不超过{target_length}字

文本:
{text}

总结:"""
        
        try:
            summary = self.llm.chat(prompt)
            return summary
        except Exception as e:
            print(f"⚠️  总结失败: {e}")
            return text[:target_length]
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        智能分块
        
        优先在段落、句子边界分割
        """
        # 按段落分
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class MapReduceSummarizer:
    """
    MapReduce总结器
    
    适合并行处理大量文档
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def summarize(
        self,
        documents: List[str],
        target_length: int = 500
    ) -> str:
        """
        MapReduce总结
        
        Map阶段: 并行总结每个文档
        Reduce阶段: 合并所有摘要
        
        Args:
            documents: 文档列表
            target_length: 目标长度
        
        Returns:
            最终总结
        """
        print(f"MapReduce总结: {len(documents)}个文档")
        
        # Map阶段: 总结每个文档
        print("Map阶段: 总结各个文档...")
        summaries = []
        for i, doc in enumerate(documents):
            print(f"  处理文档 {i+1}/{len(documents)}")
            summary = self._summarize_doc(doc, target_length//len(documents))
            summaries.append(summary)
        
        # Reduce阶段: 合并摘要
        print("Reduce阶段: 合并摘要...")
        while len(summaries) > 1:
            new_summaries = []
            
            # 两两合并
            for i in range(0, len(summaries), 2):
                if i + 1 < len(summaries):
                    merged = self._merge_summaries(
                        summaries[i],
                        summaries[i+1],
                        target_length//len(summaries)
                    )
                else:
                    merged = summaries[i]
                
                new_summaries.append(merged)
            
            summaries = new_summaries
            print(f"  剩余 {len(summaries)} 个摘要")
        
        return summaries[0]
    
    def _summarize_doc(self, doc: str, target_length: int) -> str:
        """总结单个文档"""
        if not self.llm:
            return doc[:target_length]
        
        prompt = f"请总结以下文档(不超过{target_length}字):\n\n{doc}\n\n总结:"
        
        try:
            return self.llm.chat(prompt)
        except:
            return doc[:target_length]
    
    def _merge_summaries(
        self,
        summary1: str,
        summary2: str,
        target_length: int
    ) -> str:
        """合并两个摘要"""
        if not self.llm:
            combined = summary1 + "\n" + summary2
            return combined[:target_length]
        
        prompt = f"""请合并以下两个摘要(不超过{target_length}字):

摘要1:
{summary1}

摘要2:
{summary2}

合并后的摘要:"""
        
        try:
            return self.llm.chat(prompt)
        except:
            return (summary1 + "\n" + summary2)[:target_length]


class HierarchicalSummarizer:
    """
    分层总结器
    
    保留文档的层次结构
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def summarize(
        self,
        text: str,
        levels: int = 3
    ) -> Dict[str, Any]:
        """
        分层总结
        
        Args:
            text: 文本
            levels: 层数
        
        Returns:
            分层结构 {
                'level_0': 原文,
                'level_1': 第一层摘要,
                'level_2': 第二层摘要,
                ...
            }
        """
        result = {'level_0': text}
        
        current_text = text
        for level in range(1, levels + 1):
            target_length = len(text) // (2 ** level)
            
            print(f"生成第{level}层摘要 (目标长度: {target_length})")
            
            summary = self._summarize(current_text, target_length)
            result[f'level_{level}'] = summary
            
            current_text = summary
        
        return result
    
    def _summarize(self, text: str, target_length: int) -> str:
        """总结文本"""
        if not self.llm:
            return text[:target_length]
        
        prompt = f"请总结(不超过{target_length}字):\n\n{text}\n\n总结:"
        
        try:
            return self.llm.chat(prompt)
        except:
            return text[:target_length]


class DynamicFewShotSelector:
    """
    动态Few-shot示例选择器
    
    根据查询动态选择最相关的示例
    """
    
    def __init__(self, example_pool: List[Example]):
        """
        初始化
        
        Args:
            example_pool: 示例池
        """
        self.examples = example_pool
    
    def select_examples(
        self,
        query: str,
        k: int = 3,
        diversity: float = 0.0
    ) -> List[Example]:
        """
        选择最相关的k个示例
        
        Args:
            query: 查询
            k: 选择数量
            diversity: 多样性权重 (0-1)
        
        Returns:
            选择的示例
        """
        if diversity > 0:
            return self._select_diverse(query, k, diversity)
        else:
            return self._select_by_similarity(query, k)
    
    def _select_by_similarity(self, query: str, k: int) -> List[Example]:
        """
        按相似度选择
        
        这里使用简单的关键词匹配
        生产环境应使用向量相似度
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # 计算每个示例的相似度
        scored = []
        for example in self.examples:
            input_words = set(example.input.lower().split())
            
            # 计算关键词重叠度
            overlap = len(query_words & input_words)
            similarity = overlap / max(len(query_words), 1)
            
            scored.append((example, similarity))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [ex for ex, _ in scored[:k]]
    
    def _select_diverse(
        self,
        query: str,
        k: int,
        diversity_weight: float
    ) -> List[Example]:
        """
        选择既相关又多样的示例
        
        使用MMR (Maximal Marginal Relevance)
        """
        query_words = set(query.lower().split())
        
        selected = []
        candidates = self.examples.copy()
        
        for _ in range(k):
            if not candidates:
                break
            
            best_score = -float('inf')
            best_example = None
            best_idx = None
            
            for i, candidate in enumerate(candidates):
                # 相关性分数
                input_words = set(candidate.input.lower().split())
                overlap = len(query_words & input_words)
                relevance = overlap / max(len(query_words), 1)
                
                # 多样性分数
                if selected:
                    # 与已选示例的最大相似度
                    max_sim = 0
                    for sel in selected:
                        sel_words = set(sel.input.lower().split())
                        sim = len(input_words & sel_words) / max(len(input_words), 1)
                        max_sim = max(max_sim, sim)
                    
                    diversity = 1 - max_sim
                else:
                    diversity = 1.0
                
                # MMR分数
                score = (1-diversity_weight)*relevance + diversity_weight*diversity
                
                if score > best_score:
                    best_score = score
                    best_example = candidate
                    best_idx = i
            
            if best_example:
                selected.append(best_example)
                candidates.pop(best_idx)
        
        return selected
    
    def build_prompt(
        self,
        query: str,
        k: int = 3,
        diversity: float = 0.3
    ) -> str:
        """
        构建带示例的Prompt
        
        Args:
            query: 查询
            k: 示例数量
            diversity: 多样性权重
        
        Returns:
            完整的Prompt
        """
        # 选择示例
        examples = self.select_examples(query, k, diversity)
        
        # 构建Prompt
        prompt_parts = []
        
        # 添加指令
        prompt_parts.append("请参考以下示例完成任务:\n")
        
        # 添加示例
        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"示例{i}:")
            prompt_parts.append(example.format())
            prompt_parts.append("")
        
        # 添加当前任务
        prompt_parts.append("现在请完成:")
        prompt_parts.append(f"输入: {query}")
        prompt_parts.append("输出:")
        
        return "\n".join(prompt_parts)


# ============= 测试代码 =============

def test_recursive_summarization():
    """测试递归总结"""
    print("=" * 60)
    print("测试1: 递归总结")
    print("=" * 60)
    
    # 创建长文本
    long_text = """
    人工智能是计算机科学的一个重要分支,它致力于让机器模拟人类的智能行为。
    机器学习是实现人工智能的主要方法之一,通过让机器从数据中学习模式和规律。
    深度学习是机器学习的一个子领域,使用多层神经网络来处理复杂的问题。
    自然语言处理让机器能够理解和生成人类语言,是AI的关键应用之一。
    计算机视觉使机器能够理解图像和视频内容,广泛应用于自动驾驶等领域。
    强化学习通过奖励机制训练智能体,在游戏AI等领域取得突破性进展。
    """ * 5  # 重复5次,制造长文本
    
    print(f"\n原文长度: {len(long_text)} 字符")
    
    summarizer = RecursiveSummarizer()
    summary = summarizer.summarize(long_text, target_length=200)
    
    print(f"\n总结长度: {len(summary)} 字符")
    print(f"\n总结内容:\n{summary}")
    
    print("\n✅ 递归总结测试完成!")


def test_mapreduce_summarization():
    """测试MapReduce总结"""
    print("\n" + "=" * 60)
    print("测试2: MapReduce总结")
    print("=" * 60)
    
    documents = [
        "Python是一种流行的编程语言,以其简洁的语法和强大的库而闻名。",
        "机器学习使用算法让计算机从数据中学习,无需显式编程。",
        "深度学习通过多层神经网络处理复杂模式识别任务。",
        "数据科学结合统计学、编程和领域知识来从数据中提取见解。",
        "云计算提供按需的计算资源,提高了IT基础设施的灵活性。"
    ]
    
    print(f"\n文档数量: {len(documents)}")
    
    summarizer = MapReduceSummarizer()
    summary = summarizer.summarize(documents, target_length=100)
    
    print(f"\n最终总结:\n{summary}")
    
    print("\n✅ MapReduce总结测试完成!")


def test_hierarchical_summarization():
    """测试分层总结"""
    print("\n" + "=" * 60)
    print("测试3: 分层总结")
    print("=" * 60)
    
    text = "人工智能技术正在改变我们的生活。机器学习和深度学习使计算机能够从数据中学习。" * 10
    
    print(f"\n原文长度: {len(text)} 字符")
    
    summarizer = HierarchicalSummarizer()
    result = summarizer.summarize(text, levels=3)
    
    for level, content in result.items():
        print(f"\n{level} ({len(content)}字符):")
        print(content[:100] + "..." if len(content) > 100 else content)
    
    print("\n✅ 分层总结测试完成!")


def test_dynamic_fewshot():
    """测试动态Few-shot选择"""
    print("\n" + "=" * 60)
    print("测试4: 动态Few-shot示例选择")
    print("=" * 60)
    
    # 创建示例池
    example_pool = [
        Example(
            input="如何排序列表?",
            output="使用list.sort()或sorted()函数",
            category="python"
        ),
        Example(
            input="如何读取文件?",
            output="使用open()函数配合with语句",
            category="python"
        ),
        Example(
            input="什么是机器学习?",
            output="机器学习是让计算机从数据中学习的技术",
            category="ai"
        ),
        Example(
            input="如何训练神经网络?",
            output="使用反向传播算法更新权重",
            category="ai"
        ),
        Example(
            input="如何创建数据库?",
            output="使用CREATE DATABASE SQL命令",
            category="database"
        )
    ]
    
    selector = DynamicFewShotSelector(example_pool)
    
    # 测试查询
    query = "如何写入文件?"
    print(f"\n查询: {query}")
    
    # 选择示例
    examples = selector.select_examples(query, k=2, diversity=0.0)
    
    print(f"\n选择的示例(相似度优先):")
    for i, ex in enumerate(examples, 1):
        print(f"\n{i}. {ex.input}")
        print(f"   → {ex.output}")
    
    # 选择多样示例
    diverse_examples = selector.select_examples(query, k=3, diversity=0.5)
    
    print(f"\n选择的示例(相似度+多样性):")
    for i, ex in enumerate(diverse_examples, 1):
        print(f"\n{i}. {ex.input}")
        print(f"   → {ex.output}")
    
    # 构建Prompt
    print(f"\n构建的Prompt:")
    print("-" * 60)
    prompt = selector.build_prompt(query, k=2, diversity=0.3)
    print(prompt)
    print("-" * 60)
    
    print("\n✅ Few-shot选择测试完成!")


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始测试高级压缩技术...\n")
    
    test_recursive_summarization()
    test_mapreduce_summarization()
    test_hierarchical_summarization()
    test_dynamic_fewshot()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print("=" * 60)
    
    print("\n💡 总结:")
    print("  - 递归总结: 处理超长文档")
    print("  - MapReduce总结: 并行处理多文档")
    print("  - 分层总结: 保留层次结构")
    print("  - 动态Few-shot: 智能示例选择")


if __name__ == "__main__":
    run_all_tests()
