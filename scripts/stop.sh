#!/bin/bash
# 停止本地服务脚本

echo "🛑 Stopping CLI-API services..."

# 从 PID 文件读取并停止服务
if [ -f /tmp/cli-api-hub.pid ]; then
    HUB_PID=$(cat /tmp/cli-api-hub.pid)
    if kill -0 $HUB_PID 2>/dev/null; then
        echo "Stopping Hub (PID: $HUB_PID)..."
        kill $HUB_PID
    fi
    rm -f /tmp/cli-api-hub.pid
fi

if [ -f /tmp/cli-api-broker.pid ]; then
    BROKER_PID=$(cat /tmp/cli-api-broker.pid)
    if kill -0 $BROKER_PID 2>/dev/null; then
        echo "Stopping Broker (PID: $BROKER_PID)..."
        kill $BROKER_PID
    fi
    rm -f /tmp/cli-api-broker.pid
fi

# 强制停止残留进程
pkill -f "cli-api.*hub" 2>/dev/null || true
pkill -f "cli-api.*broker" 2>/dev/null || true

echo "✅ Services stopped"