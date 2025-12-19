"""
自定义 SimpleAgent 实现
Task02 实践 - Agent 框架化开发
展示如何基于 HelloAgents 框架构建自定义 Agent
"""
import re
from typing import Optional, Iterator
from hello_agents import SimpleAgent, HelloAgentsLLM, Config, Message, ToolRegistry


class MySimpleAgent(SimpleAgent):
    """
    重写的简单对话Agent
    展示如何基于框架基类构建自定义Agent
    
    核心功能:
    1. 基础对话
    2. 工具调用支持
    3. 流式响应
    4. 历史记录管理
    """
    
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_tool_calling: bool = True
    ):
        """
        初始化自定义 SimpleAgent
        
        Args:
            name: Agent 名称
            llm: LLM 实例
            system_prompt: 系统提示词
            config: 配置对象
            tool_registry: 工具注册表
            enable_tool_calling: 是否启用工具调用
        """
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(f"✅ {name} 初始化完成，工具调用: {'启用' if self.enable_tool_calling else '禁用'}")
    
    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        """
        重写的运行方法 - 实现简单对话逻辑，支持可选工具调用
        
        Args:
            input_text: 用户输入
            max_tool_iterations: 最大工具调用迭代次数
            **kwargs: 其他参数传递给 LLM
            
        Returns:
            Agent 响应
        """
        print(f"\n🤖 {self.name} 正在处理: {input_text}")
        
        # 构建消息列表
        messages = []
        
        # 添加系统消息(可能包含工具信息)
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        messages.append({"role": "system", "content": enhanced_system_prompt})
        
        # 添加历史消息
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": input_text})
        
        # 如果没有启用工具调用，使用简单对话逻辑
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            print(f"✅ {self.name} 响应完成")
            return response
        
        # 支持多轮工具调用的逻辑
        return self._run_with_tools(messages, input_text, max_tool_iterations, **kwargs)
    
    def _get_enhanced_system_prompt(self) -> str:
        """
        构建增强的系统提示词，包含工具信息
        
        Returns:
            增强的系统提示词
        """
        base_prompt = self.system_prompt or "你是一个有用的AI助手。"
        
        if not self.enable_tool_calling or not self.tool_registry:
            return base_prompt
        
        # 获取工具描述
        tools_description = self.tool_registry.get_tools_description()
        if not tools_description or tools_description == "暂无可用工具":
            return base_prompt
        
        tools_section = "\n\n## 可用工具\n"
        tools_section += "你可以使用以下工具来帮助回答问题:\n"
        tools_section += tools_description + "\n"
        
        tools_section += "\n## 工具调用格式\n"
        tools_section += "当需要使用工具时，请使用以下格式:\n"
        tools_section += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"
        tools_section += "例如:`[TOOL_CALL:calculator:2+3*4]` 或 `[TOOL_CALL:search:Python编程]`\n\n"
        tools_section += "工具调用结果会自动插入到对话中，然后你可以基于结果继续回答。\n"
        
        return base_prompt + tools_section
    
    def _run_with_tools(
        self, 
        messages: list, 
        input_text: str, 
        max_tool_iterations: int, 
        **kwargs
    ) -> str:
        """
        支持工具调用的运行逻辑
        
        Args:
            messages: 消息列表
            input_text: 用户输入
            max_tool_iterations: 最大迭代次数
            **kwargs: LLM 参数
            
        Returns:
            最终响应
        """
        current_iteration = 0
        final_response = ""
        
        while current_iteration < max_tool_iterations:
            # 调用LLM
            response = self.llm.invoke(messages, **kwargs)
            
            # 检查是否有工具调用
            tool_calls = self._parse_tool_calls(response)
            
            if tool_calls:
                print(f"🔧 检测到 {len(tool_calls)} 个工具调用")
                # 执行所有工具调用并收集结果
                tool_results = []
                clean_response = response
                
                for call in tool_calls:
                    result = self._execute_tool_call(call['tool_name'], call['parameters'])
                    tool_results.append(result)
                    # 从响应中移除工具调用标记
                    clean_response = clean_response.replace(call['original'], "")
                
                # 构建包含工具结果的消息
                messages.append({"role": "assistant", "content": clean_response})
                
                # 添加工具结果
                tool_results_text = "\n\n".join(tool_results)
                messages.append({
                    "role": "user", 
                    "content": f"工具执行结果:\n{tool_results_text}\n\n请基于这些结果给出完整的回答。"
                })
                
                current_iteration += 1
                continue
            
            # 没有工具调用，这是最终回答
            final_response = response
            break
        
        # 如果超过最大迭代次数，获取最后一次回答
        if current_iteration >= max_tool_iterations and not final_response:
            final_response = self.llm.invoke(messages, **kwargs)
        
        # 保存到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_response, "assistant"))
        print(f"✅ {self.name} 响应完成")
        
        return final_response
    
    def _parse_tool_calls(self, text: str) -> list:
        """
        解析文本中的工具调用
        
        格式: [TOOL_CALL:tool_name:parameters]
        
        Args:
            text: 待解析文本
            
        Returns:
            工具调用列表
        """
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)
        
        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                'tool_name': tool_name.strip(),
                'parameters': parameters.strip(),
                'original': f'[TOOL_CALL:{tool_name}:{parameters}]'
            })
        
        return tool_calls
    
    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.tool_registry:
            return f"❌ 错误:未配置工具注册表"
        
        try:
            # 智能参数解析
            if tool_name == 'calculator':
                # 计算器工具直接传入表达式
                result = self.tool_registry.execute_tool(tool_name, parameters)
            else:
                # 其他工具使用智能参数解析
                param_dict = self._parse_tool_parameters(tool_name, parameters)
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    return f"❌ 错误:未找到工具 '{tool_name}'"
                result = tool.run(param_dict)
            
            return f"🔧 工具 {tool_name} 执行结果:\n{result}"
        
        except Exception as e:
            return f"❌ 工具调用失败:{str(e)}"
    
    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """
        智能解析工具参数
        
        支持格式:
        1. key=value
        2. key1=value1,key2=value2
        3. 直接值(根据工具类型推断键名)
        
        Args:
            tool_name: 工具名称
            parameters: 参数字符串
            
        Returns:
            参数字典
        """
        param_dict = {}
        
        if '=' in parameters:
            # 格式: key=value 或 key1=value1,key2=value2
            if ',' in parameters:
                # 多个参数
                pairs = parameters.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        param_dict[key.strip()] = value.strip()
            else:
                # 单个参数
                key, value = parameters.split('=', 1)
                param_dict[key.strip()] = value.strip()
        else:
            # 直接传入参数，根据工具类型智能推断
            if tool_name == 'search':
                param_dict = {'query': parameters}
            elif tool_name == 'memory':
                param_dict = {'action': 'search', 'query': parameters}
            else:
                param_dict = {'input': parameters}
        
        return param_dict
    
    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        """
        自定义的流式运行方法
        
        Args:
            input_text: 用户输入
            **kwargs: LLM 参数
            
        Yields:
            响应文本块
        """
        print(f"\n🌊 {self.name} 开始流式处理: {input_text}")
        
        messages = []
        
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": input_text})
        
        # 流式调用LLM
        full_response = ""
        print("📝 实时响应: ", end="")
        for chunk in self.llm.stream_invoke(messages, **kwargs):
            full_response += chunk
            print(chunk, end="", flush=True)
            yield chunk
        
        print()  # 换行
        
        # 保存完整对话到历史记录
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(full_response, "assistant"))
        print(f"✅ {self.name} 流式响应完成")
    
    def add_tool(self, tool) -> None:
        """添加工具到Agent(便利方法)"""
        if not self.tool_registry:
            self.tool_registry = ToolRegistry()
            self.enable_tool_calling = True
        
        self.tool_registry.register_tool(tool)
        print(f"🔧 工具 '{tool.name}' 已添加")
    
    def has_tools(self) -> bool:
        """检查是否有可用工具"""
        return self.enable_tool_calling and self.tool_registry is not None
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具(便利方法)"""
        if self.tool_registry:
            self.tool_registry.unregister(tool_name)
            return True
        return False
    
    def list_tools(self) -> list:
        """列出所有可用工具"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []


# 测试代码
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    print("="*60)
    print("测试自定义 SimpleAgent")
    print("="*60)
    
    # 加载环境变量
    load_dotenv()
    
    # 创建LLM实例
    print("\n1. 创建 LLM 实例...")
    llm = HelloAgentsLLM()
    
    # 测试1: 基础对话(无工具)
    print("\n" + "="*60)
    print("测试1: 基础对话(无工具)")
    print("="*60)
    agent1 = MySimpleAgent(
        name="基础助手",
        llm=llm,
        system_prompt="你是一个友好的AI助手"
    )
    
    response1 = agent1.run("你好，请简单介绍一下自己")
    print(f"\n回复: {response1}")
    
    print("\n" + "="*60)
    print("测试完成!")
