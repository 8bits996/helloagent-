"""
自定义计算器工具
Task02 实践 - 工具系统开发
"""
import ast
import operator
import math
from typing import Dict, Any

# 尝试导入 hello_agents 的工具类
try:
    from hello_agents.tools import Tool, ToolParameter
except ImportError:
    # 如果导入失败,使用兼容的简化版本
    from abc import ABC, abstractmethod
    from pydantic import BaseModel
    from typing import List
    
    class ToolParameter(BaseModel):
        """工具参数定义"""
        name: str
        type: str
        description: str
        required: bool = True
        default: Any = None
    
    class Tool(ABC):
        """工具基类"""
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
        
        @abstractmethod
        def run(self, parameters: Dict[str, Any]) -> str:
            """执行工具"""
            pass
        
        @abstractmethod
        def get_parameters(self) -> List[ToolParameter]:
            """获取工具参数定义"""
            pass


def _eval_node(node, operators, functions):
    """递归计算AST节点 - Python 3.8+ 兼容版本"""
    if isinstance(node, ast.Constant):  # 数字/常量 (Python 3.8+)
        return node.value
    elif isinstance(node, ast.BinOp):  # 二元运算
        left = _eval_node(node.left, operators, functions)
        right = _eval_node(node.right, operators, functions)
        op_type = type(node.op)
        if op_type in operators:
            return operators[op_type](left, right)
        else:
            raise ValueError(f"不支持的运算符: {op_type}")
    elif isinstance(node, ast.UnaryOp):  # 一元运算
        operand = _eval_node(node.operand, operators, functions)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        else:
            raise ValueError(f"不支持的一元运算符: {type(node.op)}")
    elif isinstance(node, ast.Call):  # 函数调用
        func_name = node.func.id
        if func_name in functions:
            args = [_eval_node(arg, operators, functions) for arg in node.args]
            return functions[func_name](*args)
        else:
            raise ValueError(f"不支持的函数: {func_name}")
    elif isinstance(node, ast.Name):  # 变量名(如pi)
        if node.id in functions:
            return functions[node.id]
        else:
            raise ValueError(f"未定义的变量: {node.id}")
    else:
        raise ValueError(f"不支持的表达式类型: {type(node)}")


def my_calculate(expression: str) -> str:
    """
    简单的数学计算函数
    
    Args:
        expression: 数学表达式字符串
        
    Returns:
        计算结果字符串
        
    Examples:
        >>> my_calculate("2 + 3 * 4")
        '14'
        >>> my_calculate("sqrt(16)")
        '4.0'
    """
    if not expression.strip():
        return "❌ 错误: 计算表达式不能为空"
    
    # 支持的基本运算
    operators = {
        ast.Add: operator.add,      # +
        ast.Sub: operator.sub,      # -
        ast.Mult: operator.mul,     # *
        ast.Div: operator.truediv,  # /
        ast.Pow: operator.pow,      # **
        ast.Mod: operator.mod,      # %
    }
    
    # 支持的基本函数
    functions = {
        'sqrt': math.sqrt,
        'pi': math.pi,
        'e': math.e,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'abs': abs,
        'round': round,
    }
    
    try:
        # 清理表达式
        expression = expression.strip()
        
        # 解析表达式为AST
        node = ast.parse(expression, mode='eval')
        
        # 计算结果
        result = _eval_node(node.body, operators, functions)
        
        return f"✅ 计算结果: {result}"
        
    except SyntaxError as e:
        return f"❌ 语法错误: {str(e)}"
    except ValueError as e:
        return f"❌ 计算错误: {str(e)}"
    except ZeroDivisionError:
        return "❌ 错误: 除数不能为零"
    except Exception as e:
        return f"❌ 未知错误: {str(e)}"


class MyCalculatorTool(Tool):
    """
    自定义计算器工具类
    继承自 Tool 基类,实现完整的工具接口
    """
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算。支持基本运算(+,-,*,/,**,%)和函数(sqrt,sin,cos,tan,abs,round)。示例: '2+3*4' 或 'sqrt(16)'"
        )
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """
        执行工具
        
        Args:
            parameters: 参数字典,应包含 'expression' 或 'input' 键
            
        Returns:
            计算结果字符串
        """
        # 兼容多种参数格式
        expression = parameters.get('expression') or parameters.get('input') or parameters.get('query', '')
        
        # 如果parameters直接是字符串(简化调用)
        if isinstance(parameters, str):
            expression = parameters
        
        if not expression:
            return "❌ 错误: 未提供计算表达式"
        
        return my_calculate(expression)
    
    def get_parameters(self) -> list:
        """
        获取工具参数定义
        
        Returns:
            参数定义列表
        """
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="要计算的数学表达式,如 '2+3*4' 或 'sqrt(16)'",
                required=True
            )
        ]


# 测试代码
if __name__ == "__main__":
    print("="*60)
    print("测试自定义计算器工具")
    print("="*60)
    
    # 测试1: 使用函数
    print("\n测试1: 使用函数方式")
    print(my_calculate("2 + 3 * 4"))
    print(my_calculate("sqrt(16)"))
    print(my_calculate("2 ** 8"))
    print(my_calculate("10 % 3"))
    
    # 测试2: 使用工具类
    print("\n测试2: 使用工具类方式")
    calc_tool = MyCalculatorTool()
    print(f"工具名称: {calc_tool.name}")
    print(f"工具描述: {calc_tool.description}")
    print(f"参数定义: {calc_tool.get_parameters()}")
    
    # 测试工具执行
    print("\n执行测试:")
    print(calc_tool.run({"expression": "100 / 4"}))
    print(calc_tool.run({"expression": "sin(pi/2)"}))
    
    # 测试错误处理
    print("\n错误处理测试:")
    print(calc_tool.run({"expression": "1 / 0"}))
    print(calc_tool.run({"expression": "invalid"}))
    print(calc_tool.run({"expression": ""}))
    
    print("\n" + "="*60)
    print("测试完成!")
