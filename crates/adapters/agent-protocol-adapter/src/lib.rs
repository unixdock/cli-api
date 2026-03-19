//! Agent Protocol 适配器

use async_trait::async_trait;
use cap_protocol::*;
use serde_json::Value;
use std::collections::HashMap;

pub struct AgentProtocolAdapter {
    client: reqwest::Client,
}

impl AgentProtocolAdapter {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl super::AgentAdapter for AgentProtocolAdapter {
    async fn call(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse> {
        // TODO: 实现 Agent Protocol 调用
        Ok(AgentResponse {
            id: request.id,
            success: true,
            output: Some("Agent Protocol adapter response".to_string()),
            error: None,
            metadata: HashMap::new(),
            execution_time_ms: 0,
        })
    }
    
    async fn test_connection(&self, agent: &AgentInfo) -> CapResult<bool> {
        // TODO: 实现 Agent Protocol 连接测试
        Ok(true)
    }
}