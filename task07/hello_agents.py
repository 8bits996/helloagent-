"""
HelloAgents LLM 封装 - 简化 LLM 调用
"""

import os
from openai import OpenAI


class HelloAgentsLLM:
    """HelloAgents LLM 包装器"""
    
    def __init__(
        self,
        provider: str = "modelscope",
        model: str = "Qwen/Qwen2.5-7B-Instruct",
        api_key: str = None,
        base_url: str = None
    ):
        """
        初始化 LLM
        
        Args:
            provider: LLM 提供商 (modelscope, siliconflow 等)
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
        """
        self.provider = provider
        self.model = model
        
        # 从环境变量读取默认值
        api_key = api_key or os.getenv('LLM_API_KEY')
        base_url = base_url or os.getenv('LLM_API_BASE')
        
        if not api_key:
            raise ValueError("API Key is required")
        
        # 配置 OpenAI 客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print(f"✅ HelloAgentsLLM initialized: {provider}/{model}")
    
    def invoke(self, messages, tools=None, **kwargs):
        """
        调用 LLM
        
        Args:
            messages: 消息列表
            tools: 工具列表 (可选)
            **kwargs: 其他参数
            
        Returns:
            响应文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            raise


class SimpleAgent:
    """简单的智能体基类"""
    
    def __init__(
        self,
        name: str = "Agent",
        llm: HelloAgentsLLM = None,
        system_prompt: str = None,
        tool_registry = None
    ):
        """
        初始化智能体
        
        Args:
            name: 智能体名称
            llm: LLM 实例
            system_prompt: 系统提示词
            tool_registry: 工具注册表
        """
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
    
    def run(self, input_text: str, **kwargs) -> str:
        """
        运行智能体
        
        Args:
            input_text: 用户输入
            
        Returns:
            响应文本
        """
        if not self.llm:
            raise ValueError("LLM未初始化")
        
        # 构建消息
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": input_text})
        
        # 调用 LLM
        response = self.llm.invoke(messages)
        
        return response


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, tool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"✅ 工具已注册: {tool.name}")
    
    def get_tool(self, name: str):
        """获取工具"""
        return self.tools.get(name)
