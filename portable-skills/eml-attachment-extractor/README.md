# EML 附件提取器

从 `.eml` 格式邮件文件中批量提取附件，带 **SHA256 内容哈希三级去重**。

典型场景：从 BOSS 直聘、猎聘等招聘平台邮件中批量提取候选人简历 PDF。

## 去重策略（三级）

| 级别 | 条件 | 行为 |
|------|------|------|
| 1 | 文件名相同 + SHA256 相同 | `[跳过]` 完全重复 |
| 2 | 文件名相同 + SHA256 不同 | `[重命名]` 保存为 `name(2).ext` |
| 3 | 文件名不同 + SHA256 相同 | `[内容重复]` 跳过并提示来源 |

## 使用方法

```bash
# 基础用法：提取所有附件，智能去重
python extract_eml_attachments.py "<源目录>" "<目标目录>"

# 只提取 PDF
python extract_eml_attachments.py "<源目录>" "<目标目录>" --ext .pdf

# 预览模式（不实际写入）
python extract_eml_attachments.py "<源目录>" "<目标目录>" --dry-run

# 覆盖已存在文件（跳过去重）
python extract_eml_attachments.py "<源目录>" "<目标目录>" --overwrite

# 日志写入文件（解决 Windows 中文乱码）
python extract_eml_attachments.py "<源目录>" "<目标目录>" --log output.log
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `source_dir` | 包含 .eml 文件的源目录（必填） |
| `target_dir` | 附件保存的目标目录（必填） |
| `--overwrite` | 覆盖已存在的文件（默认智能去重） |
| `--ext FILTER` | 只提取指定扩展名的附件，可多个 |
| `--log LOG_FILE` | 将日志写入指定文件 |
| `--dry-run` | 仅预览，不实际提取 |

## 依赖

仅使用 Python 标准库（`email`、`hashlib`、`argparse`、`glob`），无需安装第三方包。

## 使用记录

- **2026-03-22**: 从 TheMatrix 项目提炼，用于 `简历20260322 新简历`（87个 eml → 84个 PDF，3个同名重复自动跳过；王先生实际2人：11年+20年，非全重复）
