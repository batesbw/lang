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

    # Deployment related state
    current_deployment_request: Optional[Dict[str, Any]]  # Serialized DeploymentRequest
    current_deployment_response: Optional[Dict[str, Any]]  # Serialized DeploymentResponse
    
    # General state
    messages: Optional[List[Any]]  # For storing LangGraph message history
    error_message: Optional[str]  # General error messages not specific to an agent's response
    retry_count: int  # For managing retries in loops 