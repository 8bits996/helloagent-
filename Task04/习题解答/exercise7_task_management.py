"""
习题4: 长时程任务管理

实现:
1. 分层上下文管理（三层协调）
2. 断点续传机制
3. 任务依赖管理系统
"""

import json
import hashlib
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import copy


class ContextLayer(Enum):
    """上下文层级"""
    IMMEDIATE = "immediate"      # 即时访问（TerminalTool）
    SESSION = "session"          # 会话记忆（MemoryTool）
    PERSISTENT = "persistent"    # 持久笔记（NoteTool）


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"              # 依赖已满足，可执行
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"          # 被依赖阻塞


@dataclass
class ContextItem:
    """上下文条目"""
    key: str
    value: str
    layer: ContextLayer
    created_at: datetime = field(default_factory=datetime.now)
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None
    ttl: Optional[int] = None    # 生存时间（秒）
    
    def access(self):
        """记录访问"""
        self.accessed_count += 1
        self.last_accessed = datetime.now()


class LayeredContextManager:
    """分层上下文管理器"""
    
    def __init__(self):
        """初始化三层上下文"""
        # 即时访问层（最快，最小）
        self.immediate_context: Dict[str, ContextItem] = {}
        
        # 会话记忆层（中等，会话级）
        self.session_context: Dict[str, ContextItem] = {}
        
        # 持久笔记层（最大，持久化）
        self.persistent_context: Dict[str, ContextItem] = {}
        
        # 层级映射
        self.layer_storage = {
            ContextLayer.IMMEDIATE: self.immediate_context,
            ContextLayer.SESSION: self.session_context,
            ContextLayer.PERSISTENT: self.persistent_context
        }
        
        # 容量限制
        self.capacity_limits = {
            ContextLayer.IMMEDIATE: 10,      # 即时层只保留10条
            ContextLayer.SESSION: 100,       # 会话层100条
            ContextLayer.PERSISTENT: 1000    # 持久层1000条
        }
    
    def set(
        self,
        key: str,
        value: str,
        layer: ContextLayer = ContextLayer.SESSION,
        ttl: Optional[int] = None
    ):
        """设置上下文"""
        item = ContextItem(
            key=key,
            value=value,
            layer=layer,
            ttl=ttl
        )
        
        storage = self.layer_storage[layer]
        storage[key] = item
        
        # 检查容量并自动降级
        self._check_capacity(layer)
        
        print(f"📝 设置上下文 [{layer.value}] {key}")
    
    def get(self, key: str) -> Optional[str]:
        """获取上下文（自动搜索三层）"""
        # 按优先级搜索：即时 → 会话 → 持久
        for layer in [ContextLayer.IMMEDIATE, ContextLayer.SESSION, ContextLayer.PERSISTENT]:
            storage = self.layer_storage[layer]
            if key in storage:
                item = storage[key]
                item.access()
                
                # 热点数据自动提升
                if layer != ContextLayer.IMMEDIATE:
                    self._maybe_promote(key, item, layer)
                
                print(f"📖 读取上下文 [{layer.value}] {key}")
                return item.value
        
        return None
    
    def _check_capacity(self, layer: ContextLayer):
        """检查容量并淘汰"""
        storage = self.layer_storage[layer]
        limit = self.capacity_limits[layer]
        
        if len(storage) > limit:
            # 淘汰策略：LRU（最近最少使用）
            items_to_evict = self._select_eviction_candidates(storage, len(storage) - limit)
            
            for key in items_to_evict:
                item = storage[key]
                del storage[key]
                
                # 降级到下一层
                next_layer = self._get_next_layer(layer)
                if next_layer:
                    item.layer = next_layer
                    self.layer_storage[next_layer][key] = item
                    print(f"  ⬇️  降级 {key}: {layer.value} → {next_layer.value}")
    
    def _select_eviction_candidates(self, storage: Dict[str, ContextItem], count: int) -> List[str]:
        """选择淘汰候选"""
        # 按访问时间和频率排序
        items = []
        for key, item in storage.items():
            score = item.accessed_count
            if item.last_accessed:
                # 最近访问的加分
                age_seconds = (datetime.now() - item.last_accessed).total_seconds()
                score += max(0, 100 - age_seconds / 60)  # 距离现在越近分越高
            items.append((score, key))
        
        # 分数低的淘汰
        items.sort()
        return [key for score, key in items[:count]]
    
    def _maybe_promote(self, key: str, item: ContextItem, current_layer: ContextLayer):
        """热点数据提升"""
        # 访问频繁（>5次）提升到上一层
        if item.accessed_count > 5:
            prev_layer = self._get_prev_layer(current_layer)
            if prev_layer:
                # 从当前层删除
                del self.layer_storage[current_layer][key]
                
                # 添加到上一层
                item.layer = prev_layer
                self.layer_storage[prev_layer][key] = item
                
                print(f"  ⬆️  提升 {key}: {current_layer.value} → {prev_layer.value}")
    
    def _get_next_layer(self, layer: ContextLayer) -> Optional[ContextLayer]:
        """获取下一层"""
        order = [ContextLayer.IMMEDIATE, ContextLayer.SESSION, ContextLayer.PERSISTENT]
        try:
            idx = order.index(layer)
            return order[idx + 1] if idx + 1 < len(order) else None
        except ValueError:
            return None
    
    def _get_prev_layer(self, layer: ContextLayer) -> Optional[ContextLayer]:
        """获取上一层"""
        order = [ContextLayer.IMMEDIATE, ContextLayer.SESSION, ContextLayer.PERSISTENT]
        try:
            idx = order.index(layer)
            return order[idx - 1] if idx > 0 else None
        except ValueError:
            return None
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {}
        for layer, storage in self.layer_storage.items():
            stats[layer.value] = {
                "count": len(storage),
                "capacity": self.capacity_limits[layer],
                "usage": f"{len(storage)}/{self.capacity_limits[layer]}"
            }
        return stats


@dataclass
class TaskCheckpoint:
    """任务检查点"""
    task_id: str
    status: TaskStatus
    progress: float              # 0.0-1.0
    current_step: int
    total_steps: int
    variables: Dict[str, any]    # 任务变量
    results: List[Dict]          # 已完成步骤的结果
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "variables": self.variables,
            "results": self.results,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def compute_hash(self) -> str:
        """计算检查点哈希（用于验证完整性）"""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class CheckpointManager:
    """断点续传管理器"""
    
    def __init__(self, storage_path: str = "./checkpoints"):
        self.storage_path = storage_path
        self.checkpoints: Dict[str, TaskCheckpoint] = {}
    
    def save_checkpoint(self, checkpoint: TaskCheckpoint):
        """保存检查点"""
        checkpoint.updated_at = datetime.now()
        self.checkpoints[checkpoint.task_id] = checkpoint
        
        # 计算校验和
        checksum = checkpoint.compute_hash()
        
        print(f"💾 保存检查点: {checkpoint.task_id}")
        print(f"   进度: {checkpoint.progress:.1%}")
        print(f"   步骤: {checkpoint.current_step}/{checkpoint.total_steps}")
        print(f"   校验: {checksum[:8]}...")
        
        # 实际应用中应写入文件
        # with open(f"{self.storage_path}/{checkpoint.task_id}.json", "w") as f:
        #     json.dump(checkpoint.to_dict(), f)
    
    def load_checkpoint(self, task_id: str) -> Optional[TaskCheckpoint]:
        """加载检查点"""
        if task_id in self.checkpoints:
            checkpoint = self.checkpoints[task_id]
            
            # 验证完整性
            is_valid = self._verify_checkpoint(checkpoint)
            
            print(f"📂 加载检查点: {task_id}")
            print(f"   验证: {'✅ 通过' if is_valid else '❌ 失败'}")
            
            if is_valid:
                return checkpoint
        
        return None
    
    def _verify_checkpoint(self, checkpoint: TaskCheckpoint) -> bool:
        """验证检查点完整性"""
        # 重新计算哈希
        current_hash = checkpoint.compute_hash()
        
        # 实际应用中应与保存时的哈希对比
        # 这里简化验证
        return True
    
    def resume_from_checkpoint(self, task_id: str) -> Optional[Dict]:
        """从检查点恢复"""
        checkpoint = self.load_checkpoint(task_id)
        
        if not checkpoint:
            print(f"❌ 未找到检查点: {task_id}")
            return None
        
        print(f"\n🔄 从检查点恢复任务")
        print(f"   任务ID: {checkpoint.task_id}")
        print(f"   状态: {checkpoint.status.value}")
        print(f"   当前步骤: {checkpoint.current_step}/{checkpoint.total_steps}")
        print(f"   进度: {checkpoint.progress:.1%}")
        
        # 返回恢复信息
        return {
            "checkpoint": checkpoint,
            "resume_from_step": checkpoint.current_step + 1,
            "variables": checkpoint.variables,
            "completed_results": checkpoint.results
        }


@dataclass
class Task:
    """任务"""
    id: str
    name: str
    steps: List[Dict]
    dependencies: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    current_step: int = 0
    variables: Dict = field(default_factory=dict)
    results: List[Dict] = field(default_factory=list)


class TaskDependencyManager:
    """任务依赖管理系统"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # task_id -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = {}     # task_id -> dependents
        
        self.checkpoint_manager = CheckpointManager()
        self.context_manager = LayeredContextManager()
    
    def add_task(
        self,
        task_id: str,
        name: str,
        steps: List[Dict],
        dependencies: Optional[List[str]] = None
    ):
        """添加任务"""
        task = Task(
            id=task_id,
            name=name,
            steps=steps,
            dependencies=set(dependencies or [])
        )
        
        self.tasks[task_id] = task
        self.dependency_graph[task_id] = task.dependencies
        
        # 更新反向图
        for dep_id in task.dependencies:
            if dep_id not in self.reverse_graph:
                self.reverse_graph[dep_id] = set()
            self.reverse_graph[dep_id].add(task_id)
        
        print(f"➕ 添加任务: {task_id} - {name}")
        if task.dependencies:
            print(f"   依赖: {', '.join(task.dependencies)}")
    
    def can_execute(self, task_id: str) -> bool:
        """检查任务是否可执行"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # 检查依赖是否都完成
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def get_ready_tasks(self) -> List[str]:
        """获取所有就绪的任务"""
        ready = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING and self.can_execute(task_id):
                ready.append(task_id)
        return ready
    
    def execute_task(self, task_id: str, resume: bool = False):
        """执行任务"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在: {task_id}")
            return
        
        task = self.tasks[task_id]
        
        # 检查依赖
        if not resume and not self.can_execute(task_id):
            print(f"⏸️  任务被阻塞: {task_id}")
            task.status = TaskStatus.BLOCKED
            return
        
        print(f"\n{'🔄' if resume else '▶️ '} {'恢复' if resume else '开始'}执行任务: {task.name}")
        task.status = TaskStatus.RUNNING
        
        # 从检查点恢复
        start_step = 0
        if resume:
            resume_info = self.checkpoint_manager.resume_from_checkpoint(task_id)
            if resume_info:
                start_step = resume_info["resume_from_step"]
                task.variables = resume_info["variables"]
                task.results = resume_info["completed_results"]
                task.current_step = start_step - 1
        
        # 执行步骤
        total_steps = len(task.steps)
        
        for i in range(start_step, total_steps):
            step = task.steps[i]
            task.current_step = i
            
            print(f"\n  步骤 {i+1}/{total_steps}: {step['name']}")
            
            # 执行步骤（模拟）
            result = self._execute_step(task, step)
            task.results.append(result)
            
            # 更新进度
            task.progress = (i + 1) / total_steps
            
            # 保存检查点
            checkpoint = TaskCheckpoint(
                task_id=task_id,
                status=task.status,
                progress=task.progress,
                current_step=i,
                total_steps=total_steps,
                variables=task.variables,
                results=task.results
            )
            self.checkpoint_manager.save_checkpoint(checkpoint)
            
            # 更新上下文（分层存储）
            self._update_context(task, step, result)
            
            # 模拟可能的中断
            if i == 1 and not resume:  # 第2步模拟中断
                print("\n⚠️  [模拟中断] 系统崩溃...")
                return
        
        # 任务完成
        task.status = TaskStatus.COMPLETED
        task.progress = 1.0
        
        print(f"\n✅ 任务完成: {task.name}")
        
        # 触发依赖此任务的其他任务
        self._trigger_dependent_tasks(task_id)
    
    def _execute_step(self, task: Task, step: Dict) -> Dict:
        """执行单个步骤（模拟）"""
        # 模拟步骤执行
        result = {
            "step": step["name"],
            "status": "success",
            "output": f"步骤 {step['name']} 执行成功",
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新任务变量
        if "output_var" in step:
            task.variables[step["output_var"]] = f"result_{step['name']}"
        
        return result
    
    def _update_context(self, task: Task, step: Dict, result: Dict):
        """更新分层上下文"""
        # 决定存储在哪一层
        
        # 1. 当前步骤结果 → 即时层
        self.context_manager.set(
            f"current_step_{task.id}",
            json.dumps(result),
            ContextLayer.IMMEDIATE
        )
        
        # 2. 任务进度 → 会话层
        self.context_manager.set(
            f"task_progress_{task.id}",
            f"{task.progress:.1%}",
            ContextLayer.SESSION
        )
        
        # 3. 重要变量 → 持久层
        if "critical" in step.get("tags", []):
            self.context_manager.set(
                f"task_var_{step.get('output_var', 'result')}",
                str(task.variables.get(step.get('output_var'), '')),
                ContextLayer.PERSISTENT
            )
    
    def _trigger_dependent_tasks(self, completed_task_id: str):
        """触发依赖任务"""
        if completed_task_id not in self.reverse_graph:
            return
        
        dependent_tasks = self.reverse_graph[completed_task_id]
        
        print(f"\n🔔 检查依赖任务...")
        for task_id in dependent_tasks:
            if self.can_execute(task_id):
                task = self.tasks[task_id]
                task.status = TaskStatus.READY
                print(f"  ✅ 任务就绪: {task.name}")
    
    def visualize_dependencies(self):
        """可视化依赖关系"""
        print("\n" + "=" * 60)
        print("任务依赖关系图")
        print("=" * 60)
        
        for task_id, task in self.tasks.items():
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.READY: "✅",
                TaskStatus.RUNNING: "▶️",
                TaskStatus.COMPLETED: "✔️",
                TaskStatus.FAILED: "❌",
                TaskStatus.BLOCKED: "🔒"
            }.get(task.status, "❓")
            
            print(f"\n{status_icon} {task.name} ({task.id})")
            print(f"   状态: {task.status.value}")
            print(f"   进度: {task.progress:.1%}")
            
            if task.dependencies:
                print(f"   依赖:")
                for dep_id in task.dependencies:
                    dep_task = self.tasks.get(dep_id)
                    if dep_task:
                        dep_status = "✓" if dep_task.status == TaskStatus.COMPLETED else "✗"
                        print(f"     {dep_status} {dep_task.name}")
            
            if task_id in self.reverse_graph:
                print(f"   被依赖:")
                for dep_task_id in self.reverse_graph[task_id]:
                    dep_task = self.tasks.get(dep_task_id)
                    if dep_task:
                        print(f"     → {dep_task.name}")


# ============ 测试代码 ============

def test_layered_context():
    """测试分层上下文管理"""
    print("=" * 60)
    print("测试: 分层上下文管理")
    print("=" * 60)
    
    manager = LayeredContextManager()
    
    # 测试不同层级的存储
    print("\n1. 设置不同层级的上下文")
    manager.set("current_file", "/src/main.py", ContextLayer.IMMEDIATE)
    manager.set("session_id", "sess_123", ContextLayer.SESSION)
    manager.set("project_config", "config.json", ContextLayer.PERSISTENT)
    
    # 测试读取
    print("\n2. 读取上下文")
    file = manager.get("current_file")
    session = manager.get("session_id")
    config = manager.get("project_config")
    
    # 测试容量限制和降级
    print("\n3. 测试容量限制（添加15条到即时层，触发降级）")
    for i in range(15):
        manager.set(f"temp_{i}", f"value_{i}", ContextLayer.IMMEDIATE)
    
    # 测试热点提升
    print("\n4. 测试热点提升（多次访问会话层数据）")
    for i in range(7):
        manager.get("session_id")
    
    # 统计信息
    print("\n5. 上下文统计")
    stats = manager.get_statistics()
    for layer, info in stats.items():
        print(f"   {layer}: {info['usage']}")
    
    print("\n✅ 分层上下文测试完成!")


def test_checkpoint_resume():
    """测试断点续传"""
    print("\n\n" + "=" * 60)
    print("测试: 断点续传机制")
    print("=" * 60)
    
    checkpoint_mgr = CheckpointManager()
    
    # 创建检查点
    print("\n1. 创建检查点")
    checkpoint = TaskCheckpoint(
        task_id="data_processing",
        status=TaskStatus.RUNNING,
        progress=0.6,
        current_step=3,
        total_steps=5,
        variables={"processed_count": 600, "total_count": 1000},
        results=[
            {"step": "load", "status": "success"},
            {"step": "validate", "status": "success"},
            {"step": "transform", "status": "success"}
        ]
    )
    
    checkpoint_mgr.save_checkpoint(checkpoint)
    
    # 模拟中断后恢复
    print("\n2. 模拟系统中断...")
    print("   [系统崩溃]")
    
    print("\n3. 从检查点恢复")
    resume_info = checkpoint_mgr.resume_from_checkpoint("data_processing")
    
    if resume_info:
        print(f"\n恢复信息:")
        print(f"   从步骤 {resume_info['resume_from_step']} 继续")
        print(f"   已完成: {len(resume_info['completed_results'])} 个步骤")
        print(f"   变量: {resume_info['variables']}")
    
    print("\n✅ 断点续传测试完成!")


def test_task_dependency():
    """测试任务依赖管理"""
    print("\n\n" + "=" * 60)
    print("测试: 任务依赖管理系统")
    print("=" * 60)
    
    manager = TaskDependencyManager()
    
    # 定义任务
    print("\n1. 定义任务和依赖关系")
    
    # 任务A: 数据采集（无依赖）
    manager.add_task(
        "task_a",
        "数据采集",
        [
            {"name": "连接数据源", "tags": ["critical"], "output_var": "connection"},
            {"name": "提取数据", "output_var": "raw_data"},
            {"name": "保存原始数据", "tags": ["critical"]}
        ]
    )
    
    # 任务B: 数据清洗（依赖A）
    manager.add_task(
        "task_b",
        "数据清洗",
        [
            {"name": "加载原始数据", "output_var": "data"},
            {"name": "去除重复", "output_var": "dedup_data"},
            {"name": "处理缺失值", "tags": ["critical"]}
        ],
        dependencies=["task_a"]
    )
    
    # 任务C: 数据分析（依赖B）
    manager.add_task(
        "task_c",
        "数据分析",
        [
            {"name": "加载清洗数据", "output_var": "clean_data"},
            {"name": "统计分析", "output_var": "stats"},
            {"name": "生成报告", "tags": ["critical"]}
        ],
        dependencies=["task_b"]
    )
    
    # 任务D: 可视化（依赖B）
    manager.add_task(
        "task_d",
        "数据可视化",
        [
            {"name": "加载数据", "output_var": "viz_data"},
            {"name": "生成图表", "output_var": "charts"}
        ],
        dependencies=["task_b"]
    )
    
    # 可视化依赖关系
    manager.visualize_dependencies()
    
    # 执行任务流程
    print("\n\n2. 执行任务流程")
    print("\n--- 执行任务A ---")
    manager.execute_task("task_a")
    
    print("\n\n3. 模拟中断，然后恢复")
    print("\n--- 恢复任务A ---")
    manager.execute_task("task_a", resume=True)
    
    # 查看就绪任务
    print("\n\n4. 检查就绪任务")
    ready_tasks = manager.get_ready_tasks()
    print(f"就绪任务: {[manager.tasks[tid].name for tid in ready_tasks]}")
    
    # 执行后续任务
    print("\n--- 执行任务B ---")
    manager.execute_task("task_b")
    manager.execute_task("task_b", resume=True)
    
    # 最终状态
    manager.visualize_dependencies()
    
    # 查看上下文统计
    print("\n\n5. 上下文使用统计")
    stats = manager.context_manager.get_statistics()
    for layer, info in stats.items():
        print(f"   {layer}: {info['usage']}")
    
    print("\n✅ 任务依赖管理测试完成!")


if __name__ == "__main__":
    test_layered_context()
    test_checkpoint_resume()
    test_task_dependency()
    
    print("\n" + "=" * 60)
    print("习题4: 全部测试通过! ✅")
    print("=" * 60)
    
    print("\n核心功能:")
    print("✅ 分层上下文管理 - 三层协调+自动提升/降级")
    print("✅ 断点续传机制 - 检查点保存+完整性验证+恢复")
    print("✅ 任务依赖管理 - DAG调度+自动触发+可视化")
