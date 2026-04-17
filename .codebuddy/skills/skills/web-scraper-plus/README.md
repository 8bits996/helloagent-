# 增强网页爬取器 (web-scraper-plus)

这是一个增强版的网页爬取技能，支持网页内容提取、截图功能和iWiki知识库内容沉淀。

## 功能特性

- 🌐 网页内容爬取和结构化提取
- 📷 页面截图功能（全页面截图）
- 📄 MD和Word文档生成
- 📚 iWiki知识库内容上传
- 🎯 智能内容解析和格式化

## 使用方法

```bash
# 基本用法
node index.js <url> [格式: word|md] [文件名] [截图: true|false] [iwiki: true|false]

# 示例1: 爬取网页并生成MD文档，截图并上传到iWiki
node index.js https://example.com md my-report true true

# 示例2: 爬取网页并生成Word文档，仅截图不上传
node index.js https://csig.lexiangla.com/pages/49dbff8abd494c298e7a7d755ead2faf word report true false
```

## 技术栈

- Playwright: 网页自动化和截图
- Cheerio: HTML内容解析
- Docx: Word文档生成
- Axios: HTTP请求
- iWiki API: 知识库内容上传

## 安装依赖

```bash
npm install
```

## 注意事项

1. 需要安装Playwright浏览器：
   ```bash
   npx playwright install
   ```

2. 确保iWiki API访问权限已配置

3. 对于复杂的网页，可能需要调整爬取策略

## 贡献

欢迎提交Issue和Pull Request来改进这个技能！