from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class FlowScannerRule(BaseModel):
    """Represents a rule violation found by Lightning Flow Scanner"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Flow Scanner rule violation details"
        }
    )
    
    rule_name: str = Field(..., description="Name of the violated rule")
    severity: Literal["error", "warning", "note"] = Field(..., description="Severity level of the violation")
    message: str = Field(..., description="Description of the rule violation")
    location: Optional[str] = Field(None, description="Location in the flow where the violation occurred")
    element_name: Optional[str] = Field(None, description="Name of the flow element with the violation")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the violation")
    category: Optional[str] = Field(None, description="Category of the rule violation")
    fix_suggestion: Optional[str] = Field(None, description="Suggested fix for the violation")

class FlowValidationRequest(BaseModel):
    """Request for validating a Salesforce Flow using Lightning Flow Scanner"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for Flow validation using Lightning Flow Scanner",
            "examples": [
                {
                    "flow_api_name": "ProcessLeadConversion",
                    "flow_xml": "<Flow xmlns=\"http://soap.sforce.com/2006/04/metadata\">...</Flow>",
                    "validation_level": "strict"
                }
            ]
        }
    )
    
    request_id: str = Field(..., description="Unique identifier for this validation request")
    flow_api_name: str = Field(..., description="API name of the flow being validated")
    flow_xml: str = Field(..., description="Complete Flow XML to validate")
    validation_level: Literal["strict", "standard", "minimal"] = Field(
        default="standard", 
        description="Level of validation strictness"
    )
    ignore_rules: List[str] = Field(
        default_factory=list, 
        description="List of rule names to ignore during validation"
    )
    custom_rules_config: Optional[Dict[str, Any]] = Field(
        None, 
        description="Custom configuration for Flow Scanner rules"
    )

class FlowValidationResponse(BaseModel):
    """Response after Flow validation using Lightning Flow Scanner"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response after Flow validation using Lightning Flow Scanner"
        }
    )
    
    request_id: str = Field(..., description="Request ID that this response corresponds to")
    success: bool = Field(..., description="Whether the validation was completed successfully")
    flow_api_name: str = Field(..., description="API name of the flow that was validated")
    
    # Validation results
    is_valid: bool = Field(..., description="Whether the flow passed validation (no errors)")
    has_warnings: bool = Field(default=False, description="Whether the flow has warnings")
    
    # Rule violations
    errors: List[FlowScannerRule] = Field(default_factory=list, description="Critical errors that prevent activation")
    warnings: List[FlowScannerRule] = Field(default_factory=list, description="Warnings that should be addressed")
    notes: List[FlowScannerRule] = Field(default_factory=list, description="Informational notes")
    
    # Summary metrics
    total_violations: int = Field(default=0, description="Total number of violations found")
    error_count: int = Field(default=0, description="Number of error-level violations")
    warning_count: int = Field(default=0, description="Number of warning-level violations")
    
    # Tool execution details
    scanner_version: Optional[str] = Field(None, description="Version of Lightning Flow Scanner used")
    execution_time_seconds: Optional[float] = Field(None, description="Time taken to run validation in seconds")
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    
    # Context for retries
    validation_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context for retry attempts"
    )

class FlowValidationSummary(BaseModel):
    """Summary of validation results for decision making"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Summary of validation results for workflow decisions"
        }
    )
    
    flow_api_name: str = Field(..., description="API name of the validated flow")
    can_deploy: bool = Field(..., description="Whether the flow can be deployed (no blocking errors)")
    should_retry: bool = Field(..., description="Whether the flow should be rebuilt to fix errors")
    blocking_issues: List[str] = Field(default_factory=list, description="List of blocking issues")
    recommended_fixes: List[str] = Field(default_factory=list, description="List of recommended fixes")
    retry_guidance: Optional[str] = Field(None, description="Specific guidance for retry attempts") 