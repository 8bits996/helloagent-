#!/bin/bash
# 企业微信回调服务 V1 停止脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/app-v1.pid"

echo "=========================================="
echo "企业微信回调服务 V1 停止脚本"
echo "=========================================="

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  未找到进程文件，服务可能未运行"
    exit 0
fi

APP_PID=$(cat "$PID_FILE")

if ! ps -p "$APP_PID" > /dev/null 2>&1; then
    echo "⚠️  进程 $APP_PID 不存在，服务可能已停止"
    rm -f "$PID_FILE"
    exit 0
fi

echo "正在停止服务 (PID: $APP_PID)..."

# 尝试优雅关闭
kill -TERM "$APP_PID" 2>/dev/null || true

# 等待进程退出
for i in {1..10}; do
    if ! ps -p "$APP_PID" > /dev/null 2>&1; then
        echo "✅ 服务已停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 强制关闭
echo "⚠️  优雅关闭超时，强制停止..."
kill -KILL "$APP_PID" 2>/dev/null || true
sleep 1

if ! ps -p "$APP_PID" > /dev/null 2>&1; then
    echo "✅ 服务已强制停止"
    rm -f "$PID_FILE"
    exit 0
else
    echo "❌ 无法停止服务"
    exit 1
fi
