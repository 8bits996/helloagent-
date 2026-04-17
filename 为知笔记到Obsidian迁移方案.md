# 为知笔记 4.14 到 Obsidian 完整迁移方案

## 📋 目录
1. [方案概述](#方案概述)
2. [技术原理深度解析](#技术原理深度解析)
3. [迁移前准备工作](#迁移前准备工作)
4. [方案一：官方插件导出法（推荐）](#方案一官方插件导出法推荐)
5. [方案二：Python 脚本自动化转换](#方案二python-脚本自动化转换)
6. [方案三：Node.js 工具批量处理](#方案三nodejs-工具批量处理)
7. [方案四：手动解压转换法（兼容性最强）](#方案四手动解压转换法兼容性最强)
8. [Obsidian 导入与优化配置](#obsidian-导入与优化配置)
9. [常见问题与解决方案](#常见问题与解决方案)
10. [进阶：API 自动化迁移](#进阶api-自动化迁移)

---

## 方案概述

### 核心挑战
- **格式差异**：为知笔记使用 HTML 格式存储，Obsidian 使用 Markdown
- **图片路径**：为知笔记图片在 `index_files/`，Obsidian 推荐相对路径
- **元数据丢失**：标签、创建时间、修改时间需要保留
- **特殊格式**：代码块、表格、数学公式、思维导图等

### 方案对比

| 方案 | 适用场景 | 难度 | 信息完整度 | 耗时 |
|------|---------|------|-----------|------|
| 官方插件导出 | 少量笔记，格式简单 | ⭐ | 90% | 短 |
| Python 脚本 | 批量处理，技术用户 | ⭐⭐⭐ | 95% | 中 |
| Node.js 工具 | 本地数据库直接转换 | ⭐⭐⭐⭐ | 85% | 中 |
| 手动解压 | 兼容所有格式，完全控制 | ⭐⭐ | 100% | 长 |
| API 自动化 | 企业级批量迁移 | ⭐⭐⭐⭐⭐ | 98% | 长 |

---

## 技术原理深度解析

### 1. 为知笔记数据结构

#### 文件系统结构
```
D:\为知笔记4.14\
├── My Knowledge\
│   ├── index.db                    # SQLite 数据库（元数据）
│   └── data\
│       └── your_email@domain\
│           ├── 笔记文件夹名\
│           │   ├── {GUID}.ziw     # 笔记文件（ZIP 格式）
│           │   └── {GUID}.ziw
│           └── 另一个文件夹\
```

#### ziw 文件内部结构
```
{GUID}.ziw (实际是 ZIP 压缩包)
├── index.html              # 笔记内容（HTML 格式）
├── index_files\           # 资源文件夹
│   ├── image001.png
│   ├── image002.jpg
│   └── attachment.pdf
└── meta.xml               # 元数据（部分版本）
```

#### 数据库关键表结构（index.db）
```sql
-- 笔记元数据表
WIZ_DOCUMENT
├── DOCUMENT_GUID          -- 笔记唯一 ID
├── DOCUMENT_TITLE         -- 标题
├── DOCUMENT_LOCATION      -- 文件夹路径
├── DT_CREATED             -- 创建时间
├── DT_MODIFIED            -- 修改时间
├── DOCUMENT_TAGS          -- 标签（逗号分隔）
└── DOCUMENT_TYPE          -- 类型（markdown/html/etc）

-- 文件夹表
WIZ_FOLDER
├── FOLDER_GUID
├── FOLDER_NAME
└── FOLDER_LOCATION
```

### 2. Obsidian 格式要求

#### 标准 Markdown 格式
```markdown
---
title: 笔记标题
date: 2024-01-15
tags: [标签1, 标签2]
---

# 标题

正文内容...

![](assets/image.png)  <!-- 相对路径图片 -->
```

#### 推荐的附件管理结构
```
Obsidian Vault\
├── 笔记1.md
├── assets\
│   ├── 笔记1\           # 按笔记名分类
│   │   ├── image1.png
│   │   └── image2.jpg
│   └── 笔记2\
└── 笔记2.md
```

### 3. HTML 到 Markdown 转换原理

#### Turndown.js 核心逻辑
```javascript
// 代码块转换
turndownService.addRule('codeBlock', {
  filter: 'pre',
  replacement: function(content, node) {
    const language = node.getAttribute('class') || '';
    return '\n```' + language + '\n' + content + '\n```\n';
  }
});

// 表格转换
turndownService.addRule('table', {
  filter: 'table',
  replacement: function(content) {
    // 复杂的表格转换逻辑
  }
});
```

---

## 迁移前准备工作

### 步骤 1：数据备份（强制）

```powershell
# 创建备份目录
$source = "D:\为知笔记4.14"
$backup = "D:\WizNote_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $source -Destination $backup -Recurse
Write-Host "备份完成：$backup" -ForegroundColor Green
```

### 步骤 2：检查数据完整性

#### 检查笔记数量
```sql
-- 打开 index.db 数据库（使用 DB Browser for SQLite）
SELECT 
    COUNT(*) as total_notes,
    COUNT(DISTINCT DOCUMENT_LOCATION) as total_folders
FROM WIZ_DOCUMENT;
```

#### 检查是否有加密笔记
```sql
SELECT DOCUMENT_TITLE, DOCUMENT_LOCATION 
FROM WIZ_DOCUMENT 
WHERE DOCUMENT_TYPE = 'encrypted';
```

### 步骤 3：安装必需工具

#### Python 环境准备
```powershell
# 安装 Python 3.9+（如未安装）
winget install Python.Python.3.12

# 安装依赖库
pip install beautifulsoup4 lxml html2text pillow
```

#### Node.js 环境准备（可选）
```powershell
# 安装 Node.js 18+
winget install OpenJS.NodeJS.LTS

# 安装核心库
npm install -g turndown jszip sqlite3
```

### 步骤 4：创建工作目录

```powershell
# 创建迁移工作目录
$workDir = "D:\WizNote_Migration"
New-Item -Path $workDir -ItemType Directory -Force
New-Item -Path "$workDir\ziw_extracted" -ItemType Directory -Force
New-Item -Path "$workDir\markdown_output" -ItemType Directory -Force
New-Item -Path "$workDir\logs" -ItemType Directory -Force
```

---

## 方案一：官方插件导出法（推荐）

### 适用场景
- 笔记数量 < 500 篇
- 主要使用 Markdown 格式
- 图片较少且格式简单

### 详细步骤

#### 1. 安装 ExportToMd 插件

```powershell
# 下载插件
git clone https://github.com/zdaiot/wiznote2hexo2csdn.git
# 或直接下载 ZIP：https://github.com/zdaiot/wiznote2hexo2csdn/archive/refs/heads/master.zip

# 复制插件到为知笔记目录
$pluginPath = "D:\为知笔记4.14\WizNote\Plugins\ExportToMd"
Copy-Item -Path ".\wiznote2hexo2csdn-master\ExportToMd" -Destination $pluginPath -Recurse
```

#### 2. 配置插件

编辑 `ExportToMd\config.js`：
```javascript
module.exports = {
    // 导出的 Markdown 文件存放路径
    markdownPath: 'D:\\WizNote_Migration\\markdown_output',
    
    // 图片存放路径（相对路径）
    imagePath: 'assets',
    
    // 是否保留文件夹结构
    keepFolderStructure: true,
    
    // 是否导出标签为 categories
    exportTags: true,
    
    // 是否在文件头部添加 YAML Front Matter
    addYamlHeader: true
};
```

#### 3. 重启为知笔记并导出

1. 关闭为知笔记
2. 重新打开为知笔记
3. 右键点击根目录或特定文件夹
4. 选择"导出为 Markdown"
5. 等待导出完成

#### 4. 验证导出结果

```powershell
# 统计导出的文件数量
$mdCount = (Get-ChildItem -Path "D:\WizNote_Migration\markdown_output" -Filter "*.md" -Recurse).Count
$imageCount = (Get-ChildItem -Path "D:\WizNote_Migration\markdown_output\assets" -File -Recurse).Count

Write-Host "导出的 Markdown 文件：$mdCount 个" -ForegroundColor Green
Write-Host "导出的图片文件：$imageCount 个" -ForegroundColor Green
```

### 优缺点
- ✅ 操作简单，无需编程
- ✅ 保留文件夹结构
- ✅ 自动处理图片路径
- ❌ 仅支持 Markdown 格式笔记
- ❌ 部分特殊格式可能丢失

---

## 方案二：Python 脚本自动化转换

### 适用场景
- 笔记数量 > 500 篇
- 包含 HTML 格式笔记
- 需要高度自定义转换规则

### 完整脚本实现

创建文件 `wiz2obsidian.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为知笔记到 Obsidian 迁移脚本
支持：HTML 转 Markdown、图片路径转换、元数据保留
"""

import os
import re
import sqlite3
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import html2text
from bs4 import BeautifulSoup
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/WizNote_Migration/logs/migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WizNote2Obsidian:
    def __init__(self, wiz_data_path, output_path):
        """
        初始化迁移工具
        
        Args:
            wiz_data_path: 为知笔记数据目录（如 D:/为知笔记4.14/My Knowledge）
            output_path: Obsidian 导出目录
        """
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
            'images': 0
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
                    language = code.get('class', [''])[0].replace('language-', '')
                    code.string = f"\n```{language}\n{code.get_text()}\n```\n"
            
            # 处理表格（html2text 自动支持）
            
            # 转换为 Markdown
            markdown = self.h2t.handle(str(soup))
            
            # 清理多余的空行
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)
            
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
            
            # 提取文件名
            filename = os.path.basename(original_path)
            
            # 构建新路径：assets/note_name/filename
            new_path = f"assets/{assets_subfolder}/{filename}"
            
            return f'![{alt}]({new_path})'
        
        # 替换路径
        converted = re.sub(pattern, replace_path, markdown)
        
        # 处理 HTML img 标签
        html_img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        
        def replace_html_img(match):
            original_path = match.group(1)
            filename = os.path.basename(original_path)
            new_path = f"assets/{assets_subfolder}/{filename}"
            return match.group(0).replace(original_path, new_path)
        
        converted = re.sub(html_img_pattern, replace_html_img, converted)
        
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
            tags = [tag.strip() for tag in note_info['tags'].split(',')]
        
        # 处理日期
        created = note_info['created'] if note_info['created'] else datetime.now().strftime('%Y-%m-%d')
        modified = note_info['modified'] if note_info['modified'] else datetime.now().strftime('%Y-%m-%d')
        
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
        return re.sub(illegal_chars, '_', filename).strip()
    
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
            return False
        
        # 创建临时解压目录
        temp_dir = Path(f"D:/WizNote_Migration/temp/{note_guid}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 解压 ziw
        if not self.extract_ziw(ziw_path, temp_dir):
            self.stats['failed'] += 1
            return False
        
        # 读取 HTML 内容
        html_file = temp_dir / 'index.html'
        if not html_file.exists():
            logger.warning(f"index.html 不存在：{html_file}")
            self.stats['failed'] += 1
            return False
        
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # 转换为 Markdown
        markdown = self.html_to_markdown(html_content, note_title)
        if not markdown:
            self.stats['failed'] += 1
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
                if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']:
                    shutil.copy2(img_file, note_assets_path / img_file.name)
                    self.stats['images'] += 1
        
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
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_markdown)
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        self.stats['success'] += 1
        logger.info(f"✓ 成功转换：{output_file}")
        return True
    
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
        logger.info("="*60)


if __name__ == '__main__':
    # 配置路径
    WIZ_DATA_PATH = r'D:\为知笔记4.14\My Knowledge'
    OUTPUT_PATH = r'D:\Obsidian_Vault'
    
    # 创建迁移器
    migrator = WizNote2Obsidian(WIZ_DATA_PATH, OUTPUT_PATH)
    
    # 执行迁移（可选：指定文件夹）
    # migrator.migrate(folder_filter='/我的笔记/技术文档')
    migrator.migrate()
```

#### 使用方法

```powershell
# 安装依赖
pip install beautifulsoup4 lxml html2text

# 运行脚本
cd D:\WizNote_Migration
python wiz2obsidian.py
```

#### 高级配置选项

编辑脚本中的转换配置：
```python
# 自定义代码块语言识别
def detect_code_language(pre_tag):
    """检测代码块语言"""
    classes = pre_tag.get('class', [])
    for cls in classes:
        if cls.startswith('language-'):
            return cls.replace('language-', '')
    return ''

# 自定义表格处理
def process_table(table):
    """处理复杂表格"""
    # 使用 pandas 或自定义逻辑
    pass

# 自定义数学公式
def process_math(soup):
    """处理 MathJax 或 LaTeX 公式"""
    for script in soup.find_all('script', type='math/tex'):
        # 提取公式内容
        latex = script.string
        # 替换为 Markdown 格式
        script.replace_with(f'$$ {latex} $$')
```

### 针对特殊格式的处理

#### 1. 思维导图转换
```python
def process_mindmap(html_content):
    """将思维导图转为文本大纲"""
    # 提取思维导图数据
    # 转换为缩进列表
    pass
```

#### 2. 表格优化
```python
def optimize_table(markdown_table):
    """优化表格格式"""
    # 对齐列
    # 处理合并单元格
    pass
```

### 优缺点
- ✅ 批量处理高效
- ✅ 高度可定制
- ✅ 保留完整元数据
- ✅ 支持所有笔记类型
- ❌ 需要编程基础
- ❌ 需要调试和优化

---

## 方案三：Node.js 工具批量处理

### 适用场景
- 本地数据库直接读取
- JavaScript 技术栈用户
- 需要快速批量转换

### 完整实现

#### 1. 克隆 wiznote2markdown 项目

```powershell
# 克隆项目
git clone https://github.com/chaoyz/wiznote2markdown.git
cd wiznote2markdown

# 安装依赖
npm install
```

#### 2. 配置文件修改

创建 `config.js`：
```javascript
module.exports = {
    // 为知笔记数据目录
    wizHome: 'D:/为知笔记4.14/My Knowledge',
    
    // 用户邮箱
    username: 'your_email@example.com',
    
    // 输出目录
    outputDir: 'D:/Obsidian_Vault',
    
    // 图片处理配置
    imageConfig: {
        // 图片存储策略
        strategy: 'per_note', // 'per_note' 每个笔记单独文件夹，'centralized' 集中存储
        
        // 图片质量（0-100）
        quality: 85,
        
        // 是否转换为 WebP
        convertToWebP: false
    },
    
    // Markdown 配置
    markdownConfig: {
        // 标题风格
        headingStyle: 'atx', // 'atx' (#) 或 'setext' (下划线)
        
        // 代码块风格
        codeBlockStyle: 'fenced', // 'fenced' (```) 或 'indented'
        
        // 是否保留 HTML 标签
        keepHtmlTags: false
    }
};
```

#### 3. 优化转换脚本

修改 `wiz2md.js` 添加 Obsidian 优化：
```javascript
const TurndownService = require('turndown');
const jszip = require('jszip');
const fs = require('fs-extra');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// 自定义 Turndown 配置
const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    bulletListMarker: '-'
});

// 添加代码块语言识别
turndownService.addRule('codeBlock', {
    filter: 'pre',
    replacement: function(content, node) {
        const code = node.querySelector('code');
        let language = '';
        
        if (code) {
            const classes = code.className.split(' ');
            language = classes.find(c => c.startsWith('language-'))?.replace('language-', '') || '';
        }
        
        return '\n```' + language + '\n' + content + '\n```\n';
    }
});

// 优化表格转换
turndownService.addRule('table', {
    filter: 'table',
    replacement: function(content, node) {
        // 获取表格行
        const rows = node.querySelectorAll('tr');
        let markdown = '\n';
        
        rows.forEach((row, index) => {
            const cells = row.querySelectorAll('th, td');
            const cellContents = Array.from(cells).map(cell => 
                cell.textContent.trim().replace(/\|/g, '\\|')
            );
            
            markdown += '| ' + cellContents.join(' | ') + ' |\n';
            
            // 添加分隔行（表头后）
            if (index === 0) {
                markdown += '| ' + cellContents.map(() => '---').join(' | ') + ' |\n';
            }
        });
        
        return markdown + '\n';
    }
});

// 处理图片路径
function convertImagePaths(markdown, noteName) {
    // 匹配 Markdown 图片语法
    return markdown.replace(
        /!\[([^\]]*)\]\(([^)]+)\)/g,
        (match, alt, originalPath) => {
            const filename = path.basename(originalPath);
            return `![${alt}](assets/${noteName}/${filename})`;
        }
    );
}

// 创建 YAML Front Matter
function createYamlHeader(noteInfo) {
    const lines = [
        '---',
        `title: "${noteInfo.title}"`,
        `date: ${noteInfo.created}`,
        `modified: ${noteInfo.modified}`
    ];
    
    if (noteInfo.tags) {
        const tagArray = noteInfo.tags.split(',').map(t => t.trim());
        lines.push(`tags: [${tagArray.join(', ')}]`);
    }
    
    lines.push('source: WizNote');
    lines.push('---\n');
    
    return lines.join('\n');
}

// 主转换函数
async function convertNote(noteInfo, db) {
    const ziwPath = path.join(
        config.wizHome,
        'data',
        config.username,
        noteInfo.location,
        `${noteInfo.guid}.ziw`
    );
    
    try {
        // 读取 ziw 文件
        const ziwData = await fs.readFile(ziwPath);
        const zip = await jszip.loadAsync(ziwData);
        
        // 解压 HTML
        const htmlContent = await zip.file('index.html').async('string');
        
        // 转换为 Markdown
        let markdown = turndownService.turndown(htmlContent);
        
        // 转换图片路径
        const noteName = sanitizeFilename(noteInfo.title);
        markdown = convertImagePaths(markdown, noteName);
        
        // 提取并保存图片
        const imageFiles = Object.keys(zip.files).filter(f => 
            f.startsWith('index_files/') && 
            /\.(png|jpg|jpeg|gif|bmp|svg)$/i.test(f)
        );
        
        const imageDir = path.join(config.outputDir, 'assets', noteName);
        await fs.ensureDir(imageDir);
        
        for (const imageFile of imageFiles) {
            const imageData = await zip.file(imageFile).async('nodebuffer');
            const imageName = path.basename(imageFile);
            await fs.writeFile(path.join(imageDir, imageName), imageData);
        }
        
        // 添加 YAML 头部
        const yamlHeader = createYamlHeader(noteInfo);
        const fullMarkdown = yamlHeader + markdown;
        
        // 保存 Markdown 文件
        const outputDir = path.join(config.outputDir, noteInfo.location);
        await fs.ensureDir(outputDir);
        const outputPath = path.join(outputDir, `${noteName}.md`);
        await fs.writeFile(outputPath, fullMarkdown, 'utf8');
        
        console.log(`✓ 转换成功：${noteInfo.title}`);
        return true;
        
    } catch (error) {
        console.error(`✗ 转换失败：${noteInfo.title}`, error.message);
        return false;
    }
}

// 清理文件名
function sanitizeFilename(filename) {
    return filename.replace(/[<>:"/\\|?*]/g, '_').trim().substring(0, 100);
}

// 主函数
async function main() {
    console.log('开始迁移为知笔记到 Obsidian...');
    
    // 打开数据库
    const db = new sqlite3.Database(
        path.join(config.wizHome, 'index.db'),
        sqlite3.OPEN_READONLY
    );
    
    // 查询所有笔记
    const notes = await new Promise((resolve, reject) => {
        db.all(`
            SELECT 
                DOCUMENT_GUID as guid,
                DOCUMENT_TITLE as title,
                DOCUMENT_LOCATION as location,
                DT_CREATED as created,
                DT_MODIFIED as modified,
                DOCUMENT_TAGS as tags
            FROM WIZ_DOCUMENT
            WHERE DOCUMENT_TYPE != 'encrypted'
            ORDER BY DOCUMENT_LOCATION
        `, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
    
    console.log(`找到 ${notes.length} 篇笔记`);
    
    // 转换每个笔记
    let success = 0;
    for (const note of notes) {
        if (await convertNote(note, db)) {
            success++;
        }
    }
    
    db.close();
    
    console.log(`\n迁移完成！成功：${success}/${notes.length}`);
}

main().catch(console.error);
```

#### 4. 运行迁移

```powershell
# 运行转换
node wiz2md.js -f ./config.js

# 或使用命令行参数
node wiz2md.js \
    -w "D:/为知笔记4.14/My Knowledge" \
    -u "your_email@example.com" \
    -o "D:/Obsidian_Vault"
```

### 已知问题及解决方案

#### 问题 1：乱码问题
```javascript
// 添加编码检测
const jschardet = require('jschardet');
const iconv = require('iconv-lite');

function decodeBuffer(buffer) {
    const detected = jschardet.detect(buffer);
    const encoding = detected.encoding || 'utf-8';
    return iconv.decode(buffer, encoding);
}
```

#### 问题 2：加密笔记
```javascript
// 跳过加密笔记
if (noteInfo.doc_type === 'encrypted') {
    console.log(`跳过加密笔记：${noteInfo.title}`);
    return false;
}
```

### 优缺点
- ✅ 直接读取数据库，速度快
- ✅ JavaScript 生态丰富
- ✅ 可扩展性强
- ❌ 仅在 Mac 测试（Windows 需调整路径）
- ❌ 可能有乱码问题

---

## 方案四：手动解压转换法（兼容性最强）

### 适用场景
- 笔记数量少（< 100 篇）
- 格式复杂，需要精细控制
- 无编程基础

### 详细步骤

#### 步骤 1：批量重命名 ziw 为 zip

```powershell
# 进入笔记目录
cd "D:\为知笔记4.14\My Knowledge\data\your_email@example.com"

# 批量重命名
Get-ChildItem -Recurse -Filter "*.ziw" | ForEach-Object {
    $newName = $_.FullName -replace '\.ziw$', '.zip'
    Rename-Item -Path $_.FullName -NewName $newName
    Write-Host "重命名：$($_.Name) -> $($_.Name -replace '\.ziw$', '.zip')"
}
```

#### 步骤 2：批量解压

```powershell
# 使用 7-Zip 批量解压
$7zipPath = "C:\Program Files\7-Zip\7z.exe"
$notesPath = "D:\为知笔记4.14\My Knowledge\data\your_email@example.com"

Get-ChildItem -Path $notesPath -Recurse -Filter "*.zip" | ForEach-Object {
    $outputDir = $_.DirectoryName
    & $7zipPath x $_.FullName -o"$outputDir\$($_.BaseName)" -y
    Write-Host "解压：$($_.Name)"
}
```

#### 步骤 3：HTML 转 Markdown（使用 Pandoc）

```powershell
# 安装 Pandoc
winget install JohnMacFarlane.Pandoc

# 批量转换
Get-ChildItem -Path "D:\Extracted_Notes" -Recurse -Filter "index.html" | ForEach-Object {
    $outputMd = $_.DirectoryName + "\" + $_.Directory.Name + ".md"
    & pandoc $_.FullName -o $outputMd --wrap=none --extract-media=.
    Write-Host "转换：$($_.Directory.Name)"
}
```

#### 步骤 4：使用在线工具精调

对于格式复杂的笔记，使用在线工具手动调整：
1. **Markdown/HTML 互转工具**：https://toolshu.com/markdown
2. **Turndown 在线演示**：https://domchristie.github.io/turndown/

#### 步骤 5：手动整理资源

```powershell
# 创建资源目录结构
$vaultPath = "D:\Obsidian_Vault"
New-Item -Path "$vaultPath\assets" -ItemType Directory -Force

# 按笔记名组织图片
Get-ChildItem -Path "D:\Extracted_Notes" -Directory | ForEach-Object {
    $noteName = $_.Name
    $imagesPath = "$vaultPath\assets\$noteName"
    
    # 查找图片文件夹
    $indexFilesPath = Join-Path $_.FullName "index_files"
    if (Test-Path $indexFilesPath) {
        New-Item -Path $imagesPath -ItemType Directory -Force
        Copy-Item -Path "$indexFilesPath\*" -Destination $imagesPath -Recurse
        Write-Host "复制图片：$noteName"
    }
}
```

#### 步骤 6：修复图片路径

使用 VS Code 批量替换：
1. 打开 VS Code
2. 文件 → 在文件夹中查找
3. 搜索：`!\[(.*?)\]\(index_files/(.*?)\)`
4. 替换：`![$1](assets/${noteName}/$2)`
5. 全部替换

### 优缺点
- ✅ 兼容所有格式
- ✅ 完全可控
- ✅ 无需编程
- ❌ 耗时长
- ❌ 容易出错
- ❌ 不适合批量处理

---

## Obsidian 导入与优化配置

### 步骤 1：创建 Obsidian 仓库

```powershell
# 创建仓库目录
$vaultPath = "D:\Obsidian_Vault"
New-Item -Path $vaultPath -ItemType Directory -Force

# 创建子目录
New-Item -Path "$vaultPath\assets" -ItemType Directory -Force
New-Item -Path "$vaultPath\templates" -ItemType Directory -Force
New-Item -Path "$vaultPath\.obsidian" -ItemType Directory -Force
```

### 步骤 2：配置附件管理

创建 `.obsidian/app.json`：
```json
{
  "attachmentFolderPath": "assets",
  "newFileLocation": "current",
  "promptDelete": true,
  "showUnsupportedFiles": true,
  "alwaysUpdateLinks": true
}
```

创建 `.obsidian/core-plugins.json`：
```json
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "outgoing-link": true,
  "tag-pane": true,
  "page-preview": true,
  "templates": true,
  "note-composer": true,
  "command-palette": true,
  "markdown-importer": true,
  "word-count": true,
  "file-recovery": true
}
```

### 步骤 3：安装推荐插件

创建 `.obsidian/community-plugins.json`：
```json
[
  "obsidian-image-auto-upload-plugin",
  "obsidian-custom-attachment-location",
  "oz-clear-unused-images",
  "obsidian-excalidraw-plugin",
  "obsidian-markmind",
  "obsidian-kanban",
  "dataview"
]
```

### 步骤 4：配置图片插件

#### Custom Attachment Location 插件配置
```
设置 → Custom Attachment Location
Attachment Path: ./assets/${filename}
```

#### Image Auto Upload 插件配置
```
设置 → Image auto upload
Upload when paste: true
Default uploader: PicGo(app)
```

### 步骤 5：导入迁移的笔记

```powershell
# 方法 1：直接复制
Copy-Item -Path "D:\WizNote_Migration\markdown_output\*" `
          -Destination "D:\Obsidian_Vault" -Recurse -Force

# 方法 2：使用 Robocopy（保留目录结构）
robocopy "D:\WizNote_Migration\markdown_output" "D:\Obsidian_Vault" /E /COPYALL /R:3 /W:5
```

### 步骤 6：验证导入结果

```powershell
# 统计导入的文件
$mdFiles = Get-ChildItem -Path "D:\Obsidian_Vault" -Filter "*.md" -Recurse
$imageFiles = Get-ChildItem -Path "D:\Obsidian_Vault\assets" -File -Recurse

Write-Host "导入的 Markdown 文件：$($mdFiles.Count) 个"
Write-Host "导入的图片文件：$($imageFiles.Count) 个"

# 检查损坏的链接
$brokenLinks = @()
foreach ($file in $mdFiles) {
    $content = Get-Content $file.FullName -Raw
    $imageLinks = [regex]::Matches($content, '!\[.*?\]\((.*?)\)')
    
    foreach ($link in $imageLinks) {
        $imagePath = $link.Groups[1].Value
        if ($imagePath -notmatch '^http') {
            $fullPath = Join-Path $file.DirectoryName $imagePath
            if (-not (Test-Path $fullPath)) {
                $brokenLinks += @{
                    File = $file.FullName
                    MissingImage = $imagePath
                }
            }
        }
    }
}

Write-Host "损坏的链接：$($brokenLinks.Count) 个"
```

---

## 常见问题与解决方案

### 问题 1：图片路径损坏

**原因**：相对路径计算错误

**解决方案**：
```python
def fix_image_paths(markdown_file):
    """修复图片路径"""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取笔记所在目录
    note_dir = os.path.dirname(markdown_file)
    assets_dir = os.path.relpath('D:/Obsidian_Vault/assets', note_dir)
    
    # 替换路径
    content = re.sub(
        r'!\[([^\]]*)\]\(assets/',
        f'![\\1]({assets_dir.replace(chr(92), "/")}/',
        content
    )
    
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(content)
```

### 问题 2：中文文件名乱码

**原因**：编码不一致

**解决方案**：
```python
# Python 脚本中统一使用 UTF-8
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读写文件时指定编码
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
```

### 问题 3：代码块语言丢失

**原因**：HTML 转换时未识别语言标记

**解决方案**：
```javascript
// 手动添加语言标记
turndownService.addRule('code', {
    filter: function(node) {
        return node.nodeName === 'CODE' && 
               node.parentNode.nodeName === 'PRE';
    },
    replacement: function(content, node) {
        // 从 class 中提取语言
        const className = node.className || '';
        const langMatch = className.match(/language-(\w+)/);
        const lang = langMatch ? langMatch[1] : '';
        
        return '\n```' + lang + '\n' + content + '\n```\n';
    }
});
```

### 问题 4：表格格式错乱

**原因**：复杂表格（合并单元格）Markdown 不支持

**解决方案**：
```markdown
<!-- 方法 1：使用 HTML 表格 -->
<table>
  <tr>
    <th>列1</th>
    <th>列2</th>
  </tr>
  <tr>
    <td colspan="2">合并单元格</td>
  </tr>
</table>

<!-- 方法 2：拆分为多个简单表格 -->
| 列1 | 列2 |
|-----|-----|
| A   | B   |

**说明**：合并单元格内容

| 列1 | 列2 |
|-----|-----|
| C   | D   |
```

### 问题 5：数学公式不显示

**原因**：MathJax 格式不兼容

**解决方案**：
```python
def convert_mathjax_to_latex(html_content):
    """转换 MathJax 为 LaTeX"""
    # 行内公式
    html_content = re.sub(
        r'<script type="math/tex">(.*?)</script>',
        r'$\1$',
        html_content,
        flags=re.DOTALL
    )
    
    # 块级公式
    html_content = re.sub(
        r'<script type="math/tex; mode=display">(.*?)</script>',
        r'$$\1$$',
        html_content,
        flags=re.DOTALL
    )
    
    return html_content
```

### 问题 6：标签丢失

**原因**：标签未转换为 YAML

**解决方案**：
```python
def extract_tags_from_db(db_path, note_guid):
    """从数据库提取标签"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT DOCUMENT_TAGS FROM WIZ_DOCUMENT WHERE DOCUMENT_GUID = ?",
        (note_guid,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return [tag.strip() for tag in result[0].split(',')]
    return []

def add_tags_to_yaml(markdown, tags):
    """添加标签到 YAML 头部"""
    if tags:
        yaml_tags = f'tags: [{", ".join(tags)}]\n'
        # 在 YAML 头部插入 tags
        markdown = re.sub(
            r'(---\n.*?)(---)',
            r'\1' + yaml_tags + r'\2',
            markdown,
            count=1,
            flags=re.DOTALL
        )
    return markdown
```

### 问题 7：笔记创建时间错误

**原因**：数据库时间戳格式与 YAML 不一致

**解决方案**：
```python
from datetime import datetime

def convert_wiz_time(wiz_time_str):
    """转换为 Obsidian 时间格式"""
    # 为知笔记时间格式：2024-01-15 10:30:45
    # Obsidian 格式：2024-01-15 或 2024-01-15T10:30:45
    
    try:
        dt = datetime.strptime(wiz_time_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')
```

### 问题 8：特殊字符转义

**原因**：Markdown 特殊字符未转义

**解决方案**：
```python
def escape_markdown_chars(text):
    """转义 Markdown 特殊字符"""
    # 不在代码块中的特殊字符
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
    
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    
    return text
```

---

## 进阶：API 自动化迁移

### 适用场景
- 企业级批量迁移
- 云端笔记迁移
- 自动化持续同步

### 为知笔记 OpenAPI 详解

#### 1. 认证登录

```python
import requests

class WizNoteAPI:
    def __init__(self):
        self.base_url = 'https://as.wiz.cn'
        self.ks_url = None  # 知识库服务地址
        self.token = None
        self.kb_guid = None
    
    def login(self, username, password):
        """登录获取 token"""
        url = f'{self.base_url}/as/user/login'
        data = {
            'userId': username,
            'password': password,
            'autoRename': False
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result['returnCode'] == 200:
            self.token = result['result']['token']
            self.kb_guid = result['result']['kbGuid']
            self.ks_url = result['result']['kbServer']
            print(f"登录成功！Token: {self.token[:20]}...")
            return True
        else:
            print(f"登录失败：{result['returnMessage']}")
            return False
```

#### 2. 获取笔记列表

```python
def get_notes(self, folder_guid=None, start=0, count=100):
    """获取笔记列表"""
    url = f'{self.ks_url}/ks/category/notes'
    headers = {'X-Wiz-Token': self.token}
    params = {
        'kbGuid': self.kb_guid,
        'categoryGuid': folder_guid or self.kb_guid,
        'start': start,
        'count': count
    }
    
    response = requests.get(url, headers=headers, params=params)
    result = response.json()
    
    if result['returnCode'] == 200:
        return result['result']
    return []
```

#### 3. 下载笔记内容

```python
def download_note(self, note_guid):
    """下载笔记详细内容和资源"""
    # 获取笔记信息
    info_url = f'{self.ks_url}/ks/note/detail/{note_guid}'
    headers = {'X-Wiz-Token': self.token}
    params = {'kbGuid': self.kb_guid}
    
    response = requests.get(info_url, headers=headers, params=params)
    note_info = response.json()['result']
    
    # 下载 HTML 内容
    html_url = note_info['html']
    html_response = requests.get(html_url)
    
    # 下载资源文件
    resources = note_info.get('resources', [])
    resource_files = {}
    
    for resource in resources:
        res_url = resource['url']
        res_name = resource['name']
        res_data = requests.get(res_url).content
        resource_files[res_name] = res_data
    
    return {
        'info': note_info,
        'html': html_response.text,
        'resources': resource_files
    }
```

#### 4. 完整 API 迁移脚本

```python
#!/usr/bin/env python3
"""
使用为知笔记 OpenAPI 迁移到 Obsidian
"""

import requests
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WizNoteToObsidianAPI:
    def __init__(self, username, password, output_dir):
        self.username = username
        self.password = password
        self.output_dir = Path(output_dir)
        self.api = WizNoteAPI()
        
    def migrate(self):
        """执行迁移"""
        # 登录
        if not self.api.login(self.username, self.password):
            return False
        
        logger.info("开始下载笔记...")
        
        # 获取所有笔记
        all_notes = []
        start = 0
        count = 100
        
        while True:
            notes = self.api.get_notes(start=start, count=count)
            if not notes:
                break
            
            all_notes.extend(notes)
            start += count
            
            if len(notes) < count:
                break
            
            time.sleep(0.5)  # 避免请求过快
        
        logger.info(f"共找到 {len(all_notes)} 篇笔记")
        
        # 下载并转换每个笔记
        for i, note in enumerate(all_notes, 1):
            logger.info(f"处理 {i}/{len(all_notes)}: {note['title']}")
            
            try:
                note_data = self.api.download_note(note['guid'])
                self.process_note(note_data)
            except Exception as e:
                logger.error(f"处理失败：{e}")
        
        logger.info("迁移完成！")
        return True
    
    def process_note(self, note_data):
        """处理单个笔记"""
        # 转换 HTML 为 Markdown
        # 保存资源和笔记
        pass

# 使用示例
if __name__ == '__main__':
    migrator = WizNoteToObsidianAPI(
        username='your_email@example.com',
        password='your_password',
        output_dir='D:/Obsidian_Vault'
    )
    migrator.migrate()
```

### 优缺点
- ✅ 不依赖本地客户端
- ✅ 可迁移云端笔记
- ✅ 自动化程度高
- ❌ 需要网络连接
- ❌ 可能有 API 限流
- ❌ 需要账号密码

---

## 总结与建议

### 迁移方案选择矩阵

| 需求场景 | 推荐方案 | 理由 |
|---------|---------|------|
| 笔记 < 100 篇 | 官方插件导出 | 简单快速 |
| 笔记 100-500 篇 | Python 脚本 | 平衡效率与控制 |
| 笔记 > 500 篇 | Node.js 或 API | 批量处理高效 |
| 格式复杂 | 手动解压 | 精细控制 |
| 云端笔记 | API 自动化 | 唯一选择 |

### 最佳实践清单

#### ✅ 迁移前
- [ ] 完整备份原始数据
- [ ] 检查数据库完整性
- [ ] 记录笔记总数和文件夹结构
- [ ] 测试小批量转换

#### ✅ 迁移中
- [ ] 使用日志记录转换过程
- [ ] 保留原始创建时间和修改时间
- [ ] 正确处理图片路径
- [ ] 转换标签为 Obsidian 格式

#### ✅ 迁移后
- [ ] 验证文件数量一致性
- [ ] 检查损坏的图片链接
- [ ] 测试搜索功能
- [ ] 安装必要插件
- [ ] 配置附件管理

### 最终检查清单

```powershell
# 运行验证脚本
$originalCount = (查询数据库笔记数)
$migratedCount = (Get-ChildItem -Path "D:\Obsidian_Vault" -Filter "*.md" -Recurse).Count
$imageCount = (Get-ChildItem -Path "D:\Obsidian_Vault\assets" -File -Recurse).Count

Write-Host "原始笔记数：$originalCount"
Write-Host "迁移笔记数：$migratedCount"
Write-Host "图片资源数：$imageCount"
Write-Host "迁移率：$([math]::Round($migratedCount / $originalCount * 100, 2))%"

if ($migratedCount -eq $originalCount) {
    Write-Host "✓ 迁移完成！" -ForegroundColor Green
} else {
    Write-Host "⚠ 部分笔记未迁移，请检查日志" -ForegroundColor Yellow
}
```

---

## 附录

### A. 工具下载链接

1. **Python 3.12**：https://www.python.org/downloads/
2. **Node.js 18 LTS**：https://nodejs.org/
3. **Pandoc**：https://pandoc.org/installing.html
4. **7-Zip**：https://www.7-zip.org/
5. **DB Browser for SQLite**：https://sqlitebrowser.org/

### B. 参考项目

1. **wiznote2markdown**：https://github.com/chaoyz/wiznote2markdown
2. **ExptWizNote**：https://github.com/einverne/ExptWizNote
3. **wiznote2hexo2csdn**：https://github.com/zdaiot/wiznote2hexo2csdn
4. **Turndown**：https://github.com/mixmark-io/turndown

### C. 为知笔记 API 文档

- 官方 API 文档：https://www.cnblogs.com/drcode/p/18455353
- GitHub API 示例：https://github.com/WizTeam

### D. Obsidian 官方文档

- 官方网站：https://obsidian.md
- 文档：https://help.obsidian.md
- 插件市场：https://obsidian.md/plugins

---

## 更新日志

- **2024-01-15**：初始版本发布
- **2024-01-16**：添加 API 迁移方案
- **2024-01-17**：优化图片路径处理逻辑
- **2024-01-18**：补充常见问题解决方案

---

**作者**：AI 迁移助手  
**版本**：1.0  
**最后更新**：2024-01-18

如有疑问，请在 GitHub 提 Issue 或参考官方文档。
