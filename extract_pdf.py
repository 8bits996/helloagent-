import pdfplumber
import os

pdf_path = r'd:\AI\教育\论文\液冷泵机脚振动试验.pdf'

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

pdf = pdfplumber.open(pdf_path)
print(f"Total pages: {len(pdf.pages)}")

for i, page in enumerate(pdf.pages):
    print(f"\n{'='*60}")
    print(f"=== Page {i+1} ===")
    print(f"{'='*60}")
    text = page.extract_text()
    if text:
        print(text)
    else:
        print("[No text on this page - may contain images]")
    
    # Extract tables
    tables = page.extract_tables()
    if tables:
        for j, table in enumerate(tables):
            print(f"\n--- Table {j+1} on Page {i+1} ---")
            for row in table:
                print(row)

pdf.close()
