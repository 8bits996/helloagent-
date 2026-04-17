#!/usr/bin/env node

const WebScraperPlus = require('./src/index.js');
const path = require('path');
const fs = require('fs');

async function main() {
    const scraper = new WebScraperPlus();
    
    // 解析命令行参数
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('用法: node index.js <url> [输出格式: word|md] [输出文件名] [截图: true|false] [iwiki: true|false]');
        console.error('示例: node index.js https://example.com md my-report true true');
        process.exit(1);
    }
    
    const url = args[0];
    const format = args[1] || 'md';
    const outputFileName = args[2] || 'web-scraper-report';
    const takeScreenshot = args[3] === 'true';
    const uploadToIwiki = args[4] === 'true';
    
    try {
        // 爬取网页
        await scraper.scrapePage(url);
        
        // 生成相应格式的文档
        const outputPath = path.join(__dirname, `${outputFileName}.${format === 'word' ? 'docx' : 'md'}`);
        
        if (format === 'word') {
            await scraper.generateWordReport(outputPath);
        } else {
            scraper.generateMDReport(outputPath);
        }
        
        console.log(`文档生成成功: ${outputPath}`);
        
        // 截图功能
        if (takeScreenshot) {
            const screenshotPath = path.join(__dirname, `${outputFileName}-screenshot.png`);
            await scraper.takeScreenshot(screenshotPath);
            console.log(`截图保存成功: ${screenshotPath}`);
            
            // 上传到iWiki
            if (uploadToIwiki) {
                await scraper.uploadToIwiki(url, outputPath, screenshotPath);
            }
        }
        
    } catch (error) {
        console.error('处理过程中出错:', error);
        process.exit(1);
    }
}

main();