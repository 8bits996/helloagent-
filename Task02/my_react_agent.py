"""
Task02 - ReActAgent 框架化实现

基于 HelloAgents 框架构建的 ReAct Agent
对比 Task01: 从零实现 -> 框架化实现
"""

import re
import requests
from typing import Dict, Any, List, Optional, Callable
from hello_agents import HelloAgentsLLM
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# ========================================
# 1. BaseTool - 工具抽象基类
# ========================================
class BaseTool:
    """工具的抽象基类 - 统一工具接口"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def run(self, **kwargs) -> str:
        """执行工具 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 run 方法")
    
    def get_schema(self) -> str:
        """返回工具的调用格式说明"""
        return f"{self.name}: {self.description}"


# ========================================
# 2. 具体工具实现
# ========================================
class WeatherTool(BaseTool):
    """天气查询工具"""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="查询指定城市的实时天气，参数: city (城市名称)"
        )
    
    def run(self, city: str = "", **kwargs) -> str:
        """通过 wttr.in API 查询真实天气"""
        if not city:
            return "错误：city 参数不能为空"
        
        url = f"https://wttr.in/{city}?format=j1"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current_condition'][0]
            weather_desc = current['weatherDesc'][0]['value']
            temp_c = current['temp_C']
            
            return f"{city}当前天气：{weather_desc}，气温{temp_c}摄氏度"
            
        except requests.exceptions.RequestException as e:
            return f"错误：查询天气时遇到网络问题 - {e}"
        except (KeyError, IndexError) as e:
            return f"错误：解析天气数据失败 - {e}"


class AttractionTool(BaseTool):
    """景点推荐工具"""
    
    def __init__(self):
        super().__init__(
            name="get_attraction",
            description="根据城市和天气推荐旅游景点，参数: city (城市名称), weather (天气描述)"
        )
    
    def run(self, city: str = "", weather: str = "", **kwargs) -> str:
        """使用 Tavily Search 搜索景点推荐"""
        if not city:
            return "错误：city 参数不能为空"
        
        try:
            from tavily import TavilyClient
            
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                return "错误：未配置 TAVILY_API_KEY"
            
            tavily = TavilyClient(api_key=api_key)
            query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
            
            response = tavily.search(query=query, search_depth="basic", include_answer=True)
            
            # 优先返回 answer
            if response.get("answer"):
                return response["answer"]
            
            # 否则格式化搜索结果
            results = response.get("results", [])
            if not results:
                return "抱歉，没有找到相关的旅游景点推荐。"
            
            formatted = [f"- {r['title']}: {r['content']}" for r in results[:3]]
            return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted)
            
        except ImportError:
            return "错误：请安装 tavily-python: pip install tavily-python"
        except Exception as e:
            return f"错误：执行搜索时出现问题 - {e}"


# ========================================
# 3. ToolRegistry - 工具注册表
# ========================================
class ToolRegistry:
    """工具注册表 - 统一管理工具"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"✅ 工具已注册: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """获取所有工具"""
        return self._tools.copy()
    
    def get_tools_description(self) -> str:
        """生成工具描述文本（用于 prompt）"""
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- `{tool.name}`: {tool.description}")
        return "\n".join(descriptions)


# ========================================
# 4. ReActAgent - 框架化的 ReAct Agent
# ========================================
class ReActAgent:
    """
    ReAct Agent - 基于 HelloAgents 框架的实现
    
    核心改进（对比 Task01）:
    1. 工具系统: 统一的工具抽象和注册机制
    2. 代码组织: 模块化设计，职责清晰
    3. 错误处理: 完善的异常处理和日志
    4. 可扩展性: 易于添加新工具
    """
    
    def __init__(
        self,
        llm: HelloAgentsLLM,
        tools: Optional[List[BaseTool]] = None,
        max_iterations: int = 5,
        verbose: bool = True
    ):
        """
        初始化 ReAct Agent
        
        Args:
            llm: HelloAgentsLLM 实例
            tools: 工具列表
            max_iterations: 最大循环次数
            verbose: 是否打印详细日志
        """
        self.llm = llm
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # 初始化工具注册表
        self.tool_registry = ToolRegistry()
        if tools:
            for tool in tools:
                self.tool_registry.register(tool)
        
        # 历史记录
        self.history: List[str] = []
    
    def _get_system_prompt(self) -> str:
        """生成系统提示词"""
        tools_desc = self.tool_registry.get_tools_description()
        
        return f"""
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
{tools_desc}

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
""".strip()
    
    def _parse_action(self, action_str: str) -> tuple[str, Dict[str, Any]]:
        """
        解析 Action 字符串
        
        返回: (tool_name, kwargs)
        """
        action_str = action_str.strip()
        
        # 处理 finish 行动
        if action_str.startswith("finish"):
            match = re.search(r'finish\(answer="(.*)"\)', action_str, re.DOTALL)
            if match:
                return "finish", {"answer": match.group(1)}
            return "finish", {"answer": "任务完成"}
        
        # 解析工具名称
        tool_name_match = re.search(r"(\w+)\(", action_str)
        if not tool_name_match:
            return None, {}
        
        tool_name = tool_name_match.group(1)
        
        # 解析参数
        args_match = re.search(r"\((.*)\)", action_str, re.DOTALL)
        if args_match:
            args_str = args_match.group(1)
            # 提取 key="value" 格式的参数
            kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))
        else:
            kwargs = {}
        
        return tool_name, kwargs
    
    def _call_tool(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """调用工具并返回结果"""
        tool = self.tool_registry.get_tool(tool_name)
        
        if not tool:
            return f"错误：未定义的工具 '{tool_name}'"
        
        try:
            result = tool.run(**kwargs)
            return result
        except Exception as e:
            return f"错误：工具执行失败 - {e}"
    
    def _log(self, message: str, level: str = "INFO"):
        """日志输出"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "TOOL": "🛠️ ",
                "THINK": "🤔",
                "RESULT": "📊"
            }.get(level, "")
            print(f"{prefix} {message}")
    
    def run(self, user_input: str) -> str:
        """
        运行 ReAct Agent
        
        Args:
            user_input: 用户输入
            
        Returns:
            最终答案
        """
        # 重置历史
        self.history = []
        self.history.append(f"用户请求: {user_input}")
        
        self._log(f"用户输入: {user_input}", "INFO")
        self._log("=" * 70, "INFO")
        
        # ReAct 循环
        for iteration in range(1, self.max_iterations + 1):
            self._log(f"\n循环 {iteration}/{self.max_iterations}", "INFO")
            self._log("-" * 70, "INFO")
            
            # 1. 构建 prompt 并调用 LLM
            full_prompt = "\n".join(self.history)
            system_prompt = self._get_system_prompt()
            
            try:
                # 构建消息列表
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ]
                llm_output = self.llm.invoke(messages)
            except Exception as e:
                self._log(f"调用 LLM 失败: {e}", "ERROR")
                return "错误：语言模型调用失败"
            
            # 2. 截断多余的 Thought-Action 对
            match = re.search(
                r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)',
                llm_output,
                re.DOTALL
            )
            if match:
                llm_output = match.group(1).strip()
            
            self.history.append(llm_output)
            self._log(f"\n模型输出:\n{llm_output}", "THINK")
            
            # 3. 解析 Action
            action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
            if not action_match:
                self._log("解析错误：未找到 Action", "ERROR")
                break
            
            action_str = action_match.group(1).strip()
            tool_name, kwargs = self._parse_action(action_str)
            
            # 4. 处理 finish 行动
            if tool_name == "finish":
                final_answer = kwargs.get("answer", "任务完成")
                self._log("\n" + "=" * 70, "SUCCESS")
                self._log("任务完成!", "SUCCESS")
                self._log("=" * 70, "SUCCESS")
                self._log(f"\n最终答案:\n{final_answer}", "RESULT")
                self._log("=" * 70, "SUCCESS")
                return final_answer
            
            # 5. 调用工具
            if tool_name:
                self._log(f"调用工具: {tool_name}({kwargs})", "TOOL")
                observation = self._call_tool(tool_name, kwargs)
                self._log(f"\n观察结果:\n{observation}", "RESULT")
                
                # 添加观察到历史
                self.history.append(f"Observation: {observation}")
            else:
                self._log("解析错误：无法识别工具", "ERROR")
                break
        
        # 超时处理
        timeout_msg = "抱歉，经过多次尝试仍未完成您的请求。"
        self._log(f"\n达到最大循环次数", "ERROR")
        return timeout_msg
    
    def get_history(self) -> List[str]:
        """获取历史记录"""
        return self.history.copy()


# ========================================
# 5. 测试代码
# ========================================
def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🚀 Task02 - ReActAgent 框架化实现测试")
    print("=" * 70)
    
    # 1. 初始化 LLM
    llm = HelloAgentsLLM()
    print(f"✅ LLM 初始化完成: {llm.model}")
    
    # 2. 创建工具
    tools = [
        WeatherTool(),
        AttractionTool()
    ]
    
    # 3. 创建 Agent
    agent = ReActAgent(
        llm=llm,
        tools=tools,
        max_iterations=5,
        verbose=True
    )
    print(f"✅ ReActAgent 创建完成\n")
    
    # 4. 运行测试
    user_input = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    
    final_answer = agent.run(user_input)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
