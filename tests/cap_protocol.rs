#[cfg(test)]
mod tests {
    use super::*;
    use uuid::Uuid;
    use std::collections::HashMap;

    #[test]
    fn test_agent_request_serialization() {
        let request = AgentRequest {
            id: Uuid::new_v4(),
            agent_id: "test-agent".to_string(),
            command: "test-command".to_string(),
            args: vec!["arg1".to_string(), "arg2".to_string()],
            input: Some("test input".to_string()),
            context: None,
            metadata: HashMap::new(),
        };

        let json = serde_json::to_string(&request).unwrap();
        let deserialized: AgentRequest = serde_json::from_str(&json).unwrap();
        
        assert_eq!(request.id, deserialized.id);
        assert_eq!(request.agent_id, deserialized.agent_id);
        assert_eq!(request.command, deserialized.command);
        assert_eq!(request.args, deserialized.args);
    }

    #[test]
    fn test_agent_response_serialization() {
        let response = AgentResponse {
            id: Uuid::new_v4(),
            success: true,
            output: Some("test output".to_string()),
            error: None,
            metadata: HashMap::new(),
            execution_time_ms: 1000,
        };

        let json = serde_json::to_string(&response).unwrap();
        let deserialized: AgentResponse = serde_json::from_str(&json).unwrap();
        
        assert_eq!(response.id, deserialized.id);
        assert_eq!(response.success, deserialized.success);
        assert_eq!(response.output, deserialized.output);
        assert_eq!(response.execution_time_ms, deserialized.execution_time_ms);
    }

    #[test]  
    fn test_agent_info_creation() {
        let agent = AgentInfo {
            id: "gpt4".to_string(),
            name: "GPT-4".to_string(),
            description: "OpenAI GPT-4".to_string(),
            version: "1.0.0".to_string(),
            provider: "openai".to_string(),
            commands: vec![
                AgentCommand {
                    name: "chat".to_string(),
                    description: "Chat".to_string(),
                    args: vec![],
                    examples: vec![],
                }
            ],
            capabilities: vec!["chat".to_string()],
            endpoint: "https://api.openai.com/v1".to_string(),
            protocol: ProtocolType::OpenAI,
            auth: None,
        };

        assert_eq!(agent.id, "gpt4");
        assert_eq!(agent.commands.len(), 1);
    }

    #[test]
    fn test_cap_error_display() {
        let error = CapError::AgentNotFound("test-agent".to_string());
        assert_eq!(error.to_string(), "Agent not found: test-agent");
        
        let error = CapError::CommandNotFound("test-cmd".to_string());
        assert_eq!(error.to_string(), "Command not found: test-cmd");
    }
}