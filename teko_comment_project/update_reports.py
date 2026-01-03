#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
整合teko_comment_report.md中的详细信息到报告中
"""

import pandas as pd
import re
from datetime import datetime

def extract_details_from_report():
    """从评论报告中提取所有作品的详细信息"""
    details = {}
    
    with open('teko_comment_report.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按作品块分割
    blocks = re.split(r'\n---\n', content)
    
    for block in blocks:
        # 提取作品ID
        id_match = re.search(r'\|\s*\*\*作品ID\*\*\s*\|\s*(\d+)\s*\|', block)
        if not id_match:
            continue
            
        agent_id = int(id_match.group(1))
        info = {'id': agent_id}
        
        # 提取各字段
        field_patterns = {
            '作品名': r'###\s*\d+\.\s*(.+?)\n',
            '参赛链接': r'\|\s*\*\*参赛链接\*\*\s*\|\s*(.+?)\s*\|',
            '体验链接': r'\|\s*\*\*体验链接\*\*\s*\|\s*(.+?)\s*\|',
            '部门/个人': r'\|\s*\*\*部门/个人\*\*\s*\|\s*(.+?)\s*\|',
            '申报部门': r'\|\s*\*\*申报部门\*\*\s*\|\s*(.+?)\s*\|',
            '项目经理': r'\|\s*\*\*项目经理(?:/队长)?\*\*\s*\|\s*(.+?)\s*\|',
            '类别': r'\|\s*\*\*类别\*\*\s*\|\s*(.+?)\s*\|',
            '涉及部门': r'\|\s*\*\*涉及部门\*\*\s*\|\s*(.+?)\s*\|',
            '项目成员': r'\|\s*\*\*项目成员\*\*\s*\|\s*(.+?)\s*\|',
            '团队名称': r'\|\s*\*\*团队名称\*\*\s*\|\s*(.+?)\s*\|',
            '点赞数': r'\|\s*\*\*点赞数\*\*\s*\|\s*(.+?)\s*\|',
            '评论数': r'\|\s*\*\*评论数\*\*\s*\|\s*(.+?)\s*\|',
            '特色简介': r'\|\s*\*\*特色简介\*\*\s*\|\s*(.+?)\s*\|',
            '技术方案': r'\|\s*\*\*技术方案\*\*\s*\|\s*(.+?)\s*\|',
            '业务价值': r'\|\s*\*\*业务价值\*\*\s*\|\s*(.+?)\s*\|',
            '开源/可复制': r'\|\s*\*\*开源/可复制\*\*\s*\|\s*(.+?)\s*\|',
            '可拓展方向': r'\|\s*\*\*可拓展方向\*\*\s*\|\s*(.+?)\s*\|',
            '详细介绍': r'\|\s*\*\*详细介绍\*\*\s*\|\s*(.+?)\s*\|',
            '有价值评论': r'\|\s*\*\*有价值评论\*\*\s*\|\s*(.+?)\s*\|',
            '评论内容': r'\|\s*\*\*评论内容\*\*\s*\|\s*(.+?)\s*\|',
        }
        
        for field, pattern in field_patterns.items():
            match = re.search(pattern, block)
            if match:
                value = match.group(1).strip()
                if value and value != '-':
                    info[field] = value
        
        if len(info) > 1:  # 至少有id和一个其他字段
            details[agent_id] = info
    
    return details

def update_dept_csv():
    """更新部门赛CSV"""
    print("正在更新部门赛数据...")
    
    # 读取现有数据
    df = pd.read_csv('AI_Agent大赛_部门赛_完整数据.csv', encoding='utf-8-sig')
    
    # 确保字段类型为字符串
    for col in ['特色简介', '技术方案', '业务价值', '有价值评论', '类别']:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '')
    
    # 从报告中提取详细信息
    details = extract_details_from_report()
    print(f"从报告中提取了 {len(details)} 条作品详细信息")
    
    # 字段映射
    field_mapping = {
        '特色简介': '特色简介',
        '技术方案': '技术方案',
        '业务价值': '业务价值',
        '有价值评论': '有价值评论',
        '类别': '类别',
        '评论内容': '有价值评论',  # 评论内容也可以作为有价值评论
    }
    
    # 更新数据
    updated_count = 0
    for idx, row in df.iterrows():
        agent_id = row['id']
        if agent_id in details:
            info = details[agent_id]
            for src_field, dst_field in field_mapping.items():
                if src_field in info and dst_field in df.columns:
                    current_val = df.at[idx, dst_field]
                    if pd.isna(current_val) or str(current_val).strip() == '':
                        df.at[idx, dst_field] = info[src_field]
                        updated_count += 1
    
    print(f"更新了 {updated_count} 个字段")
    
    # 标记已评论
    for idx, row in df.iterrows():
        agent_id = row['id']
        if agent_id in details:
            df.at[idx, '是否已评论'] = '是'
    
    # 保存 - 使用新文件名避免文件占用问题
    output_file = 'AI_Agent大赛_部门赛_完整数据_更新.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"部门赛CSV已保存到: {output_file}")
    
    return df

def update_personal_csv():
    """更新个人赛CSV"""
    print("\n正在更新个人赛数据...")
    
    # 读取现有数据
    df = pd.read_csv('AI_Agent大赛_个人赛_完整数据.csv', encoding='utf-8-sig')
    
    # 从报告中提取详细信息
    details = extract_details_from_report()
    
    # 筛选个人作品
    personal_details = {k: v for k, v in details.items() 
                       if '部门/个人' in v and '个人' in v['部门/个人']}
    print(f"找到 {len(personal_details)} 条个人作品详细信息")
    
    # 添加缺失的列
    for col in ['特色简介', '技术方案', '业务价值', '有价值评论']:
        if col not in df.columns:
            df[col] = ''
    
    # 通过作品名匹配更新
    updated_count = 0
    for idx, row in df.iterrows():
        name = str(row.get('作品名', '')).strip()
        
        # 在详细信息中查找匹配的作品
        for agent_id, info in personal_details.items():
            info_name = info.get('作品名', '')
            if info_name and (name in info_name or info_name in name):
                # 更新字段
                for field in ['特色简介', '技术方案', '业务价值', '有价值评论', '评论内容']:
                    if field in info:
                        target_field = '有价值评论' if field == '评论内容' else field
                        if target_field in df.columns:
                            current_val = df.at[idx, target_field]
                            if pd.isna(current_val) or str(current_val).strip() == '':
                                df.at[idx, target_field] = info[field]
                                updated_count += 1
                df.at[idx, '是否已评论'] = '是'
                break
    
    print(f"更新了 {updated_count} 个字段")
    
    # 保存 - 使用新文件名避免文件占用问题
    output_file = 'AI_Agent大赛_个人赛_完整数据_更新.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"个人赛CSV已保存到: {output_file}")
    
    return df

def generate_updated_excel():
    """生成更新后的Excel报告"""
    print("\n正在生成Excel报告...")
    
    # 部门赛 - 尝试读取更新后的文件，如果不存在则读取原文件
    try:
        dept_df = pd.read_csv('AI_Agent大赛_部门赛_完整数据_更新.csv', encoding='utf-8-sig')
    except:
        dept_df = pd.read_csv('AI_Agent大赛_部门赛_完整数据.csv', encoding='utf-8-sig')
    
    # 确保字段类型为字符串
    for col in ['特色简介', '技术方案', '业务价值', '有价值评论', '类别']:
        if col in dept_df.columns:
            dept_df[col] = dept_df[col].astype(str).replace('nan', '')
    
    with pd.ExcelWriter('AI_Agent大赛_部门赛_综合报告_更新.xlsx', engine='openpyxl') as writer:
        # 摘要页
        summary_data = {
            '指标': ['总作品数', '有详细信息', '已评论', '有体验链接', '有评分'],
            '数值': [
                len(dept_df),
                len(dept_df[dept_df['特色简介'].notna() & (dept_df['特色简介'] != '')]),
                len(dept_df[dept_df['是否已评论'] == '是']),
                len(dept_df[dept_df['体验链接'].notna() & (dept_df['体验链接'] != '')]),
                len(dept_df[dept_df['综合评分'].notna()])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='摘要', index=False)
        
        # 完整数据
        dept_df.to_excel(writer, sheet_name='完整数据', index=False)
        
        # 有详细信息的作品
        detailed = dept_df[dept_df['特色简介'].notna() & (dept_df['特色简介'] != '')]
        detailed.to_excel(writer, sheet_name='有详细信息', index=False)
        
        # 已评分作品
        scored = dept_df[dept_df['综合评分'].notna()]
        scored.to_excel(writer, sheet_name='已评分', index=False)
        
        # 缺少信息
        missing = dept_df[dept_df['缺少字段'].notna() & (dept_df['缺少字段'] != '')]
        missing.to_excel(writer, sheet_name='缺少信息', index=False)
    
    print("部门赛Excel已生成")
    
    # 个人赛 - 尝试读取更新后的文件
    try:
        personal_df = pd.read_csv('AI_Agent大赛_个人赛_完整数据_更新.csv', encoding='utf-8-sig')
    except:
        personal_df = pd.read_csv('AI_Agent大赛_个人赛_完整数据.csv', encoding='utf-8-sig')
    
    with pd.ExcelWriter('AI_Agent大赛_个人赛_综合报告_更新.xlsx', engine='openpyxl') as writer:
        # 摘要页
        summary_data = {
            '指标': ['总作品数', '可体验', '有详细信息', '已评论'],
            '数值': [
                len(personal_df),
                len(personal_df[personal_df['可体验'] == '是']),
                len(personal_df[personal_df['特色简介'].notna() & (personal_df['特色简介'] != '')]) if '特色简介' in personal_df.columns else 0,
                len(personal_df[personal_df['是否已评论'] == '是'])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='摘要', index=False)
        
        # 完整数据
        personal_df.to_excel(writer, sheet_name='完整数据', index=False)
        
        # 可体验作品
        can_try = personal_df[personal_df['可体验'] == '是']
        can_try.to_excel(writer, sheet_name='可体验', index=False)
    
    print("个人赛Excel已生成")

def generate_updated_html():
    """生成更新后的HTML报告"""
    print("\n正在生成HTML报告...")
    
    # 部门赛 - 尝试读取更新后的文件
    try:
        dept_df = pd.read_csv('AI_Agent大赛_部门赛_完整数据_更新.csv', encoding='utf-8-sig')
    except:
        dept_df = pd.read_csv('AI_Agent大赛_部门赛_完整数据.csv', encoding='utf-8-sig')
    
    # 确保字段类型为字符串
    for col in ['特色简介', '技术方案', '业务价值', '有价值评论', '类别']:
        if col in dept_df.columns:
            dept_df[col] = dept_df[col].astype(str).replace('nan', '')
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent大赛 - 部门赛道综合报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        h1 {{ text-align: center; color: #333; margin-bottom: 30px; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .tab {{ padding: 10px 20px; background: #fff; border: none; cursor: pointer; border-radius: 8px; font-size: 14px; }}
        .tab.active {{ background: #1890ff; color: #fff; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #fff; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ font-size: 32px; color: #1890ff; margin-bottom: 10px; }}
        .stat-card p {{ color: #666; }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #fafafa; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #f5f5f5; }}
        .search {{ margin-bottom: 20px; }}
        .search input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }}
        .table-container {{ overflow-x: auto; max-height: 600px; overflow-y: auto; }}
        .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .badge-success {{ background: #52c41a; color: #fff; }}
        .badge-warning {{ background: #faad14; color: #fff; }}
        .update-time {{ text-align: center; color: #999; margin-top: 20px; }}
        a {{ color: #1890ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 AI Agent大赛 - 部门赛道综合报告</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('summary')">📊 摘要</button>
            <button class="tab" onclick="showTab('all')">📋 全部作品</button>
            <button class="tab" onclick="showTab('detailed')">📝 有详细信息</button>
            <button class="tab" onclick="showTab('scored')">⭐ 已评分</button>
            <button class="tab" onclick="showTab('commented')">💬 已评论</button>
        </div>
        
        <div id="summary" class="tab-content active">
            <div class="summary">
                <div class="stat-card">
                    <h3>{len(dept_df)}</h3>
                    <p>总作品数</p>
                </div>
                <div class="stat-card">
                    <h3>{len(dept_df[dept_df['特色简介'].notna() & (dept_df['特色简介'] != '')])}</h3>
                    <p>有详细信息</p>
                </div>
                <div class="stat-card">
                    <h3>{len(dept_df[dept_df['是否已评论'] == '是'])}</h3>
                    <p>已评论</p>
                </div>
                <div class="stat-card">
                    <h3>{len(dept_df[dept_df['综合评分'].notna()])}</h3>
                    <p>已评分</p>
                </div>
            </div>
        </div>
        
        <div id="all" class="tab-content">
            <div class="search">
                <input type="text" id="searchAll" placeholder="搜索作品名、部门、项目经理..." onkeyup="searchTable('allTable', 'searchAll')">
            </div>
            <div class="table-container">
                <table id="allTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>作品名</th>
                            <th>主导部门</th>
                            <th>项目经理</th>
                            <th>特色简介</th>
                            <th>评分</th>
                            <th>链接</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    for _, row in dept_df.iterrows():
        intro = str(row.get('特色简介', ''))[:100] + '...' if len(str(row.get('特色简介', ''))) > 100 else str(row.get('特色简介', ''))
        score = row.get('综合评分', '')
        score_html = f'<span class="badge badge-success">{score}</span>' if pd.notna(score) else '-'
        link = row.get('TEKO链接', '')
        
        html_content += f'''                        <tr>
                            <td>{row['id']}</td>
                            <td>{row['agent名']}</td>
                            <td>{row.get('主导部门', '-')}</td>
                            <td>{row.get('项目经理', '-')}</td>
                            <td>{intro if intro and intro != 'nan' else '-'}</td>
                            <td>{score_html}</td>
                            <td><a href="{link}" target="_blank">查看</a></td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="detailed" class="tab-content">
            <div class="search">
                <input type="text" id="searchDetailed" placeholder="搜索..." onkeyup="searchTable('detailedTable', 'searchDetailed')">
            </div>
            <div class="table-container">
                <table id="detailedTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>作品名</th>
                            <th>特色简介</th>
                            <th>技术方案</th>
                            <th>业务价值</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    detailed = dept_df[dept_df['特色简介'].notna() & (dept_df['特色简介'] != '')]
    for _, row in detailed.iterrows():
        html_content += f'''                        <tr>
                            <td>{row['id']}</td>
                            <td>{row['agent名']}</td>
                            <td>{str(row.get('特色简介', '-'))[:200]}</td>
                            <td>{str(row.get('技术方案', '-'))[:150]}</td>
                            <td>{str(row.get('业务价值', '-'))[:150]}</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="scored" class="tab-content">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>作品名</th>
                            <th>评分</th>
                            <th>评委建议</th>
                            <th>特点</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    scored = dept_df[dept_df['综合评分'].notna()]
    for _, row in scored.iterrows():
        html_content += f'''                        <tr>
                            <td>{row['id']}</td>
                            <td>{row['agent名']}</td>
                            <td><span class="badge badge-success">{row['综合评分']}</span></td>
                            <td>{str(row.get('评委建议', '-'))[:200]}</td>
                            <td>{str(row.get('特点', '-'))[:150]}</td>
                        </tr>
'''
    
    html_content += '''                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="commented" class="tab-content">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>作品名</th>
                            <th>有价值评论</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    commented = dept_df[dept_df['是否已评论'] == '是']
    for _, row in commented.iterrows():
        html_content += f'''                        <tr>
                            <td>{row['id']}</td>
                            <td>{row['agent名']}</td>
                            <td>{str(row.get('有价值评论', '-'))}</td>
                        </tr>
'''
    
    html_content += f'''                    </tbody>
                </table>
            </div>
        </div>
        
        <p class="update-time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <script>
        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function searchTable(tableId, inputId) {{
            const input = document.getElementById(inputId);
            const filter = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {{
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                for (let j = 0; j < cells.length; j++) {{
                    if (cells[j].textContent.toLowerCase().includes(filter)) {{
                        found = true;
                        break;
                    }}
                }}
                rows[i].style.display = found ? '' : 'none';
            }}
        }}
    </script>
</body>
</html>'''
    
    with open('AI_Agent大赛_部门赛_综合报告_更新.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("部门赛HTML已生成")

if __name__ == '__main__':
    print("=" * 50)
    print("开始更新AI Agent大赛报告")
    print("=" * 50)
    
    # 更新CSV
    update_dept_csv()
    update_personal_csv()
    
    # 生成Excel
    generate_updated_excel()
    
    # 生成HTML
    generate_updated_html()
    
    print("\n" + "=" * 50)
    print("所有报告更新完成!")
    print("=" * 50)
