"""
HTML 报告生成器 v2.0 - 鹰眼风格
Contract Review AI - Eagle Eye Style Professional HTML Report Generator

特点:
1. 紫蓝渐变背景 + 粒子动画效果
2. 毛玻璃效果卡片 (Glassmorphism)
3. 浮动胶囊标签页
4. 现代化统计卡片
5. 动画效果和悬浮交互
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class HTMLReportGeneratorV2:
    """
    鹰眼风格 HTML 报告生成器
    
    采用现代化的 UI 设计，包含粒子背景、毛玻璃效果、动画过渡等
    """
    
    def __init__(self):
        self.risk_colors = {
            "高": {"gradient": "linear-gradient(135deg, #ff4757 0%, #ff3742 100%)", "glow": "rgba(255,71,87,0.4)"},
            "中": {"gradient": "linear-gradient(135deg, #ffa726 0%, #ff7043 100%)", "glow": "rgba(255,167,38,0.4)"},
            "低": {"gradient": "linear-gradient(135deg, #2ed573 0%, #17c0eb 100%)", "glow": "rgba(46,213,115,0.4)"}
        }
    
    def generate_html_report(
        self,
        review_result: Dict[str, Any],
        output_path: Path,
        contract_name: str = "合同",
        task_id: str = ""
    ) -> Path:
        """生成完整的 HTML 报告"""
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
    <!-- 粒子背景 -->
    <div id="particles-js"></div>
    
    <div class="container">
        <!-- 头部 -->
        {self._generate_header(kwargs["contract_name"], kwargs["task_id"], kwargs["risk_level"])}
        
        <!-- 状态栏 -->
        {self._generate_status_bar(kwargs["stats"])}
        
        <!-- 浮动标签页 -->
        <div class="floating-tabs">
            <div class="tab active" onclick="switchTab(event, 'overview')">📊 决策总览</div>
            <div class="tab" onclick="switchTab(event, 'risks')">⚠️ 风险详情 <span class="badge danger">{kwargs["stats"]["high_risk"]}</span></div>
            <div class="tab" onclick="switchTab(event, 'compliance')">✅ 合规检查 <span class="badge warning">{kwargs["stats"]["compliance_fail"]}</span></div>
            <div class="tab" onclick="switchTab(event, 'recommendations')">💡 修改建议 <span class="badge info">{len(kwargs["recommendations"])}</span></div>
            <div class="tab" onclick="switchTab(event, 'missing')">📋 缺失条款 <span class="badge">{kwargs["stats"]["missing_count"]}</span></div>
        </div>
        
        <!-- 内容区域 -->
        <div class="content">
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
    
    <!-- 粒子效果库 -->
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <script>
{self._get_javascript()}
    </script>
</body>
</html>'''

    def _get_css_styles(self):
        """获取 CSS 样式 - 鹰眼风格"""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* 粒子背景 */
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 0;
        }

        /* 主容器 */
        .container {
            position: relative;
            z-index: 1;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        /* 头部 - 毛玻璃效果 */
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 30px 40px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .header-meta {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 0.9em;
            opacity: 0.8;
            flex-wrap: wrap;
        }

        .header-meta span {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* 风险徽章 */
        .risk-main-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 28px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 700;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            animation: pulse-glow 2s infinite;
        }

        .risk-main-badge.high { background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%); }
        .risk-main-badge.medium { background: linear-gradient(135deg, #ffa726 0%, #ff7043 100%); }
        .risk-main-badge.low { background: linear-gradient(135deg, #2ed573 0%, #17c0eb 100%); }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 8px 25px rgba(0,0,0,0.2); }
            50% { box-shadow: 0 8px 40px rgba(0,0,0,0.3); }
        }

        /* 状态栏 */
        .status-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .status-item {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 12px 24px;
            color: white;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.3s ease;
        }

        .status-item:hover {
            transform: translateY(-2px);
            background: rgba(255,255,255,0.15);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .status-dot.success { background: #2ed573; }
        .status-dot.warning { background: #ffa726; }
        .status-dot.danger { background: #ff4757; }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }

        /* 浮动标签页 */
        .floating-tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            gap: 10px;
            flex-wrap: wrap;
        }

        .tab {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 25px;
            padding: 12px 24px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tab:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }

        .tab.active {
            background: rgba(255,255,255,0.3);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border-color: rgba(255,255,255,0.4);
        }

        .badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            font-weight: 600;
            background: rgba(255,255,255,0.2);
        }

        .badge.danger { background: rgba(255,71,87,0.6); }
        .badge.warning { background: rgba(255,167,38,0.6); }
        .badge.info { background: rgba(59,130,246,0.6); }

        /* 内容区域 - 毛玻璃效果 */
        .content {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .tab-content {
            display: none;
            color: white;
            animation: fadeIn 0.4s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .section-title {
            font-size: 1.5em;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        /* 统计卡片网格 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 24px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.15);
            box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }

        .stat-card.highlight {
            background: linear-gradient(135deg, rgba(102,126,234,0.5) 0%, rgba(118,75,162,0.5) 100%);
        }

        .stat-card.danger {
            background: linear-gradient(135deg, rgba(255,71,87,0.4) 0%, rgba(255,55,66,0.4) 100%);
        }

        .stat-number {
            font-size: 2.8em;
            font-weight: 700;
            margin-bottom: 8px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* 评估区域 */
        .assessment-box {
            background: rgba(255,255,255,0.1);
            border-left: 4px solid #3b82f6;
            border-radius: 0 15px 15px 0;
            padding: 24px;
            margin-bottom: 30px;
        }

        .assessment-box h3 {
            margin-bottom: 12px;
            font-size: 1.1em;
        }

        .assessment-box p {
            line-height: 1.8;
            opacity: 0.95;
        }

        /* 风险分布条 */
        .risk-distribution {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .risk-bar {
            display: flex;
            height: 24px;
            border-radius: 12px;
            overflow: hidden;
            margin: 16px 0;
        }

        .risk-bar-segment {
            transition: width 0.5s ease;
        }

        .risk-bar-segment.high { background: linear-gradient(90deg, #ff4757, #ff6b7a); }
        .risk-bar-segment.medium { background: linear-gradient(90deg, #ffa726, #ffb74d); }
        .risk-bar-segment.low { background: linear-gradient(90deg, #2ed573, #7bed9f); }

        .risk-legend {
            display: flex;
            gap: 24px;
            justify-content: center;
            margin-top: 12px;
        }

        .risk-legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
        }

        .risk-legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        /* 风险卡片 */
        .risk-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .risk-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .risk-card-header {
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .risk-card-header.high { 
            background: linear-gradient(135deg, rgba(255,71,87,0.3) 0%, rgba(255,71,87,0.1) 100%);
            border-left: 5px solid #ff4757;
        }
        .risk-card-header.medium { 
            background: linear-gradient(135deg, rgba(255,167,38,0.3) 0%, rgba(255,167,38,0.1) 100%);
            border-left: 5px solid #ffa726;
        }
        .risk-card-header.low { 
            background: linear-gradient(135deg, rgba(46,213,115,0.3) 0%, rgba(46,213,115,0.1) 100%);
            border-left: 5px solid #2ed573;
        }

        .risk-card-title {
            font-weight: 600;
            font-size: 1.1em;
        }

        .risk-level-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            color: white;
        }

        .risk-level-badge.high { background: linear-gradient(135deg, #ff4757, #ff3742); }
        .risk-level-badge.medium { background: linear-gradient(135deg, #ffa726, #ff7043); }
        .risk-level-badge.low { background: linear-gradient(135deg, #2ed573, #17c0eb); }

        .risk-card-body {
            padding: 20px;
        }

        .risk-detail {
            margin-bottom: 16px;
        }

        .risk-detail:last-child {
            margin-bottom: 0;
        }

        .risk-detail-label {
            font-size: 0.8em;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .risk-detail-content {
            line-height: 1.6;
        }

        .location-tag {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }

        /* 合规检查 */
        .compliance-summary {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        .compliance-stat {
            flex: 1;
            min-width: 120px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }

        .compliance-stat.pass { border-left: 4px solid #2ed573; }
        .compliance-stat.fail { border-left: 4px solid #ff4757; }
        .compliance-stat.warn { border-left: 4px solid #ffa726; }

        .compliance-stat-number {
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .compliance-stat.pass .compliance-stat-number { color: #2ed573; }
        .compliance-stat.fail .compliance-stat-number { color: #ff4757; }
        .compliance-stat.warn .compliance-stat-number { color: #ffa726; }

        .compliance-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }

        .compliance-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
        }

        .compliance-item-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .compliance-item-number {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.9em;
        }

        .status-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-badge.pass { background: rgba(46,213,115,0.3); color: #2ed573; }
        .status-badge.fail { background: rgba(255,71,87,0.3); color: #ff4757; }
        .status-badge.warn { background: rgba(255,167,38,0.3); color: #ffa726; }

        /* 建议列表 */
        .recommendation-list {
            list-style: none;
        }

        .recommendation-item {
            display: flex;
            gap: 16px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .recommendation-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .recommendation-number {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        }

        .recommendation-content {
            flex: 1;
            line-height: 1.7;
        }

        /* 缺失条款 */
        .missing-alert {
            background: rgba(255,71,87,0.2);
            border: 1px solid rgba(255,71,87,0.3);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .missing-alert-icon {
            font-size: 1.5em;
        }

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
            background: rgba(255,71,87,0.1);
            border-radius: 12px;
            border-left: 4px solid #ff4757;
            transition: all 0.3s ease;
        }

        .missing-item:hover {
            background: rgba(255,71,87,0.15);
            transform: translateX(5px);
        }

        .missing-icon {
            width: 36px;
            height: 36px;
            background: rgba(255,71,87,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
        }

        /* 页脚 */
        .footer {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 24px;
            text-align: center;
            color: white;
        }

        .footer-disclaimer {
            background: rgba(255,167,38,0.2);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            font-size: 0.9em;
        }

        .footer-meta {
            font-size: 0.8em;
            opacity: 0.7;
        }

        /* 进度条 */
        .progress-container {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 24px;
            margin-bottom: 24px;
        }

        .progress-bar {
            height: 12px;
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            overflow: hidden;
            margin: 16px 0;
        }

        .progress-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 0.8s ease;
        }

        .progress-fill.success { background: linear-gradient(90deg, #2ed573, #7bed9f); }
        .progress-fill.warning { background: linear-gradient(90deg, #ffa726, #ffb74d); }
        .progress-fill.danger { background: linear-gradient(90deg, #ff4757, #ff6b7a); }

        /* 打印样式 */
        @media print {
            body {
                background: white;
            }
            
            #particles-js {
                display: none;
            }
            
            .container {
                padding: 0;
            }
            
            .header, .content, .footer {
                background: white;
                backdrop-filter: none;
                border: 1px solid #ddd;
                color: #333;
            }
            
            .floating-tabs {
                display: none;
            }
            
            .tab-content {
                display: block !important;
                color: #333;
                page-break-after: always;
            }
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 1.6em;
            }
            
            .floating-tabs {
                flex-direction: column;
                align-items: center;
            }
            
            .tab {
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .header-meta {
                flex-direction: column;
                gap: 8px;
            }
        }
'''

    def _get_javascript(self):
        """获取 JavaScript 代码"""
        return '''
        // 初始化粒子背景
        if (typeof particlesJS !== 'undefined') {
            particlesJS('particles-js', {
                particles: {
                    number: { value: 60, density: { enable: true, value_area: 800 } },
                    color: { value: "#ffffff" },
                    shape: { type: "circle" },
                    opacity: { value: 0.3, random: true },
                    size: { value: 3, random: true },
                    line_linked: { enable: true, distance: 150, color: "#ffffff", opacity: 0.2, width: 1 },
                    move: { enable: true, speed: 2, direction: "none", random: false, straight: false, out_mode: "out", bounce: false }
                },
                interactivity: {
                    detect_on: "canvas",
                    events: { onhover: { enable: true, mode: "grab" }, onclick: { enable: true, mode: "push" }, resize: true },
                    modes: { grab: { distance: 140, line_linked: { opacity: 0.5 } }, push: { particles_nb: 3 } }
                },
                retina_detect: true
            });
        }

        // 切换标签页
        function switchTab(evt, tabName) {
            // 隐藏所有页签内容
            var tabContents = document.getElementsByClassName("tab-content");
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove("active");
            }
            
            // 移除所有标签的激活状态
            var tabs = document.getElementsByClassName("tab");
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove("active");
            }
            
            // 显示选中的页签内容
            document.getElementById(tabName).classList.add("active");
            
            // 激活选中的标签
            evt.currentTarget.classList.add("active");
        }

        // 页面加载动画
        document.addEventListener("DOMContentLoaded", function() {
            // 统计卡片动画
            const cards = document.querySelectorAll(".stat-card, .risk-card, .recommendation-item, .compliance-item, .missing-item");
            cards.forEach((card, index) => {
                card.style.opacity = "0";
                card.style.transform = "translateY(20px)";
                setTimeout(() => {
                    card.style.transition = "all 0.5s ease";
                    card.style.opacity = "1";
                    card.style.transform = "translateY(0)";
                }, index * 80);
            });
            
            // 数字计数动画
            const statNumbers = document.querySelectorAll(".stat-number[data-value]");
            statNumbers.forEach(num => {
                const target = parseInt(num.getAttribute("data-value"));
                let current = 0;
                const increment = target / 30;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        num.textContent = target;
                        clearInterval(timer);
                    } else {
                        num.textContent = Math.floor(current);
                    }
                }, 30);
            });
        });
'''

    def _generate_header(self, contract_name, task_id, risk_level):
        """生成头部"""
        risk_class = {"高": "high", "中": "medium", "低": "low"}.get(risk_level, "medium")
        risk_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(risk_level, "⚪")
        
        return f'''
        <div class="header">
            <h1>📄 合同智能评审报告</h1>
            <div class="subtitle">{contract_name}</div>
            <div style="margin: 20px 0;">
                <span class="risk-main-badge {risk_class}">
                    {risk_emoji} 整体风险等级：{risk_level}
                </span>
            </div>
            <div class="header-meta">
                <span>📅 {datetime.now().strftime("%Y年%m月%d日 %H:%M")}</span>
                <span>🔖 任务ID: {task_id[:8] if task_id else "N/A"}...</span>
                <span>🤖 AI智能评审引擎</span>
            </div>
        </div>
        '''

    def _generate_status_bar(self, stats):
        """生成状态栏"""
        return f'''
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot {"danger" if stats["high_risk"] > 0 else "success"}"></div>
                <span>高风险: {stats["high_risk"]}项</span>
            </div>
            <div class="status-item">
                <div class="status-dot {"warning" if stats["compliance_fail"] > 0 else "success"}"></div>
                <span>合规问题: {stats["compliance_fail"]}项</span>
            </div>
            <div class="status-item">
                <div class="status-dot {"warning" if stats["missing_count"] > 0 else "success"}"></div>
                <span>缺失条款: {stats["missing_count"]}项</span>
            </div>
            <div class="status-item">
                <div class="status-dot success"></div>
                <span>评审完成</span>
            </div>
        </div>
        '''

    def _generate_overview_tab(self, overall, risk_level, stats, findings):
        """生成决策总览页签"""
        # 计算合规通过率
        total = stats["total_compliance"]
        pass_rate = round(stats["compliance_pass"] / total * 100) if total > 0 else 0
        
        # 风险分布
        total_risks = stats["total_findings"] or 1
        high_pct = round(stats["high_risk"] / total_risks * 100)
        medium_pct = round(stats["medium_risk"] / total_risks * 100)
        low_pct = 100 - high_pct - medium_pct
        
        # 高风险摘要
        high_risk_items = [f for f in findings if f.get("severity") == "高"][:3]
        high_risk_html = ""
        if high_risk_items:
            high_risk_html = '<div style="margin-top: 24px;"><h4 style="margin-bottom: 12px;">⚠️ 需要重点关注</h4>'
            for item in high_risk_items:
                high_risk_html += f'''
                <div style="background: rgba(255,71,87,0.15); padding: 14px; border-radius: 10px; margin-bottom: 10px; border-left: 3px solid #ff4757;">
                    <strong>{item.get("category", "")}</strong>: {item.get("description", "")[:120]}...
                </div>'''
            high_risk_html += '</div>'
        
        return f'''
        <h2 class="section-title">📊 决策总览</h2>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card {"danger" if risk_level == "高" else "highlight"}">
                <div class="stat-number">{risk_level}</div>
                <div class="stat-label">整体风险等级</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #ff4757;">{stats["high_risk"]}</div>
                <div class="stat-label">高风险项</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #ffa726;">{stats["compliance_fail"]}</div>
                <div class="stat-label">合规问题</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #3b82f6;">{stats["missing_count"]}</div>
                <div class="stat-label">缺失条款</div>
            </div>
        </div>
        
        <!-- 整体评估 -->
        <div class="assessment-box">
            <h3>📝 整体评估</h3>
            <p>{overall}</p>
        </div>
        
        <!-- 风险分布 -->
        <div class="risk-distribution">
            <h4>风险分布</h4>
            <div class="risk-bar">
                <div class="risk-bar-segment high" style="width: {high_pct}%;"></div>
                <div class="risk-bar-segment medium" style="width: {medium_pct}%;"></div>
                <div class="risk-bar-segment low" style="width: {low_pct}%;"></div>
            </div>
            <div class="risk-legend">
                <div class="risk-legend-item">
                    <div class="risk-legend-dot" style="background: #ff4757;"></div>
                    <span>高风险 {stats["high_risk"]}</span>
                </div>
                <div class="risk-legend-item">
                    <div class="risk-legend-dot" style="background: #ffa726;"></div>
                    <span>中风险 {stats["medium_risk"]}</span>
                </div>
                <div class="risk-legend-item">
                    <div class="risk-legend-dot" style="background: #2ed573;"></div>
                    <span>低风险 {stats["low_risk"]}</span>
                </div>
            </div>
        </div>
        
        <!-- 合规通过率 -->
        <div class="progress-container">
            <h4>合规检查通过率</h4>
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 3em; font-weight: 700; color: {"#2ed573" if pass_rate >= 70 else "#ffa726" if pass_rate >= 50 else "#ff4757"};">
                    {pass_rate}%
                </div>
                <div style="flex: 1;">
                    <div class="progress-bar">
                        <div class="progress-fill {"success" if pass_rate >= 70 else "warning" if pass_rate >= 50 else "danger"}" 
                             style="width: {pass_rate}%;"></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9em; opacity: 0.8;">
                        {stats["compliance_pass"]} 通过 / {stats["compliance_fail"]} 不通过 / {stats["compliance_warn"]} 需关注
                    </div>
                </div>
            </div>
        </div>
        
        {high_risk_html}
        '''

    def _generate_risks_tab(self, findings):
        """生成风险详情页签"""
        if not findings:
            return '''
            <h2 class="section-title">⚠️ 风险详情</h2>
            <div style="text-align: center; padding: 60px; opacity: 0.7;">
                ✅ 未发现显著风险
            </div>
            '''
        
        cards_html = ""
        for i, finding in enumerate(findings, 1):
            severity = finding.get("severity", "未知")
            severity_class = {"高": "high", "中": "medium", "低": "low"}.get(severity, "medium")
            
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
                        <div class="risk-detail-content" style="color: #7bed9f;">{finding.get("suggestion", "")}</div>
                    </div>
                </div>
            </div>
            '''
        
        return f'''
        <h2 class="section-title">⚠️ 风险详情分析</h2>
        <p style="opacity: 0.8; margin-bottom: 24px;">共发现 <strong>{len(findings)}</strong> 个风险点，请按优先级依次处理。</p>
        {cards_html}
        '''

    def _generate_compliance_tab(self, compliance, stats):
        """生成合规检查页签"""
        if not compliance:
            return '''
            <h2 class="section-title">✅ 合规检查</h2>
            <div style="text-align: center; padding: 60px; opacity: 0.7;">
                暂无合规检查数据
            </div>
            '''
        
        items_html = ""
        for i, check in enumerate(compliance, 1):
            status = check.get("status", "未知")
            status_class = {"通过": "pass", "不通过": "fail", "需关注": "warn"}.get(status, "warn")
            icon = {"通过": "✓", "不通过": "✗", "需关注": "!"}.get(status, "?")
            
            items_html += f'''
            <div class="compliance-item">
                <div class="compliance-item-left">
                    <div class="compliance-item-number">{i}</div>
                    <div>
                        <div style="font-weight: 500; margin-bottom: 4px;">{check.get("item", "")}</div>
                        <div style="font-size: 0.85em; opacity: 0.7;">{check.get("details", "")}</div>
                    </div>
                </div>
                <span class="status-badge {status_class}">
                    <span>{icon}</span> {status}
                </span>
            </div>
            '''
        
        return f'''
        <h2 class="section-title">✅ 合规检查结果</h2>
        
        <div class="compliance-summary">
            <div class="compliance-stat pass">
                <div class="compliance-stat-number">{stats["compliance_pass"]}</div>
                <div>通过</div>
            </div>
            <div class="compliance-stat fail">
                <div class="compliance-stat-number">{stats["compliance_fail"]}</div>
                <div>不通过</div>
            </div>
            <div class="compliance-stat warn">
                <div class="compliance-stat-number">{stats["compliance_warn"]}</div>
                <div>需关注</div>
            </div>
        </div>
        
        {items_html}
        '''

    def _generate_recommendations_tab(self, recommendations):
        """生成修改建议页签"""
        if not recommendations:
            return '''
            <h2 class="section-title">💡 修改建议</h2>
            <div style="text-align: center; padding: 60px; opacity: 0.7;">
                暂无修改建议
            </div>
            '''
        
        items_html = ""
        for i, rec in enumerate(recommendations, 1):
            items_html += f'''
            <li class="recommendation-item">
                <div class="recommendation-number">{i}</div>
                <div class="recommendation-content">{rec}</div>
            </li>
            '''
        
        return f'''
        <h2 class="section-title">💡 修改建议</h2>
        <p style="opacity: 0.8; margin-bottom: 24px;">
            以下是基于评审结果提出的 <strong>{len(recommendations)}</strong> 条改进建议，建议按顺序逐一落实。
        </p>
        <ul class="recommendation-list">
            {items_html}
        </ul>
        '''

    def _generate_missing_tab(self, missing_clauses):
        """生成缺失条款页签"""
        if not missing_clauses:
            return '''
            <h2 class="section-title">📋 缺失条款</h2>
            <div style="text-align: center; padding: 60px; opacity: 0.7;">
                ✅ 合同条款完整
            </div>
            '''
        
        items_html = ""
        for clause in missing_clauses:
            items_html += f'''
            <div class="missing-item">
                <div class="missing-icon">⚠</div>
                <div>{clause}</div>
            </div>
            '''
        
        return f'''
        <h2 class="section-title">📋 缺失条款清单</h2>
        
        <div class="missing-alert">
            <div class="missing-alert-icon">⚠️</div>
            <div>发现 <strong>{len(missing_clauses)}</strong> 项重要条款缺失，建议在签署前补充完善。</div>
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
                Contract Review AI v2.0 (Eagle Eye Style) | 
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
            },
            {
                "category": "支付风险",
                "severity": "中",
                "description": "付款节点与交付里程碑不够细化，可能导致款项支付与实际进度脱节",
                "location": "第三条 费用与付款",
                "suggestion": "建议细化付款节点，与项目里程碑挂钩，如：签约30%、需求确认20%、开发完成30%、验收通过20%"
            },
            {
                "category": "保密风险",
                "severity": "低",
                "description": "保密条款较为简单，未明确保密期限和违约责任",
                "location": "第八条 保密条款",
                "suggestion": "建议补充保密期限（如合同终止后3年）、违反保密义务的赔偿责任"
            }
        ],
        "compliance_check": [
            {"item": "合同主体信息完整性", "status": "通过", "details": "双方名称、地址、联系人信息完整"},
            {"item": "服务内容明确性", "status": "不通过", "details": "服务内容仅有概括性描述，缺少详细的功能清单"},
            {"item": "费用及付款条款", "status": "通过", "details": "费用金额明确，付款比例和节点有约定"},
            {"item": "知识产权条款", "status": "不通过", "details": "完全缺失知识产权相关约定"},
            {"item": "保密条款", "status": "需关注", "details": "有保密条款但不够完善"},
            {"item": "违约责任条款", "status": "通过", "details": "违约责任条款完整"},
            {"item": "争议解决机制", "status": "需关注", "details": "未约定争议解决方式和管辖地"},
            {"item": "不可抗力条款", "status": "不通过", "details": "完全缺失不可抗力相关约定"},
            {"item": "合同变更条款", "status": "需关注", "details": "变更条款较为简单"}
        ],
        "recommendations": [
            "建议1：将《需求说明书》作为合同附件一，明确其与合同正文具有同等法律效力",
            "建议2：增加知识产权条款，明确软件著作权归属、源代码交付时间和方式",
            "建议3：增加不可抗力条款，约定不可抗力事件的定义、通知义务和责任免除",
            "建议4：完善保密条款，明确保密期限、保密范围和违约责任",
            "建议5：增加争议解决条款，建议约定仲裁或诉讼管辖地",
            "建议6：细化付款节点，与项目里程碑挂钩，降低付款风险"
        ],
        "missing_clauses": [
            "知识产权归属条款",
            "不可抗力条款",
            "争议解决条款（管辖地）",
            "合同变更与终止条款",
            "交付物清单（技术附件）",
            "第三方组件授权清单",
            "数据安全条款",
            "售后维保条款"
        ]
    }
    
    # 生成报告
    generator = HTMLReportGeneratorV2()
    output_path = Path("data/outputs/test_reports/review_report_v2.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = generator.generate_html_report(
        review_result=test_result,
        output_path=output_path,
        contract_name="技术服务合同示例",
        task_id="test-12345678"
    )
    
    print(f"✅ 鹰眼风格HTML报告已生成: {result}")
    print(f"   文件大小: {result.stat().st_size:,} bytes")
