# 后端日志和API - 学习笔记

**日期**: 2025-12-28  
**学习者**: Franke Chen

---

## 🎯 核心概念

后端日志系统帮助我们**理解系统运行**和**调试问题**。API文档展示所有可用的接口。

---

## 📊 后端API文档

已自动打开浏览器访问: **http://localhost:8000/docs**

这是 FastAPI 自动生成的**交互式API文档**（Swagger UI）。

### 主要API端点

#### 1. 健康检查

```
GET /
返回: {"message": "Helloagents AI Town Backend is running"}
```

#### 2. 获取所有NPC信息

```
GET /npcs
返回: [
  {
    "name": "张三",
    "title": "Python工程师",
    "location": "工位区",
    "activity": "写代码",
    "personality": "技术宅...",
    ...
  },
  ...
]
```

#### 3. 与NPC对话（核心接口）

```
POST /chat
请求体: {
  "npc_name": "张三",
  "message": "你好",
  "player_id": "player"  // 可选
}

返回: {
  "npc_name": "张三",
  "response": "你好！我是张三...",
  "affinity": {
    "current": 55.0,
    "changed": true,
    "old_affinity": 50.0,
    "new_affinity": 55.0,
    "change_amount": 5,
    "reason": "友好问候",
    "sentiment": "positive",
    "old_level": "熟人",
    "new_level": "熟人"
  },
  "memory_count": 2
}
```

#### 4. 获取NPC状态

```
GET /npcs/status
返回: {
  "张三": {
    "idle_chat": "最近在研究一个有趣的算法...",
    "last_update": "2025-12-28T15:30:00"
  },
  ...
}
```

---

## 📝 后端日志系统

### 日志级别

赛博小镇使用**彩色日志**系统（在后端窗口可见）：

```python
# logger.py 中的日志函数
log_info()           # 💬 蓝色 - 一般信息
log_dialogue_start() # 🎭 青色 - 对话开始
log_affinity()       # 💖 粉色 - 好感度信息
log_memory_retrieval() # 💾 黄色 - 记忆检索
log_generating_response() # 🤔 蓝色 - 生成回复中
log_npc_response()   # 🤖 绿色 - NPC回复
log_analyzing_affinity() # 🔍 黄色 - 分析情感
log_affinity_change() # 📊 绿色/红色 - 好感度变化
log_memory_saved()   # 💾 蓝色 - 记忆已保存
log_dialogue_end()   # ✅ 绿色 - 对话结束
```

### 典型日志流程

当你与张三对话时，后端日志会显示：

```
🎭 [对话开始] 玩家 → 张三
💬 玩家消息: "你好，很高兴认识你！"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💖 当前好感度: 50.0/100 (等级: 熟人)

💾 检索到 0 条相关记忆

🤔 正在生成回复...

🤖 张三的回复: "你好！我也很高兴认识你。我是张三，Python工程师。"

🔍 正在分析情感并更新好感度...

📊 好感度变化详情:
   变化: 是
   原好感度: 50.0
   新好感度: 55.0
   变化量: +5
   原因: 友好问候
   情感: positive
   原等级: 熟人
   新等级: 熟人

💾 对话已保存到记忆系统

✅ 对话结束
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔍 关键日志文件

### 1. logger.py - 日志系统

**文件**: `backend/logger.py`

```python
def log_dialogue_start(npc_name: str, message: str):
    """记录对话开始"""
    print(f"\n{CYAN}🎭 [对话开始] 玩家 → {npc_name}{RESET}")
    print(f"{BLUE}💬 玩家消息: \"{message}\"{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def log_affinity(npc_name: str, affinity: float, level: str):
    """记录当前好感度"""
    print(f"{MAGENTA}💖 当前好感度: {affinity:.1f}/100 (等级: {level}){RESET}\n")

def log_memory_retrieval(npc_name: str, count: int, memories: list):
    """记录记忆检索"""
    print(f"{YELLOW}💾 检索到 {count} 条相关记忆{RESET}")
    if memories:
        for mem in memories[:3]:  # 只显示前3条
            print(f"   - {mem.content[:50]}...")
    print()
```

### 2. main.py - API路由和生命周期

**文件**: `backend/main.py`

```python
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("\n🎮 赛博小镇后端服务启动中...")
    
    # 初始化NPC Agent管理器
    app.state.npc_manager = NPCAgentManager()
    
    # 启动状态管理器（定时更新NPC状态）
    app.state.state_manager = StateManager(app.state.npc_manager)
    
    print("\n✅ 所有服务已启动!")
    print(f"📡 API地址: http://0.0.0.0:8000")
    print(f"📚 API文档: http://0.0.0.0:8000/docs")
```

---

## 🎮 在Swagger UI中测试API

### 步骤1: 访问文档

浏览器打开: http://localhost:8000/docs

### 步骤2: 展开 `/chat` 接口

点击 **POST /chat**，然后点击 **Try it out**

### 步骤3: 输入测试数据

```json
{
  "npc_name": "张三",
  "message": "你好，能教我Python吗？",
  "player_id": "test_player"
}
```

### 步骤4: 点击 Execute

观察返回结果：

```json
{
  "npc_name": "张三",
  "response": "当然可以！我很乐意分享我的Python经验。你想从哪方面开始学习？",
  "affinity": {
    "current": 58.0,
    "changed": true,
    "old_affinity": 50.0,
    "new_affinity": 58.0,
    "change_amount": 8,
    "reason": "请教学习",
    "sentiment": "positive",
    "old_level": "熟人",
    "new_level": "熟人"
  },
  "memory_count": 2
}
```

同时，后端窗口会显示详细的处理日志！

---

## 💻 代码解析：日志系统

### 完整的对话处理流程（带日志）

**文件**: `backend/agents.py:170-261`

```python
def chat(self, npc_name: str, message: str, player_id: str = "player") -> str:
    try:
        # 1️⃣ 记录对话开始
        log_dialogue_start(npc_name, message)
        
        # 2️⃣ 获取好感度
        affinity = self.relationship_manager.get_affinity(npc_name, player_id)
        affinity_level = self.relationship_manager.get_affinity_level(affinity)
        log_affinity(npc_name, affinity, affinity_level)
        
        # 3️⃣ 检索记忆
        relevant_memories = memory_manager.retrieve_memories(...)
        log_memory_retrieval(npc_name, len(relevant_memories), relevant_memories)
        
        # 4️⃣ 生成回复
        log_generating_response()
        response = agent.run(enhanced_message)
        log_npc_response(npc_name, response)
        
        # 5️⃣ 分析好感度
        log_analyzing_affinity()
        affinity_result = self.relationship_manager.analyze_and_update_affinity(...)
        log_affinity_change(affinity_result)
        
        # 6️⃣ 保存记忆
        self._save_conversation_to_memory(...)
        log_memory_saved(npc_name)
        
        # 7️⃣ 对话结束
        log_dialogue_end()
        
        return response
        
    except Exception as e:
        print(f"❌ {npc_name}对话失败: {e}")
        traceback.print_exc()
        return f"抱歉，我现在有点忙..."
```

### 日志颜色定义

```python
# logger.py
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
```

---

## 🎯 学习要点

### 理论层面

1. ✅ 理解RESTful API的设计
2. ✅ 理解FastAPI的自动文档生成
3. ✅ 理解日志系统的重要性
4. ✅ 理解彩色日志的可读性优势

### 实现层面

1. ✅ FastAPI的路由定义
2. ✅ Pydantic模型验证
3. ✅ 日志函数的封装
4. ✅ 异常处理和错误日志

### 应用层面

1. ✅ 如何使用Swagger UI测试API
2. ✅ 如何通过日志调试问题
3. ✅ 如何观察系统运行流程
4. ✅ 如何监控好感度和记忆系统

---

## 📊 API调用示例（Python）

### 使用 requests 库

```python
import requests

# 1. 与NPC对话
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "npc_name": "张三",
        "message": "你好！",
        "player_id": "player_001"
    }
)

result = response.json()
print(f"NPC回复: {result['response']}")
print(f"当前好感度: {result['affinity']['current']}")

# 2. 获取所有NPC信息
response = requests.get("http://localhost:8000/npcs")
npcs = response.json()
for npc in npcs:
    print(f"{npc['name']} - {npc['title']}")

# 3. 获取NPC状态
response = requests.get("http://localhost:8000/npcs/status")
status = response.json()
print(f"张三的闲聊: {status['张三']['idle_chat']}")
```

---

## 🚀 扩展思路

### 1. 日志持久化

```python
# 将日志保存到文件
import logging

logging.basicConfig(
    filename='dialogue.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
```

### 2. 日志分析

```python
# 分析对话统计
def analyze_dialogue_logs():
    # 统计每个NPC的对话次数
    # 统计平均好感度变化
    # 识别常见问题
    pass
```

### 3. 实时监控

```python
# 创建监控面板
# 显示实时对话数量
# 显示API响应时间
# 显示错误率
```

### 4. 日志可视化

```
# 生成图表
- 对话数量趋势图
- 好感度变化曲线
- 记忆增长曲线
- API调用统计
```

---

## 📝 练习任务

### 基础任务

- [x] 访问 http://localhost:8000/docs
- [x] 在Swagger UI中测试 GET /npcs 接口
- [ ] 在Swagger UI中测试 POST /chat 接口
- [ ] 观察后端窗口的日志输出

### 进阶任务

- [ ] 用Python脚本调用API（不通过游戏）
- [ ] 连续对话3轮，观察记忆检索日志
- [ ] 找一个导致好感度下降的对话，观察日志
- [ ] 阅读 logger.py 的完整代码

### 挑战任务

- [ ] 添加新的日志函数（例如：log_error）
- [ ] 实现日志保存到文件
- [ ] 创建一个日志分析脚本
- [ ] 设计一个实时监控面板

---

## 🔍 常见问题排查

### 问题1: 对话失败，没有回复

**查看日志**:
```
❌ 张三对话失败: API rate limit exceeded
```

**解决方案**: 等待几分钟，或者更换API Key

### 问题2: 好感度没有变化

**查看日志**:
```
❌ 好感度分析失败: JSON decode error
```

**解决方案**: 检查情感分析Agent的提示词格式

### 问题3: 记忆检索失败

**查看日志**:
```
💾 检索到 0 条相关记忆
```

**原因**: 这是首次对话，还没有历史记忆

---

## 💡 日志最佳实践

### 1. 结构化日志

```python
# 不推荐
print(f"对话: {message}")

# 推荐
log_dialogue_start(npc_name, message)  # 带上下文
```

### 2. 分级记录

```python
# DEBUG: 详细调试信息
# INFO: 一般信息
# WARNING: 警告
# ERROR: 错误
# CRITICAL: 严重错误
```

### 3. 性能监控

```python
import time

start_time = time.time()
response = agent.run(message)
elapsed = time.time() - start_time

print(f"⏱️  生成耗时: {elapsed:.2f}秒")
```

---

**创建时间**: 2025-12-28  
**状态**: 📚 学习中  
**下一步**: 浏览核心代码文件
