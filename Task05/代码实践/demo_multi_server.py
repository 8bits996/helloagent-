"""
多 Server 实战演示: 智能文件分析助手

场景:
用户想要分析一个项目目录,找出:
1. 所有 Python 文件
2. 统计代码行数
3. 分析常用的函数名
4. 生成项目报告

这个任务需要协调两个 Server:
- file-server: 文件操作
- data-server: 数据分析
"""

import asyncio
import tempfile
from pathlib import Path
from mcp_multi_server_manager import MultiServerManager, ServerConfig


async def scenario_1_file_analysis():
    """场景1: 文件分析流程"""
    
    print("=" * 80)
    print("🎯 场景1: 智能文件分析")
    print("=" * 80)
    print()
    
    # 1. 初始化多 Server 管理器
    manager = MultiServerManager()
    
    configs = [
        ServerConfig(
            name="file-server",
            command="python",
            args=["mcp_server_file.py"],
            description="文件操作"
        ),
        ServerConfig(
            name="data-server",
            command="python",
            args=["mcp_server_data.py"],
            description="数据分析"
        )
    ]
    
    await manager.connect_all(configs)
    
    # 2. 创建测试文件
    print("📝 步骤1: 创建测试项目文件")
    print("-" * 80)
    
    test_files = {
        "main.py": """
def calculate_sum(numbers):
    \"\"\"计算数字总和\"\"\"
    return sum(numbers)

def calculate_average(numbers):
    \"\"\"计算平均值\"\"\"
    return sum(numbers) / len(numbers)

def main():
    data = [1, 2, 3, 4, 5]
    print(f"Sum: {calculate_sum(data)}")
    print(f"Average: {calculate_average(data)}")

if __name__ == "__main__":
    main()
""",
        "utils.py": """
def read_config(file_path):
    \"\"\"读取配置文件\"\"\"
    with open(file_path) as f:
        return f.read()

def write_log(message):
    \"\"\"写入日志\"\"\"
    with open("app.log", "a") as f:
        f.write(message + "\\n")
""",
        "README.md": """
# 测试项目

这是一个用于演示 MCP 多 Server 协作的测试项目。

## 功能
- 数学计算
- 文件操作
- 日志记录
"""
    }
    
    for filename, content in test_files.items():
        result = await manager.call_tool(
            "write_file",
            {"file_path": filename, "content": content}
        )
        print(f"  ✓ 创建 {filename}")
    
    print()
    
    # 3. 列出项目文件
    print("📂 步骤2: 列出项目文件")
    print("-" * 80)
    
    result = await manager.call_tool(
        "list_directory",
        {"directory_path": ".", "pattern": "*.py"}
    )
    print(result)
    
    # 4. 读取并分析每个 Python 文件
    print("\n📊 步骤3: 分析 Python 文件")
    print("-" * 80)
    
    for filename in ["main.py", "utils.py"]:
        print(f"\n分析: {filename}")
        print("-" * 40)
        
        # 读取文件
        content_result = await manager.call_tool(
            "read_file",
            {"file_path": filename}
        )
        
        # 提取内容(简单处理)
        lines = content_result.split('\n')
        content = '\n'.join([line for line in lines if not line.startswith('📄') and not line.startswith('📊')])
        
        # 分析文本
        analysis_result = await manager.call_tool(
            "analyze_text",
            {"text": content}
        )
        print(analysis_result)
    
    # 5. 搜索所有函数定义
    print("\n🔍 步骤4: 搜索函数定义")
    print("-" * 80)
    
    result = await manager.call_tool(
        "search_files",
        {
            "directory_path": ".",
            "keyword": "def ",
            "file_pattern": "*.py"
        }
    )
    print(result)
    
    # 6. 生成项目报告
    print("\n📝 步骤5: 生成项目报告")
    print("-" * 80)
    
    report = f"""# 项目分析报告

生成时间: {await manager.call_tool("get_timestamp", {})}

## 文件统计
- Python 文件: 2 个
- Markdown 文件: 1 个

## 代码分析
见上述详细分析

## 总结
本项目包含基础的数学计算和文件操作功能。
"""
    
    result = await manager.call_tool(
        "write_file",
        {"file_path": "PROJECT_REPORT.md", "content": report}
    )
    print(result)
    
    # 清理测试文件
    print("\n🧹 清理测试文件...")
    for filename in list(test_files.keys()) + ["PROJECT_REPORT.md"]:
        try:
            Path(filename).unlink()
            print(f"  ✓ 删除 {filename}")
        except:
            pass
    
    await manager.close()
    print("\n✅ 场景1 完成!")


async def scenario_2_data_processing():
    """场景2: 数据处理流程"""
    
    print("\n\n")
    print("=" * 80)
    print("🎯 场景2: 数据处理与分析")
    print("=" * 80)
    print()
    
    # 初始化
    manager = MultiServerManager()
    
    configs = [
        ServerConfig(
            name="file-server",
            command="python",
            args=["mcp_server_file.py"],
            description="文件操作"
        ),
        ServerConfig(
            name="data-server",
            command="python",
            args=["mcp_server_data.py"],
            description="数据分析"
        )
    ]
    
    await manager.connect_all(configs)
    
    # 1. 创建数据文件
    print("📝 步骤1: 创建数据文件")
    print("-" * 80)
    
    data_content = """23,45,67,89,12,34,56,78,90,21,43,65,87,19,31,53,75,97,14,36"""
    
    result = await manager.call_tool(
        "write_file",
        {"file_path": "data.txt", "content": data_content}
    )
    print(result)
    
    # 2. 读取数据
    print("\n📖 步骤2: 读取数据")
    print("-" * 80)
    
    result = await manager.call_tool(
        "read_file",
        {"file_path": "data.txt"}
    )
    print(result)
    
    # 3. 统计分析
    print("\n📊 步骤3: 统计分析")
    print("-" * 80)
    
    result = await manager.call_tool(
        "calculate_stats",
        {"numbers": data_content}
    )
    print(result)
    
    # 4. 创建 JSON 报告
    print("\n📝 步骤4: 生成 JSON 报告")
    print("-" * 80)
    
    json_data = """{
  "project": "数据分析示例",
  "data_file": "data.txt",
  "record_count": 20,
  "statistics": {
    "mean": 52.3,
    "median": 54.5,
    "min": 12,
    "max": 97
  }
}"""
    
    result = await manager.call_tool(
        "write_file",
        {"file_path": "report.json", "content": json_data}
    )
    print(result)
    
    # 5. 解析 JSON
    print("\n🔍 步骤5: 解析 JSON 报告")
    print("-" * 80)
    
    result = await manager.call_tool(
        "parse_json",
        {"json_string": json_data}
    )
    print(result)
    
    # 清理
    print("\n🧹 清理测试文件...")
    for filename in ["data.txt", "report.json"]:
        try:
            Path(filename).unlink()
            print(f"  ✓ 删除 {filename}")
        except:
            pass
    
    await manager.close()
    print("\n✅ 场景2 完成!")


async def scenario_3_complex_workflow():
    """场景3: 复杂工作流 - 日志分析"""
    
    print("\n\n")
    print("=" * 80)
    print("🎯 场景3: 复杂工作流 - 日志文件分析")
    print("=" * 80)
    print()
    
    manager = MultiServerManager()
    
    configs = [
        ServerConfig(
            name="file-server",
            command="python",
            args=["mcp_server_file.py"],
            description="文件操作"
        ),
        ServerConfig(
            name="data-server",
            command="python",
            args=["mcp_server_data.py"],
            description="数据分析"
        )
    ]
    
    await manager.connect_all(configs)
    
    # 1. 创建日志文件
    print("📝 步骤1: 创建模拟日志文件")
    print("-" * 80)
    
    log_content = """2024-12-24 10:00:01 INFO: Application started
2024-12-24 10:00:05 INFO: User login: user@example.com
2024-12-24 10:00:10 ERROR: Database connection failed
2024-12-24 10:00:15 WARNING: High memory usage: 85%
2024-12-24 10:00:20 INFO: Request processed: /api/users
2024-12-24 10:00:25 ERROR: API timeout: /api/orders
2024-12-24 10:00:30 INFO: Cache cleared
2024-12-24 10:00:35 ERROR: Invalid authentication token
2024-12-24 10:00:40 WARNING: Slow query detected: 2.5s
2024-12-24 10:00:45 INFO: User logout: user@example.com
"""
    
    result = await manager.call_tool(
        "write_file",
        {"file_path": "app.log", "content": log_content}
    )
    print(result)
    
    # 2. 读取日志
    print("\n📖 步骤2: 读取日志文件")
    print("-" * 80)
    
    result = await manager.call_tool(
        "read_file",
        {"file_path": "app.log"}
    )
    print(result)
    
    # 3. 分析日志内容
    print("\n📊 步骤3: 分析日志内容")
    print("-" * 80)
    
    result = await manager.call_tool(
        "analyze_text",
        {"text": log_content}
    )
    print(result)
    
    # 4. 提取错误日志中的模式
    print("\n🔍 步骤4: 提取邮箱地址")
    print("-" * 80)
    
    result = await manager.call_tool(
        "extract_patterns",
        {"text": log_content, "pattern_type": "email"}
    )
    print(result)
    
    # 5. 生成分析报告
    print("\n📝 步骤5: 生成分析报告")
    print("-" * 80)
    
    report = """# 日志分析报告

## 概览
- 总行数: 10
- 时间范围: 2024-12-24 10:00:01 - 10:00:45

## 问题统计
- ERROR: 3 次
- WARNING: 2 次
- INFO: 5 次

## 关键问题
1. 数据库连接失败
2. API 超时
3. 认证失败

## 建议
- 检查数据库连接配置
- 优化 API 性能
- 审查认证机制
"""
    
    result = await manager.call_tool(
        "write_file",
        {"file_path": "log_analysis_report.md", "content": report}
    )
    print(result)
    
    # 6. 文件信息
    print("\n📋 步骤6: 查看报告文件信息")
    print("-" * 80)
    
    result = await manager.call_tool(
        "file_info",
        {"file_path": "log_analysis_report.md"}
    )
    print(result)
    
    # 清理
    print("\n🧹 清理测试文件...")
    for filename in ["app.log", "log_analysis_report.md"]:
        try:
            Path(filename).unlink()
            print(f"  ✓ 删除 {filename}")
        except:
            pass
    
    await manager.close()
    print("\n✅ 场景3 完成!")


async def main():
    """主函数 - 运行所有场景"""
    
    print("🚀 多 MCP Server 协作演示")
    print("=" * 80)
    print()
    print("本演示将展示如何使用多个 MCP Server 协同完成复杂任务")
    print()
    
    try:
        # 运行场景1
        await scenario_1_file_analysis()
        
        # 运行场景2
        await scenario_2_data_processing()
        
        # 运行场景3
        await scenario_3_complex_workflow()
        
        # 总结
        print("\n\n")
        print("=" * 80)
        print("🎉 所有场景演示完成!")
        print("=" * 80)
        print()
        print("🎓 学习要点:")
        print("  1. 多 Server 管理器统一管理多个 MCP Server")
        print("  2. 工具自动路由到正确的 Server")
        print("  3. 不同 Server 的工具可以协同工作")
        print("  4. 实现了复杂的工作流编排")
        print()
        print("💡 关键收获:")
        print("  - file-server 专注文件操作")
        print("  - data-server 专注数据分析")
        print("  - MultiServerManager 统一协调")
        print("  - 工具组合产生更强大的能力")
        print()
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
