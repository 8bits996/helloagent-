"""
HelloAgentsLLM 客户端
根据第四章的代码实现
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# 加载 .env 文件中的环境变量
load_dotenv()

class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)
        
        print(f"✅ HelloAgentsLLM 客户端初始化成功")
        print(f"   模型: {self.model}")
        print(f"   服务: {baseUrl}")

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            
            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

# --- 客户端测试 ---
if __name__ == '__main__':
    print("=" * 70)
    print("🧪 测试 HelloAgentsLLM 客户端")
    print("=" * 70)
    print()
    
    try:
        # 初始化客户端
        llmClient = HelloAgentsLLM()
        
        # 测试 1: 简单问答
        print("\n" + "=" * 70)
        print("📝 测试 1: 简单问答")
        print("=" * 70)
        
        messages1 = [
            {"role": "system", "content": "你是一个友好的 AI 助手。"},
            {"role": "user", "content": "用一句话介绍什么是 AI Agent"}
        ]
        
        response1 = llmClient.think(messages1)
        
        # 测试 2: 代码生成
        print("\n" + "=" * 70)
        print("📝 测试 2: 代码生成")
        print("=" * 70)
        
        messages2 = [
            {"role": "system", "content": "你是一个 Python 编程助手。"},
            {"role": "user", "content": "写一个计算斐波那契数列的函数（不超过10行）"}
        ]
        
        response2 = llmClient.think(messages2)
        
        # 测试 3: ReAct 风格的思考
        print("\n" + "=" * 70)
        print("📝 测试 3: ReAct 风格思考")
        print("=" * 70)
        
        messages3 = [
            {"role": "system", "content": "你是一个智能助手，需要按照 Thought-Action 的格式思考。"},
            {"role": "user", "content": "如果我想知道今天北京的天气，你会怎么做？请按照 Thought: ... Action: ... 的格式回答"}
        ]
        
        response3 = llmClient.think(messages3)
        
        print("\n" + "=" * 70)
        print("🎉 所有测试完成！HelloAgentsLLM 客户端工作正常！")
        print("=" * 70)

    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("\n请检查 .env 文件配置是否正确")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
