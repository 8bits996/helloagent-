#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移验证脚本
验证为知笔记到 Obsidian 的迁移结果
"""

import os
import re
import sqlite3
from pathlib import Path
import json
from datetime import datetime


class MigrationValidator:
    """迁移结果验证器"""
    
    def __init__(self, wiz_data_path, obsidian_vault):
        self.wiz_data_path = Path(wiz_data_path)
        self.obsidian_vault = Path(obsidian_vault)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
    
    def check_database_integrity(self):
        """检查数据库完整性"""
        print("\n[1/6] 检查数据库完整性...")
        
        db_path = self.wiz_data_path / 'index.db'
        if not db_path.exists():
            print("  ✗ 数据库文件不存在")
            self.results['checks']['database'] = {'status': 'failed', 'reason': '文件不存在'}
            return False
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == 'ok':
                print("  ✓ 数据库完整")
                self.results['checks']['database'] = {'status': 'ok'}
                return True
            else:
                print(f"  ✗ 数据库损坏：{result}")
                self.results['checks']['database'] = {'status': 'failed', 'reason': result}
                return False
        except Exception as e:
            print(f"  ✗ 检查失败：{e}")
            self.results['checks']['database'] = {'status': 'failed', 'reason': str(e)}
            return False
    
    def count_source_notes(self):
        """统计源笔记数量"""
        print("\n[2/6] 统计源笔记数量...")
        
        db_path = self.wiz_data_path / 'index.db'
        conn = sqlite3.connect(str(db_path))
        
        # 总笔记数
        cursor = conn.execute("SELECT COUNT(*) FROM WIZ_DOCUMENT WHERE DOCUMENT_TYPE != 'encrypted'")
        total = cursor.fetchone()[0]
        
        # 按文件夹统计
        cursor = conn.execute("""
            SELECT 
                DOCUMENT_LOCATION,
                COUNT(*) as count
            FROM WIZ_DOCUMENT
            WHERE DOCUMENT_TYPE != 'encrypted'
            GROUP BY DOCUMENT_LOCATION
            ORDER BY count DESC
            LIMIT 10
        """)
        folders = cursor.fetchall()
        
        conn.close()
        
        print(f"  总笔记数：{total}")
        print(f"  文件夹数：{len(folders)}")
        
        self.results['checks']['source_notes'] = {
            'status': 'ok',
            'total': total,
            'top_folders': [{'path': f[0], 'count': f[1]} for f in folders]
        }
        
        return total
    
    def count_migrated_notes(self):
        """统计迁移后的笔记数量"""
        print("\n[3/6] 统计迁移笔记数量...")
        
        md_files = list(self.obsidian_vault.rglob('*.md'))
        total = len(md_files)
        
        # 按文件夹统计
        folder_counts = {}
        for md_file in md_files:
            rel_path = md_file.relative_to(self.obsidian_vault)
            folder = str(rel_path.parent)
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
        
        # 排序
        sorted_folders = sorted(folder_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"  总笔记数：{total}")
        print(f"  文件夹数：{len(folder_counts)}")
        
        self.results['checks']['migrated_notes'] = {
            'status': 'ok',
            'total': total,
            'top_folders': [{'path': f[0], 'count': f[1]} for f in sorted_folders]
        }
        
        return total
    
    def check_images(self):
        """检查图片资源"""
        print("\n[4/6] 检查图片资源...")
        
        assets_path = self.obsidian_vault / 'assets'
        if not assets_path.exists():
            print("  ✗ assets 目录不存在")
            self.results['checks']['images'] = {'status': 'warning', 'reason': 'assets 目录不存在'}
            return 0
        
        # 统计图片数量
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
        image_files = [f for f in assets_path.rglob('*') if f.suffix.lower() in image_extensions]
        
        print(f"  图片数量：{len(image_files)}")
        
        # 检查大图片
        large_images = []
        for img in image_files:
            size = img.stat().st_size
            if size > 5 * 1024 * 1024:  # 5MB
                large_images.append({
                    'file': str(img.relative_to(self.obsidian_vault)),
                    'size': f"{size / 1024 / 1024:.2f} MB"
                })
        
        if large_images:
            print(f"  ⚠ 发现 {len(large_images)} 个大图片（>5MB）")
        
        self.results['checks']['images'] = {
            'status': 'ok',
            'total': len(image_files),
            'large_images': large_images[:5]  # 只记录前5个
        }
        
        return len(image_files)
    
    def check_broken_links(self):
        """检查损坏的链接"""
        print("\n[5/6] 检查损坏的链接...")
        
        md_files = list(self.obsidian_vault.rglob('*.md'))
        broken_links = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # 检查图片链接
                image_links = re.findall(r'!\[.*?\]\((.*?)\)', content)
                
                for link in image_links:
                    # 跳过网络图片
                    if link.startswith('http'):
                        continue
                    
                    # 构建完整路径
                    full_path = self.obsidian_vault / link
                    
                    if not full_path.exists():
                        broken_links.append({
                            'file': str(md_file.relative_to(self.obsidian_vault)),
                            'broken_link': link
                        })
            except Exception as e:
                print(f"  ✗ 检查文件失败 {md_file.name}: {e}")
        
        if broken_links:
            print(f"  ✗ 发现 {len(broken_links)} 个损坏的链接")
        else:
            print("  ✓ 所有链接正常")
        
        self.results['checks']['broken_links'] = {
            'status': 'ok' if not broken_links else 'warning',
            'total': len(broken_links),
            'links': broken_links[:10]  # 只记录前10个
        }
        
        return broken_links
    
    def check_yaml_headers(self):
        """检查 YAML 头部"""
        print("\n[6/6] 检查 YAML 头部...")
        
        md_files = list(self.obsidian_vault.rglob('*.md'))
        missing_headers = []
        missing_tags = 0
        missing_dates = 0
        
        for md_file in md_files[:100]:  # 只检查前100个文件
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # 检查是否有 YAML 头部
                if not content.startswith('---'):
                    missing_headers.append(str(md_file.relative_to(self.obsidian_vault)))
                    continue
                
                # 检查必需字段
                if 'tags:' not in content[:500]:
                    missing_tags += 1
                
                if 'date:' not in content[:500]:
                    missing_dates += 1
                    
            except Exception as e:
                pass
        
        if missing_headers:
            print(f"  ⚠ {len(missing_headers)} 个文件缺少 YAML 头部")
        
        print(f"  缺少标签的文件：{missing_tags}")
        print(f"  缺少日期的文件：{missing_dates}")
        
        self.results['checks']['yaml_headers'] = {
            'status': 'ok',
            'missing_headers': len(missing_headers),
            'missing_tags': missing_tags,
            'missing_dates': missing_dates
        }
        
        return len(missing_headers)
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("验证报告")
        print("="*60)
        
        source_total = self.results['checks'].get('source_notes', {}).get('total', 0)
        migrated_total = self.results['checks'].get('migrated_notes', {}).get('total', 0)
        
        if source_total > 0:
            migration_rate = (migrated_total / source_total * 100)
            print(f"\n迁移率：{migration_rate:.2f}%")
            print(f"源笔记：{source_total}")
            print(f"迁移笔记：{migrated_total}")
        
        broken_links = self.results['checks'].get('broken_links', {}).get('total', 0)
        if broken_links > 0:
            print(f"\n⚠ 损坏的链接：{broken_links}")
        
        # 保存 JSON 报告
        report_file = self.obsidian_vault / 'migration_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到：{report_file}")
        print("="*60)
        
        return self.results
    
    def validate(self):
        """执行完整验证"""
        print("开始验证迁移结果...")
        
        self.check_database_integrity()
        self.count_source_notes()
        self.count_migrated_notes()
        self.check_images()
        self.check_broken_links()
        self.check_yaml_headers()
        
        return self.generate_report()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='验证为知笔记到 Obsidian 的迁移结果')
    parser.add_argument('--wiz', required=True, help='为知笔记数据目录')
    parser.add_argument('--obsidian', required=True, help='Obsidian 仓库目录')
    
    args = parser.parse_args()
    
    validator = MigrationValidator(args.wiz, args.obsidian)
    validator.validate()


if __name__ == '__main__':
    main()
