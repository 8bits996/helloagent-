"""
文件操作 MCP Server
专注于文件和目录操作

功能:
1. 文件读写
2. 目录列出
3. 文件搜索
4. 批量操作
"""

import sys
import json
from pathlib import Path
from typing import List
from mcp.server.fastmcp import FastMCP

# 创建文件操作 Server
mcp = FastMCP("file-server")


@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码(默认utf-8)
        
    Returns:
        文件内容或错误信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"❌ 文件不存在: {file_path}"
        
        if not path.is_file():
            return f"❌ 不是文件: {file_path}"
        
        content = path.read_text(encoding=encoding)
        size = path.stat().st_size
        
        return f"""✅ 文件读取成功
        
📄 文件: {path.name}
📊 大小: {size} 字节
📝 行数: {len(content.splitlines())}

内容:
{content}
"""
    except Exception as e:
        return f"❌ 读取失败: {str(e)}"


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
        
        path.write_text(content, encoding='utf-8') if not append else path.write_text(
            path.read_text(encoding='utf-8') + content if path.exists() else content,
            encoding='utf-8'
        )
        
        size = path.stat().st_size
        action = "追加" if append else "写入"
        
        return f"""✅ 文件{action}成功
        
📄 文件: {path.name}
📊 大小: {size} 字节
📝 写入: {len(content)} 字符
"""
    except Exception as e:
        return f"❌ 写入失败: {str(e)}"


@mcp.tool()
def list_directory(directory_path: str, pattern: str = "*") -> str:
    """
    列出目录内容
    
    Args:
        directory_path: 目录路径
        pattern: 文件匹配模式(默认*)
        
    Returns:
        目录内容列表
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"❌ 目录不存在: {directory_path}"
        
        if not path.is_dir():
            return f"❌ 不是目录: {directory_path}"
        
        # 获取所有匹配的项
        items = list(path.glob(pattern))
        dirs = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]
        
        result = f"""📁 目录: {path.name if path.name else path}
📊 统计: {len(dirs)} 个目录, {len(files)} 个文件

"""
        
        if dirs:
            result += "子目录:\n"
            for d in sorted(dirs)[:10]:
                result += f"  📁 {d.name}\n"
            if len(dirs) > 10:
                result += f"  ... 还有 {len(dirs)-10} 个\n"
        
        if files:
            result += "\n文件:\n"
            for f in sorted(files)[:10]:
                size = f.stat().st_size
                result += f"  📄 {f.name} ({_format_size(size)})\n"
            if len(files) > 10:
                result += f"  ... 还有 {len(files)-10} 个\n"
        
        return result
    except Exception as e:
        return f"❌ 列出失败: {str(e)}"


@mcp.tool()
def search_files(directory_path: str, keyword: str, file_pattern: str = "*.py") -> str:
    """
    搜索包含关键词的文件
    
    Args:
        directory_path: 搜索目录
        keyword: 搜索关键词
        file_pattern: 文件模式(默认*.py)
        
    Returns:
        搜索结果
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"❌ 目录不存在: {directory_path}"
        
        matches = []
        for file_path in path.rglob(file_pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if keyword in content:
                        # 找出包含关键词的行
                        lines = content.splitlines()
                        match_lines = [
                            (i+1, line.strip()) 
                            for i, line in enumerate(lines) 
                            if keyword in line
                        ]
                        matches.append({
                            'file': str(file_path.relative_to(path)),
                            'matches': match_lines[:3]  # 最多显示3行
                        })
                except:
                    pass  # 跳过无法读取的文件
        
        if not matches:
            return f"⚠️ 未找到包含 '{keyword}' 的文件"
        
        result = f"🔍 搜索结果: 找到 {len(matches)} 个文件\n\n"
        for match in matches[:5]:  # 最多显示5个文件
            result += f"📄 {match['file']}\n"
            for line_num, line in match['matches']:
                result += f"  L{line_num}: {line[:80]}...\n" if len(line) > 80 else f"  L{line_num}: {line}\n"
            result += "\n"
        
        if len(matches) > 5:
            result += f"... 还有 {len(matches)-5} 个文件\n"
        
        return result
    except Exception as e:
        return f"❌ 搜索失败: {str(e)}"


@mcp.tool()
def file_info(file_path: str) -> str:
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"❌ 文件不存在: {file_path}"
        
        stat = path.stat()
        
        from datetime import datetime
        
        info = f"""📄 文件信息
        
名称: {path.name}
路径: {path.absolute()}
大小: {_format_size(stat.st_size)}
类型: {'目录' if path.is_dir() else '文件'}
创建时间: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
修改时间: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                info += f"行数: {len(content.splitlines())}\n"
                info += f"字符数: {len(content)}\n"
            except:
                info += "编码: 非文本文件\n"
        
        return info
    except Exception as e:
        return f"❌ 获取信息失败: {str(e)}"


# 资源定义
@mcp.resource("file://{path}")
def get_file_resource(path: str) -> str:
    """通过 Resource 接口访问文件"""
    try:
        return Path(path).read_text(encoding='utf-8')
    except Exception as e:
        return f"Error: {str(e)}"


# 辅助函数
def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    print("文件操作 MCP Server 启动中...", file=sys.stderr)
    mcp.run(transport="stdio")
