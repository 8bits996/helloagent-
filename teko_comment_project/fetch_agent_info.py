#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量获取TEKO AI Agent大赛作品信息并生成综合报告
"""

import pandas as pd
import json
from datetime import datetime

# 读取部门赛清单
df = pd.read_csv('dept_agent_list.csv')
print(f"部门赛清单共 {len(df)} 条记录")

# 已评论的作品ID列表（从历史记录中提取）
commented_ids = [
    50, 180, 200, 220, 250, 300, 350, 450, 500, 600, 691, 750, 752, 780, 790, 800,
    810, 820, 840, 850, 860, 870, 880, 890, 910, 920, 940, 950, 960, 980, 990, 1000,
    1020, 1030, 1050, 1060, 1070, 1080, 1090, 1100, 1130, 1140, 1170, 1180, 1200,
    1210, 1230, 1240, 1250, 1300, 1380, 1400, 1420, 1440, 1460, 1500, 1640, 1650,
    1670, 1680, 1700, 1260, 1270, 1290, 1310, 1320, 1340, 1360, 1390, 1470, 1490,
    630, 660, 690, 640, 680, 861, 951, 881, 921, 941, 1021, 721, 641, 581, 561, 541,
    521, 501, 461, 441, 341, 301, 281, 261, 241, 221, 201, 181, 141, 81, 1101, 1141,
    1161, 1181, 1201, 1221, 1241, 1261, 1281, 1301, 1321, 1401, 1421, 1481, 1501,
    1521, 1561, 1581
]

# 转换ID为整数进行比较
df['id_int'] = pd.to_numeric(df['id'], errors='coerce')

# 标记已评论状态
df['已评论'] = df['id_int'].isin(commented_ids)

# 统计
total = len(df)
commented = df['已评论'].sum()
not_commented = total - commented

print(f"\n=== 统计信息 ===")
print(f"部门赛作品总数: {total}")
print(f"已评论数: {commented}")
print(f"未评论数: {not_commented}")

# 按部门统计
dept_stats = df.groupby('主导部门').agg({
    'id': 'count',
    '已评论': 'sum'
}).rename(columns={'id': '作品数', '已评论': '已评论数'})
dept_stats['未评论数'] = dept_stats['作品数'] - dept_stats['已评论数']
dept_stats = dept_stats.sort_values('作品数', ascending=False)

print(f"\n=== 按部门统计 (Top 20) ===")
print(dept_stats.head(20).to_string())

# 生成未评论清单
not_commented_df = df[~df['已评论']][['id', 'agent名', '主导部门', '项目经理', '体验链接']]
print(f"\n=== 未评论作品清单 (共{len(not_commented_df)}个) ===")
print(not_commented_df.head(30).to_string())

# 保存结果
df.to_csv('dept_agent_analysis.csv', index=False, encoding='utf-8-sig')
not_commented_df.to_csv('not_commented_agents.csv', index=False, encoding='utf-8-sig')

print(f"\n分析结果已保存到:")
print(f"- dept_agent_analysis.csv (完整分析)")
print(f"- not_commented_agents.csv (未评论清单)")
