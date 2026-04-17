#!/bin/bash
# 企业微信回调服务 V2 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/app-v2.pid"

echo "=========================================="
echo "企业微信回调服务 V2 停止脚本"
echo "=========================================="
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  服务未运行（PID文件不存在）"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  服务未运行（进程不存在）"
    rm -f "$PID_FILE"
    exit 0
fi

echo "正在停止服务 (PID: $PID)..."
kill "$PID"

# 等待进程结束
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 服务已停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 强制终止
echo "⚠️  正常停止失败，强制终止..."
kill -9 "$PID"
rm -f "$PID_FILE"
echo "✅ 服务已强制停止"
