"""
简化的多 Server 演示
展示多 Server 协作的核心概念

注意: 这是一个简化版本,用于教学演示
"""

import asyncio
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_two_servers():
    """
    演示两个 Server 协同工作
    
    场景: 文件分析流程
    1. 使用 file-server 读取文件
    2. 使用 data-server 分析内容
    """
    
    print("=" * 80)
    print("🎯 多 Server 协作演示: 文件分析流程")
    print("=" * 80)
    print()
    
    # 准备测试文件
    test_content = """Python is a high-level programming language.
It is widely used for web development, data analysis, and AI.
Python was created by Guido van Rossum in 1991.
The language emphasizes code readability and simplicity."""
    
    Path("test_analysis.txt").write_text(test_content, encoding='utf-8')
    print("✅ 创建测试文件: test_analysis.txt")
    print()
    
    # ========================================================================
    # Server 1: 文件操作 Server
    # ========================================================================
    
    print("📦 步骤1: 连接文件操作 Server")
    print("-" * 80)
    
    file_server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_file.py"]
    )
    
    async with stdio_client(file_server_params) as (file_read, file_write):
        async with ClientSession(file_read, file_write) as file_session:
            await file_session.initialize()
            
            print("✅ 文件 Server 连接成功")
            
            # 获取工具列表
            file_tools = await file_session.list_tools()
            print(f"发现 {len(file_tools.tools)} 个工具:")
            for tool in file_tools.tools:
                print(f"  - {tool.name}")
            print()
            
            # 使用文件 Server 读取文件
            print("📖 步骤2: 读取文件内容")
            print("-" * 80)
            
            result = await file_session.call_tool(
                "read_file",
                {"file_path": "test_analysis.txt"}
            )
            
            file_content = result.content[0].text
            print(file_content)
            print()
            
            # 提取纯文本内容(去除格式化信息)
            lines = file_content.split('\n')
            text_content = '\n'.join(
                line for line in lines 
                if not line.startswith(('📄', '📊', '📝', '内容:')) and line.strip()
            )
    
    # ========================================================================
    # Server 2: 数据分析 Server
    # ========================================================================
    
    print("📊 步骤3: 连接数据分析 Server")
    print("-" * 80)
    
    data_server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_data.py"]
    )
    
    async with stdio_client(data_server_params) as (data_read, data_write):
        async with ClientSession(data_read, data_write) as data_session:
            await data_session.initialize()
            
            print("✅ 数据分析 Server 连接成功")
            
            # 获取工具列表
            data_tools = await data_session.list_tools()
            print(f"发现 {len(data_tools.tools)} 个工具:")
            for tool in data_tools.tools:
                print(f"  - {tool.name}")
            print()
            
            # 使用数据 Server 分析文本
            print("🔍 步骤4: 分析文件内容")
            print("-" * 80)
            
            result = await data_session.call_tool(
                "analyze_text",
                {"text": text_content}
            )
            
            print(result.content[0].text)
            print()
            
            # 提取特定模式
            print("🔍 步骤5: 提取数字信息")
            print("-" * 80)
            
            result = await data_session.call_tool(
                "extract_patterns",
                {"text": text_content, "pattern_type": "number"}
            )
            
            print(result.content[0].text)
    
    # 清理
    Path("test_analysis.txt").unlink()
    print()
    print("=" * 80)
    print("✅ 演示完成!")
    print("=" * 80)
    print()
    print("🎓 关键要点:")
    print("  1. 文件 Server 专注文件操作")
    print("  2. 数据 Server 专注数据分析")
    print("  3. 两个 Server 协同完成复杂任务")
    print("  4. 每个 Server 独立运行,职责清晰")


async def demo_coordinated_workflow():
    """
    演示协调工作流
    
    场景: 日志处理
    1. 创建日志文件 (file-server)
    2. 读取日志 (file-server)
    3. 分析日志 (data-server)
    4. 生成报告 (file-server)
    """
    
    print("\n\n")
    print("=" * 80)
    print("🎯 场景2: 协调工作流 - 日志处理")
    print("=" * 80)
    print()
    
    log_content = """2024-12-24 ERROR: Connection timeout
2024-12-24 INFO: Request processed
2024-12-24 ERROR: Database error
2024-12-24 WARNING: High memory usage
2024-12-24 INFO: User login"""
    
    # 第1步: 使用文件 Server 创建日志
    print("步骤1: 创建日志文件")
    
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_file.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            await session.call_tool(
                "write_file",
                {"file_path": "app.log", "content": log_content}
            )
            print("✅ 日志文件已创建")
    
    # 第2步: 使用文件 Server 读取
    print("\n步骤2: 读取日志文件")
    
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_file.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "read_file",
                {"file_path": "app.log"}
            )
            print("✅ 日志文件已读取")
    
    # 第3步: 使用数据 Server 分析
    print("\n步骤3: 分析日志内容")
    
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_data.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "analyze_text",
                {"text": log_content}
            )
            analysis = result.content[0].text
            print(analysis[:300] + "...")  # 显示前300字符
    
    # 第4步: 使用文件 Server 生成报告
    print("\n步骤4: 生成分析报告")
    
    report = f"""# 日志分析报告

{analysis}

## 建议
- 检查连接配置
- 优化数据库性能
- 监控内存使用
"""
    
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_file.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            await session.call_tool(
                "write_file",
                {"file_path": "log_report.md", "content": report}
            )
            print("✅ 报告已生成: log_report.md")
    
    # 清理
    Path("app.log").unlink(missing_ok=True)
    Path("log_report.md").unlink(missing_ok=True)
    
    print()
    print("=" * 80)
    print("✅ 协调工作流完成!")
    print("=" * 80)


async def demo_tool_combination():
    """
    演示工具组合的威力
    
    比较单一工具 vs 多工具协作
    """
    
    print("\n\n")
    print("=" * 80)
    print("🎯 场景3: 工具组合 vs 单一工具")
    print("=" * 80)
    print()
    
    data = "10,20,30,40,50,60,70,80,90,100"
    
    # 单一工具: 只能做统计
    print("方式1: 单一工具(data-server)")
    print("-" * 80)
    
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_data.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "calculate_stats",
                {"numbers": data}
            )
            print(result.content[0].text)
    
    # 多工具组合: 完整工作流
    print("\n方式2: 多工具组合(file + data)")
    print("-" * 80)
    
    # 1. 保存数据到文件
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_file.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            await session.call_tool(
                "write_file",
                {"file_path": "data.txt", "content": data}
            )
            print("✅ 1. 数据已保存到文件")
    
    # 2. 分析数据
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_data.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "calculate_stats",
                {"numbers": data}
            )
            stats = result.content[0].text
            print("✅ 2. 数据已分析")
    
    # 3. 保存报告
    async with stdio_client(StdioServerParameters(
        command="python", args=["mcp_server_file.py"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            report = f"# 数据分析报告\n\n{stats}"
            await session.call_tool(
                "write_file",
                {"file_path": "stats_report.md", "content": report}
            )
            print("✅ 3. 报告已生成")
    
    # 清理
    Path("data.txt").unlink(missing_ok=True)
    Path("stats_report.md").unlink(missing_ok=True)
    
    print()
    print("💡 对比总结:")
    print("  单一工具: 功能有限,只能做一件事")
    print("  多工具组合: 功能强大,完成完整工作流")
    print()


async def main():
    """主函数"""
    
    print("🚀 多 MCP Server 协作演示 (简化版)")
    print("=" * 80)
    print()
    print("本演示将展示:")
    print("  1. 两个 Server 协同工作")
    print("  2. 协调的工作流")
    print("  3. 工具组合的优势")
    print()
    
    try:
        # 场景1: 基础协作
        await demo_two_servers()
        
        # 场景2: 协调工作流
        await demo_coordinated_workflow()
        
        # 场景3: 工具组合
        await demo_tool_combination()
        
        print("=" * 80)
        print("🎉 所有演示完成!")
        print("=" * 80)
        print()
        print("🎓 核心学习点:")
        print("  1. 多个 MCP Server 可以协同工作")
        print("  2. 每个 Server 专注自己的职责")
        print("  3. 工具组合带来更强大的能力")
        print("  4. 通过编排工具可以完成复杂任务")
        print()
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
