import csv

# 读取缺少信息的作品
with open('missing_info_agents.csv', encoding='utf-8-sig') as f:
    data = list(csv.DictReader(f))

# 分类统计
only_link = []
only_member = []
both = []

for d in data:
    field = d['缺少字段']
    if field == '体验链接':
        only_link.append(d)
    elif field == '项目成员':
        only_member.append(d)
    else:
        both.append(d)

print(f"仅缺体验链接: {len(only_link)}")
print(f"仅缺项目成员: {len(only_member)}")
print(f"同时缺两者: {len(both)}")

print("\n=== 同时缺体验链接和项目成员的作品 ===")
for d in both:
    print(f"| {d['id']} | {d['agent名']} |")
