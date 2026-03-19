# Hello World - 第一个 CLI-API 调用

这是最简单的 CLI-API 使用示例，帮助您快速体验智能体调用的魅力。

## 🎯 目标

- 完成第一次智能体调用
- 理解 CLI-API 的基本工作流程  
- 熟悉命令行接口

## 📋 前置条件

```bash
# 确保 CLI-API 已安装
cli-api --version

# 检查服务状态
cli-api hub status
```

## 🚀 开始调用

### 步骤 1: 查看可用智能体

```bash
# 列出所有智能体
cli-api list

# 输出示例：
# 📋 Available agents:
#   gpt4 - OpenAI GPT-4 (openai)
#   claude - Anthropic Claude (anthropic)  
#   local-llm - Local LLM (local)
```

### 步骤 2: 获取智能体详情

```bash
# 查看 GPT-4 的详细信息
cli-api info gpt4

# 输出示例：
# ℹ️  Agent: gpt4
# Name: OpenAI GPT-4
# Provider: openai
# Version: 1.0.0
# Description: OpenAI GPT-4 language model
# 
# Commands:
#   chat - Chat with GPT-4
#     args: message (required, string) - Message to send
#     example: cli-api call gpt4 chat "Hello, world!"
#   
# Capabilities: chat, text-generation
# Endpoint: https://api.openai.com/v1
# Protocol: openai
```

### 步骤 3: 配置认证 (如需要)

```bash
# 设置 OpenAI API Key
cli-api config set openai.api_key "sk-your-api-key-here"

# 或使用环境变量
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 步骤 4: 第一次调用！

```bash
# 最简单的调用
cli-api call gpt4 chat "Hello, CLI-API!"
```

### 期望输出

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "success": true,
  "output": "Hello! I'm excited to help you through CLI-API. This is a great example of how different AI agents can be accessed through a unified command-line interface. What would you like to explore next?",
  "error": null,
  "metadata": {
    "model": "gpt-4",
    "tokens": 42,
    "cost_usd": "0.001"
  },
  "execution_time_ms": 1250
}
```

## 🧪 更多尝试

### 不同输出格式

```bash
# 纯文本输出  
cli-api call gpt4 chat "Hello!" --output text
# Hello! How can I assist you today?

# YAML 格式
cli-api call gpt4 chat "Hello!" --output yaml
# id: 123e4567-e89b-12d3-a456-426614174000
# success: true
# output: Hello! How can I assist you today?
# ...
```

### 使用管道输入

```bash
# 从文件读取
echo "What is quantum computing?" | cli-api call gpt4 chat

# 处理文件内容
cat article.txt | cli-api call gpt4 chat "请总结以下内容："
```

### 指定超时时间

```bash
# 30秒超时
cli-api call gpt4 chat "复杂问题" --timeout 30

# 详细日志输出
cli-api --verbose call gpt4 chat "Hello!"
```

## 🔍 理解输出

### 响应字段说明

```json
{
  "id": "请求唯一标识符",
  "success": "调用是否成功 (true/false)",  
  "output": "智能体的响应内容",
  "error": "错误信息 (如有)",
  "metadata": {
    "model": "使用的模型名称",
    "tokens": "消耗的 token 数量", 
    "cost_usd": "调用成本 (美元)"
  },
  "execution_time_ms": "执行时间 (毫秒)"
}
```

### 成功调用的标志

✅ `success: true`  
✅ `output` 字段包含有效内容  
✅ `error` 字段为 `null`  
✅ 返回状态码为 0

### 失败调用的处理

```bash
# 示例：调用不存在的智能体
cli-api call nonexistent chat "Hello"

# 输出：
# {
#   "success": false,
#   "error": "Agent not found: nonexistent",
#   "output": null
# }
```

## 🔧 故障排除

### 常见问题

**Q: 提示 "Agent not found"**
```bash
# 检查智能体列表
cli-api list

# 检查拼写
cli-api info gpt4  # 正确
cli-api info gpt-4 # 可能错误
```

**Q: 认证失败**
```bash
# 检查配置
cli-api config show

# 重新设置 API Key
cli-api config set openai.api_key "新的key"
```

**Q: 网络超时**
```bash
# 增加超时时间
cli-api call gpt4 chat "问题" --timeout 60

# 检查网络连接
curl -I https://api.openai.com/v1/models
```

**Q: 服务不可用**
```bash
# 检查 Hub 状态
cli-api hub status

# 重启服务 (如果是本地部署)
cargo run --bin hub &
cargo run --bin broker &
```

## 🎉 成功的标志

如果您看到类似下面的输出，恭喜您成功完成了第一次 CLI-API 调用！

```bash
$ cli-api call gpt4 chat "Hello, CLI-API!"
{
  "success": true,
  "output": "Hello! Welcome to CLI-API...",
  "execution_time_ms": 1250
}
```

## 📚 下一步

现在您已经完成了第一次调用，可以：

1. 🔄 尝试 [基础命令](basic-commands.md) 学习更多用法
2. 🛠️ 查看 [配置管理](configuration.md) 自定义设置  
3. 📊 探索 [批量处理](batch-processing.md) 提高效率
4. 🚀 学习 [工作流编排](workflow.md) 构建复杂任务

---

🎊 **恭喜！** 您已经踏出了使用 CLI-API 的第一步。接下来的智能体世界等您去探索！