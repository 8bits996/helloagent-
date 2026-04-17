const fs = require('fs');
const path = require('path');

const skillPath = path.join(__dirname, '..');

// 创建必要的目录结构
const dirs = [
    'config',
    'config/examples',
    'src',
    'src/modules',
    'src/utils',
    'tests'
];

dirs.forEach(dir => {
    const fullPath = path.join(skillPath, dir);
    if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        console.log(`创建目录: ${dir}`);
    }
});

// 创建基本文件
const files = [
    { path: 'config/style_templates.json', content: '{}' },
    { path: 'config/examples.json', content: '{}' },
    { path: 'src/index.js', content: 'module.exports = {};' },
    { path: 'package.json', content: '{}'}
];

files.forEach(file => {
    const fullPath = path.join(skillPath, file.path);
    if (!fs.existsSync(fullPath)) {
        fs.writeFileSync(fullPath, file.content);
        console.log(`创建文件: ${file.path}`);
    }
});

console.log('技能结构创建完成！');