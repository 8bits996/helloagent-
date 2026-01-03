"""
增强版UniversalAgent 使用示例
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.agents import (
    EnhancedUniversalAgent,
    create_enhanced_agent,
    quick_analyze,
    MultiAgentCoordinator,
    AgentFactory,
    TaskRequest,
    AgentCapability,
    WorkflowTemplates
)
from src.memory import EnhancedMemorySystem, MemoryType, ImportanceLevel
from src.tools import AdvancedCodeAnalysisTool


def demo_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例1: 基础使用")
    print("=" * 60)
    
    # 创建增强版智能体
    agent = create_enhanced_agent()
    
    # 简单对话
    response = agent.run("你好，请介绍一下你的能力")
    print(f"响应: {response[:500]}...")
    
    # 获取会话统计
    stats = agent.get_session_stats()
    print(f"\n会话统计: {stats}")
    
    # 结束会话
    agent.end_session("基础使用示例完成")
    print("\n" + "-" * 60)


def demo_code_analysis():
    """代码分析示例"""
    print("=" * 60)
    print("示例2: 代码分析")
    print("=" * 60)
    
    # 示例代码
    sample_code = '''
import os
import pickle

def get_user(user_id):
    # SQL注入风险
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def load_data(filename):
    # 不安全的反序列化
    with open(filename, 'rb') as f:
        return pickle.load(f)

def process_items(items):
    result = ""
    # 低效的字符串拼接
    for item in range(len(items)):
        result += str(items[item])
    return result

password = "your_password_here"  # 硬编码密码

def complex_function(a, b, c, d, e, f, g):
    # 参数过多
    if a:
        if b:
            if c:
                if d:
                    # 嵌套过深
                    return e + f + g
    return None
'''
    
    # 使用快速分析
    print("\n快速分析结果:")
    print("-" * 40)
    result = quick_analyze(sample_code)
    print(result)
    
    # 使用高级分析工具
    print("\n\n高级分析（JSON格式）:")
    print("-" * 40)
    tool = AdvancedCodeAnalysisTool()
    detailed_result = tool.analyze(sample_code, dimensions=['security', 'performance', 'complexity'])
    
    print(f"质量评分: {detailed_result['summary']['quality_score']}/100")
    print(f"等级: {detailed_result['summary']['grade']}")
    print(f"总问题数: {detailed_result['summary']['total_issues']}")
    print(f"  - 严重: {detailed_result['summary']['by_severity']['critical']}")
    print(f"  - 错误: {detailed_result['summary']['by_severity']['error']}")
    print(f"  - 警告: {detailed_result['summary']['by_severity']['warning']}")
    
    print("\n" + "-" * 60)


def demo_multi_agent():
    """多智能体协作示例"""
    print("=" * 60)
    print("示例3: 多智能体协作")
    print("=" * 60)
    
    # 创建协调器
    coordinator = MultiAgentCoordinator(max_workers=4)
    
    # 注册所有专门化智能体
    agents = AgentFactory.create_all()
    for agent in agents:
        coordinator.register_agent(agent)
    
    # 显示可用智能体
    print("\n可用智能体:")
    for agent_info in coordinator.get_available_agents():
        print(f"  - {agent_info['name']} ({agent_info['id']})")
        print(f"    能力: {agent_info['capabilities']}")
    
    # 创建代码分析任务
    sample_code = '''
def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total += items[i].price
    return total
'''
    
    task = TaskRequest(
        description="分析代码质量",
        task_type=AgentCapability.CODE_ANALYSIS,
        context={'content': sample_code}
    )
    
    # 执行任务
    print("\n执行代码分析任务...")
    response = coordinator.execute_task(task)
    
    print(f"任务状态: {response.status.value}")
    print(f"执行时间: {response.execution_time:.2f}秒")
    print(f"置信度: {response.confidence}")
    
    if response.result:
        summary = response.result.get('summary', {})
        print(f"质量评分: {summary.get('quality_score', 'N/A')}")
    
    if response.suggestions:
        print("\n建议:")
        for suggestion in response.suggestions[:3]:
            print(f"  - {suggestion}")
    
    # 获取统计
    stats = coordinator.get_statistics()
    print(f"\n协调器统计: {stats}")
    
    # 关闭协调器
    coordinator.shutdown()
    print("\n" + "-" * 60)


def demo_memory_system():
    """记忆系统示例"""
    print("=" * 60)
    print("示例4: 增强记忆系统")
    print("=" * 60)
    
    # 创建记忆系统
    memory = EnhancedMemorySystem(db_path="data/demo_memory.db")
    
    # 开始会话
    context = memory.start_session(user_id="demo_user")
    print(f"会话ID: {context.session_id}")
    
    # 添加交互
    memory.add_interaction("user", "如何优化Python代码性能？")
    memory.add_interaction("assistant", "可以从以下几个方面优化：1. 使用列表推导式 2. 避免全局变量 3. 使用生成器...")
    
    # 添加重要记忆
    memory.add_memory(
        content="用户对Python性能优化感兴趣",
        memory_type=MemoryType.SEMANTIC,
        importance=ImportanceLevel.HIGH,
        context_tags=['python', 'performance', 'optimization']
    )
    
    # 获取上下文摘要
    summary = memory.get_context_summary()
    print(f"\n上下文摘要: {summary}")
    
    # 回忆相关记忆
    memories = memory.recall("Python性能", limit=5)
    print(f"\n相关记忆数: {len(memories)}")
    for mem in memories:
        print(f"  - [{mem.memory_type.value}] {mem.content[:50]}...")
    
    # 获取相关上下文
    relevant_context = memory.get_relevant_context("如何提高代码效率")
    print(f"\n相关上下文:\n{relevant_context}")
    
    # 结束会话
    memory.end_session("记忆系统演示完成")
    print("\n" + "-" * 60)


def demo_workflow():
    """工作流示例"""
    print("=" * 60)
    print("示例5: 代码审查工作流")
    print("=" * 60)
    
    # 创建协调器
    coordinator = MultiAgentCoordinator()
    
    # 注册智能体
    for agent in AgentFactory.create_all():
        coordinator.register_agent(agent)
    
    # 创建示例代码文件
    sample_code = '''
import os

def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

def process_file(filename):
    if ".." in filename:
        pass  # 路径遍历风险
    with open(filename) as f:
        return f.read()

password = "your_password_here"
'''
    
    # 保存到临时文件
    temp_file = "data/temp_review.py"
    os.makedirs("data", exist_ok=True)
    with open(temp_file, 'w') as f:
        f.write(sample_code)
    
    # 使用工作流模板
    print("\n创建代码审查工作流...")
    tasks = WorkflowTemplates.code_review_workflow(temp_file)
    
    print(f"工作流任务数: {len(tasks)}")
    for task in tasks:
        print(f"  - {task.description} (依赖: {task.dependencies})")
    
    # 执行工作流
    print("\n执行工作流...")
    results = coordinator.execute_workflow(tasks)
    
    print(f"\n工作流结果:")
    for task_id, response in results.items():
        print(f"  任务 {task_id}: {response.status.value}")
        if response.result and isinstance(response.result, dict):
            if 'summary' in response.result:
                print(f"    评分: {response.result['summary'].get('quality_score', 'N/A')}")
            if 'risk_level' in response.result:
                print(f"    风险: {response.result['risk_level']}")
    
    # 清理
    os.remove(temp_file)
    coordinator.shutdown()
    print("\n" + "-" * 60)


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("增强版 UniversalAgent 功能演示")
    print("=" * 60 + "\n")
    
    try:
        # 运行各个示例
        demo_code_analysis()
        demo_multi_agent()
        demo_memory_system()
        demo_workflow()
        
        # 基础使用示例需要LLM配置，可选运行
        # demo_basic_usage()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
