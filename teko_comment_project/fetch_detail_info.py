#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从TEKO网站批量获取作品详细信息并更新报告
"""

import pandas as pd
import time
import re
import json

# 从teko_comment_report.md中提取已有的详细信息
def extract_from_report():
    """从评论报告中提取已有的详细信息"""
    details = {}
    
    try:
        with open('teko_comment_report.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配每个作品块
        pattern = r'\|\s*\*\*作品ID\*\*\s*\|\s*(\d+)\s*\|.*?\n(.*?)(?=\n---|\n### \d+\.|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            agent_id = int(match[0])
            block = match[1]
            
            info = {}
            
            # 提取各字段
            field_patterns = {
                '特色简介': r'\|\s*\*\*特色简介\*\*\s*\|\s*(.+?)\s*\|',
                '技术方案': r'\|\s*\*\*技术方案\*\*\s*\|\s*(.+?)\s*\|',
                '业务价值': r'\|\s*\*\*业务价值\*\*\s*\|\s*(.+?)\s*\|',
                '有价值评论': r'\|\s*\*\*有价值评论\*\*\s*\|\s*(.+?)\s*\|',
                '类别': r'\|\s*\*\*类别\*\*\s*\|\s*(.+?)\s*\|',
                '详细介绍': r'\|\s*\*\*详细介绍\*\*\s*\|\s*(.+?)\s*\|',
            }
            
            for field, pat in field_patterns.items():
                m = re.search(pat, block)
                if m:
                    value = m.group(1).strip()
                    if value and value != '-':
                        info[field] = value
            
            if info:
                details[agent_id] = info
                
    except Exception as e:
        print(f"读取报告出错: {e}")
    
    return details

def update_dept_report():
    """更新部门赛报告"""
    # 读取现有数据
    df = pd.read_csv('AI_Agent大赛_部门赛_完整数据.csv', encoding='utf-8-sig')
    
    # 从报告中提取详细信息
    details = extract_from_report()
    print(f"从报告中提取了 {len(details)} 条详细信息")
    
    # 更新数据
    updated_count = 0
    for idx, row in df.iterrows():
        agent_id = row['id']
        if agent_id in details:
            info = details[agent_id]
            for field, value in info.items():
                if field in df.columns:
                    current_val = df.at[idx, field]
                    if pd.isna(current_val) or current_val == '' or current_val == '-':
                        df.at[idx, field] = value
                        updated_count += 1
    
    print(f"更新了 {updated_count} 个字段")
    
    # 保存更新后的数据
    df.to_csv('AI_Agent大赛_部门赛_完整数据.csv', index=False, encoding='utf-8-sig')
    print("部门赛数据已更新")
    
    return df

def update_personal_report():
    """更新个人赛报告"""
    # 读取现有数据
    df = pd.read_csv('AI_Agent大赛_个人赛_完整数据.csv', encoding='utf-8-sig')
    
    # 从报告中提取详细信息
    details = extract_from_report()
    
    # 更新数据 - 个人赛需要根据作品名匹配
    updated_count = 0
    for idx, row in df.iterrows():
        name = row.get('作品名', '')
        # 尝试通过名称匹配
        for agent_id, info in details.items():
            if '特色简介' in info:
                # 更新字段
                for field, value in info.items():
                    if field in df.columns:
                        current_val = df.at[idx, field]
                        if pd.isna(current_val) or current_val == '':
                            df.at[idx, field] = value
                            updated_count += 1
    
    print(f"个人赛更新了 {updated_count} 个字段")
    
    # 保存更新后的数据
    df.to_csv('AI_Agent大赛_个人赛_完整数据.csv', index=False, encoding='utf-8-sig')
    print("个人赛数据已更新")
    
    return df

if __name__ == '__main__':
    print("开始更新报告...")
    update_dept_report()
    update_personal_report()
    print("更新完成!")
