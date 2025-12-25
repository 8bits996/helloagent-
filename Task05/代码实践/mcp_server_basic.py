"""
MCP Server 基础实现 - 使用 FastMCP
实现一个最简单的 MCP Server,包含基本的工具调用功能

学习目标:
1. 理解 MCP Server 的基本结构
2. 掌握工具注册和实现
3. 理解 FastMCP 的使用方式

FastMCP 特点:
- 简化的 API,使用装饰器定义工具
- 自动处理请求和响应
- 支持多种传输方式(stdio, streamable-http)
"""

from mcp.server.fastmcp import FastMCP

# 创建 MCP Server 实例
# name: Server 名称
mcp = FastMCP("basic-server")


# 使用 @mcp.tool() 装饰器定义工具
@mcp.tool()
def calculator(expression: str) -> str:
    """
    执行简单的数学计算
    
    Args:
        expression: 要计算的数学表达式,如 '2 + 2' 或 '10 * 5'
        
    Returns:
        计算结果
    """
    try:
        # 注意: eval 在生产环境中不安全,这里仅用于演示
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@mcp.tool()
def echo(message: str) -> str:
    """
    回显输入的文本
    
    Args:
        message: 要回显的消息
        
    Returns:
        回显的消息
    """
    return f"Echo: {message}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    计算两个数的和
    
    Args:
        a: 第一个数
        b: 第二个数
        
    Returns:
        两数之和
    """
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    计算两个数的乘积
    
    Args:
        a: 第一个数
        b: 第二个数
        
    Returns:
        两数之积
    """
    return a * b


# 添加一个资源示例
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    获取个性化问候语
    
    Args:
        name: 人名
        
    Returns:
        问候语
    """
    return f"你好, {name}! 欢迎使用 MCP Server。"


# 添加一个提示词模板示例
@mcp.prompt()
def math_helper(problem: str) -> str:
    """
    数学问题帮助提示词
    
    Args:
        problem: 数学问题描述
        
    Returns:
        提示词
    """
    return f"""请帮我解决这个数学问题:

问题: {problem}

请提供:
1. 解题思路
2. 详细步骤
3. 最终答案
"""


# 运行 Server
if __name__ == "__main__":
    # 注意: 使用 stdio 传输时,不能打印任何内容到 stdout
    # 因为 stdout 用于 JSON-RPC 通信
    # 如果需要调试,可以:
    # 1. 使用 stderr: import sys; print("debug", file=sys.stderr)
    # 2. 写入日志文件
    # 3. 使用 streamable-http 传输方式
    
    # 使用 stdio 传输方式运行
    # stdio: 通过标准输入输出通信,适合本地进程
    mcp.run(transport="stdio")
