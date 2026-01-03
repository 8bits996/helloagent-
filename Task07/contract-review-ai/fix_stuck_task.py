import sqlite3

db_path = "data/task_history.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找所有卡在 parsing 状态的任务
cursor.execute("SELECT task_id, contract_name FROM tasks WHERE status = 'parsing'")
stuck_tasks = cursor.fetchall()

print(f"发现 {len(stuck_tasks)} 个卡住的任务")

for task_id, contract_name in stuck_tasks:
    print(f"修复任务: {task_id[:8]}... ({contract_name[:30]}...)")
    
    cursor.execute("""
        UPDATE tasks 
        SET status = 'error', 
            message = '解析超时，已支持.doc格式，请重新上传尝试'
        WHERE task_id = ?
    """, (task_id,))

conn.commit()
print("已修复所有卡住的任务")

conn.close()
