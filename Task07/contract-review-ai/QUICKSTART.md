# 快速开始指�?
## 📋 环境要求

- �?Python 3.10+ 已安�?- �?CodeBuddy CLI 已安�?- �?已复制知识库文件�?`知识�?` 目录

## 🚀 5分钟快速启�?
### 步骤1: 安装依赖

```bash
cd /path/to/contract-review-ai

# 安装Python依赖
pip install -r requirements.txt
```

### 步骤2: 配置环境

```bash
# 复制配置文件
copy .env.example .env

# （可选）编辑 .env 文件调整配置
```

### 步骤3: 测试MarkItDown

```bash
# 运行测试脚本
python test_markitdown.py
```

预期输出:
```
�?所有测试完�?```

### 步骤4: 启动服务

**打开3个终端窗口，分别运行:**

#### 终端1 - CodeBuddy Headless

```bash
codebuddy --serve --port 3000
```

等待输出:
```
Service endpoint: http://127.0.0.1:3000
```

#### 终端2 - FastAPI后端

```bash
cd /path/to/contract-review-ai
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

等待输出:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 终端3 - Streamlit前端 (开发中)

```bash
# 暂时跳过，Streamlit界面正在开发中
# streamlit run app/frontend.py
```

### 步骤5: 验证服务

打开浏览器访�?

- **FastAPI文档**: http://localhost:8000/docs
- **健康检�?*: http://localhost:8000/health

应该看到:
```json
{
  "status": "healthy",
  "services": {
    "fastapi": "ok",
    "codebuddy": "ok",
    "markitdown": "ok"
  }
}
```

## 🧪 测试API

### 使用Swagger UI测试

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/upload` 接口
3. 点击 "Try it out"
4. 上传测试文件（PDF、Word、Excel等）
5. 点击 "Execute"

### 使用curl测试

```bash
# 上传文件
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test.pdf"

# 响应示例:
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "files": ["test.pdf"],
#   "status": "parsing",
#   "message": "已上�?个文件，正在解析�?.."
# }

# 查询任务状�?curl "http://localhost:8000/api/status/{task_id}"

# 启动评审
curl -X POST "http://localhost:8000/api/review/{task_id}"

# 下载结果
curl "http://localhost:8000/api/report/{task_id}/result" -o result.json
```

## 📂 项目结构

```
contract-review-ai/
├── app/
�?  ├── services/
�?  �?  ├── document_parser.py  �?已完�?- MarkItDown集成
�?  �?  ├── codebuddy_client.py �?已完�?- CodeBuddy客户�?�?  �?  └── report_generator.py �?待开�?�?  ├── config.py               �?已完�?�?  ├── main.py                 �?已完�?- FastAPI主程�?�?  └── frontend.py             �?待开�?- Streamlit前端
├── 知识�?                     �?已复�?�?  ├── 主合同评审checklist.csv
�?  ├── 风险矩阵.csv
�?  └── ...
├── data/
�?  ├── uploads/                📁 自动创建
�?  └── outputs/                📁 自动创建
├── requirements.txt            �?已完�?├── .env.example                �?已完�?├── README.md                   �?已完�?└── test_markitdown.py          �?已完�?```

## 🎯 当前开发进�?
### �?已完�?(�?�?Day1-2)

- [x] 项目结构搭建
- [x] 环境配置文件
- [x] MarkItDown集成 (`document_parser.py`)
- [x] CodeBuddy客户�?(`codebuddy_client.py`)
- [x] FastAPI基础框架 (`main.py`)
- [x] 文件上传API
- [x] 文件解析API
- [x] 评审启动API
- [x] 测试脚本 (`test_markitdown.py`)
- [x] 知识库文件复�?
### �?进行�?(�?�?Day3-4)

- [ ] MarkItDown全格式测�?- [ ] FastAPI完整测试
- [ ] 错误处理优化

### 📋 待开�?
**�?�?Day5-7:**
- [ ] 报告生成模块 (`report_generator.py`)
- [ ] Streamlit前端界面
- [ ] 端到端流程测�?
**�?�?**
- [ ] 知识库向量化（可选）
- [ ] 多轮对话支持
- [ ] 性能优化

**�?�?**
- [ ] UI美化
- [ ] 部署文档
- [ ] 用户手册

## 🐛 常见问题

### Q1: CodeBuddy服务连接失败

**问题**: `CodeBuddy服务不可用`

**解决**:
```bash
# 确认CodeBuddy已启�?codebuddy --serve --port 3000

# 检查端口是否被占用
netstat -ano | findstr :3000
```

### Q2: MarkItDown导入失败

**问题**: `ImportError: No module named 'markitdown'`

**解决**:
```bash
# 重新安装MarkItDown（包含所有功能）
pip install 'markitdown[all]'
```

### Q3: 知识库文件读取失�?
**问题**: CSV文件编码错误

**解决**:
- 确保CSV文件编码为UTF-8-BOM
- 使用 `encoding='utf-8-sig'` 读取

### Q4: 文件解析超时

**问题**: 大文件解析时间过�?
**解决**:
- 增加超时时间 (�?`codebuddy_client.py` 中调�?`timeout`)
- 分批上传文件

## 📚 参考文�?
- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [CodeBuddy HTTP API](https://cnb.cool/codebuddy/codebuddy-code/-/git/raw/main/docs/http-api.md)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [项目技术方案](./合同评审Agent-技术方案v2.md)

## 🤝 获取帮助

遇到问题�?
1. 查看日志: `logs/app.log`
2. 运行测试: `python test_markitdown.py`
3. 检查服�? http://localhost:8000/health

## �?下一�?
�?周剩余任�?
- [ ] 运行 `test_markitdown.py` 验证集成
- [ ] 测试文件上传和解析功�?- [ ] 测试完整评审流程
- [ ] 开发Streamlit前端界面

继续开�? 🚀
