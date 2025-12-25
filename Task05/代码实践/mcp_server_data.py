"""
数据分析 MCP Server
专注于数据处理和分析

功能:
1. 文本分析
2. 统计计算
3. JSON 处理
4. 数据转换
"""

import sys
import json
import re
from collections import Counter
from typing import Dict, List
from mcp.server.fastmcp import FastMCP

# 创建数据分析 Server
mcp = FastMCP("data-server")


@mcp.tool()
def analyze_text(text: str) -> str:
    """
    分析文本内容
    
    Args:
        text: 要分析的文本
        
    Returns:
        详细的文本分析结果
    """
    try:
        # 基础统计
        char_count = len(text)
        line_count = text.count('\n') + 1
        word_count = len(text.split())
        
        # 字符类型统计
        letter_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        
        # 词频分析
        words = re.findall(r'\w+', text.lower())
        word_freq = Counter(words).most_common(10)
        
        result = f"""📊 文本分析结果

基础统计:
  字符总数: {char_count}
  行数: {line_count}
  单词数: {word_count}
  字母数: {letter_count}
  数字数: {digit_count}
  空格数: {space_count}

词频统计 (Top 10):
"""
        for word, count in word_freq:
            result += f"  {word}: {count} 次\n"
        
        return result
    except Exception as e:
        return f"❌ 分析失败: {str(e)}"


@mcp.tool()
def calculate_stats(numbers: str) -> str:
    """
    计算数字统计信息
    
    Args:
        numbers: 逗号分隔的数字列表
        
    Returns:
        统计结果
    """
    try:
        nums = [float(n.strip()) for n in numbers.split(',')]
        
        if not nums:
            return "❌ 没有提供数字"
        
        total = sum(nums)
        count = len(nums)
        mean = total / count
        sorted_nums = sorted(nums)
        
        # 中位数
        if count % 2 == 0:
            median = (sorted_nums[count//2-1] + sorted_nums[count//2]) / 2
        else:
            median = sorted_nums[count//2]
        
        # 方差和标准差
        variance = sum((x - mean) ** 2 for x in nums) / count
        std_dev = variance ** 0.5
        
        result = f"""🔢 统计结果

数据: {nums}

基础统计:
  数量: {count}
  总和: {total}
  平均值: {mean:.2f}
  中位数: {median:.2f}
  最小值: {min(nums)}
  最大值: {max(nums)}
  范围: {max(nums) - min(nums)}

离散度:
  方差: {variance:.2f}
  标准差: {std_dev:.2f}
"""
        return result
    except ValueError:
        return "❌ 数字格式错误"
    except Exception as e:
        return f"❌ 计算失败: {str(e)}"


@mcp.tool()
def parse_json(json_string: str) -> str:
    """
    解析和格式化 JSON
    
    Args:
        json_string: JSON 字符串
        
    Returns:
        格式化的 JSON 和分析结果
    """
    try:
        data = json.loads(json_string)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        # 分析 JSON 结构
        def analyze_structure(obj, depth=0):
            if isinstance(obj, dict):
                return f"对象 ({len(obj)} 个键)"
            elif isinstance(obj, list):
                return f"数组 ({len(obj)} 个元素)"
            elif isinstance(obj, str):
                return f"字符串 ({len(obj)} 字符)"
            elif isinstance(obj, (int, float)):
                return "数字"
            elif isinstance(obj, bool):
                return "布尔值"
            elif obj is None:
                return "null"
            return "未知类型"
        
        structure = analyze_structure(data)
        
        result = f"""✅ JSON 解析成功

类型: {structure}

格式化 JSON:
{formatted}
"""
        return result
    except json.JSONDecodeError as e:
        return f"❌ JSON 解析失败: {str(e)}"
    except Exception as e:
        return f"❌ 处理失败: {str(e)}"


@mcp.tool()
def compare_texts(text1: str, text2: str) -> str:
    """
    比较两个文本
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        
    Returns:
        比较结果
    """
    try:
        # 基础对比
        len1, len2 = len(text1), len(text2)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # 相似度计算(简单版本)
        common_words = words1 & words2
        total_words = words1 | words2
        similarity = len(common_words) / len(total_words) * 100 if total_words else 0
        
        result = f"""📊 文本比较结果

长度对比:
  文本1: {len1} 字符
  文本2: {len2} 字符
  差异: {abs(len1-len2)} 字符

单词对比:
  文本1: {len(words1)} 个唯一单词
  文本2: {len(words2)} 个唯一单词
  共同单词: {len(common_words)} 个
  
相似度: {similarity:.1f}%

共同单词:
  {', '.join(list(common_words)[:10])}
  {'...' if len(common_words) > 10 else ''}
"""
        return result
    except Exception as e:
        return f"❌ 比较失败: {str(e)}"


@mcp.tool()
def extract_patterns(text: str, pattern_type: str) -> str:
    """
    从文本中提取特定模式
    
    Args:
        text: 要分析的文本
        pattern_type: 模式类型 (email/url/phone/number)
        
    Returns:
        提取结果
    """
    try:
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://[^\s]+',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'number': r'\b\d+\.?\d*\b'
        }
        
        if pattern_type not in patterns:
            return f"❌ 不支持的模式类型: {pattern_type}\n支持: {', '.join(patterns.keys())}"
        
        matches = re.findall(patterns[pattern_type], text)
        
        if not matches:
            return f"⚠️ 未找到 {pattern_type} 模式"
        
        # 去重
        unique_matches = list(set(matches))
        
        result = f"""🔍 提取结果: {pattern_type}

找到 {len(matches)} 个匹配 (去重后 {len(unique_matches)} 个)

"""
        for i, match in enumerate(unique_matches[:20], 1):
            result += f"{i}. {match}\n"
        
        if len(unique_matches) > 20:
            result += f"... 还有 {len(unique_matches)-20} 个\n"
        
        return result
    except Exception as e:
        return f"❌ 提取失败: {str(e)}"


@mcp.tool()
def summarize_data(data: str) -> str:
    """
    数据摘要生成
    
    Args:
        data: 要摘要的数据(文本或JSON)
        
    Returns:
        数据摘要
    """
    try:
        # 尝试作为 JSON 解析
        try:
            json_data = json.loads(data)
            return _summarize_json(json_data)
        except:
            # 作为文本处理
            return _summarize_text(data)
    except Exception as e:
        return f"❌ 摘要失败: {str(e)}"


def _summarize_json(data) -> str:
    """JSON 数据摘要"""
    def count_types(obj):
        counts = {
            'objects': 0,
            'arrays': 0,
            'strings': 0,
            'numbers': 0,
            'booleans': 0,
            'nulls': 0
        }
        
        if isinstance(obj, dict):
            counts['objects'] += 1
            for value in obj.values():
                sub_counts = count_types(value)
                for key in counts:
                    counts[key] += sub_counts[key]
        elif isinstance(obj, list):
            counts['arrays'] += 1
            for item in obj:
                sub_counts = count_types(item)
                for key in counts:
                    counts[key] += sub_counts[key]
        elif isinstance(obj, str):
            counts['strings'] += 1
        elif isinstance(obj, (int, float)):
            counts['numbers'] += 1
        elif isinstance(obj, bool):
            counts['booleans'] += 1
        elif obj is None:
            counts['nulls'] += 1
        
        return counts
    
    counts = count_types(data)
    
    result = """📊 JSON 数据摘要

类型统计:
"""
    for type_name, count in counts.items():
        if count > 0:
            result += f"  {type_name}: {count}\n"
    
    return result


def _summarize_text(text: str) -> str:
    """文本数据摘要"""
    lines = text.splitlines()
    words = text.split()
    
    result = f"""📊 文本数据摘要

规模:
  字符数: {len(text)}
  行数: {len(lines)}
  单词数: {len(words)}
  
前3行:
"""
    for i, line in enumerate(lines[:3], 1):
        preview = line[:80] + '...' if len(line) > 80 else line
        result += f"  {i}. {preview}\n"
    
    return result


# 资源定义
@mcp.resource("stats://summary")
def get_stats_summary() -> str:
    """获取统计摘要"""
    return json.dumps({
        "server": "data-server",
        "capabilities": [
            "文本分析",
            "统计计算",
            "JSON 处理",
            "模式提取",
            "数据摘要"
        ]
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("数据分析 MCP Server 启动中...", file=sys.stderr)
    mcp.run(transport="stdio")
