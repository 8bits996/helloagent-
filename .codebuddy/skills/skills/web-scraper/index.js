#!/usr/bin/env node

const WebScraper = require('./scraper.js');
const path = require('path');

async function main() {
    const scraper = new WebScraper();
    
    // 解析命令行参数
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('用法: node index.js <url> [输出格式: word|md|pdf] [输出文件名]');
        console.error('示例: node index.js https://example.com word my-report');
        process.exit(1);
    }
    
    const url = args[0];
    const format = args[1] || 'md'; // 默认为 MD 格式
    const outputFileName = args[2] || 'web-scraper-report';
    
    try {
        // 爬取网页
        await scraper.scrapePage(url);
        
        // 生成相应格式的文档
        const outputPath = path.join(__dirname, `${outputFileName}.${format === 'word' ? 'docx' : format === 'pdf' ? 'pdf' : 'md'}`);
        
        if (format === 'word') {
            scraper.generateWordReport(outputPath);
        } else if (format === 'pdf') {
            await scraper.generatePDFReport(outputPath);
        } else {
            scraper.generateMDReport(outputPath);
        }
        
        console.log(`文档生成成功: ${outputPath}`);
        
    } catch (error) {
        console.error('处理过程中出错:', error);
        process.exit(1);
    }
}

main();