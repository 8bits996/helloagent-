"""
任务历史管理服务
Contract Review AI - Task History Manager

功能：
1. 任务历史记录存储
2. 历史任务查询
3. 任务统计分析
4. 任务归档和清理
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TaskHistoryManager:
    """
    任务历史管理器
    
    使用SQLite存储任务历史记录
    """
    
    def __init__(self, db_path: Path):
        """
        初始化任务历史管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    message TEXT,
                    contract_name TEXT,
                    file_count INTEGER DEFAULT 0,
                    total_size INTEGER DEFAULT 0,
                    risk_level TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    review_mode TEXT,
                    duration_seconds INTEGER
                )
            ''')
            
            # 任务文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                )
            ''')
            
            # 评审结果摘要表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_summaries (
                    task_id TEXT PRIMARY KEY,
                    overall_assessment TEXT,
                    risk_level TEXT,
                    high_risk_count INTEGER DEFAULT 0,
                    medium_risk_count INTEGER DEFAULT 0,
                    low_risk_count INTEGER DEFAULT 0,
                    compliance_pass INTEGER DEFAULT 0,
                    compliance_fail INTEGER DEFAULT 0,
                    compliance_warn INTEGER DEFAULT 0,
                    recommendation_count INTEGER DEFAULT 0,
                    missing_clause_count INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_risk ON tasks(risk_level)')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_task(
        self,
        task_id: str,
        contract_name: str = None,
        files: List[Dict] = None,
        review_mode: str = "cli"
    ) -> Dict[str, Any]:
        """
        创建新任务记录
        
        Args:
            task_id: 任务ID
            contract_name: 合同名称
            files: 文件列表
            review_mode: 评审模式
            
        Returns:
            创建结果
        """
        now = datetime.now().isoformat()
        files = files or []
        
        total_size = sum(f.get("size", 0) for f in files)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 插入任务记录
                cursor.execute('''
                    INSERT INTO tasks (
                        task_id, status, progress, message, contract_name,
                        file_count, total_size, created_at, updated_at, review_mode
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_id, "created", 0, "任务已创建",
                    contract_name or (files[0]["name"] if files else "未命名"),
                    len(files), total_size, now, now, review_mode
                ))
                
                # 插入文件记录
                for file_info in files:
                    cursor.execute('''
                        INSERT INTO task_files (task_id, filename, file_size, file_type)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        task_id,
                        file_info.get("name", ""),
                        file_info.get("size", 0),
                        file_info.get("type", "")
                    ))
                
                conn.commit()
                
                logger.info(f"任务记录已创建: {task_id}")
                
                return {"success": True, "task_id": task_id}
            
            except sqlite3.IntegrityError:
                return {"success": False, "error": "任务ID已存在"}
            except Exception as e:
                logger.error(f"创建任务记录失败: {e}")
                return {"success": False, "error": str(e)}
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = None,
        message: str = None,
        risk_level: str = None
    ) -> Dict[str, Any]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
            message: 消息
            risk_level: 风险等级
            
        Returns:
            更新结果
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建更新SQL
            updates = ["status = ?", "updated_at = ?"]
            params = [status, now]
            
            if progress is not None:
                updates.append("progress = ?")
                params.append(progress)
            
            if message is not None:
                updates.append("message = ?")
                params.append(message)
            
            if risk_level is not None:
                updates.append("risk_level = ?")
                params.append(risk_level)
            
            # 如果完成，记录完成时间和耗时
            if status == "completed":
                updates.append("completed_at = ?")
                params.append(now)
                
                # 计算耗时
                cursor.execute('SELECT created_at FROM tasks WHERE task_id = ?', (task_id,))
                row = cursor.fetchone()
                if row:
                    created = datetime.fromisoformat(row["created_at"])
                    duration = int((datetime.now() - created).total_seconds())
                    updates.append("duration_seconds = ?")
                    params.append(duration)
            
            params.append(task_id)
            
            sql = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
            cursor.execute(sql, params)
            conn.commit()
            
            return {"success": True, "task_id": task_id}
    
    def save_review_summary(
        self,
        task_id: str,
        review_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        保存评审结果摘要
        
        Args:
            task_id: 任务ID
            review_result: 评审结果
            
        Returns:
            保存结果
        """
        # 提取统计数据
        findings = review_result.get("key_findings", [])
        compliance = review_result.get("compliance_check", [])
        
        high_risk = sum(1 for f in findings if f.get("severity") == "高")
        medium_risk = sum(1 for f in findings if f.get("severity") == "中")
        low_risk = sum(1 for f in findings if f.get("severity") == "低")
        
        pass_count = sum(1 for c in compliance if c.get("status") == "通过")
        fail_count = sum(1 for c in compliance if c.get("status") == "不通过")
        warn_count = sum(1 for c in compliance if c.get("status") == "需关注")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO review_summaries (
                    task_id, overall_assessment, risk_level,
                    high_risk_count, medium_risk_count, low_risk_count,
                    compliance_pass, compliance_fail, compliance_warn,
                    recommendation_count, missing_clause_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                review_result.get("overall_assessment", ""),
                review_result.get("risk_level", ""),
                high_risk, medium_risk, low_risk,
                pass_count, fail_count, warn_count,
                len(review_result.get("recommendations", [])),
                len(review_result.get("missing_clauses", []))
            ))
            
            conn.commit()
            
            return {"success": True, "task_id": task_id}
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务详情字典
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取任务基本信息
            cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
            task_row = cursor.fetchone()
            
            if not task_row:
                return None
            
            task = dict(task_row)
            
            # 获取文件列表
            cursor.execute('SELECT * FROM task_files WHERE task_id = ?', (task_id,))
            task["files"] = [dict(row) for row in cursor.fetchall()]
            
            # 获取评审摘要
            cursor.execute('SELECT * FROM review_summaries WHERE task_id = ?', (task_id,))
            summary_row = cursor.fetchone()
            if summary_row:
                task["review_summary"] = dict(summary_row)
            
            return task
    
    def list_tasks(
        self,
        status: str = None,
        risk_level: str = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at",
        order_dir: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """
        列出任务历史
        
        Args:
            status: 过滤状态
            risk_level: 过滤风险等级
            limit: 每页数量
            offset: 偏移量
            order_by: 排序字段
            order_dir: 排序方向
            
        Returns:
            任务列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if status:
                conditions.append("t.status = ?")
                params.append(status)
            
            if risk_level:
                conditions.append("t.risk_level = ?")
                params.append(risk_level)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            # 允许的排序字段
            allowed_order = ["created_at", "updated_at", "completed_at", "risk_level", "status"]
            if order_by not in allowed_order:
                order_by = "created_at"
            
            order_dir = "DESC" if order_dir.upper() == "DESC" else "ASC"
            
            # 查询任务列表
            sql = f'''
                SELECT t.*, rs.high_risk_count, rs.medium_risk_count, rs.low_risk_count,
                       rs.compliance_pass, rs.compliance_fail
                FROM tasks t
                LEFT JOIN review_summaries rs ON t.task_id = rs.task_id
                {where_clause}
                ORDER BY t.{order_by} {order_dir}
                LIMIT ? OFFSET ?
            '''
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            tasks = [dict(row) for row in cursor.fetchall()]
            
            # 获取每个任务的文件列表
            for task in tasks:
                cursor.execute('SELECT * FROM task_files WHERE task_id = ?', (task['task_id'],))
                task['files'] = [dict(row) for row in cursor.fetchall()]
            
            return tasks
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 总任务数
            cursor.execute('SELECT COUNT(*) FROM tasks')
            total_tasks = cursor.fetchone()[0]
            
            # 按状态统计
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM tasks
                GROUP BY status
            ''')
            status_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            # 按风险等级统计
            cursor.execute('''
                SELECT risk_level, COUNT(*) as count
                FROM tasks
                WHERE risk_level IS NOT NULL
                GROUP BY risk_level
            ''')
            risk_stats = {row["risk_level"]: row["count"] for row in cursor.fetchall()}
            
            # 平均耗时
            cursor.execute('''
                SELECT AVG(duration_seconds) as avg_duration
                FROM tasks
                WHERE duration_seconds IS NOT NULL
            ''')
            avg_duration = cursor.fetchone()["avg_duration"] or 0
            
            # 近期任务统计
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE created_at >= ?', (since_date,))
            recent_tasks = cursor.fetchone()[0]
            
            return {
                "total": total_tasks,
                "completed": status_stats.get("completed", 0),
                "in_progress": status_stats.get("reviewing", 0) + status_stats.get("parsing", 0),
                "error": status_stats.get("error", 0),
                "status_distribution": status_stats,
                "risk_distribution": risk_stats,
                "average_duration_seconds": round(avg_duration, 1),
                "recent_tasks": recent_tasks,
                "period_days": days
            }
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        删除任务记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            删除结果
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM review_summaries WHERE task_id = ?', (task_id,))
            cursor.execute('DELETE FROM task_files WHERE task_id = ?', (task_id,))
            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
            
            conn.commit()
            
            return {"success": True, "task_id": task_id}
    
    def cleanup_old_tasks(self, days: int = 90) -> Dict[str, Any]:
        """
        清理旧任务记录
        
        Args:
            days: 保留天数
            
        Returns:
            清理结果
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取要删除的任务数
            cursor.execute('''
                SELECT COUNT(*) FROM tasks WHERE created_at < ?
            ''', (cutoff_date,))
            count = cursor.fetchone()[0]
            
            # 删除相关记录
            cursor.execute('''
                DELETE FROM review_summaries WHERE task_id IN (
                    SELECT task_id FROM tasks WHERE created_at < ?
                )
            ''', (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM task_files WHERE task_id IN (
                    SELECT task_id FROM tasks WHERE created_at < ?
                )
            ''', (cutoff_date,))
            
            cursor.execute('DELETE FROM tasks WHERE created_at < ?', (cutoff_date,))
            
            conn.commit()
            
            logger.info(f"已清理 {count} 条旧任务记录")
            
            return {"success": True, "deleted_count": count}
    
    def save_task(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        message: str = "",
        files: List[Dict] = None,
        report_files: Dict = None
    ) -> Dict[str, Any]:
        """
        保存或更新任务记录（便捷方法）
        
        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
            message: 消息
            files: 文件列表
            report_files: 报告文件
            
        Returns:
            操作结果
        """
        # 检查任务是否存在
        task = self.get_task(task_id)
        
        if not task:
            # 创建新任务
            contract_name = files[0].get("name") if files else "未命名"
            result = self.create_task(
                task_id=task_id,
                contract_name=contract_name,
                files=files or []
            )
            if not result.get("success"):
                return result
        
        # 更新状态
        return self.update_task_status(
            task_id=task_id,
            status=status,
            progress=progress,
            message=message
        )
    
    def count_tasks(self, status: str = None) -> int:
        """
        统计任务数量
        
        Args:
            status: 过滤状态
            
        Returns:
            任务数量
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT COUNT(*) FROM tasks')
            
            return cursor.fetchone()[0]
    
    def search_tasks(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索任务
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的任务列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{keyword}%"
            
            cursor.execute('''
                SELECT t.*, rs.high_risk_count, rs.medium_risk_count, rs.low_risk_count
                FROM tasks t
                LEFT JOIN review_summaries rs ON t.task_id = rs.task_id
                WHERE t.task_id LIKE ? OR t.contract_name LIKE ? OR t.message LIKE ?
                ORDER BY t.created_at DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit))
            
            tasks = [dict(row) for row in cursor.fetchall()]
            
            # 获取文件列表
            for task in tasks:
                cursor.execute('SELECT * FROM task_files WHERE task_id = ?', (task['task_id'],))
                task['files'] = [dict(row) for row in cursor.fetchall()]
            
            return tasks


# 测试代码
if __name__ == "__main__":
    # 测试历史管理器
    manager = TaskHistoryManager(Path("data/task_history.db"))
    
    # 创建测试任务
    result = manager.create_task(
        task_id="test-001",
        contract_name="测试合同",
        files=[{"name": "test.pdf", "size": 1024, "type": "application/pdf"}]
    )
    print(f"创建任务: {result}")
    
    # 更新状态
    manager.update_task_status("test-001", "completed", 100, "评审完成", "高")
    
    # 保存评审摘要
    manager.save_review_summary("test-001", {
        "overall_assessment": "测试评估",
        "risk_level": "高",
        "key_findings": [{"severity": "高"}, {"severity": "中"}],
        "compliance_check": [{"status": "通过"}, {"status": "不通过"}],
        "recommendations": ["建议1"],
        "missing_clauses": ["条款1"]
    })
    
    # 获取任务
    task = manager.get_task("test-001")
    print(f"任务详情: {json.dumps(task, indent=2, ensure_ascii=False)}")
    
    # 获取统计
    stats = manager.get_statistics(30)
    print(f"统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
