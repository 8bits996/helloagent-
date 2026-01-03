# 读取Excel文件
import pandas as pd

# 尝试使用calamine引擎读取
try:
    df = pd.read_excel(r'd:\总结\Ai Agent大赛-部门赛道-体验.xlsx', engine='calamine')
    print("使用calamine引擎成功")
except Exception as e:
    print(f"calamine失败: {e}")
    # 尝试使用xlrd
    try:
        df = pd.read_excel(r'd:\总结\Ai Agent大赛-部门赛道-体验.xlsx', engine='xlrd')
        print("使用xlrd引擎成功")
    except Exception as e2:
        print(f"xlrd也失败: {e2}")
        df = None

if df is not None:
    print("\n=== 列名 ===")
    print(df.columns.tolist())
    print(f"\n=== 数据形状 ===")
    print(df.shape)
    print("\n=== 前10行数据 ===")
    print(df.head(10).to_string())
    
    # 保存为CSV以便后续处理
    df.to_csv('experience_data.csv', index=False, encoding='utf-8-sig')
    print("\n已保存为 experience_data.csv")
