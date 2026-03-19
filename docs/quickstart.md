# 快速开始

欢迎使用 CLI-API！本指南将在 5 分钟内帮您快速上手。

## 📋 前置要求

- Rust 1.70+ 
- Git

## 🚀 5分钟快速体验

### 1. 克隆并构建

```bash
# 克隆仓库
git clone https://github.com/username/cli-api.git
cd cli-api

# 构建项目
cargo build --release

# 安装到系统路径（可选）
cargo install --path crates/cli-api
```

### 2. 启动服务

```bash
# 启动 Hub (智能体注册中心)
cargo run --bin hub &

# 启动 Broker (路由服务)  
cargo run --bin broker &

# 验证服务状态
cli-api hub status
```

### 3. 第一次调用

```bash
# 查看可用智能体
cli-api list

# 调用默认的 GPT-4 智能体 (需要 API Key)
export OPENAI_API_KEY="your-key-here"
cli-api call gpt4 chat "Hello, CLI-API!"

# 查看调用历史
cli-api history
```

## 🎯 核心命令

### 智能体操作

```bash
# 列出所有智能体
cli-api list

# 按分类过滤
cli-api list --category chat
cli-api list --provider openai

# 搜索智能体
cli-api list --search "翻译"

# 查看智能体详细信息
cli-api info gpt4
cli-api info claude --json
```

### 调用智能体

```bash
# 基础调用
cli-api call <agent_id> <command> [args...]

# 示例：聊天
cli-api call gpt4 chat "解释什么是区块链"

# 示例：文件处理
cli-api call analyzer summarize --file report.pdf

# 示例：使用管道
echo "长文本内容" | cli-api call summarizer compress

# 指定输出格式
cli-api call gpt4 chat "Hello" --output json
cli-api call gpt4 chat "Hello" --output yaml
```

### 智能体管理

```bash
# 注册新智能体
cli-api agent register my-agent.yaml

# 测试智能体连接
cli-api agent test gpt4

# 注销智能体
cli-api agent unregister my-agent
```

### 配置管理

```bash
# 查看当前配置
cli-api config show

# 设置 Hub 地址  
cli-api config set hub_url "https://my-hub.com"

# 设置 API Keys
cli-api config set openai.api_key "sk-..."
cli-api config set anthropic.api_key "ant-..."

# 重置配置
cli-api config reset
```

## 📝 配置文件

CLI-API 会在 `~/.cli-api/` 目录下创建配置文件：

### 主配置文件 (~/.cli-api/config.toml)

```toml
[hub]
url = "https://hub.cli-api.org"
local_port = 8080

[broker]  
url = "https://broker.cli-api.org"
local_port = 8081

[auth.openai]
api_key = "sk-..."

[auth.anthropic]
api_key = "ant-..."

[defaults]
output_format = "json"
timeout = 30
verbose = false
```

### 智能体配置示例 (my-agent.yaml)

```yaml
id: my-custom-agent
name: "我的自定义智能体"
description: "用于特定任务的智能体"
version: "1.0.0"
provider: "custom"

endpoint: "http://localhost:3000/api/v1"
protocol: "rest"

commands:
  - name: "process"
    description: "处理文本"
    args:
      - name: "text"
        required: true
        type: "string"
      - name: "mode"
        required: false
        type: "string"
        default: "auto"

auth:
  type: "bearer"
  config:
    token_env: "MY_AGENT_TOKEN"

capabilities:
  - "text-processing"
  - "analysis"
```

## 🌟 高级功能

### 批量调用

```bash
# 从文件读取任务列表
cat tasks.txt | xargs -I {} cli-api call gpt4 process "{}"

# 并行调用多个智能体
cli-api call gpt4 analyze data.txt &
cli-api call claude review data.txt &
wait
```

### 工作流编排

```bash
#!/bin/bash
# workflow.sh - 智能体工作流示例

# 步骤1：提取关键词
keywords=$(cli-api call extractor keywords --text "$1" --output text)

# 步骤2：生成大纲  
outline=$(cli-api call gpt4 outline --keywords "$keywords" --output text)

# 步骤3：编写内容
content=$(cli-api call claude write --outline "$outline" --output text)

# 步骤4：润色文本
final=$(cli-api call polisher enhance --text "$content" --output text)

echo "$final" > result.txt
```

### 监控和调试

```bash
# 启用详细日志
cli-api --verbose call gpt4 chat "debug"

# 查看调用统计
cli-api stats

# 监控智能体状态
cli-api monitor --agent gpt4
```

## 🔧 故障排除

### 常见问题

**Q: 提示"Agent not found"**
```bash
# 检查智能体是否已注册
cli-api list
cli-api hub status

# 刷新智能体列表
cli-api hub sync
```

**Q: 调用超时**
```bash
# 增加超时时间
cli-api call gpt4 chat "hello" --timeout 60

# 或修改默认配置
cli-api config set defaults.timeout 60
```

**Q: 认证失败**
```bash
# 检查 API Key 配置
cli-api config show

# 重新设置 API Key
cli-api config set openai.api_key "your-new-key"
```

### 日志调试

```bash
# 查看详细日志
RUST_LOG=debug cli-api call gpt4 chat "hello"

# 查看网络请求
RUST_LOG=reqwest=debug cli-api call gpt4 chat "hello"
```

## 🎉 下一步

恭喜！您已经掌握了 CLI-API 的基础用法。接下来可以：

- 📖 阅读 [CLI 工具详细指南](cli/README.md)
- 🔧 了解 [CAP 协议规范](protocol/README.md)  
- 🔌 学习 [适配器开发](adapters/README.md)
- 🚀 查看 [部署指南](deployment/docker.md)

---

有问题？查看 [FAQ](guides/faq.md) 或 [提交 Issue](https://github.com/username/cli-api/issues) 💬