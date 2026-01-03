#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清理未完成的任务"""

import sqlite3
from datetime import datetime

def cleanup_stale_tasks():
    conn = sqlite3.connect('data/task_history.db')
    cursor = conn.cursor()
    
    # 查询需要清理的任务
    cursor.execute(
        "SELECT task_id, status FROM tasks WHERE status IN ('parsing', 'ready', 'reviewing')"
    )
    stale_tasks = cursor.fetchall()
    
    print(f"找到 {len(stale_tasks)} 个需要清理的任务:")
    for task_id, status in stale_tasks:
        print(f"  - {task_id[:8]}... ({status})")
    
    if not stale_tasks:
        print("没有需要清理的任务")
        conn.close()
        return
    
    # 将这些任务标记为 error
    cursor.execute("""
        UPDATE tasks 
        SET status = 'error', 
            message = '任务已手动停止',
            updated_at = ?
        WHERE status IN ('parsing', 'ready', 'reviewing')
    """, (datetime.now().isoformat(),))
    
    affected = cursor.rowcount
    conn.commit()
    
    print(f"\n已清理 {affected} 个任务，状态已更新为 error")
    
    # 验证结果
    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    stats = cursor.fetchall()
    print("\n当前状态统计:")
    for status, count in stats:
        emoji = {'completed': '✅', 'error': '❌'}.get(status, '❓')
        print(f"  {emoji} {status}: {count}")
    
    conn.close()

if __name__ == "__main__":
    cleanup_stale_tasks()
