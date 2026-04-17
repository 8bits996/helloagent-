---
name: ad-case-production
description: 广告投放案例制作。当用户提供投放数据、要求制作案例时激活。
allowed-tools: [Read, Write, Edit, Glob, Bash, ask_followup_question]
---

# 广告案例制作 Skill

## 流程

```
阶段一(数据收集) → 阶段二(亮点提炼) → 阶段三(文档撰写) → 阶段四(数据脱敏) → 阶段五(HTML生成)
```

**必须交互确认**: 
- 阶段一：动态识别并确认歧义指标
- 阶段二：多轮确认故事线，充分了解用户想法
- 阶段四：交互式脱敏选择
- 阶段五：确认生成横版/竖版/两者

---

## 阶段一：数据收集

收集: 投放数据(时间/消耗/订单/ROI/CTR/CVR)、客户信息(公司/产品/行业)、大盘数据(可选)

**必须确认歧义指标**:
- 分析用户提供的数据，识别所有可能存在歧义的指标
- 常见歧义指标示例（不限于此）:

  - 浅层CVR → "转化事件是什么(进入直播间/加购/下单)?"
  - 创意指纹数 → "是素材数量吗?"

- **必须根据实际数据动态识别歧义项，使用 `ask_followup_question` 逐一确认**

---

## 阶段二：亮点提炼

**亮点识别**:
- 增速类: 环比>100%显著, >300%爆点 → "次日订单暴增478%"
- 对比类: 高于大盘>20% → "完播率高出大盘26%"
- ROI类: >2.5优秀, >5非常优秀 → "ROI峰值8.56"

**弱项处理**: 不展示或转化说辞(CTR低→"精准定向", 规模小→"快速验证模型")

**必须多轮确认故事线**:
1. 首轮：提出初步故事线建议，询问用户想法
2. 迭代：根据用户反馈调整，直到用户满意
3. 主动询问：
   - "您希望突出哪些方面？(增长/ROI/产品能力/行业趋势)"
   - "有没有特别想强调或必须包含的信息？"
   - "这个故事线方向符合您的预期吗？需要调整哪些部分？"

```
📋 案例故事线确认（第N轮）
【主标题】[建议标题]
【核心卖点】1. [亮点1] 2. [亮点2]
【隐藏/弱化】[弱项处理]

请告诉我：
- 这个方向是否符合预期？
- 有什么需要调整或补充的？
```

**输出**: `public/XX案例-数据亮点分析思路.md`（故事线确认后再输出）

---

## 阶段三：文档撰写

**标题公式**: 数字冲击 + 核心成果 + 技术产品
- ❌ "腾讯广告-XX案例"
- ✅ "投放次日订单暴增478%！PA归因助力XX实现ROI 8+"

**文档结构**: 客户背景(200字) → 投放方案(300字) → 投放效果(50%篇幅,重点) → 成功经验 → FAQ(3-5个)

**输出**: `public/XX案例.md`

---

## 阶段四：数据脱敏

**必须使用 `ask_followup_question` 工具让用户选择**:

脱敏范围包括:
- 公司/产品名称
- 精确数值(GMV、订单量等)
- **图表元素**: 时间标签、峰值数值、拐点标注、凸显标签

```json
{
  "questions": "[{\"id\":\"q1\",\"question\":\"公司名称 'XX科技'\",\"options\":[\"保留原名\",\"脱敏为'某教育品牌'\",\"隐藏\"]},{\"id\":\"q2\",\"question\":\"图表峰值 '12/9 GMV 152万'\",\"options\":[\"保留精确值+日期\",\"脱敏为'150万+'\",\"仅显示趋势不标数值\"]}]"
}
```

---

## 阶段五：HTML生成

**生成前必须确认输出版本**:
使用 `ask_followup_question` 询问用户：
```json
{
  "questions": "[{\"id\":\"q1\",\"question\":\"需要生成哪些HTML版本？\",\"options\":[\"仅横版(PPT/投屏)\",\"仅竖版(手机/微信长图)\",\"两个版本都要\"],\"multiSelect\":false}]"
}
```

**版本说明**:
- `public/XX案例-横版.html` - 16:9比例，适合PPT/投屏演示
- `public/XX案例-竖版.html` - 长图形式，适合手机/微信分享

**生成前必读**:
1. `public/templates/_schema.json` - 模板规范
2. `public/templates/横版16x9模板.html` - 横版模板（如需横版）
3. `public/templates/长图模板.html` - 竖版模板（如需竖版）

**规范要点**:
- 可编辑元素: `<h1 data-slot="title" data-type="text">...</h1>`
- 区块标记: `<section data-section="header">...</section>`
- Logo: `<iframe src="/templates/tencentadslogo.html" style="border:none;width:140px;height:36px;"></iframe>`

**配色**: primary=#00f2ff, secondary=#7000ff, accent=#facc15, bg=#020617

**序列数据图表**:
- 若提供时间序列数据，生成SVG曲线图(GMV/ROI/消耗趋势)
- 使用`<svg viewBox="0 0 400 120">`绑定真实数据点生成path
- 标注关键节点(峰值、拐点)，添加X轴时间标签
- 双曲线对比时用不同颜色区分(primary vs slate)
- **图表中的时间标签、具体数值、峰值标注须在阶段四确认脱敏**

**图片占位符(按需)**:
- 根据故事线需要添加，非必须
- 广告外层: `<div data-slot="ad_creative" data-type="image" class="aspect-[9/16]..."><span>广告外层素材</span></div>`
- 产品图: `<div data-slot="product_image" data-type="image" class="aspect-square..."><span>产品图</span></div>`
- 直播间: `<div data-slot="livestream" data-type="image" class="aspect-video..."><span>直播间截图</span></div>`
- 必须包含`data-slot`和`data-type="image"`属性

---

## 输出清单

| 文件 | 说明 |
|-----|------|
| `XX案例-数据亮点分析思路.md` | 亮点分析 |
| `XX案例-最新版.md` | 主文档 |
| `XX案例-横版.html` | 横版(PPT) - 按需生成 |
| `XX案例-竖版.html` | 竖版(手机) - 按需生成 |

**所有文件输出到 `public/` 目录**

**索引文件(必须更新)**:
每次生成案例后，必须更新 `public/cases-index.json`:
```json
{
  "files": [
    {"name": "XX案例-横版.html", "desc": "横版"},
    {"name": "XX案例-竖版.html", "desc": "竖版"}
  ]
}
```
- 追加新案例到files数组，保留已有条目
- 若文件不存在则创建
- **仅添加实际生成的HTML文件**

---

## 质量检查

- [ ] 指标含义已确认（动态识别歧义指标）
- [ ] 故事线已多轮确认（充分了解用户想法）
- [ ] 脱敏已交互确认(含图表标签/数值)
- [ ] HTML版本已与用户确认（横版/竖版/两者）
- [ ] HTML包含data-slot/data-section
- [ ] Logo使用iframe引用
- [ ] 序列数据已生成SVG曲线图(如有)
- [ ] cases-index.json已更新
