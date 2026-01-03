import sqlite3
import os

db_path = "data/task_history.db"

if not os.path.exists(db_path):
    print(f"数据库不存在: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"数据库表: {tables}")
    
    # 查看任务
    for table in tables:
        table_name = table[0]
        print(f"\n--- {table_name} ---")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"列: {columns}")
        
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    
    conn.close()
