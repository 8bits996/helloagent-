# DeepResearch Agent 使用完整指南

**更新日期**: 2025-12-27  
**状态**: ✅ 服务运行中

---

## 🚀 快速开始

### 当前服务状态

✅ **后端服务**: http://localhost:8000 (运行中)  
✅ **前端服务**: http://localhost:5174 (运行中)  
✅ **API 文档**: http://localhost:8000/docs

---

## 📱 使用方式

### 方式 1: 网页界面 (推荐)

**步骤**:
1. 打开浏览器
2. 访问 `http://localhost:5174`
3. 在输入框输入研究主题
4. 点击"开始研究"按钮
5. 观察实时进度
6. 查看最终报告

**示例主题**:
```
✅ 适合的主题:
- "2025年人工智能的最新突破"
- "量子计算在密码学中的应用"
- "大语言模型 Agent 的发展趋势"
- "Python 3.14 的新特性"
- "区块链技术在金融领域的应用"

❌ 不适合的主题:
- 过于宽泛: "科技发展"
- 过于简单: "什么是AI"
- 无时效性: "牛顿定律"
```

---

### 方式 2: Python 脚本调用

**测试脚本**: `test_research_simple.py`

```python
# 运行脚本
cd C:\Users\frankechen\CFP-Study\Task06
python test_research_simple.py
```

**自定义主题**:
```python
# 编辑 test_research_simple.py
topic = "你的研究主题"  # 修改这行
```

---

### 方式 3: API 直接调用

**使用 curl**:
```bash
curl -X POST "http://localhost:8000/research/stream" \
  -H "Content-Type: application/json" \
  -d '{"topic": "人工智能的发展趋势"}' \
  --no-buffer
```

**使用 Python requests**:
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/research/stream",
    json={"topic": "你的研究主题"},
    stream=True
)

for line in response.iter_lines():
    if line and line.startswith(b'data: '):
        data = json.loads(line[6:])
        print(data)
```

---

## 🔧 服务管理

### 启动服务

**后端**:
```bash
cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\backend
python src\main.py
```

**前端**:
```bash
cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\frontend
npm run dev
```

### 停止服务

**方法 1: Ctrl+C**
- 在运行服务的终端窗口按 `Ctrl+C`

**方法 2: 关闭终端窗口**
- 直接关闭运行服务的终端

**方法 3: 任务管理器**
- 打开任务管理器
- 找到 `python.exe` 和 `node.exe` 进程
- 结束进程

### 查看日志

**后端日志**:
- 在后端终端窗口查看实时日志
- 日志包含请求信息、LLM 调用、搜索结果等

**前端日志**:
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签
- 可以看到事件接收和处理日志

---

## ⚙️ 配置优化

### 配置文件位置
```
backend/.env
```

### 常用配置

#### 1. 搜索引擎配置

**使用 DuckDuckGo (免费)**:
```ini
SEARCH_API=duckduckgo
```

**使用 Tavily (高质量)**:
```ini
SEARCH_API=tavily
TAVILY_API_KEY=tvly-your-api-key
```

#### 2. LLM 模型配置

**使用更大的模型 (更好的质量)**:
```ini
LLM_MODEL_ID=Qwen/Qwen2.5-14B-Instruct
```

**使用更小的模型 (更快的速度)**:
```ini
LLM_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
```

#### 3. 研究深度配置

**更深入的研究**:
```ini
MAX_WEB_RESEARCH_LOOPS=5
FETCH_FULL_PAGE=True
```

**更快的研究**:
```ini
MAX_WEB_RESEARCH_LOOPS=2
FETCH_FULL_PAGE=False
```

#### 4. 超时配置

**增加超时时间 (如果 LLM 响应慢)**:
```ini
LLM_TIMEOUT=180
```

---

## 📊 理解输出

### 研究过程

```
1. 初始化 (0-2秒)
   💬 初始化研究流程

2. 规划阶段 (2-5秒)
   📋 生成 3-5 个研究任务
   例如:
   - 任务1: 背景梳理
   - 任务2: 技术趋势
   - 任务3: 应用领域
   - 任务4: 竞争格局

3. 执行阶段 (5-40秒) - 并行
   🔄 任务1 开始执行...
   🔄 任务2 开始执行...
   🔄 任务3 开始执行...
   🔄 任务4 开始执行...
   
   对每个任务:
   🔗 搜索相关资料
   📝 生成任务总结
   ✅ 任务完成

4. 报告阶段 (40-50秒)
   📄 整合所有任务结果
   📄 生成最终研究报告

5. 完成 (50秒)
   🎉 研究完成!
```

### 报告结构

生成的报告通常包含：

```markdown
# 研究主题

## 背景概览
概述研究主题的背景和重要性

## 核心洞见
1. 关键发现1
2. 关键发现2
3. 关键发现3

## 证据与数据
- 具体的证据和数据支撑
- 引用的案例和例子

## 风险与挑战
- 技术挑战
- 市场挑战
- 应用挑战

## 参考来源
- 列出各任务的贡献

## 研究总结
- 总结和展望
```

---

## 🐛 常见问题

### 问题 1: 后端无法启动

**症状**: `ModuleNotFoundError` 或其他依赖错误

**解决**:
```bash
cd backend
pip install -r requirements.txt
pip install huggingface_hub
```

### 问题 2: 前端无法访问后端

**症状**: CORS 错误

**解决**:
检查 `backend/.env` 中的 CORS 配置:
```ini
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### 问题 3: 研究结果质量差

**原因**: 使用 DuckDuckGo 搜索质量有限

**解决**:
1. 注册 Tavily API (免费): https://tavily.com
2. 配置 API Key:
   ```ini
   SEARCH_API=tavily
   TAVILY_API_KEY=tvly-your-key
   ```

### 问题 4: LLM 响应超时

**症状**: 请求超时或连接中断

**解决**:
```ini
# 增加超时时间
LLM_TIMEOUT=180

# 或使用更稳定的模型
LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
```

### 问题 5: 研究主题没有结果

**原因**: 主题过于专业或搜索引擎找不到相关内容

**解决**:
1. 使用更通用的关键词
2. 尝试换个角度描述主题
3. 使用 Tavily 搜索引擎

---

## 💡 使用技巧

### 1. 最佳实践

**好的主题特征**:
- ✅ 明确具体: "2025年 LLM 的新突破"
- ✅ 有时效性: "最新的 AI Agent 技术"
- ✅ 适度范围: 不太宽泛也不太窄
- ✅ 可搜索性: 能在网上找到相关资料

**示例对比**:
```
❌ 不好: "AI"
✅ 好: "大语言模型在医疗诊断中的应用"

❌ 不好: "Python"
✅ 好: "Python 3.14 新特性详解"

❌ 不好: "技术发展"
✅ 好: "量子计算技术在2025年的突破"
```

### 2. 进阶使用

**组合查询**:
```
主题: "比较 GPT-4 和 Claude 3 在代码生成能力上的差异"
```

**趋势分析**:
```
主题: "过去5年人工智能技术的演进路径"
```

**应用研究**:
```
主题: "AI Agent 在企业客服中的实际应用案例分析"
```

### 3. 结果优化

**如果报告太简略**:
```ini
# 增加研究循环
MAX_WEB_RESEARCH_LOOPS=5

# 获取完整页面
FETCH_FULL_PAGE=True

# 使用更大的模型
LLM_MODEL_ID=Qwen/Qwen2.5-14B-Instruct
```

**如果报告太慢**:
```ini
# 减少研究循环
MAX_WEB_RESEARCH_LOOPS=2

# 只获取摘要
FETCH_FULL_PAGE=False

# 使用更小的模型
LLM_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
```

---

## 📈 性能基准

### 典型性能指标

| 配置 | 耗时 | 报告质量 | 成本 |
|------|------|---------|------|
| 快速模式 | 15-20秒 | ⭐⭐⭐ | 低 |
| 标准模式 | 25-35秒 | ⭐⭐⭐⭐ | 中 |
| 深度模式 | 40-60秒 | ⭐⭐⭐⭐⭐ | 高 |

**快速模式**:
```ini
SEARCH_API=duckduckgo
LLM_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
MAX_WEB_RESEARCH_LOOPS=2
FETCH_FULL_PAGE=False
```

**标准模式** (当前配置):
```ini
SEARCH_API=duckduckgo
LLM_MODEL_ID=Qwen/Qwen2.5-7B-Instruct
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True
```

**深度模式**:
```ini
SEARCH_API=tavily
LLM_MODEL_ID=Qwen/Qwen2.5-14B-Instruct
MAX_WEB_RESEARCH_LOOPS=5
FETCH_FULL_PAGE=True
```

---

## 🎯 应用场景

### 1. 学习研究

**场景**: 学习新技术或概念

**主题示例**:
- "Rust 语言的所有权系统详解"
- "微服务架构的设计模式"
- "React 18 并发特性原理"

**价值**: 快速了解技术背景、核心概念和应用

### 2. 技术选型

**场景**: 评估技术方案

**主题示例**:
- "2025年主流前端框架对比分析"
- "NoSQL 数据库选型指南"
- "云原生部署方案比较"

**价值**: 获得多维度的对比分析

### 3. 市场调研

**场景**: 了解市场和竞品

**主题示例**:
- "AI Agent 市场竞争格局分析"
- "低代码平台的发展趋势"
- "智能客服解决方案对比"

**价值**: 快速获得市场洞察

### 4. 问题排查

**场景**: 查找问题解决方案

**主题示例**:
- "Docker 容器内存溢出问题排查"
- "PostgreSQL 性能优化最佳实践"
- "React 性能瓶颈分析方法"

**价值**: 整合多个来源的解决方案

---

## 📚 相关资源

### 官方文档
- [HelloAgents 课程](https://datawhalechina.github.io/hello-agents)
- [第14章官方文档](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/)
- [官方代码仓库](https://github.com/datawhalechina/hello-agents/tree/main/code/chapter14)

### 学习笔记
- `第14章-深入学习总结.md` - 代码深度分析
- `第14章-实战测试总结.md` - 实战测试报告
- `第14章配置完成总结.md` - 环境配置指南

### 测试脚本
- `test_research_simple.py` - 简单测试脚本
- `test_backend_api.py` - API 测试脚本

---

## ⚠️ 注意事项

### 1. API 成本

- LLM API 调用有成本，建议监控使用量
- Tavily 免费版有调用次数限制
- 合理设置研究循环次数

### 2. 网络要求

- 需要稳定的网络连接
- 搜索引擎可能有地区限制
- LLM API 服务器在海外可能较慢

### 3. 内容质量

- AI 生成的内容需要人工验证
- 引用来源可能不完全准确
- 专业领域建议咨询专家

### 4. 隐私安全

- 不要输入敏感信息
- 研究主题会发送到 LLM API
- 搜索内容会记录在日志中

---

## 🔄 更新日志

### 2025-12-27
- ✅ 修复了 `.env` 文件加载问题
- ✅ 禁用了自动重载提高稳定性
- ✅ 完成了实战测试验证
- ✅ 创建了完整使用指南

---

## 📞 获取帮助

### 遇到问题？

1. 查看本指南的"常见问题"部分
2. 查看后端日志排查错误
3. 查看浏览器控制台的错误信息
4. 查阅官方文档和 GitHub Issues

### 反馈建议

- GitHub: https://github.com/datawhalechina/hello-agents/issues
- 官方社区: Datawhale 学习社区

---

**最后更新**: 2025-12-27  
**版本**: v1.0  
**状态**: ✅ 生产就绪

🎉 享受你的 AI 研究助手之旅！
