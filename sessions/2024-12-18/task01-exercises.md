# Task01 习题解答

**学习者**: frankechen  
**日期**: 2024-12-18  
**章节**: 第四章 - 智能体经典范式构建  

---

## 习题1: 三种范式的综合分析

### Q1.1: 三种范式在"思考"与"行动"组织方式上的本质区别？

**答案**:

| 范式 | 思考与行动的组织方式 | 核心特征 |
|------|-------------------|---------|
| **ReAct** | **交织式**：思考与行动紧密耦合，形成 Thought→Action→Observation 循环 | 每一步的思考都会立即转化为行动，行动结果又会影响下一步思考 |
| **Plan-and-Solve** | **分离式**：思考（Planning）与行动（Solving）明确分为两个独立阶段 | 所有思考在规划阶段一次性完成，执行阶段不再重新思考 |
| **Reflection** | **迭代式**：先行动，再反思，基于反思优化行动，形成循环 | 思考分为两种：初始执行前的思考 + 事后反思性思考 |

**本质区别**:
- **ReAct**: 思考指导行动，行动修正思考（实时反馈）
- **Plan-and-Solve**: 思考先于行动，行动严格执行思考结果（预先规划）
- **Reflection**: 行动后的思考比行动前的思考更重要（事后复盘）

---

### Q1.2: 智能家居控制助手应该选择哪种范式？

**场景分析**:
- 需要控制多个设备（灯光、空调、窗帘）
- 需要根据用户习惯自动调节
- 环境因素动态变化（温度、光线、时间）

**我的选择**: **ReAct 范式**

**理由**:

1. **环境不确定性高**
   - 用户需求随时变化
   - 环境参数实时波动（温度、光照等）
   - 需要根据传感器反馈动态调整
   - → ReAct 的"观察-调整"机制最适合

2. **需要工具协同**
   - 需要调用多个设备API（灯光控制、空调控制、窗帘控制）
   - 需要读取传感器数据（温度传感器、光线传感器）
   - → ReAct 的工具系统天然支持

3. **决策需要实时反馈**
   ```
   Thought: "用户说太热了"
   Action: get_temperature() → 观察到28°C
   
   Thought: "28°C确实偏高，降低空调温度"
   Action: set_ac_temperature(24) → 观察到设置成功
   
   Thought: "空调已调整，检查是否需要开窗帘"
   Action: get_light_level() → 观察到光线充足
   
   Thought: "光线足够，不需要开窗帘"
   Action: Finish["已将空调调至24°C"]
   ```

**为什么不选其他范式**:

- **Plan-and-Solve**: 不适合，因为：
  - 家居控制场景难以预先规划完整步骤
  - 用户需求和环境变化难以预测
  - 缺乏灵活性

- **Reflection**: 不适合，因为：
  - 家居控制需要快速响应，不能等待多轮优化
  - "先错一次再改进"的模式用户体验不好
  - 实时性要求高

---

### Q1.3: 是否可以组合使用？请设计混合架构

**答案**: 可以！

**混合架构方案1**: **ReAct + Reflection**

**场景**: 智能客服系统

```
第一阶段（ReAct）: 快速响应用户
  Thought: "用户询问退款政策"
  Action: search_policy("退款")
  Observation: "7天无理由退货..."
  
  Thought: "找到政策，生成回复"
  Action: generate_response(policy)
  Observation: 初版回复生成
  
第二阶段（Reflection）: 优化回复质量
  Reflection: "回复是否友好？是否符合公司利益？"
  Refinement: 优化后的最终回复
```

**优势**: 既保证快速响应，又确保高质量输出

---

**混合架构方案2**: **Plan-and-Solve + Reflection**

**场景**: 战略规划助手

```
第一阶段（Plan-and-Solve）: 生成战略规划
  Planning: 分解为["市场分析", "目标设定", "策略制定", ...]
  Solving: 逐步执行，生成初版战略文档
  
第二阶段（Reflection）: 蓝军审查
  Reflection: 
    - 逻辑是否自洽？
    - 数据是否支撑？
    - 可行性如何？
  Refinement: 优化战略文档
```

**优势**: 既保证结构完整性，又确保质量卓越

---

**混合架构方案3**: **三者结合**

**场景**: 智能研发助手

```
阶段1（ReAct）: 探索可行方案
  - 搜索技术文档
  - 调研开源方案
  - 评估技术栈
  → 输出：可行性报告

阶段2（Plan-and-Solve）: 制定实施计划
  - Planning: 分解开发步骤
  - Solving: 逐步实现功能
  → 输出：初版代码

阶段3（Reflection）: 代码审查优化
  - Reflection: 代码质量、性能、安全性
  - Refinement: 优化到生产级别
  → 输出：高质量代码
```

**适用场景**: 复杂、高质量要求、多阶段的综合任务

---

## 习题2: ReAct 输出解析的鲁棒性

### Q2.1: 当前正则表达式解析的脆弱性？

**答案**:

**潜在脆弱性**:

1. **格式微小变化导致失败**
   ```python
   # 正则: r"Thought: (.*)"
   
   ✅ 能解析: "Thought: 我需要搜索"
   ❌ 无法解析: "Thought:我需要搜索" (缺少空格)
   ❌ 无法解析: "thought: 我需要搜索" (大小写)
   ❌ 无法解析: "Thought : 我需要搜索" (多余空格)
   ```

2. **多行输出问题**
   ```python
   # LLM输出:
   """
   Thought: 我需要执行以下操作：
   1. 先搜索
   2. 再分析
   Action: Search[...]
   """
   
   # 正则可能只匹配到第一行
   ```

3. **特殊字符问题**
   ```python
   # Action: Search[C++ vs Python性能对比]
   # 方括号、特殊符号可能导致解析失败
   ```

4. **LLM不遵循格式**
   ```python
   # LLM可能输出:
   "我觉得应该先搜索一下，然后..."
   # 完全没有 Thought: 标记
   ```

---

### Q2.2: 更鲁棒的输出解析方案？

**答案**:

**方案1: JSON格式化输出** ⭐ 推荐

```python
# 提示词要求
"""
请严格按照以下JSON格式输出：
{
  "thought": "你的思考过程",
  "action": {
    "name": "工具名称",
    "input": "工具输入"
  }
}
"""

# 解析代码
import json

def parse_json_output(text):
    try:
        result = json.loads(text)
        return result['thought'], result['action']
    except:
        return None, None
```

**优势**:
- ✅ 结构化，易于解析
- ✅ 不受空格、换行影响
- ✅ 可以包含复杂嵌套结构

**劣势**:
- ❌ LLM可能生成非法JSON
- ❌ 需要更严格的提示词约束

---

**方案2: XML格式化输出**

```python
# 提示词要求
"""
<response>
  <thought>你的思考</thought>
  <action>
    <name>工具名称</name>
    <input>工具输入</input>
  </action>
</response>
"""

# 解析代码
import xml.etree.ElementTree as ET

def parse_xml_output(text):
    root = ET.fromstring(text)
    thought = root.find('thought').text
    action_name = root.find('action/name').text
    action_input = root.find('action/input').text
    return thought, (action_name, action_input)
```

---

**方案3: Markdown标记** (平衡方案)

```python
# 提示词要求
"""
## Thought
你的思考过程

## Action
- Tool: 工具名称
- Input: 工具输入
"""

# 解析代码
def parse_markdown_output(text):
    thought = extract_section(text, "## Thought", "## Action")
    action = extract_section(text, "## Action", None)
    return thought, parse_action(action)
```

---

**方案4: Few-shot示例约束** (增强现有方案)

```python
PROMPT_WITH_EXAMPLES = """
你是一个智能助手。请严格按照以下格式输出：

示例1:
Thought: 我需要查询天气
Action: get_weather[北京]

示例2:
Thought: 我需要搜索信息
Action: Search[人工智能发展历史]

现在请处理用户问题：{question}
"""
```

**优势**: 通过示例强化格式遵循

---

### Q2.3: 实践对比（建议实现）

**任务**: 修改 `first_agent_test.py`，对比两种解析方案

**实现建议**:
```python
# 原方案（正则）
def parse_regex(text):
    thought = re.search(r"Thought: (.*)", text)
    action = re.search(r"Action: (.*)", text)
    return thought, action

# 新方案（JSON）
def parse_json(text):
    # 提取```json```之间的内容
    json_str = extract_json_block(text)
    return json.loads(json_str)

# 对比测试
test_cases = [
    "标准格式",
    "缺少空格",
    "多余换行",
    "特殊字符"
]

for case in test_cases:
    print(f"正则成功率: {test_regex(case)}")
    print(f"JSON成功率: {test_json(case)}")
```

---

## 习题3: 工具调用扩展实践

### Q3.1: 为ReAct添加计算器工具

**实现**:

```python
def calculator(expression: str) -> str:
    """
    一个安全的计算器工具
    
    参数:
        expression: 数学表达式，如 "(123 + 456) * 789 / 12"
    
    返回:
        str: 计算结果
    """
    try:
        # 安全评估：只允许数学运算
        allowed_chars = set("0123456789+-*/()%. ")
        if not all(c in allowed_chars for c in expression):
            return "错误: 表达式包含非法字符"
        
        # 使用eval计算（在受控环境中）
        result = eval(expression)
        return f"{expression} = {result}"
    
    except ZeroDivisionError:
        return "错误: 除数不能为零"
    except Exception as e:
        return f"错误: 计算失败 - {e}"

# 注册到ToolExecutor
toolExecutor.registerTool(
    name="Calculator",
    description="一个数学计算器。当需要进行数学计算时使用，支持加减乘除和括号。输入格式: '(123 + 456) * 789 / 12'",
    func=calculator
)
```

**测试案例**:
```python
question = "计算 (123 + 456) × 789 ÷ 12 的结果是多少？"

# ReAct 会这样工作:
"""
Thought: 需要进行数学计算
Action: Calculator[(123 + 456) * 789 / 12]
Observation: (123 + 456) * 789 / 12 = 38072.25

Thought: 已获得计算结果
Action: Finish[计算结果是 38072.25]
"""
```

---

### Q3.2: 工具选择失败的处理机制

**设计方案**:

```python
class SmartToolExecutor(ToolExecutor):
    def __init__(self):
        super().__init__()
        self.failure_history = []  # 记录失败历史
        self.max_retries = 3
    
    def execute_with_retry(self, tool_name, tool_input, context):
        """
        带重试的工具执行
        
        失败类型:
        1. 工具不存在
        2. 参数格式错误
        3. 工具执行失败
        """
        
        # 检查失败次数
        if self._get_failure_count(tool_name) >= self.max_retries:
            return self._generate_guidance(tool_name, context)
        
        # 尝试执行
        tool_func = self.getTool(tool_name)
        
        if tool_func is None:
            # 工具不存在 - 提供相似工具建议
            self.failure_history.append({
                'type': 'tool_not_found',
                'tool': tool_name
            })
            return self._suggest_similar_tools(tool_name)
        
        try:
            result = tool_func(tool_input)
            # 成功 - 清除失败记录
            self._clear_failures(tool_name)
            return result
        
        except Exception as e:
            # 执行失败 - 提供错误引导
            self.failure_history.append({
                'type': 'execution_error',
                'tool': tool_name,
                'error': str(e)
            })
            return self._generate_error_guidance(tool_name, e)
    
    def _suggest_similar_tools(self, wrong_name):
        """基于相似度推荐正确工具"""
        available_tools = list(self.tools.keys())
        
        # 简单的字符串相似度
        similarities = [
            (tool, self._similarity(wrong_name, tool))
            for tool in available_tools
        ]
        
        best_match = max(similarities, key=lambda x: x[1])
        
        return f"""
错误: 工具 '{wrong_name}' 不存在。

你是想使用 '{best_match[0]}' 吗？

可用工具列表:
{self.getAvailableTools()}

请检查工具名称拼写并重试。
"""
    
    def _generate_error_guidance(self, tool_name, error):
        """生成错误引导信息"""
        tool_desc = self.tools[tool_name]['description']
        
        return f"""
工具 '{tool_name}' 执行失败。

错误信息: {error}

工具说明: {tool_desc}

常见问题:
1. 检查输入格式是否正确
2. 确认参数是否完整
3. 查看工具描述了解正确用法

请修正后重试。
"""
    
    def _get_failure_count(self, tool_name):
        """获取某个工具的失败次数"""
        return sum(
            1 for f in self.failure_history 
            if f.get('tool') == tool_name
        )
    
    def _similarity(self, s1, s2):
        """计算字符串相似度（简化版）"""
        # 可以使用 Levenshtein距离 或其他算法
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
```

**使用示例**:
```python
# 错误1: 工具名拼写错误
Action: Serach[北京天气]  # 正确应该是 Search

# 系统响应:
"""
错误: 工具 'Serach' 不存在。
你是想使用 'Search' 吗？(相似度: 0.91)

可用工具列表:
- Search: 网页搜索引擎
- Calculator: 数学计算器
...
"""

# 错误2: 参数格式错误
Action: Calculator[一百加二百]  # 应该是数字

# 系统响应:
"""
工具 'Calculator' 执行失败。
错误信息: 表达式包含非法字符

工具说明: 支持数学运算，输入格式: '(123 + 456) * 789 / 12'

常见问题:
1. 使用数字而非文字
2. 使用英文运算符 + - * /
3. 检查括号是否匹配
"""
```

---

### Q3.3: 大规模工具管理（50-100个工具）

**问题分析**:

当工具数量达到50-100个时：
- ❌ 提示词过长（超出上下文窗口）
- ❌ LLM难以准确选择工具
- ❌ 工具描述冗余、混淆

**解决方案**:

**方案1: 工具分类与动态加载** ⭐

```python
class HierarchicalToolExecutor:
    def __init__(self):
        self.tool_categories = {
            'search': ['Search', 'WebSearch', 'DatabaseSearch'],
            'compute': ['Calculator', 'StatCalculator', 'UnitConverter'],
            'data': ['ReadFile', 'WriteFile', 'QueryDB'],
            'communication': ['SendEmail', 'SendSMS', 'PostAPI'],
            # ... 更多分类
        }
        self.all_tools = {}
    
    def get_relevant_tools(self, query, top_k=5):
        """
        根据查询动态选择最相关的工具
        
        步骤:
        1. 分析查询意图 → 确定可能的类别
        2. 在相关类别中检索工具
        3. 只返回top_k个最相关工具
        """
        # 1. 意图分类（可用小模型或关键词）
        category = self._classify_intent(query)
        
        # 2. 获取该类别的工具
        candidate_tools = self.tool_categories.get(category, [])
        
        # 3. 语义相似度排序（可用embedding）
        ranked_tools = self._rank_tools_by_relevance(
            query, 
            candidate_tools
        )
        
        return ranked_tools[:top_k]
```

**使用效果**:
```
原始提示词（100个工具）: 5000+ tokens
优化后提示词（5个相关工具）: 500 tokens
→ 减少90%，提升准确性
```

---

**方案2: 工具索引与检索**

```python
class VectorToolExecutor:
    def __init__(self):
        self.tools = {}
        self.tool_embeddings = {}  # 工具描述的向量表示
    
    def registerTool(self, name, description, func):
        """注册工具并生成embedding"""
        self.tools[name] = {'description': description, 'func': func}
        
        # 生成工具描述的embedding
        self.tool_embeddings[name] = self._get_embedding(description)
    
    def search_tools(self, query, top_k=5):
        """基于语义相似度检索工具"""
        query_embedding = self._get_embedding(query)
        
        # 计算余弦相似度
        similarities = {
            name: self._cosine_similarity(query_embedding, emb)
            for name, emb in self.tool_embeddings.items()
        }
        
        # 返回top_k
        top_tools = sorted(
            similarities.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return [name for name, score in top_tools]
```

---

**方案3: 两阶段工具选择**

```
阶段1: 粗选（快速模型）
  - 从100个工具中选出10个候选
  - 基于关键词匹配或简单分类

阶段2: 精选（精准模型）
  - 从10个候选中选出最合适的1个
  - 基于语义理解和上下文
```

---

## 习题4: Plan-and-Solve 的动态性

### Q4.1: 动态重规划机制设计

**场景**: 执行过程中某步骤失败

**设计方案**:

```python
class DynamicPlanAndSolveAgent:
    def execute_with_replanning(self, question, plan):
        """支持动态重规划的执行器"""
        history = ""
        
        for i, step in enumerate(plan):
            print(f"执行步骤 {i+1}: {step}")
            
            # 尝试执行
            result = self._execute_step(step, history)
            
            # 检查执行结果
            if self._is_step_failed(result):
                print(f"⚠️  步骤 {i+1} 执行失败: {result}")
                
                # 触发重规划
                new_plan = self._replan(
                    question=question,
                    failed_step=step,
                    failed_reason=result,
                    remaining_plan=plan[i+1:],
                    history=history
                )
                
                # 替换剩余计划
                plan = plan[:i] + new_plan
                print(f"🔄 重新规划: {new_plan}")
                continue
            
            # 成功 - 更新历史
            history += f"步骤{i+1}: {step}\n结果: {result}\n"
        
        return result
    
    def _replan(self, question, failed_step, failed_reason, 
                remaining_plan, history):
        """生成新的执行计划"""
        replan_prompt = f"""
原始问题: {question}

已完成的步骤:
{history}

失败的步骤: {failed_step}
失败原因: {failed_reason}

原计划剩余步骤: {remaining_plan}

请基于当前情况，重新规划后续步骤。
输出格式: ["新步骤1", "新步骤2", ...]
"""
        
        # 调用LLM生成新计划
        new_plan = self.planner.plan(replan_prompt)
        return new_plan
```

**示例运行**:
```
原计划:
["查询北京到上海的航班",
 "预订机票",
 "预订酒店",
 "预订租车"]

执行步骤1: ✅ 成功
执行步骤2: ❌ 失败（无可用座位）

触发重规划:
["查询北京到上海的高铁",
 "预订高铁票",
 "调整酒店入住时间",
 "预订租车"]
```

---

### Q4.2: 商务旅行预订：ReAct vs Plan-and-Solve

**任务**: 预订北京到上海商务旅行（机票+酒店+租车）

**我的选择**: **Plan-and-Solve 更合适**

**理由**:

1. **任务结构清晰**
   ```
   明确的步骤:
   1. 查询航班
   2. 预订机票
   3. 根据航班时间预订酒店
   4. 预订租车服务
   ```

2. **步骤间有依赖关系**
   - 酒店入住时间取决于航班到达时间
   - 租车时间取决于航班和酒店位置
   - → 需要状态管理，Plan-and-Solve天然支持

3. **需要全局协调**
   - 三个服务需要时间协调
   - 需要考虑总预算
   - → 规划阶段可以全局优化

4. **执行相对确定**
   - API调用流程固定
   - 不需要频繁探索
   - → 按计划执行即可

**Plan-and-Solve 执行示例**:
```python
# Planning阶段
plan = [
    "查询2024-12-20北京到上海的航班",
    "根据预算和时间选择合适航班并预订",
    "根据航班到达时间(18:00)预订附近酒店",
    "预订租车服务(取车时间18:30)"
]

# Solving阶段
步骤1 → 航班列表: [CA123(14:00-16:00), MU456(16:00-18:00), ...]
步骤2 → 已预订: MU456
步骤3 → 已预订: 浦东希尔顿(18:30入住)
步骤4 → 已预订: 租车(18:30取车)
```

**ReAct 的问题**:
- 可能先订酒店后订机票 → 时间不匹配
- 缺乏全局视角 → 总价超预算
- 需要多次回溯调整 → 效率低

**结论**: 对于这种"明确步骤+依赖关系"的任务，Plan-and-Solve 更优。

---

### Q4.3: 分层规划系统设计

**设计**:

```python
class HierarchicalPlanner:
    def plan(self, question):
        """两层规划"""
        
        # 第1层: 高层抽象计划
        high_level_plan = self._generate_high_level_plan(question)
        print(f"高层计划: {high_level_plan}")
        
        # 第2层: 为每个高层步骤生成详细子计划
        detailed_plan = []
        for high_step in high_level_plan:
            sub_steps = self._generate_sub_plan(high_step, question)
            detailed_plan.append({
                'high_level': high_step,
                'sub_steps': sub_steps
            })
        
        return detailed_plan
    
    def _generate_high_level_plan(self, question):
        """生成高层计划"""
        prompt = f"""
将任务分解为3-5个高层步骤（抽象层面）：
任务: {question}

输出格式: ["高层步骤1", "高层步骤2", ...]
"""
        return self.llm.think(prompt)
    
    def _generate_sub_plan(self, high_step, context):
        """为高层步骤生成详细子步骤"""
        prompt = f"""
将高层步骤分解为具体可执行的子步骤：
高层步骤: {high_step}
任务背景: {context}

输出格式: ["子步骤1", "子步骤2", ...]
"""
        return self.llm.think(prompt)
```

**示例：商务旅行预订**

```
高层计划:
["规划行程安排",
 "预订交通工具",
 "预订住宿",
 "安排地面交通"]

详细计划:
{
  "high_level": "规划行程安排",
  "sub_steps": [
    "确定出发和返回日期",
    "确定会议时间和地点",
    "计算所需停留天数"
  ]
},
{
  "high_level": "预订交通工具",
  "sub_steps": [
    "查询北京到上海的航班",
    "比较价格和时间",
    "预订合适的航班",
    "确认订单"
  ]
},
...
```

**优势**:

1. **结构更清晰**
   - 高层计划提供全局视角
   - 子计划聚焦具体执行

2. **易于管理和调试**
   - 高层计划失败 → 重新规划整体
   - 子步骤失败 → 只需调整局部

3. **支持并行执行**
   - 某些高层步骤可以并行
   - 如："查询航班"和"查询酒店"可同时进行

4. **更好的可解释性**
   - 用户可以理解每个大步骤的目的
   - 便于进度跟踪

---

## 习题5: Reflection 机制深化

### Q5.1: 使用不同模型做反思 vs 执行

**场景**: 
- 执行模型: 快速但能力一般（如 GPT-3.5）
- 反思模型: 强大但成本高（如 GPT-4）

**影响分析**:

**优势** ✅:

1. **成本优化**
   - 执行阶段使用便宜模型
   - 反思阶段使用贵模型（调用次数少）
   - 总成本降低

2. **质量提升**
   - 强模型的反思更深刻
   - 能发现弱模型忽略的问题
   - 最终质量更高

3. **速度优化**
   - 快模型执行速度快
   - 强模型仅在关键环节使用

**劣势** ❌:

1. **理解鸿沟**
   - 强模型可能提出弱模型无法实现的优化。沟通和思考不在一个维度，相差太大则鸡同鸭讲，丢失。
   - "反思太高级，执行跟不上" 能力跟不上想法。

2. **不一致性**
   - 两个模型的"理解"可能不同
   - 反馈可能无法被准确执行

**实现建议**:

```python
class HybridReflectionAgent:
    def __init__(self, fast_model, strong_model):
        self.executor = fast_model  # GPT-3.5
        self.reflector = strong_model  # GPT-4
    
    def run(self, task):
        # 执行：使用快速模型
        code = self.executor.generate(task)
        
        # 反思：使用强大模型
        feedback = self.reflector.reflect(code, task)
        
        # 优化：使用快速模型（基于强模型的反馈）
        improved_code = self.executor.refine(code, feedback)
        
        return improved_code
```

**适用场景**:
- ✅ 成本敏感的应用
- ✅ 执行任务相对简单，反思需要深度
- ❌ 不适合：执行和反思难度相当的任务

---

### Q5.2: 更智能的终止条件

**当前终止条件的问题**:

1. **"无需改进"判断主观**
   - LLM可能过早认为"无需改进"
   - 或过晚才满意

2. **最大迭代次数过于简单**
   - 可能在接近最优时被迫终止
   - 或在已达最优时继续浪费资源

**更智能的终止条件设计**:

**方案1: 基于改进幅度**

```python
class SmartReflectionAgent:
    def should_stop(self, history):
        """基于改进幅度决定是否终止"""
        
        if len(history) < 2:
            return False
        
        # 计算最近两次的相似度
        last_code = history[-1]
        prev_code = history[-2]
        
        similarity = self._calculate_similarity(last_code, prev_code)
        
        # 如果改进幅度小于阈值，认为收敛
        if similarity > 0.95:  # 95%相似
            print("改进幅度过小，已收敛")
            return True
        
        return False
    
    def _calculate_similarity(self, code1, code2):
        """计算代码相似度"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, code1, code2).ratio()
```

---

**方案2: 基于质量评分**

```python
class MetricBasedReflectionAgent:
    def should_stop(self, code, task):
        """基于客观指标决定是否终止"""
        
        # 计算多维度评分
        scores = {
            'correctness': self._test_correctness(code, task),
            'efficiency': self._analyze_complexity(code),
            'readability': self._check_style(code),
            'robustness': self._test_edge_cases(code)
        }
        
        # 综合评分
        total_score = sum(scores.values()) / len(scores)
        
        print(f"当前评分: {scores}, 综合: {total_score}")
        
        # 达到阈值则终止
        if total_score >= 0.90:  # 90分以上
            print("质量达标，终止优化")
            return True
        
        return False
```

---

**方案3: 混合终止条件**

```python
def smart_termination(iteration, history, current_code, task):
    """综合多种终止条件"""
    
    # 条件1: 达到最大迭代次数（硬限制）
    if iteration >= MAX_ITERATIONS:
        return True, "达到最大迭代次数"
    
    # 条件2: 改进幅度过小（收敛）
    if len(history) >= 2:
        if is_converged(history[-1], history[-2]):
            return True, "改进收敛"
    
    # 条件3: 质量评分达标
    score = evaluate_quality(current_code, task)
    if score >= QUALITY_THRESHOLD:
        return True, "质量达标"
    
    # 条件4: LLM明确表示"无需改进"
    if "无需改进" in last_feedback:
        return True, "LLM确认无需改进"
    
    return False, "继续优化"
```

**推荐**: 方案3（混合条件），既有客观指标，又有主观判断。

---

### Q5.3: 学术论文写作助手的多维度Reflection

**设计**:

```python
class PaperReflectionAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.dimensions = [
            'logic', 'innovation', 'language', 
            'citation', 'structure'
        ]
    
    def run(self, topic):
        """多维度反思优化"""
        
        # 初始执行
        paper = self._generate_initial_draft(topic)
        
        # 多维度迭代优化
        for iteration in range(MAX_ITERATIONS):
            print(f"\n=== 第{iteration+1}轮优化 ===")
            
            improved = False
            
            # 逐个维度反思
            for dim in self.dimensions:
                print(f"\n--- {dim} 维度反思 ---")
                
                feedback = self._reflect_dimension(paper, dim)
                
                if "需要改进" in feedback:
                    paper = self._refine_by_feedback(
                        paper, feedback, dim
                    )
                    improved = True
            
            # 所有维度都无需改进，终止
            if not improved:
                print("\n所有维度均已达标")
                break
        
        return paper
    
    def _reflect_dimension(self, paper, dimension):
        """单维度反思"""
        
        prompts = {
            'logic': """
作为逻辑评审专家，审查论文的逻辑严密性：
- 论证链条是否完整？
- 结论是否有充分支撑？
- 是否存在逻辑跳跃？

论文: {paper}

评价: [优秀/良好/需要改进]
具体建议: ...
""",
            'innovation': """
作为领域专家，评估论文的创新性：
- 研究问题是否新颖？
- 方法是否有创新？
- 与现有工作的区别？

论文: {paper}

评价: [优秀/良好/需要改进]
具体建议: ...
""",
            'language': """
作为语言专家，审查论文的表达：
- 语言是否准确、简洁？
- 是否有语法错误？
- 术语使用是否规范？

论文: {paper}

评价: [优秀/良好/需要改进]
具体建议: ...
""",
            'citation': """
作为文献专家，检查引用规范：
- 关键文献是否引用？
- 引用格式是否正确？
- 是否有引用不当？

论文: {paper}

评价: [优秀/良好/需要改进]
具体建议: ...
""",
            'structure': """
作为结构专家，评估论文组织：
- 章节结构是否合理？
- 内容分布是否均衡？
- 过渡是否自然？

论文: {paper}

评价: [优秀/良好/需要改进]
具体建议: ...
"""
        }
        
        prompt = prompts[dimension].format(paper=paper)
        feedback = self.llm.think(prompt)
        
        return feedback
    
    def _refine_by_feedback(self, paper, feedback, dimension):
        """根据反馈优化"""
        prompt = f"""
根据{dimension}维度的反馈，优化论文：

原论文:
{paper}

反馈:
{feedback}

请输出优化后的论文。
"""
        improved_paper = self.llm.think(prompt)
        return improved_paper
```

**优化流程示例**:

```
第1轮优化:
  ├─ 逻辑维度: 需要改进（论证链不完整）→ 优化
  ├─ 创新维度: 良好
  ├─ 语言维度: 需要改进（术语不统一）→ 优化
  ├─ 引用维度: 良好
  └─ 结构维度: 需要改进（章节失衡）→ 优化

第2轮优化:
  ├─ 逻辑维度: 良好
  ├─ 创新维度: 良好
  ├─ 语言维度: 良好
  ├─ 引用维度: 需要改进（缺少关键文献）→ 优化
  └─ 结构维度: 良好

第3轮优化:
  ├─ 所有维度: 良好
  └─ 终止优化
```

**优势**:
- ✅ 多角度全面审查
- ✅ 每个维度独立优化
- ✅ 避免"顾此失彼"
- ✅ 更高的最终质量

---

## 习题6: 提示词工程分析

### Q6.1: ReAct vs Plan-and-Solve 提示词差异

**ReAct 提示词特点**:

```python
REACT_PROMPT = """
请严格按照以下格式进行回应:

Thought: 你的思考过程
Action: 你决定采取的行动
  - {tool_name}[{tool_input}]: 调用工具
  - Finish[最终答案]: 结束

可用工具:
{tools}

问题: {question}
历史: {history}
"""
```

**核心特征**:
1. **强调格式约束** - "严格按照以下格式"
2. **定义循环结构** - Thought→Action→Observation
3. **动态上下文** - 历史记录不断累积
4. **开放式结束** - 可以随时Finish

**服务目的**: 支持**动态决策**和**步进式推理**

---

**Plan-and-Solve 提示词特点**:

```python
PLANNER_PROMPT = """
你是一个顶级的AI规划专家。
将复杂问题分解成简单步骤组成的行动计划。

问题: {question}

请严格按照以下格式输出:
```python
["步骤1", "步骤2", ...]
```
"""

EXECUTOR_PROMPT = """
你是顶级的AI执行专家。
严格按照给定的计划，一步步地解决问题。

原始问题: {question}
完整计划: {plan}
历史结果: {history}
当前步骤: {current_step}

请仅输出该步骤的答案。
"""
```

**核心特征**:
1. **角色定位明确** - "规划专家" vs "执行专家"
2. **结构化输出** - Python列表格式
3. **职责分离** - 规划和执行完全分开
4. **约束执行** - "严格按照计划"、"仅输出该步骤"

**服务目的**: 支持**两阶段解耦**和**状态管理**

---

**差异总结**:

| 特征 | ReAct | Plan-and-Solve |
|------|-------|----------------|
| **提示词数量** | 1个（循环使用） | 2个（Planning + Solving） |
| **角色设定** | 单一角色 | 双角色（专家分工） |
| **输出格式** | 自然语言 + 格式标记 | 结构化数据（Python列表） |
| **上下文管理** | 历史累积 | 历史分离（Planning vs Solving） |
| **约束强度** | 中等 | 强（"严格"、"仅"） |

---

### Q6.2: 修改Reflection角色设定的影响

**原始角色设定**:
```
"你是一位极其严格的代码评审专家和资深算法工程师，
对代码的性能有极致的要求"
```

**修改后角色设定**:
```
"你是一位注重代码可读性的开源项目维护者"
```

**预期影响**:

**原始设定（性能专家）**:
- 重点关注：算法复杂度、性能瓶颈
- 可能产生的反馈：
  ```
  "时间复杂度O(n²)太高，应改用哈希表O(n)"
  "这个循环可以用numpy向量化加速"
  ```

**修改后设定（可读性专家）**:
- 重点关注：代码结构、命名、注释
- 可能产生的反馈：
  ```
  "变量名'x'不够描述性，建议改为'user_count'"
  "缺少函数文档字符串，应添加说明"
  "这个函数太长，建议拆分为多个小函数"
  ```

**实验验证**（建议实际运行）:

```python
# 测试代码
def f(n):
    r = []
    for i in range(2, n+1):
        if all(i % j != 0 for j in range(2, i)):
            r.append(i)
    return r

# 性能专家反馈（预期）:
"""
函数复杂度O(n²)，应使用埃拉托斯特尼筛法优化到O(n log log n)
"""

# 可读性专家反馈（预期）:
"""
1. 函数名'f'不清晰，应改为'find_primes'
2. 变量名'r', 'i', 'j'缺乏描述性
3. 缺少文档字符串说明功能
4. 建议添加类型提示
"""
```

**结论**: 角色设定**显著影响反思的侧重点**

---

### Q6.3: 添加Few-shot示例

**原始提示词**（Zero-shot）:
```python
REACT_PROMPT = """
请按以下格式输出:
Thought: ...
Action: ...
"""
```

**添加Few-shot示例**:
```python
REACT_PROMPT_FEWSHOT = """
请按以下格式输出:

示例1:
问题: 北京今天天气如何？
Thought: 我需要查询北京的实时天气信息
Action: get_weather[北京]
Observation: 北京今天晴，温度15°C
Thought: 已获得天气信息，可以回答
Action: Finish[北京今天晴，温度15°C]

示例2:
问题: 1000以内有多少个素数？
Thought: 需要找出1000以内的所有素数
Action: find_primes[1000]
Observation: 找到168个素数
Thought: 已得到答案
Action: Finish[1000以内有168个素数]

现在请处理:
问题: {question}
"""
```

**效果对比**（预期）:

**Zero-shot**:
- 可能出现格式错误
- 可能不知道何时Finish
- 输出可能啰嗦

**Few-shot**:
- ✅ 格式遵循度提升
- ✅ 更清楚工作流程
- ✅ 输出更简洁

**代价**:
- ❌ 提示词变长（token增加）
- ❌ 每次调用成本增加

**建议**: 
- 对于复杂格式：使用Few-shot
- 对于简单格式：Zero-shot足够

---

## 习题7: 电商客服智能体系统设计

**需求分析**:

a. 理解退款理由（NLU）  
b. 查询订单和物流（工具调用）  
c. 判断是否批准退款（决策）  
d. 生成并发送回复邮件（执行）  
e. 低置信度时自我反思（质量保证）

---

### Q7.1: 范式选择

**我的方案**: **ReAct + Reflection 混合**

**架构设计**:

```
阶段1: ReAct（快速处理）
  ├─ 理解用户退款理由
  ├─ 查询订单信息（工具）
  ├─ 查询物流状态（工具）
  ├─ 初步决策（批准/拒绝）
  └─ 生成初版回复

阶段2: Reflection（质量保证）
  ├─ 反思：决策是否合理？
  ├─ 反思：回复是否友好？
  ├─ 如果置信度高 → 直接发送
  └─ 如果置信度低 → 优化后发送
```

**为什么选ReAct**:
- ✅ 需要查询多个工具（订单、物流）
- ✅ 决策依赖查询结果（动态调整）
- ✅ 流程有一定探索性

**为什么加Reflection**:
- ✅ 决策关键（影响用户满意度和公司利益）
- ✅ 需要平衡友好性和公司利益
- ✅ 低置信度需要反思（需求e）

---

### Q7.2: 工具设计

**工具1: 订单查询**
```python
def query_order(order_id: str) -> dict:
    """
    查询订单详细信息
    
    描述: 根据订单ID查询订单的详细信息，包括商品、价格、
          下单时间、支付状态等。用于了解用户的订单背景。
    
    参数:
        order_id: 订单编号
    
    返回:
        {
            'order_id': '12345',
            'product': '手机壳',
            'price': 29.9,
            'order_time': '2024-12-10',
            'payment_status': '已支付',
            'can_refund': True
        }
    """
    # 实际实现：调用订单系统API
    pass
```

---

**工具2: 物流查询**
```python
def query_logistics(order_id: str) -> dict:
    """
    查询物流状态
    
    描述: 根据订单ID查询物流信息，包括发货状态、运输进度、
          预计送达时间等。用于判断是否可以退款。
    
    参数:
        order_id: 订单编号
    
    返回:
        {
            'status': '运输中',
            'location': '北京分拨中心',
            'estimated_delivery': '2024-12-20',
            'can_intercept': False  # 是否可拦截
        }
    """
    # 实际实现：调用物流系统API
    pass
```

---

**工具3: 退款策略引擎**
```python
def check_refund_policy(order_info: dict, reason: str) -> dict:
    """
    检查退款政策
    
    描述: 根据订单信息和退款理由，查询公司退款政策，
          给出是否应该批准的建议和置信度。
    
    参数:
        order_info: 订单详细信息
        reason: 用户退款理由
    
    返回:
        {
            'decision': 'approve',  # approve/reject/uncertain
            'confidence': 0.85,  # 置信度 0-1
            'reason': '符合7天无理由退货政策',
            'warnings': ['商品已发货，需用户承担运费']
        }
    """
    # 实际实现：调用策略规则引擎
    # 可能包含：
    # - 7天无理由
    # - 质量问题
    # - 物流延迟
    # - 特殊商品不可退
    pass
```

---

**工具4: 邮件发送**
```python
def send_email(to: str, subject: str, content: str) -> bool:
    """
    发送邮件
    
    描述: 向用户发送退款处理结果的邮件通知。
    
    参数:
        to: 收件人邮箱
        subject: 邮件主题
        content: 邮件正文
    
    返回:
        bool: 是否发送成功
    """
    # 实际实现：调用邮件服务API
    pass
```

---

### Q7.3: 提示词设计

**ReAct阶段提示词**:

```python
CUSTOMER_SERVICE_PROMPT = """
你是一位专业、友好的客服智能体。

你的目标是：
1. 理解用户的退款理由
2. 查询订单和物流信息
3. 根据公司政策做出合理决策
4. 生成友好、得体的回复

原则：
- 始终保持礼貌和尊重
- 决策需同时考虑用户权益和公司利益
- 当政策允许时，优先满足用户
- 当政策不允许时，清晰解释原因并提供替代方案

可用工具：
- query_order[订单ID]: 查询订单信息
- query_logistics[订单ID]: 查询物流状态
- check_refund_policy[订单信息, 退款理由]: 检查退款政策

请按以下格式工作：
Thought: 你的思考
Action: 工具调用或Finish[回复内容]

用户问题：{question}
"""
```

**Reflection阶段提示词**:

```python
REFLECTION_PROMPT = """
你是一位客服质量审查专家。请审查以下回复：

用户问题：{question}
初版回复：{response}
决策置信度：{confidence}

请从以下维度审查：
1. **友好性**: 语气是否温和、尊重？
2. **清晰性**: 解释是否清楚易懂？
3. **公平性**: 是否平衡了用户和公司利益？
4. **完整性**: 是否遗漏重要信息？
5. **专业性**: 是否符合客服标准？

如果置信度低于0.7或存在明显问题，请提出改进建议。
如果已经很好，请回复"无需改进"。
"""
```

**平衡策略（嵌入提示词）**:

```
决策原则：
- 用户权益优先，但需符合政策
- 质量问题：无条件退款
- 物流延迟：协商补偿
- 个人原因：政策范围内退款
- 恶意退款：礼貌拒绝

语气指导：
- 批准时：表达理解和歉意
- 拒绝时：解释原因+提供替代方案
- 不确定时：请求更多信息
```

---

### Q7.4: 风险与应对

**风险1: 错误决策**

**场景**: 系统批准了不应批准的退款

**应对**:
```python
# 1. 多重验证
if confidence < 0.8:
    # 低置信度 → 人工审核
    transfer_to_human(case)

# 2. 决策日志
log_decision(order_id, decision, reason, confidence)

# 3. 批量审计
# 定期检查决策准确率，发现异常模式
```

---

**风险2: 用户不满**

**场景**: 回复虽然正确，但用户感觉不友好

**应对**:
```python
# 1. 情感分析
sentiment = analyze_sentiment(response)
if sentiment < 0.6:  # 负面情绪
    response = improve_tone(response)

# 2. 多样化表达
# 避免机械重复，提供个性化回复

# 3. 反馈循环
# 收集用户满意度，持续优化提示词
```

---

**风险3: 政策滥用**

**场景**: 用户发现漏洞，恶意退款

**应对**:
```python
# 1. 异常检测
if is_suspicious_pattern(user_id, recent_orders):
    increase_review_level()

# 2. 风控规则
MAX_REFUNDS_PER_MONTH = 3
if user_refund_count > MAX_REFUNDS_PER_MONTH:
    require_manual_review()

# 3. 黑名单机制
if confirmed_malicious(user_id):
    add_to_blacklist()
```

---

**风险4: 数据泄露**

**场景**: 在日志或反思中泄露用户隐私

**应对**:
```python
# 1. 脱敏处理
def anonymize(text):
    # 手机号：138****1234
    # 地址：北京市**区**路
    # 邮箱：u***@example.com
    pass

# 2. 访问控制
# 限制谁可以查看决策日志

# 3. 数据加密
# 敏感信息加密存储
```

---

**风险5: 系统故障**

**场景**: 工具API调用失败

**应对**:
```python
# 1. 优雅降级
try:
    order = query_order(order_id)
except APIError:
    # 降级方案：转人工
    return "系统暂时无法查询，已转人工客服"

# 2. 重试机制
@retry(max_attempts=3, backoff=exponential)
def query_order(order_id):
    pass

# 3. 超时保护
@timeout(seconds=5)
def query_logistics(order_id):
    pass
```

---

## 总结

通过这7道习题，我们深化了对三种范式的理解：

1. **范式本质**: 思考与行动的不同组织方式
2. **范式组合**: 可以混合使用，发挥各自优势
3. **工程实践**: 鲁棒性、可扩展性、错误处理
4. **提示词工程**: 角色设定、格式约束、Few-shot
5. **实际应用**: 电商客服等真实场景

**关键洞察**:
- 没有"最好"的范式，只有"最合适"的范式
- 实际应用需要工程化思维（风控、降级、监控）
- 提示词设计是成败的关键

---

**建议**:
- ⏳ 选择1-2道题进行代码实现
- ⏳ 特别推荐：习题3（计算器工具）、习题7（客服系统设计）

**学习状态**: 习题理论分析完成 ✅  
**下一步**: 选择题目动手实践
