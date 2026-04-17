# Design Schema Generator - 基于结构化中间态的 AI 设计方案生成器

这是一个用于生成 AI 设计方案的技能，通过结构化中间态（DesignSchema）桥接业务语义与视觉生成。

## 功能特性

- 🎨 生成结构化的设计方案
- 📝 支持多种设计风格选择
- 📐 支持多种尺寸选择
- 🎯 生成可直接用于 AI 生图的 Prompt
- 📊 结构化输出，便于理解和修改
- 🚀 支持图片生成（可选）

## 使用方法

```bash
# 启动技能
node src/index.js
```

### 交互流程

1. **接收用户需求** - 输入产品/主题、核心卖点、使用场景
2. **风格选择** - 选择设计风格（简笔画、学术海报、扁平化等）
3. **尺寸选择** - 选择宣传图尺寸（16:9、4:3、1:1等）
4. **生成 DesignSchema** - 创建结构化中间态
5. **输出 Prompt** - 转换为 AI 生图可用的 Prompt
6. **生成图片** - 可选步骤，调用 API 生成图片

## 配置文件

### 风格模板 (`config/style_templates.json`)

定义各种设计风格的 Prompt 模板：

```json
{
  "简笔画风格": {
    "prompt_template": "minimalist line art, white background, clean simple lines, fresh and literary...",
    "chinese_text_suffix": "使用中文绘制，所有中文必须做独立文字图层处理，清晰可读。"
  }
}
```

### 示例 (`config/examples.json`)

包含预设的设计方案示例，用于生成 DesignSchema：

```json
{
  "product_promotion": {
    "design_schema": {
      "intent": "宣传产品发布，突出产品核心功能...",
      "visual_style": { ... },
      "size": { ... },
      "layout_structure": { ... },
      "content_mapping": [ ... ]
    }
  }
}
```

## 输出格式

### 1. 需求确认摘要
- 产品/主题
- 核心卖点  
- 使用场景

### 2. DesignSchema JSON
```json
{
  "intent": "...",
  "visual_style": { ... },
  "size": { ... },
  "layout_structure": { ... },
  "content_mapping": [ ... ]
}
```

### 3. 最终 Prompt
```markdown
## 一、设计风格
（⚠️ 必须原样输出 config/style_templates.json 中对应风格的 prompt_template 字段，一字不改）

[风格模板内容]

## 二、页面布局
...

## 三、详细板块设计建议
...

## 四、中文适配
（⚠️ 必须原样输出 config/style_templates.json 的 chinese_text_suffix 字段）
```

### 4. 流程总结表格
| 阶段 | 输出 |
|------|------|
| 输入 | 用户自然语言需求 |
| 中间态 | DesignSchema JSON |
| Prompt | 结构化设计方案 Prompt |
| 图片 | 生成的宣传图（如调用API） |

## 技术实现

- 使用 Node.js 开发
- 支持命令行交互
- 模块化设计，易于扩展
- 支持自定义风格和尺寸

## 扩展功能

- 集成 AI 生图 API（如 Midjourney、Banana Pro）
- 添加更多设计风格模板
- 支持批量生成设计方案
- 导出多种格式（JSON、Markdown、PDF）

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个技能。