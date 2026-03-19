#!/bin/bash
# 本地服务启动脚本

set -e

echo "🚀 Starting CLI-API services..."

# 检查端口是否占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# 启动 Hub
if check_port 8080; then
    echo "📡 Starting Hub on port 8080..."
    cargo run --bin hub &
    HUB_PID=$!
    sleep 2
else
    echo "❌ Hub port 8080 is occupied"
    exit 1
fi

# 启动 Broker
if check_port 8081; then
    echo "🌐 Starting Broker on port 8081..."
    cargo run --bin broker &
    BROKER_PID=$!
    sleep 2
else
    echo "❌ Broker port 8081 is occupied"
    kill $HUB_PID 2>/dev/null || true
    exit 1
fi

# 等待服务启动
echo "⏳ Waiting for services to be ready..."
sleep 5

# 测试服务
echo "🧪 Testing services..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Hub is running"
else
    echo "❌ Hub health check failed"
fi

if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ Broker is running"
else
    echo "❌ Broker health check failed"  
fi

echo ""
echo "🎉 Services are running!"
echo "Hub:    http://localhost:8080"
echo "Broker: http://localhost:8081"
echo ""
echo "To test: cargo run --bin cli-api list"
echo "To stop: kill $HUB_PID $BROKER_PID"

# 保存 PID 用于停止服务
echo $HUB_PID > /tmp/cli-api-hub.pid
echo $BROKER_PID > /tmp/cli-api-broker.pid

echo ""
echo "PIDs saved to /tmp/cli-api-*.pid"
echo "Run scripts/stop.sh to stop services"

# 等待用户中断
trap "echo ''; echo '🛑 Stopping services...'; kill $HUB_PID $BROKER_PID 2>/dev/null || true; exit 0" INT
wait