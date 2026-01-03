import json
import pandas as pd

# 从网站获取的252个部门赛作品名称（从浏览器提取）
website_agents_raw = '''人工客服智能助手-SOP托管
家庭教育咨询助手
Dola：数据知识库AI助手
腾讯卫士举报智能助手
「审小包」广告审核智能小助手
TripGO(即刻出发)
电商大促AI小助手
CPS商品营销智能体
王者营地大模型助手
腾讯水滴法务 AI
腾讯反诈助手
易链灵构
修仙短视频自动成片器
悟空AI智能测试平台
私有化AI运维助手
灵鹅点睛——开局一张图
腾讯地图AI叮当旅行管家智能体
AiX Agent
用户之声
【微信蓝包】AI选礼物助手
好物圈·购物助手
小磐SREAgent
腾讯公益AI搜索bot
Lily金融助手&深度研究
DataBrain Agent
旅鹅HotelGPT
企业级智能合同平台
电销全流程增效Agent
微信小店·商家智能客服
无障碍公益智能体集群
AI智能专题
较真AI-智能查真假
视觉创作Agent
AI驱动Web_UI自动化测试
T-Audit 分析效能助理
CasePilot自动化测试
TencentOS智能诊断助手
更懂你的助手-轻量云AI助手
QQ浏览器信息流AI评论
提示词生成智能体
信用卡AI赋能用户运营服务项目
合规智能助手
ima-agent任务模式
微信游戏 - AI游戏战报
推理回廊
【和平精英】明星AI队友
电销AI大师
审计报告智能体
广告工程智能助理Cyber
微信支付AI开发助手
QQ浏览器小说AI-Agent
"AI"治未病-SQL事前风险
IC-Helper内控合规助手
小O数智员工经管AI提效好帮手
GooDee：AI设计工作台
小码快跑-设计转前端提效工具
广告转化链路识别智能体
iDOMO联盟广告智能模板助手
Anknow安知道智能分身平台
小A：AMS经营分析AI助手
内控盖亚AI-风险策略助手
TCase测试智能体
AI智能告警系统
社交线QData
云原生现场运维专家
灵析——财经智能告警助手
疑票否决：支付凭证疑点发现
Agent-RED测试小助手
CodeBuddy Code
智能表格AI字段
Vedas智能体
客诉智能分析平台
叮小灵-零售选址专家Agent
腾讯位置服务开发者分析专家
英雄联盟手游-智能化AI指导
AI4Test
腾讯云智能客服
财经智能客服(财经小智)
腾讯云安灯：智能统一工作台
QQ浏览器AI视频助理
AgentHub智能体路由服务
天御金融反电信网络诈骗智能体
TDesign AI Chat
自动化预测智能体
赛博科学家：一站式AI科研助手
轻量云游戏服智囊-游戏AI助手
和平精英绿洲开发AI助手
多尺寸扩图agent
内控盖亚AI-RCM生成助手
工单提效专家—工单分析AI助手
微信广告开发者AI服务助手
无极智能开发
企业微信私域服务AI助手
支付平台AI研发助手
DataPocket数据智能
商品自动化测评
QQ官方AI伙伴"小Q"
Lumos：全流程分析助手
叮小游-文旅客情专家Agent
ALADIN一站式AI测试实践
王者荣耀指挥官模式AI陪玩
设计稿转代码D2C
腾讯视频AIGC影视后期制作工
QQ安全Agent
方言语料自动采集系统
DB性能智能调优
CVM AI 助手
AMS Data Agent
网络报文智能分析
游戏人生运营配置助手
游戏多模态AI翻译及应用
鹰眼·AI智审
计算运营数据AI助手【已脱敏】
瓦力 - 下一代的编程伙伴
运产研贴心助手—轻量云AI助手
TencentOS内核漏洞修复
新闻妹AI-伴随式新闻智能助手
对象存储智能专家
小途智能问答
QQ浏览器下载助手
腾讯频道问问Agent
PUBGM WOW 智能助手
「腾讯探元」AI文博助手智能体
用户动线分析与需求洞察助手
OlaSQL-AI原生数据洞察
AI智能评测富文本还原效果
安兔AI助手：B端智能任务探索
OVB智能数据助手小π
SmartUI多模态UI自动化
大禹营销创意素材生成Agent
单测生成Agent
电商监管合规小助手
忍者企鹅AI
PlayStore Pilot
悟空代码安全Agent-体验版
AI辅助应用合规审核与质量巡检
Midas智能监控
赛博医院：你的专属AI医疗团队
游戏端外营销AI助手
云手机 AI Agent项目
大模型智能文案提升直播红点体验
AiSee日志分析小助手
Text2SQL智能取数
【和平精英】全场景AI小秘书
跨境汇款门店AI数字人
党建助手
新闻微服务助手Agent
AI 高考通
QQ浏览器订阅助理
可观测AI工作台
企业微信AI搜索
如影DS智能助手
AI 视频审核
审核智能体项目
星脉高性能网络智能化运营
LangData-ChatBI
拾光回忆录
CDN接入领域SRE智能体
Talos 全链路智能测试
03助手
DDoS攻防提效AI助手
混元AI播客Agent
黑产智能情报感知系统
大同AI埋点设计
AI内容评测
微信AB实验智能助手
营销活动生成助手
智享AI提效工具
无人值守AI智能助手
AI 全链路智能测试引擎
服采视频优选智能体
鹅厂党建小助手
外部代码生成
腾讯新闻AI CR智能平台
腾讯招聘AI-面试助手
AI PPT
AI驱动UI自动化测试
Bugly AI 问题分析
工蜂AI CR赋能微信支付提效
内容安全Agent
AI助力数据关联关系挖掘
智投广告投放 AIM+
研发全流程提效 Agent
云产品优化研究分析Agent
微信广告ai机器人zaker
自选股智能客服agent
混元微信公众号AI分身
影视素材智能剪辑agent
在线图文纠错
AI助力叙事生成管线提质增效
端云协同隐私保护智能体HaS
云镜台
体育大聪明一站式AI观赛助手
AI在验证码场景的图像对抗应用
营销AI虚拟员工
智能表格AI助手
PLAN小助手-查询GPU
服采智能运营小助手
大模型护照智能审核服务
TRTC云助手
Code Agent SDK
小途灵溯AI
COS迁移AI工作流
企微智能机器人-个人助理
腾讯文档智能表格 AI 应用
DeepTest AI后台测试
新人助手agent
TDebug Agent
鹅博士知识管家
智能抽奖助手
视频号自动生产CGI测试用例
智瞳-客户商机分析
GOG智能分析平台
Data Agent
供应商咨询应答机器人
腾讯云AI驱动测试生成平台
王者共创投稿AI审核
FiT_Helper提效助手
智能素材投放
视频号智能合集
用户问题智能定位
AI驱动风控智能研发
AI智能写信
运营小助手
智研全链路可观测 Agent
腾讯开悟平台使用答疑小助手
赛宝对局问题定位agent
智能顾问-AI赋能云上架构治理
视频号智能客服小助手
共富AI-乡村经营智能体
<美职篮全明星>智能问答助手
腾讯云主机安全智能溯源助手
多代码平台AI CR
PCAD数询助手
智能排版助手
QQ 成本专家
QBoost智能平台
研发预算智能问数
⛵️扬帆-出海合规助手
赛事邀请码agent
现网问题排查小助手
Unity快捷资产插件
Feedback Hawk
大模型自动化红队Agent
七彩石产品问答和诊断Agent
金融信贷态势洞察agent
青鸟系统-营销宣传合规审查工具
腾讯新闻商业化智能AI助手
模型一体化分析助手Aly
云知AI——智能售卖助手
DBA永不眠
AI值班巡检排障助手'''

# 解析网站作品名称
website_names = set([name.strip() for name in website_agents_raw.strip().split('\n') if name.strip()])
print(f"网站部门赛作品数: {len(website_names)}")

# 读取清单
df_list = pd.read_csv('dept_agent_list.csv')
list_names = set(df_list['agent名'].dropna().str.strip().tolist())
print(f"清单作品数: {len(list_names)}")

# 找出网站有但清单没有的作品（未包含在清单中的）
not_in_list = website_names - list_names
print(f"\n=== 网站有但清单未包含的作品 ({len(not_in_list)}个) ===")
for name in sorted(not_in_list):
    print(f"  - {name}")

# 找出清单有但网站没有的作品
not_in_website = list_names - website_names
print(f"\n=== 清单有但网站未显示的作品 ({len(not_in_website)}个) ===")
for name in sorted(list(not_in_website)[:20]):
    print(f"  - {name}")
if len(not_in_website) > 20:
    print(f"  ... 还有 {len(not_in_website) - 20} 个")

# 保存未包含在清单中的作品
not_in_list_df = pd.DataFrame({'agent名': list(not_in_list)})
not_in_list_df.to_csv('agents_not_in_list.csv', index=False, encoding='utf-8-sig')
print(f"\n已保存未包含在清单中的作品到 agents_not_in_list.csv")
