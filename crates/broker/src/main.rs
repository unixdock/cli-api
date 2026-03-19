//! CLI-API Broker - 智能体调用路由服务  
//!
//! Broker 将 CAP 请求路由到相应的智能体适配器

use async_trait::async_trait;
use anyhow::Result;
use cap_protocol::*;
use std::collections::HashMap;
use tracing::{info, warn, error};
use uuid::Uuid;

pub struct Broker {
    hub_url: String,
    adapters: HashMap<ProtocolType, Box<dyn AgentAdapter>>,
    agent_cache: HashMap<String, AgentInfo>,
}

#[async_trait::async_trait]
pub trait AgentAdapter: Send + Sync {
    async fn call(&self, agent: &AgentInfo, request: &AgentRequest) -> CapResult<AgentResponse>;
    async fn test_connection(&self, agent: &AgentInfo) -> CapResult<bool>;
}

impl Broker {
    pub fn new(hub_url: String) -> Self {
        let mut adapters: HashMap<ProtocolType, Box<dyn AgentAdapter>> = HashMap::new();
        
        // 注册适配器
        // adapters.insert(ProtocolType::Mcp, Box::new(McpAdapter::new()));
        // adapters.insert(ProtocolType::A2A, Box::new(A2AAdapter::new()));
        // adapters.insert(ProtocolType::AgentProtocol, Box::new(AgentProtocolAdapter::new()));
        // adapters.insert(ProtocolType::OpenAI, Box::new(OpenAIAdapter::new()));
        
        Self {
            hub_url,
            adapters,
            agent_cache: HashMap::new(),
        }
    }
    
    /// 调用智能体
    pub async fn call_agent(&mut self, request: &AgentRequest) -> CapResult<AgentResponse> {
        info!("Routing call for agent: {}", request.agent_id);
        
        // 获取智能体信息
        let agent = self.get_agent_info(&request.agent_id).await?;
        
        // 选择适配器
        let adapter = self.adapters
            .get(&agent.protocol)
            .ok_or_else(|| CapError::ProtocolError(format!("Unsupported protocol: {:?}", agent.protocol)))?;
        
        // 执行调用
        let start_time = std::time::Instant::now();
        let mut response = adapter.call(&agent, request).await?;
        response.execution_time_ms = start_time.elapsed().as_millis() as u64;
        
        info!("Call completed for agent: {} in {}ms", request.agent_id, response.execution_time_ms);
        Ok(response)
    }
    
    /// 获取智能体信息（支持缓存）
    async fn get_agent_info(&mut self, agent_id: &str) -> CapResult<AgentInfo> {
        // 检查缓存
        if let Some(agent) = self.agent_cache.get(agent_id) {
            return Ok(agent.clone());
        }
        
        // 从 Hub 获取
        let agent = self.fetch_agent_from_hub(agent_id).await?;
        
        // 更新缓存
        self.agent_cache.insert(agent_id.to_string(), agent.clone());
        
        Ok(agent)
    }
    
    async fn fetch_agent_from_hub(&self, agent_id: &str) -> CapResult<AgentInfo> {
        // TODO: 实际的 Hub API 调用
        Err(CapError::AgentNotFound(agent_id.to_string()))
    }
    
    /// 测试智能体连接
    pub async fn test_agent(&mut self, agent_id: &str) -> CapResult<bool> {
        let agent = self.get_agent_info(agent_id).await?;
        
        let adapter = self.adapters
            .get(&agent.protocol)
            .ok_or_else(|| CapError::ProtocolError(format!("Unsupported protocol: {:?}", agent.protocol)))?;
            
        adapter.test_connection(&agent).await
    }
    
    /// 刷新智能体缓存
    pub async fn refresh_cache(&mut self) -> CapResult<()> {
        info!("Refreshing agent cache");
        self.agent_cache.clear();
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();
    
    info!("CLI-API Broker starting...");
    
    let hub_url = std::env::var("HUB_URL")
        .unwrap_or_else(|_| "http://localhost:8080".to_string());
    
    let broker = Broker::new(hub_url);
    
    info!("Broker initialized with {} adapters", broker.adapters.len());
    
    // TODO: 启动 HTTP 服务器
    info!("Broker is running at http://localhost:8081");
    
    // 保持服务运行
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
    }
}