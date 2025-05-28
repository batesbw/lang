from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class AuthenticationRequest(BaseModel):
    """
    Defines the input for requesting Salesforce authentication.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for Salesforce authentication",
            "examples": [
                {
                    "org_alias": "DevSandbox1",
                    "credential_type": "env_alias"
                }
            ]
        }
    )
    
    org_alias: str = Field(
        description="A friendly name for the Salesforce org, e.g., 'DevSandbox1'"
    )
    credential_type: Literal["env_alias"] = Field(
        default="env_alias",
        description="Type of credential to use for authentication"
    )

class SalesforceAuthRequest(BaseModel):
    """
    Defines the input for requesting Salesforce authentication (alternative naming).
    """
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Salesforce authentication request",
            "examples": [
                {
                    "org_alias": "DevSandbox1",
                    "credential_type": "env_alias"
                }
            ]
        }
    )
    
    org_alias: str = Field(
        description="A friendly name for the Salesforce org"
    )
    credential_type: Literal["env_alias"] = Field(
        default="env_alias",
        description="Type of credential to use for authentication"
    )

class SalesforceSessionDetails(BaseModel):
    """
    Holds the details of an active Salesforce session.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Details of an active Salesforce session"
        }
    )
    
    session_id: str = Field(description="Salesforce session ID")
    instance_url: str = Field(description="Salesforce instance URL")
    org_id: str = Field(description="Salesforce organization ID")
    user_id: str = Field(description="Salesforce user ID")
    org_alias: str = Field(description="Alias for the Salesforce org")

class AuthenticationResponse(BaseModel):
    """
    Defines the output after an authentication attempt.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response from authentication attempt"
        }
    )
    
    success: bool = Field(description="Whether authentication was successful")
    session_details: Optional[SalesforceSessionDetails] = Field(
        default=None,
        description="Session details if authentication was successful"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if authentication failed"
    )

class SalesforceAuthResponse(BaseModel):
    """
    Defines the output after a Salesforce authentication attempt (alternative naming).
    """
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response from Salesforce authentication attempt"
        }
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the authentication request"
    )
    success: bool = Field(description="Whether authentication was successful")
    session_id: Optional[str] = Field(
        default=None,
        description="Salesforce session ID if successful"
    )
    instance_url: Optional[str] = Field(
        default=None,
        description="Salesforce instance URL if successful"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Salesforce user ID if successful"
    )
    org_id: Optional[str] = Field(
        default=None,
        description="Salesforce organization ID if successful"
    )
    auth_type_used: Optional[str] = Field(
        default=None,
        description="Type of authentication used"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if authentication failed"
    ) 