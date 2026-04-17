# Debug Agent 手工配置指南

## 🎯 已完成的自动化配置

✅ **技能安装**: `C:\Users\frankechen\.codebuddy\skills\debug-agent\`
✅ **客户端配置**: `c:\Users\frankechen\CodeBuddy\chrome\.debug-agent\push.yaml`
✅ **服务端部署包**: `c:\Users\frankechen\CodeBuddy\chrome\.debug-agent\server-package\`

---

## 🔧 需要手工完成的步骤

### 第一步：上传服务端部署包到远程服务器【必须】

**目标服务器**: 我的CVM环境 (21.91.168.209)

#### 方法 A：使用 CodeBuddy 的远程连接功能
1. 在 IDE 中点击远程机器列表中的「我的CVM环境」
2. 通过 CodeBuddy(iOA版) 连接到远程机器
3. 在远程终端中创建临时目录: `mkdir -p /tmp/debug-agent-package`
4. 上传 `server-package` 目录下的所有文件到 `/tmp/debug-agent-package/`

#### 方法 B：使用 scp 命令
```bash
# 在本地 PowerShell 或 Git Bash 中执行
scp -r "c:/Users/frankechen/CodeBuddy/chrome/.debug-agent/server-package/*" frankechen@21.91.168.209:/tmp/debug-agent-package/
```

#### 方法 C：使用 WeTerm + rz 命令
1. 先压缩部署包:
   ```powershell
   cd c:\Users\frankechen\CodeBuddy\chrome\.debug-agent
   tar -czvf server-package.tar.gz server-package
   ```
2. 通过 WeTerm 连接到远程服务器
3. 在远程服务器执行: `cd /tmp && rz -bye`
4. 选择 `server-package.tar.gz` 上传
5. 解压: `tar xzf server-package.tar.gz`

---

### 第二步：在远程服务器执行安装脚本【必须】

通过 CodeBuddy、WeTerm 或 SSH 连接到远程服务器后执行：

```bash
cd /tmp/debug-agent-package
chmod +x install.sh debug-agent
./install.sh
```

**安装完成后会显示配置摘要和启动命令**

---

### 第三步：启动 Debug Agent 服务【必须】

选择一种方式启动服务：

#### 方式 1：后台运行（推荐日常使用）
```bash
cd /home/frankechen/debug-agent
./start-background.sh
```

#### 方式 2：systemd 服务（推荐生产环境）
```bash
sudo cp /home/frankechen/debug-agent/debug-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable debug-agent
sudo systemctl start debug-agent
```

#### 方式 3：前台运行（调试用）
```bash
cd /home/frankechen/debug-agent
./start.sh
```

---

### 第四步：验证服务状态【必须】

在远程服务器上执行：
```bash
curl http://localhost:9999/api/v1/health
```

期望输出：
```json
{"code":0,"message":"success","data":{"status":"healthy","managed_processes":[]}}
```

---

### 第五步：本地配置环境变量【必须】

在本地 Windows 机器上设置 Token 环境变量：

#### PowerShell（临时）
```powershell
$env:DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"
```

#### PowerShell（永久 - 用户级别）
```powershell
[Environment]::SetEnvironmentVariable("DEBUG_AGENT_TOKEN", "79SiR6jyCFvtcqMvzZZLuB098ioCF2K7", "User")
```

#### Git Bash / WSL
```bash
export DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"
# 永久保存
echo 'export DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"' >> ~/.bashrc
source ~/.bashrc
```

---

### 第六步：检查防火墙（如果连接失败）【可选】

在远程服务器上检查并开放端口：

```bash
# 检查端口是否监听
netstat -tulpn | grep 9999

# 如果需要开放防火墙（firewalld）
sudo firewall-cmd --permanent --add-port=9999/tcp
sudo firewall-cmd --reload

# 如果使用 iptables
sudo iptables -A INPUT -p tcp --dport 9999 -j ACCEPT
```

---

## 📋 配置文件说明

### 本地客户端配置 (`push.yaml`)

路径: `c:\Users\frankechen\CodeBuddy\chrome\.debug-agent\push.yaml`

**需要根据你的实际项目修改以下字段**：

| 字段 | 当前值 | 说明 |
|------|--------|------|
| `build.command` | `go build -o ./bin/myapp ./cmd/myapp` | 修改为你的构建命令 |
| `deploy.binary_path` | `./bin/myapp` | 本地编译产物路径 |
| `deploy.remote_path` | `/home/frankechen/debug-agent/workspace/myapp` | 远程部署路径 |
| `verify.health_check_url` | `http://localhost:8080/health` | 你的应用健康检查地址 |

### 远程服务端配置 (`agent.yaml`)

路径: `/home/frankechen/debug-agent/agent.yaml`（安装后）

**如需管理多个应用，编辑 `managed_processes` 数组**：

```yaml
managed_processes:
  - name: "app1"
    path: "/home/frankechen/debug-agent/workspace/app1"
    log_path: "/home/frankechen/debug-agent/logs/app1.log"
    working_dir: "/home/frankechen/debug-agent/workspace"
    auto_restart: false
  - name: "app2"
    path: "/home/frankechen/debug-agent/workspace/app2"
    log_path: "/home/frankechen/debug-agent/logs/app2.log"
    working_dir: "/home/frankechen/debug-agent/workspace"
    auto_restart: false

allowed_paths:
  - "/home/frankechen/debug-agent/workspace/"
```

---

## 🔑 认证 Token

```
79SiR6jyCFvtcqMvzZZLuB098ioCF2K7
```

⚠️ **此 Token 必须在客户端和服务端保持一致！**

---

## 🚀 日常使用

安装完成后，每次修改代码只需在本地项目目录执行：

### Windows (PowerShell)
```powershell
$env:DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"
C:\Users\frankechen\.codebuddy\skills\debug-agent\binaries\dev-push.exe --config=.debug-agent/push.yaml
```

### Linux/WSL/Git Bash
```bash
export DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"
~/.codebuddy/skills/debug-agent/binaries/dev-push --config=.debug-agent/push.yaml
```

**自动完成**：
1. ✅ 编译代码（交叉编译 Linux AMD64）
2. ✅ 上传到远程服务器
3. ✅ 备份旧版本
4. ✅ 重启服务
5. ✅ 健康检查

---

## ❓ 故障排查

### 问题 1：客户端无法连接服务器
```bash
# 测试网络连通性
curl http://21.91.168.209:9999/api/v1/health
# 如果超时，检查防火墙
```

### 问题 2：Token 认证失败
```bash
# 确认客户端 Token
echo $DEBUG_AGENT_TOKEN

# 确认服务端 Token（在远程服务器）
cat /home/frankechen/debug-agent/start.sh | grep TOKEN
```

### 问题 3：上传失败 - 路径不在白名单
编辑远程服务器上的 `/home/frankechen/debug-agent/agent.yaml`，在 `allowed_paths` 中添加需要的路径。

---

## 📚 更多文档

- 技能完整文档: `C:\Users\frankechen\.codebuddy\skills\debug-agent\SKILL.md`
- API 参考: `C:\Users\frankechen\.codebuddy\skills\debug-agent\references\workflow.md`
- 架构说明: `C:\Users\frankechen\.codebuddy\skills\debug-agent\references\architecture.md`
