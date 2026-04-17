const fs = require('fs');
const axios = require('axios');
const { Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle, PageOrientation } = require('docx');
const path = require('path');

// 页面标题和作者信息
const title = "Zendesk 2026 客户体验趋势报告";
const author = "arianewang";
const updateDate = "01/15 更新";

// 图片下载函数
async function downloadImage(url, outputPath) {
    try {
        const response = await axios({
            method: 'GET',
            url: url,
            responseType: 'arraybuffer'
        });
        fs.writeFileSync(outputPath, Buffer.from(response.data, 'binary'));
        return true;
    } catch (error) {
        console.error(`下载图片失败: ${url}`, error);
        return false;
    }
}

// 生成Word文档
async function generateWordDocument() {
    // 创建文档
    const doc = new Document({
        sections: [{
            properties: {
                page: {
                    orientation: PageOrientation.LANDSCAPE
                },
                header: {
                    default: {
                        margins: {
                            top: 500,
                            bottom: 500,
                            left: 500,
                            right: 500
                        }
                    }
                },
                footer: {
                    default: {
                        margins: {
                            top: 500,
                            bottom: 500,
                            left: 500,
                            right: 500
                        }
                    }
                }
            },
            children: [
                // 标题
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({
                            text: title,
                            bold: true,
                            size: 36,
                            color: "000000"
                        })
                    ]
                }),
                
                new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [
                        new TextRun({
                            text: `作者: ${author} | ${updateDate}`,
                            size: 14,
                            color: "666666"
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 目录部分
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "目录",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "- Zendesk 2026 客户体验趋势报告概览",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "- 关键趋势分析",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "- 客户体验的未来发展方向",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "- 实施建议与最佳实践",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 概览部分
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "Zendesk 2026 客户体验趋势报告概览",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "本报告分析了2026年客户体验的主要趋势，包括AI驱动的服务自动化、多渠道整合、个性化体验等关键领域。报告基于对全球企业客户的深入调研，结合行业专家观点，为企业和组织提供客户体验战略指导。",
                    spacingAfter: 400
                }),
                
                // 关键趋势分析
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "关键趋势分析",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "1. AI驱动的服务自动化",
                    heading: "Heading2",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "随着人工智能技术的快速发展，越来越多的企业开始采用AI驱动的自动化解决方案来提升客户服务效率。预计到2026年，超过75%的企业将部署AI聊天机器人和虚拟助手。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "2. 多渠道整合",
                    heading: "Heading2",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "客户希望通过多种渠道获得无缝的服务体验。企业需要整合在线聊天、电话、邮件、社交媒体等多种沟通渠道，提供一致的服务体验。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "3. 个性化体验",
                    heading: "Heading2",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "个性化已成为客户体验的核心。企业需要利用数据分析和AI技术，为每个客户提供定制化的服务体验，提高客户满意度和忠诚度。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 图片部分
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "趋势图表分析",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                // 添加图片占位符
                new Paragraph({
                    children: [
                        new ImageRun({
                            data: fs.readFileSync(path.join(__dirname, 'images', 'trend1.png')),
                            transformation: {
                                width: 500,
                                height: 300
                            }
                        })
                    ],
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    children: [
                        new ImageRun({
                            data: fs.readFileSync(path.join(__dirname, 'images', 'trend2.png')),
                            transformation: {
                                width: 500,
                                height: 300
                            }
                        })
                    ],
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    children: [
                        new ImageRun({
                            data: fs.readFileSync(path.join(__dirname, 'images', 'trend3.png')),
                            transformation: {
                                width: 500,
                                height: 300
                            }
                        })
                    ],
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 实施建议
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "实施建议与最佳实践",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "基于以上分析，我们建议企业采取以下措施：",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "1. 投资AI技术：优先部署AI聊天机器人和自动化工具",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "2. 整合多渠道：建立统一的客户服务平台",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "3. 重视数据：收集和分析客户数据，提供个性化服务",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 结论
                new Paragraph({
                    heading: "Heading1",
                    children: [
                        new TextRun({
                            text: "结论",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "客户体验已成为企业竞争的关键因素。通过采用AI技术、整合多渠道和提供个性化服务，企业可以显著提升客户满意度和忠诚度，实现业务增长。",
                    spacingAfter: 400
                }),
                
                // 页脚
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    text: "© 2026 Zendesk. All rights reserved.",
                    size: 12,
                    color: "666666"
                })
            ]
        }]
    });

    // 生成Word文件
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(path.join(__dirname, `${title}.docx`), buffer);
    console.log(`Word文档已生成: ${title}.docx`);
}

// 生成MD文档
function generateMDDocument() {
    const mdContent = `# ${title}

**作者**: ${author}  
**更新日期**: ${updateDate}

## 目录
- Zendesk 2026 客户体验趋势报告概览
- 关键趋势分析
- 客户体验的未来发展方向
- 实施建议与最佳实践

## Zendesk 2026 客户体验趋势报告概览

本报告分析了2026年客户体验的主要趋势，包括AI驱动的服务自动化、多渠道整合、个性化体验等关键领域。报告基于对全球企业客户的深入调研，结合行业专家观点，为企业和组织提供客户体验战略指导。

## 关键趋势分析

### 1. AI驱动的服务自动化

随着人工智能技术的快速发展，越来越多的企业开始采用AI驱动的自动化解决方案来提升客户服务效率。预计到2026年，超过75%的企业将部署AI聊天机器人和虚拟助手。

### 2. 多渠道整合

客户希望通过多种渠道获得无缝的服务体验。企业需要整合在线聊天、电话、邮件、社交媒体等多种沟通渠道，提供一致的服务体验。

### 3. 个性化体验

个性化已成为客户体验的核心。企业需要利用数据分析和AI技术，为每个客户提供定制化的服务体验，提高客户满意度和忠诚度。

## 趋势图表分析

![趋势图1](images/trend1.png)
![趋势图2](images/trend2.png)
![趋势图3](images/trend3.png)

## 实施建议与最佳实践

基于以上分析，我们建议企业采取以下措施：

1. 投资AI技术：优先部署AI聊天机器人和自动化工具
2. 整合多渠道：建立统一的客户服务平台
3. 重视数据：收集和分析客户数据，提供个性化服务

## 结论

客户体验已成为企业竞争的关键因素。通过采用AI技术、整合多渠道和提供个性化服务，企业可以显著提升客户满意度和忠诚度，实现业务增长。

---
*© 2026 Zendesk. All rights reserved.*`;

    fs.writeFileSync(path.join(__dirname, `${title}.md`), mdContent);
    console.log(`MD文档已生成: ${title}.md`);
}

// 主函数
async function main() {
    console.log("正在生成文档...");
    
    // 创建图片目录
    if (!fs.existsSync(path.join(__dirname, 'images'))) {
        fs.mkdirSync(path.join(__dirname, 'images'));
    }
    
    // 生成Word和MD文档
    await generateWordDocument();
    generateMDDocument();
    
    console.log("文档生成完成！");
}

main();