"""
Plan-and-Solve Agent 实现
基于 Hello Agents 第四章 4.3 节

核心思想：
1. Planning 阶段：将问题分解为多个步骤的行动计划
2. Solving 阶段：严格按照计划逐步执行

与 ReAct 的区别：
- ReAct: 边想边做，动态调整（像侦探探案）
- Plan-and-Solve: 先谋后动，按蓝图施工（像建筑师）
"""

import os
import ast
from hello_agents_llm import HelloAgentsLLM

# ===========================
# 提示词模板
# ===========================

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


# ===========================
# Planner 规划器
# ===========================

class Planner:
    """负责生成行动计划"""
    
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
    
    def plan(self, question: str) -> list:
        """
        根据用户问题生成一个行动计划
        
        参数:
            question: 用户的问题
            
        返回:
            list: 步骤列表，如 ["步骤1", "步骤2", ...]
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        
        print("\n" + "="*60)
        print("📋 正在生成计划...")
        print("="*60)
        
        response_text = self.llm_client.think(messages=messages) or ""
        
        print(f"\n✅ 计划已生成:\n{response_text}")
        
        # 解析 LLM 输出的列表字符串
        try:
            # 找到 ```python 和 ``` 之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用 ast.literal_eval 安全地将字符串转换为 Python 列表
            plan = ast.literal_eval(plan_str)
            
            if not isinstance(plan, list):
                print("❌ 警告: 解析结果不是列表")
                return []
            
            print(f"\n📝 解析后的计划步骤:")
            for i, step in enumerate(plan, 1):
                print(f"   {i}. {step}")
            
            return plan
            
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {response_text}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []


# ===========================
# Executor 执行器
# ===========================

class Executor:
    """负责按计划逐步执行"""
    
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
    
    def execute(self, question: str, plan: list) -> str:
        """
        根据计划，逐步执行并解决问题
        
        参数:
            question: 原始问题
            plan: 计划步骤列表
            
        返回:
            str: 最终答案
        """
        history = ""  # 用于存储历史步骤和结果的字符串
        
        print("\n" + "="*60)
        print("⚙️  正在执行计划...")
        print("="*60)
        
        for i, step in enumerate(plan):
            print(f"\n{'─'*60}")
            print(f"▶️  正在执行步骤 {i+1}/{len(plan)}")
            print(f"📌 步骤内容: {step}")
            print(f"{'─'*60}")
            
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",  # 第一步历史为空
                current_step=step
            )
            
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages) or ""
            
            # 更新历史记录，为下一步做准备
            history += f"步骤 {i+1}: {step}\n结果: {response_text}\n\n"
            
            print(f"\n✅ 步骤 {i+1} 已完成")
            print(f"📊 结果: {response_text}")
        
        # 循环结束后，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer


# ===========================
# PlanAndSolveAgent 主智能体
# ===========================

class PlanAndSolveAgent:
    """
    Plan-and-Solve 智能体
    
    工作流程:
    1. 调用 Planner 生成计划
    2. 调用 Executor 执行计划
    """
    
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)
    
    def run(self, question: str):
        """
        运行智能体的完整流程: 先规划，后执行
        
        参数:
            question: 用户问题
        """
        print("\n" + "🚀"*30)
        print("开始处理问题")
        print("🚀"*30)
        print(f"\n❓ 问题: {question}\n")
        
        # 1. 调用规划器生成计划
        plan = self.planner.plan(question)
        
        # 检查计划是否成功生成
        if not plan:
            print("\n" + "❌"*30)
            print("任务终止 - 无法生成有效的行动计划")
            print("❌"*30)
            return
        
        # 2. 调用执行器执行计划
        final_answer = self.executor.execute(question, plan)
        
        print("\n" + "🎉"*30)
        print("任务完成")
        print("🎉"*30)
        print(f"\n✨ 最终答案: {final_answer}\n")


# ===========================
# 测试代码
# ===========================

if __name__ == '__main__':
    try:
        # 初始化 LLM 客户端
        llm_client = HelloAgentsLLM()
        
        # 创建 Plan-and-Solve Agent
        agent = PlanAndSolveAgent(llm_client)
        
        # 测试问题：课程中的数学应用题
        question = """
        一个水果店周一卖出了15个苹果。
        周二卖出的苹果数量是周一的两倍。
        周三卖出的数量比周二少了5个。
        请问这三天总共卖出了多少个苹果？
        """
        
        # 运行 Agent
        agent.run(question.strip())
        
    except ValueError as e:
        print(f"❌ 错误: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
