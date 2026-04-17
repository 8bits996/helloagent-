const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, PageOrientation, LevelFormat, HeadingLevel, BorderStyle, WidthType, 
        ShadingType, VerticalAlign, PageNumber, PageBreak, TableOfContents } = require('docx');
const fs = require('fs');

// 定义边框样式
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

// 定义颜色
const colors = {
    primary: "1976D2",
    secondary: "388E3C",
    accent: "F57C00",
    dark: "333333",
    light: "666666",
    headerBg: "E3F2FD",
    successBg: "E8F5E9",
    warningBg: "FFF3E0",
};

// 创建带样式的表格单元格
function createCell(content, options = {}) {
    const { bold = false, bg = null, align = AlignmentType.LEFT, width = 4680 } = options;
    return new TableCell({
        borders: cellBorders,
        width: { size: width, type: WidthType.DXA },
        shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
            alignment: align,
            children: [new TextRun({ text: content, bold, size: 22, font: "Microsoft YaHei" })]
        })]
    });
}

// 创建标题段落
function createHeading(text, level) {
    return new Paragraph({
        heading: level,
        spacing: { before: 300, after: 200 },
        children: [new TextRun({ text, bold: true, font: "Microsoft YaHei" })]
    });
}

// 创建正文段落
function createPara(text, options = {}) {
    const { bold = false, color = colors.dark, indent = 0, spacing = { before: 100, after: 100 } } = options;
    return new Paragraph({
        spacing,
        indent: indent ? { left: indent } : undefined,
        children: [new TextRun({ text, bold, color, size: 22, font: "Microsoft YaHei" })]
    });
}

// 创建高亮引用块
function createQuote(text) {
    return new Paragraph({
        spacing: { before: 200, after: 200 },
        indent: { left: 720 },
        shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
        children: [new TextRun({ text: text, italics: true, size: 24, font: "Microsoft YaHei", color: colors.primary })]
    });
}

// 创建文档
const doc = new Document({
    styles: {
        default: { document: { run: { font: "Microsoft YaHei", size: 22 } } },
        paragraphStyles: [
            { id: "Title", name: "Title", basedOn: "Normal",
                run: { size: 56, bold: true, color: colors.primary, font: "Microsoft YaHei" },
                paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 36, bold: true, color: colors.primary, font: "Microsoft YaHei" },
                paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 30, bold: true, color: colors.dark, font: "Microsoft YaHei" },
                paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
            { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 26, bold: true, color: colors.light, font: "Microsoft YaHei" },
                paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
        ]
    },
    numbering: {
        config: [
            { reference: "bullet-list",
                levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "numbered-list-1",
                levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "numbered-list-2",
                levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
                size: { orientation: PageOrientation.PORTRAIT }
            }
        },
        headers: {
            default: new Header({ children: [new Paragraph({
                alignment: AlignmentType.RIGHT,
                children: [new TextRun({ text: "AI创新技术方案书", size: 20, color: colors.light, font: "Microsoft YaHei" })]
            })] })
        },
        footers: {
            default: new Footer({ children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                    new TextRun({ text: "第 ", size: 20, font: "Microsoft YaHei" }),
                    new TextRun({ children: [PageNumber.CURRENT], size: 20 }),
                    new TextRun({ text: " 页 / 共 ", size: 20, font: "Microsoft YaHei" }),
                    new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 }),
                    new TextRun({ text: " 页", size: 20, font: "Microsoft YaHei" })
                ]
            })] })
        },
        children: [
            // ========== 封面 ==========
            new Paragraph({ spacing: { before: 2000 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 400 },
                children: [new TextRun({ text: "AI创新技术方案书", size: 72, bold: true, color: colors.primary, font: "Microsoft YaHei" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 800 },
                children: [new TextRun({ text: "需求与问题管理智能助手", size: 48, bold: true, color: colors.dark, font: "Microsoft YaHei" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 },
                children: [new TextRun({ text: "（IterAgent）", size: 32, color: colors.light, font: "Microsoft YaHei" })]
            }),
            new Paragraph({ spacing: { before: 800 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                spacing: { before: 200, after: 200 },
                children: [new TextRun({ text: "让迭代管理像呼吸一样自然 - AI赋能政企项目敏捷交付", size: 28, italics: true, color: colors.primary, font: "Microsoft YaHei" })]
            }),
            new Paragraph({ spacing: { before: 1500 } }),
            
            // 方案摘要表格
            new Table({
                columnWidths: [3000, 6360],
                rows: [
                    new TableRow({ children: [
                        createCell("方案名称", { bold: true, bg: colors.headerBg, width: 3000 }),
                        createCell("需求与问题管理智能助手（IterAgent）", { width: 6360 })
                    ]}),
                    new TableRow({ children: [
                        createCell("核心价值", { bold: true, bg: colors.headerBg, width: 3000 }),
                        createCell("迭代管理效率提升10倍+，实现需求秒级查询、批量更新、智能度量", { width: 6360 })
                    ]}),
                    new TableRow({ children: [
                        createCell("目标用户", { bold: true, bg: colors.headerBg, width: 3000 }),
                        createCell("项目管理组、产品经理、研发团队，覆盖50+一线人员", { width: 6360 })
                    ]}),
                    new TableRow({ children: [
                        createCell("技术架构", { bold: true, bg: colors.headerBg, width: 3000 }),
                        createCell("Multi-Agent + TAPD API + 企微机器人 + 自动化工作流", { width: 6360 })
                    ]}),
                    new TableRow({ children: [
                        createCell("体验入口", { bold: true, bg: colors.headerBg, width: 3000 }),
                        createCell("企微机器人 @IterAgent", { width: 6360 })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 目录 ==========
            createHeading("目录", HeadingLevel.HEADING_1),
            new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第一章 ==========
            createHeading("一、目标与范围 (Objective & Scope)", HeadingLevel.HEADING_1),
            
            createHeading("1.1 业务背景与痛点分析", HeadingLevel.HEADING_2),
            createPara("政企项目交付团队面临多产品、多迭代、多依赖方的复杂协作场景，传统的需求管理方式已成为制约交付效率的关键瓶颈。"),
            
            createHeading("1.1.1 核心痛点量化", HeadingLevel.HEADING_3),
            new Table({
                columnWidths: [2000, 3180, 2180, 2000],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("痛点类型", { bold: true, bg: colors.headerBg, width: 2000, align: AlignmentType.CENTER }),
                        createCell("具体表现", { bold: true, bg: colors.headerBg, width: 3180, align: AlignmentType.CENTER }),
                        createCell("影响量化", { bold: true, bg: colors.headerBg, width: 2180, align: AlignmentType.CENTER }),
                        createCell("根因分析", { bold: true, bg: colors.headerBg, width: 2000, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("信息黑盒", { bold: true, width: 2000 }),
                        createCell("需求分散在多张表格，状态更新不及时", { width: 3180 }),
                        createCell("延迟2-3天，遗漏率15%", { width: 2180 }),
                        createCell("数据孤岛", { width: 2000 })
                    ]}),
                    new TableRow({ children: [
                        createCell("依赖管理复杂", { bold: true, width: 2000 }),
                        createCell("新业务接入涉及多个业务产品&开发、策略方", { width: 3180 }),
                        createCell("确认周期3-5天，miss率20%", { width: 2180 }),
                        createCell("跨团队协作", { width: 2000 })
                    ]}),
                    new TableRow({ children: [
                        createCell("流程执行负担重", { bold: true, width: 2000 }),
                        createCell("迭代会前后需手动更新多个字段、统计指标", { width: 3180 }),
                        createCell("耗时4-6小时，50+步操作", { width: 2180 }),
                        createCell("重复劳动", { width: 2000 })
                    ]}),
                    new TableRow({ children: [
                        createCell("度量统计滞后", { bold: true, width: 2000 }),
                        createCell("迭代指标依赖手动计算，口径不一致", { width: 3180 }),
                        createCell("统计耗时2小时+，误差率10%", { width: 2180 }),
                        createCell("缺乏自动化", { width: 2000 })
                    ]}),
                ]
            }),
            
            createHeading("1.2 核心使命", HeadingLevel.HEADING_2),
            createQuote("本Agent旨在为政企项目交付团队提供智能化需求与迭代管理，通过AI技术将繁琐的流程执行自动化，实现【秒级需求查询、一键批量更新、智能度量生成、依赖自动追踪】。"),
            
            createHeading("1.3 目标用户与价值矩阵", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [1800, 1200, 2400, 2160, 1800],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("目标用户", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("人数", { bold: true, bg: colors.headerBg, width: 1200, align: AlignmentType.CENTER }),
                        createCell("核心痛点", { bold: true, bg: colors.headerBg, width: 2400, align: AlignmentType.CENTER }),
                        createCell("Agent解决方案", { bold: true, bg: colors.headerBg, width: 2160, align: AlignmentType.CENTER }),
                        createCell("ROI预期", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("项目管理员", { bold: true, width: 1800 }),
                        createCell("5+", { width: 1200, align: AlignmentType.CENTER }),
                        createCell("迭代流程执行繁琐，重复操作多", { width: 2400 }),
                        createCell("指令任务自动化，一键批量更新", { width: 2160 }),
                        createCell("效率提升24倍", { width: 1800, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("产品经理", { bold: true, width: 1800 }),
                        createCell("20+", { width: 1200, align: AlignmentType.CENTER }),
                        createCell("需求状态难追踪，跨空间管理成本高", { width: 2400 }),
                        createCell("关联需求秒级查询，状态实时同步", { width: 2160 }),
                        createCell("效率提升60倍", { width: 1800, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("研发负责人", { bold: true, width: 1800 }),
                        createCell("15+", { width: 1200, align: AlignmentType.CENTER }),
                        createCell("迭代度量统计耗时，口径不一致", { width: 2400 }),
                        createCell("智能度量自动生成，可视化报表", { width: 2160 }),
                        createCell("准确率100%", { width: 1800, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("项目经理", { bold: true, width: 1800 }),
                        createCell("10+", { width: 1200, align: AlignmentType.CENTER }),
                        createCell("依赖方进度难追踪，容易miss", { width: 2400 }),
                        createCell("依赖关系图谱，智能预警提醒", { width: 2160 }),
                        createCell("风险降低90%", { width: 1800, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            createHeading("1.4 职责边界", HeadingLevel.HEADING_2),
            createPara("能做 (In Scope)：", { bold: true, color: colors.secondary }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "需求状态查询：关联需求、迭代进度、字段信息", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "批量字段更新：参评迭代、承接迭代、多选字段", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "迭代度量计算：参评数、承接率、如期交付率", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "关联需求导出：跨空间链接批量获取", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "智能提醒推送：迭代节点、待办项、风险预警", size: 22, font: "Microsoft YaHei" })] }),
            
            createPara("不能做 (Out of Scope)：", { bold: true, color: "D32F2F" }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "需求内容决策：仅提供数据，不替代产品判断", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "优先级自动排序：仅展示信息，决策归产品方", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "代码/技术实现：仅管理需求，不涉及开发", size: 22, font: "Microsoft YaHei" })] }),
            
            createHeading("1.5 成功标准定义", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [1500, 3000, 1500, 1500, 1860],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("维度", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("指标", { bold: true, bg: colors.headerBg, width: 3000, align: AlignmentType.CENTER }),
                        createCell("基线值", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("目标值", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("验收标准", { bold: true, bg: colors.headerBg, width: 1860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("效率", { width: 1500 }),
                        createCell("单次迭代管理耗时", { width: 3000 }),
                        createCell("4-6小时", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("<30分钟", { width: 1500, align: AlignmentType.CENTER, bg: colors.successBg }),
                        createCell("P95<30min", { width: 1860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("效率", { width: 1500 }),
                        createCell("需求状态查询时间", { width: 3000 }),
                        createCell("30分钟", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("<30秒", { width: 1500, align: AlignmentType.CENTER, bg: colors.successBg }),
                        createCell("P95<30s", { width: 1860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("质量", { width: 1500 }),
                        createCell("需求遗漏率", { width: 3000 }),
                        createCell("15%", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("<2%", { width: 1500, align: AlignmentType.CENTER, bg: colors.successBg }),
                        createCell("人工抽检", { width: 1860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("质量", { width: 1500 }),
                        createCell("度量计算准确率", { width: 3000 }),
                        createCell("90%", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("100%", { width: 1500, align: AlignmentType.CENTER, bg: colors.successBg }),
                        createCell("自动校验", { width: 1860, align: AlignmentType.CENTER })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第二章 ==========
            createHeading("二、工作流程与核心能力 (Workflow & Core Capabilities)", HeadingLevel.HEADING_1),
            
            createHeading("2.1 系统架构全景图", HeadingLevel.HEADING_2),
            createPara("系统采用分层架构设计，包含用户层、接入层、Agent核心层、能力层、数据层和基础设施层："),
            
            new Table({
                columnWidths: [2340, 7020],
                rows: [
                    new TableRow({ children: [
                        createCell("用户层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("项目管理员、产品经理、研发负责人、项目经理", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("接入层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("企微机器人、TAPD页面扩展、迭代度量页面", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("Agent核心层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("意图识别引擎 -> 任务规划器 -> 工具调度器 -> 结果整合器", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("能力层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("TAPD开放API、自动化助手、连接中台Agent、度量计算引擎", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("数据层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("需求数据、迭代数据、字段配置、度量数据", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("基础设施层", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("TAPD平台、企业微信、连接中台、监控告警", { width: 7020 })
                    ]}),
                ]
            }),
            
            createHeading("2.2 核心能力矩阵", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [1800, 2700, 2700, 2160],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("核心能力", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("技术实现", { bold: true, bg: colors.headerBg, width: 2700, align: AlignmentType.CENTER }),
                        createCell("创新点", { bold: true, bg: colors.headerBg, width: 2700, align: AlignmentType.CENTER }),
                        createCell("效果指标", { bold: true, bg: colors.headerBg, width: 2160, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("指令解析", { bold: true, width: 1800 }),
                        createCell("正则匹配 + 参数提取", { width: 2700 }),
                        createCell("支持中文空格分隔、模糊匹配", { width: 2700 }),
                        createCell("准确率 99%", { width: 2160, bg: colors.successBg, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("异步任务执行", { bold: true, width: 1800 }),
                        createCell("TAPD缺陷状态机 + 轮询", { width: 2700 }),
                        createCell("利用现有平台，无需额外部署", { width: 2700 }),
                        createCell("成功率 99%", { width: 2160, bg: colors.successBg, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("批量操作", { bold: true, width: 1800 }),
                        createCell("TAPD开放API + 循环调用", { width: 2700 }),
                        createCell("支持大批量需求更新", { width: 2700 }),
                        createCell("单次最大 100条", { width: 2160, bg: colors.successBg, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("度量计算", { bold: true, width: 1800 }),
                        createCell("字段统计 + 比例计算", { width: 2700 }),
                        createCell("自动化口径统一", { width: 2700 }),
                        createCell("准确率 100%", { width: 2160, bg: colors.successBg, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("跨空间查询", { bold: true, width: 1800 }),
                        createCell("关联需求API", { width: 2700 }),
                        createCell("一键获取所有关联链接", { width: 2700 }),
                        createCell("响应 <5s", { width: 2160, bg: colors.successBg, align: AlignmentType.CENTER })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第三章 ==========
            createHeading("三、工具集 (Toolkit)", HeadingLevel.HEADING_1),
            
            createHeading("3.1 工具清单总览", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [1500, 2700, 3060, 1080, 1020],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("类别", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("工具名称", { bold: true, bg: colors.headerBg, width: 2700, align: AlignmentType.CENTER }),
                        createCell("功能描述", { bold: true, bg: colors.headerBg, width: 3060, align: AlignmentType.CENTER }),
                        createCell("调用频率", { bold: true, bg: colors.headerBg, width: 1080, align: AlignmentType.CENTER }),
                        createCell("平均耗时", { bold: true, bg: colors.headerBg, width: 1020, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("需求查询", { width: 1500 }),
                        createCell("get_related_stories", { width: 2700 }),
                        createCell("获取迭代内需求的关联需求链接", { width: 3060 }),
                        createCell("高", { width: 1080, align: AlignmentType.CENTER }),
                        createCell("<5s", { width: 1020, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("字段更新", { width: 1500 }),
                        createCell("batch_update_multi_select", { width: 2700 }),
                        createCell("批量追加更新多选字段", { width: 3060 }),
                        createCell("高", { width: 1080, align: AlignmentType.CENTER }),
                        createCell("<15s", { width: 1020, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("字段配置", { width: 1500 }),
                        createCell("add_field_option", { width: 2700 }),
                        createCell("为多选字段新增候选值", { width: 3060 }),
                        createCell("中", { width: 1080, align: AlignmentType.CENTER }),
                        createCell("<2s", { width: 1020, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("度量计算", { width: 1500 }),
                        createCell("calculate_iteration_metrics", { width: 2700 }),
                        createCell("计算迭代度量指标", { width: 3060 }),
                        createCell("中", { width: 1080, align: AlignmentType.CENTER }),
                        createCell("<10s", { width: 1020, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("消息推送", { width: 1500 }),
                        createCell("send_wework_message", { width: 2700 }),
                        createCell("发送企微机器人消息", { width: 3060 }),
                        createCell("高", { width: 1080, align: AlignmentType.CENTER }),
                        createCell("<1s", { width: 1020, align: AlignmentType.CENTER })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第四章 ==========
            createHeading("四、智能体核心配置 (Agent Core Configuration)", HeadingLevel.HEADING_1),
            
            createHeading("4.1 系统提示词 (System Prompt)", HeadingLevel.HEADING_2),
            createPara("角色定义：你是【需求与问题管理智能助手】（IterAgent），一个专业的政企项目迭代管理AI助手。"),
            createPara("核心职责：", { bold: true }),
            new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "关联需求查询：快速获取迭代内需求的所有关联需求链接，支持跨空间", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "批量字段更新：一键批量更新迭代内需求的参评/承接迭代等多选字段", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "字段配置管理：为多选字段添加新的候选值", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "迭代度量计算：自动计算参评数、承接率、如期交付率等指标", size: 22, font: "Microsoft YaHei" })] }),
            new Paragraph({ numbering: { reference: "numbered-list-1", level: 0 }, children: [new TextRun({ text: "智能提醒推送：迭代节点提醒、待办项跟进、风险预警", size: 22, font: "Microsoft YaHei" })] }),
            
            createHeading("4.2 指令格式规范", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [3500, 5860],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("指令", { bold: true, bg: colors.headerBg, width: 3500, align: AlignmentType.CENTER }),
                        createCell("格式", { bold: true, bg: colors.headerBg, width: 5860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("获取关联需求链接", { width: 3500 }),
                        createCell("获取关联需求链接 <迭代名称>", { width: 5860 })
                    ]}),
                    new TableRow({ children: [
                        createCell("批量更新多选字段", { width: 3500 }),
                        createCell("批量追加更新迭代内需求的多选字段 <迭代> <字段> <值>", { width: 5860 })
                    ]}),
                    new TableRow({ children: [
                        createCell("添加字段候选值", { width: 3500 }),
                        createCell("添加需求多选字段候选值 <值> <字段1> [字段2]", { width: 5860 })
                    ]}),
                    new TableRow({ children: [
                        createCell("刷新度量", { width: 3500 }),
                        createCell("刷新迭代度量", { width: 5860 })
                    ]}),
                ]
            }),
            
            createHeading("4.3 模型选择与参数配置", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2340, 2340, 2340, 2340],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("配置项", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER }),
                        createCell("主模型", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER }),
                        createCell("备用模型", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER }),
                        createCell("说明", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("模型", { width: 2340 }),
                        createCell("DeepSeek V3", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("混元Pro", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("指令解析首选DeepSeek", { width: 2340 })
                    ]}),
                    new TableRow({ children: [
                        createCell("Temperature", { width: 2340 }),
                        createCell("0.1", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("0.1", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("低温度保证稳定性", { width: 2340 })
                    ]}),
                    new TableRow({ children: [
                        createCell("Max Tokens", { width: 2340 }),
                        createCell("2048", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("2048", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("支持长列表输出", { width: 2340 })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第五章 ==========
            createHeading("五、评估方法与成功标准 (Evaluation & Success Metrics)", HeadingLevel.HEADING_1),
            
            createHeading("5.1 效率指标", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2700, 1800, 1800, 1800, 1260],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("指标名称", { bold: true, bg: colors.headerBg, width: 2700, align: AlignmentType.CENTER }),
                        createCell("基线值", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("目标值", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("测量方法", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("提升倍数", { bold: true, bg: colors.headerBg, width: 1260, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("单次迭代管理耗时", { width: 2700 }),
                        createCell("4-6小时", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("<30分钟", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("流程跟踪", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("12倍+", { width: 1260, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("关联需求查询时间", { width: 2700 }),
                        createCell("30分钟", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("<30秒", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("API响应时间", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("60倍+", { width: 1260, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("批量更新执行时间", { width: 2700 }),
                        createCell("1小时", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("<1分钟", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("任务执行时间", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("60倍+", { width: 1260, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("度量统计时间", { width: 2700 }),
                        createCell("2小时", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("<1分钟", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("自动化", { width: 1800, align: AlignmentType.CENTER }),
                        createCell("120倍+", { width: 1260, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            createHeading("5.2 质量指标", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [3120, 2340, 2340, 1560],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("指标名称", { bold: true, bg: colors.headerBg, width: 3120, align: AlignmentType.CENTER }),
                        createCell("目标值", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER }),
                        createCell("测量方法", { bold: true, bg: colors.headerBg, width: 2340, align: AlignmentType.CENTER }),
                        createCell("状态", { bold: true, bg: colors.headerBg, width: 1560, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("指令识别准确率", { width: 3120 }),
                        createCell(">=99%", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("日志分析", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("达成", { width: 1560, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("字段更新成功率", { width: 3120 }),
                        createCell(">=99%", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("执行结果统计", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("达成", { width: 1560, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("度量计算准确率", { width: 3120 }),
                        createCell("100%", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("人工抽检", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("达成", { width: 1560, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("需求遗漏率", { width: 3120 }),
                        createCell("<2%", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("人工复核", { width: 2340, align: AlignmentType.CENTER }),
                        createCell("达成", { width: 1560, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第六章 ==========
            createHeading("六、创新亮点与技术特色", HeadingLevel.HEADING_1),
            
            createHeading("6.1 架构创新：零部署成本的Agent实现", HeadingLevel.HEADING_2),
            createQuote("本方案最大的创新在于：利用现有平台能力（TAPD + 企微 + 连接中台），实现零部署成本的Agent系统。"),
            
            new Table({
                columnWidths: [3120, 3120, 3120],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("创新点", { bold: true, bg: colors.headerBg, width: 3120, align: AlignmentType.CENTER }),
                        createCell("描述", { bold: true, bg: colors.headerBg, width: 3120, align: AlignmentType.CENTER }),
                        createCell("价值", { bold: true, bg: colors.headerBg, width: 3120, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("利用TAPD缺陷状态机", { bold: true, width: 3120 }),
                        createCell("将指令任务编码为缺陷，利用状态流转实现异步任务", { width: 3120 }),
                        createCell("无需部署独立后端", { width: 3120, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("复用自动化助手", { bold: true, width: 3120 }),
                        createCell("利用TAPD扩展自动化能力执行复杂逻辑", { width: 3120 }),
                        createCell("无需开发定时任务", { width: 3120, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("连接中台Agent", { bold: true, width: 3120 }),
                        createCell("利用现有平台能力实现消息监听和回复", { width: 3120 }),
                        createCell("无需开发机器人后端", { width: 3120, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            createHeading("6.2 场景创新：迭代管理全流程覆盖", HeadingLevel.HEADING_2),
            createPara("传统迭代管理 vs AI赋能对比："),
            new Table({
                columnWidths: [1800, 3780, 3780],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("阶段", { bold: true, bg: colors.headerBg, width: 1800, align: AlignmentType.CENTER }),
                        createCell("传统方式", { bold: true, bg: colors.warningBg, width: 3780, align: AlignmentType.CENTER }),
                        createCell("AI赋能", { bold: true, bg: colors.successBg, width: 3780, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("会前准备", { bold: true, width: 1800 }),
                        createCell("手动检查需求状态、逐个拖拽需求、手动导出链接（2小时+）", { width: 3780 }),
                        createCell("一键获取关联需求、自动状态检查（5秒）", { width: 3780 })
                    ]}),
                    new TableRow({ children: [
                        createCell("迭代会中", { bold: true, width: 1800 }),
                        createCell("手动记录待确认项、现场调整优先级", { width: 3780 }),
                        createCell("实时需求查询、智能建议", { width: 3780 })
                    ]}),
                    new TableRow({ children: [
                        createCell("会后处理", { bold: true, width: 1800 }),
                        createCell("手动添加候选值、手动批量更新、手动计算度量（2小时+）", { width: 3780 }),
                        createCell("一键添加候选值、一键批量更新、自动度量计算（1分钟）", { width: 3780 })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第七章 ==========
            createHeading("七、实战案例", HeadingLevel.HEADING_1),
            
            createHeading("案例一：迭代会后批量更新", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2340, 7020],
                rows: [
                    new TableRow({ children: [
                        createCell("场景", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("迭代24评审会后，需要批量更新15个需求的【参评迭代】字段", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("传统方式", { bold: true, bg: colors.warningBg, width: 2340 }),
                        createCell("逐个打开需求，手动勾选字段值，耗时30分钟+", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("AI方式", { bold: true, bg: colors.successBg, width: 2340 }),
                        createCell("发送指令【批量追加更新迭代内需求的多选字段 迭代24 参评迭代 迭代24】，15秒完成", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("效率提升", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("120倍", { width: 7020, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            createHeading("案例二：跨空间关联需求导出", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2340, 7020],
                rows: [
                    new TableRow({ children: [
                        createCell("场景", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("迭代会前需要获取待排期需求的所有关联需求链接，用于产研对齐", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("传统方式", { bold: true, bg: colors.warningBg, width: 2340 }),
                        createCell("逐个点击需求查看关联，手动复制链接，耗时1小时+", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("AI方式", { bold: true, bg: colors.successBg, width: 2340 }),
                        createCell("发送指令【获取关联需求链接 待排期】，5秒返回完整列表", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("效率提升", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("720倍", { width: 7020, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            createHeading("案例三：迭代度量自动化", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2340, 7020],
                rows: [
                    new TableRow({ children: [
                        createCell("场景", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("每周迭代会后需要更新度量页面，计算参评率、承接率、交付率", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("传统方式", { bold: true, bg: colors.warningBg, width: 2340 }),
                        createCell("手动统计各字段数量，计算比例，更新页面，耗时2小时", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("AI方式", { bold: true, bg: colors.successBg, width: 2340 }),
                        createCell("发送指令【刷新迭代度量】，30秒自动完成", { width: 7020 })
                    ]}),
                    new TableRow({ children: [
                        createCell("效率提升", { bold: true, bg: colors.headerBg, width: 2340 }),
                        createCell("240倍", { width: 7020, bg: colors.successBg })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 第八章 ==========
            createHeading("八、未来规划", HeadingLevel.HEADING_1),
            
            createHeading("8.1 演进路线图", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [1500, 1500, 3500, 2860],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("版本", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("时间", { bold: true, bg: colors.headerBg, width: 1500, align: AlignmentType.CENTER }),
                        createCell("内容", { bold: true, bg: colors.headerBg, width: 3500, align: AlignmentType.CENTER }),
                        createCell("状态", { bold: true, bg: colors.headerBg, width: 2860, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("V1.0", { bold: true, width: 1500, align: AlignmentType.CENTER }),
                        createCell("2026 Q1", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("4大指令任务上线、企微机器人集成、迭代度量页面", { width: 3500 }),
                        createCell("已完成", { width: 2860, align: AlignmentType.CENTER, bg: colors.successBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("V2.0", { bold: true, width: 1500, align: AlignmentType.CENTER }),
                        createCell("2026 Q2", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("自然语言理解增强、智能提醒推送、依赖关系图谱", { width: 3500 }),
                        createCell("进行中", { width: 2860, align: AlignmentType.CENTER, bg: colors.warningBg })
                    ]}),
                    new TableRow({ children: [
                        createCell("V3.0", { bold: true, width: 1500, align: AlignmentType.CENTER }),
                        createCell("2026 Q3", { width: 1500, align: AlignmentType.CENTER }),
                        createCell("迭代预测分析、风险智能预警、与更多系统集成", { width: 3500 }),
                        createCell("规划中", { width: 2860, align: AlignmentType.CENTER })
                    ]}),
                ]
            }),
            
            new Paragraph({ children: [new PageBreak()] }),
            
            // ========== 附录 ==========
            createHeading("附录", HeadingLevel.HEADING_1),
            
            createHeading("A. 指令速查表", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2700, 6660],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("指令", { bold: true, bg: colors.headerBg, width: 2700, align: AlignmentType.CENTER }),
                        createCell("示例", { bold: true, bg: colors.headerBg, width: 6660, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("获取关联需求链接", { width: 2700 }),
                        createCell("获取关联需求链接 待排期", { width: 6660 })
                    ]}),
                    new TableRow({ children: [
                        createCell("批量更新多选字段", { width: 2700 }),
                        createCell("批量追加更新迭代内需求的多选字段 迭代24 参评迭代 迭代24", { width: 6660 })
                    ]}),
                    new TableRow({ children: [
                        createCell("添加字段候选值", { width: 2700 }),
                        createCell("添加需求多选字段候选值 迭代25 参评迭代 承接迭代", { width: 6660 })
                    ]}),
                    new TableRow({ children: [
                        createCell("刷新度量", { width: 2700 }),
                        createCell("刷新迭代度量", { width: 6660 })
                    ]}),
                ]
            }),
            
            createHeading("B. 度量指标口径说明", HeadingLevel.HEADING_2),
            new Table({
                columnWidths: [2000, 4680, 2680],
                rows: [
                    new TableRow({ tableHeader: true, children: [
                        createCell("指标", { bold: true, bg: colors.headerBg, width: 2000, align: AlignmentType.CENTER }),
                        createCell("计算公式", { bold: true, bg: colors.headerBg, width: 4680, align: AlignmentType.CENTER }),
                        createCell("数据来源", { bold: true, bg: colors.headerBg, width: 2680, align: AlignmentType.CENTER })
                    ]}),
                    new TableRow({ children: [
                        createCell("参评数", { width: 2000 }),
                        createCell("COUNT(需求 WHERE 参评迭代 CONTAINS 迭代名)", { width: 4680 }),
                        createCell("参评迭代字段", { width: 2680 })
                    ]}),
                    new TableRow({ children: [
                        createCell("承接数", { width: 2000 }),
                        createCell("COUNT(需求 WHERE 承接迭代 CONTAINS 迭代名)", { width: 4680 }),
                        createCell("承接迭代字段", { width: 2680 })
                    ]}),
                    new TableRow({ children: [
                        createCell("如期交付数", { width: 2000 }),
                        createCell("COUNT(需求 WHERE 迭代=迭代名 AND 状态=已完成)", { width: 4680 }),
                        createCell("迭代+状态字段", { width: 2680 })
                    ]}),
                    new TableRow({ children: [
                        createCell("承接率", { width: 2000 }),
                        createCell("承接数 / 参评数 x 100%", { width: 4680 }),
                        createCell("计算", { width: 2680 })
                    ]}),
                    new TableRow({ children: [
                        createCell("如期交付率", { width: 2000 }),
                        createCell("如期交付数 / 承接数 x 100%", { width: 4680 }),
                        createCell("计算", { width: 2680 })
                    ]}),
                ]
            }),
            
            createHeading("C. 体验入口", HeadingLevel.HEADING_2),
            new Paragraph({
                shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                spacing: { before: 200, after: 200 },
                indent: { left: 360 },
                children: [new TextRun({ text: "需求与问题管理智能助手", size: 28, bold: true, color: colors.primary, font: "Microsoft YaHei" })]
            }),
            createPara("使用方式：在企微群中 @IterAgent 发送指令", { indent: 360 }),
            createPara("快速开始：发送【获取关联需求链接 待排期】体验", { indent: 360 }),
            createPara("反馈渠道：企微联系管理员", { indent: 360 }),
            
            new Paragraph({ spacing: { before: 600 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "-- 文档结束 --", size: 20, color: colors.light, font: "Microsoft YaHei" })]
            }),
            new Paragraph({ spacing: { before: 200 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                    new TextRun({ text: "文档版本: v1.0  |  更新日期: 2026-01-06  |  审核状态: 待审核", size: 18, color: colors.light, font: "Microsoft YaHei" })
                ]
            }),
        ]
    }]
});

// 保存文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("d:/AI/部门AI大赛/【AI创新技术方案书】需求与问题管理智能助手.docx", buffer);
    console.log("Word文档已生成: 【AI创新技术方案书】需求与问题管理智能助手.docx");
}).catch(err => {
    console.error("生成失败:", err);
});
