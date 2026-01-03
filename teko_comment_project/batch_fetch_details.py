#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量从TEKO网站获取作品详细信息的脚本
需要配合浏览器MCP工具使用
"""

import pandas as pd
import json
import time

# 需要获取详细信息的作品ID列表（优先获取缺少信息的）
def get_missing_ids():
    """获取缺少详细信息的作品ID"""
    df = pd.read_csv('AI_Agent大赛_部门赛_完整数据_更新.csv', encoding='utf-8-sig')
    
    # 筛选缺少特色简介的作品
    missing = df[df['特色简介'].isna() | (df['特色简介'].astype(str).str.strip() == '') | (df['特色简介'].astype(str) == 'nan')]
    
    return missing['id'].tolist()

def update_with_details(details_list):
    """使用获取到的详细信息更新CSV"""
    df = pd.read_csv('AI_Agent大赛_部门赛_完整数据_更新.csv', encoding='utf-8-sig')
    
    # 确保字段类型为字符串
    for col in ['特色简介', '技术方案', '业务价值', '类别', '详细介绍']:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '')
        else:
            df[col] = ''
    
    # 更新数据
    updated = 0
    for detail in details_list:
        agent_id = detail.get('id')
        if agent_id:
            idx = df[df['id'] == agent_id].index
            if len(idx) > 0:
                idx = idx[0]
                for field in ['特色简介', '技术方案', '业务价值', '类别', '详细介绍']:
                    if field in detail and detail[field]:
                        current = str(df.at[idx, field]).strip()
                        if not current or current == 'nan':
                            df.at[idx, field] = detail[field]
                            updated += 1
    
    print(f"更新了 {updated} 个字段")
    
    # 保存
    df.to_csv('AI_Agent大赛_部门赛_完整数据_更新.csv', index=False, encoding='utf-8-sig')
    return df

if __name__ == '__main__':
    missing_ids = get_missing_ids()
    print(f"缺少详细信息的作品数: {len(missing_ids)}")
    print(f"前20个ID: {missing_ids[:20]}")
