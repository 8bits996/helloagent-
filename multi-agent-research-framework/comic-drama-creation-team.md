# 🎬 漫剧生成多 Agent 团队（Comic Drama Creation Multi-Agent Team）

> **从一个主题创意，到一部高质量漫剧** —— 28 个专业化智能体 + 4 个贯穿型 Agent，6 个阶段全流程覆盖。
> 默认采用 **最经济方案**（CodeBuddy内置国产模型 + CosyVoice 2 + image_gen = **¥0/部**）
> 可选 **腾讯云全栈方案**（混元生图 + 腾讯TTS = ~¥4.6/部）或 **SD+InstantID本地方案**（人像克隆 = ¥0/部）

---

## 📑 目录

- [一、概述与设计理念](#一概述与设计理念)
- [二、完整架构全景图](#二完整架构全景图)
- [三、管控层：PM + Orchestrator](#三管控层pm--orchestrator)
- [四、Phase 0：主题策划与世界观](#四phase-0主题策划与世界观)
- [五、Phase 1：剧本创作](#五phase-1剧本创作)
- [六、Phase 2：视觉设定](#六phase-2视觉设定)
- [七、Phase 3：画面生成](#七phase-3画面生成)
- [八、Phase 4：排版合成](#八phase-4排版合成)
- [九、Phase 5：审校与发布](#九phase-5审校与发布)
- [十、贯穿型智能体](#十贯穿型智能体)
- [十一、腾讯云全栈配置方案](#十一腾讯云全栈配置方案)
- [十二、漫剧类型适配矩阵](#十二漫剧类型适配矩阵)
- [十三、质量门控与评分体系](#十三质量门控与评分体系)
- [十四、核心 Agent Prompt 模板](#十四核心-agent-prompt-模板)
- [十五、Agent 间协作协议](#十五agent-间协作协议)
- [十六、角色一致性引擎](#十六角色一致性引擎)
- [十七、平台适配规范](#十七平台适配规范)
- [十八、漫剧创作状态机](#十八漫剧创作状态机)
- [十九、用户配置清单与默认值](#十九用户配置清单与默认值)

---

## 一、概述与设计理念

### 1.1 什么是"漫剧"

**漫剧**（Comic Drama）= 漫画叙事 + 戏剧性故事结构，是一种以**多格漫画**为载体、通过**角色对白、分镜构图、视觉叙事**讲述完整故事的内容形式。

常见形态：
- **条漫**：微信公众号/小红书/Webtoon 竖屏长条漫画
- **格漫**：传统日漫/美漫式分页多格
- **动态漫**：带简单动效+配音的视频化漫画（短视频平台）
- **互动漫**：带选择支的互动式漫画（小程序/H5）

### 1.2 核心技术挑战

| 挑战 | 描述 | 解决方案 |
|------|------|---------|
| **角色一致性** | 同一角色在不同分镜中外观必须一致 | C3 CharacterConsistencyAgent + Prompt 锚点技术 |
| **分镜叙事** | 镜头语言、构图、阅读节奏控制 | A7 StoryboardAgent + A14 CompositionAgent |
| **对白自然** | 角色性格化对白，控制文字量 | A6 DialogueAgent（性格向量化） |
| **画面质量** | AI 生成画面的质量和稳定性 | 混元生图 3.0 + A18 RetouchAgent 精修 |
| **风格统一** | 全篇画风/色彩/线条一致 | A11 StyleGuideAgent + C1 StyleConsistencyAgent |
| **排版专业** | 气泡/音效/分格排版的专业度 | A19-A23 排版合成流水线 |

### 1.3 设计原则

```
┌───────────────────────────────────────────────────────────────┐
│  🎬 漫剧生成团队 8 大设计原则                                     │
├───────────────────────────────────────────────────────────────┤
│  1. 角色锚定  — 角色视觉特征向量化，跨帧严格一致                   │
│  2. 叙事驱动  — 故事结构优先，画面服务于叙事                       │
│  3. 分镜专业  — 镜头语言/构图/节奏遵循漫画创作专业规范              │
│  4. 风格锁定  — 全篇风格统一，单一画风贯穿始终                     │
│  5. 平台适配  — 根据发布平台自动适配尺寸/格式/阅读习惯              │
│  6. 迭代精进  — 支持局部重生/修改/风格微调                         │
│  7. 云原生    — 基于腾讯云全栈API，开箱即用                       │
│  8. 质量门控  — 6道Gate确保每个环节质量可控                       │
└───────────────────────────────────────────────────────────────┘
```

---

## 二、完整架构全景图

### 2.1 Agent 统计

| 层级 | 数量 | 角色 |
|-----|------|------|
| 管控层 | 2 | PM + Orchestrator |
| Phase 0 策划 | 4 | 主题+世界观+受众+风格参考 |
| Phase 1 剧本 | 5 | 故事+角色+对白+分镜+节奏 |
| Phase 2 视觉 | 5 | 角色设计+场景+风格规范+道具+表情库 |
| Phase 3 画面 | 5 | 构图+Prompt工程+生成+一致性+精修 |
| Phase 4 排版 | 5 | 布局+气泡+音效文字+转场+合成 |
| Phase 5 发布 | 4 | 审查+可读性+导出+发布 |
| 贯穿型 | 4 | 风格一致+叙事连贯+角色一致+记忆 |
| **总计** | **34** | |

### 2.2 架构全景图

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                       🎯 PM Agent（漫剧总监 / 主编）                        ║
║           主题审定 │ 风格基调 │ 目标受众 │ 阶段审查 │ 终审发布               ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                │
                                ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                     🔄 Orchestrator（漫剧制片人）                          ║
║        创作计划管理 │ Agent 调度 │ 资源分配 │ 进度管控 │ 冲突仲裁             ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                │
  ┌──────────────┬──────────────┼──────────────┬──────────────┐
  │              │              │              │              │
  ▼              ▼              ▼              ▼              ▼
╔══════════╗ ╔══════════╗ ╔══════════╗ ╔══════════╗ ╔══════════╗
║ Phase 0   ║ ║ Phase 1   ║ ║ Phase 2   ║ ║ Phase 3   ║ ║ Phase 4   ║
║ 🎯主题策划 ║ ║ 📝剧本创作 ║ ║ 🎨视觉设定 ║ ║ 🖼️画面生成 ║ ║ 📐排版合成 ║
║          ║ ║          ║ ║          ║ ║          ║ ║          ║
║ A0 Theme ║ ║ A4 Plot  ║ ║ A9  Char ║ ║ A14 Comp ║ ║ A19 Layt ║
║ A1 World ║ ║ A5 Chara ║ ║ A10 Scen ║ ║ A15 Prmt ║ ║ A20 Bubl ║
║ A2 Audie ║ ║ A6 Dialo ║ ║ A11 Styl ║ ║ A16 ImgG ║ ║ A21 SFX  ║
║ A3 Refer ║ ║ A7 Story ║ ║ A12 Prop ║ ║ A17 Cons ║ ║ A22 Tran ║
║          ║ ║ A8 Pace  ║ ║ A13 Expr ║ ║ A18 Retc ║ ║ A23 Assm ║
╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝ ╚════╤═════╝
 🚪G0│        🚪G1│        🚪G2│        🚪G3│        🚪G4│
     └────────────┴────────────┴────────────┴────────────┘
                                │
                                ▼
                     ╔════════════════════╗
                     ║ Phase 5             ║
                     ║ ✅ 审校与发布         ║
                     ║                    ║
                     ║ A24 QualityReview  ║
                     ║ A25 Accessibility  ║
                     ║ A26 FormatExport   ║
                     ║ A27 Publish        ║
                     ╚═════════╤══════════╝
                               │ 🚪G5
                               ▼
                     ╔══════════════════╗
                     ║  📄 漫剧成品        ║
                     ║  长条漫 / 分页版    ║
                     ║  动态视频(可选)     ║
                     ║  多平台格式        ║
                     ╚══════════════════╝

  ═══════════════  贯穿型智能体（Cross-Phase）  ═══════════════

  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
  │ 🎨 C1 StyleCons   │ │ 📖 C2 Narrative  │ │ 👤 C3 CharCons   │ │ 🧠 C4 Memory     │
  │ 风格一致性守护者    │ │ 叙事连贯性守护者  │ │ 角色一致性引擎    │ │ 创作过程记忆      │
  │ 画风/色彩/线条统一 │ │ 逻辑/伏笔/情感弧 │ │ 外观/表情/姿态   │ │ 决策/版本/参数   │
  └──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘

  ═══════════════  基础设施层（多方案可选）  ═══════════════

  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ 🤖 LLM       │ │ 🖼️ AI生图     │ │ 🗣️ TTS语音    │ │ 💾 存储       │
  │ CB内置国产   │ │ A:CB内置     │ │ CosyVoice2   │ │ A/B:本地     │
  │ 模型（免费） │ │ B:SD+InstID  │ │ (免费+克隆)  │ │ C:腾讯COS   │
  │ DS/Kimi/MM/  │ │ C:混元生图   │ │ 或腾讯TTS    │ │              │
  │ HY/GLM       │ │              │ │              │ │              │
  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 三、管控层：PM + Orchestrator

### PM Agent（漫剧总监/主编）

```yaml
角色: 漫剧总监 / 主编
核心职责:
  - 审定主题方向、目标受众、内容基调
  - 确定画风基调和质量标准
  - 关键阶段审查（Gate 0/1/2/4/5）
  - 终审漫剧成品，决定是否发布
  - 处理升级的创作分歧
行为模式: 读者视角审视 + 市场直觉判断 + 质量底线守护
```

### Orchestrator Agent（漫剧制片人）

```yaml
角色: 漫剧制片人
核心职责:
  - 将主题拆解为可执行的创作计划
  - 调度各 Phase 的 Agent 执行顺序
  - 管理 API 调用资源（特别是混元生图的并发限制）
  - 处理创作中的方向分歧和风格冲突
调度策略:
  Phase 0: A0→A1∥A2→A3              # A1/A2可并行
  Phase 1: A4→A5→A6∥A8→A7           # 对白/节奏可并行，分镜依赖两者
  Phase 2: A11→A9∥A10∥A12→A13       # 先定风格，再并行设计各元素
  Phase 3: A14→A15→A16→A17→(A18)    # 严格串行（生成→检查→修复）
  Phase 4: A19→A20∥A21→A22→A23      # 气泡/音效可并行
  Phase 5: A24→A25→A26→A27          # 串行审查
```

---

## 四、Phase 0：主题策划与世界观

> **目标**：将用户的主题创意转化为完整的创作方案和世界观设定。

| Agent | 角色 | 核心职责 | 输出 |
|-------|------|---------|------|
| **A0 ThemeAgent** | 主题策划师 | 解读用户主题意图，确定故事类型（搞笑/科普/悬疑/热血/治愈/讽刺），定义核心主题和情感基调 | 主题策划书（类型+基调+核心冲突+目标情感） |
| **A1 WorldBuildAgent** | 世界观构建师 | 构建故事世界观（时代背景、空间设定、核心规则、文化元素），确保世界内逻辑自洽 | 世界观设定文档 |
| **A2 AudienceAgent** | 受众分析师 | 分析目标受众特征和发布平台规范（微信/抖音/小红书/B站），优化叙事策略和呈现方式 | 受众画像+平台规范+叙事策略建议 |
| **A3 ReferenceAgent** | 风格参考师 | 搜集同类优秀作品，提炼风格参考板（Moodboard），确定画风方向和视觉基调 | 风格参考板（色彩+线条+构图+氛围参考） |

### 故事类型决策树

```
用户主题 → 分析核心诉求
    │
    ├─ 传递知识/概念 → 📚 科普型（幽默解说+拟人化+信息图式分镜）
    ├─ 引发共鸣/感动 → 💝 治愈型（暖色调+日常叙事+情感递进）
    ├─ 制造笑点/娱乐 → 😂 搞笑型（夸张表情+反转+网络梗+短节奏）
    ├─ 悬念/烧脑 → 🔍 悬疑型（暗色调+线索铺设+反转揭秘）
    ├─ 激励/燃向 → 🔥 热血型（动态构图+速度线+高饱和色彩）
    ├─ 社会观察/讽刺 → 🪞 讽刺型（对比构图+隐喻+留白+反讽对白）
    └─ 品牌/产品推广 → 📢 营销型（场景植入+痛点共鸣+产品解决方案）
```

**🚪 Gate 0 检查项**：主题是否清晰一句话可表述？目标受众是否明确？画风方向是否已确定？世界观是否自洽？

---

## 五、Phase 1：剧本创作

> **目标**：创作完整的漫剧剧本，包含故事结构、角色设定、分镜脚本。

| Agent | 角色 | 核心职责 | 输出 |
|-------|------|---------|------|
| **A4 PlotAgent** | 故事架构师 | 设计故事结构（三幕式/起承转合），规划主线+副线，设计冲突与转折点 | 故事大纲（幕-场-拍分层结构） |
| **A5 CharacterWriteAgent** | 角色剧作师 | 创建角色设定表（姓名/性格/背景/口头禅/关系网），设计角色弧线 | 角色设定表 × N |
| **A6 DialogueAgent** | 对白设计师 | 编写角色性格化对白，控制单格文字量（≤30字/格），融入网络化/口语化表达 | 全篇对白脚本 |
| **A7 StoryboardAgent** | 分镜脚本师 | 将剧情拆解为逐格分镜，每格包含：画面描述+角色+动作+表情+对白+镜头+特效 | 分镜脚本表（逐格） |
| **A8 PaceAgent** | 节奏控制师 | 控制叙事节奏曲线（铺垫→升温→高潮→反转→收尾），调整格密度和信息节奏 | 节奏分析图+节奏调整建议 |

### 分镜脚本标准格式

```yaml
# 分镜脚本 - 每一格的标准描述
panel_id: "P001"
page: 1
position: "top-left"  # 格子位置
size: "large"          # small/medium/large/full-width

scene:
  location: "教室，午后阳光透过窗户"
  time: "下午3点"
  weather: "晴天"
  
characters:
  - name: "小明"
    action: "趴在桌上打瞌睡"
    expression: "昏昏欲睡，嘴角有口水"
    position: "画面中心偏左"
    
  - name: "老师"
    action: "拿着粉笔回头看"
    expression: "黑线+青筋"
    position: "画面右侧，背对黑板"

camera:
  angle: "medium-shot"    # close-up/medium/wide/bird-eye/worm-eye/dutch
  perspective: "eye-level" # eye-level/high/low
  
dialogue:
  - speaker: "老师"
    text: "小明！你是来学习的还是来睡觉的？！"
    bubble_type: "shout"   # normal/shout/whisper/thought/narration
    
sfx: "ドキッ！"  # 音效文字（可选）
transition: "none"  # none/fade/zoom/time-skip
mood: "紧张搞笑"
```

### 节奏控制曲线

```
情感强度
  ▲
  │          ╱╲        ← 高潮（转折/揭秘/笑点爆发）
  │        ╱    ╲
  │      ╱        ╲    ← 收尾（余韵/反思/彩蛋）
  │    ╱            ╲
  │  ╱                ╲
  │╱                    ╲
  ├─────────────────────────▶ 格数
  开场     铺垫   升温   高潮   收尾

推荐格数分配（12格漫剧）:
  开场: 1-2格 (≈15%)
  铺垫: 2-3格 (≈25%)
  升温: 2-3格 (≈25%)
  高潮: 2-3格 (≈20%)
  收尾: 1-2格 (≈15%)
```

**🚪 Gate 1 检查项**：故事结构是否完整（有开端、发展、高潮、结尾）？角色是否有辨识度？对白是否自然且符合角色性格？每格文字量是否 ≤ 30字？分镜脚本是否足够详细可执行？

---

## 六、Phase 2：视觉设定

> **目标**：建立完整的视觉规范体系，确保后续画面生成的一致性。

| Agent | 角色 | 核心职责 | 输出 |
|-------|------|---------|------|
| **A9 CharacterDesignAgent** | 角色设计师 | 生成角色设定图（正面/侧面/3/4角度），定义视觉锚点（发型/配饰/服装颜色/体型比例） | 角色设定图 + 视觉锚点清单 |
| **A10 SceneDesignAgent** | 场景设计师 | 设计主要场景概念图（2-4个核心场景），定义光照/氛围/色调 | 场景概念图集 |
| **A11 StyleGuideAgent** | 风格统一师 | 制定视觉规范手册（配色方案/线条粗细/阴影风格/透视规则/头身比） | 视觉规范手册（StyleGuide） |
| **A12 PropDesignAgent** | 道具设计师 | 设计关键道具/标志性物件/UI元素，确保道具辨识度 | 道具设定图集 |
| **A13 ExpressionLibAgent** | 表情库构建师 | 为每个角色生成表情库（喜/怒/哀/惊/尴尬/得意/无语/暴走等 8-12 种） | 角色表情库（每角色 8-12 张） |

### 视觉锚点系统（Character Anchor System）

```
角色视觉锚点 = 确保 AI 在不同分镜中生成一致角色的关键特征

锚点层级：
  L1 - 不可变特征（每帧必须一致）:
    ├── 发型 + 发色（如：黑色齐刘海长发）
    ├── 体型比例（如：6头身Q版）
    ├── 标志性配饰（如：红色蝴蝶结发卡）
    └── 瞳色（如：琥珀色大眼）

  L2 - 可变但受限特征:
    ├── 服装（场景切换时可变，但风格一致）
    ├── 表情（随情节变化）
    └── 姿态（随动作变化）

  L3 - 自由特征:
    ├── 光影（随场景变化）
    ├── 景深（随构图变化）
    └── 特效（随剧情需要）
```

### Prompt 模板体系（给 A15 使用）

```markdown
## 角色 Prompt 基础模板
[画风描述], [角色名] character sheet,
[发型+发色], [瞳色], [体型描述], [标志性配饰],
[服装描述], [表情], [姿态/动作],
[场景/背景], [光照], [镜头角度],
high quality, detailed, consistent style, manga panel
```

**🚪 Gate 2 检查项**：角色设定图是否涵盖多角度？视觉锚点是否明确且可在 Prompt 中复现？风格规范是否完整？表情库是否覆盖剧本所需情绪？各角色视觉辨识度是否足够？

---

## 七、Phase 3：画面生成

> **目标**：基于分镜脚本和视觉设定，生成高质量、风格一致的漫画画面。
> ⚠️ 本 Phase 高度依赖 **腾讯混元生图 3.0 API**

| Agent | 角色 | 核心职责 | 腾讯云服务 |
|-------|------|---------|-----------|
| **A14 CompositionAgent** | 构图师 | 根据分镜脚本确定每格构图参数（特写/中景/远景/俯视/仰视/Dutch角/对角线构图） | — |
| **A15 PromptEngineerAgent** | Prompt工程师 | 将分镜描述+角色锚点+场景+构图参数合成为高质量混元生图 Prompt | 混元大模型（辅助优化Prompt） |
| **A16 ImageGenAgent** | 画面生成师 | 调用混元生图 3.0 API 生成漫画画面，管理生成参数（分辨率/风格/种子等） | **混元生图 3.0** |
| **A17 ConsistencyCheckAgent** | 一致性校验师 | 检查角色外观一致性（面部/发型/服装/体型），标记不一致帧→回溯 A16 重生 | 混元大模型（视觉理解） |
| **A18 RetouchAgent** | 精修师 | 局部修复（面部/手部/文字伪影）、细节增强、背景补完、表情微调 | 混元生图（图生图） |

### 混元生图 3.0 调用流程

```
A15 生成 Prompt
    │
    ▼
SubmitHunyuanImageJob（提交异步任务）
    │ 参数: Prompt + Resolution + Style + Seed + NegativePrompt
    │ Region: ap-guangzhou
    │
    ▼
获得 JobId → 轮询 QueryHunyuanImageJob
    │
    ├─ 状态: Processing → 等待
    ├─ 状态: Success → 获取图片URL
    │     │
    │     ▼
    │   A17 一致性检查
    │     │
    │     ├─ ✅ 通过 → A19 进入排版
    │     └─ ❌ 不通过 → 调整Prompt/Seed → 重新提交
    │
    └─ 状态: Failed → 记录错误 → 调整参数重试
```

### Prompt 工程最佳实践

```markdown
## 正面提示词（Positive Prompt）结构
[风格] + [角色描述（含锚点）] + [动作/表情] + [场景] + [镜头] + [质量修饰]

示例:
"japanese manga style, black and white with screentone,
a girl named Xiaomei with long black hair and red butterfly hair clip,
amber eyes, school uniform, 6-head proportion,
surprised expression with sweat drops, mouth open,
standing in classroom with sunlight through windows,
medium shot, eye-level perspective,
high quality, detailed linework, professional manga panel"

## 负面提示词（Negative Prompt）
"low quality, blurry, deformed hands, extra fingers,
inconsistent style, realistic photo, 3d render,
text artifacts, watermark, signature,
anatomical errors, broken anatomy"

## 关键参数配置
Resolution: 1024x1024（单格） / 768x1024（竖格） / 1024x768（横格）
Style: 根据 StyleGuide 固定
Seed: 同角色同场景使用相近 Seed 提升一致性
```

**🚪 Gate 3 检查项**：所有分镜画面是否已生成？角色一致性评分是否 ≥ 85%？画面质量是否达标（无明显伪影/畸形）？风格是否与 StyleGuide 一致？不一致帧是否已修复？

---

## 八、Phase 4：排版合成

> **目标**：将画面、对白、音效文字合成为专业的漫画排版。

| Agent | 角色 | 核心职责 | 工具依赖 |
|-------|------|---------|---------|
| **A19 LayoutAgent** | 排版设计师 | 设计分格布局（格子大小/间距/阅读顺序），适配目标平台尺寸 | Canvas/数据万象 CI |
| **A20 BubbleAgent** | 气泡对白师 | 设计对白气泡样式/位置/字体，旁白框设计，控制气泡不遮挡画面关键区域 | Canvas/SVG |
| **A21 SFXAgent** | 音效文字师 | 设计拟声词/特效文字（爆炸声/心跳/脚步声的视觉化表达），选择字体和排列方式 | Canvas/字体库 |
| **A22 TransitionAgent** | 转场特效师 | 设计格间转场效果（淡入淡出/缩放/时间流逝标记），情绪渲染视觉元素 | — |
| **A23 AssemblyAgent** | 成品合成师 | 画面+气泡+音效+转场 → 合成最终漫剧（长图/分页/视频） | 数据万象 CI / FFmpeg |

### 气泡类型规范

```
┌─────────────────────────────────────────────────┐
│  气泡类型                                         │
├─────────────────────────────────────────────────┤
│                                                   │
│  ╭──────────╮   普通对白（圆角矩形，白底黑字）      │
│  │  你好啊~  │                                     │
│  ╰────╥─────╯                                     │
│       ╙──▸                                        │
│                                                   │
│  ╔══════════╗   大喊/震惊（锯齿边框，粗体字）       │
│  ║  什么?!  ║                                     │
│  ╚════╦═════╝                                     │
│       ╙──▸                                        │
│                                                   │
│  ┌╌╌╌╌╌╌╌╌╌╌┐   内心独白（虚线边框，斜体字）       │
│  ╎ 怎么办... ╎                                    │
│  └╌╌╌╌╌╌╌╌╌╌┘                                    │
│       ○ ○ ○                                       │
│                                                   │
│  ┌──────────┐   旁白/叙述（方形框，位于画面边角）    │
│  │ 三年后── │                                     │
│  └──────────┘                                     │
│                                                   │
│  ꧁༺ 悄悄话 ༻꧂  耳语（波浪线小气泡，小字号）       │
│                                                   │
└─────────────────────────────────────────────────┘
```

### 排版适配矩阵

| 平台 | 宽度(px) | 单格高度 | 格间距 | 字体大小 | 特殊要求 |
|------|---------|---------|-------|---------|---------|
| 微信公众号 | 750 | 500-800 | 10-20 | 24-28px | 长图拼接，首屏吸引 |
| 小红书 | 1080 | 1080 | 0-10 | 28-32px | 方形封面，最多9图 |
| 抖音/视频号 | 1080 | 1920 | — | 36-42px | 竖屏视频，3-5秒/帧 |
| B站专栏 | 1100 | 自由 | 15-25 | 22-26px | 长图+分P |
| Webtoon | 800 | 自由 | 0 | 26-30px | 纯竖滚动，无间距 |

**🚪 Gate 4 检查项**：排版是否符合目标平台规范？气泡是否不遮挡画面关键内容？阅读顺序是否清晰？文字是否清晰可读？合成后整体视觉效果是否和谐？

---

## 九、Phase 5：审校与发布

> **目标**：最终质量把关、多格式导出、发布准备。

| Agent | 角色 | 核心职责 | 输出 |
|-------|------|---------|------|
| **A24 QualityReviewAgent** | 质量审查师 | 画面质量/文字错误/逻辑连贯/阅读体验/情感传达 全维度审查 | 质量审查报告 |
| **A25 AccessibilityAgent** | 可读性优化师 | 文字大小/对比度检查/色盲友好/移动端预览/加载速度优化 | 可读性优化报告 |
| **A26 FormatExportAgent** | 格式导出师 | 导出多格式：长图PNG/分页PDF/竖屏MP4/WebP/GIF动图 | 多格式资产包 |
| **A27 PublishAgent** | 发布助手 | 生成标题/封面图/摘要/SEO标签/Hashtag，适配各平台发布规范 | 发布物料包 |

### 发布物料清单

```
📦 漫剧发布包
├── 📄 漫剧正文
│   ├── comic_full.png        (长条漫完整版)
│   ├── comic_page_01.png     (分页版 - 第1页)
│   ├── comic_page_02.png     (分页版 - 第2页)
│   └── comic_page_XX.png     (分页版 - 第N页)
│
├── 🎬 视频版（可选）
│   ├── comic_video_vertical.mp4   (竖屏9:16)
│   └── comic_video_square.mp4     (方形1:1)
│
├── 🖼️ 封面与缩略图
│   ├── cover_wechat.png      (750x400 微信)
│   ├── cover_xiaohongshu.png (1080x1080 小红书)
│   └── cover_thumbnail.png   (400x400 缩略图)
│
├── 📝 文案
│   ├── title.txt             (标题 × 3 备选)
│   ├── summary.txt           (摘要/简介)
│   ├── tags.txt              (标签/Hashtag)
│   └── alt_text.txt          (无障碍替代文本)
│
└── 🎵 音频（可选）
    ├── voiceover.mp3         (旁白配音)
    └── character_voices/     (角色配音)
```

**🚪 Gate 5 检查项**：所有文字无错别字？画面无伪影/畸变？故事逻辑连贯？情感传达到位？各平台格式正确？封面吸引力够？

---

## 十、贯穿型智能体（Cross-Phase Agents）

| Agent | 角色 | 核心职责 | 活跃阶段 |
|-------|------|---------|---------|
| **C1 StyleConsistencyAgent** | 风格一致性守护者 | 监控全篇画风/配色/线条/阴影一致性，发现偏差立即标记 | Phase 2-5 |
| **C2 NarrativeCoherenceAgent** | 叙事连贯性守护者 | 监控故事逻辑/角色行为一致性/伏笔回收/情感弧线连贯 | Phase 1-5 |
| **C3 CharacterConsistencyAgent** | 角色一致性引擎 | 维护角色视觉特征向量+Prompt模板，跨帧比对校验一致性 | Phase 2-4（核心） |
| **C4 MemoryAgent** | 创作过程记忆 | 记录创作决策/版本历史/成功Prompt/参数配置/风格参数 | 全程 |

### C3 角色一致性引擎工作机制

```
Phase 2（建立基准）:
  A9 生成角色设定图 → C3 提取视觉特征向量
  │
  ▼
  角色特征向量 = {
    "角色名": "小明",
    "发型": "黑色短发，刘海偏左",
    "发色": "#2C2C2C",
    "瞳色": "#8B4513",
    "头身比": "6头身",
    "体型": "偏瘦少年体型",
    "标志配饰": "蓝色运动手环",
    "默认服装": "白衬衫+深蓝校裤",
    "prompt_template": "a boy named Xiaoming, short black hair parted left,
                        brown eyes, slim teenager, 6-head proportion,
                        blue sports wristband, {expression}, {action},
                        {clothing_override or 'white shirt and navy pants'}"
  }

Phase 3（持续校验）:
  每生成一帧 → C3 对比检查
  │
  ├─ 发型匹配度 ≥ 90%? ✅/❌
  ├─ 配饰是否存在? ✅/❌
  ├─ 体型比例一致? ✅/❌
  ├─ 面部特征相似? ✅/❌
  │
  └─ 总分 < 85% → 标记重生
```

---

## 十一、模型选型与配置方案

> **默认原则**：免费国产内置模型优先 → 开源本地方案次选 → 付费云API备选
> 详细模型对比请参阅 [README.md 第十章](./README.md#十模型选型与经济方案矩阵model-selection--cost-optimization)

### 11.1 LLM 文本模型选型（全部免费，CodeBuddy 内置）

| Agent 分组 | 默认模型（最经济✅） | 备选最佳（耗tokens） | 选型理由 |
|-----------|-------------------|-------------------|---------|
| PM + Orchestrator | **DeepSeek-V3.2** | Claude-Opus-4.6 | 管控层需最强推理，DS-V3.2 国产免费推理最强 |
| A0-A3（策划层） | **MiniMax-M2.7** | Claude-Sonnet-4.5 | 创意策划需要强创造力，MM-M2.7 创意写作强 |
| A4-A8（剧本创作） | **MiniMax-M2.7** | Claude-Sonnet-4.5 | 故事/角色/对白需要创意表达 |
| A9-A13（视觉设定） | **Hunyuan-2.0-Instruct** | Gemini-3.1-flash-lite | 视觉描述需精确指令跟随 |
| A14-A15（构图+Prompt） | **Hunyuan-2.0-Instruct** | GPT-5.2 | Prompt 工程需精准指令 |
| A16 ImageGen | 见下方生图方案 | — | 独立AI绘画服务 |
| A17 一致性校验 | **Hunyuan-2.0-Thinking** | GPT-5.2（多模态） | 需视觉理解+深度比较 |
| A18 精修 | 见下方生图方案 | — | 图生图服务 |
| A19-A23（排版合成） | **GLM-5.0-Turbo** | Claude-Haiku-4.5 | 轻量格式化任务，速度优先 |
| A24-A27（审校发布） | **GLM-5.0** | Claude-Sonnet-4.5 | 综合审查需理解力 |
| C1-C4（贯穿型） | **DeepSeek-V3.2** | Claude-Opus-4.6 | 跨阶段需持续深度推理 |

### 11.2 三套完整配置方案

#### 方案 A：最经济方案（默认推荐✅ 总成本 ¥0/部）

```yaml
# ====== 方案A：最经济漫剧配置（全免费） ======

# 1. LLM 文本生成 — CodeBuddy 内置国产模型（免费）
llm:
  creative:     "MiniMax-M2.7"        # 策划+剧本+创意（免费）
  reasoning:    "DeepSeek-V3.2"       # 管控+理论+贯穿（免费）
  instruction:  "Hunyuan-2.0-Instruct" # Prompt工程+视觉描述（免费）
  thinking:     "Hunyuan-2.0-Thinking" # 一致性校验+深度分析（免费）
  general:      "GLM-5.0"             # 审查+综合写作（免费）
  lightweight:  "GLM-5.0-Turbo"       # 排版+格式化+轻量（免费）

# 2. AI 生图 — CodeBuddy 内置 image_gen（免费）
image_gen:
  provider: "codebuddy_builtin"       # 内置工具，无需配置
  quality: "high"
  size: "1024x1024"
  # 无人像克隆能力，如需请切换方案B

# 3. TTS 语音合成 — CosyVoice 2（开源免费+音色克隆）
tts:
  provider: "cosyvoice2"
  repo: "https://github.com/FunAudioLLM/CosyVoice.git"
  model: "CosyVoice2-0.5B"
  features:
    voice_clone: true                 # ✅ 3秒音频即可克隆
    languages: ["zh", "en", "ja", "ko", "yue", "sichuan"]
    emotion_control: true             # ✅ 情感控制
    streaming: true                   # ✅ 流式生成，150ms首包
  character_voices:
    narrator: "reference_audio/narrator.wav"      # 旁白音色参考
    character_1: "reference_audio/char1.wav"      # 角色1参考（3秒即可）
    character_2: "reference_audio/char2.wav"      # 角色2参考
  # 👈 用户只需提供每个角色 3 秒以上的参考音频

# 4. 存储 — 本地文件系统（免费）
storage:
  provider: "local"
  base_path: "./comic-drama-output/"
  structure:
    assets: "{project_id}/assets/"
    drafts: "{project_id}/drafts/"
    output: "{project_id}/output/"
```

| 服务 | 方案 | 费用 | 备注 |
|------|------|------|------|
| LLM 文本 | CodeBuddy 内置国产模型 | **¥0** | 国产模型完全免费 |
| AI 生图 | CodeBuddy image_gen | **¥0** | 内置工具 |
| TTS | CosyVoice 2 本地 | **¥0** | 开源，支持音色克隆 |
| 存储 | 本地文件系统 | **¥0** | — |
| **单部总计** | | **¥0** | 🎉 全免费 |

#### 方案 B：最经济 + 人像克隆（需本地GPU，总成本 ¥0/部）

```yaml
# ====== 方案B：免费 + 人像克隆 ======
# 需要本地 NVIDIA GPU ≥ 8GB VRAM

# 1-3 同方案A（LLM + TTS 不变）

# 4. AI 生图 — SD + InstantID（免费+人像克隆）
image_gen:
  provider: "stable_diffusion_local"
  model: "SDXL 1.0"                   # 或 ProtoVision XL
  plugins:
    - name: "InstantID"                # 人像克隆核心插件
      model: "ip-adapter_instant_id_sdxl.bin"
      controlnet: "control_instant_id_sdxl.safetensors"
      insightface: "antelopev2"        # 人脸embedding提取
    - name: "ControlNet"               # 构图控制
      models: ["canny", "openpose"]
  default_params:
    steps: 30
    cfg_scale: 7.0
    resolution: "1024x1024"
    sampler: "euler_a"

# 人像克隆工作流
character_consistency:
  method: "InstantID"
  workflow:
    1: "提供角色正脸参考图（1张即可）"
    2: "InsightFace 提取人脸 embedding + 面部标志"
    3: "IP-Adapter 注入人脸特征到生成过程"
    4: "ControlNet 控制姿态/构图"
    5: "跨分镜保持角色外观高度一致"
  tips:
    - "参考图越清晰一致性越好"
    - "固定 seed 可提升帧间稳定性"
    - "建议先生成角色sheet（多角度）作为锚定"
```

| 服务 | 方案 | 费用 | 备注 |
|------|------|------|------|
| LLM 文本 | CodeBuddy 内置国产模型 | **¥0** | 国产模型完全免费 |
| AI 生图 | SD + InstantID 本地 | **¥0** | 开源，人像克隆 |
| TTS | CosyVoice 2 本地 | **¥0** | 开源，音色克隆 |
| 存储 | 本地文件系统 | **¥0** | — |
| **单部总计** | | **¥0** | 🎉 全免费 + 人像克隆 |

#### 方案 C：腾讯云全栈方案（~¥5-6/部，省心云端）

```yaml
# ====== 方案C：腾讯云全栈（原始方案，云端省心） ======

# 1. LLM — 依然用 CodeBuddy 内置免费模型（无需混元API）
llm:
  # 同方案A，使用 CodeBuddy 内置国产免费模型
  # 不再需要 hunyuan-pro API Key！

# 2. 混元生图 3.0（图像生成）
hunyuan_image:
  endpoint: "hunyuan.tencentcloudapi.com"
  action: "SubmitHunyuanImageJob"
  region: "ap-guangzhou"
  secret_id: "${SECRET_ID}"        # 👈 用户需提供
  secret_key: "${SECRET_KEY}"      # 👈 用户需提供
  default_params:
    resolution: "1024x1024"
    num_images: 1
    seed: -1

# 3. TTS — 腾讯云 TTS
tencent_tts:
  endpoint: "tts.tencentcloudapi.com"
  default_params:
    voice_type: 301002             # 大模型音色（女）
    character_voices:
      narrator: 301001
      character_1: 301002
      character_2: 301003
    codec: "mp3"
    speed: 0
    volume: 0
    sample_rate: 16000

# 4. COS 对象存储
cos:
  bucket: "${COS_BUCKET}"          # 👈 用户需提供
  region: "ap-guangzhou"
  base_path: "comic-drama/"

# 5. 数据万象 CI
ci:
  bindBucket: "${COS_BUCKET}"
  capabilities: ["image_process", "image_composite", "gif_compose", "media_transcode"]
```

| 服务 | 方案 | 费用 | 备注 |
|------|------|------|------|
| LLM 文本 | CodeBuddy 内置国产模型 | **¥0** | 不再需要混元API！ |
| AI 生图 | 混元生图 3.0 | ~¥4.2 | ~30张含重试 |
| TTS | 腾讯云 TTS | ~¥0.4 | ~2000字 |
| COS | 腾讯云 COS | ~¥0.01 | ~100MB |
| CI | 数据万象 | ~¥0.001 | ~50次 |
| **单部总计** | | **~¥4.6** | 比原始方案省¥1（LLM免费了） |

> 💡 **vs 原始方案**：即使选腾讯云方案，LLM 部分也改用 CodeBuddy 内置免费模型，省去 hunyuan-pro 的 ¥0.6/部费用。

### 11.3 三套方案对照速查

| 维度 | 方案A 最经济✅ | 方案B 免费+人像克隆 | 方案C 腾讯云全栈 |
|------|-------------|-------------------|----------------|
| **LLM** | CB内置国产（免费） | CB内置国产（免费） | CB内置国产（免费） |
| **生图** | CB image_gen | SD+InstantID本地 | 混元生图3.0 |
| **TTS** | CosyVoice 2 本地 | CosyVoice 2 本地 | 腾讯云TTS |
| **音色克隆** | ✅ CosyVoice | ✅ CosyVoice | ✅（付费） |
| **人像克隆** | ❌ | ✅ InstantID | ❌ |
| **需要GPU** | ❌ | ✅ NVIDIA 8GB+ | ❌ |
| **需要API Key** | ❌ | ❌ | ✅ 腾讯云 |
| **单部成本** | **¥0** | **¥0** | **~¥4.6** |
| **适合场景** | 快速出片/低成本 | 角色一致性要求高 | 生产级/高质量 |

### 11.4 方案选择决策

```
你的需求是？
    │
    ├─ 快速验证/低成本出片 → 方案A（¥0，即刻可用）
    │
    ├─ 角色外观必须跨帧一致（同一人物不同姿态） → 方案B（¥0，需本地GPU）
    │
    ├─ 生产级质量/中文生图效果最佳 → 方案C（~¥4.6/部）
    │
    └─ 混合方案（推荐✅）
        ├─ LLM: CB内置免费模型（全方案通用）
        ├─ 生图: 草稿用 CB image_gen，定稿用混元生图（精品场景）
        ├─ TTS: CosyVoice 2 本地免费（音色克隆免费）
        └─ 人像: 需要时启用 InstantID（免费）
```

---

## 十二、漫剧类型适配矩阵

```
Agent                搞笑  科普  悬疑  热血  治愈  营销
──────────────────────────────────────────────────
Phase 0 (4 agents)    ●    ●    ●    ●    ●    ●
Phase 1 A4 Plot       ●    ●    ●●   ●●   ●    ●
Phase 1 A5 Character  ●●   ◐    ●●   ●●   ●●   ◐
Phase 1 A6 Dialogue   ●●   ●    ●    ●    ●●   ●●
Phase 1 A7 Storyboard ●    ●    ●●   ●●   ●    ●
Phase 1 A8 Pace       ●●   ●    ●●   ●●   ●    ●
Phase 2 (5 agents)    ●    ●    ●    ●    ●    ●
Phase 3 A16 ImageGen  ●    ●    ●    ●●   ●    ●
Phase 3 A18 Retouch   ◐    ●    ●    ●    ◐    ◐
Phase 4 A21 SFX       ●●   ◐    ●    ●●   ◐    ◐
Phase 5 (4 agents)    ●    ●    ●    ●    ●    ●●
Cross-Phase (4)       ●    ●    ●●   ●    ●    ●
──────────────────────────────────────────────────
强调重点:        对白 信息 分镜 画面  氛围  转化
                节奏 准确 节奏 特效  色调  CTA

●● 加强  ● 标准  ◐ 可选
```

---

## 十三、质量门控与评分体系

### 漫剧质量评分卡（满分 100 分）

| 维度（各 20 分） | 评估项（各 4 分） |
|-----------------|-----------------|
| **一、叙事质量** | 故事完整性 / 节奏控制 / 冲突设计 / 情感传达 / 结尾满足感 |
| **二、角色塑造** | 性格辨识度 / 对白自然度 / 行为一致性 / 角色弧线 / 关系表达 |
| **三、视觉质量** | 画面精细度 / 风格统一性 / 角色一致性 / 构图专业度 / 色彩和谐 |
| **四、排版设计** | 格子布局合理 / 气泡不遮挡 / 阅读顺序清晰 / 文字清晰 / 整体美感 |
| **五、传播力** | 标题吸引力 / 封面抓眼 / 首格钩子 / 分享意愿 / 平台适配 |

**评级**：90-100🟢精品 / 80-89🟡优良 / 70-79🟠需改进 / <70🔴需重做

---

## 十四、核心 Agent Prompt 模板

### A4 PlotAgent（故事架构师）

```markdown
## 角色：资深漫剧编剧，擅长短篇故事结构设计
## 输入：主题({theme}) + 类型({genre}) + 格数({panel_count}) + 受众({audience})

## 工作流程：
1. 确定核心冲突/笑点/悬念/反转
2. 设计三幕式结构（起-承-转-合 或 铺垫-升温-高潮-收尾）
3. 为每一幕分配格数和情感强度
4. 确保有"钩子"（首格吸引）和"锚点"（结尾回味）

## 输出格式：
- 一句话核心：[故事核心用一句话概括]
- 故事大纲：[分幕叙述]
- 格数分配：[每幕几格，标注情感强度]
- 反转/高潮设计：[具体描述]

## 约束：
- {panel_count}格内必须讲完一个完整故事
- 首格必须在3秒内抓住读者注意力
- 每格只承载1个关键信息
- 反转/笑点/高潮必须出现在倒数2-3格
```

### A7 StoryboardAgent（分镜脚本师）

```markdown
## 角色：专业漫画分镜师，精通镜头语言和漫画叙事
## 输入：故事大纲({plot}) + 角色设定({characters}) + 对白({dialogue})

## 为每一格输出：
1. panel_id: 格子编号
2. size: 格子大小（small/medium/large/full-width）
3. camera: 镜头（close-up/medium/wide/bird-eye/worm-eye/dutch）
4. characters: 出场角色（名字+动作+表情+位置）
5. scene: 场景描述（地点+光照+氛围）
6. dialogue: 对白（说话人+内容+气泡类型）
7. sfx: 音效文字（如有）
8. mood: 情绪基调
9. transition: 与下一格的转场

## 分镜原则：
- 重要内容用大格，过渡用小格
- 对话场景交替特写说话者面部
- 高潮/反转用全幅或跨格
- 运动方向遵循阅读方向（从左到右/从上到下）
- 避免连续3格以上相同机位
```

### A15 PromptEngineerAgent（Prompt工程师）

```markdown
## 角色：AI绘画Prompt工程专家，精通混元生图3.0的提示词优化
## 输入：分镜描述({panel}) + 角色视觉锚点({character_anchors}) + 风格规范({style_guide})

## Prompt 构造规则：
1. [风格声明] — 来自StyleGuide的统一风格描述
2. [角色描述] — 从锚点系统提取，L1特征逐字复现
3. [表情动作] — 从分镜脚本提取
4. [场景环境] — 从分镜脚本+场景设定提取
5. [构图参数] — 从CompositionAgent提取
6. [质量修饰] — 固定后缀：high quality, detailed, etc.

## 输出：
- positive_prompt: [正面提示词]
- negative_prompt: [负面提示词]
- resolution: [分辨率建议]
- seed: [种子值建议（同角色同场景用相近seed）]

## 约束：
- 角色L1锚点特征必须逐字出现在prompt中
- 风格描述前缀必须与全篇一致
- 避免矛盾描述（如"微笑"和"愤怒"同时出现）
- 中文优先（混元生图对中文理解更强）
```

---

## 十五、Agent 间协作协议

### 消息协议

```json
{
  "message_id": "MSG-COMIC-001",
  "type": "phase_output | panel_gen | consistency_check | gate_result",
  "from": { "agent_id": "A16_ImageGen", "phase": "Phase3" },
  "to": { "agent_id": "A17_ConsistencyCheck", "phase": "Phase3" },
  "payload": {
    "panel_id": "P005",
    "image_url": "https://cos.ap-guangzhou.myqcloud.com/.../panel_005.png",
    "prompt_used": "...",
    "seed": 42,
    "resolution": "1024x1024",
    "generation_time_ms": 8500,
    "characters_in_panel": ["小明", "老师"],
    "quality_flag": "green"
  },
  "consistency_result": {
    "overall_score": 0.92,
    "character_scores": {
      "小明": { "score": 0.95, "issues": [] },
      "老师": { "score": 0.88, "issues": ["眼镜框颜色偏差"] }
    },
    "action": "pass"  // pass | warn | regen
  }
}
```

### 核心数据流

```
用户主题输入
    │
    ▼
A0→A1∥A2→A3 →[G0]→ A4→A5→A6∥A8→A7 →[G1]
→ A11→A9∥A10∥A12→A13 →[G2]
→ A14→A15→A16→A17→(A18) →[G3]  ← 可能循环（一致性不通过→重生）
→ A19→A20∥A21→A22→A23 →[G4]
→ A24→A25→A26→A27 →[G5]→ 📄 发布！
```

---

## 十六、角色一致性引擎（详细设计）

### 角色特征向量数据结构

```json
{
  "character_id": "CHAR-001",
  "name": "小明",
  "name_en": "Xiaoming",
  "visual_anchors": {
    "L1_immutable": {
      "hair_style": "黑色短发，齐刘海微偏左",
      "hair_color": "#2C2C2C",
      "eye_color": "#8B4513 琥珀色大眼",
      "head_body_ratio": "6头身",
      "body_type": "偏瘦少年体型",
      "signature_accessory": "左手蓝色运动手环",
      "distinguishing_features": "左眉上有一颗小痣"
    },
    "L2_constrained": {
      "default_outfit": "白衬衫+深蓝校裤+白运动鞋",
      "alt_outfits": {
        "casual": "灰色帽衫+牛仔裤",
        "sports": "蓝白运动服"
      }
    }
  },
  "prompt_template": "a teenage boy named Xiaoming, short black hair with slightly left-parted bangs, amber eyes, slim build, 6-head proportion, blue sports wristband on left hand, small mole above left eyebrow, {expression}, {action}, {outfit}, {scene}",
  "expression_library": {
    "happy": "bright smile, eyes squinting",
    "angry": "furrowed brows, clenched teeth",
    "surprised": "wide eyes, open mouth, sweat drop",
    "sad": "downcast eyes, slight frown",
    "embarrassed": "blushing cheeks, awkward smile, sweat drop",
    "smug": "half-closed eyes, corner smile, arms crossed",
    "shocked": "popping eyes, jaw drop, hair standing",
    "thinking": "hand on chin, looking up, one eye closed"
  },
  "consistency_threshold": 0.85
}
```

### 一致性评估维度

```
┌────────────────────────────────────────────┐
│  角色一致性评分维度（满分 1.0）              │
├────────────────────────────────────────────┤
│  发型匹配度      权重 0.25   阈值 0.90      │
│  面部特征匹配    权重 0.25   阈值 0.85      │
│  标志配饰存在    权重 0.20   阈值 0.95      │
│  体型比例一致    权重 0.15   阈值 0.80      │
│  服装匹配度      权重 0.15   阈值 0.80      │
│  ────────────────────────────────────────  │
│  总分 ≥ 0.85 → ✅ 通过                     │
│  总分 0.70-0.85 → ⚠️ 警告（标记但放行）     │
│  总分 < 0.70 → ❌ 重生（回退 A15→A16）      │
└────────────────────────────────────────────┘
```

---

## 十七、平台适配规范

### 微信公众号（长条漫）

```yaml
canvas:
  width: 750px
  max_single_image_height: 20000px  # 微信单图最大高度
  dpi: 72
  format: PNG/JPEG(质量95)
  
layout:
  panels_per_row: 1               # 竖排单列
  panel_gap: 10-20px
  margin_lr: 20px
  first_panel: "吸引力钩子，大标题+核心冲突预告"
  last_panel: "关注引导/二维码/下期预告"
  
text:
  font: "思源黑体/方正兰亭黑"
  size: 24-28px
  line_height: 1.5
  max_chars_per_bubble: 30
  
tips:
  - 总高度建议 5000-15000px（太长加载慢）
  - 每 3-4 格插入一个"钩子格"保持阅读动力
  - 末尾添加关注引导 CTA
```

### 抖音/视频号（动态漫剧）

```yaml
video:
  resolution: 1080x1920 (9:16竖屏)
  fps: 1-2 (漫剧节奏：每帧3-5秒)
  duration: 30-60秒
  format: MP4 (H.264)
  
audio:
  bgm: "轻音乐/环境音"
  voiceover: "TTS角色配音（可选）"
  sfx: "音效（翻页声/打击声等）"
  
animation:
  panel_transition: "slide_up / fade / zoom_in"
  ken_burns: true  # 慢速缩放/平移增加动态感
  bubble_appear: "typewriter"  # 对白逐字出现
  
tips:
  - 前3秒必须有强钩子（悬念/冲突/搞笑）
  - 配音可大幅提升完播率
  - 末尾留"评论引导"或"悬念预告"
```

---

## 十八、漫剧创作状态机

```
[主题输入] ──▶ [策划中] ──G0──▶ [编剧中] ──G1──▶ [设定中]
                                                    │
    ┌──────────────────────────────────────────G2───┘
    ▼
[生成中] ──▶ [一致性检查]
    │            │
    │     ┌──────┴──────┐
    │     │             │
    │   [通过]       [不通过]──▶ [调整Prompt] ──▶ [重新生成]
    │     │                                         │
    │     └─────────────────────────────────────────┘
    │
    ▼
[排版中] ──G4──▶ [审校中] ──G5──▶ [导出中] ──▶ [待发布]
                     │                            │
                  [需修改] ──▶ 回退至对应Phase      │
                                                  ▼
                                             [已发布 ✅]
```

---

## 十九、用户配置清单与默认值

### 🔴 必须提供

| 配置项 | 说明 | 获取方式 |
|--------|------|---------|
| **腾讯云 SecretId** | API 鉴权凭证 | [腾讯云控制台 → 访问管理 → API密钥](https://console.cloud.tencent.com/cam/capi) |
| **腾讯云 SecretKey** | API 鉴权凭证 | 同上 |
| **混元 API Key** | 混元大模型鉴权 | [混元控制台 → API Key](https://console.cloud.tencent.com/hunyuan/api-key) |
| **COS Bucket** | 对象存储桶名称 | [COS 控制台创建](https://console.cloud.tencent.com/cos/bucket)，建议 Region: `ap-guangzhou` |
| **漫剧主题** | 你想创作什么主题的漫剧 | 用户输入 |

### 🟡 建议确认（有默认值）

| 配置项 | 默认值 | 可选值 | 影响 |
|--------|-------|-------|------|
| **目标平台** | 微信公众号 | 微信/小红书/抖音/B站/Webtoon | 影响尺寸、格式、排版 |
| **画风** | 日系动漫 | 日漫/国漫/欧美/Q版/写实/赛博朋克/水墨/像素 | 影响 StyleGuide 和 Prompt |
| **格数** | 8-12格 | 4格/6格/8格/12格/16格/24格 | 影响故事深度和成本 |
| **是否配音** | 否 | 是/否 | 是→启用 TTS 服务（+¥0.4/部） |
| **是否视频版** | 否 | 是/否 | 是→启用媒体处理（+¥1/部） |
| **语言** | 中文 | 中文/英文/日文/双语 | 影响对白和 Prompt |
| **分辨率** | 1024×1024 | 512-2048 范围内 | 影响质量和成本 |
| **内容风格** | PG（全年龄） | PG/PG-13/Teen | 影响内容尺度 |

### 🟢 高级配置（可选）

| 配置项 | 默认值 | 说明 |
|--------|-------|------|
| 角色一致性阈值 | 0.85 | 降低可加快生成，升高更严格 |
| 最大重试次数 | 3 | 单帧一致性不通过的最大重生次数 |
| 混元生图并发数 | 1 | 默认1，可购买更多并发加速 |
| TTS 音色映射 | 自动分配 | 可指定每个角色使用的音色编号 |
| 自定义负面提示词 | 默认模板 | 追加额外的 Negative Prompt |
| 输出格式 | PNG | PNG/JPEG/WebP |

### 推荐快速启动配置

```bash
# 最小配置（3个必填项 + 主题即可开始）
export TENCENT_SECRET_ID="AKIDxxxxxxxx"
export TENCENT_SECRET_KEY="xxxxxxxx"
export HUNYUAN_API_KEY="hyk-xxxxxxxx"

# COS 存储桶（建议提前创建）
# 名称: comic-drama-{appid}
# 区域: ap-guangzhou（与混元生图同区域最佳）

# 然后直接输入主题即可：
# "请生成一部关于程序员转行开咖啡馆的搞笑漫剧，8格"
```

---

## 二十、与原始框架对照

| 维度 | 通用框架 | **漫剧生成团队** |
|------|---------|------------------|
| Agent 总数 | 16（通用） | **34（漫剧专用）** |
| Phase 数 | 5 | **6**（+视觉设定、+排版合成独立） |
| 核心挑战 | 信息准确性 | **角色一致性 + 画风统一** |
| AI 服务依赖 | LLM | **LLM + 文生图 + TTS + 图片处理** |
| 云服务集成 | 无 | **腾讯云全栈**（混元+COS+CI+TTS） |
| 一致性引擎 | 无 | **C3 角色一致性引擎**（视觉锚点+向量比对） |
| Prompt 工程 | 无 | **A15 专门 Prompt 工程 Agent** |
| 成本管控 | 无 | **~¥5/部（12格漫剧）** |
| 贯穿 Agent | 3 | **4**（+风格一致+叙事连贯） |
| 排版能力 | WriterAgent | **5 个排版 Agent**（布局+气泡+SFX+转场+合成） |
| 多平台适配 | 无 | **5 个平台规范**（微信/小红书/抖音/B站/Webtoon） |

---

> 💡 **核心理念**：漫剧创作是一个 **叙事驱动 + 视觉驱动** 的双轨创作过程。通过 28 个专业化 Agent 分工协作、4 个贯穿型 Agent 持续守护、6 道质量门控层层把关，配合 **腾讯云全栈 AI 基础设施**，我们构建了一个**从主题到成品的端到端漫剧生产流水线**。角色一致性引擎（C3）和 Prompt 工程 Agent（A15）是整个体系的核心技术支撑。

---

*文档版本：v1.0 | 最后更新：2026-03-21 | 基于通用多 Agent 研究框架扩展 | 默认腾讯云全栈方案*
*文件路径：`multi-agent-research-framework/comic-drama-creation-team.md`*
