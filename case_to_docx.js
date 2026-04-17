const { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, Alignment } = require('docx');

// 创建文档
const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // 标题
            new Paragraph({
                text: "利用多模态 AI 工具链实现海报、流程图与 PPT 的自动化生产",
                heading: HeadingLevel.HEADING_1,
                alignment: Alignment.CENTER,
                spacing: {
                    after: 500,
                },
            }),
            new Paragraph({
                text: "2026-01-19",
                alignment: Alignment.CENTER,
                spacing: {
                    after: 500,
                },
            }),
            
            // 背景简述
            new Paragraph({
                text: "背景简述",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            new Paragraph({
                text: "在日常工作中（无论是做产品方案、运营活动还是项目汇报），我们有 40% 的时间耗费在\"视觉化表达\"上。",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "痛点：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "配图难：做活动海报或文章配图时，找不到合适的素材，求助设计部门排期又太长。",
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "画图累：梳理复杂业务逻辑时，用 Visio/ProcessOn 手动拖拽连线，效率极低且难以维护。",
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "PPT 耗时：面对几十页的文档素材，要转化成结构清晰的 PPT，往往需要在排版和提炼上耗费大量精力。",
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "目标：建立一套不需要设计基础也能快速产出专业级视觉素材的 AI 工作流。",
                spacing: {
                    after: 400,
                },
            }),
            
            // 当前实践成果
            new Paragraph({
                text: "当前实践成果",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "海报素材\"零等待\"：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "利用本地部署的 Gemini-Nano (配合内部 Banana 工具)，实现活动配图/氛围图的秒级生成，无需依赖外部网络素材库，且数据安全。",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "复杂逻辑\"一键图示化\"：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "将繁杂的文字需求投喂给 GPT，自动生成 Mermaid/Graphviz 代码，瞬间转化为专业的业务流程图，绘图效率提升 10 倍。",
                spacing: {
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "文档转 PPT 分钟级出稿：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "利用 NotebookLM 强大的长文本理解能力，将万字文档快速结构化为 PPT 大纲和页面内容，将通读-构思-制作的周期缩短 70%。",
                spacing: {
                    after: 400,
                },
            }),
            
            // 核心步骤拆解
            new Paragraph({
                text: "核心步骤拆解",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            // 场景一：创意海报/配图生成
            new Paragraph({
                text: "场景一：创意海报/配图生成（工具：Gemini-Nano + Banana）",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "主打：本地、快速、创意发散。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "痛点场景：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "需要为内部技术沙龙做一个\"未来感\"的宣传头图。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "动作：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "不再此时此刻去搜索网站找图。打开内部集成的 Banana 工具（调用本地 Gemini-Nano 能力）。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "Prompt 策略：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "采用\"主体 + 风格 + 环境 + 构图\"的公式。例如：\"一张充满未来感的科技沙龙海报背景，赛博朋克风格，霓虹灯光线条连接着一个发光的大脑芯片，深蓝色调，扁平化插画风格。\"",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "优势：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "本地模型响应极快，可以短时间内生成几十张不同方案供挑选，且 prompt 对中文理解更好。",
                spacing: {
                    after: 400,
                },
            }),
            
            // 场景二：逻辑流程图/架构图生成
            new Paragraph({
                text: "场景二：逻辑流程图/架构图生成（工具：GPT-4）",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "主打：逻辑梳理、代码化绘图。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "痛点场景：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "手头有一大段关于\"用户订单状态流转\"的文字描述，需要画成跨职能流程图。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "动作：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "将文字描述扔给 GPT。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "Prompt：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "你是一名系统架构师。请阅读以下订单流转逻辑：[粘贴文字]。请帮我将其转化为标准的 Mermaid 流程图代码（或者 Graphviz 代码）。要求：使用泳道图区分'用户'、'订单系统'和'支付网关'。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "产出：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "得到一段代码，直接粘贴到支持 Mermaid 的编辑器（如 Notion、GitLab）中，流程图自动渲染完成。",
                spacing: {
                    after: 400,
                },
            }),
            
            // 场景三：长文档转汇报 PPT
            new Paragraph({
                text: "场景三：长文档转汇报 PPT（工具：NotebookLM）",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            new Paragraph({
                text: "主打：长文本摘要、结构化输出。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "痛点场景：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "拿到一份 50 页的行业分析报告，明天要给老板做 10 页的 PPT 汇报。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "动作：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "将 PDF 上传至 NotebookLM 建立知识库。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "Prompt：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "基于这份文档，请帮我构思一个 10 页的 PPT 大纲结构。主题是《行业机会分析》。要求每一页包含一个核心标题和 3-5 个关键 bullet points。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "进阶动作：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "对着某一页的大纲深入提问：\"请为第 3 页'市场规模预测'提供文档中的关键数据支撑和图表建议。\"",
                spacing: {
                    after: 400,
                },
            }),
            
            // 关键经验总结
            new Paragraph({
                text: "关键经验总结",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "\"术业有专攻\"：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "不要试图用一个 AI 解决所有问题。Gemini-Nano 胜在本地图像生成的效率和安全；GPT 胜在逻辑推理和代码生成（Mermaid）；NotebookLM 胜在长文档的 RAG（检索增强）能力。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "视觉提示词（Visual Prompting）不同于文本：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "生成图片时，描述\"画面风格\"（如：赛博朋克、极简线条、水彩）比描述内容细节更重要。",
                spacing: {
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "从\"画图工\"到\"导演\"：",
                bold: true,
                spacing: {
                    after: 100,
                },
            }),
            new Paragraph({
                text: "这套工作流将我们从繁重的鼠标拖拽工作中解放出来，我们的核心价值转变为：定义风格、审核逻辑、以及串联故事线。",
                spacing: {
                    after: 200,
                },
            }),
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    require('fs').writeFileSync('AI多模态工具链案例.docx', buffer);
    console.log('文档生成成功：AI多模态工具链案例.docx');
}).catch(err => {
    console.error('生成文档时出错：', err);
});