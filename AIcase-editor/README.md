# Case Editor - 广告案例可视化编辑器

将广告投放数据转化为有商业吸引力的营销案例，支持可视化编辑与一键导出。

## 功能特性

- **可视化编辑** - 双击元素直接修改文字、图片
- **实时预览** - 所见即所得，支持缩放和设备切换
- **案例列表** - 查看已生成案例，快速打开编辑
- **版本管理** - 撤销/重做，历史记录
- **一键导出** - 支持 JPG 图片 / HTML 文件导出
- **双格式输出** - 同时生成横版（16:9）和竖版（长图）

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

浏览器访问 `http://localhost:5173`

## 项目结构

```
case-editor/
├── Skill.md                        # AI 制作指南（核心）
├── Workflow.md                     # 流程图
├── docs/                           # 文档资源
│   ├── 模板/                        # Markdown 模板
│   │   ├── 01-数据亮点分析模板.md
│   │   ├── 02-案例文档模板.md
│   │   └── 03-脱敏确认表.md
│   ├── 指南/
│   │   ├── KNOW-HOW.md             # 经验总结
│   │   └── SOP.md                  # 标准流程
│   └── 历史案例/                    # 参考案例
├── public/
│   ├── templates/                  # HTML 模板
│   │   ├── 长图模板.html            # 微信传播、H5
│   │   ├── 横版16x9模板.html        # PPT 演示
│   │   ├── _schema.json            # 模板规范
│   │   ├── tencentadslogo.html     # Logo 组件
│   │   └── 组件库/                  # 图表组件
│   └── 输出/                       # 案例索引（编辑器读取）
├── src/                            # 编辑器源码
│   ├── components/
│   │   ├── Editor.jsx              # 主编辑器
│   │   ├── HtmlPane.jsx            # HTML 预览面板
│   │   ├── FileSelector.jsx        # 文件选择器（含案例列表）
│   │   ├── ExportModal.jsx         # 导出功能
│   │   └── ...
│   └── hooks/
│       ├── useHistory.js           # 撤销/重做
│       └── useSync.js              # 内容同步
└── 输出/                           # 最终产出目录
```

## 模板说明

| 模板 | 文件命名 | 适用场景 |
|-----|---------|---------|
| **竖版（长图）** | `XX案例-竖版.html` | 微信传播、H5、手机浏览 |
| **横版（16:9）** | `XX案例-横版.html` | PPT演示、投屏、屏幕分享 |

> AI 生成时会同时输出两个版本

## HTML 规范

编辑器支持的 HTML 需遵循 `_schema.json` 规范：

```html
<!-- 可编辑元素：必须包含 data-slot -->
<h1 data-slot="title" data-type="text">标题内容</h1>

<!-- 区块标记：必须包含 data-section -->
<section data-section="header">...</section>
<section data-section="result">...</section>

<!-- Logo 引用：使用 iframe -->
<iframe src="/templates/tencentadslogo.html" style="border:none; width:140px; height:36px;"></iframe>

<!-- 槽位类型 -->
data-type="text"      <!-- 纯文本 -->
data-type="richtext"  <!-- 富文本 -->
data-type="number"    <!-- 数字 -->
data-type="image"     <!-- 图片 -->
```

## 快捷键

| 快捷键 | 功能 |
|-------|------|
| `⌘ + Z` | 撤销 |
| `⌘ + Shift + Z` | 重做 |
| `⌘ + S` | 保存 |

## 技术栈

- React 18
- Vite 4
- Tailwind CSS
- CodeMirror 6
- html-to-image

## 案例制作流程

1. **数据收集** - 收集投放数据、客户信息，确认指标含义
2. **亮点提炼** - 识别核心亮点，处理弱项，**确认案例故事线**
3. **文档撰写** - 使用模板撰写案例文档
4. **数据脱敏** - **交互式选择**确认敏感信息处理
5. **HTML 制作** - **同时生成横版+竖版**两个版本

详细指南见 `Skill.md`

## License

MIT
