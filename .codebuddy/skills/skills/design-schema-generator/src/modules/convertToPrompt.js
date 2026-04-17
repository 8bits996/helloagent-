function convertToPrompt(designSchema) {
  const { visual_style, size, layout_structure, content_mapping } = designSchema;
  
  // 获取中文适配后缀
  const chineseTextSuffix = visual_style.style_prompt.includes('chinese') ? 
    visual_style.style_prompt.split('chinese ')[1] || '使用中文绘制，所有中文必须做独立文字图层处理，清晰可读。' : 
    '使用中文绘制，所有中文必须做独立文字图层处理，清晰可读。';
  
  let prompt = `## 一、设计风格\n\n（⚠️ 必须原样输出 config/style_templates.json 中对应风格的 prompt_template 字段，一字不改）\n\n${visual_style.style_prompt}\n\n## 二、页面布局\n\n**画布尺寸**：${size.aspect_ratio} ${size.orientation}\n**适用场景**：${size.use_case}\n\n**整体布局结构**：${layout_structure.description}\n\n**空间分配**：\n${layout_structure.ascii_wireframe}\n（括号内为各区域占画面的高度/宽度百分比）\n\n**视觉动线**：${layout_structure.visual_flow}\n\n**层次关系**：\n- 第一视觉层（最先注意）：${layout_structure.hierarchy.split('；')[0]}\n- 第二视觉层（细节阅读）：${layout_structure.hierarchy.split('；')[1]}\n- 第三视觉层（品牌印象）：${layout_structure.hierarchy.split('；')[2]}\n\n## 三、详细板块设计建议\n`;
  
  // 添加各个模块的详细设计
  content_mapping.forEach(module => {
    prompt += `\n### 模块${module.zone} - ${module.zone_name}\n`;
    prompt += `- **位置与占比**：${module.position}，占画面${module.size_ratio}\n`;
    prompt += `- **核心内容**：${module.copy}\n`;
    prompt += `- **主要视觉元素**：${module.visual_elements.primary}\n`;
    prompt += `- **次要/装饰元素**：${module.visual_elements.secondary}\n`;
    prompt += `- **设计要点**：${module.design_notes}\n`;
  });
  
  prompt += `\n## 四、中文适配\n\n（⚠️ 必须原样输出 config/style_templates.json 的 chinese_text_suffix 字段）\n${chineseTextSuffix}`;
  
  return prompt;
}

module.exports = { convertToPrompt };