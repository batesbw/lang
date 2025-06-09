from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class FlowType(str, Enum):
    """Types of Salesforce Flows"""
    SCREEN_FLOW = "Screen Flow"
    RECORD_TRIGGERED = "Record-Triggered Flow"
    SCHEDULED = "Scheduled Flow"
    AUTOLAUNCHED = "Autolaunched Flow"
    PLATFORM_EVENT = "Platform Event-Triggered Flow"

class FlowElementType(str, Enum):
    """Types of Flow Elements"""
    SCREEN = "screens"
    DECISION = "decisions"
    ASSIGNMENT = "assignments"
    GET_RECORDS = "recordLookups"
    CREATE_RECORDS = "recordCreates"
    UPDATE_RECORDS = "recordUpdates"
    DELETE_RECORDS = "recordDeletes"
    LOOP = "loops"
    ACTION_CALL = "actionCalls"
    SUBFLOW = "subflows"
    WAIT = "waits"
    FAULT_CONNECTOR = "faultConnectors"

class FlowTriggerType(str, Enum):
    """Flow trigger types for record-triggered flows"""
    RECORD_BEFORE_SAVE = "RecordBeforeSave"
    RECORD_AFTER_SAVE = "RecordAfterSave"
    RECORD_BEFORE_DELETE = "RecordBeforeDelete"
    RECORD_AFTER_DELETE = "RecordAfterDelete"

class UserStory(BaseModel):
    """Represents a user story for flow development"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "User story for flow development",
            "examples": [
                {
                    "title": "Automate Lead Assignment",
                    "description": "As a sales manager, I want leads to be automatically assigned to the right sales rep so that response time is improved",
                    "acceptance_criteria": ["Leads are assigned within 5 minutes", "Assignment follows territory rules"],
                    "field_names": ["Lead.Status", "Lead.OwnerId", "Lead.Territory__c", "User.Territory__c"],
                    "priority": "High"
                }
            ]
        }
    )
    
    title: str = Field(..., description="Title of the user story")
    description: str = Field(..., description="As a [user], I want [goal] so that [benefit]")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria that define when the story is complete")
    field_names: List[str] = Field(default_factory=list, description="List of specific Salesforce field names (Object.Field format) that should be used in the flow")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(default="Medium", description="Priority level of the user story")
    business_context: Optional[str] = Field(None, description="Additional business context or background")
    affected_objects: List[str] = Field(default_factory=list, description="Salesforce objects that will be affected")
    user_personas: List[str] = Field(default_factory=list, description="Types of users who will interact with this flow")

class FlowRequirement(BaseModel):
    """Detailed flow requirements derived from user stories"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Detailed flow requirements derived from user stories"
        }
    )
    
    flow_type: FlowType = Field(..., description="Type of flow to create")
    trigger_object: Optional[str] = Field(None, description="Object that triggers the flow (for record-triggered flows)")
    trigger_type: Optional[FlowTriggerType] = Field(None, description="When the flow should trigger")
    entry_criteria: Optional[str] = Field(None, description="Conditions that must be met for the flow to run")
    flow_elements_needed: List[FlowElementType] = Field(..., description="Types of flow elements required")
    data_operations: List[str] = Field(default_factory=list, description="Data operations needed (create, read, update, delete)")
    business_logic: List[str] = Field(default_factory=list, description="Business rules and logic to implement")
    error_handling: List[str] = Field(default_factory=list, description="Error scenarios to handle")
    integration_points: List[str] = Field(default_factory=list, description="External systems or APIs to integrate with")

class FlowElement(BaseModel):
    """Represents a flow element with its configuration"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Flow element with its configuration"
        }
    )
    
    element_type: FlowElementType = Field(..., description="Type of flow element")
    name: str = Field(..., description="API name of the element")
    label: str = Field(..., description="Display label for the element")
    description: Optional[str] = Field(None, description="Description of what this element does")
    location_x: int = Field(default=176, description="X coordinate for element positioning")
    location_y: int = Field(default=134, description="Y coordinate for element positioning")
    connector_target: Optional[str] = Field(None, description="Next element to connect to")
    fault_connector_target: Optional[str] = Field(None, description="Element to connect to on error")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Element-specific configuration")

class FlowVariable(BaseModel):
    """Represents a flow variable"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Flow variable definition"
        }
    )
    
    name: str = Field(..., description="API name of the variable")
    data_type: str = Field(..., description="Data type (Text, Number, Boolean, Date, etc.)")
    is_collection: bool = Field(default=False, description="Whether this is a collection variable")
    is_input: bool = Field(default=False, description="Whether this is an input variable")
    is_output: bool = Field(default=False, description="Whether this is an output variable")
    default_value: Optional[str] = Field(None, description="Default value for the variable")
    description: Optional[str] = Field(None, description="Description of the variable's purpose")

class FlowBuildRequest(BaseModel):
    """Enhanced request for building a Salesforce Flow"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for building a Salesforce Flow",
            "examples": [
                {
                    "flow_api_name": "ProcessLeadConversion",
                    "flow_label": "Process Lead Conversion",
                    "flow_description": "Automates lead conversion process",
                    "flow_type": "Screen Flow"
                }
            ]
        }
    )
    
    # Basic flow information
    flow_api_name: str = Field(..., description="API name for the Flow", examples=["ProcessLeadConversion"])
    flow_label: str = Field(..., description="Label for the Flow", examples=["Process Lead Conversion"])
    flow_description: Optional[str] = Field(None, description="Description of the Flow's purpose")
    target_api_version: str = Field(default="59.0", description="Salesforce API version")
    
    # User story and requirements
    user_story: Optional[UserStory] = Field(None, description="User story that drives this flow")
    requirements: Optional[FlowRequirement] = Field(None, description="Detailed flow requirements")
    
    # Test-Driven Development context
    tdd_context: Optional[Dict[str, Any]] = Field(None, description="Test-Driven Development context including test scenarios and deployed test classes")
    
    # Flow configuration
    flow_type: FlowType = Field(default=FlowType.SCREEN_FLOW, description="Type of flow to create")
    trigger_object: Optional[str] = Field(None, description="Object that triggers the flow")
    trigger_type: Optional[FlowTriggerType] = Field(None, description="When the flow should trigger")
    entry_criteria: Optional[str] = Field(None, description="Entry criteria for the flow")
    
    # Flow elements and structure
    flow_elements: List[FlowElement] = Field(default_factory=list, description="Flow elements to include")
    flow_variables: List[FlowVariable] = Field(default_factory=list, description="Flow variables to create")
    
    # Advanced options
    run_in_system_mode: bool = Field(default=False, description="Whether to run in system mode")
    enable_bulk_processing: bool = Field(default=True, description="Enable bulk processing for record-triggered flows")
    
    # Retry and failure learning context
    retry_context: Optional[Dict[str, Any]] = Field(None, description="Context about retry attempts and previous failures")
    
    # Legacy support for simple flows
    screen_api_name: Optional[str] = Field(None, description="API name for simple screen element")
    screen_label: Optional[str] = Field(None, description="Label for simple screen element")
    display_text_api_name: Optional[str] = Field(None, description="API name for simple display text")
    display_text_content: Optional[str] = Field(None, description="Content for simple display text")

class FlowValidationError(BaseModel):
    """Represents a flow validation error"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Flow validation error details"
        }
    )
    
    error_type: str = Field(..., description="Type of validation error")
    element_name: Optional[str] = Field(None, description="Flow element that caused the error")
    error_message: str = Field(..., description="Detailed error message")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for the error")
    severity: Literal["Error", "Warning", "Info"] = Field(default="Error", description="Severity level")

class FlowBuildResponse(BaseModel):
    """Enhanced response after a Flow build attempt"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response after a Flow build attempt"
        }
    )
    
    success: bool = Field(..., description="Whether the flow was built successfully")
    input_request: FlowBuildRequest = Field(..., description="Echo back the request for context")
    flow_xml: Optional[str] = Field(None, description="Generated Flow XML if successful")
    flow_definition_xml: Optional[str] = Field(None, description="Flow Definition XML for activation control")
    
    # Validation and errors
    validation_errors: List[FlowValidationError] = Field(default_factory=list, description="Validation errors found")
    error_message: Optional[str] = Field(None, description="Primary error message if build failed")
    
    # Metadata and insights
    elements_created: List[str] = Field(default_factory=list, description="List of flow elements created")
    variables_created: List[str] = Field(default_factory=list, description="List of variables created")
    best_practices_applied: List[str] = Field(default_factory=list, description="Best practices automatically applied")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    
    # Deployment information
    deployment_notes: Optional[str] = Field(None, description="Notes about deployment considerations")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies that need to be deployed first")

class FlowRepairRequest(BaseModel):
    """Request to repair a flow based on deployment or test errors"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request to repair a flow based on errors"
        }
    )
    
    flow_xml: str = Field(..., description="Current flow XML that needs repair")
    error_messages: List[str] = Field(..., description="Error messages from deployment or testing")
    error_context: Optional[str] = Field(None, description="Additional context about where errors occurred")
    target_org_info: Optional[Dict[str, Any]] = Field(None, description="Information about target org (API version, features, etc.)")

class FlowRepairResponse(BaseModel):
    """Response after attempting to repair a flow"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response after attempting to repair a flow"
        }
    )
    
    success: bool = Field(..., description="Whether the repair was successful")
    repaired_flow_xml: Optional[str] = Field(None, description="Repaired flow XML")
    repairs_made: List[str] = Field(default_factory=list, description="List of repairs that were made")
    remaining_issues: List[str] = Field(default_factory=list, description="Issues that could not be automatically fixed")
    repair_explanation: Optional[str] = Field(None, description="Explanation of the repair process") 