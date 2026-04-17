# 为知笔记到 Obsidian 迁移工具使用指南

## 快速开始

### 1. 安装依赖

```powershell
# 安装 Python 依赖
pip install beautifulsoup4 lxml html2text
```

### 2. 运行迁移

```powershell
# 基本用法
python wiz2obsidian.py --wiz "D:\为知笔记4.14\My Knowledge" --output "D:\Obsidian_Vault"

# 只迁移特定文件夹
python wiz2obsidian.py --wiz "D:\为知笔记4.14\My Knowledge" --output "D:\Obsidian_Vault" --folder "/我的笔记/技术文档"
```

### 3. 验证结果

```powershell
python validate_migration.py --wiz "D:\为知笔记4.14\My Knowledge" --obsidian "D:\Obsidian_Vault"
```

## 详细说明

### 迁移脚本参数

- `--wiz`: 为知笔记数据目录（必需）
  - 通常在：`D:\为知笔记4.14\My Knowledge`
  - 或：`C:\Users\你的用户名\Documents\My Knowledge`

- `--output`: Obsidian 输出目录（必需）
  - 可以是已存在的 Obsidian 仓库
  - 或新建的空目录

- `--folder`: 只迁移指定文件夹（可选）
  - 使用为知笔记中的完整路径
  - 例如：`/我的笔记/技术文档`

### 迁移内容

✓ 笔记内容（HTML → Markdown）  
✓ 图片资源（自动提取和转换路径）  
✓ 笔记元数据（标题、创建时间、修改时间、标签）  
✓ 文件夹结构  

### 不支持的内容

✗ 加密笔记（需要先解密）  
✗ 思维导图（需要手动处理）  
✗ 表格合并单元格（Markdown 不支持）  

## 常见问题

### 1. 提示"缺少依赖库"

**解决方案**：
```powershell
pip install beautifulsoup4 lxml html2text
```

### 2. 提示"ziw 文件不存在"

**原因**：笔记未同步到本地

**解决方案**：
1. 打开为知笔记客户端
2. 右键点击文件夹 → 同步
3. 等待同步完成

### 3. 部分笔记转换失败

**检查方法**：
1. 查看 `migration.log` 文件
2. 运行验证脚本：`python validate_migration.py`
3. 查看报告中的"失败的笔记"列表

**常见原因**：
- 文件损坏
- 编码问题
- 特殊格式不支持

### 4. 图片不显示

**解决方案**：
```powershell
# 检查损坏的链接
python validate_migration.py --wiz "D:\为知笔记4.14\My Knowledge" --obsidian "D:\Obsidian_Vault"

# 查看报告中的 broken_links 部分
```

### 5. 中文乱码

**解决方案**：
- 脚本已使用 UTF-8 编码
- 如果仍有乱码，可能是源文件编码问题
- 手动打开 ziw 文件检查原始编码

## 高级用法

### 自定义转换规则

编辑 `wiz2obsidian.py` 中的 `html_to_markdown` 方法：

```python
# 自定义代码块处理
def html_to_markdown(self, html_content, note_title):
    # 添加自定义逻辑
    # ...
```

### 批量重命名

```powershell
# 批量重命名笔记文件
Get-ChildItem -Path "D:\Obsidian_Vault" -Filter "*.md" -Recurse | ForEach-Object {
    $newName = $_.Name -replace '旧前缀_', '新前缀_'
    Rename-Item -Path $_.FullName -NewName $newName
}
```

### 修复图片路径

```powershell
# 使用 VS Code 批量替换
# 搜索：assets/([^/]+)/
# 替换：assets/新文件夹名/$1/
```

## 迁移后配置

### 1. 在 Obsidian 中打开仓库

1. 打开 Obsidian
2. 点击"打开文件夹作为仓库"
3. 选择迁移输出目录

### 2. 配置附件路径

设置 → 文件与链接：
- 内部链接类型：基于当前笔记的相对路径
- 附件默认存放路径：当前文件所在文件夹下指定的子文件夹中
- 子文件夹名称：assets

### 3. 安装推荐插件

- **Image auto upload plugin**: 自动上传图片到图床
- **Custom Attachment Location**: 自定义附件位置
- **Dataview**: 数据查询和展示
- **Ozan's Image in Editor Plugin**: 编辑器中显示图片

## 性能优化

### 大量笔记优化

如果笔记数量 > 1000：

```python
# 分批处理
migrator.migrate(folder_filter='/文件夹A')
migrator.migrate(folder_filter='/文件夹B')
migrator.migrate(folder_filter='/文件夹C')
```

### 减少日志输出

```python
# 修改日志级别
import logging
logging.getLogger().setLevel(logging.WARNING)
```

## 备份与恢复

### 迁移前备份

```powershell
# 备份为知笔记数据
Copy-Item -Path "D:\为知笔记4.14\My Knowledge" -Destination "D:\Backup\My Knowledge" -Recurse

# 备份数据库
Copy-Item -Path "D:\为知笔记4.14\My Knowledge\index.db" -Destination "D:\Backup\index_$(Get-Date -Format 'yyyyMMdd').db"
```

### 回滚迁移

```powershell
# 删除迁移结果
Remove-Item -Path "D:\Obsidian_Vault" -Recurse -Force

# 重新迁移
python wiz2obsidian.py --wiz "D:\为知笔记4.14\My Knowledge" --output "D:\Obsidian_Vault"
```

## 技术支持

### 日志文件

- `migration.log`: 详细迁移日志
- `migration_report.json`: 验证报告

### 问题反馈

如遇到问题，请提供以下信息：
1. Python 版本：`python --version`
2. 依赖版本：`pip list | findstr beautifulsoup4`
3. 错误日志：`migration.log` 相关部分
4. 笔记数量：验证脚本输出的"源笔记"数量

## 相关资源

- [完整迁移方案文档](./为知笔记到Obsidian迁移方案.md)
- [Obsidian 官方文档](https://help.obsidian.md)
- [为知笔记 API 文档](https://www.cnblogs.com/drcode/p/18455353)

---

**版本**：1.0  
**更新日期**：2024-01-18
