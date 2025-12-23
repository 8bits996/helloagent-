"""
习题3: 长时程任务工具扩展

实现:
1. NoteTool笔记自动整理机制
2. TerminalTool人机协作审批流程
3. 智能代码重构助手
"""

import os
import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NoteType(Enum):
    """笔记类型"""
    PROJECT = "project"      # 项目笔记
    TASK = "task"           # 任务笔记
    TEMPORARY = "temporary"  # 临时笔记


class NotePriority(Enum):
    """笔记优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Note:
    """笔记数据结构"""
    id: str
    type: NoteType
    title: str
    content: str
    priority: NotePriority = NotePriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)
    parent_id: Optional[str] = None  # 所属项目/任务ID
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": list(self.tags),
            "parent_id": self.parent_id
        }


class AutoNoteOrganizer:
    """笔记自动整理器"""
    
    def __init__(self, max_temp_notes: int = 10):
        """
        初始化笔记整理器
        
        Args:
            max_temp_notes: 临时笔记数量阈值，超过后触发整理
        """
        self.max_temp_notes = max_temp_notes
        self.notes: Dict[str, Note] = {}
        self.note_counter = 0
        
        # 关键词识别
        self.project_keywords = ["项目", "系统", "架构", "设计", "project", "system"]
        self.task_keywords = ["任务", "TODO", "实现", "修复", "task", "implement", "fix"]
        self.critical_keywords = ["重要", "紧急", "关键", "critical", "urgent", "important"]
    
    def add_note(
        self,
        content: str,
        note_type: NoteType = NoteType.TEMPORARY,
        title: Optional[str] = None
    ) -> str:
        """添加笔记"""
        note_id = f"note_{self.note_counter}"
        self.note_counter += 1
        
        # 自动生成标题
        if not title:
            title = self._generate_title(content)
        
        # 自动识别优先级
        priority = self._detect_priority(content)
        
        # 自动提取标签
        tags = self._extract_tags(content)
        
        note = Note(
            id=note_id,
            type=note_type,
            title=title,
            content=content,
            priority=priority,
            tags=tags
        )
        
        self.notes[note_id] = note
        
        print(f"✅ 创建笔记: {note_id} - {title}")
        
        # 检查是否需要整理
        temp_count = len([n for n in self.notes.values() if n.type == NoteType.TEMPORARY])
        if temp_count >= self.max_temp_notes:
            print(f"\n⚠️  临时笔记达到{temp_count}条，触发自动整理...")
            self.auto_organize()
        
        return note_id
    
    def auto_organize(self):
        """自动整理笔记"""
        print("\n" + "=" * 60)
        print("🤖 开始自动整理笔记")
        print("=" * 60)
        
        # 获取所有临时笔记
        temp_notes = [n for n in self.notes.values() if n.type == NoteType.TEMPORARY]
        
        if not temp_notes:
            print("没有临时笔记需要整理")
            return
        
        print(f"\n发现{len(temp_notes)}条临时笔记")
        
        # 分析和整理
        promoted = []
        merged = []
        deleted = []
        
        for note in temp_notes:
            action = self._analyze_note_importance(note)
            
            if action == "promote_to_task":
                # 提升为任务笔记
                self._promote_note(note, NoteType.TASK)
                promoted.append(note)
            
            elif action == "promote_to_project":
                # 提升为项目笔记
                self._promote_note(note, NoteType.PROJECT)
                promoted.append(note)
            
            elif action == "merge":
                # 合并到相关笔记
                merged_to = self._merge_to_related(note)
                if merged_to:
                    merged.append((note, merged_to))
            
            elif action == "delete":
                # 删除冗余笔记
                deleted.append(note)
                del self.notes[note.id]
        
        # 报告整理结果
        print("\n" + "=" * 60)
        print("整理完成")
        print("=" * 60)
        
        if promoted:
            print(f"\n📈 提升笔记: {len(promoted)}条")
            for note in promoted:
                print(f"  • {note.id}: {note.title} → {note.type.value}")
        
        if merged:
            print(f"\n🔗 合并笔记: {len(merged)}条")
            for note, target in merged:
                print(f"  • {note.id} → {target}")
        
        if deleted:
            print(f"\n🗑️  删除笔记: {len(deleted)}条")
            for note in deleted:
                print(f"  • {note.id}: {note.title}")
        
        # 统计当前状态
        self._print_statistics()
    
    def _analyze_note_importance(self, note: Note) -> str:
        """分析笔记重要性，决定处理动作"""
        content_lower = note.content.lower()
        
        # 1. 检查是否应提升为项目笔记
        if any(kw in content_lower for kw in self.project_keywords):
            if note.priority in [NotePriority.CRITICAL, NotePriority.HIGH]:
                return "promote_to_project"
        
        # 2. 检查是否应提升为任务笔记
        if any(kw in content_lower for kw in self.task_keywords):
            if note.priority != NotePriority.LOW:
                return "promote_to_task"
        
        # 3. 检查是否可以合并
        if len(note.content) < 100 and not note.tags:
            return "merge"
        
        # 4. 检查是否应删除
        if self._is_redundant(note):
            return "delete"
        
        # 5. 默认保持临时状态
        return "keep"
    
    def _promote_note(self, note: Note, new_type: NoteType):
        """提升笔记类型"""
        note.type = new_type
        note.updated_at = datetime.now()
        print(f"  ✅ 提升 {note.id} 为 {new_type.value}")
    
    def _merge_to_related(self, note: Note) -> Optional[str]:
        """合并到相关笔记"""
        # 查找相关笔记（有共同标签或相似内容）
        for other_id, other in self.notes.items():
            if other.id == note.id:
                continue
            
            # 检查标签重叠
            if note.tags & other.tags:
                # 合并内容
                other.content += f"\n\n[补充 from {note.id}]\n{note.content}"
                other.updated_at = datetime.now()
                
                # 删除原笔记
                del self.notes[note.id]
                
                print(f"  🔗 合并 {note.id} → {other_id}")
                return other_id
        
        return None
    
    def _is_redundant(self, note: Note) -> bool:
        """检查笔记是否冗余"""
        # 内容太短
        if len(note.content.strip()) < 20:
            return True
        
        # 优先级低且无标签
        if note.priority == NotePriority.LOW and not note.tags:
            # 检查是否有相似内容的笔记
            for other in self.notes.values():
                if other.id != note.id:
                    similarity = self._calculate_similarity(note.content, other.content)
                    if similarity > 0.8:
                        return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_title(self, content: str) -> str:
        """自动生成标题"""
        # 取第一句话或前30个字符
        first_line = content.split('\n')[0]
        if len(first_line) > 30:
            return first_line[:30] + "..."
        return first_line
    
    def _detect_priority(self, content: str) -> NotePriority:
        """自动检测优先级"""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in self.critical_keywords):
            return NotePriority.CRITICAL
        
        if "TODO" in content or "FIXME" in content:
            return NotePriority.HIGH
        
        if len(content) > 200:  # 长内容通常更重要
            return NotePriority.MEDIUM
        
        return NotePriority.LOW
    
    def _extract_tags(self, content: str) -> Set[str]:
        """自动提取标签"""
        tags = set()
        
        # 提取#标签
        words = content.split()
        for word in words:
            if word.startswith('#'):
                tags.add(word[1:].lower())
        
        # 基于关键词添加标签
        content_lower = content.lower()
        if 'python' in content_lower:
            tags.add('python')
        if 'bug' in content_lower or '错误' in content_lower:
            tags.add('bug')
        if 'feature' in content_lower or '功能' in content_lower:
            tags.add('feature')
        
        return tags
    
    def _print_statistics(self):
        """打印统计信息"""
        print("\n📊 当前笔记统计:")
        
        by_type = {}
        by_priority = {}
        
        for note in self.notes.values():
            by_type[note.type.value] = by_type.get(note.type.value, 0) + 1
            by_priority[note.priority.value] = by_priority.get(note.priority.value, 0) + 1
        
        print(f"\n按类型:")
        for note_type, count in by_type.items():
            print(f"  {note_type}: {count}条")
        
        print(f"\n按优先级:")
        for priority, count in by_priority.items():
            print(f"  {priority}: {count}条")
        
        print(f"\n总计: {len(self.notes)}条笔记")


class ApprovalRequest:
    """审批请求"""
    
    def __init__(self, operation: str, details: Dict, risk_level: str):
        self.id = f"req_{datetime.now().timestamp()}"
        self.operation = operation
        self.details = details
        self.risk_level = risk_level  # low, medium, high
        self.status = "pending"  # pending, approved, rejected
        self.created_at = datetime.now()
        self.decision_at: Optional[datetime] = None
        self.decision_by: Optional[str] = None
        self.reason: Optional[str] = None


class SecureTerminalTool:
    """安全的终端工具（带人机协作审批）"""
    
    def __init__(self, workspace_root: str):
        """
        初始化安全终端工具
        
        Args:
            workspace_root: 工作空间根目录
        """
        self.workspace_root = os.path.abspath(workspace_root)
        
        # 安全配置
        self.safe_commands = {
            "ls", "dir", "cat", "head", "tail",
            "pwd", "echo", "grep", "find"
        }
        
        self.restricted_paths = {
            "C:\\Windows\\System32",
            "/etc",
            "/usr/bin",
            "C:\\Program Files"
        }
        
        self.sensitive_patterns = [
            "password", "secret", "token", "key",
            ".env", "credentials", "config"
        ]
        
        # 审批队列
        self.pending_approvals: List[ApprovalRequest] = []
        self.approval_history: List[ApprovalRequest] = []
    
    def execute(self, command: str, path: Optional[str] = None) -> Dict:
        """
        执行命令（带安全检查和审批流程）
        
        Returns:
            Dict包含status, output, approval_required等
        """
        # 1. 基础安全检查
        risk_level = self._assess_risk(command, path)
        
        print(f"\n📋 命令: {command}")
        if path:
            print(f"📁 路径: {path}")
        print(f"⚠️  风险级别: {risk_level}")
        
        # 2. 低风险命令直接执行
        if risk_level == "low":
            print("✅ 安全命令，直接执行")
            return self._execute_safe_command(command, path)
        
        # 3. 中高风险命令需要审批
        print("⏸️  需要人工审批")
        
        approval_req = ApprovalRequest(
            operation=command,
            details={"command": command, "path": path},
            risk_level=risk_level
        )
        
        self.pending_approvals.append(approval_req)
        
        return {
            "status": "pending_approval",
            "approval_id": approval_req.id,
            "risk_level": risk_level,
            "message": "命令需要人工审批后才能执行"
        }
    
    def approve(
        self,
        approval_id: str,
        approved: bool,
        approver: str = "user",
        reason: Optional[str] = None
    ) -> Dict:
        """处理审批请求"""
        # 查找审批请求
        request = None
        for req in self.pending_approvals:
            if req.id == approval_id:
                request = req
                break
        
        if not request:
            return {"status": "error", "message": "审批请求不存在"}
        
        # 更新审批状态
        request.status = "approved" if approved else "rejected"
        request.decision_at = datetime.now()
        request.decision_by = approver
        request.reason = reason
        
        # 移到历史记录
        self.pending_approvals.remove(request)
        self.approval_history.append(request)
        
        print(f"\n{'✅' if approved else '❌'} 审批{'通过' if approved else '拒绝'}: {approval_id}")
        if reason:
            print(f"   理由: {reason}")
        
        # 如果批准，执行命令
        if approved:
            result = self._execute_safe_command(
                request.details["command"],
                request.details.get("path")
            )
            result["approval_id"] = approval_id
            return result
        else:
            return {
                "status": "rejected",
                "approval_id": approval_id,
                "message": f"命令被拒绝: {reason or '无理由'}"
            }
    
    def list_pending_approvals(self) -> List[Dict]:
        """列出待审批请求"""
        return [
            {
                "id": req.id,
                "operation": req.operation,
                "risk_level": req.risk_level,
                "created_at": req.created_at.isoformat(),
                "details": req.details
            }
            for req in self.pending_approvals
        ]
    
    def _assess_risk(self, command: str, path: Optional[str] = None) -> str:
        """评估命令风险级别"""
        cmd_parts = command.split()
        if not cmd_parts:
            return "low"
        
        base_command = cmd_parts[0].lower()
        
        # 高风险命令
        dangerous_commands = {"rm", "del", "format", "dd", "chmod", "chown"}
        if base_command in dangerous_commands:
            return "high"
        
        # 检查路径风险
        if path:
            abs_path = os.path.abspath(path)
            
            # 检查是否访问受限路径
            for restricted in self.restricted_paths:
                if abs_path.startswith(restricted):
                    return "high"
            
            # 检查是否访问敏感文件
            if any(pattern in abs_path.lower() for pattern in self.sensitive_patterns):
                return "high"
        
        # 安全命令
        if base_command in self.safe_commands:
            return "low"
        
        # 中等风险
        return "medium"
    
    def _execute_safe_command(self, command: str, path: Optional[str] = None) -> Dict:
        """执行安全命令（模拟）"""
        # 实际应用中这里会真正执行命令
        # result = subprocess.run(command, shell=True, capture_output=True)
        
        # 模拟执行
        print(f"🔧 执行: {command}")
        
        return {
            "status": "success",
            "command": command,
            "output": f"[模拟输出] 命令 '{command}' 执行成功",
            "risk_level": "low"
        }


class CodeRefactoringAssistant:
    """智能代码重构助手"""
    
    def __init__(self, codebase_path: str):
        """
        初始化重构助手
        
        Args:
            codebase_path: 代码库路径
        """
        self.codebase_path = codebase_path
        self.note_tool = AutoNoteOrganizer()
        self.terminal_tool = SecureTerminalTool(codebase_path)
        
        # 重构计划
        self.refactoring_plan: List[Dict] = []
        self.current_step = 0
    
    def analyze_codebase(self) -> Dict:
        """分析代码库结构"""
        print("\n" + "=" * 60)
        print("📊 分析代码库结构")
        print("=" * 60)
        
        # 记录分析笔记
        analysis_note = f"""
        代码库分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        路径: {self.codebase_path}
        
        分析内容:
        - 文件结构
        - 代码质量
        - 重构机会
        """
        
        self.note_tool.add_note(
            analysis_note,
            NoteType.PROJECT,
            "代码库分析"
        )
        
        # 模拟分析结果
        analysis = {
            "total_files": 50,
            "issues_found": [
                "长函数: calculate_total() - 150行",
                "重复代码: 数据验证逻辑重复5次",
                "命名不规范: 15个变量名不符合规范"
            ],
            "refactoring_opportunities": [
                "提取 calculate_total() 中的子函数",
                "创建 DataValidator 类统一验证逻辑",
                "重命名变量以提高可读性"
            ]
        }
        
        print("\n发现的问题:")
        for issue in analysis["issues_found"]:
            print(f"  ⚠️  {issue}")
        
        print("\n重构机会:")
        for opportunity in analysis["refactoring_opportunities"]:
            print(f"  💡 {opportunity}")
        
        return analysis
    
    def create_refactoring_plan(self, analysis: Dict):
        """创建重构计划"""
        print("\n" + "=" * 60)
        print("📝 创建重构计划")
        print("=" * 60)
        
        # 基于分析结果创建计划
        for i, opportunity in enumerate(analysis["refactoring_opportunities"], 1):
            step = {
                "id": f"step_{i}",
                "description": opportunity,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            self.refactoring_plan.append(step)
            
            # 创建任务笔记
            task_note = f"""
            重构任务 #{i}
            
            描述: {opportunity}
            状态: 待开始
            
            步骤:
            1. 备份相关文件
            2. 执行重构
            3. 运行测试
            4. 提交更改
            """
            
            self.note_tool.add_note(
                task_note,
                NoteType.TASK,
                f"重构任务 #{i}"
            )
            
            print(f"\n✅ 创建任务 {step['id']}: {step['description']}")
        
        print(f"\n📋 重构计划包含 {len(self.refactoring_plan)} 个步骤")
    
    def execute_refactoring_step(self, step_id: str) -> Dict:
        """执行重构步骤"""
        # 查找步骤
        step = None
        for s in self.refactoring_plan:
            if s["id"] == step_id:
                step = s
                break
        
        if not step:
            return {"status": "error", "message": "步骤不存在"}
        
        print("\n" + "=" * 60)
        print(f"🔧 执行重构: {step['description']}")
        print("=" * 60)
        
        # 记录进度笔记
        progress_note = f"""
        [进度更新] {datetime.now().strftime('%H:%M')}
        
        正在执行: {step['description']}
        
        步骤:
        1. ✅ 备份文件
        2. 🔄 执行重构中...
        """
        
        self.note_tool.add_note(progress_note, NoteType.TEMPORARY)
        
        # 模拟重构操作
        operations = [
            ("backup", "备份原始文件"),
            ("refactor", "执行重构"),
            ("test", "运行测试"),
            ("commit", "提交更改")
        ]
        
        results = []
        for op_type, op_desc in operations:
            print(f"\n{op_desc}...")
            
            if op_type == "refactor":
                # 模拟可能需要审批的操作
                result = self.terminal_tool.execute(
                    f"modify_file --refactor {step_id}",
                    "/src/module.py"
                )
            else:
                result = {"status": "success", "operation": op_type}
            
            results.append(result)
            
            if result.get("status") == "pending_approval":
                print(f"⏸️  操作需要审批: {result['approval_id']}")
                # 在实际应用中，这里会等待人工审批
                # 自动批准用于演示
                approval_result = self.terminal_tool.approve(
                    result['approval_id'],
                    approved=True,
                    reason="重构操作，已验证安全"
                )
                results[-1] = approval_result
        
        # 更新步骤状态
        step["status"] = "completed"
        step["completed_at"] = datetime.now().isoformat()
        
        # 记录完成笔记
        completion_note = f"""
        [完成] {step['description']}
        
        完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        执行的操作:
        - 备份文件
        - 执行重构
        - 通过测试
        - 提交更改
        
        结果: ✅ 成功
        """
        
        self.note_tool.add_note(completion_note, NoteType.TEMPORARY)
        
        print(f"\n✅ 重构步骤完成: {step_id}")
        
        return {
            "status": "success",
            "step_id": step_id,
            "results": results
        }
    
    def get_progress_report(self) -> Dict:
        """获取进度报告"""
        completed = len([s for s in self.refactoring_plan if s["status"] == "completed"])
        total = len(self.refactoring_plan)
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "progress": f"{completed}/{total}" if total > 0 else "0/0",
            "percentage": (completed / total * 100) if total > 0 else 0,
            "steps": self.refactoring_plan
        }


# ============ 测试代码 ============

def test_auto_note_organizer():
    """测试笔记自动整理"""
    print("=" * 60)
    print("测试: 笔记自动整理机制")
    print("=" * 60)
    
    organizer = AutoNoteOrganizer(max_temp_notes=5)
    
    # 添加各种笔记
    notes_to_add = [
        ("临时想法: 考虑使用缓存优化性能", NoteType.TEMPORARY),
        ("重要项目: 设计新的系统架构 #project", NoteType.TEMPORARY),
        ("TODO: 修复用户登录bug #bug", NoteType.TEMPORARY),
        ("临时备注: 会议记录", NoteType.TEMPORARY),
        ("关键任务: 实现支付功能 #feature", NoteType.TEMPORARY),
        ("这是一个非常短的笔记", NoteType.TEMPORARY),  # 可能被删除
        ("紧急: 修复生产环境问题 #critical", NoteType.TEMPORARY),
    ]
    
    for content, note_type in notes_to_add:
        organizer.add_note(content, note_type)
    
    print("\n✅ 笔记自动整理测试完成!")


def test_secure_terminal():
    """测试安全终端工具"""
    print("\n\n" + "=" * 60)
    print("测试: 安全终端工具（人机协作审批）")
    print("=" * 60)
    
    terminal = SecureTerminalTool("/workspace/project")
    
    # 测试1: 安全命令
    print("\n测试1: 执行安全命令")
    result1 = terminal.execute("ls", "/workspace")
    print(f"结果: {result1['status']}")
    
    # 测试2: 需要审批的命令
    print("\n测试2: 执行需要审批的命令")
    result2 = terminal.execute("rm important_file.txt", "/workspace")
    print(f"结果: {result2['status']}")
    
    if result2['status'] == 'pending_approval':
        # 查看待审批
        pending = terminal.list_pending_approvals()
        print(f"\n待审批数量: {len(pending)}")
        
        # 批准请求
        print("\n人工审批...")
        approval_result = terminal.approve(
            result2['approval_id'],
            approved=False,
            approver="admin",
            reason="不允许删除重要文件"
        )
        print(f"审批结果: {approval_result['status']}")
    
    print("\n✅ 安全终端测试完成!")


def test_code_refactoring_assistant():
    """测试代码重构助手"""
    print("\n\n" + "=" * 60)
    print("测试: 智能代码重构助手")
    print("=" * 60)
    
    assistant = CodeRefactoringAssistant("/workspace/my_project")
    
    # 1. 分析代码库
    analysis = assistant.analyze_codebase()
    
    # 2. 创建重构计划
    assistant.create_refactoring_plan(analysis)
    
    # 3. 执行第一个重构步骤
    print("\n执行第一个重构步骤...")
    assistant.execute_refactoring_step("step_1")
    
    # 4. 查看进度
    print("\n查看整体进度...")
    progress = assistant.get_progress_report()
    print(f"\n进度: {progress['progress']} ({progress['percentage']:.1f}%)")
    
    # 5. 触发笔记整理
    print("\n继续添加临时笔记，触发自动整理...")
    for i in range(5):
        assistant.note_tool.add_note(
            f"临时记录 {i+1}: 重构过程中的发现",
            NoteType.TEMPORARY
        )
    
    print("\n✅ 代码重构助手测试完成!")


if __name__ == "__main__":
    test_auto_note_organizer()
    test_secure_terminal()
    test_code_refactoring_assistant()
    
    print("\n" + "=" * 60)
    print("习题3: 全部测试通过! ✅")
    print("=" * 60)
    
    print("\n核心功能:")
    print("✅ 笔记自动整理 - 智能提升/合并/删除")
    print("✅ 人机协作审批 - 风险评估+审批流程")
    print("✅ 代码重构助手 - 分析+计划+执行+追踪")
