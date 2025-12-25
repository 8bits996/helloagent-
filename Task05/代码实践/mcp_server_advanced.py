"""
高级 MCP Server 实现
展示 MCP 的高级特性和实用功能

学习目标:
1. 掌握复杂工具的开发
2. 理解 Resources 的高级用法
3. 实现错误处理和日志
4. 状态管理和数据持久化
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# 创建高级 MCP Server
mcp = FastMCP("advanced-server")

# 模拟数据存储
_data_store: Dict[str, any] = {}
_operation_log: List[Dict] = []


# ============================================================================
# 工具组 1: 数据存储和管理
# ============================================================================

@mcp.tool()
def store_data(key: str, value: str) -> str:
    """
    存储键值对数据
    
    Args:
        key: 数据的键
        value: 数据的值
        
    Returns:
        操作结果
    """
    try:
        _data_store[key] = value
        _log_operation("store", f"key={key}")
        return f"✅ 成功存储: {key} = {value}"
    except Exception as e:
        return f"❌ 存储失败: {str(e)}"


@mcp.tool()
def get_data(key: str) -> str:
    """
    获取存储的数据
    
    Args:
        key: 数据的键
        
    Returns:
        存储的值或错误信息
    """
    try:
        if key in _data_store:
            _log_operation("get", f"key={key}")
            return f"📦 {key} = {_data_store[key]}"
        else:
            return f"⚠️ 键 '{key}' 不存在"
    except Exception as e:
        return f"❌ 获取失败: {str(e)}"


@mcp.tool()
def list_all_keys() -> str:
    """
    列出所有存储的键
    
    Returns:
        所有键的列表
    """
    try:
        if not _data_store:
            return "📭 数据存储为空"
        
        keys = list(_data_store.keys())
        _log_operation("list", f"count={len(keys)}")
        return f"📋 共有 {len(keys)} 个键:\n" + "\n".join(f"  - {k}" for k in keys)
    except Exception as e:
        return f"❌ 列出失败: {str(e)}"


@mcp.tool()
def delete_data(key: str) -> str:
    """
    删除存储的数据
    
    Args:
        key: 要删除的键
        
    Returns:
        操作结果
    """
    try:
        if key in _data_store:
            del _data_store[key]
            _log_operation("delete", f"key={key}")
            return f"🗑️ 成功删除: {key}"
        else:
            return f"⚠️ 键 '{key}' 不存在"
    except Exception as e:
        return f"❌ 删除失败: {str(e)}"


# ============================================================================
# 工具组 2: 文件操作
# ============================================================================

@mcp.tool()
def read_file(file_path: str, max_lines: int = 100) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        max_lines: 最大读取行数(默认100)
        
    Returns:
        文件内容或错误信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"❌ 文件不存在: {file_path}"
        
        if not path.is_file():
            return f"❌ 不是文件: {file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]
        
        content = ''.join(lines)
        total_lines = len(lines)
        
        _log_operation("read_file", f"path={file_path}, lines={total_lines}")
        
        return f"""📄 文件: {file_path}
📊 读取行数: {total_lines}
{'⚠️ (已截断至前' + str(max_lines) + '行)' if len(lines) == max_lines else ''}

内容:
{content}"""
    except UnicodeDecodeError:
        return f"❌ 文件编码错误: 无法读取为文本文件"
    except Exception as e:
        return f"❌ 读取失败: {str(e)}"


@mcp.tool()
def list_directory(directory_path: str) -> str:
    """
    列出目录内容
    
    Args:
        directory_path: 目录路径
        
    Returns:
        目录内容列表
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"❌ 目录不存在: {directory_path}"
        
        if not path.is_dir():
            return f"❌ 不是目录: {directory_path}"
        
        items = list(path.iterdir())
        dirs = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]
        
        _log_operation("list_dir", f"path={directory_path}")
        
        result = f"""📁 目录: {directory_path}
📊 统计: {len(dirs)} 个子目录, {len(files)} 个文件

子目录:
"""
        for d in sorted(dirs)[:20]:
            result += f"  📁 {d.name}\n"
        
        if len(dirs) > 20:
            result += f"  ... (还有 {len(dirs)-20} 个)\n"
        
        result += "\n文件:\n"
        for f in sorted(files)[:20]:
            size = f.stat().st_size
            result += f"  📄 {f.name} ({_format_size(size)})\n"
        
        if len(files) > 20:
            result += f"  ... (还有 {len(files)-20} 个)\n"
        
        return result
    except Exception as e:
        return f"❌ 列出失败: {str(e)}"


@mcp.tool()
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        append: 是否追加模式(默认False)
        
    Returns:
        操作结果
    """
    try:
        path = Path(file_path)
        mode = 'a' if append else 'w'
        
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        
        _log_operation("write_file", f"path={file_path}, append={append}")
        
        action = "追加到" if append else "写入"
        return f"✅ 成功{action}文件: {file_path}\n📊 写入字节数: {len(content.encode('utf-8'))}"
    except Exception as e:
        return f"❌ 写入失败: {str(e)}"


# ============================================================================
# 工具组 3: 数据处理
# ============================================================================

@mcp.tool()
def json_parse(json_string: str) -> str:
    """
    解析 JSON 字符串
    
    Args:
        json_string: JSON 格式的字符串
        
    Returns:
        解析后的格式化 JSON 或错误信息
    """
    try:
        data = json.loads(json_string)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        _log_operation("json_parse", "success")
        
        return f"""✅ JSON 解析成功

格式化结果:
{formatted}

类型: {type(data).__name__}
"""
    except json.JSONDecodeError as e:
        return f"❌ JSON 解析失败: {str(e)}"
    except Exception as e:
        return f"❌ 处理失败: {str(e)}"


@mcp.tool()
def text_stats(text: str) -> str:
    """
    统计文本信息
    
    Args:
        text: 要分析的文本
        
    Returns:
        文本统计信息
    """
    try:
        char_count = len(text)
        word_count = len(text.split())
        line_count = text.count('\n') + 1
        unique_chars = len(set(text))
        
        _log_operation("text_stats", f"chars={char_count}")
        
        return f"""📊 文本统计

字符数: {char_count}
单词数: {word_count}
行数: {line_count}
唯一字符: {unique_chars}

前100个字符:
{text[:100]}{'...' if len(text) > 100 else ''}
"""
    except Exception as e:
        return f"❌ 统计失败: {str(e)}"


@mcp.tool()
def batch_calculate(numbers: str, operation: str) -> str:
    """
    批量数学计算
    
    Args:
        numbers: 逗号分隔的数字列表,如 "1,2,3,4,5"
        operation: 操作类型 (sum/avg/max/min/product)
        
    Returns:
        计算结果
    """
    try:
        nums = [float(n.strip()) for n in numbers.split(',')]
        
        if operation == "sum":
            result = sum(nums)
        elif operation == "avg":
            result = sum(nums) / len(nums)
        elif operation == "max":
            result = max(nums)
        elif operation == "min":
            result = min(nums)
        elif operation == "product":
            result = 1
            for n in nums:
                result *= n
        else:
            return f"❌ 不支持的操作: {operation}"
        
        _log_operation("batch_calc", f"op={operation}, count={len(nums)}")
        
        return f"""🧮 批量计算结果

数据: {nums}
操作: {operation}
结果: {result}
"""
    except ValueError:
        return "❌ 数字格式错误"
    except Exception as e:
        return f"❌ 计算失败: {str(e)}"


# ============================================================================
# 工具组 4: 系统信息
# ============================================================================

@mcp.tool()
def get_timestamp() -> str:
    """
    获取当前时间戳
    
    Returns:
        当前时间的多种格式
    """
    now = datetime.now()
    
    _log_operation("timestamp", "")
    
    return f"""🕐 当前时间

本地时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
ISO 格式: {now.isoformat()}
Unix 时间戳: {int(now.timestamp())}
"""


@mcp.tool()
def server_stats() -> str:
    """
    获取 Server 统计信息
    
    Returns:
        Server 的统计数据
    """
    total_ops = len(_operation_log)
    data_count = len(_data_store)
    
    op_types = {}
    for op in _operation_log:
        op_type = op['type']
        op_types[op_type] = op_types.get(op_type, 0) + 1
    
    result = f"""📊 Server 统计信息

数据存储: {data_count} 个键值对
操作总数: {total_ops} 次

操作分布:
"""
    for op_type, count in sorted(op_types.items(), key=lambda x: x[1], reverse=True):
        result += f"  {op_type}: {count} 次\n"
    
    if _operation_log:
        last_op = _operation_log[-1]
        result += f"\n最后操作: {last_op['type']} ({last_op['time']})"
    
    return result


@mcp.tool()
def operation_history(limit: int = 10) -> str:
    """
    获取操作历史
    
    Args:
        limit: 返回的最大记录数(默认10)
        
    Returns:
        操作历史记录
    """
    if not _operation_log:
        return "📭 暂无操作历史"
    
    recent = _operation_log[-limit:]
    
    result = f"📜 最近 {len(recent)} 条操作记录:\n\n"
    for i, op in enumerate(reversed(recent), 1):
        result += f"{i}. [{op['time']}] {op['type']}"
        if op['details']:
            result += f" - {op['details']}"
        result += "\n"
    
    return result


# ============================================================================
# 资源定义
# ============================================================================

@mcp.resource("data://{key}")
def get_data_resource(key: str) -> str:
    """
    通过 Resource 接口访问数据
    
    Args:
        key: 数据键
        
    Returns:
        数据值
    """
    if key in _data_store:
        return _data_store[key]
    return f"Key '{key}' not found"


@mcp.resource("config://server")
def get_server_config() -> str:
    """
    获取 Server 配置信息
    
    Returns:
        Server 配置的 JSON 字符串
    """
    config = {
        "name": "advanced-server",
        "version": "1.0.0",
        "features": [
            "数据存储",
            "文件操作",
            "数据处理",
            "系统信息"
        ],
        "tool_count": 14,
        "uptime": time.time()
    }
    return json.dumps(config, indent=2, ensure_ascii=False)


# ============================================================================
# 提示词模板
# ============================================================================

@mcp.prompt()
def code_review_prompt(code: str, language: str = "python") -> str:
    """
    代码审查提示词
    
    Args:
        code: 要审查的代码
        language: 编程语言(默认python)
        
    Returns:
        代码审查提示词
    """
    return f"""请对以下 {language} 代码进行详细审查:

```{language}
{code}
```

请从以下方面进行审查:
1. 代码正确性
2. 性能优化
3. 安全问题
4. 代码风格
5. 最佳实践
6. 潜在 Bug

请提供:
- 问题列表(如果有)
- 改进建议
- 优化后的代码(如果需要)
"""


@mcp.prompt()
def data_analysis_prompt(data: str) -> str:
    """
    数据分析提示词
    
    Args:
        data: 要分析的数据
        
    Returns:
        数据分析提示词
    """
    return f"""请分析以下数据:

{data}

请提供:
1. 数据概览(类型、规模、特征)
2. 统计分析(均值、中位数、分布等)
3. 异常值识别
4. 数据质量评估
5. 可能的洞察和发现
6. 进一步分析建议
"""


# ============================================================================
# 辅助函数
# ============================================================================

def _log_operation(op_type: str, details: str = ""):
    """记录操作日志"""
    _operation_log.append({
        "type": op_type,
        "time": datetime.now().strftime('%H:%M:%S'),
        "details": details
    })


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# ============================================================================
# 运行 Server
# ============================================================================

if __name__ == "__main__":
    # 使用 stderr 输出启动信息(stdout 用于 JSON-RPC)
    print("高级 MCP Server 启动中...", file=sys.stderr)
    print("提供 14 个工具, 2 个资源, 2 个提示词", file=sys.stderr)
    
    mcp.run(transport="stdio")
