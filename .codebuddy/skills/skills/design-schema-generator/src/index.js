const { promptUser } = require('./modules/promptUser');
const { parseUserInput } = require('./modules/parseInput');
const { selectStyle } = require('./modules/selectStyle');
const { selectSize } = require('./modules/selectSize');
const { generateDesignSchema } = require('./modules/generateSchema');
const { convertToPrompt } = require('./modules/convertToPrompt');
const { generateImage } = require('./modules/generateImage');

class DesignSchemaGenerator {
  constructor() {
    this.userInput = {};
    this.selectedStyle = {};
    this.selectedSize = {};
    this.designSchema = {};
  }

  async start() {
    try {
      // Step 1: 接收用户需求
      await this.getUserInput();
      
      // Step 2: 风格选择
      await this.selectDesignStyle();
      
      // Step 3: 尺寸选择
      await this.selectDesignSize();
      
      // Step 4: 生成 DesignSchema
      this.generateDesignSchema();
      
      // Step 5: 输出最终 Prompt
      const prompt = this.convertToPrompt();
      
      // Step 6: 可选 - 生成图片
      await this.generateImageIfNeeded();
      
      // 输出结果
      this.displayResults(prompt);
      
    } catch (error) {
      console.error('生成过程中出错:', error);
    }
  }

  async getUserInput() {
    this.userInput = await promptUser();
    console.log('需求确认摘要：');
    console.log(`- 产品/主题：${this.userInput.product}`);
    console.log(`- 核心卖点：${this.userInput.keyPoints}`);
    console.log(`- 使用场景：${this.userInput.useCase}`);
  }

  async selectDesignStyle() {
    this.selectedStyle = await selectStyle();
    console.log(`已选择风格：${this.selectedStyle.style_name}`);
  }

  async selectDesignSize() {
    this.selectedSize = await selectSize();
    console.log(`已选择尺寸：${this.selectedSize.aspect_ratio} ${this.selectedSize.orientation}`);
  }

  generateDesignSchema() {
    this.designSchema = generateDesignSchema(this.userInput, this.selectedStyle, this.selectedSize);
  }

  convertToPrompt() {
    return convertToPrompt(this.designSchema);
  }

  async generateImageIfNeeded() {
    // 这里可以实现图片生成的逻辑
    // 目前为可选步骤，用户可以选择是否生成
    console.log('图片生成功能为可选步骤，如需生成请调用相应API');
  }

  displayResults(prompt) {
    console.log('\n=== 生成结果 ===');
    console.log('\n1. 需求确认摘要：');
    console.log(`- 产品/主题：${this.userInput.product}`);
    console.log(`- 核心卖点：${this.userInput.keyPoints}`);
    console.log(`- 使用场景：${this.userInput.useCase}`);
    
    console.log('\n2. DesignSchema JSON：');
    console.log('```json');
    console.log(JSON.stringify(this.designSchema, null, 2));
    console.log('```');
    
    console.log('\n3. 最终 Prompt：');
    console.log(prompt);
    
    console.log('\n4. 流程总结表格：');
    console.log('| 阶段 | 输出 |');
    console.log('|------|------|');
    console.log('| 输入 | 用户自然语言需求 |');
    console.log('| 中间态 | DesignSchema JSON |');
    console.log('| Prompt | 结构化设计方案 Prompt |');
    console.log('| 图片 | 生成的宣传图（如调用API） |');
  }
}

// 导出类
module.exports = { DesignSchemaGenerator };