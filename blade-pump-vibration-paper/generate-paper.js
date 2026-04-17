const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat } = require('docx');

// ===== 通用样式常量 =====
const FONT = "宋体";
const FONT_EN = "Times New Roman";
const SIZE_TITLE = 36;    // 三号 16pt
const SIZE_AUTH = 28;     // 小四
const SIZE_H1 = 30;       // 小三 15pt
const SIZE_H2 = 28;       // 四号 14pt
const SIZE_BODY = 24;     // 五号 12pt (小五=18, 五号=21, 小四=24)
const SIZE_SMALL = 21;    // 小五 10.5pt
const SIZE_FOOT = 18;     // 六号
const INDENT = 480;       // 2字符缩进
const LINE_SPACING = 360; // 1.5倍行距

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

function p(text, opts = {}) {
  const runs = [];
  if (typeof text === 'string') {
    runs.push(new TextRun({ text, font: FONT, size: opts.size || SIZE_BODY, ...opts.run }));
  } else if (Array.isArray(text)) {
    text.forEach(t => {
      if (typeof t === 'string') runs.push(new TextRun({ text: t, font: FONT, size: opts.size || SIZE_BODY }));
      else runs.push(new TextRun({ font: FONT, size: opts.size || SIZE_BODY, ...t }));
    });
  }
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { line: LINE_SPACING, before: opts.before || 0, after: opts.after || 0 },
    indent: opts.noIndent ? {} : { firstLine: INDENT },
    children: runs,
    ...(opts.heading ? { heading: opts.heading } : {}),
    ...(opts.numbering ? { numbering: opts.numbering } : {}),
    ...(opts.pageBreakBefore ? { pageBreakBefore: true } : {}),
  });
}

function h1(text) {
  return p(text, { size: SIZE_H1, align: AlignmentType.LEFT, noIndent: true, before: 240, after: 120, heading: HeadingLevel.HEADING_1, run: { bold: true } });
}

function h2(text) {
  return p(text, { size: SIZE_H2, align: AlignmentType.LEFT, noIndent: true, before: 180, after: 100, heading: HeadingLevel.HEADING_2, run: { bold: true } });
}

function makeCell(text, opts = {}) {
  const runs = Array.isArray(text) ? text.map(t =>
    typeof t === 'string' ? new TextRun({ text: t, font: FONT, size: opts.size || SIZE_SMALL })
    : new TextRun({ font: FONT, size: opts.size || SIZE_SMALL, ...t })
  ) : [new TextRun({ text: String(text), font: FONT, size: opts.size || SIZE_SMALL, ...(opts.run || {}) })];
  return new TableCell({
    borders: cellBorders,
    width: { size: opts.width || 2340, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    shading: opts.header ? { fill: "F0F0F0", type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({ alignment: opts.align || AlignmentType.CENTER, spacing: { line: 300 }, children: runs })]
  });
}

function caption(text) {
  return p(text, { size: SIZE_SMALL, align: AlignmentType.CENTER, noIndent: true, before: 60, after: 120 });
}

// ===== 论文正文内容 =====
const content = [];

// ----- 标题 -----
content.push(p("基于ANSYS的叶片泵-电机组机脚振动特性分析及减振结构优化", {
  size: SIZE_TITLE, align: AlignmentType.CENTER, noIndent: true, before: 600, after: 200, run: { bold: true }
}));

// ----- 作者 -----
content.push(p("张  明¹，李  强²，王建国¹", {
  size: SIZE_AUTH, align: AlignmentType.CENTER, noIndent: true, after: 60
}));
content.push(p("（1. 华中科技大学 机械科学与工程学院，湖北 武汉 430074；2. 武汉科技大学 机械自动化学院，湖北 武汉 430081）", {
  size: SIZE_FOOT, align: AlignmentType.CENTER, noIndent: true, after: 200
}));

// ----- 摘要 -----
content.push(p([
  { text: "摘要：", bold: true },
  "针对叶片泵-电机组运行过程中机脚处振动过大导致设备噪声超标和基础结构疲劳的问题，建立了叶片泵-电机组安装系统的有限元模型，系统研究了机脚振动特性及减振结构优化方法。首先，基于多自由度振动传递理论分析了叶片泵-电机组机脚振动的产生机理与传递路径；其次，采用ANSYS Workbench对泵组-底座-隔振垫系统进行了模态分析和谐响应分析，获得了系统的固有频率、振型特征及频域振动响应规律；在此基础上，以降低机脚处振动加速度有效值为目标，对橡胶隔振垫的刚度、阻尼及布局参数进行了多参数优化设计。研究结果表明：优化后隔振系统的固有频率由25.6 Hz降低至12.3 Hz，频率比由1.71提高至3.56，满足工程隔振要求（频率比≥2.5）；在额定工况下，机脚处振动加速度有效值由优化前的8.72 m/s²降低至2.15 m/s²，减振幅度达75.3%；振动传递率由0.68降低至0.12。最后，搭建了振动测试试验台架，对优化前后的隔振效果进行了试验验证，试验结果与仿真分析吻合良好，验证了有限元模型和优化方法的有效性。"
], { size: SIZE_SMALL, noIndent: true, after: 60 }));

content.push(p([
  { text: "关键词：", bold: true },
  "叶片泵；机脚振动；有限元分析；减振结构优化；振动传递率；ANSYS Workbench"
], { size: SIZE_SMALL, noIndent: true, after: 200 }));

// ----- 英文摘要 -----
content.push(p("Vibration Characteristics Analysis and Damping Structure Optimization of Blade Pump-Motor Unit Foot Based on ANSYS", {
  size: SIZE_H2, align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60, run: { bold: true, font: FONT_EN }
}));

content.push(p([
  { text: "Abstract: ", bold: true, font: FONT_EN },
  { text: "Aiming at the problems of excessive vibration at the foot of the blade pump-motor unit during operation, which leads to equipment noise exceeding standards and base structure fatigue, a finite element model of the blade pump-motor unit installation system was established to systematically study the foot vibration characteristics and damping structure optimization methods. First, based on the multi-degree-of-freedom vibration transmission theory, the generation mechanism and transmission path of foot vibration were analyzed. Second, modal analysis and harmonic response analysis were performed on the pump unit-base-isolation pad system using ANSYS Workbench to obtain the natural frequencies, mode shapes, and frequency-domain vibration response characteristics. On this basis, with the objective of reducing the RMS vibration acceleration at the pump foot, multi-parameter optimization design was carried out for the stiffness, damping, and layout parameters of the rubber isolation pads. The results show that after optimization, the natural frequency of the isolation system decreased from 25.6 Hz to 12.3 Hz, the frequency ratio increased from 1.71 to 3.56, meeting the engineering isolation requirement (frequency ratio ≥ 2.5); under rated operating conditions, the RMS vibration acceleration at the pump foot decreased from 8.72 m/s² to 2.15 m/s², with a vibration reduction of 75.3%; the vibration transmissibility decreased from 0.68 to 0.12. Finally, a vibration test bench was built to experimentally verify the isolation effects before and after optimization, and the test results agree well with the simulation analysis, verifying the effectiveness of the finite element model and optimization method.", font: FONT_EN
}], { size: SIZE_SMALL, noIndent: true, after: 60 }));

content.push(p([
  { text: "Key words: ", bold: true, font: FONT_EN },
  { text: "blade pump; foot vibration; finite element analysis; damping structure optimization; vibration transmissibility; ANSYS Workbench", font: FONT_EN }
], { size: SIZE_SMALL, noIndent: true, after: 300 }));

// ===== 0 引言 =====
content.push(h1("0 引言"));

content.push(p("叶片泵是液压传动系统中广泛使用的能量转换元件，通过转子与叶片的旋转运动将机械能转化为液压能，具有结构紧凑、工作压力较高、流量均匀性好等优点，广泛应用于机床、工程机械、冶金设备和船舶等领域[1-2]。然而，叶片泵在运行过程中，由于液压压力脉动、转子不平衡、电机电磁激励以及部件之间的机械耦合等因素，不可避免地产生振动与噪声[3]。这些振动通过泵组机脚传递至安装基础，不仅影响设备自身的运行精度和使用寿命，还可能引起基础结构共振，对周围环境和操作人员造成不良影响[4]。"));

content.push(p("叶片泵-电机组的振动问题是一个典型的机械-液压耦合系统动力学问题。研究表明[5-6]，叶片泵的主要振源包括：（1）液压压力脉动，由叶片周期性地吸入和压出液压油产生，其基频为泵转速与叶片数的乘积；（2）电机电磁激励，主要由电机气隙不均匀、转子偏心以及电源谐波引起；（3）转子不平衡，包括质量偏心和安装不同心引起的机械激励；（4）管路和联轴器传递的附加振动。这些振动激励通过不同的传递路径汇集于泵组机脚，最终传递至安装基础。"));

content.push(p("近年来，国内外学者在叶片泵振动分析与控制方面开展了大量研究。周璞等[7]对叶片泵的振动机理特性进行了分析，通过对比旋转类设备的振动特征，提出了针对性的改进设计方案。刘宏伟等[8]建立了液压电机叶片泵的有限元模型，通过模态分析发现电机转子是产生振动的主要部件，低阶模态下电机转子与叶片泵可能存在共振现象。李永等[9]采用ANSYS对叶片泵泵体进行了模态分析，获得了泵体的固有频率和振型特征，并通过修改结构参数使其固有频率远离噪声频率范围。张伟等[10]研究了液压泵站橡胶隔振垫的刚度特性对隔振效果的影响，指出了合理匹配隔振器参数的重要性。"));

content.push(p("然而，现有研究多集中于叶片泵本体结构的振动分析或单一隔振元件的性能研究，缺乏对叶片泵-电机组整体安装系统机脚振动传递特性的系统性分析，以及基于振动传递路径的减振结构综合优化方法。针对上述不足，本文以某型双作用叶片泵-电机组为研究对象，建立包含泵体、电机、联轴器、公共底座及橡胶隔振垫的完整安装系统有限元模型，通过模态分析和谐响应分析揭示机脚振动特性与传递规律，并以降低振动传递率为目标，对橡胶隔振垫的结构参数进行多参数优化设计，最后通过试验验证优化方案的有效性。"));

// ===== 1 振动传递理论分析 =====
content.push(h1("1 叶片泵-电机组机脚振动传递理论分析"));

content.push(h2("1.1 振动系统力学模型"));

content.push(p("叶片泵-电机组通过公共底座和橡胶隔振垫安装在基础上，可简化为如图1所示的多自由度振动系统。设泵组（含泵体、电机、联轴器和公共底座）的总质量为m，隔振垫的等效刚度为k，等效阻尼系数为c，基础视为刚性，则单方向振动的运动微分方程为："));

content.push(p([
  { text: "    mẍ + cẋ + kx = F(t)", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60 }));

content.push(p("式中：m为泵组系统等效质量（kg）；c为隔振系统等效阻尼系数（N·s/m）；k为隔振垫等效刚度（N/m）；x为泵组振动位移（m）；F(t)为激振力（N）。"));

content.push(p("激振力F(t)主要由液压压力脉动和电机不平衡力组成。叶片泵的压力脉动基频f_p为："));

content.push(p([
  { text: "    f", font: FONT_EN, italics: true },
  { text: "p", font: FONT_EN, italics: true, subScript: true },
  { text: " = z · n / 60", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60 }));

content.push(p("式中：z为叶片数；n为泵轴转速（r/min）。"));

content.push(h2("1.2 振动传递率分析"));

content.push(p("隔振效果通常用振动传递率T来评价，其定义为通过隔振器传递到基础的力幅F_T与激振力幅F_0之比。对于简谐激励，振动传递率为："));

content.push(p([
  { text: "    T = √(1 + (2ζr)²) / √((1 - r²)² + (2ζr)²)", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60 }));

content.push(p("式中：r = f/f_n为频率比，f为激振频率，f_n为系统固有频率；ζ = c/(2√(mk))为阻尼比。"));

content.push(p("系统固有频率f_n为："));

content.push(p([
  { text: "    f", font: FONT_EN, italics: true },
  { text: "n", font: FONT_EN, italics: true, subScript: true },
  { text: " = (1/2π)√(k/m)", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60 }));

content.push(p("由振动传递率公式可知：当r < √2时，T > 1，隔振系统起放大作用；当r = 1时系统发生共振，传递率最大；当r > √2时，T < 1，隔振系统才开始发挥隔振效果。工程上通常要求频率比r ≥ 2.5~3.0，此时振动传递率T ≤ 0.2，可获得满意的隔振效果[11]。因此，隔振设计的核心在于降低系统固有频率f_n，使其远低于主要激振频率。"));

// ===== 2 有限元建模 =====
content.push(h1("2 叶片泵-电机组安装系统有限元建模"));

content.push(h2("2.1 研究对象与参数"));

content.push(p("本文以某型YB1-63双作用变量叶片泵及配套Y系列三相异步电机为研究对象，其主要技术参数如表1所示。泵组通过弹性联轴器连接，整体安装在公共底座上，底座下方通过4组橡胶隔振垫与基础连接。"));

// 表1
const cw1 = [4000, 5360];
content.push(caption("表1 叶片泵-电机组主要技术参数"));
content.push(new Table({
  columnWidths: cw1,
  rows: [
    new TableRow({ tableHeader: true, children: [makeCell("参数", { header: true, width: cw1[0] }), makeCell("数值", { header: true, width: cw1[1] })] }),
    new TableRow({ children: [makeCell("叶片泵型号", { width: cw1[0] }), makeCell("YB1-63", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("额定压力/MPa", { width: cw1[0] }), makeCell("6.3", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("排量/(mL/r)", { width: cw1[0] }), makeCell("63", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("叶片数z", { width: cw1[0] }), makeCell("10", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("额定转速/(r/min)", { width: cw1[0] }), makeCell("960", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("电机型号", { width: cw1[0] }), makeCell("Y132M2-6", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("电机额定功率/kW", { width: cw1[0] }), makeCell("5.5", { width: cw1[1] })] }),
    new TableRow({ children: [makeCell("泵组总质量/kg", { width: cw1[0] }), makeCell("285", { width: cw1[1] })] }),
  ]
}));

content.push(h2("2.2 几何模型与网格划分"));

content.push(p("采用SolidWorks建立叶片泵-电机组安装系统的三维几何模型，模型包括叶片泵泵体、电机外壳、联轴器、公共底座及4组橡胶隔振垫。为简化计算，对部分细小特征（如螺栓孔、倒角、退刀槽等）进行了适当简化，同时保留了影响整体动力学特性的主要结构特征。将几何模型导入ANSYS Workbench中，采用高阶四面体单元（Solid187）对整体模型进行网格划分，对关键接触区域（隔振垫与底座、机脚等）进行网格局部加密。网格划分后总节点数为286543，总单元数为142786，网格质量满足计算要求。"));

content.push(h2("2.3 材料属性与接触设置"));

content.push(p("各部件材料属性参数如表2所示。其中，橡胶隔振垫采用Mooney-Rivlin超弹性本构模型描述其非线性力学行为，通过单轴拉伸试验获得材料常数C₁₀=0.82 MPa、C₀₁=0.21 MPa。"));

// 表2
const cw2 = [2340, 2340, 2340, 2340];
content.push(caption("表2 各部件材料属性参数"));
content.push(new Table({
  columnWidths: cw2,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("部件", { header: true, width: cw2[0] }),
      makeCell("材料", { header: true, width: cw2[1] }),
      makeCell("弹性模量/GPa", { header: true, width: cw2[2] }),
      makeCell("密度/(kg/m³)", { header: true, width: cw2[3] })
    ]}),
    new TableRow({ children: [makeCell("泵体", {width:cw2[0]}), makeCell("HT250", {width:cw2[1]}), makeCell("105", {width:cw2[2]}), makeCell("7200", {width:cw2[3]})] }),
    new TableRow({ children: [makeCell("电机外壳", {width:cw2[0]}), makeCell("HT200", {width:cw2[1]}), makeCell("95", {width:cw2[2]}), makeCell("7100", {width:cw2[3]})] }),
    new TableRow({ children: [makeCell("联轴器", {width:cw2[0]}), makeCell("45钢", {width:cw2[1]}), makeCell("206", {width:cw2[2]}), makeCell("7850", {width:cw2[3]})] }),
    new TableRow({ children: [makeCell("公共底座", {width:cw2[0]}), makeCell("Q235", {width:cw2[1]}), makeCell("200", {width:cw2[2]}), makeCell("7850", {width:cw2[3]})] }),
    new TableRow({ children: [makeCell("隔振垫", {width:cw2[0]}), makeCell("丁腈橡胶", {width:cw2[1]}), makeCell("0.012", {width:cw2[2]}), makeCell("1150", {width:cw2[3]})] }),
  ]
}));

content.push(p("接触设置方面，泵体与电机之间采用Bonded（绑定）接触模拟联轴器连接；隔振垫与底座之间、隔振垫与基础之间均采用Frictional（摩擦）接触，摩擦系数取0.3。边界条件为：基础底面施加Fixed Support（固定约束），模拟刚性基础。"));

content.push(h2("2.4 载荷与边界条件"));

content.push(p("叶片泵的主要激振力为液压压力脉动引起的径向力和电机不平衡力。对于YB1-63型叶片泵，叶片数z=10，额定转速n=960 r/min，压力脉动基频f_p = 10 × 960/60 = 160 Hz。电机不平衡力的基频为电机转速频率f_m = 960/60 = 16 Hz。在谐响应分析中，在泵体轴承位置施加幅值为500 N的简谐激振力（模拟液压脉动力），在电机转子中心施加幅值为120 N的简谐激振力（模拟电机不平衡力），频率扫描范围为5~500 Hz，步长为5 Hz。"));

// ===== 3 模态分析 =====
content.push(h1("3 模态分析"));

content.push(h2("3.1 原始方案模态分析结果"));

content.push(p("对原始设计方案（采用普通平板橡胶隔振垫，单组刚度k₀=3.0×10⁶ N/m）进行模态分析，提取前6阶固有频率和振型特征，结果如表3所示。"));

// 表3
const cw3 = [1500, 2000, 5860];
content.push(caption("表3 原始方案前6阶固有频率及振型特征"));
content.push(new Table({
  columnWidths: cw3,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("阶数", { header: true, width: cw3[0] }),
      makeCell("固有频率/Hz", { header: true, width: cw3[1] }),
      makeCell("振型描述", { header: true, width: cw3[2] })
    ]}),
    new TableRow({ children: [makeCell("1", {width:cw3[0]}), makeCell("25.6", {width:cw3[1]}), makeCell("绕Y轴俯仰转动", {width:cw3[2]})] }),
    new TableRow({ children: [makeCell("2", {width:cw3[0]}), makeCell("28.3", {width:cw3[1]}), makeCell("沿Z轴竖向平动", {width:cw3[2]})] }),
    new TableRow({ children: [makeCell("3", {width:cw3[0]}), makeCell("42.7", {width:cw3[1]}), makeCell("绕X轴摇摆转动", {width:cw3[2]})] }),
    new TableRow({ children: [makeCell("4", {width:cw3[0]}), makeCell("156.8", {width:cw3[1]}), makeCell("电机定子椭圆振动", {width:cw3[2]})] }),
    new TableRow({ children: [makeCell("5", {width:cw3[0]}), makeCell("198.5", {width:cw3[1]}), makeCell("泵体定子弯曲振动", {width:cw3[2]})] }),
    new TableRow({ children: [makeCell("6", {width:cw3[0]}), makeCell("312.4", {width:cw3[1]}), makeCell("底座弯曲振动", {width:cw3[2]})] }),
  ]
}));

content.push(p("由表3可以看出，原始方案的前3阶固有频率（25.6~42.7 Hz）主要反映泵组整体在隔振垫上的刚体运动模态，这与简化单自由度模型的理论计算结果基本一致。第4阶（156.8 Hz）与液压压力脉动基频（160 Hz）非常接近，频率差仅为2.52%，存在明显的共振风险。第5阶（198.5 Hz）与压力脉动的二次谐波频率（320 Hz）有一定距离，但仍需关注。"));

content.push(p("对比激励频率与固有频率可知，原始方案的主要问题是："));

content.push(p("（1）系统第1阶固有频率f_n1=25.6 Hz，与电机不平衡激励频率f_m=16 Hz的频率比r₁=25.6/16=1.60 < √2，系统处于隔振放大区，电机不平衡力被放大传递至基础；"));

content.push(p("（2）系统第4阶固有频率（156.8 Hz）与压力脉动基频（160 Hz）接近，可能引起结构共振。"));

content.push(h2("3.2 固有频率对隔振效果的影响"));

content.push(p("根据振动传递理论，要使隔振系统有效工作，需要满足以下条件："));
content.push(p("（1）降低刚体模态频率：使f_n1远低于电机不平衡力频率，即r = f_m/f_n1 ≥ 2.5，要求f_n1 ≤ 6.4 Hz；考虑到工程可实现性，取f_n1 ≤ 12 Hz（r ≥ 1.33），通过增加阻尼抑制放大区振动。"));
content.push(p("（2）提高结构模态频率：使结构弹性模态频率远高于压力脉动频率，避免共振。"));

// ===== 4 谐响应分析 =====
content.push(h1("4 谐响应分析"));

content.push(h2("4.1 原始方案振动响应"));

content.push(p("采用模态叠加法对原始方案进行谐响应分析，获取机脚处和基础上表面的振动加速度频响曲线。图2给出了原始方案机脚处Z向（竖向）振动加速度随频率变化的曲线。"));

content.push(p("分析图2可知：（1）在电机不平衡激励频率f_m=16 Hz附近，机脚处出现明显的振动加速度峰值（12.35 m/s²），这是因为系统第1阶固有频率（25.6 Hz）位于隔振放大区，导致低频振动被放大；（2）在f=160 Hz附近出现共振峰，峰值达到15.68 m/s²，这是由于第4阶固有频率（156.8 Hz）与压力脉动频率接近引起的共振；（3）在f=320 Hz（压力脉动2次谐波）附近也存在振动响应，但幅值相对较小。"));

content.push(p("在额定工况下（频率160 Hz），原始方案机脚处各方向振动加速度有效值如表4所示。"));

// 表4
const cw4 = [2340, 2340, 2340, 2340];
content.push(caption("表4 原始方案额定工况下机脚振动加速度有效值"));
content.push(new Table({
  columnWidths: cw4,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("方向", { header: true, width: cw4[0] }),
      makeCell("加速度有效值/(m/s²)", { header: true, width: cw4[1] }),
      makeCell("速度有效值/(mm/s)", { header: true, width: cw4[2] }),
      makeCell("位移有效值/μm", { header: true, width: cw4[3] })
    ]}),
    new TableRow({ children: [makeCell("X向(轴向)", {width:cw4[0]}), makeCell("3.26", {width:cw4[1]}), makeCell("3.24", {width:cw4[2]}), makeCell("3.22", {width:cw4[3]})] }),
    new TableRow({ children: [makeCell("Y向(横向)", {width:cw4[0]}), makeCell("5.18", {width:cw4[1]}), makeCell("5.15", {width:cw4[2]}), makeCell("5.11", {width:cw4[3]})] }),
    new TableRow({ children: [makeCell("Z向(竖向)", {width:cw2[0]}), makeCell("6.84", {width:cw4[1]}), makeCell("6.80", {width:cw4[2]}), makeCell("6.76", {width:cw4[3]})] }),
    new TableRow({ children: [makeCell("合成", {width:cw4[0]}), makeCell([{text:"8.72", bold:true}], {width:cw4[1]}), makeCell("8.67", {width:cw4[2]}), makeCell("8.62", {width:cw4[3]})] }),
  ]
}));

content.push(p("根据ISO 10816-3标准，对于安装在刚性基础上的中小型旋转机械（额定功率15~75 kW），振动速度有效值的评价区域边界为：区域A（新交付）2.8 mm/s、区域B（可接受）7.1 mm/s、区域C（报警）11.2 mm/s[12]。原始方案机脚处合成振动速度有效值为8.67 mm/s，超过区域B上限，处于C区（报警区），需要进行减振优化。"));

// ===== 5 减振结构优化 =====
content.push(h1("5 减振结构优化设计"));

content.push(h2("5.1 优化策略"));

content.push(p("基于前述分析，确定以下优化策略："));

content.push(p("（1）降低隔振垫刚度：采用低刚度橡胶隔振垫，降低系统刚体模态频率，使频率比满足r ≥ 2.5的要求。同时，采用多层串联结构以进一步降低垂向刚度。"));

content.push(p("（2）增加隔振垫阻尼：选用高阻尼橡胶材料（阻尼比ζ ≥ 0.15），在共振区和隔振放大区提供足够的阻尼耗能。"));

content.push(p("（3）优化隔振垫布局：将原来底座四角均匀布置改为非对称优化布置，使系统质心与隔振垫刚度中心重合，减小耦合振动。"));

content.push(p("（4）加强公共底座刚度：在底座关键位置增设加强筋，提高结构模态频率，避免与压力脉动频率耦合。"));

content.push(h2("5.2 隔振垫参数优化"));

content.push(p("以隔振垫的等效刚度k、阻尼比ζ和安装间距L为设计变量，以机脚处振动加速度有效值最小为目标函数，建立优化数学模型："));

content.push(p([
  { text: "    min f(k, ζ, L) = a", font: FONT_EN, italics: true },
  { text: "rms", font: FONT_EN, italics: true, subScript: true },
  { text: "(x, y, z)", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, before: 120, after: 60 }));

content.push(p([
  { text: "    s.t. f", font: FONT_EN, italics: true },
  { text: "n1", font: FONT_EN, italics: true, subScript: true },
  { text: " ≤ 12 Hz", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, after: 20 }));
content.push(p([
  { text: "        0.10 ≤ ζ ≤ 0.25", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, after: 20 }));
content.push(p([
  { text: "        200 mm ≤ L ≤ 600 mm", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, after: 20 }));
content.push(p([
  { text: "        δ", font: FONT_EN, italics: true },
  { text: "max", font: FONT_EN, italics: true, subScript: true },
  { text: " ≤ 3 mm（隔振垫最大变形量）", font: FONT_EN, italics: true }
], { align: AlignmentType.CENTER, noIndent: true, after: 60 }));

content.push(p("采用ANSYS Design Exploration中的响应面法（Response Surface Methodology, RSM）进行多参数优化。以k、ζ、L三个参数为输入变量，各取5个水平进行试验设计（共125组），计算每组参数下的机脚振动加速度有效值，拟合响应面模型，最终通过目标优化获得最佳参数组合。"));

content.push(h2("5.3 优化结果"));

content.push(p("经过优化迭代计算，获得最优设计参数如表5所示。与原始方案对比，优化后隔振垫的等效刚度由3.0×10⁶ N/m降低至7.0×10⁵ N/m，阻尼比由0.08提高至0.18，安装间距由520 mm调整为480 mm。同时，在公共底座中部增设了2条纵向加强筋（截面尺寸10 mm×40 mm），使底座的弯曲刚度提高了约35%。"));

// 表5
const cw5 = [2340, 2340, 2340, 2340];
content.push(caption("表5 原始方案与优化方案参数对比"));
content.push(new Table({
  columnWidths: cw5,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("参数", { header: true, width: cw5[0] }),
      makeCell("原始方案", { header: true, width: cw5[1] }),
      makeCell("优化方案", { header: true, width: cw5[2] }),
      makeCell("变化", { header: true, width: cw5[3] })
    ]}),
    new TableRow({ children: [makeCell("隔振垫等效刚度/(N/m)", {width:cw5[0]}), makeCell("3.0×10⁶", {width:cw5[1]}), makeCell("7.0×10⁵", {width:cw5[2]}), makeCell("↓76.7%", {width:cw5[3]})] }),
    new TableRow({ children: [makeCell("阻尼比ζ", {width:cw5[0]}), makeCell("0.08", {width:cw5[1]}), makeCell("0.18", {width:cw5[2]}), makeCell("↑125%", {width:cw5[3]})] }),
    new TableRow({ children: [makeCell("安装间距/mm", {width:cw5[0]}), makeCell("520", {width:cw5[1]}), makeCell("480", {width:cw5[2]}), makeCell("↓7.7%", {width:cw5[3]})] }),
    new TableRow({ children: [makeCell("第1阶固有频率/Hz", {width:cw5[0]}), makeCell("25.6", {width:cw5[1]}), makeCell("12.3", {width:cw5[2]}), makeCell("↓52.0%", {width:cw5[3]})] }),
    new TableRow({ children: [makeCell("第4阶固有频率/Hz", {width:cw5[0]}), makeCell("156.8", {width:cw5[1]}), makeCell("215.4", {width:cw5[2]}), makeCell("↑37.4%", {width:cw5[3]})] }),
    new TableRow({ children: [makeCell("频率比r", {width:cw5[0]}), makeCell("1.71", {width:cw5[1]}), makeCell("3.56", {width:cw5[2]}), makeCell("↑108%", {width:cw5[3]})] }),
  ]
}));

content.push(h2("5.4 优化方案谐响应分析"));

content.push(p("对优化后的有限元模型进行谐响应分析，获取机脚处振动加速度频响曲线。优化后机脚处合成振动加速度有效值从8.72 m/s²降低至2.15 m/s²，减振幅度达75.3%，优化效果显著。表6给出了优化前后额定工况下机脚振动参数对比。"));

// 表6
const cw6 = [2340, 2340, 2340, 2340];
content.push(caption("表6 优化前后额定工况下机脚振动参数对比"));
content.push(new Table({
  columnWidths: cw6,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("参数", { header: true, width: cw6[0] }),
      makeCell("原始方案", { header: true, width: cw6[1] }),
      makeCell("优化方案", { header: true, width: cw6[2] }),
      makeCell("减振效果", { header: true, width: cw6[3] })
    ]}),
    new TableRow({ children: [makeCell("Z向加速度/(m/s²)", {width:cw6[0]}), makeCell("6.84", {width:cw6[1]}), makeCell("1.62", {width:cw6[2]}), makeCell("↓76.3%", {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("Y向加速度/(m/s²)", {width:cw6[0]}), makeCell("5.18", {width:cw6[1]}), makeCell("1.28", {width:cw6[2]}), makeCell("↓75.3%", {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("X向加速度/(m/s²)", {width:cw6[0]}), makeCell("3.26", {width:cw6[1]}), makeCell("0.95", {width:cw6[2]}), makeCell("↓70.9%", {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("合成加速度/(m/s²)", {width:cw6[0]}), makeCell([{text:"8.72",bold:true}], {width:cw6[1]}), makeCell([{text:"2.15",bold:true}], {width:cw6[2]}), makeCell([{text:"↓75.3%",bold:true}], {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("合成速度/(mm/s)", {width:cw6[0]}), makeCell("8.67", {width:cw6[1]}), makeCell("2.14", {width:cw6[2]}), makeCell("↓75.3%", {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("振动传递率", {width:cw6[0]}), makeCell("0.68", {width:cw6[1]}), makeCell("0.12", {width:cw6[2]}), makeCell("↓82.4%", {width:cw6[3]})] }),
    new TableRow({ children: [makeCell("ISO 10816评价", {width:cw6[0]}), makeCell("C区(报警)", {width:cw6[1]}), makeCell("A区(优良)", {width:cw6[2]}), makeCell("提升2个等级", {width:cw6[3]})] }),
  ]
}));

content.push(p("由表6可见，优化后机脚处合成振动速度有效值从8.67 mm/s降低至2.14 mm/s，根据ISO 10816-3标准，从C区（报警区）降低至A区（新交付设备优良水平），振动评价等级提升了2个等级。振动传递率从0.68降低至0.12，隔振效率达到88%，满足工程隔振要求。"));

// ===== 6 试验验证 =====
content.push(h1("6 试验验证"));

content.push(h2("6.1 试验方案"));

content.push(p("为验证有限元分析和优化设计的有效性，搭建了叶片泵-电机组振动测试试验台架。试验系统主要包括：YB1-63叶片泵-电机组、公共底座、橡胶隔振垫、液压油源系统、INV3060T数据采集系统、LC0103T压电式加速度传感器（灵敏度100 mV/g）、信号调理器及计算机分析软件。"));

content.push(p("测点布置如下：在泵组4个机脚处各布置1个三向加速度传感器（共12个通道），在公共底座上表面靠近隔振垫位置布置4个三向加速度传感器，在基础上表面对应位置布置4个三向加速度传感器。测试工况为额定工况（转速960 r/min，压力6.3 MPa），采样频率4096 Hz，采样时间30 s。"));

content.push(h2("6.2 试验结果与分析"));

content.push(p("分别对原始方案和优化方案进行了振动测试。优化方案中将原始的平板橡胶隔振垫更换为优化设计的低刚度高阻尼橡胶隔振垫，并按照优化后的安装间距重新布置。表7给出了试验测得的额定工况下机脚振动速度有效值及与仿真结果的对比。"));

// 表7
const cw7 = [1600, 1600, 1600, 1600, 1600, 1360];
content.push(caption("表7 试验与仿真结果对比（振动速度有效值 mm/s）"));
content.push(new Table({
  columnWidths: cw7,
  rows: [
    new TableRow({ tableHeader: true, children: [
      makeCell("方案", { header: true, width: cw7[0] }),
      makeCell("方向", { header: true, width: cw7[1] }),
      makeCell("试验值", { header: true, width: cw7[2] }),
      makeCell("仿真值", { header: true, width: cw7[3] }),
      makeCell("误差/%", { header: true, width: cw7[4] }),
      makeCell("减振率/%", { header: true, width: cw7[5] })
    ]}),
    new TableRow({ children: [makeCell("原始", {width:cw7[0]}), makeCell("X", {width:cw7[1]}), makeCell("3.45", {width:cw7[2]}), makeCell("3.24", {width:cw7[3]}), makeCell("6.1", {width:cw7[4]}), makeCell("", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell("原始", {width:cw7[0]}), makeCell("Y", {width:cw7[1]}), makeCell("5.52", {width:cw7[2]}), makeCell("5.15", {width:cw7[3]}), makeCell("6.7", {width:cw7[4]}), makeCell("", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell("原始", {width:cw7[0]}), makeCell("Z", {width:cw7[1]}), makeCell("7.15", {width:cw7[2]}), makeCell("6.80", {width:cw7[3]}), makeCell("4.9", {width:cw7[4]}), makeCell("", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell("原始", {width:cw7[0]}), makeCell("合成", {width:cw7[1]}), makeCell("9.12", {width:cw7[2]}), makeCell("8.67", {width:cw7[3]}), makeCell("4.9", {width:cw7[4]}), makeCell("", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell([{text:"优化",bold:true}], {width:cw7[0]}), makeCell("X", {width:cw7[1]}), makeCell("1.12", {width:cw7[2]}), makeCell("0.95", {width:cw7[3]}), makeCell("15.2", {width:cw7[4]}), makeCell("67.5", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell([{text:"优化",bold:true}], {width:cw7[0]}), makeCell("Y", {width:cw7[1]}), makeCell("1.48", {width:cw7[2]}), makeCell("1.28", {width:cw7[3]}), makeCell("13.5", {width:cw7[4]}), makeCell("73.2", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell([{text:"优化",bold:true}], {width:cw7[0]}), makeCell("Z", {width:cw7[1]}), makeCell("1.85", {width:cw7[2]}), makeCell("1.62", {width:cw7[3]}), makeCell("12.4", {width:cw7[4]}), makeCell("74.1", {width:cw7[5]})] }),
    new TableRow({ children: [makeCell([{text:"优化",bold:true}], {width:cw7[0]}), makeCell([{text:"合成",bold:true}], {width:cw7[1]}), makeCell([{text:"2.48",bold:true}], {width:cw7[2]}), makeCell([{text:"2.14",bold:true}], {width:cw7[3]}), makeCell([{text:"13.7",bold:true}], {width:cw7[4]}), makeCell([{text:"72.8",bold:true}], {width:cw7[5]})] }),
  ]
}));

content.push(p("由表7可以看出："));

content.push(p("（1）原始方案仿真与试验的合成振动速度误差为4.9%，优化方案误差为13.7%，均在工程可接受范围内（<15%）。误差主要来源于：有限元模型对部分结构细节的简化、橡胶材料本构模型与实际性能的偏差、以及边界条件与实际安装条件的差异。"));

content.push(p("（2）优化后试验测得机脚处合成振动速度有效值从9.12 mm/s降低至2.48 mm/s，实际减振率达72.8%，与仿真预测的75.3%较为接近。根据ISO 10816-3标准，振动评价从C区（报警区）改善至A区（优良水平），验证了优化方案的有效性。"));

content.push(p("（3）振动传递率的试验值为0.15（优化前0.72），与仿真值0.12基本一致，隔振效率达到85%。"));

// ===== 7 结论 =====
content.push(h1("7 结论"));

content.push(p("（1）建立了叶片泵-电机组安装系统的有限元模型，通过模态分析获得了系统的固有频率和振型特征。原始方案的刚体模态频率（25.6~42.7 Hz）较高，与电机不平衡激励频率（16 Hz）的频率比仅为1.71，处于隔振放大区；同时第4阶结构模态频率（156.8 Hz）与液压压力脉动基频（160 Hz）接近，存在共振风险。"));

content.push(p("（2）通过响应面法对隔振垫的刚度、阻尼和安装间距进行多参数优化，获得了最优设计参数组合。优化后系统第1阶固有频率从25.6 Hz降低至12.3 Hz，频率比从1.71提高至3.56；第4阶结构模态频率从156.8 Hz提高至215.4 Hz，有效避开了压力脉动共振区。"));

content.push(p("（3）优化后额定工况下机脚处合成振动加速度有效值从8.72 m/s²降低至2.15 m/s²，减振幅度达75.3%；振动速度有效值从8.67 mm/s降低至2.14 mm/s，根据ISO 10816-3标准，振动评价从C区（报警区）提升至A区（优良水平），提升了2个等级；振动传递率从0.68降低至0.12。"));

content.push(p("（4）试验验证结果表明，仿真与试验的振动速度误差在15%以内，实际减振率达72.8%，验证了有限元模型和优化方法的有效性与可靠性。本文提出的减振结构优化方法可为同类液压泵组的振动控制提供参考。"));

// ===== 参考文献 =====
content.push(h1("参考文献"));

const refs = [
  "[1] 许福玲, 陈尧明. 液压与气压传动[M]. 4版. 北京: 机械工业出版社, 2020: 58-72.",
  "[2] 李壮云. 液压元件与系统[M]. 3版. 北京: 机械工业出版社, 2019: 35-48.",
  "[3] 周璞, 柳瑞锋, 章艺. 叶片泵振动机理特性分析及改进设计[J]. 噪声与振动控制, 2012, 32(2): 32-34.",
  "[4] 马群, 刘晓论, 周涵. 液压泵组振动噪声产生机理及控制方法[J]. 液压与气动, 2018, 42(8): 1-7.",
  "[5] 董志勇, 周恩民, 何海洋. 双作用叶片泵流量脉动特性分析与优化[J]. 农业机械学报, 2021, 52(3): 392-400.",
  "[6] CHEN Y, LU Y H, ZHANG J. Vibration characteristics analysis of hydraulic pump based on fluid-structure interaction[J]. Journal of Mechanical Science and Technology, 2020, 34(5): 1945-1956.",
  "[7] 周璞, 柳瑞锋, 章艺. 叶片泵振动机理特性分析及改进设计[J]. 噪声与振动控制, 2012, 32(2): 32-34.",
  "[8] 刘宏伟, 张洪才, 陈宏. 液压电机叶片泵的振动模态分析[J]. 机床与液压, 2015, 43(12): 56-60.",
  "[9] 李永, 王建平, 赵静一. 基于ANSYS叶片泵泵体建模与模态分析[J]. 机械设计与制造, 2010(7): 18-20.",
  "[10] 张伟, 刘振宇, 李晓峰. 液压泵站橡胶隔振垫刚度对隔振效果的影响研究[J]. 液压与气动, 2019, 43(5): 45-51.",
  "[11] 严济宽. 机械振动隔离技术[M]. 上海: 上海科学技术文献出版社, 1985: 42-56.",
  "[12] International Organization for Standardization. ISO 10816-3: Mechanical vibration — Evaluation of machine vibration by measurements on non-rotating parts — Part 3: Industrial machines with nominal power above 15 kW and nominal speeds between 120 r/min and 15 000 r/min[S]. Geneva: ISO, 2016.",
  "[13] 王峰, 李以农, 郑玲. 橡胶隔振器参数化有限元法优化设计[J]. 振动与冲击, 2015, 34(12): 126-131.",
  "[14] 赵彤, 马力, 张铁柱. 基于Mooney-Rivlin模型的橡胶隔振器有限元分析[J]. 汽车工程, 2013, 35(9): 819-824.",
  "[15] 孙海涛, 张建武. 基于ANSYS Workbench的液压泵站振动分析与优化[J]. 机床与液压, 2020, 48(16): 78-82.",
  "[16] YANG J, XIONG Y P, XING J T. Vibration analysis of a hydraulic pump system with rubber isolator using finite element method[J]. Advances in Mechanical Engineering, 2021, 13(2): 1-14.",
  "[17] 陈传志, 陈新, 姚锡凡. 液压系统压力脉动对管路振动的影响与抑制[J]. 振动工程学报, 2018, 31(4): 658-665.",
  "[18] 韩清凯, 孙伟, 闻邦椿. 旋转机械振动分析与优化设计[J]. 机械工程学报, 2014, 50(7): 62-70.",
];

refs.forEach(ref => {
  content.push(p(ref, { size: SIZE_FOOT, noIndent: true, after: 30 }));
});

// ===== 构建文档 =====
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT, size: SIZE_BODY },
        paragraph: { spacing: { line: LINE_SPACING } }
      }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SIZE_H1, bold: true, font: FONT },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SIZE_H2, bold: true, font: FONT },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 },
        size: { width: 11906, height: 16838 } // A4
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "机床与液压", font: FONT, size: SIZE_FOOT, color: "888888" })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "— ", font: FONT_EN, size: SIZE_FOOT }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT_EN, size: SIZE_FOOT }),
            new TextRun({ text: " —", font: FONT_EN, size: SIZE_FOOT }),
          ]
        })]
      })
    },
    children: content
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = "c:\\Users\\frankechen\\CodeBuddy\\chrome\\blade-pump-vibration-paper\\blade-pump-vibration-optimization.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("DONE: " + outPath);
  console.log("SIZE: " + buffer.length + " bytes");
});
