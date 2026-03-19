# CLI-Agent Protocol (CAP) v0.1 – 草稿

**状态**：早期草稿 / 征求意见阶段  
**目标**：让任意智能体服务（LLM Agent、Multi-Agent 系统、本地模型、本地工具、本地软件）统一暴露为 **CLI-native 接口**，实现「一条命令调用全球Agent」。

**设计哲学**（继承 & 扩展 CLI-Anything 核心思想）
1. CLI 是 Agent 最自然的控制语言（无状态/有状态 REPL 皆可）
2. `--help` 必须是自描述的机器可读元数据（JSON Schema + capabilities）
3. JSON 输出是强制选项（`--json` / `--jsonl`）
4. 零依赖、易桥接（HTTP fallback 可选，但非必须）
5. 优先本地优先、隐私优先、可离线运行

## 1. 核心命令格式（统一入口）

所有 CAP 兼容的 Agent / 服务 必须支持以下基本命令模式：

```bash
agent-cli <command> [arguments] [options]
```

### 1.1 强制性通用选项

每个 CAP 兼容的 agent 必须支持以下选项：

```bash
--help                    # 输出机器可读的能力描述（JSON Schema）
--json                    # 强制 JSON 输出格式
--jsonl                   # 强制 JSONL 输出格式（流式）
--timeout <seconds>       # 超时控制
--version                 # 版本信息（包含 CAP 版本）
--capabilities            # 输出完整能力描述
```

### 1.2 标准化命令示例

```bash
# 基础调用
gpt-cli chat "Hello world"
claude-cli summarize < document.txt
local-llm generate --prompt "写一首诗"

# 带 JSON 输出
gpt-cli chat "Hello" --json
# 输出: {"success": true, "output": "Hello! How can I help?", "metadata": {...}}

# 获取能力描述
gpt-cli --help --json
# 输出: {"commands": [...], "capabilities": [...], "version": "cap-0.1"}
```

## 2. 标准响应格式

### 2.1 成功响应

```json
{
  "success": true,
  "output": "主要输出内容",
  "type": "text|json|binary|stream",
  "metadata": {
    "command": "chat",
    "duration_ms": 1250,
    "tokens_used": 150,
    "model": "gpt-4",
    "cost": 0.003,
    "timestamp": "2026-03-18T16:30:00Z"
  },
  "cap_version": "0.1"
}
```

### 2.2 错误响应

```json
{
  "success": false,
  "error": "详细错误描述",
  "error_code": "TIMEOUT|AUTH_FAILED|RATE_LIMIT|INVALID_INPUT",
  "metadata": {
    "command": "chat",
    "duration_ms": 5000,
    "timestamp": "2026-03-18T16:30:00Z"
  },
  "cap_version": "0.1"
}
```

### 2.3 流式响应（JSONL）

```jsonl
{"type": "start", "output": "", "metadata": {"command": "generate"}}
{"type": "chunk", "output": "这是", "metadata": {"tokens": 1}}
{"type": "chunk", "output": "生成的", "metadata": {"tokens": 2}}
{"type": "chunk", "output": "内容", "metadata": {"tokens": 3}}
{"type": "end", "output": "", "metadata": {"total_tokens": 3, "duration_ms": 2000}}
```

## 3. 能力描述格式（机器可读 `--help`）

### 3.1 基础能力描述

```json
{
  "agent_info": {
    "name": "GPT-4 CLI Agent",
    "version": "1.0.0",
    "cap_version": "0.1",
    "provider": "openai",
    "description": "OpenAI GPT-4 language model CLI interface"
  },
  "commands": [
    {
      "name": "chat",
      "description": "Interactive chat with the model",
      "usage": "chat [message] [options]",
      "args": [
        {
          "name": "message",
          "type": "string",
          "required": false,
          "description": "Message to send (can also use stdin)"
        }
      ],
      "options": [
        {
          "name": "--temperature",
          "type": "float",
          "default": 0.7,
          "range": [0.0, 2.0],
          "description": "控制输出随机性"
        },
        {
          "name": "--max-tokens",
          "type": "integer", 
          "default": 1000,
          "description": "最大生成 token 数"
        }
      ],
      "examples": [
        "chat 'Hello, world!'",
        "echo 'Question?' | chat",
        "chat --temperature 0.9 --max-tokens 500"
      ]
    }
  ],
  "capabilities": [
    "text-generation",
    "conversation", 
    "analysis",
    "translation"
  ],
  "input_types": ["text", "markdown", "json"],
  "output_types": ["text", "markdown", "json"],
  "constraints": {
    "max_input_length": 8192,
    "rate_limit": "60/minute",
    "authentication": "api_key"
  }
}
```

### 3.2 高级能力扩展

```json
{
  "extended_capabilities": {
    "multimodal": {
      "input": ["text", "image", "audio"],
      "output": ["text", "image"]
    },
    "tools": [
      {
        "name": "web_search",
        "description": "搜索网络信息",
        "enabled": true
      },
      {
        "name": "code_execution", 
        "description": "执行代码",
        "enabled": false
      }
    ],
    "memory": {
      "type": "conversation",
      "persistence": "session",
      "max_history": 50
    },
    "streaming": true,
    "batch_processing": true
  }
}
```

## 4. 命令类别标准化

### 4.1 核心命令（推荐所有 Agent 实现）

```bash
# 对话交互
chat [message]                # 基础对话
ask [question]                # 问答
discuss [topic]               # 讨论

# 内容处理  
generate [prompt]             # 生成内容
summarize [content]           # 总结
translate [text]              # 翻译
analyze [data]                # 分析

# 工具功能
help [topic]                  # 获取帮助
status                        # 状态检查
config [key] [value]          # 配置管理
```

### 4.2 扩展命令（根据 Agent 特性）

```bash
# 文件处理
process-file <file>           # 处理文件
batch-process <files>         # 批量处理

# 专业功能
code-review <file>            # 代码审查  
write-docs <code>             # 文档生成
debug-issue <error>           # 问题调试

# 创作工具
write-story [theme]           # 故事创作
compose-email [topic]         # 邮件撰写
design-presentation [outline] # 演示设计
```

## 5. 认证与安全

### 5.1 认证方式

```bash
# 环境变量认证（推荐）
export AGENT_API_KEY="sk-xxx"
agent-cli chat "hello"

# 配置文件认证
agent-cli config set api_key "sk-xxx"
agent-cli chat "hello"

# 临时认证
agent-cli --auth "sk-xxx" chat "hello"
```

### 5.2 安全约束

```json
{
  "security": {
    "authentication": {
      "required": true,
      "methods": ["api_key", "oauth2", "local_auth"],
      "key_env_var": "AGENT_API_KEY"
    },
    "rate_limiting": {
      "requests_per_minute": 60,
      "tokens_per_day": 100000
    },
    "privacy": {
      "data_retention": "session_only",
      "logging": "minimal",
      "encryption": "in_transit"
    }
  }
}
```

## 6. 网络协议桥接（可选）

### 6.1 HTTP 接口映射

CAP Agent 可以可选地提供 HTTP 接口，映射如下：

```bash
# CLI 命令
agent-cli chat "hello" --json

# 等价 HTTP 调用
curl -X POST http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "format": "json"}'
```

### 6.2 标准 HTTP 端点

```
GET  /v1/capabilities          # 获取能力描述（--help 等价）
POST /v1/{command}             # 执行命令
GET  /v1/status                # 状态检查
POST /v1/config                # 配置管理
```

## 7. 互操作性

### 7.1 Agent 发现

```bash
# 列出本地可用 Agent
cap-registry list

# 搜索 Agent
cap-registry search llm
cap-registry search --capability translation

# 安装新 Agent
cap-registry install gpt4-agent
cap-registry install --local ./my-agent
```

### 7.2 Agent 组合

```bash
# 管道操作
echo "长文档内容" | summarizer-cli extract | translator-cli en-to-zh | formatter-cli markdown

# 批量调用
cap-batch run "gpt4-cli analyze" *.txt

# 工作流编排
cap-workflow run content-creation-flow.yml
```

## 8. 实现要求

### 8.1 最小实现（Tier 1）

一个最简的 CAP Agent 必须：

✅ 支持 `--help --json` 输出能力描述  
✅ 支持至少一个核心命令（如 `chat`）  
✅ 支持 `--json` 输出格式  
✅ 正确处理 stdin 输入  
✅ 返回标准化错误码

### 8.2 标准实现（Tier 2）

标准 CAP Agent 应该：

✅ 支持多个核心命令  
✅ 支持流式输出（`--jsonl`）  
✅ 支持配置管理  
✅ 提供详细的使用示例  
✅ 支持超时和中断处理

### 8.3 完整实现（Tier 3）

完整 CAP Agent 可以：

✅ 提供 HTTP 接口桥接  
✅ 支持插件和扩展  
✅ 实现高级认证方式  
✅ 支持多模态输入输出  
✅ 提供监控和日志功能

## 9. 示例实现

### 9.1 最简 Python 实现

```python
#!/usr/bin/env python3
import sys, json, argparse

def get_capabilities():
    return {
        "agent_info": {
            "name": "Simple Echo Agent",
            "version": "1.0.0", 
            "cap_version": "0.1"
        },
        "commands": [
            {
                "name": "echo",
                "description": "Echo input text",
                "args": [{"name": "text", "type": "string", "required": True}]
            }
        ]
    }

def echo_command(text, json_output=False):
    result = {
        "success": True,
        "output": f"Echo: {text}",
        "metadata": {"command": "echo"},
        "cap_version": "0.1"
    }
    
    if json_output:
        print(json.dumps(result))
    else:
        print(result["output"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--help-json", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("command", nargs="?")
    parser.add_argument("text", nargs="?")
    
    args = parser.parse_args()
    
    if args.help_json:
        print(json.dumps(get_capabilities(), indent=2))
        sys.exit(0)
    
    if args.command == "echo":
        echo_command(args.text or sys.stdin.read().strip(), args.json)
    else:
        print("Unknown command", file=sys.stderr)
        sys.exit(1)
```

### 9.2 使用示例

```bash
# 保存为 echo-agent
chmod +x echo-agent

# 测试能力查询
./echo-agent --help-json

# 测试基础调用
./echo-agent echo "Hello CAP!"

# 测试 JSON 输出
./echo-agent echo "Hello CAP!" --json

# 测试管道
echo "Pipeline test" | ./echo-agent echo --json
```

## 10. 版本演进策略

### 10.1 版本兼容性

- **向后兼容**：新版本必须支持旧版本的基础功能
- **渐进增强**：新功能通过可选字段和命令添加
- **明确废弃**：废弃功能有 6 个月过渡期

### 10.2 版本检查

```bash
# 检查 CAP 版本
agent-cli --version
# 输出: agent-cli v1.0.0 (CAP v0.1)

# 检查兼容性
cap-validator check ./agent-cli
# 输出: ✅ CAP v0.1 compatible
```

## 11. 社区与生态

### 11.1 认证流程

1. **自我声明**：Agent 开发者声明 CAP 兼容
2. **自动测试**：通过 `cap-validator` 工具验证
3. **社区验证**：社区成员测试和反馈
4. **官方认证**：通过完整测试套件

### 11.2 注册中心

```yaml
# agent-registry.yaml
name: "gpt4-cli"
description: "OpenAI GPT-4 CLI Agent"
version: "1.0.0"
cap_version: "0.1"
author: "OpenAI"
license: "MIT"
repository: "https://github.com/openai/gpt4-cli"
install_cmd: "npm install -g gpt4-cli"
commands: ["chat", "generate", "analyze"]
capabilities: ["text-generation", "analysis"]
```

## 12. 路线图

### v0.1 (Current Draft)
- [x] 基础协议规范
- [x] 核心命令格式
- [x] JSON 输出标准
- [ ] 社区反馈收集

### v0.2 (Next)
- [ ] 流式输出标准化
- [ ] 多模态支持
- [ ] 插件机制
- [ ] 错误处理完善

### v1.0 (Target)
- [ ] 完整实现规范
- [ ] 大规模生态验证
- [ ] 性能基准测试
- [ ] 企业级功能

---

## 征求意见

这是 CLI-Agent Protocol v0.1 的早期草稿。我们欢迎社区的反馈和建议：

- 🐛 **问题报告**：[GitHub Issues](https://github.com/cli-api/cap-protocol/issues)
- 💡 **功能建议**：[GitHub Discussions](https://github.com/cli-api/cap-protocol/discussions)
- 📝 **规范改进**：[Pull Requests](https://github.com/cli-api/cap-protocol/pulls)
- 💬 **社区交流**：[Discord Channel](https://discord.gg/cap-protocol)

**关键问题征询**：

1. 命令格式是否足够简洁而强大？
2. JSON Schema 的能力描述是否完整？
3. 认证和安全模型是否合适？
4. 网络协议桥接是否必要？
5. 实现复杂度是否合理？

让我们一起构建 AI Agent 的统一未来！🚀