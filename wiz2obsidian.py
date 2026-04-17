#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为知笔记到 Obsidian 迁移脚本
支持：HTML 转 Markdown、图片路径转换、元数据保留
版本：1.0
作者：AI 迁移助手
"""

import os
import re
import sqlite3
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import logging

# 尝试导入可选依赖
try:
    import html2text
    from bs4 import BeautifulSoup
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("警告：缺少依赖库，请运行以下命令安装：")
    print("pip install beautifulsoup4 lxml html2text")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WizNote2Obsidian:
    """为知笔记到 Obsidian 迁移工具"""
    
    def __init__(self, wiz_data_path, output_path):
        """
        初始化迁移工具
        
        Args:
            wiz_data_path: 为知笔记数据目录（如 D:/为知笔记4.14/My Knowledge）
            output_path: Obsidian 导出目录
        """
        if not DEPS_AVAILABLE:
            raise ImportError("缺少必需的依赖库，请先安装")
        
        self.wiz_data_path = Path(wiz_data_path)
        self.output_path = Path(output_path)
        self.assets_path = self.output_path / 'assets'
        
        # HTML 转 Markdown 配置
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # 不自动换行
        self.h2t.unicode_snob = True
        self.h2t.skip_internal_links = False
        
        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'images': 0,
            'failed_notes': []
        }
    
    def connect_database(self):
        """连接为知笔记数据库"""
        db_path = self.wiz_data_path / 'index.db'
        if not db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在：{db_path}")
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # 返回字典形式
        logger.info(f"成功连接数据库：{db_path}")
        return conn
    
    def get_all_notes(self, conn, folder_filter=None):
        """
        获取所有笔记信息
        
        Args:
            conn: 数据库连接
            folder_filter: 文件夹过滤（可选）
        """
        query = """
            SELECT 
                DOCUMENT_GUID as guid,
                DOCUMENT_TITLE as title,
                DOCUMENT_LOCATION as location,
                DT_CREATED as created,
                DT_MODIFIED as modified,
                DOCUMENT_TAGS as tags,
                DOCUMENT_TYPE as doc_type
            FROM WIZ_DOCUMENT
            WHERE DOCUMENT_TYPE != 'encrypted'
        """
        
        if folder_filter:
            query += f" AND DOCUMENT_LOCATION LIKE '{folder_filter}%'"
        
        query += " ORDER BY DOCUMENT_LOCATION, DOCUMENT_TITLE"
        
        cursor = conn.execute(query)
        notes = [dict(row) for row in cursor.fetchall()]
        logger.info(f"共找到 {len(notes)} 篇笔记")
        return notes
    
    def extract_ziw(self, ziw_path, extract_to):
        """
        解压 ziw 文件
        
        Args:
            ziw_path: ziw 文件路径
            extract_to: 解压目标目录
        """
        try:
            with zipfile.ZipFile(ziw_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except zipfile.BadZipFile:
            logger.error(f"损坏的 ZIP 文件：{ziw_path}")
            return False
        except Exception as e:
            logger.error(f"解压失败 {ziw_path}: {e}")
            return False
    
    def html_to_markdown(self, html_content, note_title):
        """
        将 HTML 转换为 Markdown
        
        Args:
            html_content: HTML 内容
            note_title: 笔记标题
        """
        try:
            # 使用 BeautifulSoup 预处理
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 处理代码块
            for pre in soup.find_all('pre'):
                code = pre.find('code')
                if code:
                    # 尝试识别语言
                    language = ''
                    if code.get('class'):
                        for cls in code.get('class'):
                            if cls.startswith('language-'):
                                language = cls.replace('language-', '')
                                break
                    
                    # 清理代码内容
                    code_text = code.get_text()
                    code.clear()
                    code.string = code_text
                    
                    # 标记语言
                    if language:
                        pre['data-language'] = language
            
            # 处理图片标签
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and not src.startswith('http'):
                    # 将相对路径标准化
                    img['src'] = os.path.basename(src)
            
            # 转换为 Markdown
            markdown = self.h2t.handle(str(soup))
            
            # 清理多余的空行
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)
            
            # 优化代码块格式
            markdown = re.sub(
                r'```\n(.*?)\n```',
                lambda m: f"```\n{m.group(1).strip()}\n```",
                markdown,
                flags=re.DOTALL
            )
            
            return markdown.strip()
            
        except Exception as e:
            logger.error(f"HTML 转 Markdown 失败 '{note_title}': {e}")
            return None
    
    def convert_image_paths(self, markdown, note_name, assets_subfolder):
        """
        转换图片路径为 Obsidian 格式
        
        Args:
            markdown: Markdown 内容
            note_name: 笔记名称
            assets_subfolder: 资源子文件夹
        """
        # 匹配 Markdown 图片语法 ![alt](path)
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_path(match):
            alt = match.group(1)
            original_path = match.group(2)
            
            # 跳过网络图片
            if original_path.startswith('http'):
                return match.group(0)
            
            # 提取文件名
            filename = os.path.basename(original_path)
            
            # 构建新路径：assets/note_name/filename
            new_path = f"assets/{assets_subfolder}/{filename}"
            
            return f'![{alt}]({new_path})'
        
        # 替换路径
        converted = re.sub(pattern, replace_path, markdown)
        
        return converted
    
    def create_yaml_header(self, note_info):
        """
        创建 YAML Front Matter
        
        Args:
            note_info: 笔记信息字典
        """
        # 处理标签
        tags = []
        if note_info['tags']:
            tags = [tag.strip() for tag in note_info['tags'].split(',') if tag.strip()]
        
        # 处理日期
        created = note_info['created'] if note_info['created'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        modified = note_info['modified'] if note_info['modified'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 格式化日期（只保留日期部分）
        if ' ' in created:
            created = created.split()[0]
        if ' ' in modified:
            modified = modified.split()[0]
        
        # 构建 YAML
        yaml_lines = [
            '---',
            f'title: "{note_info["title"]}"',
            f'date: {created}',
            f'modified: {modified}',
        ]
        
        if tags:
            yaml_lines.append(f'tags: [{", ".join(tags)}]')
        
        # 添加来源标记
        yaml_lines.append('source: WizNote')
        yaml_lines.append('---\n')
        
        return '\n'.join(yaml_lines)
    
    def sanitize_filename(self, filename):
        """
        清理文件名（移除非法字符）
        """
        # Windows 非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        clean_name = re.sub(illegal_chars, '_', filename).strip()
        
        # 移除首尾空格和点
        clean_name = clean_name.strip(' .')
        
        # 限制长度
        if len(clean_name) > 100:
            clean_name = clean_name[:100]
        
        return clean_name or 'untitled'
    
    def process_note(self, note_info, user_data_path):
        """
        处理单个笔记
        
        Args:
            note_info: 笔记信息
            user_data_path: 用户数据路径
        """
        note_title = note_info['title']
        note_guid = note_info['guid']
        note_location = note_info['location']
        
        logger.info(f"处理笔记：{note_location}/{note_title}")
        
        # 构建 ziw 文件路径
        location_path = note_location.strip('/')
        ziw_path = user_data_path / location_path / f"{note_guid}.ziw"
        
        if not ziw_path.exists():
            logger.warning(f"ziw 文件不存在：{ziw_path}")
            self.stats['failed'] += 1
            self.stats['failed_notes'].append({
                'title': note_title,
                'reason': 'ziw 文件不存在'
            })
            return False
        
        # 创建临时解压目录
        temp_dir = Path(f"./temp/{note_guid}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 解压 ziw
            if not self.extract_ziw(ziw_path, temp_dir):
                self.stats['failed'] += 1
                self.stats['failed_notes'].append({
                    'title': note_title,
                    'reason': '解压失败'
                })
                return False
            
            # 读取 HTML 内容
            html_file = temp_dir / 'index.html'
            if not html_file.exists():
                logger.warning(f"index.html 不存在：{html_file}")
                self.stats['failed'] += 1
                self.stats['failed_notes'].append({
                    'title': note_title,
                    'reason': 'HTML 文件不存在'
                })
                return False
            
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # 转换为 Markdown
            markdown = self.html_to_markdown(html_content, note_title)
            if not markdown:
                self.stats['failed'] += 1
                self.stats['failed_notes'].append({
                    'title': note_title,
                    'reason': 'HTML 转换失败'
                })
                return False
            
            # 创建资源子文件夹
            safe_title = self.sanitize_filename(note_title)
            assets_subfolder = safe_title[:50]  # 限制长度
            note_assets_path = self.assets_path / assets_subfolder
            note_assets_path.mkdir(parents=True, exist_ok=True)
            
            # 复制图片资源
            index_files = temp_dir / 'index_files'
            if index_files.exists():
                for img_file in index_files.iterdir():
                    if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']:
                        try:
                            shutil.copy2(img_file, note_assets_path / img_file.name)
                            self.stats['images'] += 1
                        except Exception as e:
                            logger.warning(f"复制图片失败 {img_file.name}: {e}")
            
            # 转换图片路径
            markdown = self.convert_image_paths(markdown, note_title, assets_subfolder)
            
            # 添加 YAML 头部
            yaml_header = self.create_yaml_header(note_info)
            full_markdown = yaml_header + markdown
            
            # 构建输出路径（保留文件夹结构）
            relative_path = note_location.strip('/')
            output_folder = self.output_path / relative_path
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # 写入 Markdown 文件
            output_file = output_folder / f"{safe_title}.md"
            
            # 处理文件名冲突
            counter = 1
            while output_file.exists():
                output_file = output_folder / f"{safe_title}_{counter}.md"
                counter += 1
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_markdown)
            
            self.stats['success'] += 1
            logger.info(f"✓ 成功转换：{output_file}")
            return True
            
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def migrate(self, folder_filter=None):
        """
        执行完整迁移
        
        Args:
            folder_filter: 只迁移指定文件夹（可选）
        """
        logger.info("="*60)
        logger.info("开始迁移为知笔记到 Obsidian")
        logger.info("="*60)
        
        # 创建输出目录
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.assets_path.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        conn = self.connect_database()
        
        # 获取所有笔记
        notes = self.get_all_notes(conn, folder_filter)
        self.stats['total'] = len(notes)
        
        # 获取用户数据路径
        data_path = self.wiz_data_path / 'data'
        user_folders = [d for d in data_path.iterdir() if d.is_dir() and '@' in d.name]
        
        if not user_folders:
            logger.error("未找到用户数据目录")
            conn.close()
            return
        
        user_data_path = user_folders[0]  # 取第一个用户
        logger.info(f"用户数据目录：{user_data_path}")
        
        # 处理每个笔记
        for i, note in enumerate(notes, 1):
            logger.info(f"进度：{i}/{self.stats['total']}")
            self.process_note(note, user_data_path)
        
        # 关闭数据库
        conn.close()
        
        # 输出统计信息
        logger.info("="*60)
        logger.info("迁移完成！统计信息：")
        logger.info(f"  总计笔记：{self.stats['total']}")
        logger.info(f"  成功转换：{self.stats['success']}")
        logger.info(f"  失败数量：{self.stats['failed']}")
        logger.info(f"  图片数量：{self.stats['images']}")
        logger.info(f"输出目录：{self.output_path}")
        
        if self.stats['failed'] > 0:
            logger.info("\n失败的笔记：")
            for failed in self.stats['failed_notes']:
                logger.info(f"  - {failed['title']}: {failed['reason']}")
        
        logger.info("="*60)
        
        return self.stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='为知笔记到 Obsidian 迁移工具')
    parser.add_argument('--wiz', required=True, help='为知笔记数据目录')
    parser.add_argument('--output', required=True, help='Obsidian 输出目录')
    parser.add_argument('--folder', help='只迁移指定文件夹（可选）')
    
    args = parser.parse_args()
    
    # 检查依赖
    if not DEPS_AVAILABLE:
        print("\n错误：缺少必需的依赖库")
        print("请运行以下命令安装：")
        print("  pip install beautifulsoup4 lxml html2text")
        return
    
    # 创建迁移器
    migrator = WizNote2Obsidian(args.wiz, args.output)
    
    # 执行迁移
    migrator.migrate(folder_filter=args.folder)


if __name__ == '__main__':
    main()
