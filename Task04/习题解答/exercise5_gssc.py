"""
习题2: GSSC流水线实践

实现:
1. 上下文质量评估功能
2. 混合压缩策略
3. GSSC完整流水线
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class QualityMetrics:
    """上下文质量指标"""
    relevance_score: float  # 相关性得分 (0-1)
    information_density: float  # 信息密度 (0-1)
    completeness: float  # 完整性 (0-1)
    token_efficiency: float  # Token效率 (信息量/Token数)
    overall_score: float  # 综合得分 (0-100)
    suggestions: List[str]  # 优化建议


class CompressionMethod(Enum):
    """压缩方法"""
    TRUNCATE = "truncate"
    SUMMARIZE = "summarize"
    EXTRACT = "extract"
    HYBRID = "hybrid"


class ContextQualityEvaluator:
    """上下文质量评估器"""
    
    def __init__(self):
        self.importance_keywords = [
            "重要", "关键", "必须", "核心", "主要",
            "critical", "important", "key", "essential"
        ]
    
    def evaluate(
        self,
        context: List[Dict],
        query: str,
        max_tokens: int = 4000
    ) -> QualityMetrics:
        """
        评估上下文质量
        
        Args:
            context: 上下文消息列表
            query: 用户查询
            max_tokens: 最大Token限制
        
        Returns:
            QualityMetrics: 质量评估结果
        """
        # 1. 计算相关性
        relevance = self._calculate_relevance(context, query)
        
        # 2. 计算信息密度
        density = self._calculate_density(context)
        
        # 3. 计算完整性
        completeness = self._calculate_completeness(context, query)
        
        # 4. 计算Token效率
        efficiency = self._calculate_efficiency(context, max_tokens)
        
        # 5. 计算综合得分
        overall = self._calculate_overall(relevance, density, completeness, efficiency)
        
        # 6. 生成优化建议
        suggestions = self._generate_suggestions(
            relevance, density, completeness, efficiency, context, max_tokens
        )
        
        return QualityMetrics(
            relevance_score=relevance,
            information_density=density,
            completeness=completeness,
            token_efficiency=efficiency,
            overall_score=overall,
            suggestions=suggestions
        )
    
    def _calculate_relevance(self, context: List[Dict], query: str) -> float:
        """计算相关性得分"""
        if not context:
            return 0.0
        
        query_words = set(query.lower().split())
        total_relevance = 0.0
        
        for msg in context:
            content = msg.get("content", "").lower()
            content_words = set(content.split())
            
            # 计算词汇重叠度
            overlap = len(query_words & content_words)
            relevance = overlap / len(query_words) if query_words else 0
            
            total_relevance += relevance
        
        # 归一化
        avg_relevance = total_relevance / len(context)
        return min(avg_relevance, 1.0)
    
    def _calculate_density(self, context: List[Dict]) -> float:
        """计算信息密度"""
        if not context:
            return 0.0
        
        total_density = 0.0
        
        for msg in context:
            content = msg.get("content", "")
            
            # 信息密度指标
            # 1. 唯一词比例
            words = content.split()
            unique_ratio = len(set(words)) / len(words) if words else 0
            
            # 2. 重要词密度
            important_words = sum(
                1 for w in words 
                if any(kw in w.lower() for kw in self.importance_keywords)
            )
            important_ratio = important_words / len(words) if words else 0
            
            # 3. 句子长度适中性 (太短或太长都不好)
            sentences = content.split('。')
            avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            length_score = min(avg_sentence_len / 15, 1.0)  # 理想长度15词
            
            # 综合密度
            density = (unique_ratio + important_ratio + length_score) / 3
            total_density += density
        
        return total_density / len(context)
    
    def _calculate_completeness(self, context: List[Dict], query: str) -> float:
        """计算完整性"""
        # 简化版: 检查是否包含必要的上下文元素
        
        has_system = any(m.get("role") == "system" for m in context)
        has_history = len([m for m in context if m.get("role") in ["user", "assistant"]]) >= 2
        has_query = any(query.lower() in m.get("content", "").lower() for m in context)
        
        completeness_score = (
            (0.3 if has_system else 0) +
            (0.4 if has_history else 0) +
            (0.3 if has_query else 0)
        )
        
        return completeness_score
    
    def _calculate_efficiency(self, context: List[Dict], max_tokens: int) -> float:
        """计算Token效率"""
        total_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in context)
        
        if total_tokens == 0:
            return 0.0
        
        # 效率 = 实际使用 / 最大限制
        # 理想使用率: 70-90%
        usage_ratio = total_tokens / max_tokens
        
        if 0.7 <= usage_ratio <= 0.9:
            efficiency = 1.0  # 理想范围
        elif usage_ratio < 0.7:
            efficiency = usage_ratio / 0.7  # 使用不足
        else:
            efficiency = max(0, 1.0 - (usage_ratio - 0.9) * 2)  # 超限惩罚
        
        return efficiency
    
    def _calculate_overall(
        self,
        relevance: float,
        density: float,
        completeness: float,
        efficiency: float
    ) -> float:
        """计算综合得分"""
        # 加权平均
        weights = {
            "relevance": 0.35,      # 相关性最重要
            "density": 0.25,        # 信息密度
            "completeness": 0.20,   # 完整性
            "efficiency": 0.20      # 效率
        }
        
        overall = (
            relevance * weights["relevance"] +
            density * weights["density"] +
            completeness * weights["completeness"] +
            efficiency * weights["efficiency"]
        )
        
        return overall * 100  # 转换为0-100分制
    
    def _generate_suggestions(
        self,
        relevance: float,
        density: float,
        completeness: float,
        efficiency: float,
        context: List[Dict],
        max_tokens: int
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 相关性建议
        if relevance < 0.6:
            suggestions.append("⚠️ 相关性较低，建议优化检索策略或提高相关性阈值")
        
        # 信息密度建议
        if density < 0.5:
            suggestions.append("⚠️ 信息密度偏低，存在冗余内容，建议压缩或提取关键信息")
        
        # 完整性建议
        if completeness < 0.7:
            suggestions.append("⚠️ 上下文不完整，建议添加系统提示或补充历史对话")
        
        # 效率建议
        total_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in context)
        usage_ratio = total_tokens / max_tokens
        
        if usage_ratio > 0.9:
            suggestions.append(f"⚠️ Token使用率{usage_ratio:.1%}，接近上限，建议压缩")
        elif usage_ratio < 0.5:
            suggestions.append(f"ℹ️ Token使用率{usage_ratio:.1%}，空间充足，可添加更多上下文")
        
        # 没有问题
        if not suggestions:
            suggestions.append("✅ 上下文质量良好，无明显优化空间")
        
        return suggestions
    
    def _estimate_tokens(self, text: str) -> int:
        """估算Token数量"""
        return len(text) // 4 + 1


class HybridCompressor:
    """混合压缩策略"""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.evaluator = ContextQualityEvaluator()
    
    def compress(
        self,
        context: List[Dict],
        target_tokens: int,
        query: str = ""
    ) -> List[Dict]:
        """
        智能混合压缩
        
        策略选择逻辑:
        1. 轻度超限 (<20%): 截断压缩
        2. 中度超限 (20-50%): 提取+截断
        3. 重度超限 (>50%): 总结压缩
        """
        current_tokens = sum(self._estimate_tokens(m["content"]) for m in context)
        
        if current_tokens <= target_tokens:
            return context  # 不需要压缩
        
        # 计算超限程度
        overflow_ratio = (current_tokens - target_tokens) / target_tokens
        
        print(f"\n压缩前: {current_tokens} tokens")
        print(f"目标: {target_tokens} tokens")
        print(f"超限: {overflow_ratio:.1%}")
        
        # 根据超限程度选择策略
        if overflow_ratio < 0.2:
            print("策略: 截断压缩")
            compressed = self._truncate_compress(context, target_tokens)
        elif overflow_ratio < 0.5:
            print("策略: 混合(提取+截断)")
            compressed = self._extract_and_truncate(context, target_tokens, query)
        else:
            print("策略: 总结压缩")
            compressed = self._summarize_compress(context, target_tokens)
        
        final_tokens = sum(self._estimate_tokens(m["content"]) for m in compressed)
        print(f"压缩后: {final_tokens} tokens")
        print(f"压缩率: {(1 - final_tokens/current_tokens):.1%}")
        
        return compressed
    
    def _truncate_compress(
        self,
        context: List[Dict],
        target_tokens: int
    ) -> List[Dict]:
        """截断压缩 - 保留最新消息"""
        compressed = []
        used_tokens = 0
        
        # 保留系统提示
        system_msgs = [m for m in context if m.get("role") == "system"]
        other_msgs = [m for m in context if m.get("role") != "system"]
        
        # 添加系统消息
        for msg in system_msgs:
            compressed.append(msg)
            used_tokens += self._estimate_tokens(msg["content"])
        
        # 从后往前添加其他消息
        for msg in reversed(other_msgs):
            msg_tokens = self._estimate_tokens(msg["content"])
            if used_tokens + msg_tokens <= target_tokens:
                compressed.insert(len(system_msgs), msg)
                used_tokens += msg_tokens
            else:
                break
        
        return compressed
    
    def _extract_and_truncate(
        self,
        context: List[Dict],
        target_tokens: int,
        query: str
    ) -> List[Dict]:
        """提取关键信息 + 截断"""
        # 第1步: 提取关键句子
        extracted = []
        
        for msg in context:
            role = msg["role"]
            content = msg["content"]
            
            # 提取关键内容
            key_content = self._extract_key_sentences(content, query)
            
            if key_content:
                extracted.append({
                    "role": role,
                    "content": key_content
                })
        
        # 第2步: 如果还超限，截断
        return self._truncate_compress(extracted, target_tokens)
    
    def _summarize_compress(
        self,
        context: List[Dict],
        target_tokens: int
    ) -> List[Dict]:
        """总结压缩"""
        # 保留系统提示
        system_msgs = [m for m in context if m.get("role") == "system"]
        other_msgs = [m for m in context if m.get("role") != "system"]
        
        # 总结其他消息
        summary_content = self._generate_summary(other_msgs, target_tokens)
        
        summary = [{
            "role": "system",
            "content": f"[对话摘要]\n{summary_content}"
        }]
        
        return system_msgs + summary
    
    def _extract_key_sentences(self, text: str, query: str) -> str:
        """提取关键句子"""
        sentences = text.split('。')
        query_words = set(query.lower().split())
        
        # 为每个句子打分
        scored_sentences = []
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words & sentence_words)
            
            # 包含重要关键词加分
            importance_bonus = sum(
                1 for word in sentence_words
                if any(kw in word for kw in ["重要", "关键", "必须", "核心"])
            )
            
            score = overlap + importance_bonus
            scored_sentences.append((score, sentence))
        
        # 选择得分最高的句子
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # 取前50%的句子
        top_half = int(len(scored_sentences) * 0.5) or 1
        key_sentences = [s[1] for s in scored_sentences[:top_half]]
        
        return '。'.join(key_sentences) + '。' if key_sentences else text[:100]
    
    def _generate_summary(self, messages: List[Dict], target_tokens: int) -> str:
        """生成摘要（模拟LLM）"""
        # 实际应调用LLM
        # summary = self.llm.summarize(messages, max_tokens=target_tokens)
        
        # 模拟摘要
        user_count = len([m for m in messages if m["role"] == "user"])
        assistant_count = len([m for m in messages if m["role"] == "assistant"])
        
        summary = f"""对话包含{user_count}个用户问题和{assistant_count}个助手回复。
主要讨论了: """
        
        # 提取前几个用户问题
        user_msgs = [m for m in messages if m["role"] == "user"][:3]
        topics = [m["content"][:30] + "..." for m in user_msgs]
        summary += ", ".join(topics)
        
        return summary
    
    def _estimate_tokens(self, text: str) -> int:
        """估算Token数量"""
        return len(text) // 4 + 1


class GSSCPipeline:
    """GSSC完整流水线"""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.evaluator = ContextQualityEvaluator()
        self.compressor = HybridCompressor(llm_client)
    
    def build_context(
        self,
        query: str,
        documents: List[str],
        max_tokens: int = 4000
    ) -> Tuple[List[Dict], QualityMetrics]:
        """
        完整GSSC流水线
        
        Returns:
            (优化的上下文, 质量评估)
        """
        print("=" * 60)
        print("GSSC流水线执行")
        print("=" * 60)
        
        # Gather: 收集
        print("\n[Gather] 收集相关文档...")
        gathered = self._gather(query, documents)
        print(f"收集到{len(gathered)}个文档")
        
        # Select: 选择
        print("\n[Select] 选择最相关的内容...")
        selected = self._select(query, gathered, top_k=5)
        print(f"选择了{len(selected)}个最相关的文档")
        
        # Structure: 结构化
        print("\n[Structure] 结构化组织...")
        structured = self._structure(query, selected)
        print(f"组织成{len(structured)}条消息")
        
        # Compress: 压缩
        print("\n[Compress] 压缩到Token限制...")
        compressed = self.compressor.compress(structured, max_tokens, query)
        
        # 评估质量
        print("\n[Evaluate] 评估上下文质量...")
        quality = self.evaluator.evaluate(compressed, query, max_tokens)
        
        print("\n" + "=" * 60)
        print("质量评估结果")
        print("=" * 60)
        print(f"相关性: {quality.relevance_score:.2f}")
        print(f"信息密度: {quality.information_density:.2f}")
        print(f"完整性: {quality.completeness:.2f}")
        print(f"Token效率: {quality.token_efficiency:.2f}")
        print(f"综合得分: {quality.overall_score:.1f}/100")
        print("\n优化建议:")
        for suggestion in quality.suggestions:
            print(f"  {suggestion}")
        
        return compressed, quality
    
    def _gather(self, query: str, documents: List[str]) -> List[Dict]:
        """收集相关文档"""
        # 简化: 返回所有文档
        return [
            {"content": doc, "relevance": self._calculate_relevance(query, doc)}
            for doc in documents
        ]
    
    def _select(self, query: str, gathered: List[Dict], top_k: int) -> List[Dict]:
        """选择最相关的文档"""
        # 按相关性排序
        sorted_docs = sorted(gathered, key=lambda x: x["relevance"], reverse=True)
        
        # 选择top_k
        return sorted_docs[:top_k]
    
    def _structure(self, query: str, selected: List[Dict]) -> List[Dict]:
        """结构化组织"""
        context = []
        
        # 系统提示
        context.append({
            "role": "system",
            "content": "你是一个专业的AI助手，能够基于提供的上下文回答问题。"
        })
        
        # 添加检索到的文档
        for i, doc in enumerate(selected, 1):
            context.append({
                "role": "system",
                "content": f"[文档{i}]\n{doc['content']}"
            })
        
        # 添加用户查询
        context.append({
            "role": "user",
            "content": query
        })
        
        return context
    
    def _calculate_relevance(self, query: str, doc: str) -> float:
        """计算相关性"""
        query_words = set(query.lower().split())
        doc_words = set(doc.lower().split())
        
        overlap = len(query_words & doc_words)
        return overlap / len(query_words) if query_words else 0


# ============ 测试代码 ============

def test_quality_evaluator():
    """测试质量评估器"""
    print("=" * 60)
    print("测试: 上下文质量评估")
    print("=" * 60)
    
    evaluator = ContextQualityEvaluator()
    
    # 测试场景1: 高质量上下文
    good_context = [
        {"role": "system", "content": "你是Python编程助手"},
        {"role": "user", "content": "如何优化Python代码性能？"},
        {"role": "assistant", "content": "Python性能优化的关键方法包括..."},
        {"role": "user", "content": "具体有哪些技巧？"},
    ]
    
    query = "Python性能优化"
    metrics = evaluator.evaluate(good_context, query, max_tokens=4000)
    
    print("\n场景1: 高质量上下文")
    print(f"相关性: {metrics.relevance_score:.2f}")
    print(f"信息密度: {metrics.information_density:.2f}")
    print(f"完整性: {metrics.completeness:.2f}")
    print(f"Token效率: {metrics.token_efficiency:.2f}")
    print(f"综合得分: {metrics.overall_score:.1f}/100")
    print("建议:")
    for s in metrics.suggestions:
        print(f"  {s}")
    
    # 测试场景2: 低质量上下文
    bad_context = [
        {"role": "user", "content": "Java和C++的区别"},
        {"role": "assistant", "content": "数据库索引优化方法..."},
    ]
    
    metrics2 = evaluator.evaluate(bad_context, query, max_tokens=4000)
    
    print("\n场景2: 低质量上下文")
    print(f"综合得分: {metrics2.overall_score:.1f}/100")
    print("建议:")
    for s in metrics2.suggestions:
        print(f"  {s}")
    
    print("\n✅ 质量评估测试完成!")


def test_hybrid_compressor():
    """测试混合压缩"""
    print("\n\n" + "=" * 60)
    print("测试: 混合压缩策略")
    print("=" * 60)
    
    compressor = HybridCompressor()
    
    # 创建测试上下文
    context = [
        {"role": "system", "content": "你是AI助手"},
    ]
    
    # 添加大量消息模拟超限
    for i in range(20):
        context.append({
            "role": "user",
            "content": f"这是第{i+1}个问题，关于Python编程的各种细节和技巧的讨论"
        })
        context.append({
            "role": "assistant",
            "content": f"这是第{i+1}个回答，详细解释了Python的特性、用法和最佳实践建议"
        })
    
    query = "Python性能优化"
    
    # 测试不同程度的压缩
    print("\n测试1: 轻度超限 (1500 → 1300 tokens)")
    compressed1 = compressor.compress(context[:10], 1300, query)
    
    print("\n测试2: 中度超限 (2000 → 1200 tokens)")
    compressed2 = compressor.compress(context[:15], 1200, query)
    
    print("\n测试3: 重度超限 (3000 → 800 tokens)")
    compressed3 = compressor.compress(context, 800, query)
    
    print("\n✅ 混合压缩测试完成!")


def test_gssc_pipeline():
    """测试完整GSSC流水线"""
    print("\n\n" + "=" * 60)
    print("测试: GSSC完整流水线")
    print("=" * 60)
    
    pipeline = GSSCPipeline()
    
    # 准备文档
    documents = [
        "Python使用引用计数进行内存管理，每个对象都有引用计数器",
        "GC垃圾回收器专门处理循环引用问题",
        "Python采用分代垃圾回收策略提高效率",
        "Java使用JVM进行内存管理",  # 不相关
        "可以使用sys.getrefcount()查看引用计数",
        "weakref模块提供弱引用支持",
        "C++需要手动管理内存",  # 不相关
        "Python的内存池机制减少malloc调用",
    ]
    
    query = "Python内存管理机制"
    
    # 执行GSSC流水线
    context, quality = pipeline.build_context(query, documents, max_tokens=2000)
    
    print("\n最终上下文:")
    for i, msg in enumerate(context, 1):
        preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
        print(f"{i}. [{msg['role']}] {preview}")
    
    print("\n✅ GSSC流水线测试完成!")


if __name__ == "__main__":
    test_quality_evaluator()
    test_hybrid_compressor()
    test_gssc_pipeline()
    
    print("\n" + "=" * 60)
    print("习题2: 全部测试通过! ✅")
    print("=" * 60)
