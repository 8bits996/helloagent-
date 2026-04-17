"""
下载KM文章图片
"""
import os
import requests

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(WORK_DIR, 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

IMAGE_URLS = [
    'https://km.woa.com/asset/00010002251200f63a486c1c4843b902?height=1120&width=1658&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200ba522e54f45642d402?height=1350&width=1040&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/0001000225120097ffb87952ff46c602?height=688&width=1180&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200ab0d49a2271e4ebc02?height=953&width=1170&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200a505422be550439d02?height=440&width=1183&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200414c928523de45db02?height=1410&width=1200&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200b65abd960591448a02?height=630&width=1190&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200de697fc7fa6b4c7d02?height=1280&width=3395&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
    'https://km.woa.com/asset/00010002251200a1438deb9654432d02?height=248&width=1005&imageMogr2/thumbnail/1540x%3E/ignore-error/1',
]

COOKIE = "storm_km_id=frankechen; t_uid=frankechen; km_uid=frankechen; _DiggerUserClientId=3594481907; km_nick=frankechen; is_feed_gray=0; enable_isearch_chat=0; KMSID=ci694a576qbpcfg7oqedvq8c75"

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://km.woa.com/',
        'Cookie': COOKIE
    })
    
    for i, url in enumerate(IMAGE_URLS):
        try:
            print(f"下载图片 {i+1}/{len(IMAGE_URLS)}...")
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            
            img_path = os.path.join(IMAGES_DIR, f'image_{i+1}.png')
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            print(f"  已保存: {img_path} ({len(resp.content)} bytes)")
        except Exception as e:
            print(f"  下载失败: {e}")
    
    print("\n完成!")

if __name__ == '__main__':
    main()
