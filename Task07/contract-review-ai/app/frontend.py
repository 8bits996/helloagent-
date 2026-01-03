"""
Streamlit 前端界面
Contract Review AI - Frontend
v3.1 - 性能优化版本
- 添加 @st.cache_data 缓存装饰器
- 优化报告下载逻辑（延迟加载）
- 减少不必要的 API 调用
- CSS 缓存优化
"""

import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import json
from pathlib import Path
from datetime import datetime
from functools import lru_cache
import threading
import hashlib

# ========== 页面配置 ==========
st.set_page_config(
    page_title="合同评审AI系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 配置 ==========
API_URL = "http://localhost:8000"

# ========== HTTP 会话配置（带重试机制）==========
def create_session_with_retry():
    """创建带重试机制的 HTTP 会话"""
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,                    # 最大重试次数
        backoff_factor=0.5,         # 重试间隔系数
        status_forcelist=[500, 502, 503, 504],  # 需要重试的状态码
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],  # 允许重试的方法
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,        # 连接池大小
        pool_maxsize=10,            # 最大连接数
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# 全局 HTTP 会话（复用连接）
if 'http_session' not in st.session_state:
    st.session_state.http_session = create_session_with_retry()

def get_session():
    """获取 HTTP 会话"""
    if 'http_session' not in st.session_state:
        st.session_state.http_session = create_session_with_retry()
    return st.session_state.http_session

# ========== API 健康状态缓存 ==========
if 'api_health_cache' not in st.session_state:
    st.session_state.api_health_cache = {
        'status': None,
        'data': None,
        'last_check': 0,
        'cache_duration': 30  # 缓存 30 秒（从10秒增加到30秒）
    }

# ========== 数据缓存 ==========
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {
        'knowledge_base': {'data': None, 'time': 0, 'ttl': 60},  # 60秒缓存
        'history_stats': {'data': None, 'time': 0, 'ttl': 30},   # 30秒缓存
        'task_history': {'data': None, 'time': 0, 'ttl': 15},    # 15秒缓存
        'report_list': {},  # 报告列表缓存，key为task_id
    }

def get_cached_data(cache_key, fetch_func, ttl=30, force_refresh=False):
    """通用缓存获取函数"""
    cache = st.session_state.data_cache.get(cache_key, {})
    current_time = time.time()
    
    if not force_refresh and cache.get('data') is not None:
        if current_time - cache.get('time', 0) < cache.get('ttl', ttl):
            return cache['data']
    
    # 调用获取函数
    result = fetch_func()
    
    # 更新缓存
    st.session_state.data_cache[cache_key] = {
        'data': result,
        'time': current_time,
        'ttl': ttl
    }
    
    return result

# ========== 自定义CSS（使用缓存避免重复注入）==========
@st.cache_data
def get_custom_css():
    """获取自定义CSS样式（缓存）"""
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .risk-high {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }
        .risk-medium {
            background-color: #fff8e1;
            border-left: 4px solid #ff9800;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }
        .risk-low {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #666;
        }
        .download-btn {
            margin: 0.25rem;
        }
        .compliance-pass { color: #4caf50; font-weight: bold; }
        .compliance-fail { color: #f44336; font-weight: bold; }
        .compliance-warn { color: #ff9800; font-weight: bold; }
        /* 性能优化：减少重绘 */
        .stButton > button {
            transition: none !important;
        }
    </style>
    """

# 注入CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ========== 工具函数 ==========

def check_api_health(force_refresh=False):
    """检查API服务状态（带缓存）"""
    cache = st.session_state.api_health_cache
    current_time = time.time()
    
    # 检查缓存是否有效
    if not force_refresh and cache['status'] is not None:
        if current_time - cache['last_check'] < cache['cache_duration']:
            return cache['status'], cache['data']
    
    # 执行健康检查
    try:
        session = get_session()
        response = session.get(f"{API_URL}/health", timeout=5)
        result = (response.status_code == 200, response.json())
        
        # 更新缓存
        cache['status'] = result[0]
        cache['data'] = result[1]
        cache['last_check'] = current_time
        
        return result
    except requests.exceptions.ConnectionError as e:
        # 连接错误，返回缓存的错误信息
        cache['status'] = False
        cache['data'] = {"error": f"无法连接到后端服务: {str(e)}"}
        cache['last_check'] = current_time
        return False, cache['data']
    except Exception as e:
        cache['status'] = False
        cache['data'] = {"error": str(e)}
        cache['last_check'] = current_time
        return False, cache['data']

def upload_files(files):
    """上传文件到API（带重试）"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            files_data = [
                ("files", (file.name, file.getvalue(), file.type))
                for file in files
            ]
            
            session = get_session()
            response = session.post(
                f"{API_URL}/api/upload",
                files=files_data,
                timeout=120  # 增加超时时间
            )
            
            response.raise_for_status()
            return True, response.json()
        
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待 1 秒后重试
                continue
            return False, {"error": f"无法连接到后端服务，请检查服务是否运行: {str(e)}"}
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return False, {"error": f"上传超时，请稍后重试: {str(e)}"}
        except Exception as e:
            return False, {"error": str(e)}
    
    return False, {"error": "上传失败，已达最大重试次数"}

def get_task_status(task_id):
    """获取任务状态（带重试）"""
    try:
        session = get_session()
        response = session.get(f"{API_URL}/api/status/{task_id}", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败，请检查服务状态"}
    except Exception as e:
        return False, {"error": str(e)}

def start_review(task_id):
    """启动评审任务（带重试）"""
    try:
        session = get_session()
        response = session.post(f"{API_URL}/api/review/{task_id}", timeout=30)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败，请检查服务状态"}
    except Exception as e:
        return False, {"error": str(e)}

def download_report(task_id, report_type):
    """下载报告（带重试）"""
    try:
        session = get_session()
        response = session.get(
            f"{API_URL}/api/report/{task_id}/{report_type}",
            timeout=60
        )
        response.raise_for_status()
        return True, response.content
    except requests.exceptions.ConnectionError:
        return False, "后端服务连接失败"
    except Exception as e:
        return False, str(e)

def get_report_list(task_id):
    """获取可用报告列表（带重试）"""
    try:
        session = get_session()
        response = session.get(f"{API_URL}/api/report/{task_id}/list", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def get_risk_color(level):
    """获取风险等级颜色"""
    colors = {
        "高": "#f44336",
        "中": "#ff9800", 
        "低": "#4caf50"
    }
    return colors.get(level, "#9e9e9e")

def get_risk_icon(level):
    """获取风险等级图标"""
    icons = {
        "高": "🔴",
        "中": "🟡",
        "低": "🟢"
    }
    return icons.get(level, "⚪")

def get_status_icon(status):
    """获取合规状态图标"""
    icons = {
        "通过": "✅",
        "不通过": "❌",
        "需关注": "⚠️"
    }
    return icons.get(status, "❓")


# ========== 知识库和历史API函数 ==========

def get_knowledge_base_list():
    """获取知识库文件列表（带重试和缓存）"""
    try:
        session = get_session()
        response = session.get(f"{API_URL}/api/knowledge-base/list", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def get_knowledge_base_list_cached(force_refresh=False):
    """获取知识库文件列表（带缓存）"""
    cache = st.session_state.data_cache.get('knowledge_base', {})
    current_time = time.time()
    
    if not force_refresh and cache.get('data') is not None:
        if current_time - cache.get('time', 0) < cache.get('ttl', 60):
            return cache['data']
    
    result = get_knowledge_base_list()
    st.session_state.data_cache['knowledge_base'] = {
        'data': result,
        'time': current_time,
        'ttl': 60
    }
    return result

def upload_knowledge_base(file, description="", category="custom"):
    """上传知识库文件（带重试）"""
    try:
        session = get_session()
        files = {"file": (file.name, file.getvalue(), file.type)}
        params = {"description": description, "category": category}
        
        response = session.post(
            f"{API_URL}/api/knowledge-base/upload",
            files=files,
            params=params,
            timeout=60
        )
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def delete_knowledge_base(filename):
    """删除知识库文件（带重试）"""
    try:
        session = get_session()
        response = session.delete(f"{API_URL}/api/knowledge-base/{filename}", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def preview_knowledge_base(filename, rows=10):
    """预览知识库文件（带重试）"""
    try:
        session = get_session()
        response = session.get(
            f"{API_URL}/api/knowledge-base/{filename}/preview",
            params={"rows": rows},
            timeout=10
        )
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def get_task_history_list(limit=50, offset=0, status=None):
    """获取任务历史列表（带重试）"""
    try:
        session = get_session()
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        
        response = session.get(f"{API_URL}/api/history/list", params=params, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def get_history_statistics():
    """获取任务统计（带重试）"""
    try:
        session = get_session()
        response = session.get(f"{API_URL}/api/history/statistics", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def get_history_statistics_cached(force_refresh=False):
    """获取任务统计（带缓存）"""
    cache = st.session_state.data_cache.get('history_stats', {})
    current_time = time.time()
    
    if not force_refresh and cache.get('data') is not None:
        if current_time - cache.get('time', 0) < cache.get('ttl', 30):
            return cache['data']
    
    result = get_history_statistics()
    st.session_state.data_cache['history_stats'] = {
        'data': result,
        'time': current_time,
        'ttl': 30
    }
    return result

def delete_task_history(task_id):
    """删除任务历史（带重试）"""
    try:
        session = get_session()
        response = session.delete(f"{API_URL}/api/history/{task_id}", timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

def search_task_history(keyword, limit=20):
    """搜索任务历史（带重试）"""
    try:
        session = get_session()
        response = session.get(
            f"{API_URL}/api/history/search",
            params={"keyword": keyword, "limit": limit},
            timeout=10
        )
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "后端服务连接失败"}
    except Exception as e:
        return False, {"error": str(e)}

# ========== 评审结果展示组件 ==========

def render_review_summary(result):
    """渲染评审结果摘要"""
    st.markdown("### 📊 评审结果概览")
    
    # 整体评估
    overall = result.get("overall_assessment", "")
    risk_level = result.get("risk_level", "未知")
    
    # 顶部统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {get_risk_color(risk_level)};">
                {get_risk_icon(risk_level)} {risk_level}
            </div>
            <div class="metric-label">整体风险等级</div>
        </div>
        """, unsafe_allow_html=True)
    
    findings = result.get("key_findings", [])
    with col2:
        high_count = sum(1 for f in findings if f.get("severity") == "高")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #f44336;">{high_count}</div>
            <div class="metric-label">高风险项</div>
        </div>
        """, unsafe_allow_html=True)
    
    compliance = result.get("compliance_check", [])
    with col3:
        fail_count = sum(1 for c in compliance if c.get("status") == "不通过")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ff9800;">{fail_count}</div>
            <div class="metric-label">合规问题</div>
        </div>
        """, unsafe_allow_html=True)
    
    missing = result.get("missing_clauses", [])
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #2196f3;">{len(missing)}</div>
            <div class="metric-label">缺失条款</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 整体评估文字
    st.markdown("---")
    st.markdown("#### 📝 整体评估")
    st.info(overall)

def render_risk_findings(result):
    """渲染风险发现"""
    st.markdown("### ⚠️ 关键风险发现")
    
    findings = result.get("key_findings", [])
    
    if not findings:
        st.success("未发现显著风险")
        return
    
    # 按风险等级分组显示
    for finding in findings:
        severity = finding.get("severity", "未知")
        category = finding.get("category", "未分类")
        description = finding.get("description", "")
        location = finding.get("location", "")
        suggestion = finding.get("suggestion", "")
        
        # 根据风险等级选择样式
        if severity == "高":
            css_class = "risk-high"
        elif severity == "中":
            css_class = "risk-medium"
        else:
            css_class = "risk-low"
        
        st.markdown(f"""
        <div class="{css_class}">
            <strong>{get_risk_icon(severity)} {category}</strong> - 风险等级: {severity}<br>
            <small>📍 位置: {location}</small><br><br>
            <strong>问题描述:</strong><br>
            {description}<br><br>
            <strong>改进建议:</strong><br>
            {suggestion}
        </div>
        """, unsafe_allow_html=True)

def render_compliance_check(result):
    """渲染合规检查结果"""
    st.markdown("### ✅ 合规检查结果")
    
    compliance = result.get("compliance_check", [])
    
    if not compliance:
        st.info("无合规检查数据")
        return
    
    # 统计
    pass_count = sum(1 for c in compliance if c.get("status") == "通过")
    fail_count = sum(1 for c in compliance if c.get("status") == "不通过")
    warn_count = sum(1 for c in compliance if c.get("status") == "需关注")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ 通过", pass_count)
    col2.metric("❌ 不通过", fail_count)
    col3.metric("⚠️ 需关注", warn_count)
    
    st.markdown("---")
    
    # 详细列表
    for check in compliance:
        item = check.get("item", "")
        status = check.get("status", "")
        details = check.get("details", "")
        
        icon = get_status_icon(status)
        
        if status == "通过":
            st.success(f"{icon} **{item}**: {details}")
        elif status == "不通过":
            st.error(f"{icon} **{item}**: {details}")
        else:
            st.warning(f"{icon} **{item}**: {details}")

def render_recommendations(result):
    """渲染修改建议"""
    st.markdown("### 💡 修改建议")
    
    recommendations = result.get("recommendations", [])
    
    if not recommendations:
        st.info("暂无修改建议")
        return
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")

def render_missing_clauses(result):
    """渲染缺失条款"""
    st.markdown("### 📋 缺失条款")
    
    missing = result.get("missing_clauses", [])
    
    if not missing:
        st.success("合同条款完整")
        return
    
    st.warning(f"发现 {len(missing)} 项缺失条款，建议补充：")
    
    for i, clause in enumerate(missing, 1):
        st.markdown(f"{i}. {clause}")

def render_download_buttons(task_id):
    """渲染报告下载按钮组（优化版：延迟加载）"""
    st.markdown("### 📥 下载报告")
    
    # HTML 报告预览按钮（突出显示）
    st.markdown("#### 🌐 专业网页报告")
    col1, col2 = st.columns(2)
    
    with col1:
        # 在新窗口预览 HTML 报告（无需下载）
        preview_url = f"{API_URL}/api/report/{task_id}/html/preview"
        st.markdown(f'''
        <a href="{preview_url}" target="_blank" style="
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        ">🔍 在浏览器中预览报告</a>
        ''', unsafe_allow_html=True)
    
    with col2:
        # 使用直接下载链接而非预加载
        download_url = f"{API_URL}/api/report/{task_id}/html"
        st.markdown(f'''
        <a href="{download_url}" download="review_report_{task_id[:8]}.html" style="
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        ">📥 下载HTML报告</a>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 📄 其他格式")
    
    # 使用缓存获取报告列表
    cache_key = f"report_list_{task_id}"
    if cache_key not in st.session_state.data_cache.get('report_list', {}):
        success, report_data = get_report_list(task_id)
        if success:
            st.session_state.data_cache.setdefault('report_list', {})[cache_key] = report_data
        else:
            st.error("无法获取报告列表")
            return
    else:
        report_data = st.session_state.data_cache['report_list'][cache_key]
    
    reports = report_data.get("reports", [])
    
    if not reports:
        st.info("暂无可下载的报告")
        return
    
    # 报告图标映射
    icons = {
        "markdown": "📝",
        "excel": "📊",
        "csv": "📋",
        "json": "🔧",
        "zip": "📦",
        "html": "🌐"
    }
    
    # 过滤掉 html 类型（已在上方单独显示）
    filtered_reports = [r for r in reports if r.get("type") != "html"]
    
    # 优先级排序
    priority_order = ["summary", "excel", "zip", "risk-matrix", "compliance", "result", "markdown"]
    sorted_reports = sorted(
        filtered_reports,
        key=lambda x: priority_order.index(x.get("endpoint", "").split("/")[-1]) 
            if x.get("endpoint", "").split("/")[-1] in priority_order else 99
    )
    
    # 使用直接下载链接（避免预加载所有文件）
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    
    for i, report in enumerate(sorted_reports[:6]):
        col = columns[i % 3]
        
        name = report.get("name", "报告")
        report_type = report.get("type", "")
        endpoint = report.get("endpoint", "").split("/")[-1]
        size = report.get("size", 0)
        filename = report.get("filename", "report")
        
        icon = icons.get(report_type, "📄")
        
        with col:
            # 使用直接下载链接
            download_url = f"{API_URL}/api/report/{task_id}/{endpoint}"
            st.markdown(f'''
            <a href="{download_url}" download="{filename}" style="
                display: inline-block;
                background: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-size: 14px;
                text-align: center;
                width: 100%;
                box-sizing: border-box;
                margin-bottom: 4px;
            ">{icon} {name}</a>
            ''', unsafe_allow_html=True)
            st.caption(f"大小: {format_file_size(size)}")

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("### 📋 功能导航")
    
    page = st.radio(
        "选择功能",
        ["📤 上传评审", "📊 任务状态", "🤖 Agent团队", "📈 评审结果", "📚 知识库管理", "📜 任务历史", "⚙️ 系统设置"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 系统状态（使用缓存，避免每次刷新都检查）
    st.markdown("### 🔍 系统状态")
    
    # 使用缓存的健康检查结果
    api_ok, health_data = check_api_health()
    
    if api_ok:
        st.success("✅ API服务正常")
        
        services = health_data.get("services", {})
        
        if services.get("fastapi") == "ok":
            st.caption("✅ FastAPI")
        
        if services.get("codebuddy") == "ok":
            st.caption("✅ CodeBuddy")
        else:
            st.caption("⚠️ CodeBuddy (CLI模式)")
        
        if services.get("markitdown") == "ok":
            st.caption("✅ MarkItDown")
    else:
        st.error("❌ API服务不可用")
        error_msg = health_data.get('error', '未知') if isinstance(health_data, dict) else str(health_data)
        # 截断过长的错误信息
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        st.caption(f"错误: {error_msg}")
        
        # 添加重试按钮
        if st.button("🔄 重新检查", key="retry_health_check"):
            # 强制刷新健康检查
            check_api_health(force_refresh=True)
            st.rerun()
    
    st.markdown("---")
    
    # 当前任务
    if 'current_task_id' in st.session_state and st.session_state.current_task_id:
        st.markdown("### 📌 当前任务")
        st.code(st.session_state.current_task_id[:8] + "...")
        
        if st.button("🗑️ 清除任务", use_container_width=True):
            st.session_state.current_task_id = None
            st.rerun()
    
    st.markdown("---")
    
    # 系统信息
    st.markdown("### ℹ️ 系统信息")
    st.caption(f"**版本**: v2.0.0")
    st.caption(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 支持的格式
    with st.expander("📁 支持的文件格式"):
        st.markdown("""
        - PDF (.pdf)
        - Word (.docx, .doc)
        - Excel (.xlsx, .xls)
        - PowerPoint (.pptx)
        - 图片 (.jpg, .png)
        - HTML, CSV, JSON, XML
        - ZIP (.zip)
        """)

# ========== 主页面 ==========

# 页面1: 上传评审
if page == "📤 上传评审":
    st.markdown('<div class="main-header">📄 合同评审AI系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">基于 CodeBuddy + MarkItDown + ContractCopilot 知识库</div>', unsafe_allow_html=True)
    
    # 文件上传区域
    st.markdown("### 1️⃣ 上传合同文件")
    
    uploaded_files = st.file_uploader(
        "支持多个文件同时上传",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 
              'jpg', 'jpeg', 'png', 'gif', 'html', 'htm', 'csv', 
              'json', 'xml', 'zip'],
        help="支持PDF、Word、Excel、PowerPoint、图片等多种格式"
    )
    
    if uploaded_files:
        st.success(f"✅ 已选择 {len(uploaded_files)} 个文件")
        
        # 显示文件列表
        st.markdown("#### 📋 文件列表")
        
        for idx, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{idx}. {file.name}**")
            
            with col2:
                st.caption(f"大小: {format_file_size(file.size)}")
            
            with col3:
                file_ext = file.name.split('.')[-1].upper()
                st.caption(f"类型: {file_ext}")
        
        st.markdown("---")
        
        # 开始评审按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 开始上传并评审", type="primary", use_container_width=True):
                # 上传文件
                with st.spinner("正在上传文件..."):
                    success, result = upload_files(uploaded_files)
                
                if success:
                    task_id = result.get("task_id")
                    st.session_state.current_task_id = task_id
                    
                    st.success("✅ 文件上传成功！")
                    st.info(f"📌 任务ID: `{task_id}`")
                    
                    # 等待文件解析
                    st.markdown("### 2️⃣ 文件解析")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    max_wait = 60
                    wait_count = 0
                    parsing_done = False
                    
                    while wait_count < max_wait:
                        success, status_data = get_task_status(task_id)
                        
                        if success:
                            status = status_data.get("status")
                            progress = status_data.get("progress", 0)
                            message = status_data.get("message", "处理中...")
                            
                            progress_bar.progress(progress / 100)
                            status_text.text(f"状态: {message}")
                            
                            if status == "ready":
                                st.success("✅ 文件解析完成！")
                                parsing_done = True
                                break
                            
                            elif status == "error":
                                st.error(f"❌ 文件解析失败: {message}")
                                break
                        
                        time.sleep(2)
                        wait_count += 2
                    
                    # 自动启动评审
                    if parsing_done:
                        st.markdown("### 3️⃣ 启动AI评审")
                        
                        with st.spinner("正在启动AI评审..."):
                            success, review_result = start_review(task_id)
                        
                        if success:
                            st.success("✅ 评审任务已启动！")
                            st.info("⏳ 评审预计需要1-5分钟，请切换到【📊 任务状态】页面查看进度")
                        else:
                            st.error(f"❌ 启动评审失败: {review_result.get('error')}")
                
                else:
                    st.error(f"❌ 文件上传失败: {result.get('error')}")
    
    else:
        st.info("👆 请先上传合同文件")
        
        # 使用说明
        with st.expander("💡 使用说明", expanded=True):
            st.markdown("""
            ### 快速开始
            
            1. **上传文件**: 点击上方按钮上传合同文件
            2. **自动处理**: 系统自动解析文件并启动AI评审
            3. **查看结果**: 在【📈 评审结果】页面查看详细报告
            
            ### 支持的评审内容
            
            - 📋 **条款完整性检查** - 对照专业Checklist逐项核查
            - ⚠️ **风险量化评估** - 高/中/低三级风险分类
            - ✅ **合规性检查** - SOP流程验证
            - 📊 **综合报告生成** - Markdown/Excel/CSV多格式
            """)

# 页面2: 任务状态
elif page == "📊 任务状态":
    st.markdown("## 📊 任务状态监控")
    
    if 'current_task_id' in st.session_state and st.session_state.current_task_id:
        task_id = st.session_state.current_task_id
        
        st.markdown(f"**任务ID**: `{task_id}`")
        
        # 刷新和自动刷新
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 刷新状态", use_container_width=True):
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("自动刷新", value=False)
        
        st.markdown("---")
        
        # 获取任务状态
        success, status_data = get_task_status(task_id)
        
        if success:
            status = status_data.get("status")
            progress = status_data.get("progress", 0)
            message = status_data.get("message", "")
            
            # 进度条
            st.progress(progress / 100)
            
            # 状态显示
            status_icons = {
                "uploading": ("📤", "info"),
                "parsing": ("🔄", "info"),
                "ready": ("✅", "success"),
                "reviewing": ("🤖", "warning"),
                "generating_report": ("📝", "warning"),
                "completed": ("🎉", "success"),
                "error": ("❌", "error")
            }
            
            icon, msg_type = status_icons.get(status, ("❓", "info"))
            
            if msg_type == "success":
                st.success(f"{icon} {message}")
            elif msg_type == "warning":
                st.warning(f"{icon} {message}")
            elif msg_type == "error":
                st.error(f"{icon} {message}")
            else:
                st.info(f"{icon} {message}")
            
            # 详细信息
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("进度", f"{progress}%")
            
            with col2:
                st.metric("状态", status)
            
            # 如果正在评审，显示提示
            if status == "reviewing":
                st.info("⏳ AI正在分析合同，请耐心等待...")
                
                if auto_refresh:
                    time.sleep(5)
                    st.rerun()
            
            # 如果完成，显示下载按钮
            elif status == "completed":
                st.markdown("---")
                render_download_buttons(task_id)
                
                st.markdown("---")
                st.success("👉 请切换到【📈 评审结果】页面查看详细分析")
            
            # 文件信息
            files = status_data.get("files", [])
            if files:
                st.markdown("---")
                st.markdown("### 📁 上传的文件")
                
                for file_info in files:
                    st.markdown(
                        f"- **{file_info['name']}** "
                        f"({format_file_size(file_info['size'])})"
                    )
        
        else:
            st.error(f"❌ 获取任务状态失败: {status_data.get('error')}")
    
    else:
        st.info("暂无任务，请先在【📤 上传评审】页面上传文件")
        
        # 手动输入任务ID
        st.markdown("---")
        st.markdown("### 🔍 查询历史任务")
        
        manual_task_id = st.text_input("输入任务ID查询")
        
        if manual_task_id and st.button("查询"):
            success, status_data = get_task_status(manual_task_id)
            if success:
                st.session_state.current_task_id = manual_task_id
                st.success("找到任务！")
                st.rerun()
            else:
                st.error("任务不存在")

# 页面: Agent团队
elif page == "🤖 Agent团队":
    st.markdown("## 🤖 Agent 团队工作台")
    
    st.markdown("""
    本系统由4个专业AI Agent协同工作，每个Agent都有明确的角色和职责。
    """)
    
    # 展示Agent卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        ### 🔍 条款分析专家 (ClauseAnalysisAgent)
        **职责**: 分析合同条款，提取关键信息，检查完整性
        **能力**: 基本信息提取、关键条款识别、完整性检查
        **知识库**: 主合同评审checklist
        """)
        
        st.info("""
        ### ✅ 合规检查专员 (ComplianceCheckAgent)
        **职责**: 检查合同合规性
        **能力**: SOP检查、法律合规检查、政策合规检查
        **知识库**: 可交付评审SOP流程说明
        """)
    
    with col2:
        st.warning("""
        ### 🛡️ 风险评估专家 (RiskAssessmentAgent)
        **职责**: 识别并量化评估风险
        **能力**: 风险识别、风险量化、应对建议
        **知识库**: 风险矩阵
        """)
        
        st.success("""
        ### 👨‍⚖️ 首席评审官 (ReportGenerationAgent)
        **职责**: 生成最终评审报告
        **能力**: 结果整合、决策生成、报告撰写
        """)
    
    st.markdown("---")
    
    # 实时监控
    if 'current_task_id' in st.session_state and st.session_state.current_task_id:
        task_id = st.session_state.current_task_id
        st.markdown(f"### 📡 实时监控 (任务ID: `{task_id}`)")
        
        success, status_data = get_task_status(task_id)
        if success:
            status = status_data.get("status")
            
            if status == "reviewing":
                st.info("🔄 Agent团队正在协作评审中...")
                # 模拟进度展示
                progress = status_data.get("progress", 0)
                st.progress(progress / 100)
                
                # 阶段指示器
                cols = st.columns(4)
                stages = ["条款分析", "风险评估", "合规检查", "报告生成"]
                current_stage_idx = int(progress / 25)
                
                for i, stage in enumerate(stages):
                    with cols[i]:
                        if i < current_stage_idx:
                            st.success(f"✅ {stage}")
                        elif i == current_stage_idx:
                            st.warning(f"🔄 {stage}")
                        else:
                            st.caption(f"⏳ {stage}")
                            
                if st.button("🔄 刷新状态", key="refresh_agent_status"):
                    st.rerun()
            
            elif status == "completed":
                st.success("✅ Agent团队已完成评审工作")
                
                # 获取并展示详细结果（如果支持）
                if st.button("查看Agent详细输出"):
                     success, content = download_report(task_id, "result")
                     if success:
                         try:
                             result = json.loads(content)
                             agent_details = result.get("_agent_details", {})
                             if agent_details:
                                 st.markdown("#### Clause Analysis")
                                 st.json(agent_details.get("clause", {}))
                                 st.markdown("#### Risk Assessment")
                                 st.json(agent_details.get("risk", {}))
                                 st.markdown("#### Compliance Check")
                                 st.json(agent_details.get("compliance", {}))
                                 st.markdown("#### Final Report")
                                 st.json(agent_details.get("report", {}))
                             else:
                                 st.info("该任务未包含详细的Agent输出信息")
                         except:
                             st.error("解析结果失败")
            
            else:
                st.info(f"当前状态: {status}")
        else:
            st.error("无法获取任务状态")
    else:
        st.info("暂无活动任务")

# 页面3: 评审结果
elif page == "📈 评审结果":
    st.markdown("## 📈 评审结果分析")
    
    if 'current_task_id' in st.session_state and st.session_state.current_task_id:
        task_id = st.session_state.current_task_id
        
        # 检查任务状态
        success, status_data = get_task_status(task_id)
        
        if success and status_data.get("status") == "completed":
            # 获取评审结果
            success, content = download_report(task_id, "result")
            
            if success:
                try:
                    result = json.loads(content)
                    
                    # 渲染各个部分
                    render_review_summary(result)
                    
                    st.markdown("---")
                    
                    # 使用标签页组织内容
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "⚠️ 风险发现", 
                        "✅ 合规检查", 
                        "💡 修改建议",
                        "📋 缺失条款"
                    ])
                    
                    with tab1:
                        render_risk_findings(result)
                    
                    with tab2:
                        render_compliance_check(result)
                    
                    with tab3:
                        render_recommendations(result)
                    
                    with tab4:
                        render_missing_clauses(result)
                    
                    # 下载报告
                    st.markdown("---")
                    render_download_buttons(task_id)
                    
                except json.JSONDecodeError:
                    st.error("评审结果解析失败")
                    st.text(content.decode())
            
            else:
                st.error("无法获取评审结果")
        
        elif success and status_data.get("status") == "reviewing":
            st.warning("⏳ 评审正在进行中，请稍后再来查看结果")
            
            progress = status_data.get("progress", 0)
            st.progress(progress / 100)
            st.caption(status_data.get("message", ""))
        
        elif success and status_data.get("status") == "error":
            st.error(f"❌ 评审失败: {status_data.get('message')}")
        
        else:
            st.info("任务尚未完成评审")
    
    else:
        st.info("暂无评审结果，请先上传合同进行评审")

# 页面4: 知识库管理
elif page == "📚 知识库管理":
    st.markdown("## 📚 知识库管理")
    st.markdown("管理合同评审所需的知识库文件，包括Checklist、风险矩阵、SOP流程等。")
    
    # 创建标签页
    kb_tab1, kb_tab2 = st.tabs(["📁 文件列表", "📤 上传文件"])
    
    with kb_tab1:
        # 添加刷新按钮
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 刷新", key="refresh_kb"):
                st.session_state.data_cache['knowledge_base'] = {'data': None, 'time': 0, 'ttl': 60}
                st.rerun()
        
        # 获取文件列表（使用缓存）
        success, kb_data = get_knowledge_base_list_cached()
        
        if success:
            files = kb_data.get("files", [])
            
            if files:
                st.markdown(f"### 共 {len(files)} 个知识库文件")
                
                # 按分类分组显示
                categories = {}
                for f in files:
                    cat = f.get("category", "其他")
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(f)
                
                for cat, cat_files in categories.items():
                    with st.expander(f"📂 {cat} ({len(cat_files)} 个文件)", expanded=True):
                        for file_info in cat_files:
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{file_info['filename']}**")
                                if file_info.get('description'):
                                    st.caption(file_info['description'])
                            
                            with col2:
                                st.caption(f"大小: {format_file_size(file_info.get('size', 0))}")
                                st.caption(f"更新: {file_info.get('modified_time', '未知')[:10]}")
                            
                            with col3:
                                # 预览按钮
                                if st.button("👁️ 预览", key=f"preview_btn_{file_info['filename']}"):
                                    success, preview_data = preview_knowledge_base(file_info['filename'])
                                    if success and isinstance(preview_data, dict):
                                        st.session_state[f"preview_{file_info['filename']}"] = preview_data
                                    else:
                                        st.error("预览失败")
                            
                            with col4:
                                # 删除按钮
                                if st.button("🗑️ 删除", key=f"delete_{file_info['filename']}"):
                                    if st.session_state.get(f"confirm_delete_{file_info['filename']}"):
                                        success, _ = delete_knowledge_base(file_info['filename'])
                                        if success:
                                            st.success(f"已删除: {file_info['filename']}")
                                            st.rerun()
                                        else:
                                            st.error("删除失败")
                                    else:
                                        st.session_state[f"confirm_delete_{file_info['filename']}"] = True
                                        st.warning("再次点击确认删除")
                            
                            # 显示预览内容
                            preview_key = f"preview_{file_info['filename']}"
                            if preview_key in st.session_state:
                                preview_data = st.session_state[preview_key]
                                if isinstance(preview_data, dict) and preview_data.get("success"):
                                    st.markdown("**预览内容:**")
                                    
                                    if preview_data.get("format") == "table":
                                        import pandas as pd
                                        columns = preview_data.get("columns", [])
                                        data = preview_data.get("data", [])
                                        if columns and data:
                                            df = pd.DataFrame(data, columns=columns)
                                            st.dataframe(df, use_container_width=True)
                                        else:
                                            st.info("无数据")
                                    else:
                                        st.text(preview_data.get("content", "无内容"))
                                    
                                    if st.button("关闭预览", key=f"close_preview_{file_info['filename']}"):
                                        del st.session_state[preview_key]
                                        st.rerun()
                            
                            st.markdown("---")
            else:
                st.info("暂无知识库文件")
        else:
            st.error(f"获取知识库列表失败: {kb_data.get('error')}")
    
    with kb_tab2:
        st.markdown("### 上传新的知识库文件")
        st.markdown("支持 CSV、Excel (.xlsx/.xls)、JSON 格式")
        
        uploaded_kb_file = st.file_uploader(
            "选择文件",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="上传知识库文件"
        )
        
        if uploaded_kb_file:
            col1, col2 = st.columns(2)
            
            with col1:
                kb_description = st.text_input(
                    "文件描述",
                    placeholder="例如：主合同评审检查清单"
                )
            
            with col2:
                kb_category = st.selectbox(
                    "文件分类",
                    ["checklist", "risk_matrix", "sop", "custom"],
                    format_func=lambda x: {
                        "checklist": "📋 检查清单",
                        "risk_matrix": "⚠️ 风险矩阵",
                        "sop": "📝 SOP流程",
                        "custom": "📁 自定义"
                    }.get(x, x)
                )
            
            if st.button("📤 上传文件", type="primary", use_container_width=True):
                with st.spinner("上传中..."):
                    success, result = upload_knowledge_base(
                        uploaded_kb_file,
                        description=kb_description,
                        category=kb_category
                    )
                
                if success:
                    st.success(f"✅ 上传成功: {uploaded_kb_file.name}")
                    st.rerun()
                else:
                    st.error(f"❌ 上传失败: {result.get('error')}")
        
        # 导入导出
        st.markdown("---")
        st.markdown("### 📦 批量导入/导出")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**导出全部知识库**")
            if st.button("📥 导出为ZIP", use_container_width=True):
                try:
                    response = requests.post(f"{API_URL}/api/knowledge-base/export", timeout=30)
                    if response.status_code == 200:
                        st.download_button(
                            label="下载ZIP",
                            data=response.content,
                            file_name="knowledge_base_export.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error("导出失败")
                except Exception as e:
                    st.error(f"导出失败: {e}")
        
        with col2:
            st.markdown("**从ZIP导入知识库**")
            import_file = st.file_uploader("选择ZIP文件", type=['zip'], key="import_kb")
            if import_file:
                if st.button("📤 导入", use_container_width=True):
                    try:
                        files = {"file": (import_file.name, import_file, "application/zip")}
                        response = requests.post(
                            f"{API_URL}/api/knowledge-base/import",
                            files=files,
                            timeout=60
                        )
                        if response.status_code == 200:
                            st.success("导入成功！")
                            st.rerun()
                        else:
                            st.error("导入失败")
                    except Exception as e:
                        st.error(f"导入失败: {e}")

# 页面5: 任务历史
elif page == "📜 任务历史":
    st.markdown("## 📜 任务历史")
    
    # 统计信息（使用缓存）
    success, stats_data = get_history_statistics_cached()
    
    if success:
        stats = stats_data.get("statistics", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #2196f3;">{stats.get('total', 0)}</div>
                <div class="metric-label">总任务数</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #4caf50;">{stats.get('completed', 0)}</div>
                <div class="metric-label">已完成</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ff9800;">{stats.get('in_progress', 0)}</div>
                <div class="metric-label">进行中</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #f44336;">{stats.get('error', 0)}</div>
                <div class="metric-label">失败</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 搜索和过滤
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_keyword = st.text_input("🔍 搜索任务", placeholder="输入关键词搜索...")
    
    with col2:
        status_filter = st.selectbox(
            "状态过滤",
            [None, "completed", "reviewing", "error"],
            format_func=lambda x: {
                None: "全部",
                "completed": "✅ 已完成",
                "reviewing": "🔄 进行中",
                "error": "❌ 失败"
            }.get(x, x)
        )
    
    with col3:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # 任务列表
    if search_keyword:
        success, history_data = search_task_history(search_keyword)
    else:
        success, history_data = get_task_history_list(limit=50, status=status_filter)
    
    if success:
        tasks = history_data.get("tasks", [])
        
        if tasks:
            st.markdown(f"### 共 {len(tasks)} 个任务")
            
            for task in tasks:
                task_id = task.get("task_id", "")
                status = task.get("status", "unknown")
                created_at = task.get("created_at", "")
                files = task.get("files", [])
                
                # 状态颜色和图标
                status_config = {
                    "completed": ("🎉", "#4caf50", "已完成"),
                    "reviewing": ("🔄", "#ff9800", "评审中"),
                    "error": ("❌", "#f44336", "失败"),
                    "ready": ("✅", "#2196f3", "就绪"),
                    "parsing": ("📝", "#9c27b0", "解析中")
                }
                
                icon, color, status_text = status_config.get(status, ("❓", "#9e9e9e", status))
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{icon} 任务 {task_id[:8]}...**")
                        if files:
                            st.caption(f"📁 {', '.join([f.get('name', '') for f in files[:2]])}")
                    
                    with col2:
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{status_text}</span>', unsafe_allow_html=True)
                    
                    with col3:
                        st.caption(f"创建: {created_at[:16] if created_at else '未知'}")
                    
                    with col4:
                        col4a, col4b = st.columns(2)
                        
                        with col4a:
                            if st.button("📋 查看", key=f"view_{task_id}"):
                                st.session_state.current_task_id = task_id
                                st.success("已切换到该任务，请到【📊 任务状态】查看")
                        
                        with col4b:
                            if st.button("🗑️", key=f"del_{task_id}"):
                                success, _ = delete_task_history(task_id)
                                if success:
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("暂无任务历史")
    else:
        st.error(f"获取任务历史失败: {history_data.get('error')}")
    
    # 清理旧任务
    st.markdown("### 🧹 数据清理")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        cleanup_days = st.slider("清理超过N天的任务", 7, 365, 30)
    
    with col2:
        if st.button("🗑️ 清理", type="secondary", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_URL}/api/history/cleanup",
                    params={"days": cleanup_days},
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"已清理 {result.get('deleted_count', 0)} 个旧任务")
                    st.rerun()
                else:
                    st.error("清理失败")
            except Exception as e:
                st.error(f"清理失败: {e}")

# 页面6: 系统设置
elif page == "⚙️ 系统设置":
    st.markdown("## ⚙️ 系统设置")
    
    # API配置
    st.markdown("### 🔗 连接配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input(
            "API地址",
            value=API_URL,
            help="FastAPI后端服务地址"
        )
    
    with col2:
        st.text_input(
            "CodeBuddy地址",
            value="CLI模式 (本地调用)",
            disabled=True
        )
    
    # 系统信息
    st.markdown("---")
    st.markdown("### 📊 系统信息")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("版本", "v2.0.0")
    
    with col2:
        st.metric("前端", "Streamlit")
    
    with col3:
        st.metric("后端", "FastAPI")
    
    with col4:
        st.metric("AI引擎", "CodeBuddy CLI")
    
    # 技术栈
    st.markdown("---")
    st.markdown("### 🛠️ 技术栈")
    
    st.markdown("""
    | 组件 | 技术 | 说明 |
    |------|------|------|
    | 前端 | Streamlit | Python Web框架 |
    | 后端 | FastAPI | 异步API框架 |
    | 文件解析 | MarkItDown | 微软开源文档转换 |
    | AI引擎 | CodeBuddy CLI | 智能评审引擎 |
    | 知识库 | ContractCopilot | 合同评审知识库 |
    """)
    
    # 关于
    st.markdown("---")
    st.markdown("### 📖 关于")
    
    st.info("""
    **合同评审AI系统** 是 CFP-Study Task07 毕业设计项目。
    
    该系统利用大语言模型对合同进行智能评审，自动识别风险点、
    检查合规性、生成专业报告。
    """)

# ========== 页脚 ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    合同评审AI系统 v3.0.0 | 技术栈: CodeBuddy + MarkItDown + FastAPI + Streamlit<br>
    © 2025 CFP Study - Task07 毕业项目
</div>
""", unsafe_allow_html=True)
