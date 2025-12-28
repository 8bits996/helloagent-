# DeepResearch Agent - 快速启动指南

**创建日期**: 2025-12-26  
**状态**: ✅ 已配置完成

---

## 🎯 项目简介

DeepResearch Agent 是一个自动化深度研究智能体，能够：
- 📚 将研究主题分解为多个子任务
- 🔍 自动搜索和收集信息
- 📝 生成结构化的研究报告
- 🔗 提供可追溯的来源引用

**技术特点**:
- TODO 驱动的研究范式
- 顺序协作的 Agent 设计
- 支持多种搜索引擎（DuckDuckGo/Tavily/Perplexity/SearXNG）
- SSE 实时推送研究进度

---

## ✅ 环境配置完成

### 后端配置
- ✅ Python 依赖已安装
- ✅ 环境变量已配置 (`.env`)
- ✅ LLM: Qwen/Qwen2.5-7B-Instruct (硅基流动)
- ✅ 搜索引擎: DuckDuckGo (免费) + Tavily (可选)

### 前端配置
- ⚠️ 需要安装依赖 (npm install)

---

## 🚀 快速启动

### 方式1: 使用启动脚本 (推荐)

#### 启动后端
```powershell
# 在项目根目录双击或运行:
.\启动后端.ps1
```

后端服务将启动在: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 方式2: 手动启动

#### 启动后端
```powershell
# 进入后端目录
cd backend

# 启动服务
python src\main.py
```

#### 启动前端
```powershell
# 进入前端目录
cd frontend

# 安装依赖 (首次运行)
npm install

# 启动开发服务器
npm run dev
```

前端访问地址: http://localhost:5174

---

## 📊 服务状态

### 后端服务
```
✅ 状态: 运行中
🌐 地址: http://0.0.0.0:8000
🔍 搜索: DuckDuckGo + Tavily
🤖 模型: Qwen/Qwen2.5-7B-Instruct
📝 日志: INFO 级别
```

### 配置信息
```ini
# 搜索引擎
SEARCH_API=duckduckgo          # 主要使用 DuckDuckGo (免费)
TAVILY_API_KEY=配置完成         # Tavily 作为备用

# LLM 配置
LLM_PROVIDER=custom            # 自定义 API
LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
LLM_BASE_URL=https://api.siliconflow.cn/v1

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 研究配置
MAX_WEB_RESEARCH_LOOPS=3       # 最多 3 轮研究
FETCH_FULL_PAGE=True           # 获取完整页面内容
```

---

## 🎮 使用方法

### 1. 访问前端界面
打开浏览器访问: http://localhost:5174

### 2. 输入研究主题
例如:
- "量子计算的最新进展"
- "人工智能在医疗领域的应用"
- "区块链技术的发展趋势"

### 3. 观察研究过程
系统会实时显示:
- 🔍 规划阶段: 分解子任务
- 📊 执行阶段: 搜索和总结
- 📝 报告阶段: 生成研究报告

### 4. 查看研究报告
- 自动生成 Markdown 格式报告
- 包含来源引用
- 支持导出和分享

---

## 🔧 配置说明

### 搜索引擎选择

1. **DuckDuckGo** (默认，免费)
   - 优点: 无需 API 密钥，隐私保护
   - 缺点: 结果质量一般
   - 适合: 初学者和测试

2. **Tavily** (推荐，已配置)
   - 优点: AI 优化，结果质量高
   - 缺点: 需要 API 密钥
   - 适合: 生产环境
   - 申请: https://tavily.com

3. **Perplexity** (可选)
   - 优点: AI 直接生成答案
   - 缺点: 需要付费 API
   - 申请: https://www.perplexity.ai

4. **SearXNG** (高级)
   - 优点: 自托管，完全可控
   - 缺点: 需要自己搭建
   - 适合: 企业级部署

### 切换搜索引擎

修改 `backend/.env` 文件:
```ini
# 使用 Tavily (更高质量)
SEARCH_API=tavily

# 使用 DuckDuckGo (免费)
SEARCH_API=duckduckgo

# 使用 Perplexity
SEARCH_API=perplexity

# 使用 SearXNG
SEARCH_API=searxng
SEARXNG_URL=http://localhost:8888
```

---

## 📝 日志查看

### 后端日志
后端服务会在控制台输出详细日志:
- 配置加载信息
- API 请求记录
- 工具调用过程
- 错误和警告信息

### 日志级别控制
修改 `backend/.env`:
```ini
LOG_LEVEL=INFO     # 正常日志
LOG_LEVEL=DEBUG    # 详细调试
LOG_LEVEL=WARNING  # 仅警告
LOG_LEVEL=ERROR    # 仅错误
```

---

## ⚠️ 常见问题

### 1. 后端启动失败

**问题**: `ModuleNotFoundError`
```bash
# 解决: 安装缺失的依赖
pip install -r requirements.txt
pip install huggingface_hub  # 如果仍然缺少
```

### 2. API 密钥错误

**问题**: `TAVILY_API_KEY 未设置`
```bash
# 解决: 检查 .env 文件
# 1. 确认文件存在: backend/.env
# 2. 检查密钥格式: TAVILY_API_KEY=tvly-xxxxx
# 3. 或者改用 DuckDuckGo: SEARCH_API=duckduckgo
```

### 3. 端口被占用

**问题**: `Address already in use`
```bash
# 解决1: 修改端口
# 编辑 backend/.env:
PORT=8001

# 解决2: 结束占用进程
netstat -ano | findstr :8000
taskkill /PID [进程ID] /F
```

### 4. 研究速度慢

**可能原因**:
- LLM API 响应慢
- 搜索引擎响应慢
- 子任务过多

**优化方法**:
```ini
# 减少研究循环次数
MAX_WEB_RESEARCH_LOOPS=2

# 使用更快的搜索引擎
SEARCH_API=tavily  # Tavily 通常更快

# 使用更快的 LLM 模型
# 如 Qwen2.5-1.5B 或 Qwen2.5-3B
```

---

## 📚 相关文档

### 学习资料
- `学习笔记/第14章-自动化深度研究智能体.md` - 详细学习笔记
- `学习笔记/第14章-自动化深度研究智能体-官方学习指南.md` - 分阶段学习路线

### 官方资源
- [官方文档](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/)
- [官方代码](https://github.com/datawhalechina/hello-agents/tree/main/code/chapter14)
- [HelloAgents 框架](https://github.com/datawhalechina/hello-agents)

---

## 🎯 下一步

### 1. 测试基本功能
- 启动服务
- 输入简单的研究主题
- 观察研究过程

### 2. 深入学习
- 阅读学习笔记
- 理解代码结构
- 尝试修改配置

### 3. 扩展功能
- 添加新的搜索引擎
- 优化 Prompt
- 改进报告格式

### 4. 实践应用
- 用于实际研究任务
- 整理研究成果
- 分享使用经验

---

## 💡 使用建议

### 研究主题选择
- ✅ 明确具体: "2025年量子计算硬件突破"
- ✅ 有时效性: "最新AI模型评测结果"
- ❌ 过于宽泛: "科技发展"
- ❌ 过于简单: "什么是AI"

### 结果优化
1. **提高质量**: 使用 Tavily 搜索引擎
2. **加快速度**: 减少 MAX_WEB_RESEARCH_LOOPS
3. **增加深度**: 设置 FETCH_FULL_PAGE=True
4. **改进报告**: 优化 Prompt 模板

---

## 🛠️ 技术支持

遇到问题？
1. 查看日志输出
2. 检查配置文件
3. 阅读学习笔记
4. 参考官方文档
5. 提交 Issue

---

**创建日期**: 2025-12-26  
**最后更新**: 2025-12-26  
**当前状态**: ✅ 后端运行中，前端待启动
