"""
文档解析服务 - 基于MarkItDown
Document Parser Service based on Microsoft MarkItDown
增强: 支持旧版 .doc 文件解析 (通过 pywin32)
"""

from pathlib import Path
from typing import Dict, List, Optional
import logging
import time
import os
import tempfile

# MarkItDown导入
try:
    from markitdown import MarkItDown
except ImportError:
    raise ImportError(
        "MarkItDown未安装。请运行: pip install 'markitdown[all]'"
    )

# pywin32 导入 (用于解析旧版 .doc 文件)
try:
    import win32com.client
    import pythoncom
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

logger = logging.getLogger(__name__)


class UnifiedDocumentParser:
    """
    统一文档解析器 - 基于MarkItDown
    
    支持格式:
    - PDF, Word (.docx), Excel (.xlsx/.xls), PowerPoint (.pptx)
    - 图片 (.jpg, .png) - 支持OCR
    - 音频 (.wav, .mp3) - 支持语音转文字
    - HTML, CSV, JSON, XML
    - ZIP (递归解析内部文件)
    - EPub, Outlook邮件 (.msg)
    """
    
    def __init__(self, enable_llm_description: bool = False):
        """
        初始化解析器
        
        Args:
            enable_llm_description: 是否启用LLM图片描述功能（需要OpenAI API Key）
        """
        self.enable_llm_description = enable_llm_description
        
        if enable_llm_description:
            try:
                from openai import OpenAI
                client = OpenAI()
                self.md = MarkItDown(
                    llm_client=client,
                    llm_model="gpt-4o"
                )
                logger.info("MarkItDown初始化完成 (LLM图片描述已启用)")
            except Exception as e:
                logger.warning(f"无法启用LLM图片描述: {e}")
                self.md = MarkItDown()
                logger.info("MarkItDown初始化完成 (标准模式)")
        else:
            self.md = MarkItDown()
            logger.info("MarkItDown初始化完成 (标准模式)")
        
        # 检查 .doc 支持
        if HAS_WIN32COM:
            logger.info("已启用 .doc 文件支持 (pywin32)")
        else:
            logger.warning("pywin32 未安装，.doc 文件将尝试用 MarkItDown 解析")
    
    def _convert_doc_to_docx(self, doc_path: str) -> Optional[str]:
        """
        使用 Word COM 将 .doc 转换为 .docx
        
        Args:
            doc_path: .doc 文件路径
            
        Returns:
            转换后的 .docx 文件路径，失败返回 None
        """
        if not HAS_WIN32COM:
            return None
        
        try:
            # 初始化 COM
            pythoncom.CoInitialize()
            
            # 创建 Word 应用实例
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            
            # 打开 .doc 文件
            doc_path = os.path.abspath(doc_path)
            doc = word.Documents.Open(doc_path)
            
            # 创建临时 .docx 文件路径
            docx_path = doc_path + "x"  # .doc -> .docx
            
            # 另存为 .docx (FileFormat=16 表示 docx)
            doc.SaveAs2(docx_path, FileFormat=16)
            doc.Close()
            word.Quit()
            
            # 释放 COM
            pythoncom.CoUninitialize()
            
            logger.info(f"成功将 .doc 转换为 .docx: {docx_path}")
            return docx_path
            
        except Exception as e:
            logger.error(f"转换 .doc 文件失败: {e}")
            try:
                pythoncom.CoUninitialize()
            except:
                pass
            return None
    
    def _extract_doc_text_directly(self, doc_path: str) -> Optional[str]:
        """
        直接从 .doc 文件提取文本（不转换格式）
        
        Args:
            doc_path: .doc 文件路径
            
        Returns:
            提取的文本内容，失败返回 None
        """
        if not HAS_WIN32COM:
            return None
        
        try:
            # 初始化 COM
            pythoncom.CoInitialize()
            
            # 创建 Word 应用实例
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            
            # 打开 .doc 文件
            doc_path = os.path.abspath(doc_path)
            doc = word.Documents.Open(doc_path)
            
            # 提取全部文本
            text = doc.Content.Text
            
            # 提取表格内容
            tables_text = []
            for i, table in enumerate(doc.Tables):
                table_content = []
                for row in table.Rows:
                    row_text = []
                    for cell in row.Cells:
                        cell_text = cell.Range.Text.strip().replace('\r\x07', '')
                        row_text.append(cell_text)
                    table_content.append(" | ".join(row_text))
                tables_text.append(f"\n**表格 {i+1}:**\n" + "\n".join(table_content))
            
            doc.Close()
            word.Quit()
            
            # 释放 COM
            pythoncom.CoUninitialize()
            
            # 组合内容
            full_text = text
            if tables_text:
                full_text += "\n\n---\n\n## 表格内容\n" + "\n".join(tables_text)
            
            logger.info(f"成功从 .doc 文件提取文本: {len(full_text)} 字符")
            return full_text
            
        except Exception as e:
            logger.error(f"提取 .doc 文本失败: {e}")
            try:
                pythoncom.CoUninitialize()
            except:
                pass
            return None
    
    def parse_file(self, file_path: str) -> Dict[str, any]:
        """
        解析单个文件为Markdown
        
        Args:
            file_path: 文件路径
            
        Returns:
            {
                "success": True/False,
                "markdown": "Markdown文本",
                "metadata": {
                    "file_name": "文件名",
                    "file_type": "文件类型",
                    "file_size": 文件大小(bytes),
                    "parse_time": 解析耗时(seconds)
                },
                "error": "错误信息（如果失败）"
            }
        """
        start_time = time.time()
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {file_path}",
                "metadata": {}
            }
        
        logger.info(f"开始解析文件: {file_path.name}")
        
        try:
            # 检查是否是 .doc 文件，需要特殊处理
            if file_path.suffix.lower() == '.doc':
                logger.info(f"检测到 .doc 文件，使用特殊处理: {file_path.name}")
                
                # 方法1: 尝试直接提取文本
                text_content = self._extract_doc_text_directly(str(file_path))
                
                if text_content:
                    parse_time = time.time() - start_time
                    logger.info(f".doc 文件解析成功 (直接提取): {file_path.name} (耗时: {parse_time:.2f}s)")
                    
                    return {
                        "success": True,
                        "markdown": text_content,
                        "metadata": {
                            "file_name": file_path.name,
                            "file_type": file_path.suffix,
                            "file_size": file_path.stat().st_size,
                            "parse_time": round(parse_time, 2),
                            "parse_method": "win32com_direct"
                        },
                        "error": None
                    }
                
                # 方法2: 尝试转换为 .docx 再解析
                docx_path = self._convert_doc_to_docx(str(file_path))
                if docx_path and Path(docx_path).exists():
                    try:
                        result = self.md.convert(docx_path)
                        parse_time = time.time() - start_time
                        
                        # 清理临时文件
                        try:
                            os.remove(docx_path)
                        except:
                            pass
                        
                        logger.info(f".doc 文件解析成功 (转换后): {file_path.name} (耗时: {parse_time:.2f}s)")
                        
                        return {
                            "success": True,
                            "markdown": result.text_content,
                            "metadata": {
                                "file_name": file_path.name,
                                "file_type": file_path.suffix,
                                "file_size": file_path.stat().st_size,
                                "parse_time": round(parse_time, 2),
                                "parse_method": "win32com_convert"
                            },
                            "error": None
                        }
                    except Exception as e:
                        logger.warning(f"转换后解析失败: {e}")
                        # 清理临时文件
                        try:
                            os.remove(docx_path)
                        except:
                            pass
                
                # 方法3: 回退到 MarkItDown 尝试解析
                logger.warning(f"尝试用 MarkItDown 解析 .doc 文件: {file_path.name}")
            
            # 调用MarkItDown转换 (常规文件或 .doc 回退)
            result = self.md.convert(str(file_path))
            
            parse_time = time.time() - start_time
            
            logger.info(f"文件解析成功: {file_path.name} (耗时: {parse_time:.2f}s)")
            
            return {
                "success": True,
                "markdown": result.text_content,
                "metadata": {
                    "file_name": file_path.name,
                    "file_type": file_path.suffix,
                    "file_size": file_path.stat().st_size,
                    "parse_time": round(parse_time, 2)
                },
                "error": None
            }
        
        except Exception as e:
            parse_time = time.time() - start_time
            error_msg = f"文件解析失败: {file_path.name}, 错误: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "markdown": "",
                "metadata": {
                    "file_name": file_path.name,
                    "file_type": file_path.suffix,
                    "file_size": file_path.stat().st_size if file_path.exists() else 0,
                    "parse_time": round(parse_time, 2)
                },
                "error": str(e)
            }
    
    def parse_multiple_files(self, file_paths: List[str]) -> Dict[str, Dict]:
        """
        批量解析多个文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            {
                "file1.pdf": {"success": True, "markdown": "...", "metadata": {...}},
                "file2.docx": {"success": True, "markdown": "...", "metadata": {...}},
                ...
            }
        """
        results = {}
        
        logger.info(f"开始批量解析 {len(file_paths)} 个文件")
        
        for file_path in file_paths:
            file_name = Path(file_path).name
            result = self.parse_file(file_path)
            results[file_name] = result
        
        # 统计
        success_count = sum(1 for r in results.values() if r["success"])
        fail_count = len(results) - success_count
        
        logger.info(f"批量解析完成: 成功 {success_count} 个, 失败 {fail_count} 个")
        
        return results
    
    def combine_markdowns(
        self,
        results: Dict[str, Dict],
        include_metadata: bool = True
    ) -> str:
        """
        合并多个文件的Markdown内容
        
        Args:
            results: parse_multiple_files的返回结果
            include_metadata: 是否包含元数据信息
            
        Returns:
            合并后的Markdown文本
        """
        combined = []
        
        # 添加总览
        total_files = len(results)
        success_files = sum(1 for r in results.values() if r["success"])
        
        combined.append(f"# 合同文件解析结果\n")
        combined.append(f"**总文件数**: {total_files}\n")
        combined.append(f"**解析成功**: {success_files}\n")
        combined.append(f"**解析失败**: {total_files - success_files}\n")
        combined.append("\n---\n\n")
        
        # 逐个文件添加内容
        for file_name, data in results.items():
            if not data["success"]:
                combined.append(f"## ❌ 文件: {file_name}\n")
                combined.append(f"**解析失败**: {data['error']}\n")
                combined.append("\n---\n\n")
                continue
            
            combined.append(f"## 📄 文件: {file_name}\n\n")
            
            if include_metadata:
                meta = data["metadata"]
                combined.append(f"- **文件类型**: {meta['file_type']}\n")
                combined.append(f"- **文件大小**: {self._format_size(meta['file_size'])}\n")
                combined.append(f"- **解析耗时**: {meta['parse_time']}秒\n")
                combined.append("\n")
            
            combined.append("### 文件内容\n\n")
            combined.append(data['markdown'])
            combined.append("\n\n---\n\n")
        
        return "".join(combined)
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的文件格式列表"""
        return [
            '.pdf',      # PDF文件
            '.docx',     # Word文档
            '.doc',      # Word文档（旧版）
            '.xlsx',     # Excel表格
            '.xls',      # Excel表格（旧版）
            '.pptx',     # PowerPoint演示
            '.ppt',      # PowerPoint演示（旧版）
            '.jpg',      # 图片
            '.jpeg',     # 图片
            '.png',      # 图片
            '.gif',      # 图片
            '.bmp',      # 图片
            '.wav',      # 音频
            '.mp3',      # 音频
            '.html',     # HTML
            '.htm',      # HTML
            '.csv',      # CSV
            '.json',     # JSON
            '.xml',      # XML
            '.zip',      # ZIP压缩包
            '.epub',     # 电子书
            '.msg',      # Outlook邮件
        ]
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = Path(file_path).suffix.lower()
        return ext in UnifiedDocumentParser.get_supported_formats()


# ========== 使用示例 ==========
def example_usage():
    """使用示例"""
    
    # 初始化解析器
    parser = UnifiedDocumentParser()
    
    # 单文件解析
    result = parser.parse_file("contract.pdf")
    if result["success"]:
        print(result["markdown"])
    else:
        print(f"解析失败: {result['error']}")
    
    # 多文件解析
    files = ["contract.pdf", "appendix.docx", "budget.xlsx"]
    results = parser.parse_multiple_files(files)
    
    # 合并为一个Markdown
    combined_md = parser.combine_markdowns(results)
    print(combined_md)
    
    # 保存到文件
    with open("combined_contract.md", "w", encoding="utf-8") as f:
        f.write(combined_md)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行示例
    example_usage()
