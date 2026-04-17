const https = require('https');
const fs = require('fs');
const path = require('path');

// 图片 URL 列表
const imageUrls = [
    'https://sid-preview-sh-1258344699.previewsh.myqcloud.com/shapes%2Flexiang-10029162_7b0e0603c8f807e7eedf633cf143834d2c52a191%2F18f7ff62a4f397ac1b765251ede23b30?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDaz7GCrPc5LL5YotAuyqRr1yFL8fYu8Wg%26q-sign-time%3D1769521542%3B1769644800%26q-key-time%3D1769521542%3B1769644800%26q-header-list%3D%26q-url-param-list%3D%26q-signature%3Dfb98d8121913428c4aeb8b94ecb2f0c14e179bcb',
    'https://sid-preview-sh-1258344699.previewsh.myqcloud.com/shapes%2Flexiang-10029162_7b0e0603c8f807e7eedf633cf143834d2c52a191%2Fce2ad44c19c1fb670d66e4ba5b4b31d2?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDaz7GCrPc5LL5YotAuyqRr1yFL8fYu8Wg%26q-sign-time%3D1769521542%3B1769644800%26q-key-time%3D1769521542%3B1769644800%26q-header-list%3D%26q-url-param-list%3D%26q-signature%3D76720ff052cfe3ac9af0e1408644d8e643ecbba8',
    'https://sid-preview-sh-1258344699.previewsh.myqcloud.com/shapes%2Flexiang-10029162_7b0e0603c8f807e7eedf633cf143834d2c52a191%2Fca8a820e7b50853b2c396a9fb4e1d178?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDaz7GCrPc5LL5YotAuyqRr1yFL8fYu8Wg%26q-sign-time%3D1769521542%3B1769644800%26q-key-time%3D1769521542%3B1769644800%26q-header-list%3D%26q-url-param-list%3D%26q-signature%3Dd0c1e13753b97b650996b8d77a09979a80ef74e7',
    'https://sid-preview-sh-1258344699.previewsh.myqcloud.com/shapes%2Flexiang-10029162_7b0e0603c8f807e7eedf633cf143834d2c52a191%2F9f01f80f787e85f7227fe724f9629922?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDaz7GCrPc5LL5YotAuyqRr1yFL8fYu8Wg%26q-sign-time%3D1769521542%3B1769644800%26q-key-time%3D1769521542%3B1769644800%26q-header-list%3D%26q-url-param-list%3D%26q-signature%3D401bb95d27ff0238e17366f2864fa345679920bb'
];

const imageNames = [
    'aaru_screenshot1.png',
    'competitor_a_screenshot.png',
    'competitor_b_screenshot.png',
    'competitor_c_screenshot.png'
];

function downloadImage(url, filename) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filename);
        
        https.get(url, (response) => {
            response.pipe(file);
            
            file.on('finish', () => {
                file.close(resolve);
            });
            
            file.on('error', (err) => {
                fs.unlink(filename);
                reject(err);
            });
        }).on('error', (err) => {
            fs.unlink(filename);
            reject(err);
        });
    });
}

async function downloadAllImages() {
    console.log('开始下载图片...');
    
    for (let i = 0; i < imageUrls.length; i++) {
        try {
            await downloadImage(imageUrls[i], imageNames[i]);
            console.log(`已下载: ${imageNames[i]}`);
        } catch (error) {
            console.error(`下载 ${imageNames[i]} 时出错:`, error);
        }
    }
    
    console.log('所有图片下载完成');
}

downloadAllImages();