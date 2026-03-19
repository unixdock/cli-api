//! CLI-Agent Protocol (CAP) - 核心协议定义
//! 
//! CLI-Agent Protocol 是基于 CLI-Anything 设计的标准化智能体调用协议，
//! 提供统一的接口规范来调用各种智能体服务。

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

/// CAP 协议版本
pub const CAP_VERSION: &str = "1.0.0";

/// 智能体调用请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentRequest {
    pub id: Uuid,
    pub agent_id: String,
    pub command: String,
    pub args: Vec<String>,
    pub input: Option<String>,
    pub context: Option<HashMap<String, serde_json::Value>>,
    pub metadata: HashMap<String, String>,
}

/// 智能体调用响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResponse {
    pub id: Uuid,
    pub success: bool,
    pub output: Option<String>,
    pub error: Option<String>,
    pub metadata: HashMap<String, String>,
    pub execution_time_ms: u64,
}

/// 智能体元信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentInfo {
    pub id: String,
    pub name: String,
    pub description: String,
    pub version: String,
    pub provider: String,
    pub commands: Vec<AgentCommand>,
    pub capabilities: Vec<String>,
    pub endpoint: String,
    pub protocol: ProtocolType,
    pub auth: Option<AuthConfig>,
}

/// 智能体命令定义
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentCommand {
    pub name: String,
    pub description: String,
    pub args: Vec<CommandArg>,
    pub examples: Vec<String>,
}

/// 命令参数定义
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommandArg {
    pub name: String,
    pub description: String,
    pub required: bool,
    pub arg_type: ArgType,
    pub default: Option<String>,
}

/// 参数类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ArgType {
    String,
    Integer,
    Boolean,
    File,
    Json,
}

/// 协议类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProtocolType {
    Cap,      // 原生 CLI-Agent Protocol
    Mcp,      // Model Context Protocol
    A2A,      // Agent-to-Agent
    AgentProtocol,  // Agent Protocol
    OpenAI,   // OpenAI API
    Rest,     // 通用 REST API
    Grpc,     // gRPC
}

/// 认证配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthConfig {
    pub auth_type: AuthType,
    pub config: HashMap<String, String>,
}

/// 认证类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AuthType {
    None,
    ApiKey,
    Bearer,
    Basic,
    OAuth2,
}

/// CAP 协议错误类型
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

/// CAP 协议结果类型
pub type CapResult<T> = Result<T, CapError>;