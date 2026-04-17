const readline = require('readline');

function promptUser() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const userInput = {
      product: '',
      keyPoints: '',
      useCase: ''
    };

    function askQuestion(question, field) {
      return new Promise((resolveQuestion) => {
        rl.question(question, (answer) => {
          userInput[field] = answer;
          resolveQuestion();
        });
      });
    }

    async function collectInput() {
      await askQuestion('请输入产品或主题：', 'product');
      await askQuestion('请输入核心卖点（用逗号分隔）：', 'keyPoints');
      await askQuestion('请输入使用场景：', 'useCase');
      
      rl.close();
      resolve(userInput);
    }

    collectInput();
  });
}

module.exports = { promptUser };