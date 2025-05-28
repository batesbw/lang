from typing import Dict, Optional, TypedDict
from src.schemas.auth_schemas import SalesforceSessionDetails
from src.schemas.flow_builder_schemas import FlowBuildRequest

# Using TypedDict for the overall graph state as per LangGraph common practices.
# Specific agent-related states can be nested Pydantic models if complex, 
# or directly included as shown here for authentication.

class AgentWorkforceState(TypedDict):
    """
    Represents the overall state of the multi-agent workforce graph.
    This will be expanded as more agents and capabilities are added.
    """
    
    # AuthenticationAgent related state
    active_salesforce_sessions: Optional[Dict[str, SalesforceSessionDetails]]
    """Stores active Salesforce sessions, keyed by org_alias."""
    
    authentication_error: Optional[str]
    """Stores the last error message from an authentication attempt."""
    
    last_authenticated_org_alias: Optional[str]
    """Stores the alias of the most recently successfully authenticated org."""
    
    current_org_alias_request: Optional[str]
    """The org_alias that the AuthenticationAgent should attempt to connect to in the current step."""
    
    # FlowBuilderAgent related state
    current_flow_build_request: Optional[FlowBuildRequest]
    """The request details for the Flow to be built."""
    
    generated_flow_xml: Optional[str]
    """Stores the XML string of the successfully generated Flow."""
    
    flow_build_error: Optional[str]
    """Stores any error message from the Flow building process."""
    
    # Placeholder for other agent states to be added later
    # e.g., deployment_state: Optional[dict] = None 