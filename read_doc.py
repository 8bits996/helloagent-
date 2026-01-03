import win32com.client
import os

doc_path = r'c:\Users\frankechen\Downloads\利用codebuddy+skills+chrome-devtool-mcp实现AI自动测试UI.doc'
output_path = r'c:\Users\frankechen\CodeBuddy\chrome\doc_content.txt'

# 使用 Word COM 对象读取 doc 文件
word = win32com.client.Dispatch("Word.Application")
word.Visible = False

try:
    doc = word.Documents.Open(doc_path)
    text = doc.Content.Text
    doc.Close(False)
    
    # 保存到文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Content saved to {output_path}")
    print(f"Total length: {len(text)} characters")
finally:
    word.Quit()
