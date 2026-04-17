import pdfplumber
import os
from PIL import Image
import io

pdf_path = r'd:\AI\教育\论文\液冷泵机脚振动试验.pdf'
output_dir = r'c:\Users\frankechen\CodeBuddy\chrome\liquid-pump-vibration-paper\images\report'
os.makedirs(output_dir, exist_ok=True)

pdf = pdfplumber.open(pdf_path)
img_count = 0

for i, page in enumerate(pdf.pages):
    # Convert page to image for visual reference
    img = page.to_image(resolution=200)
    img_path = os.path.join(output_dir, f'page_{i+1}.png')
    img.save(img_path)
    img_count += 1
    print(f"Saved page {i+1} as image: {img_path}")

pdf.close()
print(f"\nTotal images saved: {img_count}")

# Also extract embedded images using pypdf
from pypdf import PdfReader

reader = PdfReader(pdf_path)
embed_dir = os.path.join(output_dir, 'embedded')
os.makedirs(embed_dir, exist_ok=True)

embed_count = 0
for i, page in enumerate(reader.pages):
    if '/XObject' in page['/Resources']:
        xObject = page['/Resources']['/XObject'].get_object()
        for obj_name in xObject:
            obj = xObject[obj_name].get_object()
            if obj['/Subtype'] == '/Image':
                try:
                    width = obj['/Width']
                    height = obj['/Height']
                    # Only save meaningful images (not tiny decorations)
                    if width > 100 and height > 100:
                        data = obj.get_data()
                        if obj.get('/Filter') == '/DCTDecode':
                            ext = 'jpg'
                        elif obj.get('/Filter') == '/FlateDecode':
                            ext = 'png'
                        else:
                            ext = 'png'
                        
                        img_path = os.path.join(embed_dir, f'page{i+1}_{obj_name[1:]}_{width}x{height}.{ext}')
                        with open(img_path, 'wb') as f:
                            f.write(data)
                        embed_count += 1
                        print(f"Extracted embedded image: {img_path} ({width}x{height})")
                except Exception as e:
                    print(f"Error extracting image from page {i+1}: {e}")

print(f"\nTotal embedded images: {embed_count}")
