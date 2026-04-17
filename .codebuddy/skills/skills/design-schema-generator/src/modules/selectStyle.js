const fs = require('fs');
const path = require('path');

function selectStyle() {
  return new Promise((resolve) => {
    const rl = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });

    // 读取风格模板
    const styleTemplatesPath = path.join(__dirname, '../../config/style_templates.json');
    const styleTemplates = JSON.parse(fs.readFileSync(styleTemplatesPath, 'utf8'));

    console.log('\n请选择设计风格（回复数字或名称）：');
    console.log('| 序号 | 风格 | 特点 |');
    console.log('|------|------|------|');
    
    const styles = Object.keys(styleTemplates);
    styles.forEach((style, index) => {
      const template = styleTemplates[style];
      console.log(`| ${index + 1} | ${style} | ${template.prompt_template.substring(0, 50)}... |`);
    });
    console.log('| 6 | 自定义 | 请描述你想要的风格 |');

    rl.question('\n请输入选择：', (answer) => {
      const choice = answer.trim();
      
      let selectedStyle;
      
      if (choice === '6' || choice.toLowerCase() === '自定义') {
        rl.question('请描述你想要的风格：', (customStyle) => {
          selectedStyle = {
            style_name: customStyle.trim() || '自定义风格',
            style_prompt: customStyle.trim() || 'custom artistic style'
          };
          rl.close();
          resolve(selectedStyle);
        });
      } else {
        const index = parseInt(choice) - 1;
        if (index >= 0 && index < styles.length) {
          const styleName = styles[index];
          selectedStyle = {
            style_name: styleName,
            style_prompt: styleTemplates[styleName].prompt_template
          };
          rl.close();
          resolve(selectedStyle);
        } else {
          console.log('无效选择，请重新选择');
          selectStyle().then(resolve);
        }
      }
    });
  });
}

module.exports = { selectStyle };