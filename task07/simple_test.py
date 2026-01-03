"""简单测试脚本"""
import os
import sys

# 设置UTF-8编码以避免Windows控制台编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 设置路径
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# 测试结果
results = []

# 测试1: 导入模块
results.append("=== 测试1: 模块导入 ===")
try:
    from src.memory import EnhancedMemorySystem, MemoryType, ImportanceLevel
    results.append("  [OK] 记忆系统模块")
except Exception as e:
    results.append(f"  [FAIL] 记忆系统: {e}")

try:
    from src.tools import AdvancedCodeAnalysisTool
    results.append("  [OK] 代码分析工具")
except Exception as e:
    results.append(f"  [FAIL] 代码分析工具: {e}")

try:
    from src.agents import MultiAgentCoordinator, AgentFactory, TaskRequest, AgentCapability
    results.append("  [OK] 多智能体协调器")
except Exception as e:
    results.append(f"  [FAIL] 多智能体协调器: {e}")

try:
    from src.agents import EnhancedUniversalAgent
    results.append("  [OK] 增强版智能体")
except Exception as e:
    results.append(f"  [FAIL] 增强版智能体: {e}")

# 测试2: 代码分析
results.append("\n=== 测试2: 代码分析 ===")
try:
    tool = AdvancedCodeAnalysisTool()
    test_code = 'def test(x): query = f"SELECT * FROM t WHERE id={x}"; return query'
    result = tool.analyze(test_code, dimensions=['security'])
    results.append(f"  Score: {result['summary']['quality_score']}")
    results.append(f"  Issues: {result['summary']['total_issues']}")
    results.append("  [OK] 代码分析")
except Exception as e:
    results.append(f"  [FAIL] 代码分析: {e}")

# 测试3: 记忆系统
results.append("\n=== 测试3: 记忆系统 ===")
try:
    os.makedirs("data", exist_ok=True)
    memory = EnhancedMemorySystem(db_path="data/test_memory.db")
    context = memory.start_session(user_id="test_user")
    results.append(f"  Session: {context.session_id[:20]}...")
    memory.add_interaction("user", "test message")
    memory.add_memory(
        content="test memory",
        memory_type=MemoryType.SEMANTIC,
        importance=ImportanceLevel.HIGH,
        context_tags=['test']
    )
    memories = memory.recall("test", limit=5)
    results.append(f"  Recalled: {len(memories)} memories")
    memory.end_session("test done")
    # 关闭数据库连接
    memory.close()
    results.append("  [OK] 记忆系统")
except Exception as e:
    results.append(f"  [FAIL] 记忆系统: {e}")

# 测试4: 多智能体协调器
results.append("\n=== 测试4: 多智能体协调器 ===")
try:
    coordinator = MultiAgentCoordinator(max_workers=2)
    agents = AgentFactory.create_all()
    for agent in agents:
        coordinator.register_agent(agent)
    available = coordinator.get_available_agents()
    results.append(f"  Agents: {len(available)}")
    for a in available:
        results.append(f"    - {a['name']}")
    
    task = TaskRequest(
        description="test code analysis",
        task_type=AgentCapability.CODE_ANALYSIS,
        context={'content': 'def test(): pass'}
    )
    response = coordinator.execute_task(task)
    results.append(f"  Task Status: {response.status.value}")
    results.append(f"  Exec Time: {response.execution_time:.2f}s")
    coordinator.shutdown()
    results.append("  [OK] 多智能体协调器")
except Exception as e:
    results.append(f"  [FAIL] 多智能体协调器: {e}")

# 测试5: 增强版智能体初始化
results.append("\n=== 测试5: 增强版智能体 ===")
try:
    agent = EnhancedUniversalAgent(
        enable_multi_agent=True,
        enable_memory=True,
        enable_code_analysis=True,
        skip_llm_init=True  # 跳过LLM初始化用于测试
    )
    stats = agent.get_session_stats()
    session_start = str(stats.get('session_start', 'N/A'))[:20]
    results.append(f"  Session Start: {session_start}...")
    results.append(f"  Interactions: {stats.get('interaction_count', 0)}")
    available = agent.get_available_agents()
    results.append(f"  Available Agents: {len(available)}")
    agent.end_session("test done")
    results.append("  [OK] 增强版智能体")
except Exception as e:
    import traceback
    results.append(f"  [FAIL] 增强版智能体: {e}")
    results.append(f"  Traceback: {traceback.format_exc()}")

results.append("\n=== 测试完成 ===")

# 保存结果
with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Test completed. Results saved to test_results.txt")
