#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫描网站作品并与清单对比，找出差异
"""

import pandas as pd
import re

# 网站上的337个部门赛作品
website_agents = [
    "人工客服智能助手-SOP托管", "家庭教育咨询助手", "Dola：数据知识库AI助手", "腾讯卫士举报智能助手",
    "「审小包」广告审核智能小助手", "TripGO(即刻出发)", "电商大促AI小助手", "CPS商品营销智能体",
    "王者营地大模型助手", "腾讯水滴法务 AI", "腾讯反诈助手", "​​易链灵构", "修仙短视频自动成片器",
    "悟空AI智能测试平台", "私有化AI运维助手", "灵鹅点睛——开局一张图", "腾讯地图AI叮当旅行管家智能体",
    "AiX Agent", "用户之声", "【微信蓝包】AI选礼物助手", "好物圈·购物助手", "小磐SREAgent",
    "腾讯公益AI搜索bot", "Lily金融助手&深度研究", "DataBrain Agent", "旅鹅HotelGPT",
    "企业级智能合同平台", "电销全流程增效Agent", "微信小店·商家智能客服", "无障碍公益智能体集群",
    "AI智能专题", "较真AI-智能查真假", "视觉创作Agent", "AI驱动Web_UI自动化测试",
    "T-Audit 分析效能助理", "CasePilot自动化测试", "TencentOS智能诊断助手", "更懂你的助手-轻量云AI助手",
    "QQ浏览器信息流AI评论", "提示词生成智能体", "信用卡AI赋能用户运营服务项目", "合规智能助手",
    "ima-agent任务模式", "微信游戏 - AI游戏战报", "推理回廊", "【和平精英】明星AI队友",
    "电销AI大师", "审计报告智能体", "广告工程智能助理Cyber", "微信支付AI开发助手",
    "QQ浏览器小说AI-Agent", "AI治未病-SQL事前风险", "IC-Helper内控合规助手",
    "小O数智员工经管AI提效好帮手", "GooDee：AI设计工作台", "小码快跑-设计转前端提效工具",
    "广告转化链路识别智能体", "iDOMO联盟广告智能模板助手", "Anknow安知道智能分身平台",
    "小A：AMS经营分析AI助手", "内控盖亚AI-风险策略助手", "TCase测试智能体", "AI智能告警系统",
    "社交线QData", "云原生现场运维专家", "灵析——财经智能告警助手", "疑票否决：支付凭证疑点发现",
    "Agent-RED测试小助手", "CodeBuddy Code", "智能表格AI字段", "Vedas智能体",
    "客诉智能分析平台", "叮小灵-零售选址专家Agent", "腾讯位置服务开发者分析专家",
    "英雄联盟手游-智能化AI指导", "AI4Test", "腾讯云智能客服", "财经智能客服(财经小智)",
    "腾讯云安灯：智能统一工作台", "QQ浏览器AI视频助理", "AgentHub智能体路由服务",
    "天御金融反电信网络诈骗智能体", "TDesign AI Chat", "自动化预测智能体",
    "赛博科学家：一站式AI科研助手", "轻量云游戏服智囊-游戏AI助手", "和平精英绿洲开发AI助手",
    "多尺寸扩图agent", "内控盖亚AI-RCM生成助手", "工单提效专家—工单分析AI助手",
    "微信广告开发者AI服务助手", "无极智能开发", "企业微信私域服务AI助手", "支付平台AI研发助手",
    "DataPocket数据智能", "商品自动化测评", "QQ官方AI伙伴小Q", "Lumos：全流程分析助手",
    "叮小游-文旅客情专家Agent", "ALADIN一站式AI测试实践", "王者荣耀指挥官模式AI陪玩",
    "设计稿转代码D2C", "腾讯视频AIGC影视后期制作工", "QQ安全Agent", "方言语料自动采集系统",
    "DB性能智能调优", "CVM AI 助手", "AMS Data Agent", "网络报文智能分析",
    "游戏人生运营配置助手", "游戏多模态AI翻译及应用", "鹰眼·AI智审", "计算运营数据AI助手【已脱敏】",
    "瓦力 - 下一代的编程伙伴", "运产研贴心助手—轻量云AI助手", "TencentOS内核漏洞修复",
    "新闻妹AI-伴随式新闻智能助手", "对象存储智能专家", "小途智能问答", "QQ浏览器下载助手",
    "腾讯频道问问Agent", "PUBGM WOW 智能助手", "「腾讯探元」AI文博助手智能体",
    "用户动线分析与需求洞察助手", "OlaSQL-AI原生数据洞察", "AI智能评测富文本还原效果",
    "安兔AI助手：B端智能任务探索", "OVB智能数据助手小π", "SmartUI多模态UI自动化",
    "大禹营销创意素材生成Agent", "单测生成Agent", "电商监管合规小助手", "忍者企鹅AI",
    "PlayStore Pilot", "悟空代码安全Agent-体验版", "AI辅助应用合规审核与质量巡检",
    "Midas智能监控", "赛博医院：你的专属AI医疗团队", "游戏端外营销AI助手", "云手机 AI Agent项目",
    "大模型智能文案提升直播红点体验", "AiSee日志分析小助手", "Text2SQL智能取数",
    "【和平精英】全场景AI小秘书", "跨境汇款门店AI数字人", "党建助手", "新闻微服务助手Agent",
    "AI 高考通", "QQ浏览器订阅助理", "可观测AI工作台", "企业微信AI搜索", "如影DS智能助手",
    "AI 视频审核", "审核智能体项目", "星脉高性能网络智能化运营", "LangData-ChatBI", "拾光回忆录",
    "CDN接入领域SRE智能体", "Talos 全链路智能测试", "03助手", "DDoS攻防提效AI助手",
    "混元AI播客Agent", "黑产智能情报感知系统", "大同AI埋点设计", "AI内容评测",
    "微信AB实验智能助手", "营销活动生成助手", "智享AI提效工具", "无人值守AI智能助手",
    "AI 全链路智能测试引擎​", "服采视频优选智能体", "鹅厂党建小助手", "外部代码生成",
    "腾讯新闻AI CR智能平台", "腾讯招聘AI-面试助手", "AI PPT", "AI驱动UI自动化测试",
    "Bugly AI 问题分析", "工蜂AI CR赋能微信支付提效", "内容安全Agent", "AI助力数据关联关系挖掘",
    "智投广告投放 AIM+", "研发全流程提效 Agent", "云产品优化研究分析Agent",
    "微信广告ai机器人zaker", "自选股智能客服agent", "混元微信公众号AI分身", "影视素材智能剪辑agent",
    "在线图文纠错", "AI助力叙事生成管线提质增效", "端云协同隐私保护智能体HaS", "云镜台",
    "体育大聪明一站式AI观赛助手", "AI在验证码场景的图像对抗应用", "营销AI虚拟员工", "智能表格AI助手",
    "PLAN小助手-查询GPU", "服采智能运营小助手", "大模型护照智能审核服务", "TRTC云助手",
    "Code Agent SDK", "小途灵溯AI", "COS迁移AI工作流", "企微智能机器人-个人助理",
    "腾讯文档智能表格 AI 应用", "DeepTest AI后台测试", "新人助手agent", "TDebug Agent",
    "鹅博士知识管家", "智能抽奖助手", "视频号自动生产CGI测试用例", "智瞳-客户商机分析",
    "GOG智能分析平台", "Data Agent", "供应商咨询应答机器人", "腾讯云AI驱动测试生成平台",
    "王者共创投稿AI审核", "FiT_Helper提效助手", "智能素材投放", "视频号智能合集",
    "用户问题智能定位", "AI驱动风控智能研发", "AI智能写信", "运营小助手",
    "智研全链路可观测 Agent", "腾讯开悟平台使用答疑小助手", "赛宝对局问题定位agent",
    "智能顾问-AI赋能云上架构治理", "视频号智能客服小助手", "共富AI-乡村经营智能体",
    "<美职篮全明星>智能问答助手", "腾讯云主机安全智能溯源助手", "多代码平台AI CR",
    "PCAD数询助手", "智能排版助手", "QQ 成本专家", "QBoost智能平台", "研发预算智能问数",
    "⛵️扬帆-出海合规助手", "赛事邀请码agent", "现网问题排查小助手", "Unity快捷资产插件",
    "Feedback Hawk", "大模型自动化红队Agent", "七彩石产品问答和诊断Agent",
    "金融信贷态势洞察agent", "青鸟系统-营销宣传合规审查工具", "腾讯新闻商业化智能AI助手",
    "模型一体化分析助手Aly", "云知AI——智能售卖助手", "DBA永不眠", "AI值班巡检排障助手",
    "新闻智慧运营Agent", "草场地智能客服agent", "PCopilot:代码评审助手", "代码覆盖率智能体",
    "Launch Canvas", "【视频号直播】直播高光系统", "文档抽取Agent", "数据库助手Agent",
    "门店通—门店营销AI助手", "公益项目进展分析报告生成智能体", "OCNET智能运营助手",
    "理财通编码与测试提效Agent", "智能表 AI 高效响应用户反馈", "阿瓦隆多Agent游戏",
    "公域垂媒分析助手", "工蜂AI CR赋能元梦之星提效", "免广告券Helper", "大模型安全自动评估 Agent",
    "智能AI营销图生成", "安全攻击智能分析助手", "小店广告客户增长Agent", "广告推荐特征发现助手",
    "webAssistant", "AI数智化实施顾问", "微信支付境外商户海报Agent", "设计稿转界面代码的Agent",
    "代码异常定位助手", "With", "TAB-AI实验助手", "微信输入法表情包创作agent",
    "需求到测试代码一站式生成", "千万级3D资产库AI搜索方案", "X5灵析助手", "EPlus智能助手",
    "网络建设智能助手", "开悟D2C Figma插件", "腾讯公益数据需求智能助手", "广告人群挖掘助手",
    "GhostUnit", "taihu-tgit", "视频号文案红点爆款审核提效", "多模态AI驱动UI自动化测试",
    "腾讯新闻用户反馈智能诊断助手", "InfraSec基础安全运营", "技术风险大脑Agent",
    "tRPC项目级AI代码生成", "Midas商城内容生成助手", "游戏版号助手", "EGA智能起量系统",
    "腾讯文档AI救命文档智能体", "高价值弹幕AI挖掘助手", "用户体验一致性智能助手",
    "元梦活动助手", "A/Brain-广告实验大模型", "AI智能化运营", "AI辅助测试用例生成",
    "广告落地页违规巡查Agent", "C++转Java批跑AI自动化", "TCE云API AI助手", "moredb-pgsql",
    "开悟前端代码生成助手", "混元AI x 腾讯视频IP分身", "企微文档用户反馈自动定位",
    "智能检查服务-你的资产治理助手", "DLC UDF迁移助手", "MRR专家访谈AI助手-小玄",
    "ppt-agent 自动生成", "AI 埋点自动化测试", "POI生产智能体", "FiT 云平台AI助手",
    "跨境商户智能助手", "数据中心事件AI转单及诊断", "活动运营风险检测", "跨境汇款研发智能助手",
    "企业微信智能服务总结", "腾讯公益研发助手", "生产风险AI定位助手", "midas经营分析问答助手",
    "美观度评测助手", "公益项目AI评审", "资金中台运营小助手-证账实智能", "TXSQL智能诊断Agent",
    "跨境业务研发智能运维", "起名专家", "IT运维智能服务台"
]

def normalize_name(name):
    """标准化名称用于比较"""
    if pd.isna(name):
        return ""
    name = str(name).strip()
    # 移除特殊字符和空格
    name = re.sub(r'[\s\u200b\u200c\u200d\ufeff]+', '', name)
    # 转小写
    name = name.lower()
    # 移除常见前后缀
    name = re.sub(r'[：:—\-_·]', '', name)
    return name

# 读取清单
df_list = pd.read_csv('dept_agent_list.csv')
list_names = df_list['agent名'].tolist()

# 读取之前找到的未在清单中的作品
df_not_in_list = pd.read_csv('agents_not_in_list.csv')
not_in_list_names = df_not_in_list['agent名'].tolist()

# 标准化所有名称
website_normalized = {normalize_name(n): n for n in website_agents}
list_normalized = {normalize_name(n): n for n in list_names if pd.notna(n)}
not_in_list_normalized = {normalize_name(n): n for n in not_in_list_names if pd.notna(n)}

print("=" * 60)
print("部门赛作品对比分析")
print("=" * 60)
print(f"\n网站部门赛作品总数: {len(website_agents)}")
print(f"清单作品总数: {len(list_names)}")
print(f"之前发现未在清单中的作品数: {len(not_in_list_names)}")

# 找出网站有但清单没有的作品
website_only = []
for norm_name, orig_name in website_normalized.items():
    if norm_name not in list_normalized:
        website_only.append(orig_name)

print(f"\n网站有但清单没有的作品数: {len(website_only)}")

# 找出新发现的（不在之前的not_in_list中）
new_found = []
for name in website_only:
    norm = normalize_name(name)
    if norm not in not_in_list_normalized:
        new_found.append(name)

print(f"新发现的作品数（之前未记录）: {len(new_found)}")

if new_found:
    print("\n新发现的作品列表:")
    for i, name in enumerate(new_found, 1):
        print(f"  {i}. {name}")

# 找出清单有但网站没有的作品
list_only = []
for norm_name, orig_name in list_normalized.items():
    if norm_name not in website_normalized:
        list_only.append(orig_name)

print(f"\n清单有但网站没有的作品数: {len(list_only)}")
if list_only[:10]:
    print("部分示例:")
    for name in list_only[:10]:
        print(f"  - {name}")

# 检查清单中缺少信息的作品
print("\n" + "=" * 60)
print("清单中缺少信息的作品检查")
print("=" * 60)

missing_info = []
for idx, row in df_list.iterrows():
    agent_name = row['agent名']
    missing_fields = []
    
    if pd.isna(row['体验链接']) or str(row['体验链接']).strip() == '':
        missing_fields.append('体验链接')
    if pd.isna(row['主导部门']) or str(row['主导部门']).strip() == '':
        missing_fields.append('主导部门')
    if pd.isna(row['项目经理']) or str(row['项目经理']).strip() == '':
        missing_fields.append('项目经理')
    if pd.isna(row['项目成员']) or str(row['项目成员']).strip() == '':
        missing_fields.append('项目成员')
    
    if missing_fields:
        missing_info.append({
            'id': row['id'],
            'agent名': agent_name,
            '缺少字段': ', '.join(missing_fields)
        })

print(f"\n清单中缺少信息的作品数: {len(missing_info)}")

# 按缺少字段分类统计
from collections import Counter
field_counter = Counter()
for item in missing_info:
    for field in item['缺少字段'].split(', '):
        field_counter[field] += 1

print("\n缺少字段统计:")
for field, count in field_counter.most_common():
    print(f"  - {field}: {count}个作品")

# 保存新发现的作品
if new_found:
    with open('new_found_agents.txt', 'w', encoding='utf-8') as f:
        f.write("新发现的部门赛作品（之前未记录）\n")
        f.write("=" * 40 + "\n")
        for name in new_found:
            f.write(f"{name}\n")
    print(f"\n新发现的作品已保存到 new_found_agents.txt")

# 保存所有网站有但清单没有的作品（更新版）
with open('website_only_agents_updated.txt', 'w', encoding='utf-8') as f:
    f.write(f"网站有但清单没有的作品（共{len(website_only)}个）\n")
    f.write("=" * 40 + "\n")
    for name in website_only:
        f.write(f"{name}\n")
print(f"网站独有作品列表已保存到 website_only_agents_updated.txt")

# 保存缺少信息的作品
df_missing = pd.DataFrame(missing_info)
df_missing.to_csv('missing_info_agents.csv', index=False, encoding='utf-8-sig')
print(f"缺少信息的作品已保存到 missing_info_agents.csv")

print("\n" + "=" * 60)
print("分析完成")
print("=" * 60)
