from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from src.schemas.auth_schemas import SalesforceAuthResponse

class MetadataComponent(BaseModel):
    """Represents a single metadata component to deploy"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single metadata component to deploy",
            "examples": [
                {
                    "component_type": "Flow",
                    "api_name": "MyTestFlow",
                    "metadata_xml": "<Flow xmlns='http://soap.sforce.com/2006/04/metadata'>...</Flow>",
                    "directory": "flows",
                    "file_extension": "flow-meta.xml"
                },
                {
                    "component_type": "CustomObject",
                    "api_name": "MyCustomObject__c",
                    "metadata_xml": "<CustomObject xmlns='http://soap.sforce.com/2006/04/metadata'>...</CustomObject>",
                    "directory": "objects",
                    "file_extension": "object"
                }
            ]
        }
    )
    
    component_type: str = Field(..., description="Salesforce metadata type (e.g., 'Flow', 'CustomObject', 'ApexClass')")
    api_name: str = Field(..., description="API name of the component")
    metadata_xml: str = Field(..., description="XML metadata content for the component")
    directory: Optional[str] = Field(None, description="Directory for the component in deployment package (e.g., 'flows', 'objects')")
    file_extension: Optional[str] = Field(None, description="File extension for the component (e.g., 'flow-meta.xml', 'object')")

class DeploymentRequest(BaseModel):
    """Request to deploy multiple metadata components to Salesforce"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request to deploy multiple metadata components to Salesforce",
            "examples": [
                {
                    "request_id": "deploy-123",
                    "components": [
                        {
                            "component_type": "Flow",
                            "api_name": "MyTestFlow",
                            "metadata_xml": "<Flow xmlns='http://soap.sforce.com/2006/04/metadata'>...</Flow>"
                        }
                    ]
                }
            ]
        }
    )
    
    request_id: str = Field(..., description="Unique identifier for the deployment request")
    components: List[MetadataComponent] = Field(..., description="List of metadata components to deploy")
    salesforce_session: SalesforceAuthResponse = Field(..., description="Contains session_id and instance_url")
    api_version: str = Field(default="59.0", description="Salesforce API version to use")

    # Backward compatibility properties for single flow deployment
    @property
    def flow_xml(self) -> Optional[str]:
        """Backward compatibility: return first Flow's XML if available"""
        for component in self.components:
            if component.component_type == "Flow":
                return component.metadata_xml
        return None
    
    @property
    def flow_name(self) -> Optional[str]:
        """Backward compatibility: return first Flow's API name if available"""
        for component in self.components:
            if component.component_type == "Flow":
                return component.api_name
        return None

class DeploymentResponse(BaseModel):
    """Response from a metadata deployment attempt"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response from a metadata deployment attempt"
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
    
    # Summary information
    total_components: Optional[int] = Field(None, description="Total number of components in deployment")
    successful_components: Optional[int] = Field(None, description="Number of successfully deployed components")
    failed_components: Optional[int] = Field(None, description="Number of failed components") 