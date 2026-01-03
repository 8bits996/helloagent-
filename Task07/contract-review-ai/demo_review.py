#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合同评审AI系统 - 演示脚本
完整演示上传合同 → AI评审 → 生成报告的流程
"""

import requests
import time
import json
import os
from pathlib import Path

# API配置
API_URL = "http://127.0.0.1:8000"

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step_num, text):
    """打印步骤"""
    print(f"\n[步骤 {step_num}] {text}")
    print("-" * 40)

def check_health():
    """检查系统健康状态"""
    print_step(1, "检查系统健康状态")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        data = response.json()
        
        print(f"  状态: {data['status']}")
        print(f"  服务:")
        for service, status in data['services'].items():
            emoji = "✅" if status in ['ok', 'cli_mode'] else "❌"
            print(f"    {emoji} {service}: {status}")
        
        return data['status'] == 'healthy'
    except Exception as e:
        print(f"  ❌ 健康检查失败: {e}")
        return False

def upload_contract(file_path):
    """上传合同文件"""
    print_step(2, "上传合同文件")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'files': (os.path.basename(file_path), f, 'text/markdown')}
            response = requests.post(
                f"{API_URL}/api/upload",
                files=files,
                timeout=60
            )
        
        data = response.json()
        
        if response.status_code == 200:
            print(f"  ✅ 上传成功!")
            print(f"  任务ID: {data['task_id']}")
            print(f"  文件数: {len(data['files'])}")
            for f in data['files']:
                print(f"    - {f['filename']} ({f['size']} bytes)")
            return data['task_id']
        else:
            print(f"  ❌ 上传失败: {data}")
            return None
            
    except Exception as e:
        print(f"  ❌ 上传异常: {e}")
        return None

def start_review(task_id):
    """启动AI评审"""
    print_step(3, "启动AI评审")
    
    try:
        print(f"  任务ID: {task_id}")
        print(f"  正在调用 CodeBuddy 进行智能评审...")
        print(f"  (这可能需要 3-5 分钟，请耐心等待)")
        print()
        
        # 使用SSE方式获取实时进度
        response = requests.post(
            f"{API_URL}/api/review/{task_id}",
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=600  # 10分钟超时
        )
        
        result = None
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        
                        if data.get('type') == 'progress':
                            print(f"  📊 进度: {data.get('progress', 0)}% - {data.get('message', '')}")
                        elif data.get('type') == 'result':
                            result = data
                            print(f"  ✅ 评审完成!")
                        elif data.get('type') == 'error':
                            print(f"  ❌ 评审失败: {data.get('error', '未知错误')}")
                            return None
                            
                    except json.JSONDecodeError:
                        continue
        
        return result
        
    except requests.exceptions.Timeout:
        print(f"  ❌ 评审超时，请稍后查看任务状态")
        return None
    except Exception as e:
        print(f"  ❌ 评审异常: {e}")
        return None

def check_status(task_id):
    """检查任务状态"""
    print_step(4, "检查任务状态")
    
    try:
        response = requests.get(f"{API_URL}/api/status/{task_id}", timeout=10)
        data = response.json()
        
        print(f"  任务ID: {data['task_id']}")
        print(f"  状态: {data['status']}")
        print(f"  进度: {data.get('progress', 0)}%")
        print(f"  消息: {data.get('message', '')}")
        
        return data
        
    except Exception as e:
        print(f"  ❌ 状态查询失败: {e}")
        return None

def show_results(task_id, result):
    """展示评审结果"""
    print_step(5, "评审结果摘要")
    
    if not result:
        print("  ❌ 无评审结果")
        return
    
    review_result = result.get('review_result', {})
    
    # 决策建议
    decision = review_result.get('decision', {})
    print(f"\n  📋 决策建议:")
    print(f"    建议: {decision.get('recommendation', '未知')}")
    print(f"    置信度: {decision.get('confidence', 0) * 100:.0f}%")
    
    # 风险评估
    risks = review_result.get('risks', [])
    print(f"\n  ⚠️ 风险评估:")
    print(f"    风险项数量: {len(risks)}")
    
    high_risks = [r for r in risks if r.get('level') == '高']
    medium_risks = [r for r in risks if r.get('level') == '中']
    low_risks = [r for r in risks if r.get('level') == '低']
    
    print(f"    🔴 高风险: {len(high_risks)} 项")
    print(f"    🟡 中风险: {len(medium_risks)} 项")
    print(f"    🟢 低风险: {len(low_risks)} 项")
    
    # 展示高风险项
    if high_risks:
        print(f"\n  🔴 高风险详情:")
        for i, risk in enumerate(high_risks[:3], 1):
            print(f"    {i}. {risk.get('type', '未知')}: {risk.get('description', '')[:50]}...")
    
    # 合规检查
    compliance = review_result.get('compliance', [])
    print(f"\n  ✅ 合规检查:")
    print(f"    检查项数量: {len(compliance)}")
    
    passed = len([c for c in compliance if c.get('status') == '通过'])
    failed = len([c for c in compliance if c.get('status') == '不通过'])
    
    print(f"    通过: {passed} 项")
    print(f"    不通过: {failed} 项")
    
    # 缺失条款
    missing = review_result.get('missing_clauses', [])
    print(f"\n  📝 缺失条款:")
    print(f"    缺失数量: {len(missing)} 项")
    if missing:
        for i, clause in enumerate(missing[:5], 1):
            print(f"    {i}. {clause}")

def list_reports(task_id):
    """列出可下载的报告"""
    print_step(6, "可下载报告")
    
    print(f"\n  📁 报告文件:")
    print(f"    1. 管理层摘要 (Markdown)")
    print(f"       GET /api/report/{task_id}/summary")
    print(f"    2. 综合报告 (Excel)")
    print(f"       GET /api/report/{task_id}/excel")
    print(f"    3. 风险矩阵 (CSV)")
    print(f"       GET /api/report/{task_id}/risk_matrix")
    print(f"    4. 合规检查 (CSV)")
    print(f"       GET /api/report/{task_id}/compliance")
    print(f"    5. 专业报告 (HTML)")
    print(f"       GET /api/report/{task_id}/html/preview")
    print(f"    6. 全部报告 (ZIP)")
    print(f"       GET /api/report/{task_id}/all")

def main():
    """主函数"""
    print_header("合同评审AI系统 - 演示")
    print(f"\n  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  API: {API_URL}")
    
    # 1. 检查系统健康
    if not check_health():
        print("\n❌ 系统不健康，请先启动服务!")
        return
    
    # 2. 上传合同
    contract_file = Path(__file__).parent / "data" / "uploads" / "demo_contract.md"
    if not contract_file.exists():
        print(f"\n❌ 测试合同文件不存在: {contract_file}")
        return
    
    task_id = upload_contract(str(contract_file))
    if not task_id:
        return
    
    # 3. 启动评审
    result = start_review(task_id)
    
    # 4. 检查状态
    status = check_status(task_id)
    
    # 5. 展示结果
    if result and result.get('type') == 'result':
        show_results(task_id, result)
    elif status and status.get('status') == 'completed':
        # 从状态中获取结果
        show_results(task_id, status)
    
    # 6. 列出报告
    list_reports(task_id)
    
    print_header("演示完成")
    print(f"\n  任务ID: {task_id}")
    print(f"  前端界面: http://localhost:8501")
    print(f"  HTML报告: {API_URL}/api/report/{task_id}/html/preview")
    print()

if __name__ == "__main__":
    main()
