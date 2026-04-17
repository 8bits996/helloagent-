# 为知笔记到 Obsidian 迁移工具包

## 📦 文件清单

```
./
├── 为知笔记到Obsidian迁移方案.md    # 完整迁移方案文档（必读）
├── README_迁移工具.md               # 使用指南
├── wiz2obsidian.py                  # Python 迁移脚本
├── validate_migration.py            # 验证脚本
└── run_migration.bat                # Windows 快速启动脚本
```

## 🚀 快速使用

### Windows 用户

双击运行 `run_migration.bat`，按提示输入路径即可。

### 命令行用户

```powershell
# 1. 安装依赖
pip install beautifulsoup4 lxml html2text

# 2. 运行迁移
python wiz2obsidian.py --wiz "D:\为知笔记4.14\My Knowledge" --output "D:\Obsidian_Vault"

# 3. 验证结果
python validate_migration.py --wiz "D:\为知笔记4.14\My Knowledge" --obsidian "D:\Obsidian_Vault"
```

## 📖 详细文档

完整的迁移方案、技术原理、常见问题解决方案请查看：

**[为知笔记到Obsidian迁移方案.md](./为知笔记到Obsidian迁移方案.md)**

## ⚠️ 重要提示

1. **备份原始数据**：迁移前务必备份为知笔记数据
2. **同步到本地**：确保所有笔记已同步到本地
3. **检查加密笔记**：加密笔记需要先解密才能迁移

## 📊 迁移统计

运行后会生成：
- `migration.log`：详细迁移日志
- `migration_report.json`：验证报告（JSON 格式）

## 🔧 系统要求

- Python 3.9+
- 内存：建议 4GB+
- 磁盘空间：至少为笔记数据的 2 倍

## 📝 支持的格式

| 格式 | 支持程度 | 说明 |
|------|---------|------|
| HTML 笔记 | ✅ 完全支持 | 自动转换为 Markdown |
| Markdown 笔记 | ✅ 完全支持 | 保留原始格式 |
| 图片 | ✅ 完全支持 | PNG/JPG/GIF/SVG/WebP |
| 代码块 | ✅ 完全支持 | 自动识别语言 |
| 表格 | ⚠️ 部分支持 | 不支持合并单元格 |
| 数学公式 | ⚠️ 部分支持 | LaTeX 格式 |
| 加密笔记 | ❌ 不支持 | 需要先解密 |

## 💡 最佳实践

1. **小批量测试**：先用少量笔记测试
2. **保留元数据**：迁移脚本会保留创建时间、标签等
3. **验证结果**：迁移后运行验证脚本
4. **优化配置**：在 Obsidian 中配置插件和附件路径

## 🆘 常见问题

### Q: 提示"ziw 文件不存在"
**A**: 在为知笔记客户端中同步笔记到本地

### Q: 图片不显示
**A**: 运行验证脚本检查损坏的链接

### Q: 转换失败
**A**: 查看 `migration.log` 了解详细错误信息

## 📚 相关资源

- [Obsidian 官方文档](https://help.obsidian.md)
- [为知笔记 API 文档](https://www.cnblogs.com/drcode/p/18455353)
- [GitHub 项目](https://github.com/chaoyz/wiznote2markdown)

---

**版本**：1.0  
**作者**：AI 迁移助手  
**更新日期**：2024-01-18
