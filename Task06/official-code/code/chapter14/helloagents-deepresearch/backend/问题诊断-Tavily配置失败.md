# DeepResearch 搜索引擎配置问题诊断报告

**创建时间**: 2025-12-27  
**问题状态**: ⚠️ 未解决

---

## 问题总结

DeepResearch 后端服务无法识别 Tavily API 密钥，即使在 `.env` 文件中正确配置，仍然显示 `⚠️ TAVILY_API_KEY 未设置` 警告。

---

## 根本原因

`hello_agents` Python 包在初始化时直接检查**系统环境变量**，而不是从项目的 `.env` 文件读取。

**证据**:
```
File "C:\Users\frankechen\AppData\Roaming\Python\Python314\site-packages\hello_agents\tools\builtin\search_tool.py", line 292
RuntimeError: TAVILY_API_KEY 未配置或 tavily 未安装
```

这个错误来自 `hello_agents` 包自身的代码，说明包在导入时就已经检查环境变量，而此时 `main.py` 的 `load_dotenv()` 还没有执行。

---

## 时序问题分析

```
1. Python 启动
2. hello_agents 包被导入
3. hello_agents 检查 os.environ['TAVILY_API_KEY'] ❌ 找不到
4. hello_agents 初始化完成（已决定不使用 Tavily）
5. main.py 执行
6. load_dotenv() 加载 .env 文件 ⏰ 太晚了！
7. 服务启动（但 hello_agents 已经决定不用 Tavily）
```

---

## 尝试过的解决方案

### ❌ 方案1: 修改 `.env` 文件
**结果**: 失败  
**原因**: `.env` 文件在 hello_agents 包初始化之后才加载

### ❌ 方案2: 使用 PowerShell 设置环境变量后启动
**命令**:
```powershell
$env:SEARCH_API="tavily"
$env:TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
python src\main.py
```
**结果**: 失败  
**原因**: PowerShell 的环境变量语法解析错误

### ❌ 方案3: 使用 bat 脚本设置环境变量
**命令**:
```batch
set SEARCH_API=tavily
set TAVILY_API_KEY=YOUR_TAVILY_API_KEY_HERE
python src\main.py
```
**结果**: 失败  
**原因**: bat 文件中文字符编码问题，且环境变量未被子进程继承

### ⚠️ 方案4: 回退到 DuckDuckGo
**结果**: 部分成功  
**说明**: 
- 服务可以启动
- 任务规划正常
- 但搜索步骤被跳过，生成空报告
- 可能是 DuckDuckGo 也有限流或其他问题

---

## 当前服务状态

### 后端服务
- **状态**: ✅ 运行中
- **地址**: http://localhost:8000
- **Shell ID**: p6eyFu
- **配置**: DuckDuckGo（无API密钥）

### 前端服务
- **状态**: ✅ 运行中  
- **地址**: http://localhost:5174
- **Shell ID**: RHBHo1

### 功能状态
- ✅ 服务启动
- ✅ API 端点响应
- ✅ 任务规划（4个任务成功生成）
- ❌ 搜索执行（无搜索日志）
- ❌ 报告生成（生成空报告或占位符内容）

---

## 推荐解决方案

### 方案 A: 在系统级别设置环境变量（最可靠）

1. **Windows系统设置**:
   ```
   控制面板 → 系统 → 高级系统设置 → 环境变量
   
   添加用户变量:
   - 变量名: TAVILY_API_KEY
   - 变量值: YOUR_TAVILY_API_KEY_HERE
   
   - 变量名: SEARCH_API
   - 变量值: tavily
   ```

2. **重启 PowerShell** 或计算机

3. **启动服务**:
   ```powershell
   cd C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\backend
   python src\main.py
   ```

**优点**: 一劳永逸，环境变量对所有进程可见  
**缺点**: 需要重启 PowerShell/系统，影响全局环境

---

### 方案 B: 使用 Python 包装脚本（推荐）

创建文件 `start_with_env.py`:

```python
import os
import sys

# 在导入任何包之前设置环境变量
os.environ['SEARCH_API'] = 'tavily'
os.environ['TAVILY_API_KEY'] = 'YOUR_TAVILY_API_KEY_HERE'

# 确保环境变量已设置
print(f"✅ SEARCH_API = {os.environ.get('SEARCH_API')}")
print(f"✅ TAVILY_API_KEY = {os.environ.get('TAVILY_API_KEY')[:20]}...{os.environ.get('TAVILY_API_KEY')[-10:]}")

# 导入并运行主程序
if __name__ == "__main__":
    import src.main
```

启动命令:
```powershell
python start_with_env.py
```

**优点**: 简单、可控、不影响系统环境  
**缺点**: 需要创建额外文件

---

### 方案 C: 继续使用 DuckDuckGo 并接受限制

**说明**: DuckDuckGo 免费但有限流风险

**适用场景**:
- 轻量级测试
- 偶尔使用
- 不介意偶尔失败

**限制**:
- 搜索请求过多会被限流
- 搜索结果质量可能较低
- 可能返回空结果

---

## API 密钥记录

### Tavily（推荐使用）
```
API Key: YOUR_TAVILY_API_KEY_HERE
免费额度: 1000次/月
支持状态: ✅ hello_agents 原生支持
配置状态: ⚠️ 环境变量加载时序问题
```

### SERPER
```
API Key: YOUR_SERPER_API_KEY_HERE
支持状态: ❌ hello_agents 当前版本不支持
```

### Metaso
```
API Key: YOUR_METASO_API_KEY_HERE
支持状态: ❌ hello_agents 当前版本不支持
```

---

## 下一步行动

### 选项 1: 快速测试（使用 Python 包装脚本）
1. 创建 `start_with_env.py`（见方案B）
2. 使用 `python start_with_env.py` 启动
3. 测试研究功能

### 选项 2: 永久解决（设置系统环境变量）
1. 在 Windows 系统设置中添加环境变量（见方案A）
2. 重启 PowerShell
3. 正常启动服务

### 选项 3: 继续使用当前配置
- 前端已可访问: http://localhost:5174
- 功能受限但可以体验界面和流程
- 搜索可能失败或返回空结果

---

## 参考信息

### 相关文件
- `.env`: `C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\backend\.env`
- `main.py`: `C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\backend\src\main.py`
- `search_tool.py` (hello_agents): `C:\Users\frankechen\AppData\Roaming\Python\Python314\site-packages\hello_agents\tools\builtin\search_tool.py`

### 错误堆栈
```
File "...\hello_agents\tools\builtin\search_tool.py", line 292, in _search_tavily
    raise RuntimeError(message)
RuntimeError: TAVILY_API_KEY 未配置或 tavily 未安装
```

---

**建议**: 尝试方案B（Python包装脚本），这是最快且最可靠的解决方案。
