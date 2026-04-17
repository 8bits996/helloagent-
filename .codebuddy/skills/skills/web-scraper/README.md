# Web Scraper - 网页爬取与文档生成技能

这是一个用于爬取网页内容并生成多种格式文档的技能。

## 功能特性

- 🌐 爬取任意网页内容
- 📄 生成 Word 文档（.docx）
- 📝 生成 Markdown 文档（.md）
- 📑 支持生成 PDF 文档（.pdf）
- 📚 自动提取标题和内容结构
- 📋 生成目录和格式化内容
- 🎯 默认输出为 MD 格式

## 使用方法

### 基本用法

```bash
# 爬取网页并生成默认 MD 格式文档
node index.js https://example.com

# 爬取网页并生成 Word 文档
node index.js https://example.com word my-report

# 爬取网页并生成 Markdown 文档
node index.js https://example.com md my-report

# 爬取网页并生成 PDF 文档（功能开发中）
node index.js https://example.com pdf my-report
```

### 参数说明

- `url`: 必需 - 要爬取的网页 URL
- `format`: 可选 - 输出格式 (word, md, pdf)，默认为 md
- `outputFileName`: 可选 - 输出文件名，默认为 web-scraper-report

## 安装依赖

```bash
npm install
```

## 依赖项

- `docx`: 用于生成 Word 文档
- `axios`: 用于 HTTP 请求
- `playwright`: 用于网页爬取
- `cheerio`: 用于 HTML 解析

## 注意事项

- 需要网络连接才能正常工作
- 某些网站可能有反爬虫机制
- PDF 生成功能需要额外的 PDF 生成库支持
- 内容提取可能因网站结构而异

## 示例

```bash
# 爬取 Zendesk 报告
node index.js https://csig.lexiangla.com/pages/262e893577df4d8e8ec6a4b557c0a2e7?company_from=csig word zendesk-report

# 爬取云服务调研报告
node index.js https://csig.lexiangla.com/pages/435250abb95f41178b54ce421083ae9b?company_from=csig md cloud-service-report

# 爬取 ITSM 领导者 AI 能力调研报告
node index.js https://csig.lexiangla.com/pages/49dbff8abd494c298e7a7d755ead2faf?company_from=csig word itsm-ai-survey
```

## 技术实现

- 使用 Playwright 进行网页爬取
- 使用 Cheerio 进行 HTML 解析
- 使用 docx 库生成 Word 文档
- 自动提取标题和内容结构
- 支持多种输出格式

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个技能。