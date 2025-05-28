from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from src.schemas.auth_schemas import SalesforceAuthResponse

class DeploymentRequest(BaseModel):
    """Request to deploy a flow to Salesforce"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request to deploy a flow to Salesforce",
            "examples": [
                {
                    "request_id": "deploy-123",
                    "flow_xml": "<Flow xmlns='http://soap.sforce.com/2006/04/metadata'>...</Flow>",
                    "flow_name": "MyTestFlow"
                }
            ]
        }
    )
    
    request_id: str = Field(..., description="Unique identifier for the deployment request")
    flow_xml: str = Field(..., description="Flow XML metadata to deploy")
    flow_name: str = Field(..., description="API name of the Flow, e.g., 'MyTestFlow'")
    salesforce_session: SalesforceAuthResponse = Field(..., description="Contains session_id and instance_url")

class DeploymentResponse(BaseModel):
    """Response from a flow deployment attempt"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response from a flow deployment attempt"
        }
    )
    
    request_id: str = Field(..., description="Unique identifier for the deployment request")
    success: bool = Field(..., description="Whether the deployment was successful")
    status: str = Field(..., description="Deployment status: 'Succeeded', 'Failed', 'InProgress', 'Canceled', 'Pending'")
    deployment_id: Optional[str] = Field(None, description="Salesforce deployment ID if available")
    error_message: Optional[str] = Field(None, description="General error message for the deployment operation")
    # Salesforce provides detailed success/failure info per component
    component_successes: Optional[List[Dict[str, Any]]] = Field(None, description="List of successfully deployed components")
    component_errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of component deployment errors") 