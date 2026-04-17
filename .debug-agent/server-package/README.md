# Debug Agent 服务端部署包

## 目标服务器信息
- **服务器**: 我的CVM环境
- **IP地址**: 21.91.168.209
- **用户名**: frankechen

## 包含文件
- `debug-agent` - 服务端二进制文件
- `agent.yaml` - 服务端配置
- `install.sh` - 安装脚本
- `README.md` - 本文件

## 认证 Token
```
79SiR6jyCFvtcqMvzZZLuB098ioCF2K7
```
⚠️ **请妥善保存此 Token！客户端配置需要使用**

## 安装步骤

### 1. 上传此目录到远程服务器

```bash
# 方法 1: 使用 scp
scp -r .debug-agent/server-package frankechen@21.91.168.209:/tmp/debug-agent-package

# 方法 2: 通过 WeTerm 的 rz 命令上传
# 先压缩: tar czf server-package.tar.gz server-package
# 在远程服务器执行: rz -bye
# 然后解压: tar xzf server-package.tar.gz
```

### 2. 在远程服务器执行安装

```bash
cd /tmp/debug-agent-package
chmod +x install.sh
./install.sh
```

### 3. 启动服务

**后台运行（推荐）:**
```bash
cd /home/frankechen/debug-agent
./start-background.sh
```

**systemd 服务（生产环境）:**
```bash
sudo cp /home/frankechen/debug-agent/debug-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable debug-agent
sudo systemctl start debug-agent
```

### 4. 验证安装

```bash
curl http://localhost:9999/api/v1/health
```

期望输出:
```json
{"code":0,"message":"success","data":{"status":"healthy","managed_processes":[]}}
```

## 客户端配置

在本地开发机设置环境变量:
```bash
export DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"
```

或添加到 shell 配置文件:
```bash
echo 'export DEBUG_AGENT_TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"' >> ~/.bashrc
source ~/.bashrc
```
