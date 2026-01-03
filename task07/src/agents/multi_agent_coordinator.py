"""
多智能体协调器 - 管理多个专门化智能体的协作
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class AgentCapability(Enum):
    """智能体能力类型"""
    CODE_ANALYSIS = "code_analysis"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"
    SEARCH = "search"
    FILE_OPERATION = "file_operation"
    GENERAL = "general"


@dataclass
class TaskRequest:
    """任务请求数据结构"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    task_type: AgentCapability = AgentCapability.GENERAL
    priority: TaskPriority = TaskPriority.NORMAL
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 秒
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'task_type': self.task_type.value,
            'priority': self.priority.value,
            'context': self.context,
            'dependencies': self.dependencies,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AgentResponse:
    """智能体响应数据结构"""
    task_id: str
    agent_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    confidence: float = 1.0
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'agent_id': self.agent_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time,
            'confidence': self.confidence,
            'suggestions': self.suggestions,
            'metadata': self.metadata
        }


class BaseSpecializedAgent(ABC):
    """专门化智能体基类"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.is_busy = False
        self.task_history: List[Dict] = []
        self.success_rate = 1.0
        self._lock = threading.Lock()
    
    @abstractmethod
    def process(self, task: TaskRequest) -> AgentResponse:
        """处理任务的抽象方法"""
        pass
    
    def can_handle(self, task: TaskRequest) -> bool:
        """检查是否能处理该任务"""
        return task.task_type in self.capabilities
    
    def get_capability_score(self, task: TaskRequest) -> float:
        """获取处理该任务的能力评分"""
        if task.task_type not in self.capabilities:
            return 0.0
        
        # 基础分数
        base_score = 0.8
        
        # 根据历史成功率调整
        score = base_score * self.success_rate
        
        # 如果是主要能力，加分
        if self.capabilities and task.task_type == self.capabilities[0]:
            score += 0.2
        
        return min(score, 1.0)
    
    def update_stats(self, success: bool):
        """更新统计信息"""
        with self._lock:
            # 简单的指数移动平均
            alpha = 0.1
            self.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * self.success_rate


class TaskQueue:
    """任务队列"""
    
    def __init__(self):
        self._queue: List[TaskRequest] = []
        self._lock = threading.Lock()
    
    def add(self, task: TaskRequest):
        """添加任务"""
        with self._lock:
            self._queue.append(task)
            # 按优先级排序
            self._queue.sort(key=lambda t: t.priority.value, reverse=True)
    
    def get(self) -> Optional[TaskRequest]:
        """获取下一个任务"""
        with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None
    
    def peek(self) -> Optional[TaskRequest]:
        """查看下一个任务但不移除"""
        with self._lock:
            return self._queue[0] if self._queue else None
    
    def remove(self, task_id: str) -> bool:
        """移除指定任务"""
        with self._lock:
            for i, task in enumerate(self._queue):
                if task.id == task_id:
                    self._queue.pop(i)
                    return True
            return False
    
    def size(self) -> int:
        """获取队列大小"""
        return len(self._queue)
    
    def clear(self):
        """清空队列"""
        with self._lock:
            self._queue.clear()


class MultiAgentCoordinator:
    """多智能体协调器 - 核心调度类"""
    
    def __init__(self, max_workers: int = 4):
        self.agents: Dict[str, BaseSpecializedAgent] = {}
        self.task_queue = TaskQueue()
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: Dict[str, AgentResponse] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._running = False
        
        # 任务依赖图
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # 回调函数
        self.on_task_complete: Optional[Callable[[AgentResponse], None]] = None
        self.on_task_failed: Optional[Callable[[AgentResponse], None]] = None
    
    def register_agent(self, agent: BaseSpecializedAgent):
        """注册智能体"""
        with self._lock:
            self.agents[agent.agent_id] = agent
            logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """注销智能体"""
        with self._lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")
    
    def submit_task(self, task: TaskRequest) -> str:
        """提交任务"""
        # 记录依赖关系
        if task.dependencies:
            self.dependency_graph[task.id] = task.dependencies
        
        # 检查依赖是否满足
        if self._dependencies_satisfied(task):
            self.task_queue.add(task)
            logger.info(f"Task submitted: {task.id} - {task.description[:50]}")
        else:
            # 等待依赖完成
            with self._lock:
                self.active_tasks[task.id] = task
            logger.info(f"Task {task.id} waiting for dependencies: {task.dependencies}")
        
        return task.id
    
    def submit_tasks(self, tasks: List[TaskRequest]) -> List[str]:
        """批量提交任务"""
        return [self.submit_task(task) for task in tasks]
    
    def execute_task(self, task: TaskRequest) -> AgentResponse:
        """执行单个任务"""
        start_time = datetime.now()
        
        # 选择最佳智能体
        agent = self._select_best_agent(task)
        
        if agent is None:
            return AgentResponse(
                task_id=task.id,
                agent_id="none",
                status=TaskStatus.FAILED,
                error="No suitable agent found for this task",
                execution_time=0.0
            )
        
        # 标记智能体忙碌
        agent.is_busy = True
        
        try:
            # 执行任务
            response = agent.process(task)
            response.execution_time = (datetime.now() - start_time).total_seconds()
            
            # 更新智能体统计
            agent.update_stats(response.status == TaskStatus.COMPLETED)
            
            return response
            
        except Exception as e:
            logger.error(f"Task {task.id} failed with error: {str(e)}")
            return AgentResponse(
                task_id=task.id,
                agent_id=agent.agent_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        finally:
            agent.is_busy = False
    
    def execute_tasks_parallel(self, tasks: List[TaskRequest]) -> List[AgentResponse]:
        """并行执行多个任务"""
        responses = []
        futures = []
        
        for task in tasks:
            future = self.executor.submit(self.execute_task, task)
            futures.append((task.id, future))
        
        for task_id, future in futures:
            try:
                response = future.result(timeout=300)
                responses.append(response)
                self._handle_task_completion(response)
            except Exception as e:
                responses.append(AgentResponse(
                    task_id=task_id,
                    agent_id="unknown",
                    status=TaskStatus.FAILED,
                    error=str(e)
                ))
        
        return responses
    
    def execute_workflow(self, tasks: List[TaskRequest]) -> Dict[str, AgentResponse]:
        """执行工作流（考虑依赖关系）"""
        results = {}
        pending = {task.id: task for task in tasks}
        
        while pending:
            # 找出可以执行的任务（依赖已满足）
            ready_tasks = []
            for task_id, task in list(pending.items()):
                if self._dependencies_satisfied(task, results):
                    ready_tasks.append(task)
                    del pending[task_id]
            
            if not ready_tasks:
                # 检查是否有循环依赖
                if pending:
                    logger.error(f"Circular dependency detected or unresolved dependencies: {list(pending.keys())}")
                    for task_id in pending:
                        results[task_id] = AgentResponse(
                            task_id=task_id,
                            agent_id="none",
                            status=TaskStatus.FAILED,
                            error="Unresolved dependencies"
                        )
                break
            
            # 并行执行就绪的任务
            responses = self.execute_tasks_parallel(ready_tasks)
            for response in responses:
                results[response.task_id] = response
        
        return results
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        if task_id in self.active_tasks:
            return TaskStatus.IN_PROGRESS
        return None
    
    def get_task_result(self, task_id: str) -> Optional[AgentResponse]:
        """获取任务结果"""
        return self.completed_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 从队列中移除
        if self.task_queue.remove(task_id):
            logger.info(f"Task {task_id} cancelled from queue")
            return True
        
        # 标记为取消
        if task_id in self.active_tasks:
            self.completed_tasks[task_id] = AgentResponse(
                task_id=task_id,
                agent_id="none",
                status=TaskStatus.CANCELLED
            )
            del self.active_tasks[task_id]
            return True
        
        return False
    
    def get_available_agents(self) -> List[Dict]:
        """获取可用智能体列表"""
        return [
            {
                'id': agent.agent_id,
                'name': agent.name,
                'capabilities': [c.value for c in agent.capabilities],
                'is_busy': agent.is_busy,
                'success_rate': agent.success_rate
            }
            for agent in self.agents.values()
        ]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        completed = list(self.completed_tasks.values())
        successful = [r for r in completed if r.status == TaskStatus.COMPLETED]
        failed = [r for r in completed if r.status == TaskStatus.FAILED]
        
        return {
            'total_agents': len(self.agents),
            'queue_size': self.task_queue.size(),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(completed),
            'successful_tasks': len(successful),
            'failed_tasks': len(failed),
            'success_rate': len(successful) / len(completed) if completed else 0.0,
            'avg_execution_time': sum(r.execution_time for r in completed) / len(completed) if completed else 0.0
        }
    
    def _select_best_agent(self, task: TaskRequest) -> Optional[BaseSpecializedAgent]:
        """选择最佳智能体处理任务"""
        candidates = []
        
        for agent in self.agents.values():
            if agent.can_handle(task) and not agent.is_busy:
                score = agent.get_capability_score(task)
                candidates.append((agent, score))
        
        if not candidates:
            # 如果没有空闲的合适智能体，等待
            for agent in self.agents.values():
                if agent.can_handle(task):
                    score = agent.get_capability_score(task)
                    candidates.append((agent, score))
        
        if not candidates:
            return None
        
        # 选择得分最高的
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def _dependencies_satisfied(self, task: TaskRequest, results: Optional[Dict] = None) -> bool:
        """检查任务依赖是否满足"""
        if not task.dependencies:
            return True
        
        results = results or self.completed_tasks
        
        for dep_id in task.dependencies:
            if dep_id not in results:
                return False
            if results[dep_id].status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _handle_task_completion(self, response: AgentResponse):
        """处理任务完成"""
        with self._lock:
            self.completed_tasks[response.task_id] = response
            
            if response.task_id in self.active_tasks:
                del self.active_tasks[response.task_id]
        
        # 检查是否有等待此任务的其他任务
        self._check_waiting_tasks(response.task_id)
        
        # 触发回调
        if response.status == TaskStatus.COMPLETED:
            if self.on_task_complete:
                self.on_task_complete(response)
        else:
            if self.on_task_failed:
                self.on_task_failed(response)
    
    def _check_waiting_tasks(self, completed_task_id: str):
        """检查等待该任务的其他任务"""
        with self._lock:
            for task_id, task in list(self.active_tasks.items()):
                if completed_task_id in task.dependencies:
                    if self._dependencies_satisfied(task):
                        self.task_queue.add(task)
                        del self.active_tasks[task_id]
    
    def shutdown(self):
        """关闭协调器"""
        self._running = False
        self.executor.shutdown(wait=True)
        logger.info("Coordinator shutdown complete")


class WorkflowBuilder:
    """工作流构建器 - 帮助构建复杂的任务工作流"""
    
    def __init__(self):
        self.tasks: List[TaskRequest] = []
        self._task_map: Dict[str, TaskRequest] = {}
    
    def add_task(
        self,
        description: str,
        task_type: AgentCapability,
        priority: TaskPriority = TaskPriority.NORMAL,
        context: Optional[Dict] = None,
        task_id: Optional[str] = None
    ) -> str:
        """添加任务"""
        task = TaskRequest(
            id=task_id or str(uuid.uuid4())[:8],
            description=description,
            task_type=task_type,
            priority=priority,
            context=context or {}
        )
        self.tasks.append(task)
        self._task_map[task.id] = task
        return task.id
    
    def add_dependency(self, task_id: str, depends_on: str):
        """添加依赖关系"""
        if task_id in self._task_map:
            self._task_map[task_id].dependencies.append(depends_on)
    
    def chain(self, *task_ids: str):
        """创建任务链（顺序依赖）"""
        for i in range(1, len(task_ids)):
            self.add_dependency(task_ids[i], task_ids[i-1])
    
    def parallel(self, *task_ids: str, then: Optional[str] = None):
        """创建并行任务组，可选地指定后续任务"""
        if then and then in self._task_map:
            for task_id in task_ids:
                self.add_dependency(then, task_id)
    
    def build(self) -> List[TaskRequest]:
        """构建工作流"""
        return self.tasks.copy()
    
    def clear(self):
        """清空构建器"""
        self.tasks.clear()
        self._task_map.clear()


# 预定义的工作流模板
class WorkflowTemplates:
    """工作流模板"""
    
    @staticmethod
    def code_review_workflow(code_path: str) -> List[TaskRequest]:
        """代码审查工作流"""
        builder = WorkflowBuilder()
        
        # 1. 代码分析
        analysis_id = builder.add_task(
            description=f"分析代码结构和质量: {code_path}",
            task_type=AgentCapability.CODE_ANALYSIS,
            priority=TaskPriority.HIGH,
            context={'path': code_path}
        )
        
        # 2. 安全审计（依赖代码分析）
        security_id = builder.add_task(
            description=f"安全漏洞扫描: {code_path}",
            task_type=AgentCapability.SECURITY_AUDIT,
            priority=TaskPriority.HIGH,
            context={'path': code_path}
        )
        builder.add_dependency(security_id, analysis_id)
        
        # 3. 性能分析（依赖代码分析）
        perf_id = builder.add_task(
            description=f"性能问题检测: {code_path}",
            task_type=AgentCapability.PERFORMANCE_OPTIMIZATION,
            priority=TaskPriority.NORMAL,
            context={'path': code_path}
        )
        builder.add_dependency(perf_id, analysis_id)
        
        # 4. 生成报告（依赖安全和性能分析）
        report_id = builder.add_task(
            description="生成综合代码审查报告",
            task_type=AgentCapability.DOCUMENTATION,
            priority=TaskPriority.NORMAL,
            context={'path': code_path}
        )
        builder.add_dependency(report_id, security_id)
        builder.add_dependency(report_id, perf_id)
        
        return builder.build()
    
    @staticmethod
    def refactoring_workflow(code_path: str) -> List[TaskRequest]:
        """代码重构工作流"""
        builder = WorkflowBuilder()
        
        # 1. 分析当前代码
        analysis_id = builder.add_task(
            description=f"分析代码结构: {code_path}",
            task_type=AgentCapability.CODE_ANALYSIS,
            context={'path': code_path}
        )
        
        # 2. 识别重构点
        identify_id = builder.add_task(
            description="识别可重构的代码区域",
            task_type=AgentCapability.REFACTORING,
            context={'path': code_path}
        )
        builder.add_dependency(identify_id, analysis_id)
        
        # 3. 执行重构
        refactor_id = builder.add_task(
            description="执行代码重构",
            task_type=AgentCapability.REFACTORING,
            context={'path': code_path}
        )
        builder.add_dependency(refactor_id, identify_id)
        
        # 4. 验证重构结果
        verify_id = builder.add_task(
            description="验证重构后的代码质量",
            task_type=AgentCapability.TESTING,
            context={'path': code_path}
        )
        builder.add_dependency(verify_id, refactor_id)
        
        return builder.build()
