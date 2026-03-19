# CLI-Agent Protocol (CAP) 字段

CAP 是 CLI-API 的核心协议，定义了智能体调用的标准化接口。

## 🛠️ 协议设计原则

### 1. CLI 优先
- 基于命令行接口设计，天然支持脚本化
- JSON 结构化输出，便于程序解析  
- `--help` 自描述，无需额外文档

### 2. 无状态设计
- 每次调用都是独立的，无需会话管理
- 简化错误处理和故障恢复
- 便于负载均衡和水平扩展

### 3. 扩展友好
- 开放的 metadata 字段支持自定义扩展
- 向后兼容的版本演进策略
- 灵活的认证和授权机制

## 📦 核心数据结构

### AgentRequest - 智能体调用请求

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentRequest {
    pub id: Uuid,                                    // 唯一请求ID
    pub agent_id: String,                           // 智能体标识符  
    pub command: String,                            // 要执行的命令
    pub args: Vec<String>,                          // 命令参数列表
    pub input: Option<String>,                      // 可选的输入文本
    pub context: Option<HashMap<String, Value>>,     // 上下文信息
    pub metadata: HashMap<String, String>,          // 元数据
}
```

#### 字段说明

- `id`: UUID v4，用于请求跟踪和去重
- `agent_id`: 智能体的唯一标识符，如 "gpt4", "claude-3"
- `command`: 要执行的命令名称，如 "chat", "summarize"  
- `args`: 位置参数列表，类似 CLI 的 argv
- `input`: 可选的输入内容，支持大文本或文件内容
- `context`: 额外的上下文信息，如会话ID、用户偏好等
- `metadata`: 元数据键值对，用于扩展和调试

#### 使用示例

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_id": "gpt4", 
  "command": "chat",
  "args": ["解释什么是量子计算"],
  "input": null,
  "context": {
    "user_id": "user123",
    "session_id": "sess456"
  },
  "metadata": {
    "client": "cli-api/1.0.0",
    "timestamp": "2024-03-18T10:30:00Z"
  }
}
```

### AgentResponse - 智能体调用响应

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResponse {
    pub id: Uuid,                                  // 对应的请求ID
    pub success: bool,                             // 调用是否成功
    pub output: Option<String>,                    // 输出内容
    pub error: Option<String>,                     // 错误信息
    pub metadata: HashMap<String, String>,         // 响应元数据  
    pub execution_time_ms: u64,                    // 执行时间(毫秒)
}
```

#### 字段说明

- `id`: 与请求 ID 对应，用于关联请求和响应
- `success`: 布尔值，指示调用是否成功 
- `output`: 成功时的输出内容，通常是文本或 JSON
- `error`: 失败时的错误描述信息
- `metadata`: 响应相关的元数据，如 token 使用量等
- `execution_time_ms`: 智能体实际执行时间

#### 使用示例

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "success": true,
  "output": "量子计算是利用量子力学现象进行信息处理的技术...",
  "error": null,
  "metadata": {
    "model": "gpt-4",
    "tokens_used": "150", 
    "cost_usd": "0.003"
  },
  "execution_time_ms": 1250
}
```

### AgentInfo - 智能体元信息

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentInfo {
    pub id: String,                                // 智能体ID
    pub name: String,                              // 显示名称
    pub description: String,                       // 详细描述  
    pub version: String,                           // 版本号
    pub provider: String,                          // 提供商
    pub commands: Vec<AgentCommand>,               // 支持的命令
    pub capabilities: Vec<String>,                 // 能力标签
    pub endpoint: String,                          // 服务端点
    pub protocol: ProtocolType,                    // 协议类型
    pub auth: Option<AuthConfig>,                  // 认证配置
}
```

### AgentCommand - 命令定义

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentCommand {
    pub name: String,                              // 命令名称
    pub description: String,                       // 命令描述
    pub args: Vec<CommandArg>,                     // 参数定义
    pub examples: Vec<String>,                     // 使用示例
}
```

### CommandArg - 参数定义

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommandArg {
    pub name: String,                              // 参数名称
    pub description: String,                       // 参数描述
    pub required: bool,                            // 是否必需
    pub arg_type: ArgType,                         // 参数类型
    pub default: Option<String>,                   // 默认值
}
```

## 🔧 协议类型

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProtocolType {
    Cap,              // CLI-Agent Protocol (原生)
    Mcp,              // Model Context Protocol  
    A2A,              // Agent-to-Agent
    AgentProtocol,    // Agent Protocol 标准
    OpenAI,           // OpenAI API
    Rest,             // 通用 REST API
    Grpc,             // gRPC
}
```

## 🔐 认证机制

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthConfig {
    pub auth_type: AuthType,
    pub config: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AuthType {
    None,             // 无认证
    ApiKey,           // API Key  
    Bearer,           // Bearer Token
    Basic,            // HTTP Basic Auth
    OAuth2,           // OAuth 2.0
}
```

### 认证配置示例

```json
{
  "auth_type": "Bearer",
  "config": {
    "token_env": "OPENAI_API_KEY",
    "header_name": "Authorization", 
    "prefix": "Bearer "
  }
}
```

## ⚡ 错误处理

```rust
#[derive(Debug, thiserror::Error)]
pub enum CapError {
    #[error("Agent not found: {0}")]
    AgentNotFound(String),
    
    #[error("Command not found: {0}")]  
    CommandNotFound(String),
    
    #[error("Protocol error: {0}")]
    ProtocolError(String),
    
    #[error("Authentication error: {0}")]
    AuthError(String),
    
    #[error("Network error: {0}")]
    NetworkError(String),
    
    #[error("Serialization error: {0}")]
    SerializationError(String),
}
```

## 📏 协议限制

### 参数限制
- 单个请求最大大小：10MB
- 参数数量限制：1000个
- 参数名称长度：255字符
- 响应超时时间：默认30秒

### 安全限制  
- 强制 HTTPS (生产环境)
- 请求频率限制：1000/分钟/IP
- 认证 token 有效期管理
- 敏感信息脱敏记录

## 🔄 版本兼容性

### 当前版本：1.0.0

- 遵循语义化版本控制 (SemVer)
- 向后兼容承诺：同主版本内兼容
- 废弃字段渐进式移除策略
- 新字段可选，默认值兜底

### 版本协商

```json
{
  "cap_version": "1.0.0",
  "supported_versions": ["1.0.0", "0.9.x"],
  "min_version": "0.9.0"
}
```

---

📚 **更多信息**
- [协议实现指南](implementation.md)
- [适配器开发](../adapters/README.md)
- [最佳实践](../guides/best-practices.md)