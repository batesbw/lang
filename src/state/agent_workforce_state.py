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

    # Flow Validation related state
    current_flow_validation_response: Optional[Dict[str, Any]]  # Serialized FlowValidationResponse
    validation_requires_retry: Optional[bool]  # Whether validation failed and requires retry

    # User requirements
    user_story: Optional[Dict[str, Any]]  # Serialized UserStory with acceptance criteria

    # Deployment related state
    current_deployment_request: Optional[Dict[str, Any]]  # Serialized DeploymentRequest
    current_deployment_response: Optional[Dict[str, Any]]  # Serialized DeploymentResponse
    
    # Simple Retry Management
    build_deploy_retry_count: int  # Current retry attempt for build/deploy cycle
    max_build_deploy_retries: int  # Maximum allowed retries from environment
    
    # General state
    messages: Optional[List[Any]]  # For storing LangGraph message history
    error_message: Optional[str]
    retry_count: int  # General retry counter (legacy) 