"""
习题3: 上下文优化对比

对比不同上下文策略的效果:
- 固定窗口 vs 动态窗口
- 压缩 vs 不压缩
- 不同压缩率的影响
"""

import time
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class StrategyResult:
    """策略测试结果"""
    strategy_name: str
    token_count: int
    message_count: int
    execution_time: float
    quality_score: float
    cost_estimate: float


class ContextStrategyComparison:
    """上下文策略对比实验"""
    
    def __init__(self):
        # GPT-4定价 (示例)
        self.input_token_price = 0.03 / 1000
        self.output_token_price = 0.06 / 1000
    
    def run_comparison(self, messages: List[Dict], query: str):
        """运行完整对比实验"""
        print("=" * 80)
        print("上下文策略对比实验")
        print("=" * 80)
        
        print(f"\n测试数据:")
        print(f"  总消息数: {len(messages)}")
        print(f"  总Token数: {self._count_tokens(messages)}")
        print(f"  查询: {query}\n")
        
        # 实验1: 固定窗口 vs 动态窗口
        print("\n" + "=" * 80)
        print("实验1: 固定窗口 vs 动态窗口")
        print("=" * 80)
        self._compare_window_strategies(messages, query)
        
        # 实验2: 压缩 vs 不压缩
        print("\n" + "=" * 80)
        print("实验2: 压缩 vs 不压缩")
        print("=" * 80)
        self._compare_compression(messages, query)
        
        # 实验3: 不同压缩率的影响
        print("\n" + "=" * 80)
        print("实验3: 不同压缩率的影响")
        print("=" * 80)
        self._compare_compression_ratios(messages, query)
    
    def _compare_window_strategies(self, messages: List[Dict], query: str):
        """对比固定窗口和动态窗口"""
        results = []
        
        # 固定窗口策略
        fixed_result = self._test_fixed_window(messages, query, window_size=5)
        results.append(fixed_result)
        
        # 动态窗口策略
        dynamic_result = self._test_dynamic_window(messages, query, top_k=5)
        results.append(dynamic_result)
        
        # 显示结果
        self._print_results_table(results)
        
        # 分析
        print("\n分析:")
        print("  固定窗口:")
        print("    ✓ 优点: 实现简单、速度快")
        print("    ✗ 缺点: 可能丢失重要的早期信息")
        print("  动态窗口:")
        print("    ✓ 优点: 保留重要信息、上下文质量高")
        print("    ✗ 缺点: 需要计算重要性、速度较慢")
        
        # 推荐
        if dynamic_result.quality_score > fixed_result.quality_score * 1.2:
            print("\n推荐: 动态窗口 (质量提升明显)")
        elif fixed_result.execution_time < dynamic_result.execution_time * 0.5:
            print("\n推荐: 固定窗口 (速度优势明显)")
        else:
            print("\n推荐: 根据场景选择")
    
    def _compare_compression(self, messages: List[Dict], query: str):
        """对比压缩和不压缩"""
        results = []
        
        # 不压缩
        no_compress_result = self._test_no_compression(messages, query)
        results.append(no_compress_result)
        
        # 压缩50%
        compress_result = self._test_with_compression(messages, query, ratio=0.5)
        results.append(compress_result)
        
        # 显示结果
        self._print_results_table(results)
        
        # 计算节省
        token_saved = no_compress_result.token_count - compress_result.token_count
        cost_saved = no_compress_result.cost_estimate - compress_result.cost_estimate
        quality_loss = no_compress_result.quality_score - compress_result.quality_score
        
        print(f"\n压缩效果:")
        print(f"  Token节省: {token_saved} ({token_saved/no_compress_result.token_count:.1%})")
        print(f"  成本节省: ${cost_saved:.4f} ({cost_saved/no_compress_result.cost_estimate:.1%})")
        print(f"  质量损失: {quality_loss:.1f} ({quality_loss/no_compress_result.quality_score:.1%})")
        
        # 推荐
        if len(messages) > 10:
            print("\n推荐: 启用压缩 (对话轮数多)")
        elif cost_saved / no_compress_result.cost_estimate > 0.3:
            print("\n推荐: 启用压缩 (成本节省显著)")
        else:
            print("\n推荐: 不压缩 (对话较短，保持质量)")
    
    def _compare_compression_ratios(self, messages: List[Dict], query: str):
        """对比不同压缩率"""
        results = []
        ratios = [0.3, 0.5, 0.7, 1.0]  # 1.0表示不压缩
        
        for ratio in ratios:
            if ratio == 1.0:
                result = self._test_no_compression(messages, query)
            else:
                result = self._test_with_compression(messages, query, ratio)
            results.append(result)
        
        # 显示结果
        self._print_results_table(results)
        
        # 绘制趋势
        print("\n压缩率影响趋势:")
        print(f"{'压缩率':<10} {'Token':<10} {'成本':<12} {'质量':<10} {'效率':<10}")
        print("-" * 52)
        
        for result in results:
            # 提取压缩率
            if "不压缩" in result.strategy_name:
                ratio_str = "100%"
            else:
                ratio_str = result.strategy_name.split("压缩")[1].strip()
            
            efficiency = result.quality_score / (result.cost_estimate * 1000)
            
            print(f"{ratio_str:<10} {result.token_count:<10} "
                  f"${result.cost_estimate:<11.4f} "
                  f"{result.quality_score:<10.1f} {efficiency:<10.1f}")
        
        print("\n结论:")
        print("  - 压缩率越低，Token和成本越少，但质量也降低")
        print("  - 50%压缩率是较好的平衡点")
        print("  - 70%压缩适合成本敏感场景")
        print("  - 30%压缩适合严格Token限制场景")
    
    def _test_fixed_window(
        self,
        messages: List[Dict],
        query: str,
        window_size: int
    ) -> StrategyResult:
        """测试固定窗口策略"""
        start_time = time.time()
        
        # 保留最新的N条消息
        context = messages[-window_size:] if len(messages) > window_size else messages
        context.append({"role": "user", "content": query})
        
        token_count = self._count_tokens(context)
        execution_time = time.time() - start_time
        
        # 评估质量 (简化: 基于保留的消息数)
        quality = min(len(context) / window_size * 8, 10.0)
        
        cost = token_count * self.input_token_price
        
        return StrategyResult(
            strategy_name=f"固定窗口({window_size}条)",
            token_count=token_count,
            message_count=len(context),
            execution_time=execution_time,
            quality_score=quality,
            cost_estimate=cost
        )
    
    def _test_dynamic_window(
        self,
        messages: List[Dict],
        query: str,
        top_k: int
    ) -> StrategyResult:
        """测试动态窗口策略"""
        start_time = time.time()
        
        # 计算每条消息的重要性
        scored_messages = []
        for msg in messages:
            score = self._calculate_importance(msg, query)
            scored_messages.append((score, msg))
        
        # 排序并选择top_k
        scored_messages.sort(reverse=True, key=lambda x: x[0])
        context = [msg for _, msg in scored_messages[:top_k]]
        
        # 按原始顺序排列
        context = sorted(context, key=lambda m: messages.index(m))
        context.append({"role": "user", "content": query})
        
        token_count = self._count_tokens(context)
        execution_time = time.time() - start_time
        
        # 动态窗口质量通常更高
        quality = min(8.5, 10.0)
        
        cost = token_count * self.input_token_price
        
        return StrategyResult(
            strategy_name=f"动态窗口(top{top_k})",
            token_count=token_count,
            message_count=len(context),
            execution_time=execution_time,
            quality_score=quality,
            cost_estimate=cost
        )
    
    def _test_no_compression(
        self,
        messages: List[Dict],
        query: str
    ) -> StrategyResult:
        """测试不压缩"""
        start_time = time.time()
        
        context = messages.copy()
        context.append({"role": "user", "content": query})
        
        token_count = self._count_tokens(context)
        execution_time = time.time() - start_time
        quality = 10.0  # 不压缩，质量最高
        cost = token_count * self.input_token_price
        
        return StrategyResult(
            strategy_name="不压缩",
            token_count=token_count,
            message_count=len(context),
            execution_time=execution_time,
            quality_score=quality,
            cost_estimate=cost
        )
    
    def _test_with_compression(
        self,
        messages: List[Dict],
        query: str,
        ratio: float
    ) -> StrategyResult:
        """测试带压缩"""
        start_time = time.time()
        
        # 简单压缩: 保留最新的消息
        target_count = int(len(messages) * ratio)
        context = messages[-target_count:] if target_count < len(messages) else messages
        
        # 添加压缩摘要
        if target_count < len(messages):
            old_messages = messages[:-target_count]
            summary = self._create_summary(old_messages)
            context = [{"role": "system", "content": summary}] + context
        
        context.append({"role": "user", "content": query})
        
        token_count = self._count_tokens(context)
        execution_time = time.time() - start_time
        
        # 压缩会损失一些质量
        quality = 10.0 * (0.7 + 0.3 * ratio)
        
        cost = token_count * self.input_token_price
        
        return StrategyResult(
            strategy_name=f"压缩{int(ratio*100)}%",
            token_count=token_count,
            message_count=len(context),
            execution_time=execution_time,
            quality_score=quality,
            cost_estimate=cost
        )
    
    def _calculate_importance(self, message: Dict, query: str) -> float:
        """计算消息重要性"""
        score = 5.0
        content = message.get("content", "")
        
        # 关键词加分
        keywords = ["重要", "关键", "必须", "注意", "问题"]
        for kw in keywords:
            if kw in content:
                score += 1.0
        
        # 与查询相关性
        query_words = set(query.split())
        content_words = set(content.split())
        overlap = len(query_words & content_words)
        score += overlap * 0.5
        
        # 用户消息优先级高
        if message.get("role") == "user":
            score += 2.0
        
        return min(score, 10.0)
    
    def _create_summary(self, messages: List[Dict]) -> str:
        """创建消息摘要"""
        return f"[历史摘要: 共{len(messages)}条消息已压缩]"
    
    def _count_tokens(self, messages: List[Dict]) -> int:
        """计算Token数"""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # 简化: 1 token ≈ 4 chars
            total += len(content) // 4 + 1
        return total
    
    def _print_results_table(self, results: List[StrategyResult]):
        """打印结果表格"""
        print(f"\n{'策略':<20} {'Token':<10} {'消息数':<8} {'时间(ms)':<12} {'质量':<8} {'成本':<12}")
        print("-" * 80)
        
        for result in results:
            print(f"{result.strategy_name:<20} "
                  f"{result.token_count:<10} "
                  f"{result.message_count:<8} "
                  f"{result.execution_time*1000:<12.2f} "
                  f"{result.quality_score:<8.1f} "
                  f"${result.cost_estimate:<11.4f}")


# ============ 测试代码 ============

def create_test_messages() -> List[Dict]:
    """创建测试消息 (20轮对话)"""
    messages = []
    
    conversations = [
        ("你好", "你好！有什么可以帮助你的？"),
        ("我想学习编程", "很好！你想学习哪种编程语言？"),
        ("Python怎么样？", "Python非常适合初学者，语法简洁。"),
        ("需要什么基础吗？", "不需要，Python适合零基础学习。"),
        ("从哪里开始？", "建议从安装Python和学习基础语法开始。"),
        ("变量怎么用？", "在Python中，变量直接赋值即可，如 x = 10"),
        ("数据类型有哪些？", "主要有int、float、str、bool、list、dict等。"),
        ("重要：列表和字典的区别？", "列表是有序序列，字典是键值对映射。"),
        ("能举个例子吗？", "列表: [1,2,3]，字典: {'name':'Tom'}"),
        ("明白了", "很好！还有问题吗？"),
        ("函数怎么定义？", "使用def关键字定义函数。"),
        ("参数怎么传递？", "函数定义时在括号中指定参数。"),
        ("返回值呢？", "使用return语句返回值。"),
        ("类和对象是什么？", "类是对象的模板，对象是类的实例。"),
        ("怎么创建类？", "使用class关键字定义类。"),
        ("继承怎么实现？", "在类定义时指定父类。"),
        ("模块怎么导入？", "使用import语句导入模块。"),
        ("包和模块的区别？", "包是包含多个模块的目录。"),
        ("关键：异常怎么处理？", "使用try-except语句处理异常。"),
        ("文件怎么读写？", "使用open()函数打开文件。")
    ]
    
    for user_msg, assistant_msg in conversations:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    
    return messages


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("Task04 习题3: 上下文优化对比实验")
    print("=" * 80)
    
    # 创建测试数据
    messages = create_test_messages()
    query = "Python的异常处理最佳实践是什么？"
    
    # 运行对比实验
    comparison = ContextStrategyComparison()
    comparison.run_comparison(messages, query)
    
    print("\n" + "=" * 80)
    print("实验结论")
    print("=" * 80)
    print("\n1. 窗口策略选择:")
    print("   - 简单场景: 使用固定窗口")
    print("   - 复杂任务: 使用动态窗口")
    print("   - 生产环境: 推荐动态窗口")
    
    print("\n2. 压缩策略选择:")
    print("   - <10轮对话: 不压缩")
    print("   - 10-20轮: 压缩50%")
    print("   - >20轮: 压缩70%")
    
    print("\n3. 综合建议:")
    print("   - 开发阶段: 固定窗口 + 不压缩")
    print("   - 生产环境: 动态窗口 + 50%压缩")
    print("   - 成本优化: 固定窗口 + 70%压缩")
    
    print("\n✅ 习题3测试完成!")


if __name__ == "__main__":
    main()
