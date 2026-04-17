const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel } = require('docx');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const cheerio = require('cheerio');

class WebScraper {
    constructor() {
        this.content = {
            title: '',
            author: '',
            updateDate: new Date().toLocaleDateString('zh-CN'),
            sections: []
        };
    }

    async scrapePage(url) {
        console.log(`正在爬取页面: ${url}`);
        
        const browser = await chromium.launch();
        const page = await browser.newPage();
        
        try {
            await page.goto(url, { waitUntil: 'networkidle' });
            
            // 获取页面内容
            const content = await page.content();
            const $ = cheerio.load(content);
            
            // 提取标题
            const title = $('h1').first().text() || $('title').text();
            this.content.title = title || '未找到标题';
            
            // 提取作者信息（如果存在）
            this.content.author = this.extractAuthor($);
            
            // 提取主要内容和结构
            this.extractSections($);
            
            console.log(`成功爬取页面: ${title}`);
            
        } catch (error) {
            console.error('爬取页面时出错:', error);
            throw error;
        } finally {
            await browser.close();
        }
    }

    extractAuthor($) {
        // 尝试从常见位置提取作者信息
        const authorSelectors = [
            '.author', '.byline', '.writer', '.editor',
            '.meta .author', '.post-author', '.article-author',
            'meta[name="author"]', 'meta[property="author"]'
        ];
        
        for (const selector of authorSelectors) {
            const author = $(selector).text().trim();
            if (author) return author;
        }
        
        return '未知作者';
    }

    extractSections($) {
        // 尝试提取标题和内容
        const sectionSelectors = [
            'h1, h2, h3, h4, h5, h6',
            'section', 'article', '.section', '.content',
            '.article-content', '.post-content', '.main-content'
        ];
        
        let currentSection = null;
        
        // 先尝试提取所有标题和内容
        $(sectionSelectors.join(', ')).each((index, element) => {
            const tag = element.tagName.toLowerCase();
            const text = $(element).text().trim();
            
            if (text && ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) {
                // 如果是标题，创建新章节
                if (currentSection) {
                    this.content.sections.push(currentSection);
                }
                
                currentSection = {
                    heading: text,
                    content: ''
                };
            } else if (text && currentSection) {
                // 如果是内容，添加到当前章节
                currentSection.content += text + '\n\n';
            }
        });
        
        // 添加最后一个章节
        if (currentSection) {
            this.content.sections.push(currentSection);
        }
        
        // 如果没有找到结构化内容，使用整个页面内容
        if (this.content.sections.length === 0) {
            const fullContent = $('body').text().trim();
            this.content.sections.push({
                heading: '全文内容',
                content: fullContent
            });
        }
    }

    generateWordReport(outputPath) {
        const doc = new Document({
            sections: [{
                properties: {
                    title: this.content.title,
                    subject: "网页爬取报告",
                    creator: this.content.author,
                    keywords: "网页爬取, 文档生成, 报告",
                    lastModifiedBy: this.content.author,
                    modified: new Date(),
                    created: new Date(),
                },
                children: [
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: this.content.title,
                                bold: true,
                                size: 32,
                                font: "宋体",
                            }),
                        ],
                        alignment: "center",
                        spacing: {
                            after: 200,
                        },
                    }),
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: `作者：${this.content.author}`,
                                font: "宋体",
                            }),
                            new TextRun({
                                text: " | ",
                                font: "宋体",
                            }),
                            new TextRun({
                                text: `更新日期：${this.content.updateDate}`,
                                font: "宋体",
                            }),
                        ],
                        alignment: "center",
                        spacing: {
                            after: 200,
                        },
                    }),
                    
                    // 目录
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "目录",
                                bold: true,
                                size: 24,
                                font: "宋体",
                            }),
                        ],
                        spacing: {
                            after: 100,
                        },
                    }),
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: this.content.sections.map((section, index) => 
                                    `${section.heading} ........................................................................................................................................................................... ${index + 1}`
                                ).join('\n'),
                                font: "宋体",
                            }),
                        ],
                        spacing: {
                            after: 200,
                        },
                    }),
                    
                    // 正文内容
                    ...this.content.sections.map((section, index) => [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: section.heading,
                                    bold: true,
                                    size: 24,
                                    font: "宋体",
                                }),
                            ],
                            spacing: {
                                after: 100,
                            },
                        }),
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: section.content,
                                    font: "宋体",
                                    size: 20,
                                }),
                            ],
                            spacing: {
                                after: 200,
                            },
                        }),
                    ]).flat(),
                    
                    // 结尾
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "© " + new Date().getFullYear() + " 网页爬取报告",
                                font: "宋体",
                                size: 16,
                            }),
                        ],
                        alignment: "center",
                        spacing: {
                            after: 100,
                        },
                    }),
                ]
            }]
        });

        const buffer = Packer.toBuffer(doc);
        fs.writeFileSync(outputPath, buffer);
        console.log(`Word 文档已生成：${outputPath}`);
    }

    generateMDReport(outputPath) {
        let mdContent = `# ${this.content.title}\n\n`;
        mdContent += `作者：${this.content.author} | 更新日期：${this.content.updateDate}\n\n`;
        mdContent += `---\n\n`;
        
        this.content.sections.forEach((section) => {
            mdContent += `## ${section.heading}\n\n`;
            mdContent += `${section.content}\n\n`;
        });
        
        fs.writeFileSync(outputPath, mdContent);
        console.log(`MD 文档已生成：${outputPath}`);
    }

    async generatePDFReport(outputPath) {
        console.log('PDF 生成功能需要额外的 PDF 库支持');
        // 这里可以集成 pdf-lib 或其他 PDF 生成库
        // 暂时创建一个占位符文件
        fs.writeFileSync(outputPath, 'PDF 生成功能开发中...');
        console.log(`PDF 文档已生成（占位符）：${outputPath}`);
    }
}

module.exports = WebScraper;