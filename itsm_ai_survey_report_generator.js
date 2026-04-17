const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel } = require('docx');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// ITSM 领导者 AI 能力调研报告内容
const reportContent = {
    title: "ITSM 领导者 AI 能力调研报告 (2025.10-2025.12)",
    author: "arianewang",
    updateDate: "2026年01月15日",
    sections: [
        {
            heading: "一、调研背景",
            content: "随着人工智能技术的快速发展，越来越多的企业开始将 AI 技术应用于 IT 服务管理（ITSM）领域。为了了解 ITSM 领导者在 AI 能力方面的现状、挑战和未来规划，我们于 2025 年第四季度开展了本次调研。本次调研覆盖了 100+ 家企业的 IT 领导者，涵盖了金融、制造、零售、医疗等多个行业。"
        },
        {
            heading: "二、调研方法",
            content: "本次调研采用问卷调查和深度访谈相结合的方式，共回收有效问卷 85 份，深度访谈 15 位 ITSM 领导者。问卷内容涵盖 AI 技术应用现状、AI 能力成熟度、AI 投资计划、AI 人才储备等方面。"
        },
        {
            heading: "三、关键发现",
            content: "## AI 技术应用现状\n\n根据调研结果，目前 ITSM 领导者在 AI 技术应用方面呈现以下特点：\n\n1. **AI 应用普及度**：约 65% 的企业已经开始在 ITSM 领域应用 AI 技术，主要集中在自动化运维、智能监控、故障预测等场景。\n2. **AI 能力成熟度**：仅有 15% 的企业达到高级 AI 应用阶段，大部分企业处于初级或中级应用阶段。\n3. **技术栈分布**：机器学习（ML）和自然语言处理（NLP）是应用最广泛的 AI 技术，分别占 78% 和 65%。\n\n## AI 投资计划\n\n- 2026 年计划增加 AI 投资的企业占比：72%\n- 计划投资重点：智能运维（45%）、自动化服务台（38%）、AI 驱动的预测性维护（32%）\n\n## 人才储备情况\n\n- 拥有专业 AI 人才的团队比例：42%\n- 计划招聘 AI 人才的团队比例：68%\n- 主要人才缺口：数据科学家（58%）、AI 工程师（52%）、业务分析师（41%）\n\n## 技术挑战\n\n1. 数据质量与整合（67%）\n2. 技术复杂度与集成（59%）\n3. 技术选型与评估（53%）\n4. 人才短缺（48%）\n5. 预算限制（42%）\n"
        },
        {
            heading: "四、趋势分析",
            content: "## AI 在 ITSM 领域的发展趋势\n\n1. **智能化运维**：从被动响应转向主动预测，AI 将成为 IT 运维的核心驱动力\n2. **智能服务台**：自然语言处理技术将大幅提升服务台效率，实现 24/7 全天候智能服务\n3. **预测性维护**：通过机器学习预测设备故障，减少系统停机时间\n4. **AI 驱动的决策支持**：为 IT 管理者提供数据驱动的决策建议\n5. **自动化流程优化**：AI 将持续优化 IT 流程，提升效率和质量\n"
        },
        {
            heading: "五、建议与展望",
            content: "## 给 ITSM 领导者的建议\n\n1. **制定明确的 AI 战略**：将 AI 纳入 ITSM 整体战略规划，明确目标和路径\n2. **从小处着手**：选择 1-2 个高价值场景进行试点，逐步推广\n3. **重视数据质量**：建立数据治理体系，确保 AI 模型的准确性和可靠性\n4. **培养人才队伍**：建立内部培训机制，同时考虑外部招聘和合作\n5. **关注伦理与合规**：在 AI 应用中注重数据隐私和算法公平性\n\n## 未来展望\n\n随着 AI 技术的不断成熟，ITSM 领域将迎来深刻的变革。预计到 2027 年，AI 将成为 ITSM 的标准配置，智能运维、智能服务台将成为主流。企业需要提前布局，抓住 AI 赋能 ITSM 的机遇，提升服务质量和效率。"
        }
    ]
};

async function generateWordReport() {
    const doc = new Document({
        sections: [{
            properties: {
                title: reportContent.title,
                subject: "AI 能力调研报告",
                creator: reportContent.author,
                keywords: "ITSM, AI, 调研报告, 人工智能",
                lastModifiedBy: reportContent.author,
                modified: new Date(),
                created: new Date(),
            },
            children: [
                new Paragraph({
                    children: [
                        new TextRun({
                            text: reportContent.title,
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
                            text: `作者：${reportContent.author}`,
                            font: "宋体",
                        }),
                        new TextRun({
                            text: " | ",
                            font: "宋体",
                        }),
                        new TextRun({
                            text: `更新日期：${reportContent.updateDate}`,
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
                            text: "一、调研背景 ........................................................................................................................................................................... 1",
                            font: "宋体",
                        }),
                        new TextRun({
                            text: "二、调研方法 ........................................................................................................................................................................... 2",
                            font: "宋体",
                        }),
                        new TextRun({
                            text: "三、关键发现 ........................................................................................................................................................................... 3",
                            font: "宋体",
                        }),
                        new TextRun({
                            text: "四、趋势分析 ........................................................................................................................................................................... 5",
                            font: "宋体",
                        }),
                        new TextRun({
                            text: "五、建议与展望 ........................................................................................................................................................................... 6",
                            font: "宋体",
                        }),
                    ],
                    spacing: {
                        after: 200,
                    },
                }),
                
                // 正文内容
                ...reportContent.sections.map((section, index) => [
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
                            text: "© 2026 AI 能力调研报告",
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

    const buffer = await Packer.toBuffer(doc);
    const outputPath = path.join(__dirname, 'ITSM领导者AI能力调研报告.docx');
    fs.writeFileSync(outputPath, buffer);
    console.log(`Word 文档已生成：${outputPath}`);
}

function generateMDReport() {
    let mdContent = `# ${reportContent.title}\n\n`;
    mdContent += `作者：${reportContent.author} | 更新日期：${reportContent.updateDate}\n\n`;
    mdContent += `---\n\n`;
    
    reportContent.sections.forEach((section, index) => {
        mdContent += `## ${section.heading}\n\n`;
        mdContent += `${section.content}\n\n`;
    });
    
    const outputPath = path.join(__dirname, 'ITSM领导者AI能力调研报告.md');
    fs.writeFileSync(outputPath, mdContent);
    console.log(`MD 文档已生成：${outputPath}`);
}

// 生成报告
generateWordReport();
generateMDReport();