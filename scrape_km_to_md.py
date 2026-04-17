#!/usr/bin/env python3
"""
爬取km.woa.com文章内容并转换为Markdown格式
"""
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import html2text

# 文章URL列表
ARTICLES = [
    "https://km.woa.com/articles/show/651243?kmref=author_recommend",
    "https://km.woa.com/articles/show/650673",
    "https://km.woa.com/base/attachments/attachment_view/277645",
    "https://km.woa.com/base/attachments/attachment_view/277676"
]

OUTPUT_DIR = "c:/Users/frankechen/CodeBuddy/chrome/km_articles_md"

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
    chrome_options.add_argument(r"--user-data-dir=C:\Users\frankechen\.cache\chrome-km-scrape")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9225")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

def html_to_markdown(html_content):
    """将HTML转换为Markdown"""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # 不自动换行
    h.unicode_snob = True
    return h.handle(html_content)

def extract_article_content(driver):
    """提取文章内容"""
    # 等待页面加载
    time.sleep(3)
    
    # 滚动页面以加载所有内容
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
    
    # 获取页面标题
    title = driver.title
    
    # 尝试多种可能的内容选择器
    content_selectors = [
        '.article-content',
        '.km-article-json-content',
        '.article-detail-wrapper',
        '.markdown-body',
        '.wiki-content',
        '[class*="content"]',
        'article'
    ]
    
    article_html = ""
    content_div = None
    
    for selector in content_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                content_div = elements[0]
                article_html = content_div.get_attribute('innerHTML')
                print(f"使用选择器 '{selector}' 找到内容")
                break
        except:
            continue
    
    # 如果没有找到内容，尝试获取整个body
    if not article_html:
        print("未找到特定内容区域，尝试获取整个body")
        article_html = driver.find_element(By.TAG_NAME, "body").get_attribute('innerHTML')
    
    # 提取元数据（作者、时间等）
    metadata = {}
    try:
        # 尝试查找作者
        author_selectors = ['.author', '.writer', '[class*="author"]']
        for sel in author_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            if elements:
                metadata['author'] = elements[0].text.strip()
                break
    except:
        pass
    
    try:
        # 尝试查找发布时间
        time_selectors = ['.time', '.date', '[class*="time"]', '[class*="date"]']
        for sel in time_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            if elements:
                metadata['date'] = elements[0].text.strip()
                break
    except:
        pass
    
    return title, article_html, metadata

def clean_filename(filename):
    """清理文件名中的非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # 去除或替换换行符
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    filename = re.sub(r'\s+', ' ', filename)  # 合并多个空格
    return filename[:150]  # 限制长度

def process_article(driver, url, index):
    """处理单篇文章"""
    print(f"\n{'='*60}")
    print(f"处理文章 {index + 1}/{len(ARTICLES)}: {url}")
    print(f"{'='*60}")
    
    try:
        driver.get(url)
        print(f"页面已加载")
        
        # 检查是否重定向到登录页
        if 'signin.ashx' in driver.current_url or 'login' in driver.current_url.lower():
            print(f"警告: 页面重定向到登录页面，可能需要先登录")
            print(f"当前URL: {driver.current_url}")
            return False
        
        # 等待页面加载
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print("等待页面超时，继续尝试...")
        
        # 提取内容
        title, article_html, metadata = extract_article_content(driver)
        print(f"文章标题: {title}")
        
        if metadata:
            print(f"元数据: {metadata}")
        
        # 转换为Markdown
        markdown_content = html_to_markdown(article_html)
        
        # 构建完整的Markdown文档
        full_markdown = f"# {title}\n\n"
        
        if metadata:
            if 'author' in metadata:
                full_markdown += f"**作者**: {metadata['author']}\n\n"
            if 'date' in metadata:
                full_markdown += f"**时间**: {metadata['date']}\n\n"
        
        full_markdown += f"**来源**: {url}\n\n"
        full_markdown += "---\n\n"
        full_markdown += markdown_content
        
        # 保存为Markdown文件
        clean_title = clean_filename(title)
        md_filename = f"{clean_title}.md"
        md_path = os.path.join(OUTPUT_DIR, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)
        
        print(f"✓ Markdown文件已保存: {md_path}")
        print(f"✓ 内容长度: {len(markdown_content)} 字符")
        
        # 同时保存原始HTML
        html_filename = f"{clean_title}.html"
        html_path = os.path.join(OUTPUT_DIR, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print(f"✓ HTML文件已保存: {html_path}")
        print(f"文章 {index + 1} 处理完成!")
        return True
        
    except Exception as e:
        print(f"✗ 处理文章时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"输出目录: {OUTPUT_DIR}")
    
    driver = None
    try:
        # 尝试连接到已存在的浏览器
        try:
            driver = setup_driver()
            print("✓ 已连接到现有的Chrome浏览器实例")
        except Exception as e:
            print(f"无法连接到现有浏览器: {e}")
            print("启动新的浏览器实例...")
            driver = setup_driver_new()
            print("✓ 已启动新的Chrome浏览器实例")
            print("⚠️  请在新浏览器中登录后，按Enter键继续...")
            input()
        
        success_count = 0
        for i, url in enumerate(ARTICLES):
            if process_article(driver, url, i):
                success_count += 1
            time.sleep(2)  # 间隔一段时间
        
        print(f"\n{'='*60}")
        print(f"所有文章处理完成!")
        print(f"成功: {success_count}/{len(ARTICLES)}")
        print(f"失败: {len(ARTICLES) - success_count}/{len(ARTICLES)}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            input("\n按Enter键关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    main()
