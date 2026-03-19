# CLI-Agent Protocol (CAP) 规范

CLI-Agent Protocol (CAP) version 0.1 - 早期草稿

## 概述

CLI-Agent Protocol 是基于 CLI-Anything 设计理念的标准化智能体调用协议。目标是让任意智能体服务统一暴露为 CLI-native 接口，实现"一条命令调用全球Agent"。

## 设计哲学

1. **CLI优先**: CLI 是 Agent 最自然的控制语言
2. **自描述**: 通过 `--help --json` 提供机器可读元数据  
3. **JSON输出**: 强制支持结构化数据交换
4. **零依赖**: 易于桥接，支持本地和网络部署
5. **隐私优先**: 支持离线运行，数据可控

## 协议版本

当前版本: 0.1 (草稿阶段)

支持语义化版本控制 (SemVer)

## 核心命令格式

```bash
agent-cli <command> [arguments] [options]
```

### 强制选项

- `--help` : 输出机器可读的能力描述
- `--json` : 强制 JSON 输出格式
- `--jsonl` : JSONL 流式输出
- `--timeout <seconds>` : 超时控制
- `--version` : 版本信息
- `--capabilities` : 完整能力描述

## 响应格式

### 成功响应

```json
{
  "success": true,
  "output": "响应内容",
  "type": "text|json|binary|stream",
  "metadata": {
    "command": "执行的命令",
    "duration_ms": 1250,
    "tokens_used": 150,
    "timestamp": "2026-03-18T16:30:00Z"
  },
  "cap_version": "0.1"
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "TIMEOUT|AUTH_FAILED|RATE_LIMIT|INVALID_INPUT",
  "metadata": {
    "command": "执行的命令",
    "duration_ms": 5000,
    "timestamp": "2026-03-18T16:30:00Z"
  },
  "cap_version": "0.1"
}
```

## 能力描述格式

```json
{
  "agent_info": {
    "name": "Agent名称",
    "version": "1.0.0", 
    "cap_version": "0.1",
    "provider": "提供商",
    "description": "Agent描述"
  },
  "commands": [
    {
      "name": "命令名称",
      "description": "命令描述",
      "usage": "使用方法",
      "args": [...],
      "options": [...],
      "examples": [...]
    }
  ],
  "capabilities": ["text-generation", "analysis", ...],
  "constraints": {
    "max_input_length": 8192,
    "rate_limit": "60/minute"
  }
}
```

## 实现层级

### Tier 1 - 最小实现
- ✅ 支持 `--help --json`
- ✅ 至少一个核心命令
- ✅ 标准化错误处理

### Tier 2 - 标准实现  
- ✅ 多核心命令支持
- ✅ 流式输出
- ✅ 配置管理

### Tier 3 - 完整实现
- ✅ HTTP 接口桥接
- ✅ 插件扩展
- ✅ 多模态支持

## 版本兼容性

- 向后兼容承诺
- 语义化版本控制
- 渐进式功能增强

## 详细规范

本文档为 CAP 协议的简化概览。完整的规范文档请查看：

📖 **[CAP v0.1 完整草稿](cap-protocol-v0.1-draft.md)** - 详细的协议规范、示例实现和社区指南

---

## 征求反馈

CAP v0.1 目前处于草稿阶段，欢迎社区提供反馈：

- 🐛 [问题报告](https://github.com/cli-api/cap-protocol/issues)
- 💡 [功能建议](https://github.com/cli-api/cap-protocol/discussions)  
- 📝 [规范改进](https://github.com/cli-api/cap-protocol/pulls)

让我们一起构建 AI Agent 的统一未来！🚀