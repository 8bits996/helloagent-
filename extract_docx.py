import zipfile
import os

docx_path = r'd:\AI\26年规划\harness\从零实践Harness Engineering：找bug修bug，全让AI自己来.docx'
output_dir = r'c:\Users\frankechen\CodeBuddy\chrome\harness_doc_unpacked'

with zipfile.ZipFile(docx_path, 'r') as z:
    z.extractall(output_dir)

print(f"Extracted to {output_dir}")
