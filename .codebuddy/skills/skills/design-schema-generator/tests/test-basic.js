const { DesignSchemaGenerator } = require('../src/index.js');

async function testDesignSchemaGenerator() {
  const generator = new DesignSchemaGenerator();
  
  // 模拟用户输入
  generator.userInput = {
    product: 'AI 产品',
    keyPoints: '智能分析、高效处理、云端同步、安全保障',
    useCase: '产品宣传'
  };
  
  // 模拟风格选择
  generator.selectedStyle = {
    style_name: '科技渐变风',
    style_prompt: 'tech gradient style, dark background, neon light effects, strong tech feel, futuristic, cyberpunk aesthetic, glowing effects, digital art, high contrast, modern technology, sci-fi design, gradient backgrounds, neon colors'
  };
  
  // 模拟尺寸选择
  generator.selectedSize = {
    aspect_ratio: '16:9',
    orientation: '横版',
    use_case: 'PPT宽屏、官网Banner、社交媒体'
  };
  
  // 测试 DesignSchema 生成
  generator.generateDesignSchema();
  
  // 测试 Prompt 转换
  const prompt = generator.convertToPrompt();
  
  console.log('测试通过！');
  console.log('DesignSchema 生成成功');
  console.log('Prompt 转换成功');
  console.log('生成的 Prompt 长度：', prompt.length);
}

testDesignSchemaGenerator().catch(console.error);