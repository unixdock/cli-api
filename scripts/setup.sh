#!/bin/bash
# 开发环境安装脚本

set -e

echo "🚀 Setting up CLI-API development environment..."

# 检查 Rust 环境
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not found. Please install Rust first:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

echo "✅ Rust found: $(cargo --version)"

# 安装必要的工具
echo "📦 Installing development tools..."
cargo install --locked cargo-watch
cargo install --locked cargo-audit
cargo install --locked cargo-tarpaulin

# 构建项目
echo "🔨 Building project..."
cargo build

# 运行测试
echo "🧪 Running tests..."
cargo test

# 创建配置目录
echo "📁 Creating config directory..."
mkdir -p ~/.cli-api

# 创建示例配置
cat > ~/.cli-api/config.toml << 'EOF'
[hub]
url = "http://localhost:8080"
local_port = 8080

[broker]
url = "http://localhost:8081"
local_port = 8081

[defaults]
output_format = "json"
timeout = 30
verbose = false

# 在这里添加您的 API Keys
# [auth.openai]
# api_key = "sk-your-openai-key"

# [auth.anthropic]  
# api_key = "ant-your-anthropic-key"
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to ~/.cli-api/config.toml"
echo "2. Start the hub: cargo run --bin hub"
echo "3. Start the broker: cargo run --bin broker"  
echo "4. Try: cargo run --bin cli-api list"
echo ""
echo "📚 See docs/quickstart.md for more information"