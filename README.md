# cli-api
$ cli-api --help #CLI-API：一条命令，统一未来


# CLI-First通用协议（CAP）
核心规范：cli-api <service> <action> [args] --json --session
自描述：--help自动返回JSON Schema + capability清单（能力发现）。
状态管理：内置REPL Skin + undo/redo（复用CLI-Anything的ReplSkin）。
语义扩展：新增--agent-role、--chain、--monitor（支持多Agent编排与实时监控）。
与现有协议兼容：自动翻译MCP/A2A/ACP为CAP命令（双向桥接）。

# 智能聚合Hub（Marketplace）
自动适配器生成：借鉴CLI-Anything 7阶段流水线，为任意智能体服务（即使无开源代码）生成CAP wrapper。
社区驱动：一键提交cli-api register openai-assistants即自动生成适配器并上架。
智能Broker：根据任务复杂度、成本、延迟、隐私自动路由到最佳后端Agent（类似Load Balancer for Agents）。

# Agent-to-Agent原生协作
支持cli-api chain grok-researcher -> claude-writer -> grok-reviewer一条命令完成端到端工作流。
内置共享内存与事件总线（Redis-backed可选），真正实现“Agent即微服务”。

# 本地优先 + 隐私保护
支持Ollama/LM Studio本地Agent零配置接入。
所有调用默认本地转发，敏感数据永不离开用户环境。

# 创新计量与生态
cli-api usage实时展示跨服务消耗（token/credit统一折算）。
开源插件市场：开发者可发布“Agent Skill Packs”（e.g. 科研Agent套件、金融Agent套件）。
