# 示例与教程

本目录包含 CLI-API 的各种使用示例和教程，帮助您快速上手和深入理解。

## 📋 目录

### 🚀 基础示例
- [hello-world.md](hello-world.md) - 第一个 CLI-API 调用
- [basic-commands.md](basic-commands.md) - 常用命令演示
- [configuration.md](configuration.md) - 配置管理示例

### 🔧 进阶用法
- [batch-processing.md](batch-processing.md) - 批量调用和并行处理
- [workflow.md](workflow.md) - 智能体工作流编排
- [custom-agent.md](custom-agent.md) - 注册自定义智能体

### 🎯 应用场景
- [content-generation.md](content-generation.md) - 内容创作工作流
- [data-analysis.md](data-analysis.md) - 数据分析任务
- [code-assistance.md](code-assistance.md) - 代码开发辅助

### 🔌 集成示例  
- [rest-api.md](rest-api.md) - REST API 集成
- [python-integration.md](python-integration.md) - Python 脚本集成
- [docker-usage.md](docker-usage.md) - Docker 容器使用

---

## 🎮 快速体验

### Hello World

```bash
# 最简单的调用
cli-api call gpt4 chat "Hello, CLI-API!"
```

### 查看帮助

```bash 
# 查看所有命令
cli-api --help

# 查看子命令帮助
cli-api call --help
cli-api list --help
```

### 列出智能体

```bash
# 查看所有可用智能体
cli-api list

# 输出示例：
# 📋 Available agents:
#   gpt4 - OpenAI GPT-4 (openai) [chat, generate, analyze]
#   claude - Anthropic Claude (anthropic) [chat, summarize, translate] 
#   local-llm - Local LLM (ollama) [chat, embed]
```

### 查看智能体信息

```bash
# 查看具体智能体详情
cli-api info gpt4

# JSON 格式输出
cli-api info gpt4 --output json
```

## 📖 教程导读

### 新手必读
1. 先阅读 [hello-world.md](hello-world.md) 了解基本概念
2. 学习 [basic-commands.md](basic-commands.md) 掌握常用命令  
3. 配置您的环境 [configuration.md](configuration.md)

### 进阶学习
1. 尝试 [batch-processing.md](batch-processing.md) 提高效率
2. 掌握 [workflow.md](workflow.md) 构建复杂任务
3. 学习 [custom-agent.md](custom-agent.md) 扩展功能

### 实际应用
1. 内容创作者看 [content-generation.md](content-generation.md)
2. 数据分析师看 [data-analysis.md](data-analysis.md) 
3. 程序员看 [code-assistance.md](code-assistance.md)

## 🛠️ 实用脚本

### 智能体状态监测

```bash
#!/bin/bash
# check-agents.sh
echo "🔍 Checking agent status..."

agents=$(cli-api list --output json | jq -r '.[].id')

for agent in $agents; do
    if cli-api agent test $agent > /dev/null 2>&1; then
        echo "✅ $agent: Online"
    else
        echo "❌ $agent: Offline"
    fi
done
```

### 批量内容处理

```bash
#!/bin/bash
# process-files.sh
for file in *.txt; do
    echo "Processing $file..."
    cli-api call summarizer extract \
        --input "$file" \
        --output "summary-$(basename $file .txt).md"
done
```

### 智能体性能测试

```bash
#!/bin/bash
# benchmark.sh
echo "⚡ Running performance benchmark..."

start_time=$(date +%s%N)
cli-api call gpt4 chat "测试消息" > /dev/null
end_time=$(date +%s%N)

latency=$(( (end_time - start_time) / 1000000 ))
echo "Latency: ${latency}ms"
```

## 🎯 常见问题解答

### Q: 如何处理大文件输入？
```bash
# 使用管道
cat large-file.txt | cli-api call analyzer process

# 或指定输入文件
cli-api call processor analyze --input large-file.txt
```

### Q: 如何保存调用历史？
```bash
# 输出到文件
cli-api call gpt4 chat "问题" > result.json

# 追加到日志
cli-api call gpt4 chat "问题" >> history.jsonl
```

### Q: 如何处理认证信息？
```bash
# 设置环境变量
export OPENAI_API_KEY="sk-..."

# 或使用配置命令  
cli-api config set openai.api_key "sk-..."
```

## 📚 更多资源

- 📖 [用户手册](../README.md) - 完整文档  
- 🔧 [开发指南](../development/README.md) - 贡献代码
- 🚀 [部署指南](../deployment/README.md) - 生产部署
- 💬 [社区讨论](https://github.com/username/cli-api/discussions) - 交流分享

---

💡 **提示**: 所有示例都可以直接复制运行，记得先配置好相关的 API Keys！