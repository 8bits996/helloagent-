"""
HTML 报告生成器
Contract Review AI - Professional HTML Report Generator

生成专业的多页签网页格式报告，包含：
1. 决策总览 - 整体评估和关键指标
2. 风险详情 - 详细风险分析
3. 合规检查 - 合规性检查结果
4. 修改建议 - 具体改进建议
5. 缺失条款 - 缺失条款清单
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """
    专业 HTML 报告生成器
    
    生成可独立查看的单页 HTML 报告，包含多个页签
    """
    
    def __init__(self):
        self.risk_colors = {
            "高": {"bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b", "badge": "#dc2626"},
            "中": {"bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e", "badge": "#d97706"},
            "低": {"bg": "#d1fae5", "border": "#10b981", "text": "#065f46", "badge": "#059669"}
        }
        
        self.status_colors = {
            "通过": {"bg": "#d1fae5", "text": "#065f46", "icon": "✓"},
            "不通过": {"bg": "#fee2e2", "text": "#991b1b", "icon": "✗"},
            "需关注": {"bg": "#fef3c7", "text": "#92400e", "icon": "!"}
        }
    
    def generate_html_report(
        self,
        review_result: Dict[str, Any],
        output_path: Path,
        contract_name: str = "合同",
        task_id: str = ""
    ) -> Path:
        """
        生成完整的 HTML 报告
        """
        output_path = Path(output_path)
        
        # 提取数据
        overall = review_result.get("overall_assessment", "")
        risk_level = review_result.get("risk_level", "未知")
        findings = review_result.get("key_findings", [])
        compliance = review_result.get("compliance_check", [])
        recommendations = review_result.get("recommendations", [])
        missing_clauses = review_result.get("missing_clauses", [])
        
        # 计算统计数据
        stats = self._calculate_stats(findings, compliance, missing_clauses)
        
        # 生成 HTML
        html_content = self._generate_full_html(
            contract_name=contract_name,
            task_id=task_id,
            overall=overall,
            risk_level=risk_level,
            findings=findings,
            compliance=compliance,
            recommendations=recommendations,
            missing_clauses=missing_clauses,
            stats=stats
        )
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"HTML报告已生成: {output_path}")
        
        return output_path
    
    def _calculate_stats(self, findings, compliance, missing_clauses):
        """计算统计数据"""
        return {
            "total_findings": len(findings),
            "high_risk": sum(1 for f in findings if f.get("severity") == "高"),
            "medium_risk": sum(1 for f in findings if f.get("severity") == "中"),
            "low_risk": sum(1 for f in findings if f.get("severity") == "低"),
            "compliance_pass": sum(1 for c in compliance if c.get("status") == "通过"),
            "compliance_fail": sum(1 for c in compliance if c.get("status") == "不通过"),
            "compliance_warn": sum(1 for c in compliance if c.get("status") == "需关注"),
            "total_compliance": len(compliance),
            "missing_count": len(missing_clauses)
        }
    
    def _generate_full_html(self, **kwargs):
        """生成完整的 HTML 内容"""
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合同评审报告 - {kwargs["contract_name"]}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        {self._generate_header(kwargs["contract_name"], kwargs["task_id"], kwargs["risk_level"])}
        
        <!-- 页签导航 -->
        <div class="tab-container">
            <div class="tabs">
                <button class="tab-btn active" onclick="openTab(event, 'overview')">
                    <span class="tab-icon">📊</span> 决策总览
                </button>
                <button class="tab-btn" onclick="openTab(event, 'risks')">
                    <span class="tab-icon">⚠️</span> 风险详情
                    <span class="tab-badge risk">{kwargs["stats"]["high_risk"]}</span>
                </button>
                <button class="tab-btn" onclick="openTab(event, 'compliance')">
                    <span class="tab-icon">✅</span> 合规检查
                    <span class="tab-badge warn">{kwargs["stats"]["compliance_fail"]}</span>
                </button>
                <button class="tab-btn" onclick="openTab(event, 'recommendations')">
                    <span class="tab-icon">💡</span> 修改建议
                    <span class="tab-badge info">{len(kwargs["recommendations"])}</span>
                </button>
                <button class="tab-btn" onclick="openTab(event, 'missing')">
                    <span class="tab-icon">📋</span> 缺失条款
                    <span class="tab-badge">{kwargs["stats"]["missing_count"]}</span>
                </button>
            </div>
            
            <!-- 决策总览 -->
            <div id="overview" class="tab-content active">
                {self._generate_overview_tab(kwargs["overall"], kwargs["risk_level"], kwargs["stats"], kwargs["findings"])}
            </div>
            
            <!-- 风险详情 -->
            <div id="risks" class="tab-content">
                {self._generate_risks_tab(kwargs["findings"])}
            </div>
            
            <!-- 合规检查 -->
            <div id="compliance" class="tab-content">
                {self._generate_compliance_tab(kwargs["compliance"], kwargs["stats"])}
            </div>
            
            <!-- 修改建议 -->
            <div id="recommendations" class="tab-content">
                {self._generate_recommendations_tab(kwargs["recommendations"])}
            </div>
            
            <!-- 缺失条款 -->
            <div id="missing" class="tab-content">
                {self._generate_missing_tab(kwargs["missing_clauses"])}
            </div>
        </div>
        
        <!-- 页脚 -->
        {self._generate_footer()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>'''
    
    def _get_css_styles(self):
        """获取 CSS 样式"""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1f2937;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }
        
        /* 头部样式 */
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 30px 40px;
        }
        
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .risk-badge {
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 700;
            text-align: center;
        }
        
        .risk-high { background: #dc2626; }
        .risk-medium { background: #d97706; }
        .risk-low { background: #059669; }
        
        .header-meta {
            display: flex;
            gap: 30px;
            font-size: 13px;
            opacity: 0.9;
        }
        
        .header-meta span {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* 页签样式 */
        .tab-container {
            padding: 0;
        }
        
        .tabs {
            display: flex;
            background: #f8fafc;
            border-bottom: 2px solid #e2e8f0;
            overflow-x: auto;
        }
        
        .tab-btn {
            flex: 1;
            min-width: 150px;
            padding: 16px 24px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #64748b;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            position: relative;
        }
        
        .tab-btn:hover {
            background: #f1f5f9;
            color: #334155;
        }
        
        .tab-btn.active {
            color: #1e40af;
            background: white;
            border-bottom: 3px solid #3b82f6;
            margin-bottom: -2px;
        }
        
        .tab-icon {
            font-size: 18px;
        }
        
        .tab-badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            background: #e2e8f0;
            color: #475569;
        }
        
        .tab-badge.risk { background: #fee2e2; color: #991b1b; }
        .tab-badge.warn { background: #fef3c7; color: #92400e; }
        .tab-badge.info { background: #dbeafe; color: #1e40af; }
        
        .tab-content {
            display: none;
            padding: 30px 40px;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* 统计卡片 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card.highlight {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
        }
        
        .stat-card.danger {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 13px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* 整体评估 */
        .assessment-box {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-left: 4px solid #3b82f6;
            border-radius: 0 12px 12px 0;
            padding: 24px;
            margin-bottom: 30px;
        }
        
        .assessment-box h3 {
            color: #1e40af;
            margin-bottom: 12px;
            font-size: 16px;
        }
        
        .assessment-box p {
            line-height: 1.8;
            color: #334155;
        }
        
        /* 风险卡片 */
        .risk-card {
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .risk-card:hover {
            transform: translateX(4px);
        }
        
        .risk-card-header {
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .risk-card-header.high { background: #fee2e2; border-left: 5px solid #dc2626; }
        .risk-card-header.medium { background: #fef3c7; border-left: 5px solid #d97706; }
        .risk-card-header.low { background: #d1fae5; border-left: 5px solid #059669; }
        
        .risk-card-title {
            font-weight: 600;
            font-size: 16px;
        }
        
        .risk-level-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }
        
        .risk-level-badge.high { background: #dc2626; }
        .risk-level-badge.medium { background: #d97706; }
        .risk-level-badge.low { background: #059669; }
        
        .risk-card-body {
            padding: 20px;
            border-top: 1px solid #f1f5f9;
        }
        
        .risk-detail {
            margin-bottom: 16px;
        }
        
        .risk-detail:last-child {
            margin-bottom: 0;
        }
        
        .risk-detail-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        
        .risk-detail-content {
            color: #334155;
            line-height: 1.6;
        }
        
        .location-tag {
            display: inline-block;
            background: #f1f5f9;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 13px;
            color: #475569;
        }
        
        /* 合规检查表格 */
        .compliance-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .compliance-table th {
            background: #f8fafc;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            color: #475569;
            border-bottom: 2px solid #e2e8f0;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .compliance-table td {
            padding: 16px;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .compliance-table tr:hover {
            background: #f8fafc;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }
        
        .status-pass { background: #d1fae5; color: #065f46; }
        .status-fail { background: #fee2e2; color: #991b1b; }
        .status-warn { background: #fef3c7; color: #92400e; }
        
        /* 建议列表 */
        .recommendation-list {
            list-style: none;
        }
        
        .recommendation-item {
            display: flex;
            gap: 16px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            margin-bottom: 16px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .recommendation-item:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.1);
        }
        
        .recommendation-number {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }
        
        .recommendation-content {
            flex: 1;
            line-height: 1.7;
            color: #334155;
        }
        
        /* 缺失条款 */
        .missing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }
        
        .missing-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: #fef2f2;
            border-radius: 10px;
            border-left: 4px solid #ef4444;
        }
        
        .missing-icon {
            width: 32px;
            height: 32px;
            background: #fee2e2;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #dc2626;
            font-size: 18px;
        }
        
        .missing-text {
            color: #991b1b;
            font-weight: 500;
        }
        
        /* 进度条 */
        .progress-bar {
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .progress-fill.success { background: linear-gradient(90deg, #10b981, #34d399); }
        .progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
        .progress-fill.danger { background: linear-gradient(90deg, #ef4444, #f87171); }
        
        /* 页脚 */
        .footer {
            background: #f8fafc;
            padding: 24px 40px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
        }
        
        .footer-disclaimer {
            background: #fef3c7;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            font-size: 13px;
            color: #92400e;
        }
        
        .footer-meta {
            font-size: 12px;
            color: #64748b;
        }
        
        /* 打印样式 */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
            }
            
            .tabs {
                display: none;
            }
            
            .tab-content {
                display: block !important;
                page-break-after: always;
            }
        }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .header {
                padding: 20px;
            }
            
            .header-top {
                flex-direction: column;
                gap: 16px;
            }
            
            .header h1 {
                font-size: 22px;
            }
            
            .tabs {
                flex-wrap: nowrap;
                overflow-x: auto;
            }
            
            .tab-btn {
                min-width: 120px;
                padding: 12px 16px;
                font-size: 13px;
            }
            
            .tab-content {
                padding: 20px;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        '''
    
    def _get_javascript(self):
        """获取 JavaScript 代码"""
        return '''
        function openTab(evt, tabName) {
            // 隐藏所有页签内容
            var tabContents = document.getElementsByClassName("tab-content");
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove("active");
            }
            
            // 移除所有按钮的激活状态
            var tabBtns = document.getElementsByClassName("tab-btn");
            for (var i = 0; i < tabBtns.length; i++) {
                tabBtns[i].classList.remove("active");
            }
            
            // 显示选中的页签内容
            document.getElementById(tabName).classList.add("active");
            
            // 激活选中的按钮
            evt.currentTarget.classList.add("active");
        }
        
        // 页面加载动画
        document.addEventListener("DOMContentLoaded", function() {
            const cards = document.querySelectorAll(".stat-card, .risk-card, .recommendation-item");
            cards.forEach((card, index) => {
                card.style.opacity = "0";
                card.style.transform = "translateY(20px)";
                setTimeout(() => {
                    card.style.transition = "all 0.5s ease";
                    card.style.opacity = "1";
                    card.style.transform = "translateY(0)";
                }, index * 100);
            });
        });
        '''
    
    def _generate_header(self, contract_name, task_id, risk_level):
        """生成头部"""
        risk_class = {"高": "high", "中": "medium", "低": "low"}.get(risk_level, "")
        risk_text = {"高": "高风险", "中": "中风险", "低": "低风险"}.get(risk_level, "未知")
        
        return f'''
        <div class="header">
            <div class="header-top">
                <div>
                    <h1>📄 合同评审报告</h1>
                    <div class="subtitle">{contract_name}</div>
                </div>
                <div class="risk-badge risk-{risk_class}">
                    {risk_text}
                </div>
            </div>
            <div class="header-meta">
                <span>📅 {datetime.now().strftime("%Y年%m月%d日 %H:%M")}</span>
                <span>🔖 任务ID: {task_id[:8] if task_id else "N/A"}...</span>
                <span>🤖 AI智能评审</span>
            </div>
        </div>
        '''
    
    def _generate_overview_tab(self, overall, risk_level, stats, findings):
        """生成决策总览页签"""
        # 计算合规通过率
        total = stats["total_compliance"]
        pass_rate = round(stats["compliance_pass"] / total * 100) if total > 0 else 0
        
        # 风险分布图
        high_pct = round(stats["high_risk"] / stats["total_findings"] * 100) if stats["total_findings"] > 0 else 0
        medium_pct = round(stats["medium_risk"] / stats["total_findings"] * 100) if stats["total_findings"] > 0 else 0
        low_pct = 100 - high_pct - medium_pct
        
        # 关键发现摘要（只取高风险）
        high_risk_findings = [f for f in findings if f.get("severity") == "高"][:3]
        findings_html = ""
        for f in high_risk_findings:
            findings_html += f'''
            <div style="background: #fef2f2; padding: 12px; border-radius: 8px; margin-top: 12px; border-left: 3px solid #ef4444;">
                <strong style="color: #991b1b;">{f.get("category", "")}</strong>: {f.get("description", "")[:100]}...
            </div>
            '''
        
        return f'''
        <h2 style="margin-bottom: 24px; color: #1e293b;">决策总览</h2>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card {"danger" if risk_level == "高" else "highlight" if risk_level == "中" else ""}">
                <div class="stat-value">{risk_level}</div>
                <div class="stat-label">整体风险等级</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #dc2626;">{stats["high_risk"]}</div>
                <div class="stat-label">高风险项</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #d97706;">{stats["compliance_fail"]}</div>
                <div class="stat-label">合规问题</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #3b82f6;">{stats["missing_count"]}</div>
                <div class="stat-label">缺失条款</div>
            </div>
        </div>
        
        <!-- 整体评估 -->
        <div class="assessment-box">
            <h3>📝 整体评估</h3>
            <p>{overall}</p>
        </div>
        
        <!-- 风险分布 -->
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
            <h3 style="margin-bottom: 16px; color: #334155;">风险分布</h3>
            <div style="display: flex; gap: 24px; align-items: center;">
                <div style="flex: 1;">
                    <div style="display: flex; height: 24px; border-radius: 12px; overflow: hidden;">
                        <div style="width: {high_pct}%; background: #ef4444;"></div>
                        <div style="width: {medium_pct}%; background: #f59e0b;"></div>
                        <div style="width: {low_pct}%; background: #10b981;"></div>
                    </div>
                </div>
                <div style="display: flex; gap: 16px; font-size: 13px;">
                    <span><span style="color: #ef4444;">●</span> 高 {stats["high_risk"]}</span>
                    <span><span style="color: #f59e0b;">●</span> 中 {stats["medium_risk"]}</span>
                    <span><span style="color: #10b981;">●</span> 低 {stats["low_risk"]}</span>
                </div>
            </div>
        </div>
        
        <!-- 合规通过率 -->
        <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
            <h3 style="margin-bottom: 16px; color: #334155;">合规检查通过率</h3>
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 48px; font-weight: 700; color: {"#10b981" if pass_rate >= 70 else "#f59e0b" if pass_rate >= 50 else "#ef4444"};">
                    {pass_rate}%
                </div>
                <div style="flex: 1;">
                    <div class="progress-bar">
                        <div class="progress-fill {"success" if pass_rate >= 70 else "warning" if pass_rate >= 50 else "danger"}" 
                             style="width: {pass_rate}%;"></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 13px; color: #64748b;">
                        {stats["compliance_pass"]} 通过 / {stats["compliance_fail"]} 不通过 / {stats["compliance_warn"]} 需关注
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 关键发现摘要 -->
        {"<div style='background: #fff7ed; border-radius: 12px; padding: 24px;'><h3 style='margin-bottom: 12px; color: #9a3412;'>⚠️ 需要重点关注</h3>" + findings_html + "</div>" if high_risk_findings else ""}
        '''
    
    def _generate_risks_tab(self, findings):
        """生成风险详情页签"""
        if not findings:
            return '<div style="text-align: center; padding: 60px; color: #64748b;">✅ 未发现显著风险</div>'
        
        cards_html = ""
        for i, finding in enumerate(findings, 1):
            severity = finding.get("severity", "未知")
            severity_class = {"高": "high", "中": "medium", "低": "low"}.get(severity, "")
            
            cards_html += f'''
            <div class="risk-card">
                <div class="risk-card-header {severity_class}">
                    <span class="risk-card-title">#{i} {finding.get("category", "未分类")}</span>
                    <span class="risk-level-badge {severity_class}">{severity}风险</span>
                </div>
                <div class="risk-card-body">
                    <div class="risk-detail">
                        <div class="risk-detail-label">📍 问题位置</div>
                        <div class="risk-detail-content">
                            <span class="location-tag">{finding.get("location", "未指定")}</span>
                        </div>
                    </div>
                    <div class="risk-detail">
                        <div class="risk-detail-label">📋 问题描述</div>
                        <div class="risk-detail-content">{finding.get("description", "")}</div>
                    </div>
                    <div class="risk-detail">
                        <div class="risk-detail-label">💡 改进建议</div>
                        <div class="risk-detail-content" style="color: #1e40af;">{finding.get("suggestion", "")}</div>
                    </div>
                </div>
            </div>
            '''
        
        return f'''
        <h2 style="margin-bottom: 24px; color: #1e293b;">风险详情分析</h2>
        <p style="color: #64748b; margin-bottom: 24px;">共发现 <strong>{len(findings)}</strong> 个风险点，请按优先级依次处理。</p>
        {cards_html}
        '''
    
    def _generate_compliance_tab(self, compliance, stats):
        """生成合规检查页签"""
        if not compliance:
            return '<div style="text-align: center; padding: 60px; color: #64748b;">暂无合规检查数据</div>'
        
        rows_html = ""
        for i, check in enumerate(compliance, 1):
            status = check.get("status", "未知")
            status_class = {"通过": "pass", "不通过": "fail", "需关注": "warn"}.get(status, "")
            icon = {"通过": "✓", "不通过": "✗", "需关注": "!"}.get(status, "?")
            
            rows_html += f'''
            <tr>
                <td style="font-weight: 500; color: #334155;">{i}</td>
                <td style="font-weight: 500;">{check.get("item", "")}</td>
                <td>
                    <span class="status-badge status-{status_class}">
                        <span>{icon}</span> {status}
                    </span>
                </td>
                <td style="color: #64748b;">{check.get("details", "")}</td>
            </tr>
            '''
        
        return f'''
        <h2 style="margin-bottom: 24px; color: #1e293b;">合规检查结果</h2>
        
        <!-- 统计摘要 -->
        <div style="display: flex; gap: 16px; margin-bottom: 24px;">
            <div style="flex: 1; background: #d1fae5; padding: 16px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #065f46;">{stats["compliance_pass"]}</div>
                <div style="font-size: 13px; color: #047857;">通过</div>
            </div>
            <div style="flex: 1; background: #fee2e2; padding: 16px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #991b1b;">{stats["compliance_fail"]}</div>
                <div style="font-size: 13px; color: #dc2626;">不通过</div>
            </div>
            <div style="flex: 1; background: #fef3c7; padding: 16px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #92400e;">{stats["compliance_warn"]}</div>
                <div style="font-size: 13px; color: #d97706;">需关注</div>
            </div>
        </div>
        
        <table class="compliance-table">
            <thead>
                <tr>
                    <th style="width: 60px;">#</th>
                    <th style="width: 200px;">检查项目</th>
                    <th style="width: 120px;">状态</th>
                    <th>详细说明</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        '''
    
    def _generate_recommendations_tab(self, recommendations):
        """生成修改建议页签"""
        if not recommendations:
            return '<div style="text-align: center; padding: 60px; color: #64748b;">暂无修改建议</div>'
        
        items_html = ""
        for i, rec in enumerate(recommendations, 1):
            items_html += f'''
            <li class="recommendation-item">
                <div class="recommendation-number">{i}</div>
                <div class="recommendation-content">{rec}</div>
            </li>
            '''
        
        return f'''
        <h2 style="margin-bottom: 24px; color: #1e293b;">修改建议</h2>
        <p style="color: #64748b; margin-bottom: 24px;">
            以下是基于评审结果提出的 <strong>{len(recommendations)}</strong> 条改进建议，建议按顺序逐一落实。
        </p>
        <ul class="recommendation-list">
            {items_html}
        </ul>
        '''
    
    def _generate_missing_tab(self, missing_clauses):
        """生成缺失条款页签"""
        if not missing_clauses:
            return '<div style="text-align: center; padding: 60px; color: #64748b;">✅ 合同条款完整</div>'
        
        items_html = ""
        for clause in missing_clauses:
            items_html += f'''
            <div class="missing-item">
                <div class="missing-icon">!</div>
                <div class="missing-text">{clause}</div>
            </div>
            '''
        
        return f'''
        <h2 style="margin-bottom: 24px; color: #1e293b;">缺失条款清单</h2>
        <div style="background: #fef2f2; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
            <p style="color: #991b1b; margin: 0;">
                ⚠️ 发现 <strong>{len(missing_clauses)}</strong> 项重要条款缺失，建议在签署前补充完善。
            </p>
        </div>
        <div class="missing-grid">
            {items_html}
        </div>
        '''
    
    def _generate_footer(self):
        """生成页脚"""
        return f'''
        <div class="footer">
            <div class="footer-disclaimer">
                ⚠️ 免责声明：本报告由 AI 智能评审系统自动生成，仅供参考。建议在签署合同前，由专业法律人员进行最终审核。
            </div>
            <div class="footer-meta">
                报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
                Contract Review AI System v2.0 | 
                © 2025 CFP Study
            </div>
        </div>
        '''


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    # 测试数据
    test_result = {
        "overall_assessment": "该技术服务合同框架基本完整，涵盖了服务内容、费用、期限、验收和违约责任等核心要素。但合同存在多项重要条款缺失，交付范围和验收标准不够具体，知识产权归属未约定，整体风险等级较高，建议补充完善后再签署。",
        "risk_level": "高",
        "key_findings": [
            {
                "category": "交付风险",
                "severity": "高",
                "description": "交付分工界面不明确，验收标准引用'需求说明书'但合同未附该文件，ERP系统具体功能模块、定制开发范围均未明确定义，存在交付争议隐患",
                "location": "第二条 服务内容、第五条 验收标准",
                "suggestion": "1) 将需求说明书作为合同附件并明确其法律效力；2) 详细列明ERP系统功能模块清单；3) 明确'系统集成与部署'的具体内容和环境要求"
            },
            {
                "category": "知识产权风险",
                "severity": "高",
                "description": "合同未约定软件著作权归属、源代码交付、第三方组件授权等知识产权相关条款，可能导致后续系统维护和二次开发受限",
                "location": "全文缺失",
                "suggestion": "增加知识产权条款，明确定制开发部分著作权归属、源代码是否交付及交付时间、使用的第三方组件清单及授权方式"
            },
            {
                "category": "验收风险",
                "severity": "中",
                "description": "性能指标'响应时间<3秒，并发用户>100'缺乏具体测试场景和测试方法定义，'连续运行30天无重大故障'中'重大故障'未定义",
                "location": "第五条 验收标准",
                "suggestion": "明确性能测试的具体操作场景和测试环境；定义'重大故障'的判定标准；约定验收测试方法和工具"
            }
        ],
        "compliance_check": [
            {"item": "合同主体信息完整性", "status": "通过", "details": "双方名称、地址、联系人信息完整"},
            {"item": "服务内容明确性", "status": "不通过", "details": "服务内容仅有概括性描述，缺少详细的功能清单"},
            {"item": "费用及付款条款", "status": "通过", "details": "费用金额明确，付款比例和节点有约定"},
            {"item": "知识产权条款", "status": "不通过", "details": "完全缺失知识产权相关约定"},
            {"item": "保密条款", "status": "不通过", "details": "完全缺失保密义务相关约定"},
            {"item": "争议解决机制", "status": "需关注", "details": "未约定争议解决方式和管辖地"}
        ],
        "recommendations": [
            "建议1：将《需求说明书》作为合同附件一，明确其与合同正文具有同等法律效力",
            "建议2：增加知识产权条款，明确软件著作权归属",
            "建议3：增加保密条款，约定双方对项目信息的保密义务",
            "建议4：增加争议解决条款，建议约定仲裁或诉讼管辖"
        ],
        "missing_clauses": [
            "知识产权归属条款",
            "保密条款",
            "不可抗力条款",
            "争议解决条款",
            "合同变更与终止条款",
            "交付物清单"
        ]
    }
    
    # 生成报告
    generator = HTMLReportGenerator()
    output_path = Path("data/outputs/test_reports/review_report.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = generator.generate_html_report(
        review_result=test_result,
        output_path=output_path,
        contract_name="技术服务合同示例",
        task_id="test-12345678"
    )
    
    print(f"✅ HTML报告已生成: {result}")
    print(f"   文件大小: {result.stat().st_size:,} bytes")
