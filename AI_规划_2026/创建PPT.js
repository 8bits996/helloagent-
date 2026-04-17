const pptxgen = require('pptxgenjs');
const html2pptx = require('c:/Users/frankechen/.codebuddy/skills/pptx/scripts/html2pptx');
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

// 颜色定义 - 专业商务风格
const colors = {
    primary: '1a365d',      // 深蓝
    secondary: '2c5282',    // 中蓝
    accent: '3182ce',       // 亮蓝
    success: '38a169',      // 绿
    warning: 'd69e2e',      // 黄
    danger: 'e53e3e',       // 红
    light: 'f7fafc',        // 浅灰
    dark: '1a202c',         // 深灰
    white: 'FFFFFF',
    gold: 'ecc94b'          // 金色强调
};

// 创建HTML幻灯片的辅助函数
function createSlideHTML(slideNum, title, content, type = 'content') {
    let html = '';
    
    if (type === 'title') {
        html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #${colors.white}; }
body {
    width: 720pt; height: 405pt; margin: 0; padding: 0;
    background: linear-gradient(135deg, #${colors.primary} 0%, #${colors.secondary} 100%);
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
<div class="section-num">${slideNum}</div>
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
    font-size: 24pt;
    margin: 0;
}
.content {
    flex: 1;
    padding: 25pt 30pt;
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
    
    const filePath = path.join(slidesDir, `slide${slideNum}.html`);
    fs.writeFileSync(filePath, html);
    return filePath;
}

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = '政企客户成功中心';
    pptx.title = '2026年度AI战略规划';
    pptx.subject = 'AI战略规划';
    
    console.log('开始创建PPT...');
    
    // Slide 1: 封面
    console.log('创建封面...');
    await html2pptx(createSlideHTML(1, 'AI赋能·智领未来', '政企客户成功中心 2026年度AI战略规划', 'title'), pptx);
    
    // Slide 2: 目录
    console.log('创建目录...');
    const tocContent = {
        css: `
.toc-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15pt;
    height: 100%;
}
.toc-item {
    background: #${colors.white};
    border-left: 5pt solid #${colors.accent};
    padding: 15pt;
    display: flex;
    align-items: center;
}
.toc-num {
    font-size: 28pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-right: 15pt;
}
.toc-text {
    font-size: 14pt;
    color: #${colors.dark};
}
`,
        html: `
<div class="toc-grid">
    <div class="toc-item"><span class="toc-num">01</span><span class="toc-text">五看分析：洞察趋势与机会</span></div>
    <div class="toc-item"><span class="toc-num">02</span><span class="toc-text">三定规划：明确战略与目标</span></div>
    <div class="toc-item"><span class="toc-num">03</span><span class="toc-text">小组规划框架与目标</span></div>
    <div class="toc-item"><span class="toc-num">04</span><span class="toc-text">实施路径与里程碑</span></div>
    <div class="toc-item"><span class="toc-num">05</span><span class="toc-text">资源保障与支撑体系</span></div>
    <div class="toc-item"><span class="toc-num">06</span><span class="toc-text">预期成效与价值</span></div>
</div>
`
    };
    await html2pptx(createSlideHTML(2, '目录', tocContent), pptx);
    
    // Slide 3: 第一部分分隔页
    await html2pptx(createSlideHTML(3, '五看分析', '', 'section'), pptx);
    
    // Slide 4: 五看框架
    const wukangContent = {
        css: `
.framework {
    display: flex;
    justify-content: space-between;
    height: 100%;
    gap: 10pt;
}
.wu-item {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.wu-icon {
    font-size: 28pt;
    margin-bottom: 10pt;
}
.wu-title {
    font-size: 14pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 8pt;
}
.wu-desc {
    font-size: 10pt;
    color: #666;
    text-align: left;
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
    await html2pptx(createSlideHTML(4, '五看分析框架', wukangContent), pptx);
    
    // Slide 5: 看趋势 - 2026 AI技术趋势
    const trendContent = {
        css: `
.trend-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20pt;
    height: 100%;
}
.trend-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 18pt;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.trend-title {
    font-size: 14pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 12pt;
    padding-bottom: 8pt;
    border-bottom: 2pt solid #${colors.accent};
}
.trend-list {
    font-size: 11pt;
    color: #333;
    line-height: 1.6;
}
.trend-list ul {
    margin: 0;
    padding-left: 18pt;
}
.trend-list li {
    margin-bottom: 6pt;
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
                <li><span class="highlight">上下文工程</span>：长上下文、RAG成为标配能力</li>
                <li><span class="highlight">模型即服务</span>：推理成本持续下降，API化普及</li>
            </ul>
        </div>
    </div>
    <div class="trend-card">
        <div class="trend-title">🏢 产业应用趋势</div>
        <div class="trend-list">
            <ul>
                <li><span class="highlight">数字分身/员工</span>：7×24小时AI工作伙伴</li>
                <li><span class="highlight">个人AI助理</span>：Clawbot等爆火，Agentic工作流</li>
                <li><span class="highlight">复利工程</span>：知识沉淀、经验复用成为核心竞争力</li>
                <li><span class="highlight">人机协作</span>：从工具使用到组织原生AI</li>
            </ul>
        </div>
    </div>
    <div class="trend-card">
        <div class="trend-title">📊 行业报告洞察</div>
        <div class="trend-list">
            <ul>
                <li>Google Cloud：企业级Agent部署进入爆发期</li>
                <li>麦肯锡：AI生产力提升进入规模化应用阶段</li>
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
    await html2pptx(createSlideHTML(5, '看趋势：2026 AI技术发展趋势', trendContent), pptx);
    
    // Slide 6: 看市场/客户 - 需求洞察
    const marketContent = {
        css: `
.market-container {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 20pt;
    height: 100%;
}
.market-left {
    display: flex;
    flex-direction: column;
    gap: 12pt;
}
.pain-card {
    background: #${colors.white};
    border-left: 4pt solid #${colors.danger};
    padding: 12pt;
    border-radius: 0 6pt 6pt 0;
}
.pain-title {
    font-size: 12pt;
    font-weight: bold;
    color: #${colors.danger};
    margin-bottom: 6pt;
}
.pain-desc {
    font-size: 10pt;
    color: #555;
}
.market-right {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 18pt;
}
.need-title {
    font-size: 14pt;
    font-weight: bold;
    color: #${colors.success};
    margin-bottom: 12pt;
}
.need-list {
    font-size: 11pt;
    line-height: 1.8;
}
.need-list ul {
    margin: 0;
    padding-left: 18pt;
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
    await html2pptx(createSlideHTML(6, '看市场/客户：需求洞察与痛点分析', marketContent), pptx);
    
    // Slide 7: 看竞争 - 内外部分析
    const competeContent = {
        css: `
.compete-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20pt;
    height: 100%;
}
.compete-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 18pt;
}
.compete-title {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 12pt;
    padding-bottom: 8pt;
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
    font-size: 10pt;
    line-height: 1.7;
}
.compete-list ul {
    margin: 0;
    padding-left: 16pt;
}
.compete-list li {
    margin-bottom: 8pt;
}
.sub-title {
    font-weight: bold;
    color: #${colors.dark};
    margin: 10pt 0 6pt 0;
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
            <div class="sub-title">安灯、云一、TEG等研发团队</div>
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
    await html2pptx(createSlideHTML(7, '看竞争：内外部AI能力建设对标', competeContent), pptx);
    
    // Slide 8: 看自己 - 现状盘点
    const selfContent = {
        css: `
.self-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15pt;
    height: 100%;
}
.status-card {
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
}
.status-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
    margin-bottom: 10pt;
}
.achievement-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8pt;
}
.ach-item {
    background: #f0f7ff;
    padding: 10pt;
    border-radius: 6pt;
    text-align: center;
}
.ach-num {
    font-size: 20pt;
    font-weight: bold;
    color: #${colors.accent};
}
.ach-label {
    font-size: 9pt;
    color: #666;
}
.gap-list {
    font-size: 10pt;
    line-height: 1.8;
}
.gap-list ul {
    margin: 0;
    padding-left: 16pt;
}
.gap-list li {
    margin-bottom: 6pt;
}
`,
        html: `
<div class="self-container">
    <div class="status-card">
        <div class="status-title">🏆 已有成果（2025）</div>
        <div class="achievement-grid">
            <div class="ach-item">
                <div class="ach-num">13</div>
                <div class="ach-label">AI智能体总数</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">8</div>
                <div class="ach-label">已上线应用</div>
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
                <div class="ach-label">预计年节省</div>
            </div>
            <div class="ach-item">
                <div class="ach-num">4</div>
                <div class="ach-label">KM知识沉淀</div>
            </div>
        </div>
    </div>
    <div class="status-card">
        <div class="status-title">📋 能力现状盘点</div>
        <div class="gap-list">
            <ul>
                <li><b>鹰眼-合同智审</b>：99.7%效率提升，已规模化应用</li>
                <li><b>项目AI问诊</b>：188项目清淤，231万损益量化</li>
                <li><b>扬帆出海合规</b>：60+用户，70+MB知识库</li>
                <li><b>AI学习助教</b>：3次全员培训，200+人覆盖</li>
                <li><b>技术底座</b>：Dify平台、RAG知识库、MCP集成</li>
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
    await html2pptx(createSlideHTML(8, '看自己：现状盘点与能力评估', selfContent), pptx);
    
    // Slide 9: 看机会 - 战略机会点
    const opportunityContent = {
        css: `
.opp-container {
    display: flex;
    flex-direction: column;
    gap: 12pt;
    height: 100%;
}
.opp-row {
    display: flex;
    gap: 15pt;
    flex: 1;
}
.opp-card {
    flex: 1;
    background: #${colors.white};
    border-radius: 8pt;
    padding: 15pt;
    display: flex;
    flex-direction: column;
}
.opp-header {
    display: flex;
    align-items: center;
    margin-bottom: 10pt;
}
.opp-icon {
    font-size: 24pt;
    margin-right: 10pt;
}
.opp-title {
    font-size: 13pt;
    font-weight: bold;
    color: #${colors.primary};
}
.opp-desc {
    font-size: 10pt;
    color: #555;
    line-height: 1.5;
    flex: 1;
}
.opp-tag {
    background: #${colors.accent};
    color: white;
    padding: 3pt 8pt;
    border-radius: 4pt;
    font-size: 9pt;
    display: inline-block;
    margin-top: 8pt;
    align-self: flex-start;
}
`,
        html: `
<div class="opp-container">
    <div class="opp-row">
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
    </div>
    <div class="opp-row">
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
</div>
`
    };
    await html2pptx(createSlideHTML(9, '看机会：战略机会点识别', opportunityContent), pptx);
    
    console.log('五看分析部分完成！');
    
    // 保存PPT（第一部分）
    const outputPath = path.join(outputDir, 'AI战略规划_五看分析.pptx');
    await pptx.writeFile({ fileName: outputPath });
    console.log(`PPT已保存至: ${outputPath}`);
}

createPresentation().catch(err => {
    console.error('创建PPT时出错:', err);
    process.exit(1);
});
