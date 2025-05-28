from typing import Optional, Literal
from pydantic import BaseModel

class AuthenticationRequest(BaseModel):
    """
    Defines the input for requesting Salesforce authentication.
    """
    org_alias: str  # A friendly name for the Salesforce org, e.g., "DevSandbox1"
    # For initial implementation (Task 1.1.2), this implies fetching credentials
    # associated with this alias from a secure source (e.g., env vars or vault).
    # Later, this could be expanded for different OAuth flows.
    credential_type: Literal["env_alias"] = "env_alias"

class SalesforceAuthRequest(BaseModel):
    """
    Defines the input for requesting Salesforce authentication (alternative naming).
    """
    org_alias: str
    credential_type: Literal["env_alias"] = "env_alias"

class SalesforceSessionDetails(BaseModel):
    """
    Holds the details of an active Salesforce session.
    """
    session_id: str
    instance_url: str
    org_id: str
    user_id: str
    org_alias: str # To track which org this session belongs to

class AuthenticationResponse(BaseModel):
    """
    Defines the output after an authentication attempt.
    """
    success: bool
    session_details: Optional[SalesforceSessionDetails] = None
    error_message: Optional[str] = None

class SalesforceAuthResponse(BaseModel):
    """
    Defines the output after a Salesforce authentication attempt (alternative naming).
    """
    request_id: Optional[str] = None
    success: bool
    session_id: Optional[str] = None
    instance_url: Optional[str] = None
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    auth_type_used: Optional[str] = None
    error_message: Optional[str] = None 