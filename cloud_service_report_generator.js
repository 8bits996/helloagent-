const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, PageOrientation, Table, TableRow, TableCell } = require('docx');
const path = require('path');

// 页面标题和作者信息
const title = "云服务调研";
const author = "gavrielliu";
const updateDate = "01/12 更新";

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
                    text: "1. 亚马逊云科技 (AWS) 最新 AI 产品调研报告 (2025-2026)",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "2. 微软 Azure 最新 AI 产品调研报告 (2025-2026)",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // AWS部分
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [
                        new TextRun({
                            text: "亚马逊云科技 (AWS) 最新 AI 产品调研报告 (2025-2026)",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "本报告总结了 AWS 在 2025 年至 2026 年初推出的核心 AI 产品与技术更新。在 re:Invent 2025 期间，AWS 展示了其在模型性能、智能体（Agentic AI）以及底层基础设施方面的全面突破。",
                    spacingAfter: 400
                }),
                
                // 1. 核心模型：Amazon Nova 2 家族
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "1. 核心模型：Amazon Nova 2 家族",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "Amazon Nova 2 是 AWS 自研模型的重大迭代，实现了从文本到多模态、从低延迟到高推理的全面覆盖。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "模型型号",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Table({
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "模型型号" })],
                                    width: { size: 50, type: 'percentage' }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "核心定位与特点" })],
                                    width: { size: 50, type: 'percentage' }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Nova 2 Sonic" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "原生语音到语音模型。支持自然轮替对话和多语种（英、法、德、西等）无缝切换，响应极快。" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Nova 2 Lite" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "极速且高性价比的推理模型，拥有 100万 token 上下文窗口，内置 Web Grounding（网页检索）。" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Nova 2 Pro" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "针对复杂、多步骤任务优化的智能模型，支持"扩展思考（Extended Thinking）"模式。" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Nova 2 Omni" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "全能多模态模型。支持文本、图像、视频、语音输入，并能生成文本和图像。" })],
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "创新点：Amazon Nova Web Grounding",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "允许模型根据需要自主决定是否检索网页信息，并提供带有引用的回答，无需开发者自行构建 RAG 管道。",
                    spacingAfter: 400
                }),
                
                // 2. 智能体与开发工具 (Agentic AI)
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "2. 智能体与开发工具 (Agentic AI)",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "AWS 致力于将 AI 从"对话框"推向"执行端"，通过一系列工具实现业务流程自动化。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "● Kiro (AWS Agentic IDE): AWS 推出的智能体集成开发环境。其核心是 Kiro Autonomous Agent，能够跨会话保持上下文，自主分析代码库、拆分任务并异步执行（支持同时运行 10 个任务）。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Amazon Nova Act: 实现了 90% 以上可靠性的浏览器自动化技术。AI 可以通过自然语言指令操作网页，自动处理 Docker 部署和基础设施配置。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Amazon Bedrock AgentCore: 为生产级智能体提供治理、观测和评估的底层框架，支持 Cedar 策略语言进行安全管控。",
                    spacingAfter: 400
                }),
                
                // 3. 基础设施与算力革新
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "3. 基础设施与算力革新",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "AWS 继续通过自研芯片和优化存储来降低 AI 成本并提升性能。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "● Trainium3 UltraServers: 新一代 AI 训练服务器，专为万亿参数规模的模型训练设计。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Graviton5 处理器: AWS 最强大的通用 CPU，相比前代在 AI 推理性能上有显著提升。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Amazon S3 Vectors: S3 现在原生支持向量存储，单索引容量从 5000 万提升至 20 亿向量，是构建超大规模 RAG 系统的高性价比选择。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● AWS AI Factories: 提供全托管的 AI 基础设施，允许企业在自己的数据中心内部署与 AWS 云端完全一致的 AI 算力环境。",
                    spacingAfter: 400
                }),
                
                // 4. 总结与建议
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "4. 总结与建议",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "AWS 的最新布局显示出其在"工程化 AI"方面的深厚积累。相比于其他云厂商，AWS 更强调 AI 在实际生产环境中的可靠性（如 Nova Act 的 90% 成功率）和存量业务的现代化（如 AWS Transform）。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "建议关注方向：",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 企业级自动化：利用 Amazon Nova Act 替代传统的 Selenium/Playwright 脚本，实现更具弹性的网页自动化。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 代码现代化：使用 AWS Transform 快速迁移和重构遗留系统，降低维护成本。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 大规模 RAG：结合 Amazon S3 Vectors 和 Nova 2 Lite 的长上下文能力，构建低成本、高性能的知识库。",
                    spacingAfter: 400
                }),
                
                // Azure部分
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [
                        new TextRun({
                            text: "微软 Azure 最新 AI 产品调研报告 (2025-2026)",
                            bold: true,
                            size: 24
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "本报告旨在总结微软 Azure 在 2025 年至 2026 年初推出的最新、最具创新性的 AI 产品与技术。微软在 Microsoft Ignite 2025 期间发布了一系列重大更新，标志着其从"Copilot 时代"全面迈向"智能体（Agentic AI）时代"。",
                    spacingAfter: 400
                }),
                
                // 1. 核心平台：Microsoft Foundry
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "1. 核心平台：Microsoft Foundry (原 Azure AI Foundry)",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "Microsoft Foundry 是微软推出的统一 AI 开发与管理平台，旨在简化从模型选择到智能体部署的全流程。",
                    spacingAfter: 400
                }),
                
                new Table({
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "功能模块" })],
                                    width: { size: 50, type: 'percentage' }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "描述" })],
                                    width: { size: 50, type: 'percentage' }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Foundry IQ" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "简化了智能体与企业数据（如 SharePoint、Fabric、Web）的连接，提供单一 API 的智能检索。" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Model Router" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "允许开发者根据成本、性能或延迟需求，在不同模型之间自动路由请求。" })],
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ text: "Foundry Control Plane" })],
                                }),
                                new TableCell({
                                    children: [new Paragraph({ text: "提供企业级的治理、安全和合规性控制，确保 AI 应用的可控性。" })],
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "\n",
                }),
                
                // 2. 尖端模型：多模态与实时交互
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "2. 尖端模型：多模态与实时交互",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "Azure 进一步扩大了其模型库，不仅深度集成 OpenAI 的最新成果，还引入了顶级第三方模型。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "● GPT-5-Codex (GA): 专为编程设计的最新多模态模型，支持通过架构图或 UI 截图进行代码推理，能够处理复杂的深度重构和代码审查。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Sora video-to-video (Preview): 引入了视频生成与编辑能力，支持视频到视频的转换，为多媒体创作提供 AI 动力。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● gpt-realtime (GA): 实现了极低延迟的语音到语音推理，支持更自然的实时人机对话。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Anthropic Claude 4.5 系列：包括 Sonnet、Opus 和 Haiku，现已集成至 Microsoft Foundry，使 Azure 成为唯一同时提供 OpenAI 和 Anthropic 顶级模型的云平台。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Grok 4 Fast (Preview): 针对极速推理场景优化的新型模型。",
                    spacingAfter: 400
                }),
                
                // 3. 智能体技术 (Agentic AI)
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "3. 智能体技术 (Agentic AI)",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "这是微软近期最核心的创新方向，旨在让 AI 不仅仅是辅助工具，而是能够自主执行任务的智能体。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "“智能体时代”的定义：AI 不再只是回答问题，而是能够理解业务上下文、访问系统并代表用户执行操作。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "关键技术组件：",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "1. Computer Use (Preview): 允许 AI 像人类一样操作计算机屏幕（点击、输入、截图反馈），特别适用于没有 API 的遗留系统或复杂 UI。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "2. Browser Automation (Preview): 基于 Playwright 的弹性 DOM 自动化技术，使智能体能够稳定地在网页上执行复杂任务。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "3. Microsoft Agent Framework (OSS): 统一了 Semantic Kernel 和 AutoGen 的编排引擎，支持智能体间的协作（A2A 消息传递）。",
                    spacingAfter: 400
                }),
                
                // 4. AI 驱动的数据与基础设施
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "4. AI 驱动的数据与基础设施",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "为了支撑强大的 AI 算力，微软在数据库和硬件层面也进行了深度革新。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "数据库创新：",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Azure HorizonDB (Preview): 全新推出的全托管、兼容 PostgreSQL 的数据库，专为 AI 应用优化，具备极高的扩展性和智能索引能力。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● SQL Server 2025: 深度集成 AI 功能，支持向量数据类型（Vector Search）以及直接在 T-SQL 中调用外部 AI 模型。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Azure DocumentDB (GA): 原 Cosmos DB for MongoDB (vCore) 的演进版，为 MongoDB 工作负载提供更高的灵活性和成本效益。",
                    spacingAfter: 400
                }),
                
                new Paragraph({
                    text: "硬件与算力：",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Azure Cobalt 200: 微软自研的 ARM 架构处理器，专为通用云工作负载和 AI 推理优化，显著提升了能效比。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● Azure Boost: 通过卸载虚拟化功能至专用硬件，大幅提升了存储和网络性能。",
                    spacingAfter: 400
                }),
                
                // 5. 总结与展望
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [
                        new TextRun({
                            text: "5. 总结与展望",
                            bold: true,
                            size: 20
                        })
                    ]
                }),
                
                new Paragraph({
                    text: "微软 Azure 的最新布局显示出其在 Agentic AI（智能体 AI）领域的领先地位。通过 Microsoft Foundry 这一统一入口，企业可以灵活组合 OpenAI、Anthropic 等顶级模型，并利用 Computer Use 等技术实现业务流程的全面自动化。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "建议关注方向：",
                    heading: HeadingLevel.HEADING_3,
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 利用 Foundry IQ 快速构建基于企业私有数据的 RAG 系统。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 探索 Computer Use 在自动化传统办公流程中的潜力。",
                    spacingAfter: 200
                }),
                
                new Paragraph({
                    text: "● 关注 SQL Server 2025 的向量搜索功能，实现数据层面的语义检索。",
                    spacingAfter: 400
                }),
                
                // 页脚
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    text: "© 2026 云服务调研报告. All rights reserved.",
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
1. 亚马逊云科技 (AWS) 最新 AI 产品调研报告 (2025-2026)
2. 微软 Azure 最新 AI 产品调研报告 (2025-2026)

## 1. 亚马逊云科技 (AWS) 最新 AI 产品调研报告 (2025-2026)

本报告总结了 AWS 在 2025 年至 2026 年初推出的核心 AI 产品与技术更新。在 re:Invent 2025 期间，AWS 展示了其在模型性能、智能体（Agentic AI）以及底层基础设施方面的全面突破。

### 1.1 核心模型：Amazon Nova 2 家族

Amazon Nova 2 是 AWS 自研模型的重大迭代，实现了从文本到多模态、从低延迟到高推理的全面覆盖。

#### 模型型号

| 模型型号 | 核心定位与特点 |
|---------|--------------|
| Nova 2 Sonic | 原生语音到语音模型。支持自然轮替对话和多语种（英、法、德、西等）无缝切换，响应极快。 |
| Nova 2 Lite | 极速且高性价比的推理模型，拥有 100万 token 上下文窗口，内置 Web Grounding（网页检索）。 |
| Nova 2 Pro | 针对复杂、多步骤任务优化的智能模型，支持"扩展思考（Extended Thinking）"模式。 |
| Nova 2 Omni | 全能多模态模型。支持文本、图像、视频、语音输入，并能生成文本和图像。 |

#### 创新点：Amazon Nova Web Grounding

允许模型根据需要自主决定是否检索网页信息，并提供带有引用的回答，无需开发者自行构建 RAG 管道。

### 1.2 智能体与开发工具 (Agentic AI)

AWS 致力于将 AI 从"对话框"推向"执行端"，通过一系列工具实现业务流程自动化。

- **Kiro (AWS Agentic IDE)**: AWS 推出的智能体集成开发环境。其核心是 Kiro Autonomous Agent，能够跨会话保持上下文，自主分析代码库、拆分任务并异步执行（支持同时运行 10 个任务）。
- **Amazon Nova Act**: 实现了 90% 以上可靠性的浏览器自动化技术。AI 可以通过自然语言指令操作网页，自动处理 Docker 部署和基础设施配置。
- **Amazon Bedrock AgentCore**: 为生产级智能体提供治理、观测和评估的底层框架，支持 Cedar 策略语言进行安全管控。

### 1.3 基础设施与算力革新

AWS 继续通过自研芯片和优化存储来降低 AI 成本并提升性能。

- **Trainium3 UltraServers**: 新一代 AI 训练服务器，专为万亿参数规模的模型训练设计。
- **Graviton5 处理器**: AWS 最强大的通用 CPU，相比前代在 AI 推理性能上有显著提升。
- **Amazon S3 Vectors**: S3 现在原生支持向量存储，单索引容量从 5000 万提升至 20 亿向量，是构建超大规模 RAG 系统的高性价比选择。
- **AWS AI Factories**: 提供全托管的 AI 基础设施，允许企业在自己的数据中心内部署与 AWS 云端完全一致的 AI 算力环境。

### 1.4 总结与建议

AWS 的最新布局显示出其在"工程化 AI"方面的深厚积累。相比于其他云厂商，AWS 更强调 AI 在实际生产环境中的可靠性（如 Nova Act 的 90% 成功率）和存量业务的现代化（如 AWS Transform）。

#### 建议关注方向：
- 企业级自动化：利用 Amazon Nova Act 替代传统的 Selenium/Playwright 脚本，实现更具弹性的网页自动化。
- 代码现代化：使用 AWS Transform 快速迁移和重构遗留系统，降低维护成本。
- 大规模 RAG：结合 Amazon S3 Vectors 和 Nova 2 Lite 的长上下文能力，构建低成本、高性能的知识库。

## 2. 微软 Azure 最新 AI 产品调研报告 (2025-2026)

本报告旨在总结微软 Azure 在 2025 年至 2026 年初推出的最新、最具创新性的 AI 产品与技术。微软在 Microsoft Ignite 2025 期间发布了一系列重大更新，标志着其从"Copilot 时代"全面迈向"智能体（Agentic AI）时代"。

### 2.1 核心平台：Microsoft Foundry (原 Azure AI Foundry)

Microsoft Foundry 是微软推出的统一 AI 开发与管理平台，旨在简化从模型选择到智能体部署的全流程。

| 功能模块 | 描述 |
|---------|------|
| Foundry IQ | 简化了智能体与企业数据（如 SharePoint、Fabric、Web）的连接，提供单一 API 的智能检索。 |
| Model Router | 允许开发者根据成本、性能或延迟需求，在不同模型之间自动路由请求。 |
| Foundry Control Plane | 提供企业级的治理、安全和合规性控制，确保 AI 应用的可控性。 |

### 2.2 尖端模型：多模态与实时交互

Azure 进一步扩大了其模型库，不仅深度集成 OpenAI 的最新成果，还引入了顶级第三方模型。

- **GPT-5-Codex (GA)**: 专为编程设计的最新多模态模型，支持通过架构图或 UI 截图进行代码推理，能够处理复杂的深度重构和代码审查。
- **Sora video-to-video (Preview)**: 引入了视频生成与编辑能力，支持视频到视频的转换，为多媒体创作提供 AI 动力。
- **gpt-realtime (GA)**: 实现了极低延迟的语音到语音推理，支持更自然的实时人机对话。
- **Anthropic Claude 4.5 系列**: 包括 Sonnet、Opus 和 Haiku，现已集成至 Microsoft Foundry，使 Azure 成为唯一同时提供 OpenAI 和 Anthropic 顶级模型的云平台。
- **Grok 4 Fast (Preview)**: 针对极速推理场景优化的新型模型。

### 2.3 智能体技术 (Agentic AI)

这是微软近期最核心的创新方向，旨在让 AI 不仅仅是辅助工具，而是能够自主执行任务的智能体。

#### "智能体时代"的定义：
AI 不再只是回答问题，而是能够理解业务上下文、访问系统并代表用户执行操作。

#### 关键技术组件：
1. **Computer Use (Preview)**: 允许 AI 像人类一样操作计算机屏幕（点击、输入、截图反馈），特别适用于没有 API 的遗留系统或复杂 UI。
2. **Browser Automation (Preview)**: 基于 Playwright 的弹性 DOM 自动化技术，使智能体能够稳定地在网页上执行复杂任务。
3. **Microsoft Agent Framework (OSS)**: 统一了 Semantic Kernel 和 AutoGen 的编排引擎，支持智能体间的协作（A2A 消息传递）。

### 2.4 AI 驱动的数据与基础设施

为了支撑强大的 AI 算力，微软在数据库和硬件层面也进行了深度革新。

#### 数据库创新：
- **Azure HorizonDB (Preview)**: 全新推出的全托管、兼容 PostgreSQL 的数据库，专为 AI 应用优化，具备极高的扩展性和智能索引能力。
- **SQL Server 2025**: 深度集成 AI 功能，支持向量数据类型（Vector Search）以及直接在 T-SQL 中调用外部 AI 模型。
- **Azure DocumentDB (GA)**: 原 Cosmos DB for MongoDB (vCore) 的演进版，为 MongoDB 工作负载提供更高的灵活性和成本效益。

#### 硬件与算力：
- **Azure Cobalt 200**: 微软自研的 ARM 架构处理器，专为通用云工作负载和 AI 推理优化，显著提升了能效比。
- **Azure Boost**: 通过卸载虚拟化功能至专用硬件，大幅提升了存储和网络性能。

### 2.5 总结与展望

微软 Azure 的最新布局显示出其在 Agentic AI（智能体 AI）领域的领先地位。通过 Microsoft Foundry 这一统一入口，企业可以灵活组合 OpenAI、Anthropic 等顶级模型，并利用 Computer Use 等技术实现业务流程的全面自动化。

#### 建议关注方向：
- 利用 Foundry IQ 快速构建基于企业私有数据的 RAG 系统。
- 探索 Computer Use 在自动化传统办公流程中的潜力。
- 关注 SQL Server 2025 的向量搜索功能，实现数据层面的语义检索。

---
*© 2026 云服务调研报告. All rights reserved.*`;

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