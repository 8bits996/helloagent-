"""
MCP 工具直接调用演示
展示如何直接使用 MCP 工具,不依赖 LLM

学习要点:
1. MCP Client 的基本用法
2. 工具调用的完整流程
3. 多工具协作示例
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_all_tools():
    """演示所有 MCP 工具"""
    print("\n" + "=" * 70)
    print("🚀 MCP 工具完整演示")
    print("=" * 70)
    print()
    
    # 配置 Server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_basic.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("✓ 已连接到 MCP Server\n")
            
            # 1. 列出所有工具
            print("📋 第1步: 发现可用工具")
            print("-" * 70)
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"发现 {len(tools)} 个工具:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool.name} - {tool.description.split(chr(10))[0]}")
            print()
            
            # 2. 数学计算场景
            print("🧮 第2步: 数学计算场景")
            print("-" * 70)
            print("任务: 计算 (10 + 5) * 2 的结果\n")
            
            # 步骤1: 计算 10 + 5
            print("  步骤1: 使用 add 工具计算 10 + 5")
            result1 = await session.call_tool("add", {"a": 10, "b": 5})
            step1_result = None
            for content in result1.content:
                if hasattr(content, 'text'):
                    step1_result = int(content.text)
                    print(f"    ✅ 结果: {step1_result}")
            
            # 步骤2: 计算结果 * 2
            if step1_result:
                print(f"\n  步骤2: 使用 multiply 工具计算 {step1_result} * 2")
                result2 = await session.call_tool(
                    "multiply",
                    {"a": float(step1_result), "b": 2.0}
                )
                for content in result2.content:
                    if hasattr(content, 'text'):
                        print(f"    ✅ 最终结果: {content.text}")
            print()
            
            # 3. 复杂表达式计算
            print("🔢 第3步: 使用 calculator 工具计算复杂表达式")
            print("-" * 70)
            expressions = [
                "2 ** 8",           # 2的8次方
                "(100 - 25) / 5",   # 除法运算
                "3.14 * 10 ** 2",   # 圆的面积 (半径=10)
            ]
            
            for expr in expressions:
                result = await session.call_tool("calculator", {"expression": expr})
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  {expr:20} => {content.text}")
            print()
            
            # 4. 文本处理场景
            print("💬 第4步: 文本处理场景")
            print("-" * 70)
            messages = [
                "Hello from MCP!",
                "这是一个测试消息",
                "MCP makes AI tools easy! 🚀",
            ]
            
            for msg in messages:
                result = await session.call_tool("echo", {"message": msg})
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(f"  📢 {content.text}")
            print()
            
            # 5. 获取提示词
            print("📝 第5步: 使用提示词模板")
            print("-" * 70)
            try:
                prompts = await session.list_prompts()
                if prompts.prompts:
                    prompt = await session.get_prompt(
                        "math_helper",
                        arguments={"problem": "计算圆的面积,已知半径 r = 5"}
                    )
                    print("生成的提示词:")
                    print(prompt.messages[0].content.text)
            except Exception as e:
                print(f"提示词功能暂不可用: {e}")
            print()
            
            # 6. 性能测试
            print("⚡ 第6步: 性能测试")
            print("-" * 70)
            import time
            
            start_time = time.time()
            tasks_count = 10
            
            for i in range(tasks_count):
                await session.call_tool("add", {"a": i, "b": i})
            
            elapsed = time.time() - start_time
            print(f"  完成 {tasks_count} 次工具调用")
            print(f"  总耗时: {elapsed:.3f} 秒")
            print(f"  平均延迟: {elapsed/tasks_count*1000:.1f} ms")
            print()
            
            # 总结
            print("=" * 70)
            print("✅ 演示完成!")
            print("=" * 70)
            print("\n🎓 学习要点:")
            print("  1. MCP 提供统一的工具接口")
            print("  2. 工具可以组合使用完成复杂任务")
            print("  3. FastMCP 自动生成工具描述")
            print("  4. 工具调用延迟低,性能好")
            print("  5. 提示词模板可以复用")


async def demo_real_world_scenario():
    """演示真实世界场景"""
    print("\n\n" + "🌍" * 35)
    print("\n📦 真实场景演示: 数据处理流程")
    print("\n" + "🌍" * 35)
    print()
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_basic.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("场景: 处理一批数据并计算统计信息\n")
            
            # 模拟数据
            data = [23, 45, 67, 89, 12, 34, 56, 78]
            print(f"原始数据: {data}\n")
            
            # 1. 计算总和
            print("1️⃣ 计算总和...")
            total = 0
            for i in range(len(data) - 1):
                result = await session.call_tool("add", {"a": total, "b": data[i]})
                for content in result.content:
                    if hasattr(content, 'text'):
                        total = int(content.text)
            # 加上最后一个数
            result = await session.call_tool("add", {"a": total, "b": data[-1]})
            for content in result.content:
                if hasattr(content, 'text'):
                    total = int(content.text)
            print(f"   总和: {total}")
            
            # 2. 计算平均值
            print("\n2️⃣ 计算平均值...")
            avg_result = await session.call_tool(
                "multiply",
                {"a": float(total), "b": 1.0/len(data)}
            )
            for content in avg_result.content:
                if hasattr(content, 'text'):
                    print(f"   平均值: {content.text}")
            
            # 3. 生成报告
            print("\n3️⃣ 生成报告...")
            report = f"""
数据分析报告
=============
样本数量: {len(data)}
数据总和: {total}
数据范围: [{min(data)}, {max(data)}]
"""
            result = await session.call_tool("echo", {"message": report})
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            
            print("\n✅ 数据处理完成!")


async def main():
    """主函数"""
    # 演示1: 所有工具功能
    await demo_all_tools()
    
    # 演示2: 真实场景
    await demo_real_world_scenario()
    
    print("\n\n" + "🎉" * 35)
    print("\n  恭喜! 你已经掌握了 MCP 工具的基本使用")
    print("\n" + "🎉" * 35)
    print()


if __name__ == "__main__":
    asyncio.run(main())
