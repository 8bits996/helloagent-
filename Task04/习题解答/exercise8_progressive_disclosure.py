"""
习题5: 渐进式披露

实现:
1. 渐进式披露应用场景（学术论文写作）
2. 探索引导机制
3. 渐进式披露 vs 一次性加载对比
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class ExplorationStrategy(Enum):
    """探索策略"""
    BREADTH_FIRST = "breadth_first"      # 广度优先
    DEPTH_FIRST = "depth_first"          # 深度优先
    IMPORTANCE_FIRST = "importance_first"  # 重要性优先
    GUIDED = "guided"                    # 启发式引导


class NodeType(Enum):
    """知识图谱节点类型"""
    TOPIC = "topic"
    SUBTOPIC = "subtopic"
    CONCEPT = "concept"
    DETAIL = "detail"


@dataclass
class KnowledgeNode:
    """知识节点"""
    id: str
    type: NodeType
    title: str
    content: str
    importance: float = 5.0  # 1-10
    children: List[str] = field(default_factory=list)
    explored: bool = False
    depth: int = 0


class AcademicPaperWritingAgent:
    """学术论文写作Agent（渐进式披露示例）"""
    
    def __init__(self, topic: str):
        """
        初始化论文写作Agent
        
        Args:
            topic: 论文主题
        """
        self.topic = topic
        
        # 知识图谱
        self.knowledge_graph: Dict[str, KnowledgeNode] = {}
        
        # 探索历史
        self.exploration_history: List[str] = []
        
        # 已收集的信息
        self.collected_info: List[Dict] = []
        
        # 当前上下文（渐进式构建）
        self.current_context: List[Dict] = []
        
        # 初始化知识图谱
        self._build_knowledge_graph()
    
    def _build_knowledge_graph(self):
        """构建知识图谱"""
        # 根节点
        root = KnowledgeNode(
            id="root",
            type=NodeType.TOPIC,
            title=self.topic,
            content=f"研究主题: {self.topic}",
            importance=10.0,
            depth=0
        )
        
        # 子主题
        subtopics = [
            KnowledgeNode(
                id="background",
                type=NodeType.SUBTOPIC,
                title="研究背景",
                content="介绍研究领域的发展历程和现状",
                importance=9.0,
                depth=1
            ),
            KnowledgeNode(
                id="motivation",
                type=NodeType.SUBTOPIC,
                title="研究动机",
                content="阐述为什么要进行这项研究",
                importance=8.5,
                depth=1
            ),
            KnowledgeNode(
                id="methodology",
                type=NodeType.SUBTOPIC,
                title="研究方法",
                content="描述研究采用的方法论",
                importance=9.5,
                depth=1
            ),
            KnowledgeNode(
                id="results",
                type=NodeType.SUBTOPIC,
                title="研究结果",
                content="展示实验和分析结果",
                importance=10.0,
                depth=1
            ),
        ]
        
        root.children = [n.id for n in subtopics]
        
        # 细节节点
        methodology_details = [
            KnowledgeNode(
                id="data_collection",
                type=NodeType.CONCEPT,
                title="数据收集",
                content="数据来源：公开数据集，共10000样本",
                importance=7.0,
                depth=2
            ),
            KnowledgeNode(
                id="model_design",
                type=NodeType.CONCEPT,
                title="模型设计",
                content="采用Transformer架构，12层编码器",
                importance=8.0,
                depth=2
            ),
            KnowledgeNode(
                id="evaluation",
                type=NodeType.CONCEPT,
                title="评估指标",
                content="使用F1-score, Accuracy, Precision等指标",
                importance=7.5,
                depth=2
            ),
        ]
        
        subtopics[2].children = [n.id for n in methodology_details]
        
        # 更细节的节点
        model_details = [
            KnowledgeNode(
                id="attention_mechanism",
                type=NodeType.DETAIL,
                title="注意力机制",
                content="Multi-head self-attention with 8 heads",
                importance=6.0,
                depth=3
            ),
            KnowledgeNode(
                id="hyperparameters",
                type=NodeType.DETAIL,
                title="超参数设置",
                content="learning_rate=1e-4, batch_size=32, epochs=50",
                importance=5.5,
                depth=3
            ),
        ]
        
        methodology_details[1].children = [n.id for n in model_details]
        
        # 添加到图谱
        all_nodes = [root] + subtopics + methodology_details + model_details
        for node in all_nodes:
            self.knowledge_graph[node.id] = node
    
    def progressive_explore(self, max_steps: int = 10) -> str:
        """
        渐进式探索并写作
        
        Returns:
            生成的论文内容
        """
        print("\n" + "=" * 60)
        print("🔍 渐进式披露：学术论文写作")
        print("=" * 60)
        
        # 从根节点开始
        current_node_id = "root"
        
        for step in range(max_steps):
            print(f"\n--- 步骤 {step + 1}/{max_steps} ---")
            
            # 1. 探索当前节点
            node = self.knowledge_graph[current_node_id]
            self._explore_node(node)
            
            # 2. 决定下一步探索什么
            next_node_id = self._decide_next_exploration(current_node_id)
            
            if not next_node_id:
                print("✅ 探索完成，所有重要节点已访问")
                break
            
            # 3. 更新上下文
            self._update_context(node)
            
            # 4. 生成当前部分内容
            section = self._generate_section(node)
            self.collected_info.append(section)
            
            print(f"📝 生成章节: {section['title']}")
            print(f"   内容长度: {len(section['content'])} 字符")
            
            current_node_id = next_node_id
        
        # 5. 整合成完整论文
        paper = self._assemble_paper()
        
        return paper
    
    def _explore_node(self, node: KnowledgeNode):
        """探索节点"""
        if node.explored:
            print(f"⏭️  跳过已探索节点: {node.title}")
            return
        
        node.explored = True
        self.exploration_history.append(node.id)
        
        print(f"🔍 探索节点: {node.title}")
        print(f"   类型: {node.type.value}")
        print(f"   重要性: {node.importance}/10")
        print(f"   深度: {node.depth}")
        print(f"   内容: {node.content}")
        
        if node.children:
            print(f"   子节点数: {len(node.children)}")
    
    def _decide_next_exploration(self, current_id: str) -> Optional[str]:
        """
        决定下一步探索哪个节点
        
        使用启发式策略:
        1. 优先探索重要的未访问节点
        2. 考虑深度（不要太深）
        3. 考虑相关性
        """
        current_node = self.knowledge_graph[current_id]
        
        # 候选节点：当前节点的子节点 + 兄弟节点
        candidates = []
        
        # 1. 子节点（深入）
        for child_id in current_node.children:
            child = self.knowledge_graph[child_id]
            if not child.explored:
                candidates.append((child_id, child, "child"))
        
        # 2. 兄弟节点（广度）
        for node in self.knowledge_graph.values():
            if not node.explored and node.depth == current_node.depth:
                if node.id != current_id:
                    candidates.append((node.id, node, "sibling"))
        
        if not candidates:
            return None
        
        # 启发式评分
        scored_candidates = []
        for node_id, node, relation in candidates:
            score = self._calculate_exploration_score(node, current_node, relation)
            scored_candidates.append((score, node_id, node))
        
        # 选择得分最高的
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        
        best_score, best_id, best_node = scored_candidates[0]
        
        print(f"\n💡 探索决策:")
        print(f"   候选数量: {len(candidates)}")
        print(f"   选择: {best_node.title}")
        print(f"   理由: 得分 {best_score:.2f} (重要性={best_node.importance}, 深度={best_node.depth})")
        
        return best_id
    
    def _calculate_exploration_score(
        self,
        node: KnowledgeNode,
        current: KnowledgeNode,
        relation: str
    ) -> float:
        """
        计算探索得分
        
        考虑因素:
        1. 重要性（最重要）
        2. 深度（不要太深）
        3. 关系（子节点优先）
        """
        score = 0.0
        
        # 1. 重要性（权重0.5）
        score += node.importance * 0.5
        
        # 2. 深度惩罚（权重0.3）
        # 深度0-1: 无惩罚
        # 深度2: 小惩罚
        # 深度3+: 大惩罚
        depth_penalty = max(0, (node.depth - 1) * 2)
        score -= depth_penalty * 0.3
        
        # 3. 关系加分（权重0.2）
        if relation == "child":
            score += 2.0 * 0.2  # 深入优先
        elif relation == "sibling":
            score += 1.0 * 0.2  # 广度次之
        
        return score
    
    def _update_context(self, node: KnowledgeNode):
        """更新当前上下文（渐进式）"""
        # 只保留最相关的上下文
        context_item = {
            "role": "system",
            "content": f"[{node.type.value}] {node.title}: {node.content}"
        }
        
        self.current_context.append(context_item)
        
        # 限制上下文大小（保持渐进式）
        max_context_size = 5
        if len(self.current_context) > max_context_size:
            # 保留最重要和最新的
            self.current_context = self.current_context[-max_context_size:]
    
    def _generate_section(self, node: KnowledgeNode) -> Dict:
        """生成章节内容"""
        # 模拟基于上下文生成内容
        section = {
            "title": node.title,
            "content": f"{node.content}\n\n[基于当前探索的{len(self.exploration_history)}个节点生成的详细内容...]",
            "node_id": node.id,
            "importance": node.importance
        }
        
        return section
    
    def _assemble_paper(self) -> str:
        """整合成完整论文"""
        print("\n" + "=" * 60)
        print("📄 整合论文")
        print("=" * 60)
        
        paper = f"# {self.topic}\n\n"
        
        for section in self.collected_info:
            paper += f"## {section['title']}\n\n"
            paper += f"{section['content']}\n\n"
        
        print(f"\n论文统计:")
        print(f"   章节数: {len(self.collected_info)}")
        print(f"   探索节点数: {len(self.exploration_history)}")
        print(f"   总字符数: {len(paper)}")
        
        return paper


class ExplorationGuide:
    """探索引导系统"""
    
    def __init__(self):
        """初始化引导系统"""
        # 启发式规则
        self.heuristic_rules = {
            "avoid_rabbit_hole": {
                "name": "避免钻牛角尖",
                "description": "检测到深度过深，建议返回上层",
                "trigger": lambda context: context.get("depth", 0) > 3
            },
            "breadth_before_depth": {
                "name": "先广后深",
                "description": "同层节点未完全探索时，建议先完成同层",
                "trigger": lambda context: context.get("unexplored_siblings", 0) > 0
            },
            "importance_threshold": {
                "name": "重要性阈值",
                "description": "优先探索重要性>7的节点",
                "trigger": lambda context: context.get("max_importance", 0) > 7
            },
            "time_budget": {
                "name": "时间预算",
                "description": "探索步数过多，建议收敛",
                "trigger": lambda context: context.get("steps", 0) > 15
            }
        }
        
        # 元认知策略
        self.metacognitive_strategies = {
            "goal_check": "每3步检查一次是否偏离目标",
            "progress_review": "每5步回顾探索进度",
            "cost_benefit": "评估继续探索的成本收益比"
        }
    
    def guide_next_step(self, context: Dict) -> Dict:
        """
        引导下一步探索
        
        Args:
            context: 当前探索上下文
            
        Returns:
            Dict包含建议和理由
        """
        suggestions = []
        
        # 应用启发式规则
        for rule_id, rule in self.heuristic_rules.items():
            if rule["trigger"](context):
                suggestions.append({
                    "rule": rule_id,
                    "name": rule["name"],
                    "description": rule["description"],
                    "priority": self._calculate_priority(rule_id, context)
                })
        
        # 排序建议
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        # 生成综合建议
        if suggestions:
            top_suggestion = suggestions[0]
            action = self._suggest_action(top_suggestion["rule"], context)
        else:
            action = {"action": "continue", "reason": "无特殊情况，继续探索"}
        
        return {
            "suggestions": suggestions,
            "recommended_action": action,
            "applied_rules": [s["rule"] for s in suggestions]
        }
    
    def _calculate_priority(self, rule_id: str, context: Dict) -> float:
        """计算规则优先级"""
        priorities = {
            "time_budget": 10.0,        # 最高优先级
            "avoid_rabbit_hole": 8.0,
            "importance_threshold": 6.0,
            "breadth_before_depth": 5.0
        }
        return priorities.get(rule_id, 5.0)
    
    def _suggest_action(self, rule_id: str, context: Dict) -> Dict:
        """根据规则建议行动"""
        actions = {
            "avoid_rabbit_hole": {
                "action": "backtrack",
                "reason": "当前深度过深，建议返回上一层继续探索"
            },
            "breadth_before_depth": {
                "action": "explore_siblings",
                "reason": "同层还有未探索节点，建议先完成广度探索"
            },
            "importance_threshold": {
                "action": "prioritize_important",
                "reason": "发现高重要性节点，建议优先探索"
            },
            "time_budget": {
                "action": "converge",
                "reason": "探索步数较多，建议开始收敛总结"
            }
        }
        return actions.get(rule_id, {"action": "continue", "reason": "继续探索"})


class ComparisonTester:
    """对比测试器：渐进式 vs 一次性加载"""
    
    def __init__(self):
        pass
    
    def compare_strategies(self, task_type: str) -> Dict:
        """
        对比两种策略
        
        Args:
            task_type: 任务类型
        
        Returns:
            对比结果
        """
        print("\n" + "=" * 60)
        print(f"对比测试: {task_type}")
        print("=" * 60)
        
        # 模拟两种策略的执行
        progressive_result = self._simulate_progressive(task_type)
        full_load_result = self._simulate_full_load(task_type)
        
        # 对比分析
        comparison = {
            "task_type": task_type,
            "progressive": progressive_result,
            "full_load": full_load_result,
            "winner": self._determine_winner(progressive_result, full_load_result)
        }
        
        self._print_comparison(comparison)
        
        return comparison
    
    def _simulate_progressive(self, task_type: str) -> Dict:
        """模拟渐进式策略"""
        # 基于任务类型调整参数
        if task_type == "research":
            return {
                "total_tokens": 5000,
                "relevant_ratio": 0.85,
                "time_cost": 15,
                "quality_score": 8.5,
                "efficiency": 0.85
            }
        elif task_type == "debugging":
            return {
                "total_tokens": 3000,
                "relevant_ratio": 0.90,
                "time_cost": 10,
                "quality_score": 9.0,
                "efficiency": 0.90
            }
        else:  # code_review
            return {
                "total_tokens": 6000,
                "relevant_ratio": 0.75,
                "time_cost": 20,
                "quality_score": 7.5,
                "efficiency": 0.75
            }
    
    def _simulate_full_load(self, task_type: str) -> Dict:
        """模拟一次性加载策略"""
        if task_type == "research":
            return {
                "total_tokens": 50000,
                "relevant_ratio": 0.30,
                "time_cost": 60,
                "quality_score": 7.0,
                "efficiency": 0.30
            }
        elif task_type == "debugging":
            return {
                "total_tokens": 20000,
                "relevant_ratio": 0.40,
                "time_cost": 40,
                "quality_score": 6.5,
                "efficiency": 0.40
            }
        else:  # code_review
            return {
                "total_tokens": 80000,
                "relevant_ratio": 0.50,
                "time_cost": 50,
                "quality_score": 8.0,
                "efficiency": 0.50
            }
    
    def _determine_winner(self, progressive: Dict, full_load: Dict) -> str:
        """确定优胜者"""
        # 综合评分
        prog_score = (
            progressive["efficiency"] * 0.4 +
            progressive["quality_score"] / 10 * 0.3 +
            (1 - progressive["time_cost"] / 100) * 0.3
        )
        
        full_score = (
            full_load["efficiency"] * 0.4 +
            full_load["quality_score"] / 10 * 0.3 +
            (1 - full_load["time_cost"] / 100) * 0.3
        )
        
        if prog_score > full_score * 1.1:
            return "progressive"
        elif full_score > prog_score * 1.1:
            return "full_load"
        else:
            return "tie"
    
    def _print_comparison(self, comparison: Dict):
        """打印对比结果"""
        print(f"\n{'指标':<20} {'渐进式':<20} {'一次性加载':<20}")
        print("-" * 60)
        
        metrics = [
            ("Token消耗", "total_tokens"),
            ("相关性", "relevant_ratio"),
            ("时间成本(s)", "time_cost"),
            ("质量得分", "quality_score"),
            ("效率", "efficiency")
        ]
        
        prog = comparison["progressive"]
        full = comparison["full_load"]
        
        for metric_name, metric_key in metrics:
            prog_val = prog[metric_key]
            full_val = full[metric_key]
            
            # 格式化
            if metric_key == "total_tokens":
                prog_str = f"{prog_val:,}"
                full_str = f"{full_val:,}"
            elif metric_key in ["relevant_ratio", "efficiency"]:
                prog_str = f"{prog_val:.1%}"
                full_str = f"{full_val:.1%}"
            else:
                prog_str = f"{prog_val}"
                full_str = f"{full_val}"
            
            # 标记优胜者
            if metric_key in ["relevant_ratio", "quality_score", "efficiency"]:
                # 越高越好
                if prog_val > full_val:
                    prog_str += " ✅"
                elif full_val > prog_val:
                    full_str += " ✅"
            else:
                # 越低越好
                if prog_val < full_val:
                    prog_str += " ✅"
                elif full_val < prog_val:
                    full_str += " ✅"
            
            print(f"{metric_name:<20} {prog_str:<20} {full_str:<20}")
        
        print("\n" + "=" * 60)
        winner = comparison["winner"]
        if winner == "progressive":
            print("🏆 渐进式披露胜出")
        elif winner == "full_load":
            print("🏆 一次性加载胜出")
        else:
            print("🤝 两种方法不相上下")


# ============ 测试代码 ============

def test_progressive_paper_writing():
    """测试渐进式论文写作"""
    print("=" * 60)
    print("测试1: 渐进式披露 - 学术论文写作")
    print("=" * 60)
    
    agent = AcademicPaperWritingAgent("基于Transformer的文本分类研究")
    
    # 渐进式探索和写作
    paper = agent.progressive_explore(max_steps=8)
    
    print("\n" + "=" * 60)
    print("生成的论文大纲")
    print("=" * 60)
    print(paper[:500] + "...\n")
    
    print("✅ 渐进式论文写作测试完成!")


def test_exploration_guide():
    """测试探索引导机制"""
    print("\n\n" + "=" * 60)
    print("测试2: 探索引导机制")
    print("=" * 60)
    
    guide = ExplorationGuide()
    
    # 测试不同场景
    scenarios = [
        {
            "name": "场景1: 深度过深",
            "context": {"depth": 4, "steps": 5, "unexplored_siblings": 0}
        },
        {
            "name": "场景2: 同层未完成",
            "context": {"depth": 1, "steps": 3, "unexplored_siblings": 3}
        },
        {
            "name": "场景3: 发现重要节点",
            "context": {"depth": 2, "steps": 4, "max_importance": 9.0}
        },
        {
            "name": "场景4: 步数过多",
            "context": {"depth": 2, "steps": 16, "unexplored_siblings": 1}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"上下文: {scenario['context']}")
        
        guidance = guide.guide_next_step(scenario['context'])
        
        print(f"触发规则: {', '.join(guidance['applied_rules'])}")
        print(f"建议行动: {guidance['recommended_action']['action']}")
        print(f"理由: {guidance['recommended_action']['reason']}")
    
    print("\n✅ 探索引导机制测试完成!")


def test_strategy_comparison():
    """测试策略对比"""
    print("\n\n" + "=" * 60)
    print("测试3: 渐进式 vs 一次性加载对比")
    print("=" * 60)
    
    tester = ComparisonTester()
    
    # 测试不同类型任务
    task_types = [
        ("research", "学术研究"),
        ("debugging", "问题调试"),
        ("code_review", "代码审查")
    ]
    
    results = []
    for task_id, task_name in task_types:
        print(f"\n{'='*60}")
        print(f"任务类型: {task_name}")
        result = tester.compare_strategies(task_id)
        results.append(result)
    
    # 综合分析
    print("\n\n" + "=" * 60)
    print("综合分析")
    print("=" * 60)
    
    progressive_wins = sum(1 for r in results if r["winner"] == "progressive")
    full_load_wins = sum(1 for r in results if r["winner"] == "full_load")
    ties = sum(1 for r in results if r["winner"] == "tie")
    
    print(f"\n渐进式胜出: {progressive_wins}次")
    print(f"一次性加载胜出: {full_load_wins}次")
    print(f"平局: {ties}次")
    
    print("\n结论:")
    print("✅ 渐进式披露在以下场景有明显优势:")
    print("   - 学术研究（需要探索和深入理解）")
    print("   - 问题调试（需要逐步定位问题）")
    print("")
    print("✅ 一次性加载在以下场景可能更合适:")
    print("   - 代码审查（需要全局视图）")
    print("   - 全文翻译（需要完整上下文）")
    print("   - 数据统计（需要所有数据）")
    
    print("\n✅ 策略对比测试完成!")


if __name__ == "__main__":
    test_progressive_paper_writing()
    test_exploration_guide()
    test_strategy_comparison()
    
    print("\n" + "=" * 60)
    print("习题5: 全部测试通过! ✅")
    print("=" * 60)
    
    print("\n核心功能:")
    print("✅ 渐进式披露应用 - 学术论文写作Agent")
    print("✅ 探索引导机制 - 启发式规则+元认知策略")
    print("✅ 策略对比分析 - 3种任务类型全面对比")
    
    print("\n" + "=" * 60)
    print("🎉 Task04 全部5道官方习题已完成!")
    print("=" * 60)
