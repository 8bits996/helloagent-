# 快速开始 - 第13章实践环境

> 3 步启动智能旅行助手，开始您的学习之旅！

## 🎯 概览

您已经成功克隆了官方代码！现在只需三步即可启动完整的智能旅行助手系统。

**您将启动**：
- ✅ FastAPI 后端服务 (端口 8000)
- ✅ Vue3 前端应用 (端口 5173)
- ✅ 完整的 AI 旅行规划功能

---

## 📋 启动前检查

### 必需环境

在开始之前，请确认：

```powershell
# 检查 Python (需要 3.10+)
python --version

# 检查 Node.js (需要 16+)
node --version

# 检查 npm
npm --version
```

如果任何命令失败，请参考 [环境配置指南.md](./环境配置指南.md) 安装相应环境。

### 必需 API 密钥

⚠️ **启动服务前，您需要准备以下 API 密钥**：

| API | 必需性 | 用途 | 申请地址 |
|-----|--------|------|---------|
| 高德地图 Web服务 Key | ⭐⭐⭐ 必需 | 后端 MCP 工具调用 | https://lbs.amap.com/ |
| 高德地图 JavaScript Key | ⭐⭐⭐ 必需 | 前端地图显示 | https://lbs.amap.com/ |
| LLM API Key | ⭐⭐⭐ 必需 | AI 智能体（推荐 DeepSeek） | https://platform.deepseek.com/ |
| Unsplash API | ⭐ 可选 | 景点图片 | https://unsplash.com/developers |

**详细申请步骤**请参考：[环境配置指南.md - API密钥准备章节](./环境配置指南.md#-api-密钥准备)

---

## 🚀 三步启动

### 方法一：一键启动（推荐）

**最简单的方式！一个命令启动全部服务。**

```powershell
# 右键点击 "一键启动全部.ps1"，选择 "使用 PowerShell 运行"
# 或在 PowerShell 中执行：
cd C:\Users\frankechen\CFP-Study\Task06\实践环境
.\一键启动全部.ps1
```

**脚本将自动**：
1. ✅ 检查环境
2. ✅ 创建虚拟环境（如需要）
3. ✅ 安装依赖（如需要）
4. ✅ 检查配置文件
5. ✅ 在两个新窗口中启动后端和前端
6. ✅ 打开浏览器访问应用

**首次运行**可能需要 3-5 分钟安装依赖。

---

### 方法二：分步启动

如果您想更好地控制启动过程，可以分别启动后端和前端。

#### Step 1: 启动后端

**打开第一个 PowerShell 窗口**：

```powershell
# 方式 1: 使用启动脚本（推荐）
cd C:\Users\frankechen\CFP-Study\Task06\实践环境
.\启动后端.ps1
```

或者

```powershell
# 方式 2: 手动启动
cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter13\helloagents-trip-planner\backend

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 启动服务
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

**看到这样的输出说明成功**：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**验证后端**：访问 http://localhost:8000/docs

---

#### Step 2: 启动前端

**打开第二个 PowerShell 窗口**（保持后端窗口运行）：

```powershell
# 方式 1: 使用启动脚本（推荐）
cd C:\Users\frankechen\CFP-Study\Task06\实践环境
.\启动前端.ps1
```

或者

```powershell
# 方式 2: 手动启动
cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter13\helloagents-trip-planner\frontend

# 启动服务
npm run dev
```

**看到这样的输出说明成功**：
```
VITE v6.0.7  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

**验证前端**：访问 http://localhost:5173

---

#### Step 3: 体验功能

打开浏览器访问 http://localhost:5173，您应该看到智能旅行助手的界面。

**试试这个示例请求**：
- 目的地：北京
- 旅行天数：3天
- 出发日期：选择未来的日期
- 交通方式：公共交通
- 住宿偏好：经济型
- 旅行风格：文化探索、美食体验

点击"生成旅行计划"，等待 AI 为您生成个性化行程！

---

## 🛠️ 首次运行配置

### 后端配置（backend/.env）

**首次运行时**，启动脚本会自动复制 `.env.example` 到 `.env`。

您需要编辑 `.env` 文件，填入以下必需配置：

```env
# ============================================
# LLM 配置（必需）
# ============================================
LLM_MODEL_ID=deepseek-chat
LLM_API_KEY=sk-你的DeepSeek密钥
LLM_BASE_URL=https://api.deepseek.com/v1

# ============================================
# 高德地图 API 配置（必需）
# ============================================
AMAP_API_KEY=你的高德Web服务密钥

# ============================================
# Unsplash API 配置（可选）
# ============================================
UNSPLASH_ACCESS_KEY=你的Unsplash密钥
UNSPLASH_SECRET_KEY=你的Unsplash密钥
```

### 前端配置（frontend/.env）

```env
# 高德地图 Web 端 JavaScript API Key（必需）
VITE_AMAP_WEB_KEY=你的高德JavaScript密钥

# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📁 项目结构速览

```
official-code/code/chapter13/helloagents-trip-planner/
│
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── agents/                  # AI 智能体
│   │   │   └── trip_planner_agent.py    # 旅行规划智能体
│   │   ├── api/                     # FastAPI 路由
│   │   │   └── routes/
│   │   │       ├── trip.py         # 旅行规划接口
│   │   │       └── map.py          # 地图服务接口
│   │   ├── services/                # 业务逻辑
│   │   │   ├── amap_service.py     # 高德地图服务
│   │   │   └── llm_service.py      # LLM 服务
│   │   └── models/                  # 数据模型
│   │       └── schemas.py          # Pydantic 模型
│   ├── .env                         # 环境配置（需自己创建）
│   └── requirements.txt             # Python 依赖
│
└── frontend/                         # 前端应用
    ├── src/
    │   ├── views/                   # 页面视图
    │   │   ├── Home.vue            # 首页
    │   │   └── Result.vue          # 结果页
    │   ├── services/                # API 服务
    │   │   └── api.ts              # HTTP 请求封装
    │   └── types/                   # TypeScript 类型
    │       └── index.ts            # 类型定义
    ├── .env                         # 环境配置（需自己创建）
    └── package.json                 # npm 依赖
```

---

## 🔍 验证服务运行

### 后端健康检查

```powershell
# 使用 curl 或浏览器访问
curl http://localhost:8000/health

# 或打开浏览器访问
# http://localhost:8000/docs
```

**预期响应**：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 前端访问测试

在浏览器中访问：
- **前端首页**：http://localhost:5173
- **API 文档**：http://localhost:8000/docs

---

## ⚠️ 常见问题

### 1. PowerShell 脚本无法运行

**错误**：
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Python 虚拟环境创建失败

**解决**：
```powershell
# 确保 Python 版本 >= 3.10
python --version

# 手动创建虚拟环境
cd backend
python -m venv venv
```

### 3. 后端启动报错：找不到模块

**解决**：
```powershell
# 确保在 backend 目录
cd backend

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 重新安装依赖
pip install -r requirements.txt
```

### 4. npm 安装依赖很慢

**解决**：
```powershell
# 切换到国内镜像
npm config set registry https://registry.npmmirror.com

# 清除缓存
npm cache clean --force

# 重新安装
npm install
```

### 5. 前端地图不显示

**可能原因**：
- 高德地图 JavaScript API Key 未配置
- Key 绑定的域名不包含 localhost

**解决**：
1. 检查 `frontend/.env` 中的 `VITE_AMAP_WEB_KEY`
2. 在高德开放平台控制台，将 Key 的绑定域名设置为 `localhost`

### 6. AI 生成失败

**可能原因**：
- LLM API Key 错误或未配置
- 高德地图 API Key 错误
- API 调用额度用完

**解决**：
1. 检查 `backend/.env` 中的 API 密钥配置
2. 查看后端日志中的详细错误信息
3. 访问对应平台查看 API 调用额度

---

## 📚 下一步

### 学习路径

1. ✅ **运行官方代码**（您现在在这里）
   - 体验完整功能
   - 了解项目结构

2. 📖 **学习理论知识**
   - 阅读 [第13章官方学习指南](../学习笔记/第13章-智能旅行助手-官方学习指南.md)
   - 理解多智能体协作设计
   - 学习 MCP 工具集成

3. 🔍 **阅读源码**
   - 从智能体实现开始：`backend/app/agents/trip_planner_agent.py`
   - 理解 MCP 工具调用：`backend/app/services/amap_service.py`
   - 学习前端实现：`frontend/src/views/`

4. 🛠️ **动手实践**
   - 修改 prompt，观察行为变化
   - 添加新的 MCP 工具
   - 扩展功能（如餐厅推荐）

### 推荐阅读

- [环境配置指南](./环境配置指南.md) - 详细的环境搭建教程
- [官方文档](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/第十三章%20智能旅行助手.md) - 完整的章节内容
- [官方资源索引](../官方资源索引.md) - 所有相关资源链接

---

## 💡 使用技巧

### 调试技巧

1. **查看后端日志**
   - 后端窗口会实时显示 API 请求和错误信息
   - 使用 `LOG_LEVEL=DEBUG` 获取更详细的日志

2. **使用 API 文档测试**
   - 访问 http://localhost:8000/docs
   - 可以直接在浏览器中测试 API 接口

3. **浏览器开发者工具**
   - 按 F12 打开开发者工具
   - 在 Console 标签查看前端错误
   - 在 Network 标签查看 HTTP 请求

### 性能优化

1. **缓存机制**
   - 项目已实现基本的缓存
   - 重复查询相同景点会更快

2. **并发请求**
   - 多个 MCP 工具可以并发调用
   - 减少总体响应时间

---

## 🎉 开始使用

一切准备就绪！现在：

1. 运行启动脚本
2. 打开浏览器访问 http://localhost:5173
3. 输入您的梦想旅行目的地
4. 让 AI 为您生成个性化行程！

**祝您学习愉快！** 🚀

---

## 📞 需要帮助？

- 📖 查看详细配置：[环境配置指南.md](./环境配置指南.md)
- 🐛 常见问题：[环境配置指南.md - 常见问题排查](./环境配置指南.md#-常见问题排查)
- 💬 官方 Issues：https://github.com/datawhalechina/hello-agents/issues

---

**HelloAgents 智能旅行助手** - 让学习变得简单而有趣 ✨
