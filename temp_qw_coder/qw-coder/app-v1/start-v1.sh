#!/bin/bash
# 企业微信回调服务 V1 启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 自动加载 .env 文件
if [ -f .env ]; then
    echo "🔧 加载环境变量..."
    set -a  # 自动导出所有变量
    source .env
    set +a
fi

echo "=========================================="
echo "企业微信回调服务 V1 启动脚本"
echo "=========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# 检查依赖
echo ""
echo "检查依赖包..."
MISSING_PACKAGES=""

# 检查 fastapi
if ! python3 -c "import fastapi" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES fastapi"
fi

# 检查 uvicorn
if ! python3 -c "import uvicorn" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES uvicorn"
fi

# 检查 httpx
if ! python3 -c "import httpx" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES httpx"
fi

# 检查 defusedxml
if ! python3 -c "import defusedxml" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES defusedxml"
fi

# 检查 pycryptodome (导入时使用 Crypto)
if ! python3 -c "from Crypto.Cipher import AES" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES pycryptodome"
fi

if [ -n "$MISSING_PACKAGES" ]; then
    echo "❌ 缺少依赖包:$MISSING_PACKAGES"
    echo ""
    echo "请运行以下命令安装:"
    echo "  pip install$MISSING_PACKAGES"
    exit 1
fi

echo "✅ 依赖包完整"

# 检查环境变量
echo ""
echo "检查环境变量..."

if [ -z "$QYWX_TOKEN" ] || [ -z "$QYWX_ENCODING_AES_KEY" ]; then
    echo "⚠️  警告: 缺少必需的环境变量"
    echo ""
    echo "请设置以下环境变量:"
    echo "  - QYWX_TOKEN"
    echo "  - QYWX_ENCODING_AES_KEY"
    echo ""
    echo "提示: 可以从 .env 文件加载"
    if [ -f ".env" ]; then
        echo "  source .env"
    else
        echo "  cp .env.v1.example .env"
        echo "  编辑 .env 文件并填入实际值"
        echo "  source .env"
    fi
    exit 1
fi

echo "✅ 环境变量配置完整"

# 检查端口
PORT=${PORT:-8088}
if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo ""
    echo "⚠️  警告: 端口 $PORT 已被占用"
    echo "请设置 PORT 环境变量使用其他端口，或停止占用该端口的服务"
    exit 1
fi

# 启动服务
echo ""
echo "=========================================="
echo "🚀 启动服务..."
echo "=========================================="
echo ""

# 显示配置信息
echo "============================================================"
echo "企业微信回调服务 V1 配置:"
echo "- 服务端口: $PORT"
echo "- 日志文件: $SCRIPT_DIR/app-v1.log"
echo "============================================================"
echo ""

# 使用 nohup 后台运行
PID_FILE="$SCRIPT_DIR/app-v1.pid"
LOG_FILE="$SCRIPT_DIR/app-v1.log"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  服务已在运行 (PID: $OLD_PID)"
        echo "如需重启，请先运行: ./stop-v1.sh"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 使用 uvicorn 命令行启动（兼容 Python 3.6）
nohup python3 -m uvicorn app-v1:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
APP_PID=$!

echo $APP_PID > "$PID_FILE"

# 等待服务启动
sleep 2

if ps -p $APP_PID > /dev/null 2>&1; then
    echo "✅ 服务启动成功 (PID: $APP_PID)"
    echo ""
    echo "服务信息:"
    echo "  - 进程ID: $APP_PID"
    echo "  - 监听端口: $PORT"
    echo "  - 日志文件: $SCRIPT_DIR/app-v1.log"
    echo "  - 进程文件: $PID_FILE"
    echo ""
    echo "查看日志:"
    echo "  tail -f app-v1.log"
    echo ""
    echo "停止服务:"
    echo "  ./stop-v1.sh"
else
    echo "❌ 服务启动失败"
    rm -f "$PID_FILE"
    exit 1
fi
