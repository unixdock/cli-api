//! CLI-API Hub - 智能体注册与发现服务
//! 
//! Hub 提供集中式的智能体注册、发现和管理服务

use anyhow::Result;
use cap_protocol::*;
use serde_json::Value;
use std::collections::HashMap;
use tracing::{info, error};
use uuid::Uuid;

pub struct Hub {
    agents: HashMap<String, AgentInfo>,
    categories: HashMap<String, Vec<String>>,
    providers: HashMap<String, Vec<String>>,
}

impl Hub {
    pub fn new() -> Self {
        Self {
            agents: HashMap::new(),
            categories: HashMap::new(),
            providers: HashMap::new(),
        }
    }
    
    /// 注册智能体
    pub async fn register_agent(&mut self, agent: AgentInfo) -> CapResult<()> {
        info!("Registering agent: {} ({})", agent.name, agent.id);
        
        // 更新分类索引
        for category in &agent.capabilities {
            self.categories
                .entry(category.clone())
                .or_insert_with(Vec::new)
                .push(agent.id.clone());
        }
        
        // 更新提供商索引
        self.providers
            .entry(agent.provider.clone())
            .or_insert_with(Vec::new)
            .push(agent.id.clone());
            
        self.agents.insert(agent.id.clone(), agent);
        
        Ok(())
    }
    
    /// 注销智能体
    pub async fn unregister_agent(&mut self, agent_id: &str) -> CapResult<()> {
        info!("Unregistering agent: {}", agent_id);
        
        if let Some(agent) = self.agents.remove(agent_id) {
            // 清理索引
            for category in &agent.capabilities {
                if let Some(agent_list) = self.categories.get_mut(category) {
                    agent_list.retain(|id| id != agent_id);
                }
            }
            
            if let Some(agent_list) = self.providers.get_mut(&agent.provider) {
                agent_list.retain(|id| id != agent_id);
            }
            
            Ok(())
        } else {
            Err(CapError::AgentNotFound(agent_id.to_string()))
        }
    }
    
    /// 获取智能体信息
    pub async fn get_agent(&self, agent_id: &str) -> CapResult<AgentInfo> {
        self.agents
            .get(agent_id)
            .cloned()
            .ok_or_else(|| CapError::AgentNotFound(agent_id.to_string()))
    }
    
    /// 列出智能体
    pub async fn list_agents(
        &self,
        category: Option<&str>,
        provider: Option<&str>,
        search: Option<&str>,
    ) -> CapResult<Vec<AgentInfo>> {
        let mut result: Vec<AgentInfo> = self.agents.values().cloned().collect();
        
        // 按分类过滤
        if let Some(cat) = category {
            result.retain(|agent| agent.capabilities.contains(&cat.to_string()));
        }
        
        // 按提供商过滤
        if let Some(prov) = provider {
            result.retain(|agent| agent.provider == prov);
        }
        
        // 按搜索词过滤
        if let Some(search_term) = search {
            let search_lower = search_term.to_lowercase();
            result.retain(|agent| {
                agent.name.to_lowercase().contains(&search_lower)
                    || agent.description.to_lowercase().contains(&search_lower)
            });
        }
        
        Ok(result)
    }
    
    /// 获取分类列表
    pub async fn get_categories(&self) -> CapResult<Vec<String>> {
        Ok(self.categories.keys().cloned().collect())
    }
    
    /// 获取提供商列表
    pub async fn get_providers(&self) -> CapResult<Vec<String>> {
        Ok(self.providers.keys().cloned().collect())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();
    
    info!("CLI-API Hub starting...");
    
    let mut hub = Hub::new();
    
    // 注册示例智能体
    let example_agents = vec![
        AgentInfo {
            id: "gpt4".to_string(),
            name: "OpenAI GPT-4".to_string(),
            description: "OpenAI GPT-4 language model".to_string(),
            version: "1.0.0".to_string(),
            provider: "openai".to_string(),
            commands: vec![
                AgentCommand {
                    name: "chat".to_string(),
                    description: "Chat with GPT-4".to_string(),
                    args: vec![
                        CommandArg {
                            name: "message".to_string(),
                            description: "Message to send".to_string(),
                            required: true,
                            arg_type: ArgType::String,
                            default: None,
                        },
                    ],
                    examples: vec!["cli-api call gpt4 chat \"Hello, world!\"".to_string()],
                },
            ],
            capabilities: vec!["chat".to_string(), "text-generation".to_string()],
            endpoint: "https://api.openai.com/v1".to_string(),
            protocol: ProtocolType::OpenAI,
            auth: Some(AuthConfig {
                auth_type: AuthType::Bearer,
                config: HashMap::new(),
            }),
        },
    ];
    
    for agent in example_agents {
        hub.register_agent(agent).await?;
    }
    
    info!("Hub initialized with {} agents", hub.agents.len());
    
    // TODO: 启动 HTTP 服务器
    info!("Hub is running at http://localhost:8080");
    
    // 保持服务运行
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
    }
}