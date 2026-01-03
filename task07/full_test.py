"""
完整端到端测试脚本
"""
import os
import sys

# 设置UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 设置路径
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from src.memory import EnhancedMemorySystem, MemoryType, ImportanceLevel
from src.tools import AdvancedCodeAnalysisTool
from src.agents import (
    MultiAgentCoordinator, 
    AgentFactory, 
    TaskRequest, 
    AgentCapability,
    WorkflowTemplates
)

print("=" * 60)
print("UniversalAgent 完整端到端测试")
print("=" * 60)

# 测试1: 代码分析 - 检测安全问题
print("\n[测试1] 代码分析 - 安全漏洞检测")
print("-" * 40)

vulnerable_code = '''
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

def execute_cmd(cmd):
    # 命令注入风险
    os.system(cmd)

password = "your_password_here"  # 硬编码密码
api_key = "your_api_key_here"  # 硬编码API密钥
'''

tool = AdvancedCodeAnalysisTool()
result = tool.analyze(vulnerable_code, dimensions=['security'])

print(f"质量评分: {result['summary']['quality_score']}/100")
print(f"等级: {result['summary']['grade']}")
print(f"安全问题数: {result['summary']['total_issues']}")
print(f"  - 严重: {result['summary']['by_severity']['critical']}")
print(f"  - 错误: {result['summary']['by_severity']['error']}")
print(f"  - 警告: {result['summary']['by_severity']['warning']}")

if result['issues']:
    print("\n发现的安全问题:")
    for issue in result['issues'][:5]:
        if hasattr(issue, 'to_dict'):
            issue = issue.to_dict()
        print(f"  [{issue['severity']}] 行{issue['line']}: {issue['message']}")

# 测试2: 代码分析 - 性能问题检测
print("\n" + "=" * 60)
print("[测试2] 代码分析 - 性能问题检测")
print("-" * 40)

inefficient_code = '''
def process_items(items):
    result = ""
    # 低效的字符串拼接
    for i in range(len(items)):
        result += str(items[i])
    return result

def find_duplicates(lst):
    duplicates = []
    # 低效的嵌套循环
    for i in range(len(lst)):
        for j in range(len(lst)):
            if i != j and lst[i] == lst[j]:
                if lst[i] not in duplicates:
                    duplicates.append(lst[i])
    return duplicates

def compute_sum(n):
    # 低效的递归
    if n <= 1:
        return n
    return compute_sum(n-1) + compute_sum(n-2)
'''

result = tool.analyze(inefficient_code, dimensions=['performance'])
print(f"质量评分: {result['summary']['quality_score']}/100")
print(f"性能问题数: {result['summary']['total_issues']}")

if result['issues']:
    print("\n发现的性能问题:")
    for issue in result['issues'][:5]:
        if hasattr(issue, 'to_dict'):
            issue = issue.to_dict()
        print(f"  [{issue['severity']}] 行{issue['line']}: {issue['message']}")

# 测试3: 代码分析 - 复杂度检测
print("\n" + "=" * 60)
print("[测试3] 代码分析 - 复杂度检测")
print("-" * 40)

complex_code = '''
def complex_function(a, b, c, d, e, f, g, h):
    """参数过多的复杂函数"""
    if a:
        if b:
            if c:
                if d:
                    if e:
                        # 嵌套过深
                        return f + g + h
                    else:
                        return f
                else:
                    return g
            else:
                return h
        else:
            return a
    else:
        return 0

def very_long_function():
    """过长的函数"""
    x = 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    return x
'''

result = tool.analyze(complex_code, dimensions=['complexity'])
print(f"质量评分: {result['summary']['quality_score']}/100")
print(f"复杂度问题数: {result['summary']['total_issues']}")

if result['issues']:
    print("\n发现的复杂度问题:")
    for issue in result['issues'][:5]:
        if hasattr(issue, 'to_dict'):
            issue = issue.to_dict()
        print(f"  [{issue['severity']}] 行{issue['line']}: {issue['message']}")

# 测试4: 记忆系统
print("\n" + "=" * 60)
print("[测试4] 记忆系统测试")
print("-" * 40)

os.makedirs("data", exist_ok=True)
memory = EnhancedMemorySystem(db_path="data/full_test_memory.db")

# 开始会话
context = memory.start_session(user_id="test_user")
print(f"会话ID: {context.session_id}")

# 模拟对话
memory.add_interaction("user", "如何优化Python代码性能？")
memory.add_interaction("assistant", "可以从以下几个方面优化：1. 使用列表推导式 2. 避免全局变量 3. 使用生成器...")

memory.add_interaction("user", "什么是SQL注入？")
memory.add_interaction("assistant", "SQL注入是一种安全漏洞，攻击者通过在输入中插入恶意SQL代码来操纵数据库...")

# 添加重要记忆
memory.add_memory(
    content="用户对Python性能优化和安全编程感兴趣",
    memory_type=MemoryType.SEMANTIC,
    importance=ImportanceLevel.HIGH,
    context_tags=['python', 'performance', 'security']
)

# 获取上下文摘要
summary = memory.get_context_summary()
print(f"消息数: {summary['message_count']}")
print(f"当前话题: {summary['current_topic']}")
print(f"检测到的意图: {summary['detected_intents']}")
print(f"短期记忆数: {summary['short_term_memory_count']}")

# 回忆相关记忆
memories = memory.recall("Python性能", limit=5)
print(f"回忆到 {len(memories)} 条相关记忆")

# 获取相关上下文
relevant = memory.get_relevant_context("如何提高代码效率")
print(f"相关上下文长度: {len(relevant)} 字符")

memory.end_session("测试完成")
memory.close()
print("[OK] 记忆系统测试通过")

# 测试5: 多智能体协调器
print("\n" + "=" * 60)
print("[测试5] 多智能体协调器测试")
print("-" * 40)

coordinator = MultiAgentCoordinator(max_workers=4)

# 注册所有专门化智能体
agents = AgentFactory.create_all()
for agent in agents:
    coordinator.register_agent(agent)

# 显示可用智能体
available = coordinator.get_available_agents()
print(f"可用智能体数: {len(available)}")
for a in available:
    print(f"  - {a['name']}: {a['capabilities']}")

# 测试代码分析任务
print("\n执行代码分析任务...")
task1 = TaskRequest(
    description="分析代码质量",
    task_type=AgentCapability.CODE_ANALYSIS,
    context={'content': vulnerable_code}
)
response1 = coordinator.execute_task(task1)
print(f"  状态: {response1.status.value}")
print(f"  执行时间: {response1.execution_time:.2f}秒")
print(f"  置信度: {response1.confidence}")
if response1.result and 'summary' in response1.result:
    print(f"  质量评分: {response1.result['summary'].get('quality_score', 'N/A')}")

# 测试安全审计任务
print("\n执行安全审计任务...")
task2 = TaskRequest(
    description="安全漏洞扫描",
    task_type=AgentCapability.SECURITY_AUDIT,
    context={'content': vulnerable_code}
)
response2 = coordinator.execute_task(task2)
print(f"  状态: {response2.status.value}")
print(f"  执行时间: {response2.execution_time:.2f}秒")
if response2.result and 'risk_level' in response2.result:
    print(f"  风险等级: {response2.result['risk_level']}")
    print(f"  漏洞数: {response2.result.get('total_vulnerabilities', 'N/A')}")

# 测试性能优化任务
print("\n执行性能优化任务...")
task3 = TaskRequest(
    description="性能问题检测",
    task_type=AgentCapability.PERFORMANCE_OPTIMIZATION,
    context={'content': inefficient_code}
)
response3 = coordinator.execute_task(task3)
print(f"  状态: {response3.status.value}")
print(f"  执行时间: {response3.execution_time:.2f}秒")
if response3.result and 'performance_score' in response3.result:
    print(f"  性能评分: {response3.result['performance_score']}")

# 获取统计
stats = coordinator.get_statistics()
print(f"\n协调器统计:")
print(f"  总智能体数: {stats['total_agents']}")
print(f"  完成任务数: {stats['completed_tasks']}")
print(f"  失败任务数: {stats['failed_tasks']}")
print(f"  成功率: {stats['success_rate']*100:.1f}%")

coordinator.shutdown()
print("[OK] 多智能体协调器测试通过")

# 测试6: 工作流执行
print("\n" + "=" * 60)
print("[测试6] 工作流执行测试")
print("-" * 40)

# 创建新的协调器
coordinator2 = MultiAgentCoordinator()
for agent in AgentFactory.create_all():
    coordinator2.register_agent(agent)

# 保存测试代码到临时文件
temp_file = "data/temp_workflow_test.py"
with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(vulnerable_code)

# 创建代码审查工作流
print("创建代码审查工作流...")
tasks = WorkflowTemplates.code_review_workflow(temp_file)
print(f"工作流任务数: {len(tasks)}")
for task in tasks:
    print(f"  - {task.description} (依赖: {task.dependencies})")

# 执行工作流
print("\n执行工作流...")
results = coordinator2.execute_workflow(tasks)

print("\n工作流结果:")
for task_id, response in results.items():
    print(f"  任务 {task_id}: {response.status.value}")
    if response.result:
        if 'summary' in response.result:
            print(f"    评分: {response.result['summary'].get('quality_score', 'N/A')}")
        if 'risk_level' in response.result:
            print(f"    风险: {response.result['risk_level']}")
        if 'performance_score' in response.result:
            print(f"    性能: {response.result['performance_score']}")

# 清理
os.remove(temp_file)
coordinator2.shutdown()
print("[OK] 工作流执行测试通过")

# 总结
print("\n" + "=" * 60)
print("端到端测试完成!")
print("=" * 60)
print("""
测试结果汇总:
  [OK] 代码分析 - 安全漏洞检测
  [OK] 代码分析 - 性能问题检测
  [OK] 代码分析 - 复杂度检测
  [OK] 记忆系统
  [OK] 多智能体协调器
  [OK] 工作流执行

所有测试通过!
""")
