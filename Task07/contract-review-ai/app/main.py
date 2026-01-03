"""
FastAPI 主程序
Contract Review AI - Backend API
v3.2 - OpenAI Compatible & End-to-End
"""

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import List, Optional
import uuid
import os
from pathlib import Path
import logging
from datetime import datetime
import time
from functools import lru_cache

from app.config import settings
from app.services.document_parser import UnifiedDocumentParser
from app.services.codebuddy_client import CodeBuddyClient
from app.services.mock_review_client import MockReviewClient
from app.services.report_generator import ReportGenerator
from app.services.knowledge_base_manager import KnowledgeBaseManager
from app.services.task_history_manager import TaskHistoryManager
from app.services.agent_orchestrator import AgentOrchestrator
from app.agents.llm_provider import LLMProvider

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="合同评审AI系统",
    description="基于Agentic Workflow的智能合同评审系统",
    version="3.2.0"
)

# GZip 压缩中间件（加速传输）
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
parser = UnifiedDocumentParser(
    enable_llm_description=settings.ENABLE_LLM_DESCRIPTION
)
# CodeBuddyClient 仅用于 Knowledge Base 相关操作 (如果需要), 
# 但核心Agent评审现在通过 LLMProvider 直接调用 API
codebuddy_client = CodeBuddyClient(base_url=settings.CODEBUDDY_API_URL)
mock_client = MockReviewClient()
report_generator = ReportGenerator()  # 报告生成器
kb_manager = KnowledgeBaseManager(settings.KB_DIR)  # 知识库管理器
history_manager = TaskHistoryManager(settings.DATA_DIR / "task_history.db")  # 历史管理器

# 初始化Agent编排器
# 使用 OpenAI 兼容模式
llm_provider = LLMProvider(
    api_key=settings.LLM_API_KEY, 
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL,
    use_mock=False # 设置为 True 可强制使用 Mock
)
agent_orchestrator = AgentOrchestrator(llm_provider)

# 任务状态存储（简化版，生产环境应使用数据库）
task_status_db = {}

# 评审模式：'agent' (标准Agent模式), 'mock' (模拟模式)
review_mode = os.getenv("REVIEW_MODE", "agent")

# ========== 缓存配置 ==========
# 健康检查缓存
health_cache = {
    'result': None,
    'timestamp': 0,
    'ttl': 30  # 30秒缓存
}

# 知识库列表缓存
kb_list_cache = {
    'result': None,
    'timestamp': 0,
    'ttl': 60  # 60秒缓存
}


# ========== API路由 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "合同评审AI系统",
        "version": "3.2.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "services": {
            "fastapi": "ok",
            "llm_provider": "configured",
            "markitdown": "ok"
        }
    }


@app.post("/api/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    上传合同文件
    
    支持: PDF, Word, Excel, PowerPoint, 图片, ZIP等
    """
    task_id = str(uuid.uuid4())
    task_dir = settings.UPLOAD_DIR / task_id
    task_dir.mkdir(exist_ok=True)
    
    logger.info(f"新任务 {task_id}: 上传 {len(files)} 个文件")
    
    # 初始化任务状态
    task_status_db[task_id] = {
        "task_id": task_id,
        "status": "uploading",
        "progress": 0,
        "message": "文件上传中...",
        "files": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # 保存文件
    file_paths = []
    for file in files:
        file_path = task_dir / file.filename
        
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            file_paths.append(str(file_path))
            task_status_db[task_id]["files"].append({
                "name": file.filename,
                "size": len(content),
                "path": str(file_path)
            })
            
            logger.info(f"文件已保存: {file.filename} ({len(content)} bytes)")
        
        except Exception as e:
            logger.error(f"保存文件失败: {file.filename}, 错误: {e}")
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    # 更新状态
    update_task_status(task_id, "parsing", 20, "文件上传完成，正在解析...")
    
    # 后台任务：解析文件
    background_tasks.add_task(
        parse_files_task,
        task_id,
        file_paths
    )
    
    return {
        "task_id": task_id,
        "files": [f.filename for f in files],
        "status": "parsing",
        "message": f"已上传{len(files)}个文件，正在解析中..."
    }


async def parse_files_task(task_id: str, file_paths: List[str]):
    """
    后台任务：解析文件为Markdown
    """
    try:
        logger.info(f"任务 {task_id}: 开始解析 {len(file_paths)} 个文件")
        
        # 使用MarkItDown解析
        results = parser.parse_multiple_files(file_paths)
        
        # 检查解析结果
        success_count = sum(1 for r in results.values() if r["success"])
        if success_count == 0:
            update_task_status(task_id, "error", 0, "所有文件解析失败")
            return
        
        # 合并Markdown
        combined_md = parser.combine_markdowns(results)
        
        # 保存Markdown
        output_dir = settings.OUTPUT_DIR / task_id
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / "combined.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_md)
        
        logger.info(f"任务 {task_id}: 文件解析完成，已保存到 {output_path}")
        
        # 更新任务状态
        update_task_status(
            task_id,
            "ready",
            40,
            f"文件解析完成 ({success_count}/{len(file_paths)} 成功)"
        )
    
    except Exception as e:
        logger.error(f"任务 {task_id}: 文件解析失败 - {str(e)}")
        update_task_status(task_id, "error", 0, f"文件解析失败: {str(e)}")


@app.post("/api/review/{task_id}")
async def start_review(
    task_id: str,
    background_tasks: BackgroundTasks
):
    """
    启动评审任务
    """
    # 检查任务是否存在
    if task_id not in task_status_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查Markdown文件是否存在
    md_path = settings.OUTPUT_DIR / task_id / "combined.md"
    
    if not md_path.exists():
        raise HTTPException(status_code=400, detail="文件解析未完成或失败")
    
    logger.info(f"任务 {task_id}: 启动评审")
    
    # 更新状态
    update_task_status(task_id, "reviewing", 50, "正在进行AI评审...")
    
    # 后台任务：AI评审
    background_tasks.add_task(
        review_contract_task,
        task_id,
        str(md_path)
    )
    
    return {
        "task_id": task_id,
        "status": "reviewing",
        "message": "评审任务已启动，预计5-10分钟完成"
    }


async def review_contract_task(task_id: str, markdown_path: str):
    """
    后台任务：AI评审（带重试机制）
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"任务 {task_id}: 开始AI评审 (尝试 {retry_count + 1}/{max_retries + 1})")
            
            # 读取合同Markdown
            with open(markdown_path, "r", encoding="utf-8") as f:
                contract_md = f.read()
            
            # 检查合同内容
            if not contract_md or len(contract_md.strip()) < 100:
                update_task_status(task_id, "error", 0, "合同内容过短或为空")
                return
            
            # 知识库文件（使用所有可用的知识库）
            kb_files = [str(f) for f in settings.KB_DIR.glob("*.csv")]
            logger.info(f"使用 {len(kb_files)} 个知识库文件，合同长度: {len(contract_md)} 字符")
            
            # 调用评审客户端（根据模式选择）
            update_task_status(task_id, "reviewing", 60, "正在调用AI模型进行评审...")
            
            if review_mode == "mock":
                logger.info(f"任务 {task_id}: 使用Mock模式进行评审")
                result = await mock_client.review_contract(
                    contract_markdown=contract_md,
                    knowledge_base_files=kb_files
                )
            else:  # standard agent mode
                logger.info(f"任务 {task_id}: 使用多Agent协作模式进行评审")
                
                # 加载知识库内容
                kb_content = codebuddy_client._load_knowledge_bases(kb_files)
                
                # 执行工作流
                workflow_result = await agent_orchestrator.execute_review_workflow(
                    contract_markdown=contract_md,
                    knowledge_base=kb_content
                )
                
                if workflow_result["success"]:
                    # 适配结果格式，以便兼容报告生成器
                    results = workflow_result.get("results", {})
                    final_report = workflow_result.get("final_report", {})
                    
                    clause_out = results.get("clause", {}).output if hasattr(results.get("clause"), "output") else {}
                    risk_out = results.get("risk", {}).output if hasattr(results.get("risk"), "output") else {}
                    comp_out = results.get("compliance", {}).output if hasattr(results.get("compliance"), "output") else {}
                    
                    # 构造兼容旧格式的 review_result
                    review_result = {
                        "summary": {
                            "decision": final_report.get("decision", "需人工复核"),
                            "confidence": final_report.get("confidence_score", 0.0),
                            "key_findings": final_report.get("executive_summary", ""),
                            "review_time": datetime.now().isoformat()
                        },
                        "checklist_results": clause_out.get("checklist_analysis", []),
                        "risk_assessment": risk_out.get("risks", []),
                        "compliance_check": {
                            "issues": comp_out.get("legal_check", []) + comp_out.get("policy_check", []) if isinstance(comp_out, dict) else []
                        },
                        "recommendations": final_report.get("action_items", []),
                        # 保留原始Agent输出以供前端展示
                        "_agent_details": {
                            "clause": clause_out,
                            "risk": risk_out,
                            "compliance": comp_out,
                            "report": final_report
                        }
                    }
                    
                    result = {
                        "success": True,
                        "review_result": review_result,
                        "usage": {},
                        "model": "multi-agent",
                        "error": None
                    }
                else:
                    result = {
                        "success": False,
                        "error": workflow_result.get("error", "Agent工作流执行失败")
                    }

            
            if not result["success"]:
                error_msg = result.get('error', '未知错误')
                logger.warning(f"任务 {task_id}: 评审返回失败 - {error_msg}")
                
                # 如果是可重试的错误，继续重试
                if retry_count < max_retries and "超时" in str(error_msg):
                    retry_count += 1
                    update_task_status(task_id, "reviewing", 55, f"评审超时，正在重试 ({retry_count}/{max_retries})...")
                    continue
                
                update_task_status(task_id, "error", 0, f"评审失败: {error_msg}")
                return
            
            # 验证评审结果
            review_result = result.get("review_result", {})
            if not review_result or not isinstance(review_result, dict):
                logger.warning(f"任务 {task_id}: 评审结果格式异常")
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                update_task_status(task_id, "error", 0, "评审结果格式异常")
                return
            
            # 保存评审结果
            output_dir = settings.OUTPUT_DIR / task_id
            result_path = output_dir / "review_result.json"
            
            import json
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(review_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"任务 {task_id}: 评审完成，结果已保存到 {result_path}")
            
            # 生成报告
            update_task_status(task_id, "generating_report", 80, "正在生成报告...")
            
            # 获取合同文件名（从任务状态中获取）
            contract_name = "合同"
            if task_id in task_status_db and task_status_db[task_id].get("files"):
                contract_name = task_status_db[task_id]["files"][0].get("name", "合同")
            
            # 调用报告生成器
            try:
                report_files = report_generator.generate_all_reports(
                    task_id=task_id,
                    review_result=review_result,
                    output_dir=output_dir,
                    contract_name=contract_name
                )
                
                # 保存报告文件路径到任务状态
                task_status_db[task_id]["report_files"] = {
                    name: str(path) for name, path in report_files.items()
                }
                
                logger.info(f"任务 {task_id}: 已生成 {len(report_files)} 个报告文件")
            except Exception as e:
                logger.error(f"任务 {task_id}: 报告生成失败 - {str(e)}")
                # 报告生成失败不影响主流程，继续标记为完成
            
            # 更新任务状态
            update_task_status(task_id, "completed", 100, "评审完成")
            return  # 成功完成，退出循环
        
        except FileNotFoundError as e:
            logger.error(f"任务 {task_id}: 文件未找到 - {str(e)}")
            update_task_status(task_id, "error", 0, f"文件未找到: {str(e)}")
            return
        
        except json.JSONDecodeError as e:
            logger.error(f"任务 {task_id}: JSON解析错误 - {str(e)}")
            if retry_count < max_retries:
                retry_count += 1
                continue
            update_task_status(task_id, "error", 0, f"评审结果解析失败")
            return
        
        except Exception as e:
            logger.error(f"任务 {task_id}: 评审异常 - {str(e)}", exc_info=True)
            if retry_count < max_retries:
                retry_count += 1
                update_task_status(task_id, "reviewing", 55, f"发生错误，正在重试 ({retry_count}/{max_retries})...")
                continue
            update_task_status(task_id, "error", 0, f"评审失败: {str(e)}")


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """
    查询任务状态
    """
    if task_id not in task_status_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task_status_db[task_id]


@app.get("/api/report/{task_id}/result")
async def download_result(task_id: str):
    """
    下载评审结果 (JSON)
    """
    file_path = settings.OUTPUT_DIR / task_id / "review_result.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="评审结果不存在")
    
    return FileResponse(
        file_path,
        media_type="application/json",
        filename=f"review_result_{task_id}.json"
    )


@app.get("/api/report/{task_id}/markdown")
async def download_markdown(task_id: str):
    """
    下载解析后的Markdown文件
    """
    file_path = settings.OUTPUT_DIR / task_id / "combined.md"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Markdown文件不存在")
    
    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename=f"contract_{task_id}.md"
    )


@app.get("/api/report/{task_id}/summary")
async def download_summary(task_id: str):
    """
    下载管理层摘要报告 (Markdown)
    """
    file_path = settings.OUTPUT_DIR / task_id / "management_summary.md"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="摘要报告不存在")
    
    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename=f"management_summary_{task_id}.md"
    )


@app.get("/api/report/{task_id}/excel")
async def download_excel(task_id: str):
    """
    下载Excel综合报告
    """
    # 首先尝试xlsx格式
    file_path = settings.OUTPUT_DIR / task_id / "comprehensive_report.xlsx"
    
    if file_path.exists():
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"comprehensive_report_{task_id}.xlsx"
        )
    
    # 如果xlsx不存在，尝试csv格式
    csv_path = settings.OUTPUT_DIR / task_id / "comprehensive_report.csv"
    if csv_path.exists():
        return FileResponse(
            csv_path,
            media_type="text/csv",
            filename=f"comprehensive_report_{task_id}.csv"
        )
    
    raise HTTPException(status_code=404, detail="Excel报告不存在")


@app.get("/api/report/{task_id}/html")
async def download_html_report(task_id: str):
    """
    下载专业HTML网页报告 (多页签格式)
    """
    file_path = settings.OUTPUT_DIR / task_id / "review_report.html"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="HTML报告不存在")
    
    return FileResponse(
        file_path,
        media_type="text/html",
        filename=f"review_report_{task_id}.html"
    )


@app.get("/api/report/{task_id}/html/preview")
async def preview_html_report(task_id: str):
    """
    在浏览器中预览HTML报告
    """
    file_path = settings.OUTPUT_DIR / task_id / "review_report.html"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="HTML报告不存在")
    
    # 直接返回HTML内容用于预览
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


@app.get("/api/report/{task_id}/risk-matrix")
async def download_risk_matrix(task_id: str):
    """
    下载风险矩阵 (CSV)
    """
    file_path = settings.OUTPUT_DIR / task_id / "risk_matrix.csv"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="风险矩阵不存在")
    
    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=f"risk_matrix_{task_id}.csv"
    )


@app.get("/api/report/{task_id}/compliance")
async def download_compliance(task_id: str):
    """
    下载合规检查报告 (CSV)
    """
    file_path = settings.OUTPUT_DIR / task_id / "compliance_check.csv"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="合规检查报告不存在")
    
    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=f"compliance_check_{task_id}.csv"
    )


@app.get("/api/report/{task_id}/zip")
async def download_all_reports(task_id: str):
    """
    下载所有报告 (ZIP打包)
    """
    # 查找ZIP文件
    output_dir = settings.OUTPUT_DIR / task_id
    
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 查找ZIP文件（文件名格式：review_reports_{task_id[:8]}.zip）
    zip_files = list(output_dir.glob("review_reports_*.zip"))
    
    if zip_files:
        return FileResponse(
            zip_files[0],
            media_type="application/zip",
            filename=f"review_reports_{task_id[:8]}.zip"
        )
    
    # 如果ZIP不存在，尝试即时生成
    try:
        import json
        result_path = output_dir / "review_result.json"
        if result_path.exists():
            with open(result_path, "r", encoding="utf-8") as f:
                review_result = json.load(f)
            
            report_files = report_generator.generate_all_reports(
                task_id=task_id,
                review_result=review_result,
                output_dir=output_dir
            )
            
            if "zip_package" in report_files:
                return FileResponse(
                    report_files["zip_package"],
                    media_type="application/zip",
                    filename=f"review_reports_{task_id[:8]}.zip"
                )
    except Exception as e:
        logger.error(f"生成ZIP包失败: {e}")
    
    raise HTTPException(status_code=404, detail="报告包不存在")


@app.get("/api/report/{task_id}/list")
async def list_reports(task_id: str):
    """
    列出所有可用的报告文件
    """
    output_dir = settings.OUTPUT_DIR / task_id
    
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    available_reports = []
    
    report_files = {
        "review_report.html": {"name": "专业网页报告", "type": "html", "endpoint": "html"},
        "review_result.json": {"name": "原始评审结果", "type": "json", "endpoint": "result"},
        "management_summary.md": {"name": "管理层摘要报告", "type": "markdown", "endpoint": "summary"},
        "comprehensive_report.xlsx": {"name": "Excel综合报告", "type": "excel", "endpoint": "excel"},
        "comprehensive_report.csv": {"name": "CSV综合报告", "type": "csv", "endpoint": "excel"},
        "risk_matrix.csv": {"name": "风险矩阵", "type": "csv", "endpoint": "risk-matrix"},
        "compliance_check.csv": {"name": "合规检查报告", "type": "csv", "endpoint": "compliance"},
        "combined.md": {"name": "合同Markdown", "type": "markdown", "endpoint": "markdown"}
    }
    
    for filename, info in report_files.items():
        file_path = output_dir / filename
        if file_path.exists():
            available_reports.append({
                "filename": filename,
                "name": info["name"],
                "type": info["type"],
                "endpoint": f"/api/report/{task_id}/{info['endpoint']}",
                "size": file_path.stat().st_size
            })
    
    # 检查ZIP包
    zip_files = list(output_dir.glob("review_reports_*.zip"))
    if zip_files:
        available_reports.append({
            "filename": zip_files[0].name,
            "name": "全部报告打包",
            "type": "zip",
            "endpoint": f"/api/report/{task_id}/zip",
            "size": zip_files[0].stat().st_size
        })
    
    return {
        "task_id": task_id,
        "reports": available_reports,
        "total": len(available_reports)
    }


# ========== 知识库管理 API ==========

@app.get("/api/knowledge-base/list")
async def list_knowledge_base():
    """
    列出所有知识库文件（带缓存）
    """
    current_time = time.time()
    
    # 检查缓存
    if kb_list_cache['result'] is not None:
        if current_time - kb_list_cache['timestamp'] < kb_list_cache['ttl']:
            return kb_list_cache['result']
    
    try:
        files = kb_manager.list_knowledge_bases()
        result = {
            "success": True,
            "files": files,
            "total": len(files)
        }
        
        # 更新缓存
        kb_list_cache['result'] = result
        kb_list_cache['timestamp'] = current_time
        
        return result
    except Exception as e:
        logger.error(f"列出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-base/upload")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    description: str = Query("", description="文件描述"),
    category: str = Query("custom", description="文件分类")
):
    """
    上传知识库文件
    
    支持: CSV, Excel (.xlsx, .xls), JSON
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 保存文件
        result = kb_manager.upload_knowledge_base(
            filename=file.filename,
            content=content,
            description=description,
            category=category
        )
        
        if result["success"]:
            logger.info(f"知识库文件上传成功: {file.filename}")
            # 清除知识库列表缓存
            kb_list_cache['result'] = None
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "上传失败"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传知识库文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge-base/{filename}")
async def delete_knowledge_base(filename: str):
    """
    删除知识库文件
    """
    try:
        result = kb_manager.delete_knowledge_base(filename)
        
        if result["success"]:
            logger.info(f"知识库文件删除成功: {filename}")
            # 清除知识库列表缓存
            kb_list_cache['result'] = None
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "文件不存在"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/{filename}/preview")
async def preview_knowledge_base(filename: str, rows: int = Query(10, ge=1, le=100)):
    """
    预览知识库文件内容
    """
    try:
        detail = kb_manager.get_knowledge_base_detail(filename)
        
        if "error" not in detail:
            return {
                "success": True,
                "format": "table",
                "data": detail.get("preview_rows", []),
                "columns": detail.get("columns", []),
                "row_count": detail.get("row_count", 0)
            }
        else:
            raise HTTPException(status_code=404, detail=detail.get("error", "文件不存在"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览知识库文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/{filename}/download")
async def download_knowledge_base(filename: str):
    """
    下载知识库文件
    """
    file_path = settings.KB_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 根据文件类型设置MIME类型
    suffix = file_path.suffix.lower()
    mime_types = {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".json": "application/json"
    }
    
    return FileResponse(
        file_path,
        media_type=mime_types.get(suffix, "application/octet-stream"),
        filename=filename
    )


@app.put("/api/knowledge-base/{filename}/metadata")
async def update_knowledge_base_metadata(
    filename: str,
    description: str = Query(None, description="新的文件描述"),
    category: str = Query(None, description="新的文件分类")
):
    """
    更新知识库文件元数据
    """
    try:
        updates = {}
        if description is not None:
            updates["description"] = description
        if category is not None:
            updates["category"] = category
        
        if not updates:
            raise HTTPException(status_code=400, detail="没有提供更新内容")
        
        result = kb_manager.update_knowledge_base_meta(filename, description=description, category=category)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "更新失败"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识库元数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-base/export")
async def export_knowledge_base():
    """
    导出整个知识库为ZIP包
    """
    try:
        # 生成导出文件
        import tempfile
        export_path = Path(tempfile.gettempdir()) / f"kb_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = kb_manager.export_all(export_path)
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-base/import")
async def import_knowledge_base(file: UploadFile = File(...)):
    """
    从ZIP包导入知识库
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持ZIP文件")
    
    try:
        # 保存临时ZIP文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # 导入
        result = kb_manager.import_from_zip(tmp_path)
        
        # 删除临时文件
        os.unlink(tmp_path)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "导入失败"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导入知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 任务历史管理 API ==========

@app.get("/api/history/list")
async def list_task_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="过滤状态")
):
    """
    获取任务历史列表
    """
    try:
        tasks = history_manager.list_tasks(limit=limit, offset=offset, status=status)
        total = history_manager.count_tasks(status=status)
        
        return {
            "success": True,
            "tasks": tasks,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"获取任务历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/statistics")
async def get_history_statistics():
    """
    获取任务统计信息
    """
    try:
        stats = history_manager.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/search")
async def search_task_history(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    搜索任务历史
    """
    try:
        tasks = history_manager.search_tasks(keyword=keyword, limit=limit)
        return {
            "success": True,
            "tasks": tasks,
            "keyword": keyword,
            "total": len(tasks)
        }
    except Exception as e:
        logger.error(f"搜索任务历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/history/cleanup")
async def cleanup_old_tasks(days: int = Query(30, ge=1, le=365)):
    """
    清理旧任务记录
    """
    try:
        result = history_manager.cleanup_old_tasks(days=days)
        return result
    except Exception as e:
        logger.error(f"清理任务历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{task_id}")
async def get_task_history(task_id: str):
    """
    获取单个任务的详细历史
    """
    try:
        task = history_manager.get_task(task_id)
        
        if task:
            return {
                "success": True,
                "task": task
            }
        else:
            raise HTTPException(status_code=404, detail="任务不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history/{task_id}")
async def delete_task_history(task_id: str):
    """
    删除单个任务的历史记录
    """
    try:
        result = history_manager.delete_task(task_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "删除失败"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 工具函数 ==========

def update_task_status(
    task_id: str,
    status: str,
    progress: int,
    message: str
):
    """更新任务状态"""
    if task_id in task_status_db:
        task_status_db[task_id].update({
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": datetime.now().isoformat()
        })
        logger.info(f"任务 {task_id}: {status} - {message} ({progress}%)")
        
        # 同步更新到历史管理器
        try:
            task_data = task_status_db[task_id]
            history_manager.save_task(
                task_id=task_id,
                status=status,
                progress=progress,
                message=message,
                files=task_data.get("files", []),
                report_files=task_data.get("report_files", {})
            )
        except Exception as e:
            logger.warning(f"保存任务历史失败: {e}")


# ========== 启动和关闭事件 ==========

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 60)
    logger.info("合同评审AI系统启动 (End-to-End Edition)")
    logger.info(f"FastAPI: http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
    logger.info(f"API文档: http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}/docs")
    logger.info(f"评审模式: {review_mode}")
    logger.info(f"LLM Provider: {settings.LLM_MODEL} @ {settings.LLM_BASE_URL}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    await codebuddy_client.close()
    await llm_provider.close()
    logger.info("合同评审AI系统已关闭")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True
    )
