"""
第一章节示例 - FirstAgentTest
适配版本 - 使用我们的 .env 配置
"""
import requests
import json
import os
import re
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从 .env 加载配置
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_ID = os.getenv("LLM_MODEL_ID")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY

# 系统提示词
AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""

# ========================================
# 工具函数定义
# ========================================
def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        return f"{city}当前天气：{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        return f"错误：查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"

def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """
    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return "错误：未配置TAVILY_API_KEY。"

    tavily = TavilyClient(api_key=api_key)
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
    
    try:
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        
        if response.get("answer"):
            return response["answer"]
        
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        
        if not formatted_results:
             return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误：执行Tavily搜索时出现问题 - {e}"

available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

print("✅ 工具函数定义完成!")

# ========================================
# LLM 客户端
# ========================================
class OpenAICompatibleClient:
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        print("🧠 正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("✅ 大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return "错误：调用语言模型服务时出错。"

# ========================================
# 旅行助手类
# ========================================
class TravelAssistant:
    def __init__(self):
        self.llm = OpenAICompatibleClient(
            model=MODEL_ID,
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.prompt_history = []
    
    def reset(self):
        self.prompt_history = []
    
    def add_user_message(self, message: str):
        self.prompt_history.append(f"用户请求: {message}")
    
    def add_assistant_message(self, message: str):
        self.prompt_history.append(message)
    
    def add_observation(self, observation: str):
        self.prompt_history.append(f"Observation: {observation}")

print("✅ 智能助手类定义完成!")

# ========================================
# 辅助函数
# ========================================
def parse_action(action_str):
    """解析行动字符串"""
    if action_str.startswith("finish"):
        match = re.search(r'finish\(answer="(.*)"\)', action_str)
        if match:
            return "finish", {"answer": match.group(1)}
        return "finish", {"answer": "任务完成"}
    
    tool_name_match = re.search(r"(\w+)\(", action_str)
    if not tool_name_match:
        return None, {}
    
    tool_name = tool_name_match.group(1)
    args_match = re.search(r"\((.*)\)", action_str)
    if args_match:
        args_str = args_match.group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))
    else:
        kwargs = {}
    
    return tool_name, kwargs

print("✅ 辅助函数定义完成!")

# ========================================
# 主运行函数
# ========================================
def run_assistant(user_input, max_iterations=5):
    """运行旅行助手"""
    assistant = TravelAssistant()
    assistant.add_user_message(user_input)
    
    print(f"\n{'=' * 70}")
    print(f"👤 用户输入: {user_input}")
    print(f"{'=' * 70}\n")
    
    for i in range(max_iterations):
        print(f"\n🔄 循环 {i+1}/{max_iterations}")
        print("-" * 70)
        
        # 构建完整prompt并调用LLM
        full_prompt = "\n".join(assistant.prompt_history)
        llm_output = assistant.llm.generate(full_prompt, AGENT_SYSTEM_PROMPT)
        
        # 截断多余的Thought-Action
        match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
                print("⚠️  已截断多余的 Thought-Action 对")
        
        assistant.add_assistant_message(llm_output)
        
        print(f"\n🤖 模型输出:\n{llm_output}\n")
        
        # 解析行动
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            print("❌ 解析错误：模型输出中未找到 Action。")
            break
            
        action_str = action_match.group(1).strip()
        tool_name, kwargs = parse_action(action_str)
        
        # 处理完成行动
        if tool_name == "finish":
            final_answer = kwargs.get("answer", "任务完成")
            print(f"\n{'=' * 70}")
            print(f"🎉 任务完成!")
            print(f"{'=' * 70}")
            print(f"\n✅ 最终答案:\n{final_answer}\n")
            print(f"{'=' * 70}\n")
            return final_answer, assistant.prompt_history
        
        # 处理工具调用
        if tool_name in available_tools:
            print(f"🛠️  调用工具: {tool_name}({kwargs})")
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误：未定义的工具 '{tool_name}'"
        
        print(f"\n📊 观察结果:\n{observation}")
        print("-" * 70)
        
        assistant.add_observation(observation)
    
    timeout_answer = "抱歉，经过多次尝试仍未完成您的请求。"
    print(f"\n⏰ 达到最大循环次数\n")
    return timeout_answer, assistant.prompt_history

# ========================================
# 测试示例
# ========================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 第一章节示例 - 智能旅行助手测试")
    print("=" * 70)
    
    # 测试问题
    user_input = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    
    # 运行助手
    final_answer, history = run_assistant(user_input, max_iterations=5)
    
    print("\n✅ 测试完成！")
