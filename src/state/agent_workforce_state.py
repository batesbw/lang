from typing import TypedDict, Optional, List, Any, Dict
from src.schemas.auth_schemas import SalesforceAuthRequest, SalesforceAuthResponse
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse

class AgentWorkforceState(TypedDict, total=False):
    """State for the Agent Workforce LangGraph workflow"""
    
    # Authentication related state
    current_auth_request: Optional[Dict[str, Any]]  # Serialized SalesforceAuthRequest
    current_auth_response: Optional[Dict[str, Any]]  # Serialized SalesforceAuthResponse
    is_authenticated: bool
    salesforce_session: Optional[Dict[str, Any]]  # Serialized SalesforceAuthResponse for active session

    # Flow Building related state
    current_flow_build_request: Optional[Dict[str, Any]]  # Serialized FlowBuildRequest
    current_flow_build_response: Optional[Dict[str, Any]]  # Serialized FlowBuildResponse
    flow_builder_memory_data: Optional[Dict[str, Any]]  # Persistent memory data for enhanced flow builder

    # User requirements
    user_story: Optional[Dict[str, Any]]  # Serialized UserStory with acceptance criteria

    # Deployment related state
    current_deployment_request: Optional[Dict[str, Any]]  # Serialized DeploymentRequest
    current_deployment_response: Optional[Dict[str, Any]]  # Serialized DeploymentResponse
    
    # TestDesigner related state
    current_test_designer_request: Optional[Dict[str, Any]]  # Serialized TestDesignerRequest
    current_test_designer_response: Optional[Dict[str, Any]]  # Serialized TestDesignerResponse
    test_scenarios: Optional[List[Dict[str, Any]]]  # Serialized TestScenario objects
    apex_test_classes: Optional[List[Dict[str, Any]]]  # Serialized ApexTestClass objects
    deployable_apex_code: Optional[List[str]]  # Generated Apex test class code ready for deployment
    
    # Test Class Deployment related state
    current_test_deployment_request: Optional[Dict[str, Any]]  # Serialized DeploymentRequest for test classes
    current_test_deployment_response: Optional[Dict[str, Any]]  # Serialized DeploymentResponse for test classes
    
    # Web Search related state
    current_web_search_request: Optional[Dict[str, Any]]  # Serialized WebSearchAgentRequest
    current_web_search_response: Optional[Dict[str, Any]]  # Serialized WebSearchAgentResponse
    
    # Simple Retry Management
    build_deploy_retry_count: int  # Current retry attempt for build/deploy cycle
    max_build_deploy_retries: int  # Maximum allowed retries from environment
    test_deploy_retry_count: int  # Current retry attempt for test deployment cycle
    
    # General state
    messages: Optional[List[Any]]  # For storing LangGraph message history
    error_message: Optional[str]
    retry_count: int  # General retry counter (legacy) 