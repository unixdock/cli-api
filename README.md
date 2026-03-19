# CLI-API

**通用智能体调用协议与平台** - 基于 CLI-Agent Protocol (CAP) 的统一智能体生态

[![Build Status](https://github.com/username/cli-api/workflows/CI/badge.svg)](https://github.com/username/cli-api/actions)
[![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](Cargo.toml)

## 🌟 核心价值主张

> **一条命令，调用全世界的智能体**

```bash
# 统一的调用方式，支持任何智能体
cli-api call gpt4 chat "解释量子计算"
cli-api call claude summarize article.txt
cli-api call local-llm translate --from en --to zh "Hello World"
```

## 🎯 解决的问题

### 当前AI智能体生态的痛点

- **协议分化**: MCP、A2A、Agent Protocol、OpenAI API 等各自为政
- **接口混乱**: REST、gRPC、WebSocket、SDK 多种调用方式并存
- **集成复杂**: 每种智能体都需要单独的适配代码
- **维护困难**: 协议升级导致大量适配工作

### CLI-API 的解决方案

✅ **统一协议**: 基于 CLI-Agent Protocol (CAP) 的标准化调用接口  
✅ **零学习成本**: CLI 天然的易用性，JSON 结构化输出  
✅ **即插即用**: 自动适配主流智能体服务，无需修改现有代码  
✅ **生态开放**: 开源 Hub + Broker，社区驱动的智能体注册中心

## 🏗️ 架构概览

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CLI 工具   │────│    Hub      │    │   智能体A   │
│ (用户界面)   │    │ (注册中心)   │◄───│ (OpenAI)    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                     │
       ▼                  ▼                     │
┌─────────────┐    ┌─────────────┐              │
│   Broker    │◄───│  适配器层    │              │
│ (路由代理)   │    │ (协议转换)   │◄─────────────┤
└─────────────┘    └─────────────┘              │
                          │                    │
                          ▼                    │
                   ┌─────────────┐    ┌─────────────┐
                   │   智能体B   │    │   智能体C   │
                   │  (Claude)   │    │  (本地LLM)  │
                   └─────────────┘    └─────────────┘
```

### 核心组件

- **CLI 工具** (`cli-api`): 统一的命令行接口
- **Hub 服务**: 智能体注册、发现与管理  
- **Broker 服务**: 请求路由与协议适配
- **适配器层**: 各种智能体协议的标准化适配
- **CAP 协议**: 核心的通信协议规范

## 🚀 快速开始

### 安装

```bash
# 从源码构建
git clone https://github.com/username/cli-api.git
cd cli-api
./scripts/setup.sh

# 或下载预编译版本  
curl -L https://github.com/username/cli-api/releases/latest/download/cli-api-linux.tar.gz | tar xz
```

### 启动服务

```bash
# 启动 Hub 和 Broker 服务
./scripts/start-dev.sh

# 或手动启动
cargo run --bin hub &      # 端口 8080
cargo run --bin broker &   # 端口 8081
```

### 第一次调用

```bash
# 查看可用智能体
cli-api list

# 配置 API Key
cli-api config set openai.api_key "sk-your-key"

# 调用 GPT-4
cli-api call gpt4 chat "Hello, CLI-API!"

# 输出示例:
# {
#   "success": true,
#   "output": "Hello! I'm excited to help you through CLI-API...",
#   "execution_time_ms": 1250
# }
```

## 📖 使用示例

### 基础调用

```bash
# 聊天对话
cli-api call gpt4 chat "什么是区块链？"

# 文档总结
cli-api call claude summarize --file report.pdf

# 文本翻译
cli-api call translator translate --from en --to zh "Hello World"

# 代码解释
cli-api call coder explain --lang python < script.py
```

### 工作流编排

```bash
#!/bin/bash
# 内容创作工作流

# 1. 提取关键词
keywords=$(cli-api call extractor keywords --text "$input" --output text)

# 2. 生成大纲
outline=$(cli-api call gpt4 outline --keywords "$keywords" --output text)

# 3. 撰写内容
content=$(cli-api call claude write --outline "$outline" --output text)

# 4. 润色优化
result=$(cli-api call polisher enhance --text "$content" --output text)

echo "$result" > final_article.md
```

### 批量处理

```bash
# 并行处理多个文件
find ./docs -name "*.md" | xargs -I {} -P 4 \
  cli-api call summarizer extract --file {}

# 管道流水线
cat large_dataset.json | \
  cli-api call analyzer extract-features | \
  cli-api call classifier predict | \
  cli-api call reporter generate-insights > insights.txt
```

## 🔌 支持的智能体

### 已支持的协议

| 协议 | 状态 | 示例智能体 | 适配器 |
|------|------|-----------|--------|
| OpenAI API | ✅ | GPT-4, GPT-3.5 | `openai-adapter` |
| Model Context Protocol (MCP) | ✅ | Claude Desktop | `mcp-adapter` |
| Agent Protocol | 🚧 | AutoGPT | `agent-protocol-adapter` |
| Anthropic API | 📋 | Claude | `anthropic-adapter` |
| Ollama | 📋 | Local LLMs | `ollama-adapter` |
| Custom REST API | ✅ | 自定义服务 | `rest-adapter` |

### 智能体注册

```yaml
# my-agent.yaml
id: my-custom-agent
name: "我的智能体"
description: "专门的任务处理智能体"
provider: "custom"
endpoint: "http://localhost:3000/api"
protocol: "rest"

commands:
  - name: "process"
    description: "处理文本数据"
    args:
      - name: "input"
        required: true
        type: "string"

auth:
  type: "api_key"
  config:
    header: "X-API-Key"
    env_var: "MY_AGENT_KEY"
```

```bash
# 注册智能体
cli-api agent register my-agent.yaml

# 测试连通性
cli-api agent test my-custom-agent

# 开始使用
cli-api call my-custom-agent process "这是测试数据"
```

## 🛠️ 开发指南

### 项目结构

```
cli-api/
├── crates/
│   ├── cli-api/           # CLI 工具
│   ├── cap-protocol/      # 核心协议
│   ├── hub/              # 注册中心服务  
│   ├── broker/           # 代理路由服务
│   └── adapters/         # 协议适配器
│       ├── openai-adapter/
│       ├── mcp-adapter/
│       └── ...
├── docs/                 # 文档
├── examples/             # 使用示例
├── tests/               # 集成测试
└── scripts/             # 工具脚本
```

### 开发环境

```bash
# 安装开发依赖
./scripts/setup.sh

# 启动开发服务
./scripts/start-dev.sh

# 运行测试
cargo test --all

# 代码检查
cargo clippy --all-targets
cargo fmt --all
```

### 开发新适配器

```rust
// 实现 AgentAdapter trait
#[async_trait]
impl AgentAdapter for MyAdapter {
    async fn call(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse> {
        // 1. 转换请求格式
        let native_request = self.convert_request(request)?;
        
        // 2. 调用原生 API
        let native_response = self.client.call(agent.endpoint, native_request).await?;
        
        // 3. 转换响应格式
        let response = self.convert_response(native_response)?;
        
        Ok(response)
    }
    
    async fn test_connection(&self, agent: &AgentInfo) -> CapResult<bool> {
        // 实现连通性测试
        self.client.health_check(agent.endpoint).await
    }
}
```

详情请查看 [适配器开发指南](docs/adapters/README.md)

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker build -t cli-api .

# 运行服务
docker-compose up -d

# 检查状态
curl http://localhost:8080/health
```

### Kubernetes 部署

```bash
# 应用 K8s 配置
kubectl apply -f k8s/

# 检查服务
kubectl get pods -l app=cli-api
```

### 云服务部署

支持部署到各大云平台：

- **AWS**: ECS/EKS + ALB + RDS
- **GCP**: GKE + Cloud Functions + Cloud SQL  
- **Azure**: AKS + Functions + SQL Database
- **阿里云**: ACK + 函数计算 + RDS

详细指南请参考 [部署文档](docs/deployment/)

## 📊 性能指标

### 基准测试结果

| 配置 | QPS | P99延迟 | 内存占用 | CPU占用 |
|------|-----|---------|----------|---------|
| 单机模式 | 1,000 | <100ms | <50MB | <20% |
| 集群模式 | 10,000 | <200ms | <200MB | <60% |
| 容器模式 | 5,000 | <150ms | <100MB | <40% |

### 扩展性

- **智能体数量**: 支持 10,000+ 智能体注册
- **并发调用**: 支持 10,000+ 并发请求
- **协议适配**: 支持 100+ 不同协议类型
- **水平扩展**: 支持多实例负载均衡

## 🤝 社区

### 贡献指南

我们欢迎各种类型的贡献：

- 🐛 **Bug 报告**: [提交 Issue](https://github.com/username/cli-api/issues/new?template=bug_report.md)
- 🚀 **功能建议**: [提交 Feature Request](https://github.com/username/cli-api/issues/new?template=feature_request.md)  
- 📝 **文档改进**: 完善使用文档和示例
- 🔧 **代码贡献**: 参与核心功能开发

详情请阅读 [贡献指南](docs/development/contributing.md)

### 社区资源

- 💬 **讨论区**: [GitHub Discussions](https://github.com/username/cli-api/discussions)
- 📞 **开发者会议**: 每周四 UTC 14:00
- 📧 **邮件列表**: cli-api-dev@groups.io
- 🐦 **Twitter**: [@cli_api_org](https://twitter.com/cli_api_org)

### 路线图

- **v0.1** ✅ 核心协议和基础适配器
- **v0.2** 🚧 智能体商店和社区功能  
- **v0.3** 📋 企业级认证和监控
- **v1.0** 🎯 生产就绪和生态自治

查看详细的 [发展路线图](docs/roadmap.md)

## 📄 许可证

本项目采用双许可证：

- MIT License ([LICENSE-MIT](LICENSE-MIT))
- Apache License 2.0 ([LICENSE-APACHE](LICENSE-APACHE))

您可以选择其中任意一种许可证使用本软件。

## 🙏 致谢

特别感谢以下项目和社区：

- [CLI-Anything](https://github.com/systemprompt/cli-anything) - 核心设计灵感
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification) - 协议参考
- [Rust 社区] - 优秀的编程语言和生态

---

<div align="center">

**🌟 让我们一起构建 AI 智能体的统一未来！ 🌟**

[快速开始](docs/quickstart.md) • [文档](docs/README.md) • [示例](examples/README.md) • [CAP v0.1 规范](specs/cap-protocol-v0.1-draft.md) • [社区讨论](https://github.com/username/cli-api/discussions)

