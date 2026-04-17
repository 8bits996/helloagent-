import zipfile
z = zipfile.ZipFile(r'd:\AI\26年规划\harness\控制论.docx')
z.extractall(r'c:\Users\frankechen\CodeBuddy\chrome\control_theory_unpacked')
print("Done")
