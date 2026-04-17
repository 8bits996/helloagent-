const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, PageOrientation, Table, TableRow, TableCell } = require('docx');
const path = require('path');

// 页面标题和作者信息
const title = "Zendesk 2026 客户体验趋势报告";
const author = "arianewang";
const updateDate = "01/15 更新";

// 生成Word文档
async function generateWordDocument() {
    // 创建文档
    const doc = new Document({
        sections: [{
            properties: {
                page: {
                    orientation: PageOrientation.LANDSCAPE,
                    margin: {
                        top: 720, // 1 inch
                        right: 720,
                        bottom: 720,
                        left: 720
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
                    heading: HeadingLevel.HEADING_1,
                    children: [
                        new TextRun({
                            text: "目录",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "1. Zendesk 2026 客户体验趋势报告概览",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "2. 关键趋势分析",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "3. 客户体验的未来发展方向",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "4. 实施建议与最佳实践",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 概览部分
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
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
                    heading: HeadingLevel.HEADING_1,
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
                    heading: HeadingLevel.HEADING_2,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "随着人工智能技术的快速发展，越来越多的企业开始采用AI驱动的自动化解决方案来提升客户服务效率。预计到2026年，超过75%的企业将部署AI聊天机器人和虚拟助手。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "2. 多渠道整合",
                    heading: HeadingLevel.HEADING_2,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "客户希望通过多种渠道获得无缝的服务体验。企业需要整合在线聊天、电话、邮件、社交媒体等多种沟通渠道，提供一致的服务体验。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "3. 个性化体验",
                    heading: HeadingLevel.HEADING_2,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "个性化已成为客户体验的核心。企业需要利用数据分析和AI技术，为每个客户提供定制化的服务体验，提高客户满意度和忠诚度。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 趋势表格
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [
                        new TextRun({
                            text: "2026年客户体验关键趋势",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Table({
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "趋势领域" })],
                                    width: { size: 50, type: 'percentage' }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "预计采用率" })],
                                    width: { size: 25, type: 'percentage' }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "主要影响" })],
                                    width: { size: 25, type: 'percentage' }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "AI驱动的服务自动化" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "75%" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "提高效率，降低成本" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "多渠道整合" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "68%" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "提升客户满意度" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "个性化体验" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "82%" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "增强客户忠诚度" })],
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 实施建议
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
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
                    heading: HeadingLevel.HEADING_1,
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
1. Zendesk 2026 客户体验趋势报告概览
2. 关键趋势分析
3. 客户体验的未来发展方向
4. 实施建议与最佳实践

## 1. Zendesk 2026 客户体验趋势报告概览

本报告分析了2026年客户体验的主要趋势，包括AI驱动的服务自动化、多渠道整合、个性化体验等关键领域。报告基于对全球企业客户的深入调研，结合行业专家观点，为企业和组织提供客户体验战略指导。

## 2. 关键趋势分析

### 2.1 AI驱动的服务自动化

随着人工智能技术的快速发展，越来越多的企业开始采用AI驱动的自动化解决方案来提升客户服务效率。预计到2026年，超过75%的企业将部署AI聊天机器人和虚拟助手。

### 2.2 多渠道整合

客户希望通过多种渠道获得无缝的服务体验。企业需要整合在线聊天、电话、邮件、社交媒体等多种沟通渠道，提供一致的服务体验。

### 2.3 个性化体验

个性化已成为客户体验的核心。企业需要利用数据分析和AI技术，为每个客户提供定制化的服务体验，提高客户满意度和忠诚度。

## 3. 2026年客户体验关键趋势

| 趋势领域 | 预计采用率 | 主要影响 |
|---------|----------|---------|
| AI驱动的服务自动化 | 75% | 提高效率，降低成本 |
| 多渠道整合 | 68% | 提升客户满意度 |
| 个性化体验 | 82% | 增强客户忠诚度 |

## 4. 实施建议与最佳实践

基于以上分析，我们建议企业采取以下措施：

1. 投资AI技术：优先部署AI聊天机器人和自动化工具
2. 整合多渠道：建立统一的客户服务平台
3. 重视数据：收集和分析客户数据，提供个性化服务

## 5. 结论

客户体验已成为企业竞争的关键因素。通过采用AI技术、整合多渠道和提供个性化服务，企业可以显著提升客户满意度和忠诚度，实现业务增长。

---
*© 2026 Zendesk. All rights reserved.*`;

    fs.writeFileSync(path.join(__dirname, `${title}.md`), mdContent);
    console.log(`MD文档已生成: ${title}.md`);
}

// 主函数
async function main() {
    console.log("正在生成文档...");
    
    await generateWordDocument();
    generateMDDocument();
    
    console.log("文档生成完成！");
}

main();