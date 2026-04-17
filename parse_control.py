import xml.etree.ElementTree as ET
import re

# 读取 XML
with open(r'c:\Users\frankechen\CodeBuddy\chrome\control_theory_unpacked\word\document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义命名空间
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# 解析 XML
root = ET.fromstring(content)

# 提取所有文本
texts = []
for elem in root.iter():
    if elem.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t':
        if elem.text:
            texts.append(elem.text)
    elif elem.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p':
        texts.append('\n')

# 合并文本
full_text = ''.join(texts)

# 清理多余空行
full_text = re.sub(r'\n{3,}', '\n\n', full_text)

# 保存
with open(r'c:\Users\frankechen\CodeBuddy\chrome\control_theory_content.md', 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters")
