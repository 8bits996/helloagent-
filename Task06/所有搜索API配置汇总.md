# 搜索 API 配置汇总

**更新日期**: 2025-12-27  
**状态**: 已配置 Tavily（推荐使用）

---

## 📋 您拥有的 API Keys

### 1. ✅ Tavily API (已配置，正在使用)

**API Key**: `YOUR_TAVILY_API_KEY_HERE`  
**状态**: ✅ 已配置并运行成功  
**免费额度**: 1000次/月  
**优点**: 
- 专为 AI 应用优化
- 搜索质量高
- 稳定不限流
- 支持中英文

**配置方式**:
```powershell
# 启动后端时设置环境变量
$env:SEARCH_API="tavily"
$env:TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
```

---

### 2. ⚠️ SERPER API (暂不支持)

**API Key**: `YOUR_SERPER_API_KEY_HERE`  
**状态**: ⚠️ 当前代码版本不支持  
**说明**: Google Search API 提供商

**可能的配置方式** (如果支持):
```ini
# backend/.env
SEARCH_API=serper
SERPER_API_KEY=YOUR_SERPER_API_KEY_HERE
```

**替代方案**: 使用 Tavily (已支持且效果很好)

---

### 3. ⚠️ Metaso API (暂不支持)

**官网**: https://metaso.cn/  
**API Key**: `YOUR_METASO_API_KEY_HERE`  
**状态**: ⚠️ 当前代码版本不支持  
**说明**: 中文优化的搜索引擎

**特点**:
- 专注中文搜索
- 可能对中文内容搜索效果更好

**可能的配置方式** (如果支持):
```ini
# backend/.env
SEARCH_API=metaso
METASO_API_KEY=YOUR_METASO_API_KEY_HERE
```

**替代方案**: 使用 Tavily (支持中文搜索)

---

## 🎯 当前推荐配置

### 最佳方案: 使用 Tavily ⭐⭐⭐⭐⭐

**原因**:
1. ✅ 已经配置成功并测试通过
2. ✅ 搜索质量高，找到大量真实来源
3. ✅ 支持中英文搜索
4. ✅ 免费额度充足（1000次/月）
5. ✅ 稳定可靠，不会被限流

**使用方法**:

1. **使用启动脚本** (推荐):
   ```powershell
   # 双击运行
   Task06\启动后端-带Tavily.ps1
   ```

2. **手动启动**:
   ```powershell
   $env:SEARCH_API="tavily"
   $env:TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
   cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\backend
   python src\main.py
   ```

---

## 🔧 如何添加新的搜索引擎支持

如果您想使用 SERPER 或 Metaso，需要修改代码。以下是可能的方法：

### 方法 1: 修改 hello_agents 包 (复杂)

需要修改 `hello_agents` 包的源代码，添加新的搜索引擎支持。

### 方法 2: 使用 MCP Server (推荐)

Metaso 可能提供 MCP Server 支持，可以通过 MCP 协议集成。

**步骤**:
1. 查看 Metaso 官方文档是否提供 MCP Server
2. 如果有，安装对应的 MCP Server
3. 配置 MCP settings
4. 在代码中启用 MCP 工具

### 方法 3: 等待官方更新

等待 `hello_agents` 包更新，支持更多搜索引擎。

---

## 📊 搜索引擎对比

| 搜索引擎 | 支持状态 | 免费额度 | 中文支持 | 质量 | 推荐度 |
|---------|---------|---------|---------|------|--------|
| **Tavily** | ✅ 已配置 | 1000次/月 | ✅ 很好 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DuckDuckGo | ✅ 支持 | 无限（限流） | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| SERPER | ❌ 不支持 | - | ✅ 好 | ⭐⭐⭐⭐ | - |
| Metaso | ❌ 不支持 | - | ✅ 很好 | ？ | - |
| Perplexity | ✅ 支持 | 付费 | ✅ 很好 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 💡 实用建议

### 当前最佳实践

1. **主要使用 Tavily**
   - 已配置成功
   - 搜索质量高
   - 免费额度充足
   - 中英文都支持

2. **保留其他 API Keys**
   - SERPER 和 Metaso 的 Keys 保存好
   - 等待官方支持或社区插件

3. **监控使用量**
   - Tavily 每月 1000 次
   - 平均每次研究 4-8 次搜索
   - 可以进行 125-250 次研究

### 如果需要中文优化

虽然 Metaso 暂不支持，但 Tavily 对中文搜索效果也很好：

**测试建议**:
```python
# 尝试中文主题
主题 = "大语言模型在中国的发展"
主题 = "人工智能医疗应用案例"
主题 = "2025年中国AI产业趋势"
```

---

## 🔗 相关资源

### API 官方文档

1. **Tavily**
   - 官网: https://tavily.com
   - 文档: https://docs.tavily.com
   - 免费额度: 1000次/月

2. **SERPER**
   - 官网: https://serper.dev
   - 说明: Google Search API

3. **Metaso**
   - 官网: https://metaso.cn
   - 说明: 中文搜索引擎

### Hello Agents 文档

- GitHub: https://github.com/datawhalechina/hello-agents
- 搜索工具文档: 查看源码中的 `search_tool.py`

---

## 📝 配置文件示例

### 当前工作配置 (backend/.env)

```ini
# ========================================
# 搜索引擎配置 (当前使用 Tavily)
# ========================================
SEARCH_API=tavily
TAVILY_API_KEY=YOUR_TAVILY_API_KEY_HERE

# 备用配置 (暂不支持)
# SERPER_API_KEY=YOUR_SERPER_API_KEY_HERE
# METASO_API_KEY=YOUR_METASO_API_KEY_HERE

# ========================================
# LLM 配置
# ========================================
LLM_PROVIDER=custom
LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
LLM_API_KEY=YOUR_LLM_API_KEY_HERE
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_TIMEOUT=180

# ========================================
# 研究配置
# ========================================
MAX_WEB_RESEARCH_LOOPS=2
FETCH_FULL_PAGE=False
LOG_LEVEL=DEBUG

# ========================================
# 服务器配置
# ========================================
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

---

## ✅ 快速检查清单

### 验证 Tavily 配置

```powershell
# 1. 检查环境变量
$env:SEARCH_API
$env:TAVILY_API_KEY

# 2. 测试配置
cd C:\Users\frankechen\CFP-Study\Task06
python test_tavily_config.py

# 3. 运行研究测试
python test_research_simple.py
```

### 查看后端日志

启动后端时应该看到:
```
✅ Tavily 搜索引擎已初始化
🔧 混合搜索模式已启用，可用后端: tavily
```

---

## 🎯 总结

### 当前状态

✅ **Tavily API 已配置并运行成功**
- 搜索质量高
- 找到大量真实来源
- 中英文都支持
- 稳定可靠

⚠️ **SERPER 和 Metaso 暂不支持**
- API Keys 已记录
- 等待官方支持
- 或考虑自行开发插件

### 建议

**继续使用 Tavily**，它已经完美工作，质量很好！

**保存好所有 API Keys**，以备将来使用。

**监控 hello_agents 项目更新**，可能会添加更多搜索引擎支持。

---

## 📞 如果需要支持 Metaso

### 可能的解决方案

1. **联系 Metaso 官方**
   - 询问是否有 Python SDK
   - 询问是否支持 MCP Server

2. **查看 hello_agents 社区**
   - 提交 Feature Request
   - 查看是否有社区插件

3. **自行开发插件**
   - 参考 `search_tool.py` 源码
   - 添加 Metaso 支持
   - 贡献回社区

---

**最后更新**: 2025-12-27  
**配置状态**: ✅ Tavily 完美运行  
**建议**: 继续使用 Tavily，效果很好！
