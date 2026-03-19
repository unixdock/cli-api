//! MCP (Model Context Protocol) 适配器

use async_trait::async_trait;
use cap_protocol::*;
use serde_json::Value;
use std::collections::HashMap;

pub struct McpAdapter {
    client: reqwest::Client,
}

impl McpAdapter {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl super::AgentAdapter for McpAdapter {
    async fn call(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse> {
        // TODO: 实现 MCP 协议调用
        Ok(AgentResponse {
            id: request.id,
            success: true,
            output: Some("MCP adapter response".to_string()),
            error: None,
            metadata: HashMap::new(),
            execution_time_ms: 0,
        })
    }
    
    async fn test_connection(&self, agent: &AgentInfo) -> CapResult<bool> {
        // TODO: 实现 MCP 连接测试
        Ok(true)
    }
}