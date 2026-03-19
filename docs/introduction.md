# CLI-API 项目介绍

## 🌟 项目愿景

**CLI-API 的终极愿景：任何开发者只需一条 `cli-api call` 命令，即可调用全球任意智能体服务，实现"写一次CLI，调用全世界Agent"。**

## 🎯 核心使命

### 1. 解决当前痛点

当前AI智能体生态高度碎片化：

- **协议不统一**: MCP、A2A、ACP、Agent Protocol等各自为政
- **调用方式混乱**: REST、gRPC、SDK、GUI等多种接口并存  
- **集成成本极高**: 开发者需要维护多套适配器，Agent间协作困难

### 2. CLI-Anything 的启发

[CLI-Anything](https://github.com/systemprompt/cli-anything) 项目证明了：

✅ **CLI + JSON结构化输出 + --help自描述** 是AI Agent最自然的"通用语言"

✅ **无需持久化上下文**：每次调用都是独立的，简化了状态管理

✅ **完美支持REPL**：可以在交互式环境中无缝使用

✅ **100%测试通过**：CLI接口天然易于测试和验证

## 🏗️ 技术架构

### CLI-Agent Protocol (CAP)

基于 CLI-Anything 设计理念，扩展为跨服务、跨Agent的标准化协议：

```json
{
  "id": "uuid",
  "agent_id": "gpt4",
  "command": "chat", 
  "args": ["Hello, world!"],
  "input": "optional_input_text",
  "context": {},
  "metadata": {}
}
```

### 核心组件

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CLI 工具   │───▶│    Hub      │◀───│   智能体A   │
│ cli-api call│    │  (注册中心)  │    │   (MCP)     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Broker    │    │  适配器层   │◀───│   智能体B   │
│  (路由层)    │◀───│             │    │ (OpenAI API)│  
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 核心特性

### ✨ 开发者友好

```bash
# 一条命令调用任意智能体
cli-api call gpt4 chat "解释量子计算"

# 自动发现可用智能体  
cli-api list

# 智能体信息查看
cli-api info claude-3

# 批量调用和管道操作
echo "数据" | cli-api call analyzer process
```

### 🌍 生态整合

```yaml
# agent-registry.yaml
agents:
  - id: gpt4
    provider: openai
    protocol: openai-api
    endpoint: https://api.openai.com/v1
    
  - id: claude
    provider: anthropic  
    protocol: mcp
    endpoint: ws://localhost:8080/mcp
    
  - id: local-llm
    provider: ollama
    protocol: rest
    endpoint: http://localhost:11434
```

### 📦 即插即用

- **零配置启动**: `cargo run --bin cli-api`
- **自动适配**: 支持主流协议的开箱即用适配器
- **热插拔**: 运行时动态注册/注销智能体
- **容器友好**: 完整 Docker/K8s 支持

## 🎯 使用场景

### 1. 统一调用入口
```bash
# 不同提供商的智能体，统一调用方式
cli-api call gpt4 generate --prompt "写一篇博客"
cli-api call claude summarize --text "长文本内容"  
cli-api call local-llm translate --from en --to zh
```

### 2. Agent 编排
```bash
# 智能体工作流
cli-api call analyzer extract-keywords < article.txt | \
cli-api call gpt4 expand-outline | \  
cli-api call claude polish-content > final.md
```

### 3. 开发集成
```rust
// Rust 代码中调用
use cap_protocol::*;

let request = AgentRequest {
    agent_id: "gpt4".to_string(),
    command: "chat".to_string(),
    args: vec!["Hello!".to_string()],
    ..Default::default()
};

let response = broker.call_agent(&request).await?;
```

## 🗺️ 发展路线图

### Phase 1: 基础设施 (v0.1) ✅
- [x] CAP 协议定义
- [x] 核心 CLI 工具
- [x] Hub/Broker 服务
- [x] 基础适配器 (OpenAI, MCP)

### Phase 2: 生态建设 (v0.2) 🚧  
- [ ] 更多协议适配器 (A2A, Agent Protocol)
- [ ] 智能体商店 (官方注册中心)
- [ ] 社区贡献工具链
- [ ] 性能优化

### Phase 3: 企业增强 (v0.3) 📋
- [ ] 认证授权体系  
- [ ] 负载均衡与容错
- [ ] 监控告警系统
- [ ] 企业级部署工具

### Phase 4: 智能化演进 (v1.0) 🎯
- [ ] 自动协议发现
- [ ] 智能路由优化  
- [ ] Agent 自动组织
- [ ] 生态自治系统

## 🤝 参与贡献

CLI-API 是一个开源项目，我们欢迎各种形式的贡献：

- 🐛 **Bug 报告**: [提交 Issue](https://github.com/username/cli-api/issues)
- 💡 **功能建议**: [讨论区](https://github.com/username/cli-api/discussions)  
- 🔧 **代码贡献**: [贡献指南](development/contributing.md)
- 📚 **文档改进**: 完善使用文档和示例

---

**让我们一起构建AI智能体的统一未来！** 🚀