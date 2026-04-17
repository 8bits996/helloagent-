const fs = require('fs');
const path = require('path');

function generateDesignSchema(userInput, selectedStyle, selectedSize) {
  const { product, keyPoints, useCase } = userInput;
  
  // 确保keyPoints是数组
  const keyPointsArray = Array.isArray(keyPoints) ? keyPoints : [keyPoints];
  
  // 读取示例和模板
  const examplesPath = path.join(__dirname, '../../config/examples.json');
  const examples = JSON.parse(fs.readFileSync(examplesPath, 'utf8'));
  
  const styleTemplatesPath = path.join(__dirname, '../../config/style_templates.json');
  const styleTemplates = JSON.parse(fs.readFileSync(styleTemplatesPath, 'utf8'));
  
  // 根据产品类型选择示例模板（简化版，实际应更智能）
  const templateKey = product.includes('产品') ? 'product_promotion' : 
                    product.includes('活动') ? 'event_poster' : 'product_promotion';
  
  const example = examples[templateKey] || examples.product_promotion;
  
  return {
    intent: `宣传${product}，突出${keyPointsArray.join('、')}，适用于${useCase}`,
    visual_style: {
      style_name: selectedStyle.style_name,
      style_prompt: selectedStyle.style_prompt
    },
    size: {
      aspect_ratio: selectedSize.aspect_ratio,
      orientation: selectedSize.orientation,
      use_case: selectedSize.use_case
    },
    layout_structure: example.design_schema.layout_structure,
    content_mapping: example.design_schema.content_mapping.map(module => ({
      ...module,
      copy: module.copy.replace(/产品/g, product).replace(/功能特点/g, keyPointsArray.join('、'))
    }))
  };
}

module.exports = { generateDesignSchema };