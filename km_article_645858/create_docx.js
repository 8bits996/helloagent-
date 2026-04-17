const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, 
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType, 
        ShadingType, LevelFormat } = require('docx');
const fs = require('fs');
const https = require('https');
const path = require('path');

// 文章内容
const articleTitle = "扬帆出海：AI赋能云业务全球化合规实战（含技术实现核心方案）";
const articleAuthor = "frankechen";
const articleDate = "2025-11-30 23:07";

// 文章结构化内容
const content = [
  { type: 'heading1', text: '导语' },
  { type: 'paragraph', text: '从0到1构建智能出海合规助手的完整方法论，基于腾讯云真实出海项目经验沉淀和AI平台赋能。核心问题：企业出海决策周期长(6+个月)、成本高、重复劳动严重等，解决方案：通过AI+知识库，打造智能方案和合规审核系统。' },
  
  { type: 'heading1', text: '第一部分：背景篇' },
  { type: 'heading2', text: '1.1 问题定义：出海三大核心痛点' },
  { type: 'heading3', text: '痛点1：产品可售性黑盒' },
  { type: 'paragraph', text: '📍 真实场景还原' },
  { type: 'paragraph', text: '时间：202X年X月 | 地点：腾讯云深圳总部 | 人物：销售XX vs 客户XX集团' },
  { type: 'code', text: `客户: "我们要在XX建数据中心，X,000台服务器的需求。"
销售: "没问题！我们XXX产品可以满足。"
客户: "大概多少钱，什么时候能交付？"
销售: "这个...让我确认一下产品团队，3天内回复您。"
客户: "3天？我们下周就要决策了，今天就能给方案。"

[3天后]
产品: "XXX需要Anatel认证，巴西还没做，需要6个月。"
销售: (内心OS: 糟了，项目要黄了...)

客户: "那不是3个月交付，而是9个月？！我们等不及。"` },

  { type: 'heading4', text: '问题根因分析' },
  { type: 'table', headers: ['层级', '为什么？', '根因'], rows: [
    ['Why 1', '为什么销售不知道？', '产品认证信息缺乏共享'],
    ['Why 2', '为什么信息未共享？', '信息散落在各个产品线和前端团队'],
    ['Why 3', '为什么信息散落？', '缺乏统一的分享平台'],
    ['Why 4', '为什么没有统一平台？', '没有意识到信息共享重要性'],
    ['Why 5', '为什么没有意识到？', '缺乏出海项目失败成本核算和复盘机制']
  ]},

  { type: 'heading4', text: '影响推导' },
  { type: 'table', headers: ['影响维度', '影响', '成本影响'], rows: [
    ['项目延期', '项目因信息不明确延期', '每个项目延期成本X'],
    ['客户流失', '客户因响应慢转向竞品', '每流失一个大客户损失X'],
    ['重复沟通', '每个问题多次转发', '内部沟通成本X/项目'],
    ['决策失误', 'X%项目因误判可行性失败', '沉没成本']
  ]},

  { type: 'paragraph', text: '总损失 = 项目延期 + 客户流失 + 流程推进沟通成本等', bold: true },

  { type: 'heading3', text: '痛点2：税务方案迷宫' },
  { type: 'paragraph', text: '💰 XXX项目税务对比' },
  { type: 'paragraph', text: '初版税负高达4X%，利润大头都被税务黑洞吃掉，对客报价缺乏竞争力。' },

  { type: 'heading4', text: '问题根因（问题树分解）' },
  { type: 'code', text: `为什么初版方案税负如此高?

根因1: 重复计税
- 腾讯利润 X M被当作SP成本再次征税
- 每一层交易都扩大税基

根因2: 交易结构不优
- SP转售模式是最差方案
- 未考虑本地主体和本地采购的税务优势

根因3: 缺乏国际税务专业知识
- 销售和产品不了解巴西税制
- 外部律师评估成本 XK且耗时4周

根因4: 决策依赖外部专家
- 每个项目都需要重新评估
- 无法沉淀税务优化模型` },

  { type: 'heading2', text: '1.2 方案创新：AI如何重构出海决策流程' },
  { type: 'heading3', text: '传统流程 vs AI赋能流程对比' },
  { type: 'table', headers: ['对比维度', '传统模式（4周）', 'AI模式（30秒）', '提升幅度'], rows: [
    ['评估周期', '4周（产品3天+法务2周+税务1周）', '90秒即时回答', '99.7%↓'],
    ['单项目成本', 'X（人工+外包）', 'X（AI边际成本）', '98%↓'],
    ['准确率', 'X%（人工主观判断）', 'X%（基于真实案例）', '41.5%↑']
  ]},

  { type: 'heading1', text: '第二部分：方法论篇' },
  { type: 'heading2', text: '2.1 方案实现：AI Agent与知识库落地' },
  { type: 'heading3', text: '工作流规划' },
  { type: 'code', text: `【第一层：整体规划】
企业出海合规智能决策系统
通过AI+知识库，将100+出海项目经验沉淀为可复用的决策系统

【第二层：三大支柱】
├─ 支柱1：产品可售性查询（即时回答）
│   - 为什么重要？避免盲目报价导致项目失败
│   - 怎么实现？数据中心开区表 + 认证清单 + 历史案例
│   - 效果如何？响应时间从3天→90秒
│
├─ 支柱2：税务优化方案（自动生成对比表）
│   - 为什么重要？税负差异可达X%影响成交
│   - 怎么实现？税率矩阵 + 交易结构优化 + 自动计算
└─ 支柱3：专家智能匹配（实时推荐）
    - 减少跨部门多次找人
    - 怎么实现？专家库 + 意图识别 + 协同工作流
    - 效果如何？对接时间从X天→即时推荐` },

  { type: 'paragraph', text: '价值预估：扬帆出海AI助手：让出海决策从6+个月缩短到X个月', bold: true },
  { type: 'paragraph', text: '核心价值：构建智能出海合规助手，通过AI+知识库，提前识别风险和解决，缩短整体流程时间。' },
  { type: 'paragraph', text: '产品可售性查询（3天→30秒）| 税务优化方案（节省X/项目）| 专家智能匹配（即时推荐）' },

  { type: 'heading3', text: '结合出海痛点，构建5大场景和工作流' },
  { type: 'table', headers: ['功能模块', '核心价值'], rows: [
    ['知识库检索', '查询目标国家法规和合规要求、产品文档'],
    ['场景分析', '收集项目信息，输出方案'],
    ['产品可行性查询', '30秒判断能否售卖'],
    ['税务优化方案', '节税方案规划'],
    ['对接人匹配', '即时推荐产品专家（持续接入中，当前仅接入CDC/CDZ产品）'],
    ['完整报告生成', '（基于场景规划中）']
  ]},

  { type: 'heading3', text: '场景化工作流详细构建方案' },
  { type: 'paragraph', text: '将高频痛点场景转化为标准化工作流，实现智能化问题解决。核心架构包含五大核心场景和智能化工作流引擎，通过意图识别、知识库检索、LLM大模型分析、代码解释器+插件、工作流执行五个关键环节实现落地。' },
  { type: 'paragraph', text: '核心价值：针对确定性高的场景，形成标准化SOP方案并通过Workflow固化，利用Code Interpreter+插件增强工作流能力；对于不确定性场景，通过LLM节点引入大模型智能应对。这种组合确保了输出质量可控、成本优化，同时保持应对复杂场景的灵活性。' },

  { type: 'heading2', text: '2.2 构建清晰高效的知识体系' },
  { type: 'heading3', text: '技术规格' },
  { type: 'heading4', text: '工具清单' },
  { type: 'table', headers: ['工具', '文件名', '功能', '代码量'], rows: [
    ['🕷️ 网页爬虫', 'web_scraper.py', '批量爬取网页，HTML转Markdown', '~350行'],
    ['📄 PDF解析器', 'pdf_parser.py', '解析PDF，提取文本表格目录', '~400行'],
    ['✨ 格式化器', 'formatter.py', '标准化格式，文本分片，质量评分', '~500行'],
    ['⚙️ 批量处理器', 'batch_processor.py', '整合所有工具，一键批量处理', '~350行']
  ]},

  { type: 'heading3', text: '知识库构建关键技术点' },
  { type: 'paragraph', text: '自动化搜集：基于沙箱环境的网页爬虫 + PDF解析，批量获取1600+篇文档，节省90%人工时间' },
  { type: 'paragraph', text: '智能格式化：标准Markdown格式，7维度质量评分，确保文档质量' },
  { type: 'paragraph', text: 'RAG优化：针对BGE-M3优化的分片策略，检索效果提升30%+' },

  { type: 'heading4', text: '最佳实践: 基于BGE-M3模型特性和大量测试得出的推荐配置' },
  { type: 'table', headers: ['文档类型', 'chunk_size', 'chunk_overlap', '策略', '原因'], rows: [
    ['法律法规', '512字符', '128字符 (25%)', '段落感知', '条款完整性重要'],
    ['产品文档', '768字符', '192字符 (25%)', '固定长度', '内容连续性强'],
    ['案例研究', '1024字符', '256字符 (25%)', '段落感知', '叙事完整性'],
    ['FAQ/问答', '384字符', '96字符 (25%)', '问答对', '一问一答独立']
  ]},

  { type: 'paragraph', text: '✅ 默认配置: chunk_size=512, overlap=128 - 适用于大多数合规文档' },

  { type: 'heading1', text: '第三部分：实战篇' },
  { type: 'heading2', text: '2.3 综合应用' },
  { type: 'paragraph', text: '进入界面后可在引导下咨询关心的问题。' },

  { type: 'heading2', text: '2.4 运营监控体系与持续优化' },
  { type: 'paragraph', text: '接入langfuse，对系统运行情况监控，针对性进行成本、性能分析和优化。' },
  { type: 'paragraph', text: '系统具备点赞、点踩功能，针对点踩的badcase可基于后台数据分析改进。' },

  { type: 'heading1', text: '3.1 总结与后续规划' },
  { type: 'heading2', text: '核心要点回顾' },
  { type: 'bullet', items: [
    '问题本质：出海合规评审最大挑战是信息缺失、合规评审专业性强和流程环节长',
    '解决方案：AI+知识库将历史经验沉淀为智能评估系统',
    '核心成果：评估周期↓ X%、风险提前X个月应对、年度节省XXX',
    '技术栈：AI Agent+LLM+工作流+30大类知识库+6大核心功能'
  ]},

  { type: 'heading2', text: '后续规划' },
  { type: 'bullet', items: [
    '更多知识库：接入更多产品，丰富知识库维度',
    '更多客户场景：工作流打磨和接入更多客户场景，方案持续打磨',
    '知识库分库：设置知识优先级，工作流根据查询类型路由到不同知识库，降低检索噪音和单库规模超大',
    '实时更新：知识库实时自动更新',
    '评测与改进：知识库评测'
  ]},

  { type: 'paragraph', text: '🌏 让每一个客户和产品都能成功扬帆出海', bold: true },
  { type: 'paragraph', text: '"智能新航海，合规不触礁"。面临出海和AI的大航海时代，采用AI技术，助力云业务出海合规评估、解决方案，打造出海合规咨询服务，护航云业务和中国企业出海。' }
];

// 创建表格边框样式
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

// 创建文档
function createDocument() {
  const children = [];
  
  // 标题
  children.push(new Paragraph({
    heading: HeadingLevel.TITLE,
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 },
    children: [new TextRun({ text: articleTitle, bold: true, size: 48 })]
  }));
  
  // 作者和日期
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 },
    children: [
      new TextRun({ text: `作者：${articleAuthor}  |  发布时间：${articleDate}`, size: 22, color: "666666" })
    ]
  }));
  
  // 分隔线
  children.push(new Paragraph({
    spacing: { after: 400 },
    children: [new TextRun({ text: "─".repeat(60), color: "CCCCCC" })]
  }));

  // 处理内容
  for (const item of content) {
    switch (item.type) {
      case 'heading1':
        children.push(new Paragraph({
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 },
          children: [new TextRun({ text: item.text, bold: true, size: 36, color: "0066CC" })]
        }));
        break;
      case 'heading2':
        children.push(new Paragraph({
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 150 },
          children: [new TextRun({ text: item.text, bold: true, size: 32, color: "333333" })]
        }));
        break;
      case 'heading3':
        children.push(new Paragraph({
          heading: HeadingLevel.HEADING_3,
          spacing: { before: 200, after: 100 },
          children: [new TextRun({ text: item.text, bold: true, size: 28, color: "444444" })]
        }));
        break;
      case 'heading4':
        children.push(new Paragraph({
          spacing: { before: 150, after: 100 },
          children: [new TextRun({ text: item.text, bold: true, size: 24, color: "555555" })]
        }));
        break;
      case 'paragraph':
        children.push(new Paragraph({
          spacing: { after: 150 },
          children: [new TextRun({ text: item.text, size: 22, bold: item.bold || false })]
        }));
        break;
      case 'code':
        children.push(new Paragraph({
          spacing: { before: 100, after: 100 },
          shading: { fill: "F5F5F5" },
          indent: { left: 360, right: 360 },
          children: [new TextRun({ text: item.text, size: 20, font: "Consolas" })]
        }));
        break;
      case 'bullet':
        for (const bulletItem of item.items) {
          children.push(new Paragraph({
            spacing: { after: 80 },
            indent: { left: 360 },
            children: [new TextRun({ text: `• ${bulletItem}`, size: 22 })]
          }));
        }
        break;
      case 'table':
        const rows = [];
        // 表头
        rows.push(new TableRow({
          tableHeader: true,
          children: item.headers.map(header => new TableCell({
            borders: cellBorders,
            shading: { fill: "E6F3FF", type: ShadingType.CLEAR },
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: header, bold: true, size: 20 })]
            })]
          }))
        }));
        // 数据行
        for (const row of item.rows) {
          rows.push(new TableRow({
            children: row.map(cell => new TableCell({
              borders: cellBorders,
              children: [new Paragraph({
                children: [new TextRun({ text: cell, size: 20 })]
              })]
            }))
          }));
        }
        children.push(new Table({
          rows: rows,
          width: { size: 100, type: WidthType.PERCENTAGE }
        }));
        children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));
        break;
    }
  }

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: "Microsoft YaHei", size: 22 }
        }
      },
      paragraphStyles: [
        { id: "Title", name: "Title", basedOn: "Normal",
          run: { size: 48, bold: true, font: "Microsoft YaHei" },
          paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, color: "0066CC", font: "Microsoft YaHei" },
          paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, color: "333333", font: "Microsoft YaHei" },
          paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, color: "444444", font: "Microsoft YaHei" },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } }
      ]
    },
    sections: [{
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: children
    }]
  });

  return doc;
}

async function main() {
  const doc = createDocument();
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(__dirname, '扬帆出海_AI赋能云业务全球化合规实战.docx'), buffer);
  console.log('文档已生成: 扬帆出海_AI赋能云业务全球化合规实战.docx');
}

main().catch(console.error);
