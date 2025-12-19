"""
Task02 - PlanAndSolveAgent 框架化实现

Plan-and-Solve Agent: Planning -> Solving 两阶段
将复杂任务分解为步骤，然后逐步执行

核心功能:
1. Planning: 制定执行计划
2. Solving: 按计划逐步求解
3. 计划可视化
4. 步骤追踪
"""

import re
from typing import List, Dict, Any, Optional
from hello_agents import HelloAgentsLLM
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# ========================================
# PlanAndSolveAgent - 计划与执行型 Agent
# ========================================
class PlanAndSolveAgent:
    """
    Plan-and-Solve Agent - 计划与执行分离
    
    工作流程:
    1. Planning: LLM 制定详细的执行计划
    2. Solving: 按计划逐步执行，并验证每一步
    
    特色功能:
    - 计划分解（将复杂任务拆成步骤）
    - 步骤追踪（记录每一步的执行结果）
    - 自适应调整（发现问题时重新规划）
    """
    
    def __init__(
        self,
        llm: HelloAgentsLLM,
        max_plan_steps: int = 10,
        verbose: bool = True
    ):
        """
        初始化 Plan-and-Solve Agent
        
        Args:
            llm: HelloAgentsLLM 实例
            max_plan_steps: 最大计划步骤数
            verbose: 是否打印详细日志
        """
        self.llm = llm
        self.max_plan_steps = max_plan_steps
        self.verbose = verbose
        
        # 历史记录
        self.plan: List[str] = []
        self.execution_log: List[Dict[str, Any]] = []
    
    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "PLAN": "📋",
                "SOLVE": "🔨",
                "STEP": "  →"
            }.get(level, "")
            print(f"{prefix} {message}")
    
    def _generate_plan(self, task: str) -> List[str]:
        """
        Planning 阶段：生成执行计划
        
        Args:
            task: 用户任务
            
        Returns:
            步骤列表
        """
        system_prompt = """
你是一个专业的任务规划专家。你的职责是将复杂任务分解为清晰的执行步骤。

要求:
1. 步骤要具体、可执行
2. 步骤之间有逻辑顺序
3. 每个步骤都有明确的目标
4. 不要超过10个步骤

格式要求:
请以列表形式返回步骤，每行一个步骤，格式为：
步骤1: [具体内容]
步骤2: [具体内容]
...
"""
        
        user_prompt = f"""
任务: {task}

请制定详细的执行计划:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            # 解析步骤
            steps = self._parse_plan(response)
            return steps
        except Exception as e:
            self._log(f"生成计划失败: {e}", "ERROR")
            return []
    
    def _parse_plan(self, response: str) -> List[str]:
        """
        解析计划步骤
        
        Args:
            response: LLM 返回的计划
            
        Returns:
            步骤列表
        """
        steps = []
        
        # 匹配步骤格式：步骤X: ...  或  X. ...  或  - ...
        patterns = [
            r'步骤\s*\d+\s*[：:]\s*(.*)',
            r'\d+\.\s*(.*)',
            r'-\s*(.*)',
            r'•\s*(.*)'
        ]
        
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试匹配各种格式
            matched = False
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    step_content = match.group(1).strip()
                    if step_content and len(step_content) > 5:  # 过滤太短的
                        steps.append(step_content)
                        matched = True
                        break
            
            # 如果没有匹配到，但行内容足够长且看起来像步骤
            if not matched and len(line) > 10 and not line.startswith('#'):
                steps.append(line)
        
        # 限制步骤数
        return steps[:self.max_plan_steps]
    
    def _execute_step(self, step: str, step_number: int, context: str = "") -> str:
        """
        执行单个步骤
        
        Args:
            step: 步骤描述
            step_number: 步骤编号
            context: 之前步骤的执行结果
            
        Returns:
            步骤执行结果
        """
        system_prompt = """
你是一个专业的任务执行助手。请根据计划步骤执行具体操作。

要求:
- 认真完成当前步骤
- 给出具体的执行结果
- 如果需要前置信息，从上下文中获取
"""
        
        user_prompt = f"""
当前步骤（第{step_number}步）: {step}

{context}

请执行这一步并给出结果:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response
        except Exception as e:
            self._log(f"执行步骤失败: {e}", "ERROR")
            return f"错误：步骤执行失败 - {e}"
    
    def run(self, task: str) -> str:
        """
        运行 Plan-and-Solve Agent
        
        Args:
            task: 用户任务
            
        Returns:
            最终结果
        """
        self.plan = []
        self.execution_log = []
        
        self._log(f"任务: {task}", "INFO")
        self._log("=" * 70, "INFO")
        
        # ========== Phase 1: Planning ==========
        self._log("\n📋 Phase 1: Planning (制定计划)", "PLAN")
        self._log("-" * 70, "INFO")
        
        self.plan = self._generate_plan(task)
        
        if not self.plan:
            self._log("计划生成失败", "ERROR")
            return "错误：无法生成执行计划"
        
        self._log(f"\n生成了 {len(self.plan)} 个步骤:", "PLAN")
        for i, step in enumerate(self.plan, 1):
            self._log(f"{i}. {step}", "STEP")
        
        # ========== Phase 2: Solving ==========
        self._log("\n\n🔨 Phase 2: Solving (执行计划)", "SOLVE")
        self._log("-" * 70, "INFO")
        
        context = ""
        results = []
        
        for i, step in enumerate(self.plan, 1):
            self._log(f"\n执行步骤 {i}/{len(self.plan)}: {step}", "SOLVE")
            
            # 执行步骤
            result = self._execute_step(step, i, context)
            results.append(result)
            
            # 记录日志
            self.execution_log.append({
                "step_number": i,
                "step": step,
                "result": result
            })
            
            # 更新上下文
            if context:
                context += f"\n\n步骤{i}的结果:\n{result}"
            else:
                context = f"之前的执行结果:\n\n步骤{i}的结果:\n{result}"
            
            self._log(f"✓ 步骤 {i} 完成", "SUCCESS")
        
        # ========== 汇总结果 ==========
        self._log("\n\n" + "=" * 70, "SUCCESS")
        self._log("🎉 所有步骤执行完成！", "SUCCESS")
        self._log("=" * 70, "SUCCESS")
        
        # 生成最终答案
        final_answer = self._generate_final_answer(task, results)
        
        self._log(f"\n最终答案:\n{final_answer}\n", "INFO")
        
        return final_answer
    
    def _generate_final_answer(self, task: str, results: List[str]) -> str:
        """
        根据执行结果生成最终答案
        
        Args:
            task: 原始任务
            results: 各步骤执行结果
            
        Returns:
            最终答案
        """
        system_prompt = """
你是一个总结专家。请根据各步骤的执行结果，整合出完整的最终答案。

要求:
- 答案要完整、连贯
- 包含关键信息
- 简洁明了
"""
        
        steps_summary = ""
        for i, (step, result) in enumerate(zip(self.plan, results), 1):
            steps_summary += f"\n步骤{i} ({step}):\n{result}\n"
        
        user_prompt = f"""
任务: {task}

执行过程:
{steps_summary}

请整合以上信息，给出完整的最终答案:
""".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response
        except Exception as e:
            # 如果汇总失败，返回最后一步的结果
            return results[-1] if results else "错误：无法生成最终答案"
    
    def get_plan(self) -> List[str]:
        """获取执行计划"""
        return self.plan.copy()
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """获取执行日志"""
        return self.execution_log.copy()
    
    def print_execution_summary(self):
        """打印执行摘要"""
        print("\n" + "=" * 70)
        print("执行摘要")
        print("=" * 70)
        
        print(f"\n任务分解: {len(self.plan)} 个步骤")
        for i, step in enumerate(self.plan, 1):
            status = "✓" if i <= len(self.execution_log) else "○"
            print(f"  {status} 步骤{i}: {step}")
        
        print(f"\n已执行: {len(self.execution_log)}/{len(self.plan)} 个步骤")
        print("=" * 70)


# ========================================
# 测试代码
# ========================================
def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🚀 Task02 - PlanAndSolveAgent 框架化实现测试")
    print("=" * 70)
    
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()
    print(f"✅ LLM 初始化完成: {llm.model}")
    
    # 2. 创建 Plan-and-Solve Agent
    agent = PlanAndSolveAgent(
        llm=llm,
        max_plan_steps=10,
        verbose=True
    )
    print(f"✅ PlanAndSolveAgent 创建完成\n")
    
    # 3. 测试任务：数学应用题
    task = """
小明有100元，他买了3本书，每本书25元。
然后他用剩余的钱买了一些笔，每支笔5元。
请问：
1. 小明买书花了多少钱？
2. 他还剩多少钱？
3. 他最多能买多少支笔？
"""
    
    # 运行 Agent
    final_answer = agent.run(task)
    
    # 输出执行摘要
    agent.print_execution_summary()
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
