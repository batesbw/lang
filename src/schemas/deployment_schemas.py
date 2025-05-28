from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from src.schemas.auth_schemas import SalesforceAuthResponse

class DeploymentRequest(BaseModel):
    request_id: str
    flow_xml: str
    flow_name: str # API name of the Flow, e.g., "MyTestFlow"
    salesforce_session: SalesforceAuthResponse # Contains session_id and instance_url

class DeploymentResponse(BaseModel):
    request_id: str
    success: bool
    status: str # e.g., "Succeeded", "Failed", "InProgress", "Canceled", "Pending"
    deployment_id: Optional[str] = None
    error_message: Optional[str] = None # General error message for the deployment operation itself
    # Salesforce provides detailed success/failure info per component
    component_successes: Optional[List[Dict[str, Any]]] = None 
    component_errors: Optional[List[Dict[str, Any]]] = None 