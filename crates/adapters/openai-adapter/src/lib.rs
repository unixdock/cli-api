//! OpenAI API 适配器

use async_trait::async_trait;
use cap_protocol::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

pub struct OpenAIAdapter {
    client: reqwest::Client,
}

#[derive(Serialize)]
struct OpenAIRequest {
    model: String,
    messages: Vec<OpenAIMessage>,
    max_tokens: Option<u32>,
    temperature: Option<f32>,
}

#[derive(Serialize, Deserialize)]
struct OpenAIMessage {
    role: String,
    content: String,
}

#[derive(Deserialize)]
struct OpenAIResponse {
    choices: Vec<OpenAIChoice>,
    usage: Option<OpenAIUsage>,
}

#[derive(Deserialize)]
struct OpenAIChoice {
    message: OpenAIMessage,
    finish_reason: Option<String>,
}

#[derive(Deserialize)]
struct OpenAIUsage {
    prompt_tokens: u32,
    completion_tokens: u32,
    total_tokens: u32,
}

impl OpenAIAdapter {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl super::AgentAdapter for OpenAIAdapter {
    async fn call(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse> {
        match request.command.as_str() {
            "chat" => self.handle_chat(agent, request).await,
            _ => Err(CapError::CommandNotFound(request.command.clone())),
        }
    }
    
    async fn test_connection(&self, agent: &AgentInfo) -> CapResult<bool> {
        // TODO: 实现连接测试
        Ok(true)
    }
}

impl OpenAIAdapter {
    async fn handle_chat(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse> {
        let message = request.args
            .get(0)
            .or_else(|| request.input.as_ref())
            .ok_or_else(|| CapError::ProtocolError("Missing message".to_string()))?;
        
        let openai_request = OpenAIRequest {
            model: "gpt-4".to_string(),
            messages: vec![
                OpenAIMessage {
                    role: "user".to_string(),
                    content: message.clone(),
                }
            ],
            max_tokens: Some(1000),
            temperature: Some(0.7),
        };
        
        // TODO: 实际的 OpenAI API 调用
        // let response = self.client
        //     .post(&format!("{}/chat/completions", agent.endpoint))
        //     .bearer_token(&api_key)
        //     .json(&openai_request)
        //     .send()
        //     .await
        //     .map_err(|e| CapError::NetworkError(e.to_string()))?;
        
        // 模拟响应
        Ok(AgentResponse {
            id: request.id,
            success: true,
            output: Some(format!("Echo: {}", message)),
            error: None,
            metadata: HashMap::new(),
            execution_time_ms: 0, // 将由调用者设置
        })
    }
}