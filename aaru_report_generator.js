const { Document, Packer, Paragraph, TextRun, HeadingLevel, Alignment, ImageRun } = require('docx');
const fs = require('fs');

// 创建文档
const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // 标题
            new Paragraph({
                text: "Aaru AI 产品竞品调研报告",
                heading: HeadingLevel.HEADING_1,
                alignment: Alignment.CENTER,
                spacing: {
                    after: 500,
                },
            }),
            new Paragraph({
                text: "arianewang",
                alignment: Alignment.CENTER,
                spacing: {
                    after: 400,
                },
            }),
            new Paragraph({
                text: "01/15 更新",
                alignment: Alignment.RIGHT,
                spacing: {
                    after: 400,
                },
            }),
            
            // 报告内容
            new Paragraph({
                text: "# Aaru AI 产品竞品调研报告",
                heading: HeadingLevel.HEADING_1,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "## 1. 产品概述",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "Aaru AI 是一款基于人工智能技术的产品，专注于提供智能解决方案。本报告将对其主要竞品进行分析和比较。",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "## 2. 竞品分析",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "### 2.1 主要竞品",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 100,
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- **竞品A**: 提供类似AI功能，但用户体验较差",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- **竞品B**: 功能全面，但价格较高",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- **竞品C**: 新兴产品，发展潜力大",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "### 2.2 功能对比",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 100,
                    after: 50,
                },
            }),
            new Paragraph({
                text: "| 功能 | Aaru AI | 竞品A | 竞品B | 竞品C |",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "|------|---------|-------|-------|-------|",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "| 核心功能 | ✅ | ✅ | ✅ | ✅ |",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "| 用户体验 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "| 价格定位 | 中等 | 低 | 高 | 中等 |",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "## 3. 市场定位",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "Aaru AI 在市场上定位为中高端AI产品，主要面向企业用户和开发者。其优势在于平衡的功能和价格。",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "## 4. 发展建议",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "基于竞品分析，建议 Aaru AI：",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- 继续优化用户体验",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- 保持价格竞争力",
                spacing: {
                    after: 50,
                },
            }),
            new Paragraph({
                text: "- 加强核心功能创新",
                spacing: {
                    after: 200,
                },
            }),
            
            // 图片部分（占位符）
            new Paragraph({
                text: "## 5. 产品截图",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "以下是 Aaru AI 及其主要竞品的产品截图：",
                spacing: {
                    after: 200,
                },
            }),
            
            // 图片1
            new Paragraph({
                children: [
                    new ImageRun({
                        data: fs.readFileSync('aaru_screenshot1.png'),
                        transformation: {
                            width: 400,
                            height: 300,
                        },
                    }),
                ],
                spacing: {
                    after: 100,
                },
            }),
            
            // 图片2
            new Paragraph({
                children: [
                    new ImageRun({
                        data: fs.readFileSync('competitor_a_screenshot.png'),
                        transformation: {
                            width: 400,
                            height: 300,
                        },
                    }),
                ],
                spacing: {
                    after: 100,
                },
            }),
            
            // 图片3
            new Paragraph({
                children: [
                    new ImageRun({
                        data: fs.readFileSync('competitor_b_screenshot.png'),
                        transformation: {
                            width: 400,
                            height: 300,
                        },
                    }),
                ],
                spacing: {
                    after: 100,
                },
            }),
            
            // 图片4
            new Paragraph({
                children: [
                    new ImageRun({
                        data: fs.readFileSync('competitor_c_screenshot.png'),
                        transformation: {
                            width: 400,
                            height: 300,
                        },
                    }),
                ],
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "---",
                alignment: Alignment.CENTER,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "报告生成时间：2026年1月27日",
                alignment: Alignment.CENTER,
            }),
        ]
    }]
});

// 生成 Word 文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('Aaru AI 产品竞品调研报告.docx', buffer);
    console.log('Word文档生成成功：Aaru AI 产品竞品调研报告.docx');
    
    // 这里可以添加生成 PDF 的代码
    // 由于需要 LibreOffice 或其他 PDF 转换工具，我们先只生成 Word 文档
    console.log('MD 文件内容已包含在文档中');
    
}).catch(err => {
    console.error('生成文档时出错：', err);
});