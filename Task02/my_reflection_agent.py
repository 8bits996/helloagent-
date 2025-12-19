"""
Task02 - ReflectionAgent 框架化实现

Reflection Agent: Execute -> Reflect -> Refine 循环
通过自我反思和评分机制迭代优化输出质量

核心功能:
1. 初步生成答案（Execute）
2. LLM 自我评估（Reflect）
3. 基于反思改进（Refine）
4. 质量评分机制
"""

import re
from typing import List, Dict, Any, Optional
from hello_agents import HelloAgentsLLM
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# ========================================
# ReflectionAgent - 反思型 Agent
# ========================================
class ReflectionAgent:
    """
    Reflection Agent - 通过反思迭代优化输出
    
    工作流程:
    1. Execute: 生成初步答案
    2. Reflect: LLM 对答案进行自我评估
    3. Refine: 基于反思改进答案
    4. Repeat: 循环直到达到质量阈值或最大次数
    
    特色功能:
    - 质量评分机制 (0-100分)
    - 反思历史记录
    - 可配置质量阈值
    """
    
    def __init__(
        self,
        llm: HelloAgentsLLM,
        max_iterations: int = 3,
        quality_threshold: float = 80.0,
        verbose: bool = True
    ):
        """
        初始化 Reflection Agent
        
        Args:
            llm: HelloAgentsLLM 实例
            max_iterations: 最大迭代次数
            quality_threshold: 质量阈值 (0-100)，达到后停止迭代
            verbose: 是否打印详细日志
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.verbose = verbose
        
        # 历史记录
        self.execution_history: List[Dict[str, Any]] = []
    
    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "EXECUTE": "🏃",
                "REFLECT": "🤔",
                "REFINE": "🔧",
                "SCORE": "📊"
            }.get(level, "")
            print(f"{prefix} {message}")
    
    def _execute(self, task: str, context: str = "") -> str:
        """
        Execute 阶段：生成初步答案
        
        Args:
            task: 用户任务
            context: 上下文信息（之前的反思和改进）
            
        Returns:
            生成的答案
        """
        system_prompt = """
你是一个专业的问题解决助手。你的任务是为用户提供高质量的答案。

请注意:
- 答案要准确、完整
- 逻辑要清晰
- 表达要简洁
"""
        
        user_prompt = f"""
任务: {task}

{context}

请提供你的答案:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response
        except Exception as e:
            self._log(f"Execute 失败: {e}", "ERROR")
            return ""
    
    def _reflect(self, task: str, answer: str) -> Dict[str, Any]:
        """
        Reflect 阶段：LLM 自我评估
        
        Args:
            task: 原始任务
            answer: 当前答案
            
        Returns:
            {
                "score": 0-100 的质量评分,
                "strengths": 优点列表,
                "weaknesses": 缺点列表,
                "suggestions": 改进建议
            }
        """
        system_prompt = """
你是一个严格的评审专家。请对给定的答案进行客观评估。

评估标准:
1. 准确性 (30分): 信息是否正确
2. 完整性 (30分): 是否全面回答问题
3. 清晰性 (20分): 逻辑是否清晰
4. 简洁性 (20分): 表达是否简洁

请以JSON格式返回评估结果:
{
  "score": 85,
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "suggestions": "具体的改进建议"
}
"""
        
        user_prompt = f"""
任务: {task}

答案:
{answer}

请评估这个答案（返回JSON格式）:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            # 尝试解析JSON
            reflection = self._parse_reflection(response)
            return reflection
        except Exception as e:
            self._log(f"Reflect 失败: {e}", "ERROR")
            return {
                "score": 50.0,
                "strengths": [],
                "weaknesses": ["评估失败"],
                "suggestions": "无法生成改进建议"
            }
    
    def _parse_reflection(self, response: str) -> Dict[str, Any]:
        """
        解析反思结果（JSON格式）
        
        Args:
            response: LLM 返回的反思内容
            
        Returns:
            解析后的字典
        """
        import json
        
        # 尝试直接解析JSON
        try:
            # 提取JSON部分（可能包含在```json```中）
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试找到 { ... } 部分
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response
            
            reflection = json.loads(json_str)
            
            # 验证必需字段
            if "score" not in reflection:
                reflection["score"] = 70.0
            if "strengths" not in reflection:
                reflection["strengths"] = []
            if "weaknesses" not in reflection:
                reflection["weaknesses"] = []
            if "suggestions" not in reflection:
                reflection["suggestions"] = "继续改进"
            
            return reflection
            
        except json.JSONDecodeError:
            # JSON解析失败，尝试从文本中提取信息
            self._log("JSON 解析失败，使用文本解析", "INFO")
            
            # 提取评分
            score_match = re.search(r'score["\']?\s*:\s*(\d+)', response)
            score = float(score_match.group(1)) if score_match else 70.0
            
            return {
                "score": score,
                "strengths": [],
                "weaknesses": [],
                "suggestions": response
            }
    
    def _refine(self, task: str, answer: str, reflection: Dict[str, Any]) -> str:
        """
        Refine 阶段：基于反思改进答案
        
        Args:
            task: 原始任务
            answer: 当前答案
            reflection: 反思结果
            
        Returns:
            改进后的答案
        """
        system_prompt = """
你是一个专业的内容优化专家。请根据评审意见改进答案。

要求:
- 保留原答案的优点
- 针对性解决指出的问题
- 提升整体质量
"""
        
        suggestions = reflection.get("suggestions", "")
        weaknesses = reflection.get("weaknesses", [])
        
        user_prompt = f"""
任务: {task}

当前答案:
{answer}

评审意见:
- 评分: {reflection.get('score', 0)}分
- 缺点: {', '.join(weaknesses) if weaknesses else '无'}
- 改进建议: {suggestions}

请提供改进后的答案:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response
        except Exception as e:
            self._log(f"Refine 失败: {e}", "ERROR")
            return answer  # 返回原答案
    
    def run(self, task: str) -> str:
        """
        运行 Reflection Agent
        
        Args:
            task: 用户任务
            
        Returns:
            最终优化后的答案
        """
        self.execution_history = []
        
        self._log(f"任务: {task}", "INFO")
        self._log("=" * 70, "INFO")
        
        current_answer = ""
        context = ""
        
        for iteration in range(1, self.max_iterations + 1):
            self._log(f"\n🔄 迭代 {iteration}/{self.max_iterations}", "INFO")
            self._log("-" * 70, "INFO")
            
            # 1. Execute: 生成答案
            self._log("Execute: 生成答案...", "EXECUTE")
            current_answer = self._execute(task, context)
            self._log(f"\n生成的答案:\n{current_answer}\n", "EXECUTE")
            
            # 2. Reflect: 自我评估
            self._log("Reflect: 自我评估...", "REFLECT")
            reflection = self._reflect(task, current_answer)
            
            score = reflection.get("score", 0)
            strengths = reflection.get("strengths", [])
            weaknesses = reflection.get("weaknesses", [])
            suggestions = reflection.get("suggestions", "")
            
            self._log(f"\n评估结果:", "SCORE")
            self._log(f"  评分: {score}/100", "SCORE")
            if strengths:
                self._log(f"  优点: {', '.join(strengths)}", "SCORE")
            if weaknesses:
                self._log(f"  缺点: {', '.join(weaknesses)}", "SCORE")
            self._log(f"  建议: {suggestions}\n", "SCORE")
            
            # 记录历史
            self.execution_history.append({
                "iteration": iteration,
                "answer": current_answer,
                "reflection": reflection
            })
            
            # 3. 检查是否达到质量阈值
            if score >= self.quality_threshold:
                self._log(f"✅ 达到质量阈值 {self.quality_threshold}，停止迭代", "SUCCESS")
                break
            
            # 4. Refine: 改进答案（如果还有迭代次数）
            if iteration < self.max_iterations:
                self._log("Refine: 改进答案...", "REFINE")
                
                # 构建上下文
                context = f"""
之前的答案:
{current_answer}

评审反馈:
- 评分: {score}/100
- 需要改进: {', '.join(weaknesses) if weaknesses else '无'}
- 改进建议: {suggestions}

请在之前答案的基础上进行改进。
""".strip()
        
        # 返回最终答案
        self._log("\n" + "=" * 70, "SUCCESS")
        self._log("🎉 迭代完成！", "SUCCESS")
        self._log("=" * 70, "SUCCESS")
        self._log(f"\n最终答案:\n{current_answer}\n", "RESULT")
        
        return current_answer
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def get_improvement_summary(self) -> str:
        """获取改进摘要"""
        if not self.execution_history:
            return "无执行历史"
        
        summary = "改进历程:\n"
        for record in self.execution_history:
            iteration = record["iteration"]
            score = record["reflection"].get("score", 0)
            summary += f"  迭代 {iteration}: 评分 {score}/100\n"
        
        # 计算改进幅度
        if len(self.execution_history) > 1:
            first_score = self.execution_history[0]["reflection"].get("score", 0)
            last_score = self.execution_history[-1]["reflection"].get("score", 0)
            improvement = last_score - first_score
            summary += f"\n总改进: {improvement:+.1f} 分"
        
        return summary


# ========================================
# 测试代码
# ========================================
def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🚀 Task02 - ReflectionAgent 框架化实现测试")
    print("=" * 70)
    
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()
    print(f"✅ LLM 初始化完成: {llm.model}")
    
    # 2. 创建 Reflection Agent
    agent = ReflectionAgent(
        llm=llm,
        max_iterations=3,
        quality_threshold=85.0,  # 85分以上停止
        verbose=True
    )
    print(f"✅ ReflectionAgent 创建完成\n")
    
    # 3. 测试任务：素数优化
    task = """
编写一个Python函数，判断一个数是否为素数。
要求：高效、代码简洁、有注释。
"""
    
    # 运行 Agent
    final_answer = agent.run(task)
    
    # 输出改进摘要
    print("\n" + "=" * 70)
    print(agent.get_improvement_summary())
    print("=" * 70)
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
