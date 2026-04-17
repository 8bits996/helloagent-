const readline = require('readline');

function selectSize() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\n请选择宣传图尺寸（回复数字或自定义输入）：');
    console.log('| 序号 | 尺寸 | 适用场景 |');
    console.log('|------|------|----------|');
    console.log('| 1 | 16:9 横版 | PPT宽屏、公众号头图、官网Banner |');
    console.log('| 2 | 4:3 横版 | 传统演示、产品展示 |');
    console.log('| 3 | 1:1 方形 | 社交媒体、朋友圈、小红书 |');
    console.log('| 4 | 9:16 竖版 | 手机壁纸、短视频封面、小红书 |');
    console.log('| 5 | 3:4 竖版 | 海报、易拉宝 |');
    console.log('| 6 | 自定义 | 请输入宽高比，如 21:9 |');

    rl.question('\n请输入选择：', (answer) => {
      const choice = answer.trim();
      
      let selectedSize;
      
      if (choice === '6' || choice.toLowerCase() === '自定义') {
        rl.question('请输入宽高比，如 21:9：', (customSize) => {
          const [width, height] = customSize.split(':').map(s => s.trim());
          selectedSize = {
            aspect_ratio: customSize.trim(),
            orientation: width > height ? '横版' : '竖版',
            use_case: '自定义尺寸'
          };
          rl.close();
          resolve(selectedSize);
        });
      } else {
        const index = parseInt(choice);
        const sizes = [
          { aspect_ratio: '16:9', orientation: '横版', use_case: 'PPT宽屏、公众号头图、官网Banner' },
          { aspect_ratio: '4:3', orientation: '横版', use_case: '传统演示、产品展示' },
          { aspect_ratio: '1:1', orientation: '方形', use_case: '社交媒体、朋友圈、小红书' },
          { aspect_ratio: '9:16', orientation: '竖版', use_case: '手机壁纸、短视频封面、小红书' },
          { aspect_ratio: '3:4', orientation: '竖版', use_case: '海报、易拉宝' }
        ];
        
        if (index >= 1 && index <= 5) {
          selectedSize = sizes[index - 1];
          rl.close();
          resolve(selectedSize);
        } else {
          console.log('无效选择，请重新选择');
          selectSize().then(resolve);
        }
      }
    });
  });
}

module.exports = { selectSize };