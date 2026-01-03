#!/usr/bin/env python3
"""
保存KM文章为HTML和PDF格式
"""
import os
import time
import base64
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 文章URL列表
ARTICLES = [
    "https://km.woa.com/articles/show/637673?from=iSearch",
    "https://km.woa.com/knowledge/9948/node/183"
]

OUTPUT_DIR = "c:/Users/frankechen/CodeBuddy/chrome/km_article"

def setup_driver():
    """设置Chrome浏览器 - 连接到已运行的MCP浏览器"""
    chrome_options = Options()
    # 连接到MCP已启动的浏览器
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

def setup_driver_new():
    """设置新的Chrome浏览器实例"""
    chrome_options = Options()
    # 使用临时profile避免冲突
    chrome_options.add_argument(r"--user-data-dir=C:\Users\frankechen\.cache\chrome-km-save")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9224")
    
    # PDF打印设置
    chrome_options.add_experimental_option("prefs", {
        "printing.print_preview_sticky_settings.appState": json.dumps({
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": ""
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }),
        "savefile.default_directory": OUTPUT_DIR
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

def save_page_as_html(driver, output_path):
    """保存页面为HTML文件"""
    html_content = driver.page_source
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML已保存: {output_path}")

def save_page_as_pdf(driver, output_path):
    """使用Chrome DevTools Protocol保存页面为PDF"""
    # 隐藏不需要的元素
    try:
        driver.execute_script("""
            var style = document.createElement('style');
            style.textContent = `
                @media print {
                    .km-header, .km-footer, .km-sidebar, .article-sidebar, 
                    nav, header, footer, .watermark, .km-right-side, 
                    .article-right-side, .article-bottom-bar, .km-top-bar,
                    .article-action-bar, .comment-section, .recommend-section {
                        display: none !important;
                    }
                    .article-content, .km-article-json-content, .article-detail-wrapper {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    body {
                        background: white !important;
                    }
                }
            `;
            document.head.appendChild(style);
        """)
    except:
        pass
    
    # 使用CDP打印为PDF
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
        "printBackground": True,
        "preferCSSPageSize": True,
        "marginTop": 0.5,
        "marginBottom": 0.5,
        "marginLeft": 0.5,
        "marginRight": 0.5
    })
    
    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(pdf_data['data']))
    print(f"PDF已保存: {output_path}")

def take_full_screenshot(driver, output_path):
    """截取完整页面截图"""
    # 获取页面总高度
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # 设置窗口大小以捕获完整页面
    driver.set_window_size(1920, total_height)
    time.sleep(1)
    
    driver.save_screenshot(output_path)
    print(f"截图已保存: {output_path}")

def get_article_title(driver):
    """获取文章标题"""
    try:
        title = driver.title
        # 清理标题中的非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        return title[:100]  # 限制长度
    except:
        return "untitled"

def process_article(driver, url, index):
    """处理单篇文章"""
    print(f"\n处理文章 {index + 1}: {url}")
    
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        # 等待内容加载
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 滚动页面以加载所有图片
        driver.execute_script("""
            return new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 500;
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= document.body.scrollHeight){
                        clearInterval(timer);
                        window.scrollTo(0, 0);
                        resolve();
                    }
                }, 200);
            });
        """)
        time.sleep(2)
        
        title = get_article_title(driver)
        print(f"文章标题: {title}")
        
        # 保存HTML
        html_path = os.path.join(OUTPUT_DIR, f"{title}.html")
        save_page_as_html(driver, html_path)
        
        # 保存PDF
        pdf_path = os.path.join(OUTPUT_DIR, f"{title}.pdf")
        save_page_as_pdf(driver, pdf_path)
        
        # 保存截图
        screenshot_path = os.path.join(OUTPUT_DIR, f"{title}_full.png")
        take_full_screenshot(driver, screenshot_path)
        
        print(f"文章 {index + 1} 处理完成!")
        return True
        
    except Exception as e:
        print(f"处理文章时出错: {e}")
        return False

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    driver = None
    try:
        driver = setup_driver()
        
        for i, url in enumerate(ARTICLES):
            process_article(driver, url, i)
            time.sleep(2)
        
        print("\n所有文章处理完成!")
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
