"""
知识库管理服务
Contract Review AI - Knowledge Base Manager

功能：
1. 知识库文件上传和管理
2. 知识库内容预览
3. 知识库版本管理
4. 自定义评审规则
"""

import os
import csv
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """
    知识库管理器
    
    管理评审所需的知识库文件（CSV格式），包括：
    - 主合同评审checklist
    - 风险矩阵
    - SOP流程说明
    - 自定义规则
    """
    
    def __init__(self, kb_dir: Path):
        """
        初始化知识库管理器
        
        Args:
            kb_dir: 知识库目录路径
        """
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        
        # 知识库元数据文件
        self.metadata_file = self.kb_dir / ".kb_metadata.json"
        
        # 备份目录
        self.backup_dir = self.kb_dir / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 初始化元数据
        self._init_metadata()
    
    def _init_metadata(self):
        """初始化或加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "files": {}
            }
            self._save_metadata()
    
    def _save_metadata(self):
        """保存元数据"""
        self.metadata["updated_at"] = datetime.now().isoformat()
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        列出所有知识库文件
        
        Returns:
            知识库文件列表
        """
        kb_files = []
        
        for file_path in self.kb_dir.glob("*.csv"):
            if file_path.name.startswith("."):
                continue
            
            stats = file_path.stat()
            file_hash = self._calculate_file_hash(file_path)
            
            # 读取预览数据
            preview = self._get_file_preview(file_path)
            
            # 获取元数据
            file_meta = self.metadata.get("files", {}).get(file_path.name, {})
            
            kb_files.append({
                "filename": file_path.name,
                "display_name": file_meta.get("display_name", file_path.stem),
                "description": file_meta.get("description", ""),
                "category": file_meta.get("category", "通用"),
                "size": stats.st_size,
                "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "hash": file_hash,
                "row_count": preview.get("row_count", 0),
                "columns": preview.get("columns", []),
                "enabled": file_meta.get("enabled", True)
            })
        
        # 按类别和名称排序
        kb_files.sort(key=lambda x: (x["category"], x["filename"]))
        
        return kb_files
    
    def _get_file_preview(self, file_path: Path, max_rows: int = 5) -> Dict[str, Any]:
        """
        获取文件预览数据
        
        Args:
            file_path: 文件路径
            max_rows: 最大预览行数
            
        Returns:
            预览数据字典
        """
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                return {"columns": [], "row_count": 0, "preview_rows": []}
            
            columns = rows[0]
            data_rows = rows[1:]
            
            return {
                "columns": columns,
                "row_count": len(data_rows),
                "preview_rows": data_rows[:max_rows]
            }
        
        except Exception as e:
            logger.error(f"读取文件预览失败: {file_path}, 错误: {e}")
            return {"columns": [], "row_count": 0, "preview_rows": [], "error": str(e)}
    
    def get_knowledge_base_detail(self, filename: str) -> Dict[str, Any]:
        """
        获取知识库详细信息
        
        Args:
            filename: 文件名
            
        Returns:
            详细信息字典
        """
        file_path = self.kb_dir / filename
        
        if not file_path.exists():
            return {"error": "文件不存在"}
        
        stats = file_path.stat()
        preview = self._get_file_preview(file_path, max_rows=20)
        file_meta = self.metadata.get("files", {}).get(filename, {})
        
        return {
            "filename": filename,
            "display_name": file_meta.get("display_name", file_path.stem),
            "description": file_meta.get("description", ""),
            "category": file_meta.get("category", "通用"),
            "size": stats.st_size,
            "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "hash": self._calculate_file_hash(file_path),
            "columns": preview.get("columns", []),
            "row_count": preview.get("row_count", 0),
            "preview_rows": preview.get("preview_rows", []),
            "enabled": file_meta.get("enabled", True),
            "tags": file_meta.get("tags", [])
        }
    
    def upload_knowledge_base(
        self,
        filename: str,
        content: bytes,
        display_name: str = None,
        description: str = "",
        category: str = "通用"
    ) -> Dict[str, Any]:
        """
        上传知识库文件
        
        Args:
            filename: 文件名
            content: 文件内容
            display_name: 显示名称
            description: 描述
            category: 分类
            
        Returns:
            上传结果
        """
        # 验证文件扩展名
        if not filename.endswith(".csv"):
            return {"success": False, "error": "仅支持CSV格式"}
        
        file_path = self.kb_dir / filename
        
        # 如果文件已存在，先备份
        if file_path.exists():
            self._backup_file(file_path)
        
        try:
            # 写入文件
            with open(file_path, "wb") as f:
                f.write(content)
            
            # 验证CSV格式
            preview = self._get_file_preview(file_path)
            if "error" in preview:
                # 删除无效文件
                file_path.unlink()
                return {"success": False, "error": f"CSV格式无效: {preview['error']}"}
            
            # 更新元数据
            self.metadata["files"][filename] = {
                "display_name": display_name or file_path.stem,
                "description": description,
                "category": category,
                "uploaded_at": datetime.now().isoformat(),
                "enabled": True,
                "tags": []
            }
            self._save_metadata()
            
            logger.info(f"知识库上传成功: {filename}")
            
            return {
                "success": True,
                "filename": filename,
                "row_count": preview.get("row_count", 0),
                "columns": preview.get("columns", [])
            }
        
        except Exception as e:
            logger.error(f"上传知识库失败: {filename}, 错误: {e}")
            return {"success": False, "error": str(e)}
    
    def _backup_file(self, file_path: Path):
        """备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"已备份: {file_path.name} -> {backup_name}")
    
    def delete_knowledge_base(self, filename: str, backup: bool = True) -> Dict[str, Any]:
        """
        删除知识库文件
        
        Args:
            filename: 文件名
            backup: 是否备份
            
        Returns:
            删除结果
        """
        file_path = self.kb_dir / filename
        
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        try:
            if backup:
                self._backup_file(file_path)
            
            file_path.unlink()
            
            # 删除元数据
            if filename in self.metadata.get("files", {}):
                del self.metadata["files"][filename]
                self._save_metadata()
            
            logger.info(f"知识库已删除: {filename}")
            
            return {"success": True, "filename": filename}
        
        except Exception as e:
            logger.error(f"删除知识库失败: {filename}, 错误: {e}")
            return {"success": False, "error": str(e)}
    
    def update_knowledge_base_meta(
        self,
        filename: str,
        display_name: str = None,
        description: str = None,
        category: str = None,
        enabled: bool = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        更新知识库元数据
        
        Args:
            filename: 文件名
            display_name: 显示名称
            description: 描述
            category: 分类
            enabled: 是否启用
            tags: 标签
            
        Returns:
            更新结果
        """
        file_path = self.kb_dir / filename
        
        if not file_path.exists():
            return {"success": False, "error": "文件不存在"}
        
        # 获取或创建元数据
        if filename not in self.metadata.get("files", {}):
            self.metadata["files"][filename] = {}
        
        file_meta = self.metadata["files"][filename]
        
        # 更新非空字段
        if display_name is not None:
            file_meta["display_name"] = display_name
        if description is not None:
            file_meta["description"] = description
        if category is not None:
            file_meta["category"] = category
        if enabled is not None:
            file_meta["enabled"] = enabled
        if tags is not None:
            file_meta["tags"] = tags
        
        file_meta["updated_at"] = datetime.now().isoformat()
        
        self._save_metadata()
        
        logger.info(f"知识库元数据已更新: {filename}")
        
        return {"success": True, "filename": filename, "metadata": file_meta}
    
    def get_enabled_knowledge_bases(self) -> List[Path]:
        """
        获取所有启用的知识库文件路径
        
        Returns:
            启用的知识库文件路径列表
        """
        enabled_files = []
        
        for file_path in self.kb_dir.glob("*.csv"):
            if file_path.name.startswith("."):
                continue
            
            file_meta = self.metadata.get("files", {}).get(file_path.name, {})
            
            # 默认启用
            if file_meta.get("enabled", True):
                enabled_files.append(file_path)
        
        return enabled_files
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        kb_list = self.list_knowledge_bases()
        
        total_size = sum(kb["size"] for kb in kb_list)
        total_rows = sum(kb["row_count"] for kb in kb_list)
        enabled_count = sum(1 for kb in kb_list if kb["enabled"])
        
        # 按类别统计
        categories = {}
        for kb in kb_list:
            cat = kb["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "total_rows": 0}
            categories[cat]["count"] += 1
            categories[cat]["total_rows"] += kb["row_count"]
        
        return {
            "total_files": len(kb_list),
            "enabled_files": enabled_count,
            "disabled_files": len(kb_list) - enabled_count,
            "total_size": total_size,
            "total_rows": total_rows,
            "categories": categories,
            "last_updated": self.metadata.get("updated_at", "")
        }
    
    def export_all(self, output_path: Path) -> Path:
        """
        导出所有知识库为ZIP包
        
        Args:
            output_path: 输出路径
            
        Returns:
            ZIP文件路径
        """
        import zipfile
        
        output_path = Path(output_path)
        
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # 添加所有CSV文件
            for file_path in self.kb_dir.glob("*.csv"):
                if not file_path.name.startswith("."):
                    zf.write(file_path, file_path.name)
            
            # 添加元数据
            zf.writestr(".kb_metadata.json", json.dumps(self.metadata, indent=2, ensure_ascii=False))
        
        logger.info(f"知识库已导出: {output_path}")
        
        return output_path
    
    def import_from_zip(self, zip_path: Path, overwrite: bool = False) -> Dict[str, Any]:
        """
        从ZIP包导入知识库
        
        Args:
            zip_path: ZIP文件路径
            overwrite: 是否覆盖现有文件
            
        Returns:
            导入结果
        """
        import zipfile
        
        zip_path = Path(zip_path)
        
        if not zip_path.exists():
            return {"success": False, "error": "ZIP文件不存在"}
        
        imported_files = []
        skipped_files = []
        
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    if name.endswith(".csv") and not name.startswith("."):
                        target_path = self.kb_dir / name
                        
                        if target_path.exists() and not overwrite:
                            skipped_files.append(name)
                            continue
                        
                        if target_path.exists():
                            self._backup_file(target_path)
                        
                        zf.extract(name, self.kb_dir)
                        imported_files.append(name)
                
                # 导入元数据
                if ".kb_metadata.json" in zf.namelist():
                    meta_content = zf.read(".kb_metadata.json").decode("utf-8")
                    imported_meta = json.loads(meta_content)
                    
                    # 合并元数据
                    for filename, file_meta in imported_meta.get("files", {}).items():
                        if filename in imported_files:
                            self.metadata["files"][filename] = file_meta
                    
                    self._save_metadata()
            
            logger.info(f"知识库导入完成: {len(imported_files)} 个文件")
            
            return {
                "success": True,
                "imported": imported_files,
                "skipped": skipped_files
            }
        
        except Exception as e:
            logger.error(f"导入知识库失败: {e}")
            return {"success": False, "error": str(e)}


# 预定义的知识库类别
KB_CATEGORIES = [
    "评审Checklist",
    "风险矩阵",
    "SOP流程",
    "法律法规",
    "行业标准",
    "自定义规则",
    "通用"
]


# 测试代码
if __name__ == "__main__":
    # 测试知识库管理器
    kb_manager = KnowledgeBaseManager(Path("知识库"))
    
    # 列出所有知识库
    print("=" * 60)
    print("知识库列表")
    print("=" * 60)
    
    kb_list = kb_manager.list_knowledge_bases()
    for kb in kb_list:
        print(f"  - {kb['filename']}")
        print(f"    行数: {kb['row_count']}, 大小: {kb['size']} bytes")
        print(f"    列: {', '.join(kb['columns'][:5])}...")
        print()
    
    # 统计信息
    print("=" * 60)
    print("统计信息")
    print("=" * 60)
    stats = kb_manager.get_knowledge_base_stats()
    print(f"  总文件数: {stats['total_files']}")
    print(f"  总行数: {stats['total_rows']}")
    print(f"  总大小: {stats['total_size']:,} bytes")
