# 企业微信回调服务 - V1 版本

这是一个纯粹的企业微信回调服务，专注于企微消息的接收、解密和回复功能。

## 功能特性

- ✅ 企业微信消息接收和解密
- ✅ 企业微信消息发送和回复
- ✅ 用户白名单验证
- ✅ 完整的日志记录
- ✅ 简洁的代码实现（约100行）

## 环境要求

- Python 3.8+
- FastAPI
- httpx
- defusedxml
- pycryptodome

## 配置说明

### 必需的环境变量

```bash
# 企业微信配置
export QYWX_TOKEN="your_token"
export QYWX_ENCODING_AES_KEY="your_aes_key"
```

### 可选的环境变量

```bash
# 服务端口（默认 8088）
export PORT=8088

# 白名单用户（逗号分隔，默认 rtxid）
export ALLOWED_USERS="user1,user2,user3"
```

## 快速启动

### 1. 安装依赖

```bash
pip install fastapi uvicorn httpx defusedxml pycryptodome
```

### 2. 设置环境变量

```bash
# 复制示例配置
cp .env.v1.example .env

# 编辑配置文件
vim .env

# 加载环境变量
source .env
```

### 3. 启动服务

```bash
python app-v1.py
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8088/health

# 根路径
curl http://localhost:8088/
```

## API 接口

### 1. 企微回调接口

```
POST /qyapi?msg_signature=xxx&timestamp=xxx&nonce=xxx
```

企业微信会向此接口发送消息，服务会自动解密并处理。

**功能说明：**
- GET 请求：用于企业微信验证 URL
- POST 请求：接收企业微信消息并回复

### 2. 健康检查

```
GET /health
```

返回示例：
```json
{
  "status": "ok",
  "message": "配置验证通过",
  "version": "1.0.0"
}
```

### 3. 根路径

```
GET /
```

返回服务基本信息。

## 工作流程

```
用户发送消息
    ↓
企业微信回调 (/qyapi)
    ↓
解密消息
    ↓
白名单验证
    ↓
处理消息（回显）
    ↓
发送回复到企微群
```

## 消息处理

当前版本使用**简单回显**模式，收到消息后会：
1. 发送确认消息
2. 回显用户发送的内容

**扩展方式：**

在 `handle_message()` 函数中可以接入你自己的业务逻辑：

```python
async def handle_message(content: str, from_name: str, webhook_url: str):
    """处理消息并回复"""
    try:
        log_message("处理消息", f"用户: {from_name}\n内容: {content}")

        # ========== 在这里添加你的业务逻辑 ==========
        # 例如：
        # - 调用 AI 模型
        # - 查询数据库
        # - 调用其他 API
        # - 执行特定命令
        # ==========================================

        reply = process_your_logic(content, from_name)
        await send_qywx_message(webhook_url, reply)

    except Exception as e:
        log_message("处理异常", str(e))
        await send_qywx_message(webhook_url, f"❌ 处理失败: {str(e)}")
```

## 日志文件

日志文件位置：`app-v1.log`

日志格式：
```
[2025-12-28 10:30:45] [消息类型]
消息内容
--------------------------------------------------------------------------------
```

## 安全说明

1. **白名单机制**：只有在 `ALLOWED_USERS` 中的用户才能使用服务
2. **消息加密**：所有企微消息都经过 AES 加密
3. **环境变量**：敏感信息通过环境变量配置，不写入代码

## 故障排查

### 配置验证失败

```bash
❌ 配置错误: 缺少必需的环境变量: QYWX_TOKEN, QYWX_ENCODING_AES_KEY
```

**解决方法**：检查并设置所有必需的环境变量。

### 权限不足

```
❌ 权限不足，您不在白名单中
```

**解决方法**：将用户添加到 `ALLOWED_USERS` 环境变量中。

### 解密失败

查看日志文件 `app-v1.log` 获取详细错误信息，通常是因为：
1. `QYWX_ENCODING_AES_KEY` 配置错误
2. 消息格式不正确

## 代码结构

```python
app-v1.py (约100行)
├── ConfigV1          # 配置类
├── log_message()     # 日志记录
├── decrypt()         # 消息解密
├── send_qywx_message()    # 发送企微消息
├── handle_message()  # 消息处理（可自定义）
├── qyapi_callback()  # 企微回调接口
├── health_check()    # 健康检查
└── root()            # 根路径
```

## 与完整版的区别

| 功能 | V1 版本 | 完整版 |
|------|---------|--------|
| 企微消息接收 | ✅ | ✅ |
| 企微消息回复 | ✅ | ✅ |
| 消息处理 | 简单回显 | CodeBuddy CLI |
| iWiki AI | ❌ | ✅ |
| TAPD 修复 | ❌ | ✅ |
| Git Worktree | ❌ | ✅ |
| 迭代修复 | ❌ | ✅ |
| 代码行数 | ~100 | ~800 |

## 许可证

内部使用
