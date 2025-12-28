# DuckDuckGo 搜索失败问题 - 完整解决方案

**问题日期**: 2025-12-27  
**问题类型**: 搜索引擎限流  
**影响**: 所有任务搜索失败

---

## 🔴 问题描述

### 错误信息
```
ERROR:services.search:Search backend duckduckgo failed: DuckDuckGo 搜索失败: No results found.
RuntimeError: DuckDuckGo 搜索失败: No results found.
```

### 问题原因
DuckDuckGo 免费搜索服务检测到**频繁请求**后进行了**限流（Rate Limiting）**，导致：
- ❌ 所有搜索请求返回 "No results found"
- ❌ 4个并行任务全部失败
- ❌ 无法生成研究报告

---

## ✅ 解决方案

### 方案 1: 使用 Tavily 搜索（强烈推荐）⭐⭐⭐⭐⭐

**优点**:
- ✅ 专为 AI 研究优化的搜索引擎
- ✅ 搜索质量高，结果更相关
- ✅ 免费版有 1000 次/月调用额度
- ✅ 稳定性好，不会被限流

**步骤**:

1. **注册 Tavily API** (免费)
   ```
   访问: https://tavily.com
   注册账号 → 获取 API Key
   ```

2. **配置 API Key**
   
   编辑文件: `backend/.env`
   
   ```ini
   # 搜索引擎配置
   SEARCH_API=tavily
   TAVILY_API_KEY=tvly-your-api-key-here
   ```

3. **重启后端服务**
   ```bash
   # 停止当前后端 (Ctrl+C)
   # 重新启动
   cd backend
   python src\main.py
   ```

4. **验证配置**
   启动后应该看到:
   ```
   INFO: Tavily API configured successfully
   ```

---

### 方案 2: 等待限流恢复（临时方案）

**DuckDuckGo 限流时长**: 通常 **15-30分钟**

**步骤**:
1. 停止所有测试
2. 等待 30 分钟
3. 重新尝试

**缺点**:
- ⏰ 需要等待
- 🔄 可能再次被限流
- ❌ 不适合频繁使用

---

### 方案 3: 使用 Perplexity API（高级方案）

**优点**:
- 🌟 最智能的搜索，直接返回答案
- 🌟 质量最高，不会被限流

**缺点**:
- 💰 需要付费 API

**配置**:
```ini
SEARCH_API=perplexity
PERPLEXITY_API_KEY=your-perplexity-key
```

---

## 🚀 推荐配置（最佳实践）

### 配置文件示例

`backend/.env`:
```ini
# ===================================
# 搜索引擎配置 (推荐 Tavily)
# ===================================
SEARCH_API=tavily
TAVILY_API_KEY=tvly-your-api-key-here

# 备用: DuckDuckGo (免费但可能被限流)
# SEARCH_API=duckduckgo

# ===================================
# LLM 配置
# ===================================
LLM_PROVIDER=custom
LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_TIMEOUT=120

# ===================================
# 研究配置
# ===================================
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True
LOG_LEVEL=INFO

# ===================================
# 服务器配置
# ===================================
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

---

## 📊 搜索引擎对比

| 搜索引擎 | 免费额度 | 质量 | 稳定性 | 限流风险 | 推荐度 |
|---------|---------|------|--------|---------|--------|
| **Tavily** | 1000次/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 无 | ⭐⭐⭐⭐⭐ |
| DuckDuckGo | 无限 | ⭐⭐⭐ | ⭐⭐ | ✅ 有 | ⭐⭐ |
| Perplexity | 付费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ 无 | ⭐⭐⭐⭐ |

---

## 🔧 快速修复步骤

### 如果您现在就想使用系统

**选择 A: 使用 Tavily (5分钟配置)**

1. 访问 https://tavily.com 注册
2. 获取 API Key
3. 修改 `backend/.env`:
   ```ini
   SEARCH_API=tavily
   TAVILY_API_KEY=tvly-xxxxxxxxxx
   ```
4. 重启后端服务
5. 立即可用 ✅

**选择 B: 等待恢复 (30分钟)**

1. 停止测试
2. 等待 30 分钟
3. 重新尝试（仍使用 DuckDuckGo）
4. 可能再次限流 ⚠️

---

## 💡 预防措施

### 1. 控制请求频率

**当前配置**:
```ini
MAX_WEB_RESEARCH_LOOPS=3  # 每个任务最多3次搜索
```

**优化建议**:
```ini
# 减少搜索次数（降低限流风险）
MAX_WEB_RESEARCH_LOOPS=2

# 或者使用 Tavily（无限流风险）
SEARCH_API=tavily
```

### 2. 分散测试时间

- ❌ 不要连续执行多个研究任务
- ✅ 每次测试间隔 2-3 分钟
- ✅ 避免短时间内大量请求

### 3. 使用更可靠的搜索引擎

**Tavily 是最佳选择**:
- 专为 AI 应用设计
- 免费额度足够日常使用
- 不会被限流

---

## 📝 Tavily API 注册指南

### 步骤详解

1. **访问官网**
   ```
   https://tavily.com
   ```

2. **注册账号**
   - 点击 "Sign Up"
   - 使用 Google/GitHub 账号或邮箱注册

3. **获取 API Key**
   - 登录后进入 Dashboard
   - 找到 "API Keys" 部分
   - 复制 API Key (格式: `tvly-xxxxxxxxxx`)

4. **查看额度**
   - 免费版: 1000 次/月
   - 足够日常研究使用

5. **配置到项目**
   ```ini
   # backend/.env
   SEARCH_API=tavily
   TAVILY_API_KEY=tvly-xxxxxxxxxx
   ```

---

## 🧪 测试验证

### 测试搜索是否正常

创建测试文件 `test_search.py`:

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

search_api = os.getenv('SEARCH_API', 'duckduckgo')
tavily_key = os.getenv('TAVILY_API_KEY')

print(f"搜索引擎: {search_api}")
print(f"Tavily API: {'已配置' if tavily_key else '未配置'}")

if search_api == 'tavily':
    if tavily_key:
        print("✅ 配置正确，可以使用 Tavily 搜索")
    else:
        print("❌ 请配置 TAVILY_API_KEY")
elif search_api == 'duckduckgo':
    print("⚠️  使用 DuckDuckGo，可能被限流")
```

运行测试:
```bash
cd C:\Users\frankechen\CFP-Study\Task06
python test_search.py
```

---

## ❓ 常见问题

### Q1: Tavily 免费额度够用吗？

**A**: 足够！
- 免费额度: 1000 次/月
- 每次研究: 约 4-5 次搜索
- 可以进行: 200+ 次研究
- 日常使用完全够用

### Q2: DuckDuckGo 什么时候会恢复？

**A**: 通常 15-30 分钟
- 限流是临时的
- 但可能再次被限流
- 不推荐作为主要方案

### Q3: 可以同时配置多个搜索引擎吗？

**A**: 可以，但只能使用一个
```ini
SEARCH_API=tavily  # 主要使用 Tavily

# 备用配置（注释掉）
# SEARCH_API=duckduckgo
```

### Q4: 如何知道是否被限流了？

**A**: 看日志
```
ERROR: DuckDuckGo 搜索失败: No results found.
```
如果看到这个错误，就是被限流了。

---

## 📚 相关资源

### 官方文档
- [Tavily 官网](https://tavily.com)
- [Tavily API 文档](https://docs.tavily.com)
- [DuckDuckGo API](https://duckduckgo.com/api)

### 项目文档
- `如何使用DeepResearch-完整指南.md` - 完整使用指南
- `第14章-实战测试总结.md` - 测试经验总结
- `第14章-深入学习总结.md` - 代码深度分析

---

## ✅ 解决方案总结

### 推荐方案（按优先级）

1. **⭐⭐⭐⭐⭐ 使用 Tavily** (5分钟配置，永久解决)
   - 质量高、稳定、不限流
   - 免费额度充足

2. **⭐⭐ 等待 DuckDuckGo 恢复** (30分钟等待)
   - 无需配置
   - 但可能再次限流

3. **⭐⭐⭐⭐ 使用 Perplexity** (付费方案)
   - 质量最高
   - 需要付费

### 最佳实践

```ini
# 推荐配置
SEARCH_API=tavily
TAVILY_API_KEY=tvly-your-key
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True
```

---

**创建时间**: 2025-12-27  
**问题状态**: ✅ 有完整解决方案  
**推荐方案**: 使用 Tavily API

🎯 **立即行动**: 注册 Tavily API，5分钟解决问题！
