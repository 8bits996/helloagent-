const pptxgen = require('C:/Users/frankechen/AppData/Roaming/npm/node_modules/pptxgenjs');
const html2pptx = require('C:/Users/frankechen/.codebuddy/skills/pptx/scripts/html2pptx');
const fs = require('fs');
const path = require('path');

// 创建输出目录
const outputDir = 'c:/Users/frankechen/CodeBuddy/chrome/AI_规划_2026';
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// 创建slides目录
const slidesDir = path.join(outputDir, 'slides');
if (!fs.existsSync(slidesDir)) {
    fs.mkdirSync(slidesDir, { recursive: true });
}

// 颜色定义
const colors = {
    primary: '1a365d',
    secondary: '2c5282',
    accent: '3182ce',
    success: '38a169',
    warning: 'd69e2e',
    danger: 'e53e3e',
    light: 'f7fafc',
    dark: '1a202c',
    white: 'FFFFFF',
    gold: 'ecc94b',
    purple: '6b46c1'
};

let slideCounter = 0;

function createSlideHTML(title, content, type = 'content') {
    slideCounter++;
    let html = '';
    
    if (type === 'title') {
        html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #${colors.white}; }
body {
    width: 720pt; height: 405pt; margin: 0; padding: 0;
    background: #${colors.primary};
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.title-container {
    text-align: center;
    padding: 40pt;
}
h1 {
    color: #${colors.white};
    font-size: 36pt;
    margin: 0 0 20pt 0;
    font-weight: bold;
}
.subtitle {
    color: #${colors.gold};
    font-size: 20pt;
    margin: 0 0 30pt 0;
}
.divider {
    width: 200pt;
    height: 4pt;
    background: #${colors.gold};
    margin: 20pt auto;
}
.meta {
    color: #${colors.white};
    font-size: 14pt;
    margin-top: 30pt;
}
</style>
</head>
<body>
<div class="title-container">
    <h1>${title}</h1>
    <div class="divider"></div>
    <p class="subtitle">${content}</p>
    <p class="meta">2026年度规划 | 政企客户成功中心</p>
</div>
</body>
</html>`;
    } else if (type === 'section') {
        html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #${colors.white}; }
body {
    width: 720pt; height: 405pt; margin: 0; padding: 0;
    background: #${colors.primary};
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.section-num {
    color: #${colors.gold};
    font-size: 72pt;
    font-weight: bold;
    margin-bottom: 20pt;
}
h1 {
    color: #${colors.white};
    font-size: 42pt;
    margin: 0;
}
</style>
</head>
<body>
<p class="section-num">${content}</p>
<h1>${title}</h1>
</body>
</html>`;
    } else {
        html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #${colors.white}; }
body {
    width: 720pt; height: 405pt; margin: 0; padding: 0;
    background: #${colors.light};
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
}
.header {
    background: #${colors.primary};
    padding: 15pt 30pt;
}
h1 {
    color: #${colors.white};
    font-size: 22pt;
    margin: 0;
}
.content {
    flex: 1;
    padding: 20pt 30pt;
    overflow: hidden;
}
${content.css || ''}
</style>
</head>
<body>
<div class="header">
    <h1>${title}</h1>
</div>
<div class="content">
    ${content.html || content}
</div>
</body>
</html>`;
    }
    
    const filePath = path.join(slidesDir, `slide${slideCounter}.html`);
    fs.writeFileSync(filePath, html);
    return filePath;
}

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = '政企客户成功中心';
    pptx.title = '2026年度AI战略规划';
    pptx.subject = 'AI战略规划 - 五看三定框架';
    
    console.log('开始创建AI年度规划PPT...');
    
    // Slide 1: 封面
    console.log('创建封面...');
    await html2pptx(createSlideHTML('AI赋能·智领未来', '政企客户成功中心 2026年度AI战略规划', 'title'), pptx);
    
    // Slide 2: 目录
    const tocContent = {
        css: `
.toc-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12pt;
    height: 100%;
}
.toc-item {
    background: #${colors.white};
    border-left: 5pt solid #${colors.accent};
    padding: 12pt 15pt;
    display: flex;
    align-items: center;
    border-radius: 0 6pt 6pt 0;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
}
.toc-num {
    font-size: 26pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-right: 12pt;
}
.toc-text {
    font-size: 13pt;
    color: #${colors.dark};
}
`,
        html: `
<div class="toc-grid">
    <div class="toc-item"><span class="toc-num">01</span><span class="toc-text">五看分析：洞察趋势与机会</span></div>
    <div class="toc-item"><span class="toc-num">02</span><span class="toc-text">三定规划：明确战略与目标</span></div>
    <div class="toc-item"><span class="toc-num">03</span><span class="toc-text">战略屋：整体架构设计</span></div>
    <div class="toc-item"><span class="toc-num">04</span><span class="toc-text">小组规划框架与目标</span></div>
    <div class="toc-item"><span class="toc-num">05</span><span class="toc-text">实施路径与里程碑</span></div>
    <div class="toc-item"><span class="toc-num">06</span><span class="toc-text">资源保障与预期成效</span></div>
</div>
`
    };
    await html2pptx(createSlideHTML('目录', tocContent), pptx);
    
    // Slide 3: 五看分隔页
    await html2pptx(createSlideHTML('五看分析', '01', 'section'), pptx);
    
    // Slide 4: 五看框架
    const wukangContent = {
        css: `
.framework {
    display: flex;
    justify-content: space-between;
    height: 100%;
    gap: 8pt;
}
.wu-item {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt 8pt;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.wu-icon {
    font-size: 26pt;
    margin-bottom: 8pt;
}
.wu-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 6pt;
}
.wu-desc {
    font-size: 9pt;
    color: #666;
    text-align: center;
    line-height: 1.4;
}
`,
        html: `
<div class="framework">
    <div class="wu-item">
        <div class="wu-icon">📈</div>
        <div class="wu-title">看趋势</div>
        <div class="wu-desc">AI技术发展趋势<br/>行业变革方向</div>
    </div>
    <div class="wu-item">
        <div class="wu-icon">🎯</div>
        <div class="wu-title">看市场</div>
        <div class="wu-desc">客户需求变化<br/>市场机会窗口</div>
    </div>
    <div class="wu-item">
        <div class="wu-icon">⚔️</div>
        <div class="wu-title">看竞争</div>
        <div class="wu-desc">竞争对手布局<br/>行业最佳实践</div>
    </div>
    <div class="wu-item">
        <div class="wu-icon">🔍</div>
        <div class="wu-title">看自己</div>
        <div class="wu-desc">内部能力评估<br/>优势与短板</div>
    </div>
    <div class="wu-item">
        <div class="wu-icon">💡</div>
        <div class="wu-title">看机会</div>
        <div class="wu-desc">战略机会点<br/>破局切入点</div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('五看分析框架', wukangContent), pptx);
    
    // Slide 5: 看趋势
    const trendContent = {
        css: `
.trend-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15pt;
    height: 100%;
}
.trend-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.trend-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 10pt;
    padding-bottom: 6pt;
    border-bottom: 2pt solid #${colors.accent};
}
.trend-list {
    font-size: 10pt;
    color: #333;
    line-height: 1.5;
}
.trend-list ul {
    margin: 0;
    padding-left: 16pt;
}
.trend-list li {
    margin-bottom: 5pt;
}
.highlight {
    color: #${colors.accent};
    font-weight: bold;
}
`,
        html: `
<div class="trend-container">
    <div class="trend-card">
        <div class="trend-title">🚀 技术演进趋势</div>
        <div class="trend-list">
            <ul>
                <li><span class="highlight">Agentic AI时代</span>：从对话助手到自主智能体</li>
                <li><span class="highlight">多模态融合</span>：文本+图像+语音+代码统一处理</li>
                <li><span class="highlight">上下文工程</span>：长上下文、RAG成为标配</li>
                <li><span class="highlight">模型即服务</span>：推理成本持续下降</li>
            </ul>
        </div>
    </div>
    <div class="trend-card">
        <div class="trend-title">🏢 产业应用趋势</div>
        <div class="trend-list">
            <ul>
                <li><span class="highlight">数字分身/员工</span>：7×24小时AI工作伙伴</li>
                <li><span class="highlight">个人AI助理</span>：Clawbot爆火，Agentic工作流</li>
                <li><span class="highlight">复利工程</span>：知识沉淀成为核心竞争力</li>
                <li><span class="highlight">人机协作</span>：从工具使用到组织原生AI</li>
            </ul>
        </div>
    </div>
    <div class="trend-card">
        <div class="trend-title">📊 关键行业报告</div>
        <div class="trend-list">
            <ul>
                <li>Google Cloud AI Agent Trends 2026</li>
                <li>麦肯锡：AI生产力规模化应用</li>
                <li>Gartner：2026年80%企业使用AI Agent</li>
            </ul>
        </div>
    </div>
    <div class="trend-card">
        <div class="trend-title">🎯 关键判断</div>
        <div class="trend-list">
            <ul>
                <li>2026年是<span class="highlight">Agentic元年</span></li>
                <li>从"会用AI"到"用好AI"的质变期</li>
                <li>组织AI能力成为核心竞争壁垒</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('看趋势：2026 AI技术发展趋势', trendContent), pptx);
    
    // Slide 6: 看市场
    const marketContent = {
        css: `
.market-container {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 15pt;
    height: 100%;
}
.market-left {
    display: flex;
    flex-direction: column;
    gap: 10pt;
}
.pain-card {
    background: #${colors.white};
    border-left: 4pt solid #${colors.danger};
    padding: 10pt 12pt;
    border-radius: 0 6pt 6pt 0;
}
.pain-title {
    font-size: 11pt;
    font-weight: bold;
    color: #${colors.danger};
    margin-bottom: 4pt;
}
.pain-desc {
    font-size: 9pt;
    color: #555;
}
.market-right {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
}
.need-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.success};
    margin-bottom: 10pt;
}
.need-list {
    font-size: 10pt;
    line-height: 1.7;
}
.need-list ul {
    margin: 0;
    padding-left: 16pt;
}
`,
        html: `
<div class="market-container">
    <div class="market-left">
        <div class="pain-card">
            <div class="pain-title">⚠️ 合同评审效率瓶颈</div>
            <div class="pain-desc">人工2-3天/份，风险条款易遗漏，峰值期积压严重</div>
        </div>
        <div class="pain-card">
            <div class="pain-title">⚠️ 项目清淤难度大</div>
            <div class="pain-desc">历史项目积压，人工梳理耗时长，损益难量化</div>
        </div>
        <div class="pain-card">
            <div class="pain-title">⚠️ 出海合规复杂度高</div>
            <div class="pain-desc">多国法规复杂，决策周期6+月，专家资源稀缺</div>
        </div>
        <div class="pain-card">
            <div class="pain-title">⚠️ 知识传承断层</div>
            <div class="pain-desc">经验分散难沉淀，培训成本高，人员流动知识流失</div>
        </div>
    </div>
    <div class="market-right">
        <div class="need-title">✅ AI赋能机会点</div>
        <div class="need-list">
            <ul>
                <li>智能合同评审与风险识别</li>
                <li>项目健康度智能诊断</li>
                <li>出海合规知识库与问答</li>
                <li>客户成功智能助手</li>
                <li>培训赋能体系升级</li>
                <li>内部流程自动化</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('看市场/客户：需求洞察与痛点分析', marketContent), pptx);
    
    // Slide 7: 看竞争
    const competeContent = {
        css: `
.compete-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15pt;
    height: 100%;
}
.compete-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
}
.compete-title {
    font-size: 13pt;
    font-weight: bold;
    margin-bottom: 10pt;
    padding-bottom: 6pt;
    border-bottom: 2pt solid;
}
.internal .compete-title {
    color: #${colors.primary};
    border-color: #${colors.primary};
}
.external .compete-title {
    color: #${colors.success};
    border-color: #${colors.success};
}
.compete-list {
    font-size: 9pt;
    line-height: 1.6;
}
.compete-list ul {
    margin: 0;
    padding-left: 14pt;
}
.compete-list li {
    margin-bottom: 6pt;
}
.sub-title {
    font-weight: bold;
    color: #${colors.dark};
    margin: 8pt 0 4pt 0;
}
`,
        html: `
<div class="compete-container">
    <div class="compete-card internal">
        <div class="compete-title">🏢 内部竞争格局</div>
        <div class="compete-list">
            <div class="sub-title">腾讯研究院 - 晓辉博士</div>
            <ul>
                <li>复利工程、FDE（前沿部署工程师）</li>
                <li>组织级AI能力建设探索</li>
            </ul>
            <div class="sub-title">余一 - AIasme</div>
            <ul>
                <li>数字分身技术探索</li>
                <li>个人AI品牌建设</li>
            </ul>
            <div class="sub-title">安灯、云一、TEG等团队</div>
            <ul>
                <li>研发场景下的AI提效实践</li>
                <li>团队复利工程探索</li>
            </ul>
        </div>
    </div>
    <div class="compete-card external">
        <div class="compete-title">🌐 外部对标分析</div>
        <div class="compete-list">
            <div class="sub-title">公司AI专家 Jeff</div>
            <ul>
                <li>"AI领导力进化论：从超级个体到超级军团"</li>
                <li>7×24小时个人秘书贾维斯概念</li>
            </ul>
            <div class="sub-title">行业领先实践</div>
            <ul>
                <li>京东数字员工、数字军团</li>
                <li>Clawbot个人AI助理</li>
                <li>Anthropic Claude Code工程实践</li>
                <li>OpenAI Codex规模化应用</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('看竞争：内外部AI能力建设对标', competeContent), pptx);
    
    // Slide 8: 看自己
    const selfContent = {
        css: `
.self-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12pt;
    height: 100%;
}
.status-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
}
.status-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.achievement-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6pt;
}
.ach-item {
    background: #f0f7ff;
    padding: 8pt;
    border-radius: 6pt;
    text-align: center;
}
.ach-num {
    font-size: 18pt;
    font-weight: bold;
    color: #${colors.accent};
}
.ach-label {
    font-size: 8pt;
    color: #666;
}
.gap-list {
    font-size: 9pt;
    line-height: 1.7;
}
.gap-list ul {
    margin: 0;
    padding-left: 14pt;
}
.gap-list li {
    margin-bottom: 5pt;
}
`,
        html: `
<div class="self-container">
    <div class="status-card">
        <div class="status-title">🏆 已有成果（2025）</div>
        <div class="achievement-grid">
            <div class="ach-item">
                <div class="ach-num">13</div>
                <div class="ach-label">AI智能体</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">8</div>
                <div class="ach-label">已上线</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">50+</div>
                <div class="ach-label">项目评审</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">60+</div>
                <div class="ach-label">用户数</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">2000万</div>
                <div class="ach-label">年节省</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">4</div>
                <div class="ach-label">KM沉淀</div>
            </div>
        </div>
    </div>
    <div class="status-card">
        <div class="status-title">📋 核心能力盘点</div>
        <div class="gap-list">
            <ul>
                <li><b>鹰眼-合同智审</b>：99.7%效率提升</li>
                <li><b>项目AI问诊</b>：188项目，231万损益</li>
                <li><b>扬帆出海合规</b>：60+用户，70+MB知识库</li>
                <li><b>AI学习助教</b>：200+人培训覆盖</li>
                <li><b>技术底座</b>：Dify+RAG+MCP</li>
            </ul>
        </div>
    </div>
    <div class="status-card" style="grid-column: span 2;">
        <div class="status-title">⚠️ 差距与提升空间</div>
        <div class="gap-list">
            <ul>
                <li>Agent自主化程度有待提升，当前多为辅助型</li>
                <li>知识沉淀体系化不足，经验复用率需提高</li>
                <li>跨团队协作深度有限，复利效应未充分释放</li>
                <li>个人AI助理覆盖率低，规模化推广待加强</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('看自己：现状盘点与能力评估', selfContent), pptx);
    
    // Slide 9: 看机会
    const oppContent = {
        css: `
.opp-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12pt;
    height: 100%;
}
.opp-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
    display: flex;
    flex-direction: column;
}
.opp-header {
    display: flex;
    align-items: center;
    margin-bottom: 8pt;
}
.opp-icon {
    font-size: 22pt;
    margin-right: 8pt;
}
.opp-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
}
.opp-desc {
    font-size: 9pt;
    color: #555;
    line-height: 1.4;
    flex: 1;
}
.opp-tag {
    background: #${colors.accent};
    color: white;
    padding: 2pt 6pt;
    border-radius: 3pt;
    font-size: 8pt;
    display: inline-block;
    margin-top: 6pt;
    align-self: flex-start;
}
`,
        html: `
<div class="opp-container">
    <div class="opp-card">
        <div class="opp-header">
            <span class="opp-icon">🎯</span>
            <span class="opp-title">机会点1：Agent规模化</span>
        </div>
        <div class="opp-desc">
            从13个智能体扩展到全员覆盖，打造"人均AI助理"工作模式，实现从辅助工具到生产力核心的跃迁。
        </div>
        <span class="opp-tag">高优先级</span>
    </div>
    <div class="opp-card">
        <div class="opp-header">
            <span class="opp-icon">🔄</span>
            <span class="opp-title">机会点2：复利工程体系</span>
        </div>
        <div class="opp-desc">
            构建知识沉淀-复用-进化的飞轮，让每次项目经验转化为组织能力，实现边际成本递减。
        </div>
        <span class="opp-tag">核心战略</span>
    </div>
    <div class="opp-card">
        <div class="opp-header">
            <span class="opp-icon">🤖</span>
            <span class="opp-title">机会点3：数字分身探索</span>
        </div>
        <div class="opp-desc">
            探索数字员工、个人AI助理落地，构建7×24小时服务能力，打造差异化竞争优势。
        </div>
        <span class="opp-tag">创新突破</span>
    </div>
    <div class="opp-card">
        <div class="opp-header">
            <span class="opp-icon">🌐</span>
            <span class="opp-title">机会点4：生态协同</span>
        </div>
        <div class="opp-desc">
            与研究院、TEG等团队深度协同，共享复利工程成果，形成组织级AI能力网络。
        </div>
        <span class="opp-tag">战略合作</span>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('看机会：战略机会点识别', oppContent), pptx);
    
    console.log('五看分析部分完成！');
    
    // 保存第一部分
    const outputPath1 = path.join(outputDir, 'AI战略规划_五看分析.pptx');
    await pptx.writeFile({ fileName: outputPath1 });
    console.log(`第一部分已保存: ${outputPath1}`);
    
    // ===== 第二部分：三定规划 =====
    
    const pptx2 = new pptxgen();
    pptx2.layout = 'LAYOUT_16x9';
    pptx2.author = '政企客户成功中心';
    pptx2.title = '2026年度AI战略规划';
    pptx2.subject = 'AI战略规划 - 三定规划';
    
    slideCounter = 0;
    
    // Slide 10: 三定分隔页
    await html2pptx(createSlideHTML('三定规划', '02', 'section'), pptx2);
    
    // Slide 11: 三定框架
    const sandingContent = {
        css: `
.sanding-container {
    display: flex;
    justify-content: space-between;
    height: 100%;
    gap: 15pt;
}
.ding-item {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.ding-num {
    font-size: 36pt;
    font-weight: bold;
    color: #${colors.gold};
    margin-bottom: 5pt;
}
.ding-title {
    font-size: 16pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 10pt;
}
.ding-content {
    font-size: 10pt;
    color: #555;
    text-align: left;
    line-height: 1.5;
}
.ding-content ul {
    margin: 0;
    padding-left: 14pt;
}
.ding-content li {
    margin-bottom: 5pt;
}
`,
        html: `
<div class="sanding-container">
    <div class="ding-item">
        <div class="ding-num">定</div>
        <div class="ding-title">定战略</div>
        <div class="ding-content">
            <ul>
                <li>Agentic AI战略定位</li>
                <li>复利工程核心路径</li>
                <li>组织AI能力建设</li>
            </ul>
        </div>
    </div>
    <div class="ding-item">
        <div class="ding-num">定</div>
        <div class="ding-title">定目标</div>
        <div class="ding-content">
            <ul>
                <li>量化业务指标</li>
                <li>能力建设目标</li>
                <li>覆盖率与渗透度</li>
            </ul>
        </div>
    </div>
    <div class="ding-item">
        <div class="ding-num">定</div>
        <div class="ding-title">定策略</div>
        <div class="ding-content">
            <ul>
                <li>实施路径规划</li>
                <li>关键举措分解</li>
                <li>资源保障机制</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('三定规划框架', sandingContent), pptx2);
    
    // Slide 12: 定战略
    const strategyContent = {
        css: `
.strategy-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15pt;
    height: 100%;
}
.strategy-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
}
.strategy-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 10pt;
    padding-bottom: 6pt;
    border-bottom: 2pt solid #${colors.accent};
}
.strategy-content {
    font-size: 10pt;
    line-height: 1.6;
}
.strategy-content ul {
    margin: 0;
    padding-left: 14pt;
}
.strategy-content li {
    margin-bottom: 6pt;
}
.highlight-box {
    background: #fffbeb;
    border: 1pt solid #${colors.gold};
    padding: 10pt;
    border-radius: 6pt;
    margin-top: 10pt;
}
.highlight-text {
    font-size: 11pt;
    font-weight: bold;
    color: #${colors.primary};
    text-align: center;
}
`,
        html: `
<div class="strategy-container">
    <div class="strategy-card">
        <div class="strategy-title">🎯 战略定位</div>
        <div class="strategy-content">
            <ul>
                <li><b>愿景</b>：成为公司AI赋能标杆团队</li>
                <li><b>使命</b>：让AI成为每个人的超级助手</li>
                <li><b>价值观</b>：复利思维、持续进化、开放协同</li>
            </ul>
            <div class="highlight-box">
                <div class="highlight-text">从「AI辅助」到「AI原生」<br/>从「工具使用」到「组织进化」</div>
            </div>
        </div>
    </div>
    <div class="strategy-card">
        <div class="strategy-title">🔄 复利工程战略</div>
        <div class="strategy-content">
            <ul>
                <li><b>知识沉淀</b>：每次项目经验编码为可复用资产</li>
                <li><b>经验复用</b>：通过Context工程实现知识自动加载</li>
                <li><b>持续进化</b>：建立反馈闭环，越用越聪明</li>
                <li><b>规模效应</b>：边际成本递减，组织智慧复利增长</li>
            </ul>
        </div>
    </div>
    <div class="strategy-card" style="grid-column: span 2;">
        <div class="strategy-title">📋 三大核心战略方向</div>
        <div class="strategy-content">
            <ul>
                <li><b>方向一：Agent规模化部署</b> - 实现全员AI助理覆盖，从13个智能体扩展到50+场景</li>
                <li><b>方向二：复利工程体系建设</b> - 构建知识沉淀-复用-进化飞轮，实现经验资产化</li>
                <li><b>方向三：数字分身探索</b> - 试点数字员工，探索7×24小时AI服务模式</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('定战略：AI赋能战略定位', strategyContent), pptx2);
    
    // Slide 13: 定目标
    const targetContent = {
        css: `
.target-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12pt;
    height: 100%;
}
.target-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
}
.target-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.target-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6pt 0;
    border-bottom: 1pt solid #eee;
}
.target-item:last-child {
    border-bottom: none;
}
.target-label {
    font-size: 10pt;
    color: #555;
}
.target-value {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.accent};
}
.target-value.highlight {
    color: #${colors.success};
}
`,
        html: `
<div class="target-container">
    <div class="target-card">
        <div class="target-title">📊 业务指标目标</div>
        <div class="target-item">
            <span class="target-label">AI智能体数量</span>
            <span class="target-value">13 → 50+</span>
        </div>
        <div class="target-item">
            <span class="target-label">活跃用户覆盖率</span>
            <span class="target-value">60 → 100人</span>
        </div>
        <div class="target-item">
            <span class="target-label">预计年节省成本</span>
            <span class="target-value highlight">2000万 → 5000万</span>
        </div>
        <div class="target-item">
            <span class="target-label">效率提升幅度</span>
            <span class="target-value">平均50%+</span>
        </div>
    </div>
    <div class="target-card">
        <div class="target-title">🎯 能力建设目标</div>
        <div class="target-item">
            <span class="target-label">知识库覆盖</span>
            <span class="target-value">70MB → 200MB</span>
        </div>
        <div class="target-item">
            <span class="target-label">KM沉淀文章</span>
            <span class="target-value">4 → 20篇</span>
        </div>
        <div class="target-item">
            <span class="target-label">培训覆盖人次</span>
            <span class="target-value">200 → 500人</span>
        </div>
        <div class="target-item">
            <span class="target-label">Agent自主化率</span>
            <span class="target-value">20% → 60%</span>
        </div>
    </div>
    <div class="target-card" style="grid-column: span 2;">
        <div class="target-title">🚀 关键里程碑目标</div>
        <div class="target-item">
            <span class="target-label">Q1：完成复盘与规划，启动复利工程</span>
            <span class="target-value">完成</span>
        </div>
        <div class="target-item">
            <span class="target-label">Q2：Agent规模化推广，覆盖核心场景</span>
            <span class="target-value">30个Agent</span>
        </div>
        <div class="target-item">
            <span class="target-label">Q3：数字分身试点，探索新服务模式</span>
            <span class="target-value">2个试点</span>
        </div>
        <div class="target-item">
            <span class="target-label">Q4：全面复盘，形成可复制方法论</span>
            <span class="target-value">方法论输出</span>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('定目标：2026年度核心目标', targetContent), pptx2);
    
    // Slide 14: 定策略
    const tacticContent = {
        css: `
.tactic-container {
    display: flex;
    flex-direction: column;
    gap: 10pt;
    height: 100%;
}
.tactic-row {
    display: flex;
    gap: 12pt;
    flex: 1;
}
.tactic-card {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
}
.tactic-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.tactic-list {
    font-size: 9pt;
    line-height: 1.5;
}
.tactic-list ul {
    margin: 0;
    padding-left: 14pt;
}
.tactic-list li {
    margin-bottom: 4pt;
}
`,
        html: `
<div class="tactic-container">
    <div class="tactic-row">
        <div class="tactic-card">
            <div class="tactic-title">🎯 策略一：Agent规模化</div>
            <div class="tactic-list">
                <ul>
                    <li>梳理全业务流程，识别AI赋能点</li>
                    <li>按优先级分批次开发部署Agent</li>
                    <li>建立Agent使用培训与推广机制</li>
                    <li>构建Agent效果评估与优化体系</li>
                </ul>
            </div>
        </div>
        <div class="tactic-card">
            <div class="tactic-title">🔄 策略二：复利工程</div>
            <div class="tactic-list">
                <ul>
                    <li>建立Context规范与知识分层体系</li>
                    <li>每次项目强制沉淀可复用经验</li>
                    <li>构建Skills和Rules共享机制</li>
                    <li>定期Review与知识资产更新</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="tactic-row">
        <div class="tactic-card">
            <div class="tactic-title">🤖 策略三：数字分身</div>
            <div class="tactic-list">
                <ul>
                    <li>选择高频标准化场景试点</li>
                    <li>构建数字员工工作流</li>
                    <li>探索7×24小时服务模式</li>
                    <li>评估效果并决定是否推广</li>
                </ul>
            </div>
        </div>
        <div class="tactic-card">
            <div class="tactic-title">🌐 策略四：生态协同</div>
            <div class="tactic-list">
                <ul>
                    <li>与研究院建立复利工程协作</li>
                    <li>参与TEG技术中台共建</li>
                    <li>输出最佳实践到更大范围</li>
                    <li>引入外部先进经验与方法</li>
                </ul>
            </div>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('定策略：四大实施策略', tacticContent), pptx2);
    
    console.log('三定规划部分完成！');
    
    // 保存第二部分
    const outputPath2 = path.join(outputDir, 'AI战略规划_三定规划.pptx');
    await pptx2.writeFile({ fileName: outputPath2 });
    console.log(`第二部分已保存: ${outputPath2}`);
    
    // ===== 第三部分：战略屋与实施 =====
    
    const pptx3 = new pptxgen();
    pptx3.layout = 'LAYOUT_16x9';
    pptx3.author = '政企客户成功中心';
    pptx3.title = '2026年度AI战略规划';
    pptx3.subject = 'AI战略规划 - 战略屋与实施';
    
    slideCounter = 0;
    
    // Slide 15: 战略屋分隔页
    await html2pptx(createSlideHTML('战略屋', '03', 'section'), pptx3);
    
    // Slide 16: 战略屋
    const houseContent = {
        css: `
.house-container {
    display: flex;
    flex-direction: column;
    gap: 8pt;
    height: 100%;
}
.house-roof {
    background: linear-gradient(135deg, #${colors.primary} 0%, #${colors.secondary} 100%);
    color: white;
    padding: 12pt;
    text-align: center;
    border-radius: 8pt 8pt 0 0;
}
.house-roof-title {
    font-size: 14pt;
    font-weight: bold;
}
.house-body {
    display: flex;
    gap: 10pt;
    flex: 1;
}
.house-pillar {
    flex: 1;
    background: #${colors.white};
    border: 2pt solid #${colors.accent};
    border-radius: 6pt;
    padding: 10pt;
}
.pillar-title {
    font-size: 11pt;
    font-weight: bold;
    color: #${colors.primary};
    text-align: center;
    margin-bottom: 8pt;
    padding-bottom: 4pt;
    border-bottom: 1pt solid #${colors.accent};
}
.pillar-content {
    font-size: 9pt;
    line-height: 1.4;
}
.pillar-content ul {
    margin: 0;
    padding-left: 12pt;
}
.pillar-content li {
    margin-bottom: 3pt;
}
.house-base {
    background: #${colors.light};
    border: 2pt solid #${colors.success};
    border-radius: 0 0 8pt 8pt;
    padding: 10pt;
}
.base-title {
    font-size: 11pt;
    font-weight: bold;
    color: #${colors.success};
    text-align: center;
    margin-bottom: 6pt;
}
.base-content {
    display: flex;
    justify-content: space-around;
    font-size: 9pt;
}
`,
        html: `
<div class="house-container">
    <div class="house-roof">
        <div class="house-roof-title">🏆 愿景：成为公司AI赋能标杆团队</div>
    </div>
    <div class="house-body">
        <div class="house-pillar">
            <div class="pillar-title">🎯 Agent规模化</div>
            <div class="pillar-content">
                <ul>
                    <li>50+智能体覆盖</li>
                    <li>全场景AI赋能</li>
                    <li>人均AI助理</li>
                    <li>效率提升50%+</li>
                </ul>
            </div>
        </div>
        <div class="house-pillar">
            <div class="pillar-title">🔄 复利工程</div>
            <div class="pillar-content">
                <ul>
                    <li>知识沉淀体系</li>
                    <li>经验复用机制</li>
                    <li>Context工程</li>
                    <li>组织智慧增长</li>
                </ul>
            </div>
        </div>
        <div class="house-pillar">
            <div class="pillar-title">🤖 数字分身</div>
            <div class="pillar-content">
                <ul>
                    <li>数字员工试点</li>
                    <li>7×24服务</li>
                    <li>新服务模式</li>
                    <li>差异化优势</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="house-base">
        <div class="base-title">🏗️ 支撑体系</div>
        <div class="base-content">
            <span>技术底座</span>
            <span>人才体系</span>
            <span>知识管理</span>
            <span>生态协同</span>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('战略屋：整体架构设计', houseContent), pptx3);
    
    // Slide 17: 小组规划框架
    const groupContent = {
        css: `
.group-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12pt;
    height: 100%;
}
.group-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
    border-top: 4pt solid #${colors.accent};
}
.group-name {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.group-section {
    margin-bottom: 8pt;
}
.group-section-title {
    font-size: 10pt;
    font-weight: bold;
    color: #${colors.dark};
    margin-bottom: 4pt;
}
.group-list {
    font-size: 9pt;
    line-height: 1.4;
    color: #555;
}
.group-list ul {
    margin: 0;
    padding-left: 12pt;
}
`,
        html: `
<div class="group-container">
    <div class="group-card">
        <div class="group-name">🎯 业务组A</div>
        <div class="group-section">
            <div class="group-section-title">目标</div>
            <div class="group-list">合同评审AI覆盖率100%，效率提升80%</div>
        </div>
        <div class="group-section">
            <div class="group-section-title">关键举措</div>
            <div class="group-list">
                <ul>
                    <li>鹰眼智审优化升级</li>
                    <li>新场景Agent开发</li>
                    <li>团队培训赋能</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="group-card">
        <div class="group-name">🎯 业务组B</div>
        <div class="group-section">
            <div class="group-section-title">目标</div>
            <div class="group-list">项目AI问诊覆盖200+项目，损益量化500万</div>
        </div>
        <div class="group-section">
            <div class="group-section-title">关键举措</div>
            <div class="group-list">
                <ul>
                    <li>问诊Agent能力提升</li>
                    <li>历史项目数据治理</li>
                    <li>知识库持续完善</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="group-card">
        <div class="group-name">🎯 业务组C</div>
        <div class="group-section">
            <div class="group-section-title">目标</div>
            <div class="group-list">出海合规服务100+用户，决策效率提升60%</div>
        </div>
        <div class="group-section">
            <div class="group-section-title">关键举措</div>
            <div class="group-list">
                <ul>
                    <li>知识库扩容至200MB</li>
                    <li>多语言支持增强</li>
                    <li>合规流程自动化</li>
                </ul>
            </div>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('小组规划框架：各组目标与举措', groupContent), pptx3);
    
    // Slide 18: 实施路径
    const roadmapContent = {
        css: `
.roadmap-container {
    display: flex;
    flex-direction: column;
    gap: 10pt;
    height: 100%;
}
.quarter-row {
    display: flex;
    gap: 10pt;
    flex: 1;
}
.quarter-card {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
    border-left: 5pt solid;
}
.q1 { border-color: #${colors.accent}; }
.q2 { border-color: #${colors.success}; }
.q3 { border-color: #${colors.warning}; }
.q4 { border-color: #${colors.purple}; }
.quarter-title {
    font-size: 12pt;
    font-weight: bold;
    margin-bottom: 8pt;
}
.q1 .quarter-title { color: #${colors.accent}; }
.q2 .quarter-title { color: #${colors.success}; }
.q3 .quarter-title { color: #${colors.warning}; }
.q4 .quarter-title { color: #${colors.purple}; }
.quarter-content {
    font-size: 9pt;
    line-height: 1.4;
}
.quarter-content ul {
    margin: 0;
    padding-left: 12pt;
}
`,
        html: `
<div class="roadmap-container">
    <div class="quarter-row">
        <div class="quarter-card q1">
            <div class="quarter-title">Q1 规划启动</div>
            <div class="quarter-content">
                <ul>
                    <li>年度规划评审与发布</li>
                    <li>复利工程体系搭建</li>
                    <li>Agent需求梳理与排期</li>
                    <li>团队培训计划启动</li>
                </ul>
            </div>
        </div>
        <div class="quarter-card q2">
            <div class="quarter-title">Q2 规模推广</div>
            <div class="quarter-content">
                <ul>
                    <li>30个Agent上线</li>
                    <li>核心场景全覆盖</li>
                    <li>知识库扩容100MB</li>
                    <li>月度复盘优化</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="quarter-row">
        <div class="quarter-card q3">
            <div class="quarter-title">Q3 创新突破</div>
            <div class="quarter-content">
                <ul>
                    <li>数字分身试点启动</li>
                    <li>Agent自主化率提升</li>
                    <li>生态协同深化</li>
                    <li>效果评估与调优</li>
                </ul>
            </div>
        </div>
        <div class="quarter-card q4">
            <div class="quarter-title">Q4 总结升华</div>
            <div class="quarter-content">
                <ul>
                    <li>年度成果盘点</li>
                    <li>方法论沉淀输出</li>
                    <li>标杆案例包装</li>
                    <li>2027规划启动</li>
                </ul>
            </div>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('实施路径：2026年度路线图', roadmapContent), pptx3);
    
    // Slide 19: 资源保障
    const resourceContent = {
        css: `
.resource-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12pt;
    height: 100%;
}
.resource-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
}
.resource-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
    padding-bottom: 4pt;
    border-bottom: 2pt solid #${colors.accent};
}
.resource-list {
    font-size: 9pt;
    line-height: 1.5;
}
.resource-list ul {
    margin: 0;
    padding-left: 12pt;
}
.resource-list li {
    margin-bottom: 4pt;
}
`,
        html: `
<div class="resource-container">
    <div class="resource-card">
        <div class="resource-title">👥 人才保障</div>
        <div class="resource-list">
            <ul>
                <li>AI赋能负责人1名，统筹整体规划</li>
                <li>各小组AI联络员，推进落地执行</li>
                <li>全员AI素养培训，提升使用能力</li>
                <li>外部专家顾问，提供前沿指导</li>
            </ul>
        </div>
    </div>
    <div class="resource-card">
        <div class="resource-title">💰 预算保障</div>
        <div class="resource-list">
            <ul>
                <li>大模型API调用费用预算</li>
                <li>Dify等平台订阅费用</li>
                <li>知识库建设与维护费用</li>
                <li>培训与活动费用</li>
            </ul>
        </div>
    </div>
    <div class="resource-card">
        <div class="resource-title">🛠️ 技术保障</div>
        <div class="resource-list">
            <ul>
                <li>Dify平台稳定运行与升级</li>
                <li>RAG知识库技术支持</li>
                <li>MCP工具持续集成</li>
                <li>代码仓库与协作平台</li>
            </ul>
        </div>
    </div>
    <div class="resource-card">
        <div class="resource-title">📋 机制保障</div>
        <div class="resource-list">
            <ul>
                <li>月度复盘机制，跟踪进度</li>
                <li>季度评审机制，调整方向</li>
                <li>知识沉淀机制，复利增长</li>
                <li>激励表彰机制，持续动力</li>
            </ul>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('资源保障：支撑体系', resourceContent), pptx3);
    
    // Slide 20: 预期成效
    const outcomeContent = {
        css: `
.outcome-container {
    display: flex;
    flex-direction: column;
    gap: 10pt;
    height: 100%;
}
.outcome-row {
    display: flex;
    gap: 12pt;
    flex: 1;
}
.outcome-card {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 12pt;
}
.outcome-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.outcome-list {
    font-size: 9pt;
    line-height: 1.5;
}
.outcome-list ul {
    margin: 0;
    padding-left: 12pt;
}
.outcome-list li {
    margin-bottom: 4pt;
}
.highlight-card {
    background: linear-gradient(135deg, #${colors.primary} 0%, #${colors.secondary} 100%);
    color: white;
}
.highlight-card .outcome-title {
    color: #${colors.gold};
}
`,
        html: `
<div class="outcome-container">
    <div class="outcome-row">
        <div class="outcome-card">
            <div class="outcome-title">📊 业务成效</div>
            <div class="outcome-list">
                <ul>
                    <li>效率提升：平均50%+，部分场景99.7%</li>
                    <li>成本节省：预计年节省5000万</li>
                    <li>质量提升：风险识别准确率92%+</li>
                    <li>响应速度：从天数到分钟级</li>
                </ul>
            </div>
        </div>
        <div class="outcome-card">
            <div class="outcome-title">👥 组织成效</div>
            <div class="outcome-list">
                <ul>
                    <li>全员AI素养显著提升</li>
                    <li>知识沉淀体系化建立</li>
                    <li>团队协作效率优化</li>
                    <li>创新氛围与能力增强</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="outcome-row">
        <div class="outcome-card">
            <div class="outcome-title">🏆 品牌成效</div>
            <div class="outcome-list">
                <ul>
                    <li>成为公司AI赋能标杆团队</li>
                    <li>方法论输出，可复用推广</li>
                    <li>KM文章沉淀，影响力提升</li>
                    <li>行业交流与分享机会</li>
                </ul>
            </div>
        </div>
        <div class="outcome-card highlight-card">
            <div class="outcome-title">🎯 核心目标</div>
            <div class="outcome-list">
                <ul>
                    <li>从「会用AI」到「用好AI」</li>
                    <li>从「个体提效」到「组织进化」</li>
                    <li>从「工具使用」到「复利增长」</li>
                    <li>打造AI原生组织能力</li>
                </ul>
            </div>
        </div>
    </div>
</div>
`
    };
    await html2pptx(createSlideHTML('预期成效：价值与影响', outcomeContent), pptx3);
    
    // Slide 21: 结束页
    await html2pptx(createSlideHTML('AI赋能·智领未来', '让AI成为每个人的超级助手', 'title'), pptx3);
    
    console.log('战略屋与实施部分完成！');
    
    // 保存第三部分
    const outputPath3 = path.join(outputDir, 'AI战略规划_战略屋与实施.pptx');
    await pptx3.writeFile({ fileName: outputPath3 });
    console.log(`第三部分已保存: ${outputPath3}`);
    
    console.log('\n=== 全部PPT创建完成！===');
    console.log(`文件位置：${outputDir}`);
}

createPresentation().catch(err => {
    console.error('创建PPT时出错:', err);
    process.exit(1);
});
