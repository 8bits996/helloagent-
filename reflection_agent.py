"""
Reflection Agent 实现
基于 Hello Agents 第四章 4.4 节

核心思想：
通过"执行-反思-优化"的迭代循环，持续提升解决方案质量

工作流程：
1. Execution（执行）：生成初始方案
2. Reflection（反思）：批判性审视，发现问题
3. Refinement（优化）：根据反馈改进方案
4. 重复2-3步，直到无需改进或达到最大迭代次数

类比：
- 华为/军队的蓝军机制
- 代码的Code Review流程
- 批评与自我批评
"""

import os
from hello_agents_llm import HelloAgentsLLM
from memory import Memory


# ===========================
# 提示词模板
# ===========================

# 1. 初始执行提示词
INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""


# 2. 反思提示词（扮演严格的代码评审员）
REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在**算法效率**上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种**算法上更优**的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答"无需改进"。

请直接输出你的反馈，不要包含任何额外的解释。
"""


# 3. 优化提示词
REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
```python
{last_code_attempt}
```

# 评审员的反馈:
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

请直接输出优化后的代码，不要包含任何额外的解释。
"""


# ===========================
# ReflectionAgent 主智能体
# ===========================

class ReflectionAgent:
    """
    Reflection 智能体
    
    工作流程：
    1. 初始执行：生成初版方案
    2. 迭代循环：
       a. 反思：评审当前方案
       b. 检查：是否需要改进
       c. 优化：生成改进版本
    3. 输出最终优化后的方案
    """
    
    def __init__(self, llm_client: HelloAgentsLLM, max_iterations: int = 3):
        """
        初始化 Reflection Agent
        
        参数:
            llm_client: LLM 客户端
            max_iterations: 最大迭代次数（防止无限循环）
        """
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations
    
    def run(self, task: str):
        """
        运行 Reflection 智能体来完成任务
        
        参数:
            task: 任务描述
            
        返回:
            str: 最终优化后的代码
        """
        print("\n" + "🎯"*30)
        print("开始处理任务")
        print("🎯"*30)
        print(f"\n📋 任务: {task}\n")
        
        # ===========================
        # 阶段1: 初始执行
        # ===========================
        print("\n" + "="*60)
        print("🚀 阶段1: 初始执行（生成初版方案）")
        print("="*60)
        
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        
        # 清理代码（去除可能的markdown标记）
        initial_code = self._clean_code(initial_code)
        
        self.memory.add_record("execution", initial_code)
        
        print(f"\n✅ 初版代码已生成")
        print(f"📊 代码预览:\n```python\n{initial_code[:200]}...\n```")
        
        # ===========================
        # 阶段2: 迭代循环（反思-优化）
        # ===========================
        for iteration in range(self.max_iterations):
            print("\n" + "="*60)
            print(f"🔄 第 {iteration + 1}/{self.max_iterations} 轮迭代")
            print("="*60)
            
            # --- 步骤 a: 反思 ---
            print("\n▶️  步骤1: 反思（蓝军审查）")
            print("─"*60)
            
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(
                task=task,
                code=last_code
            )
            feedback = self._get_llm_response(reflect_prompt)
            
            self.memory.add_record("reflection", feedback)
            
            print(f"\n💬 评审反馈:\n{feedback[:300]}...")
            
            # --- 步骤 b: 检查是否需要停止 ---
            if "无需改进" in feedback or "已经最优" in feedback or "无法进一步优化" in feedback:
                print("\n" + "✅"*30)
                print("反思认为代码已达最优，迭代结束")
                print("✅"*30)
                break
            
            # --- 步骤 c: 优化 ---
            print("\n▶️  步骤2: 优化（根据反馈改进）")
            print("─"*60)
            
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            
            # 清理代码
            refined_code = self._clean_code(refined_code)
            
            self.memory.add_record("execution", refined_code)
            
            print(f"\n✅ 优化后的代码已生成")
            print(f"📊 代码预览:\n```python\n{refined_code[:200]}...\n```")
        
        # ===========================
        # 阶段3: 输出最终结果
        # ===========================
        final_code = self.memory.get_last_execution()
        
        print("\n" + "🎉"*30)
        print("任务完成")
        print("🎉"*30)
        
        print(f"\n📈 迭代统计:")
        counts = self.memory.get_record_count()
        print(f"   - 执行次数: {counts['execution']}")
        print(f"   - 反思次数: {counts['reflection']}")
        print(f"   - 总迭代轮数: {counts['reflection']}")
        
        print(f"\n✨ 最终优化后的代码:\n")
        print("```python")
        print(final_code)
        print("```")
        
        return final_code
    
    def _get_llm_response(self, prompt: str) -> str:
        """
        辅助方法：调用LLM并获取完整的流式响应
        
        参数:
            prompt: 提示词
            
        返回:
            str: LLM的响应文本
        """
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""
        return response_text
    
    def _clean_code(self, code: str) -> str:
        """
        清理代码：去除可能的markdown标记
        
        参数:
            code: 原始代码
            
        返回:
            str: 清理后的代码
        """
        # 去除 ```python 和 ``` 标记
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()


# ===========================
# 测试代码
# ===========================

if __name__ == '__main__':
    try:
        # 初始化 LLM 客户端
        llm_client = HelloAgentsLLM()
        
        # 创建 Reflection Agent
        agent = ReflectionAgent(llm_client, max_iterations=2)
        
        # 测试任务：课程中的素数查找问题
        task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
        
        # 运行 Agent
        final_code = agent.run(task)
        
        # 可选：测试生成的代码
        print("\n" + "="*60)
        print("🧪 测试生成的代码")
        print("="*60)
        
        # 这里可以添加代码测试逻辑
        # 例如：exec(final_code) 然后调用函数
        
    except ValueError as e:
        print(f"❌ 错误: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
