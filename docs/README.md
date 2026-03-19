# CLI-API 项目文档

欢迎来到 CLI-API 项目文档！这里包含了所有您需要了解的关于 CLI-Agent Protocol (CAP) 和相关工具的信息。

## 文档结构

### 📖 基础文档
- [项目介绍](introduction.md) - 了解 CLI-API 的核心概念和愿景
- [快速开始](quickstart.md) - 5分钟快速上手指南
- [安装指南](installation.md) - 详细的安装说明

### 🔧 核心组件
- [CLI 工具](cli/README.md) - 命令行工具使用指南
- [CAP 协议](protocol/README.md) - CLI-Agent Protocol (CAP) v0.1 规范  
- [Hub 服务](hub/README.md) - 智能体注册与发现
- [Broker 服务](broker/README.md) - 路由与代理服务

### 🔌 适配器
- [适配器开发](adapters/README.md) - 如何开发新的协议适配器
- [OpenAI 适配器](adapters/openai.md) - OpenAI API 集成
- [MCP 适配器](adapters/mcp.md) - Model Context Protocol 支持
- [Agent Protocol 适配器](adapters/agent-protocol.md) - Agent Protocol 兼容性

### 💡 示例与教程
- [基础示例](examples/README.md) - 常见使用场景
- [最佳实践](guides/best-practices.md) - 生产环境建议
- [故障排除](guides/troubleshooting.md) - 常见问题解决

### 🚀 部署与运维
- [Docker 部署](deployment/docker.md) - 容器化部署指南
- [Kubernetes 部署](deployment/kubernetes.md) - K8s 集群部署
- [监控告警](deployment/monitoring.md) - 系统监控配置

### 🔧 开发者指南
- [贡献指南](development/contributing.md) - 如何参与项目开发
- [架构设计](development/architecture.md) - 系统架构详解
- [API 参考](api/README.md) - 完整的 API 文档

## 快速导航

### 🎯 我想...
- **快速试用** → [快速开始](quickstart.md)
- **了解概念** → [项目介绍](introduction.md) 
- **集成现有智能体** → [适配器开发](adapters/README.md)
- **部署到生产** → [Docker 部署](deployment/docker.md)
- **贡献代码** → [贡献指南](development/contributing.md)

### 🛠️ 技术栈
- **语言**: Rust 🦀
- **协议**: CLI-Agent Protocol (CAP) v0.1 草稿
- **架构**: 微服务 + 分布式
- **兼容**: MCP, Agent Protocol, OpenAI API

---

📧 **有问题？** 查看 [FAQ](guides/faq.md) 或 [提交 Issue](https://github.com/username/cli-api/issues)