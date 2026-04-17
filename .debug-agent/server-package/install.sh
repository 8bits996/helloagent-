#!/bin/bash
# Debug Agent 服务端安装脚本
# 远程机器: 我的CVM环境 (21.91.168.209)

set -e

# === 配置参数 ===
INSTALL_DIR="/home/frankechen/debug-agent"
WORKSPACE_DIR="/home/frankechen/debug-agent/workspace"
TOKEN="79SiR6jyCFvtcqMvzZZLuB098ioCF2K7"

echo "════════════════════════════════════════════════════════════════"
echo "  Debug Agent Server Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 1: 创建目录
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"/{logs,backups}
mkdir -p "$WORKSPACE_DIR"
cd "$INSTALL_DIR"

# Step 2: 复制文件
echo "📋 Copying files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/debug-agent" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/agent.yaml" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/debug-agent"

# Step 3: 创建启动脚本
echo "📝 Creating start script..."
cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
export DEBUG_AGENT_TOKEN="$TOKEN"
cd "$INSTALL_DIR"
./debug-agent --config=agent.yaml
EOF
chmod +x "$INSTALL_DIR/start.sh"

# Step 4: 创建后台运行脚本
echo "📝 Creating background start script..."
cat > "$INSTALL_DIR/start-background.sh" << EOF
#!/bin/bash
export DEBUG_AGENT_TOKEN="$TOKEN"
cd "$INSTALL_DIR"
nohup ./debug-agent --config=agent.yaml > "$INSTALL_DIR/debug-agent.log" 2>&1 &
echo \$! > "$INSTALL_DIR/debug-agent.pid"
echo "Debug Agent started with PID: \$(cat $INSTALL_DIR/debug-agent.pid)"
EOF
chmod +x "$INSTALL_DIR/start-background.sh"

# Step 5: 创建停止脚本
echo "📝 Creating stop script..."
cat > "$INSTALL_DIR/stop.sh" << EOF
#!/bin/bash
if [ -f "$INSTALL_DIR/debug-agent.pid" ]; then
    PID=\$(cat "$INSTALL_DIR/debug-agent.pid")
    if kill -0 \$PID 2>/dev/null; then
        kill \$PID
        echo "Debug Agent stopped (PID: \$PID)"
        rm -f "$INSTALL_DIR/debug-agent.pid"
    else
        echo "Process not running"
        rm -f "$INSTALL_DIR/debug-agent.pid"
    fi
else
    echo "PID file not found"
fi
EOF
chmod +x "$INSTALL_DIR/stop.sh"

# Step 6: 创建 systemd 服务文件
echo "📝 Creating systemd service file..."
cat > "$INSTALL_DIR/debug-agent.service" << EOF
[Unit]
Description=Debug Agent Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="DEBUG_AGENT_TOKEN=$TOKEN"
ExecStart=$INSTALL_DIR/debug-agent --config=$INSTALL_DIR/agent.yaml
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Installation completed!"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Configuration Summary"
echo "════════════════════════════════════════════════════════════════"
echo "Installation Dir: $INSTALL_DIR"
echo "Workspace Dir:    $WORKSPACE_DIR"
echo "Token:            $TOKEN"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Quick Start Commands"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Option 1: 前台运行（测试用）"
echo "  cd $INSTALL_DIR && ./start.sh"
echo ""
echo "Option 2: 后台运行"
echo "  cd $INSTALL_DIR && ./start-background.sh"
echo "  cd $INSTALL_DIR && ./stop.sh   # 停止"
echo ""
echo "Option 3: systemd 服务（推荐）"
echo "  sudo cp $INSTALL_DIR/debug-agent.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable debug-agent"
echo "  sudo systemctl start debug-agent"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Health Check"
echo "════════════════════════════════════════════════════════════════"
echo "  curl http://localhost:9999/api/v1/health"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: Token for client configuration:"
echo "    $TOKEN"
echo ""
