from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class TestScenarioType(str, Enum):
    """Types of test scenarios"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    BOUNDARY = "boundary"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"

class ApexTestMethodType(str, Enum):
    """Types of Apex test methods"""
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    FLOW_TEST = "flow_test"
    BULK_TEST = "bulk_test"
    NEGATIVE_TEST = "negative_test"

class TestDataPattern(str, Enum):
    """Patterns for test data creation"""
    MINIMAL = "minimal"
    COMPREHENSIVE = "comprehensive"
    BULK = "bulk"
    RELATIONSHIP_HEAVY = "relationship_heavy"
    VALIDATION_TRIGGERING = "validation_triggering"

class TestScenario(BaseModel):
    """Represents a single test scenario"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Test scenario derived from acceptance criteria"
        }
    )
    
    scenario_id: str = Field(..., description="Unique identifier for the scenario")
    title: str = Field(..., description="Short descriptive title")
    description: str = Field(..., description="Detailed description of what's being tested")
    scenario_type: TestScenarioType = Field(..., description="Type of test scenario")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(default="Medium")
    
    # Test setup requirements
    required_objects: List[str] = Field(default_factory=list, description="Salesforce objects needed for this test")
    test_data_requirements: Dict[str, Any] = Field(default_factory=dict, description="Specific test data requirements")
    preconditions: List[str] = Field(default_factory=list, description="Conditions that must be met before test execution")
    
    # Test execution
    test_steps: List[str] = Field(default_factory=list, description="Step-by-step test execution")
    input_parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the flow")
    
    # Expected results
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected results")
    success_criteria: List[str] = Field(default_factory=list, description="Criteria for test success")
    
    # Flow-specific
    flow_elements_tested: List[str] = Field(default_factory=list, description="Flow elements this scenario tests")
    coverage_areas: List[str] = Field(default_factory=list, description="Areas of business logic covered")

class ApexTestMethod(BaseModel):
    """Represents an Apex test method"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Apex test method configuration"
        }
    )
    
    method_name: str = Field(..., description="Name of the test method")
    method_type: ApexTestMethodType = Field(..., description="Type of test method")
    test_scenario_id: str = Field(..., description="Associated test scenario ID")
    
    # Test method structure
    test_setup_code: List[str] = Field(default_factory=list, description="Setup code for the test")
    test_execution_code: List[str] = Field(default_factory=list, description="Main test execution code")
    assertion_code: List[str] = Field(default_factory=list, description="Assertion and verification code")
    
    # Metadata
    description: str = Field(..., description="Description of what the method tests")
    expected_coverage: List[str] = Field(default_factory=list, description="Code coverage expected")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other tests or data")

class ApexTestClass(BaseModel):
    """Represents a complete Apex test class"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Complete Apex test class for Flow testing"
        }
    )
    
    class_name: str = Field(..., description="Name of the Apex test class")
    description: str = Field(..., description="Description of what the class tests")
    flow_name: str = Field(..., description="Name of the Flow being tested")
    
    # Class structure
    class_annotations: List[str] = Field(default_factory=list, description="Class-level annotations")
    test_setup_method: Optional[str] = Field(None, description="@TestSetup method code")
    test_methods: List[ApexTestMethod] = Field(default_factory=list, description="Test methods in the class")
    utility_methods: List[str] = Field(default_factory=list, description="Helper/utility methods")
    
    # Test data
    test_data_patterns: List[TestDataPattern] = Field(default_factory=list, description="Test data creation patterns used")
    required_permissions: List[str] = Field(default_factory=list, description="Required permissions for tests")
    
    # Coverage and quality
    expected_coverage_percentage: Optional[int] = Field(None, description="Expected code coverage percentage")
    best_practices_applied: List[str] = Field(default_factory=list, description="Best practices incorporated")

class SalesforceObjectInfo(BaseModel):
    """Information about a Salesforce object for test design"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Salesforce object metadata for test design"
        }
    )
    
    object_name: str = Field(..., description="API name of the object")
    label: str = Field(..., description="Display label of the object")
    required_fields: List[str] = Field(default_factory=list, description="Required fields")
    optional_fields: List[str] = Field(default_factory=list, description="Optional fields commonly used")
    
    # Relationships
    parent_relationships: Dict[str, str] = Field(default_factory=dict, description="Parent relationship fields")
    child_relationships: List[str] = Field(default_factory=list, description="Child objects")
    
    # Constraints and validation
    validation_rules: List[str] = Field(default_factory=list, description="Active validation rules")
    unique_fields: List[str] = Field(default_factory=list, description="Fields with unique constraints")
    picklist_fields: Dict[str, List[str]] = Field(default_factory=dict, description="Picklist fields and values")
    
    # Test considerations
    test_data_considerations: List[str] = Field(default_factory=list, description="Special considerations for test data")

class TestDesignerRequest(BaseModel):
    """Request for the TestDesigner Agent"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for designing comprehensive Apex tests for a Flow"
        }
    )
    
    # Core inputs
    flow_name: str = Field(..., description="Name of the Flow to test")
    user_story: Dict[str, Any] = Field(..., description="User story that drove the Flow creation")
    acceptance_criteria: List[str] = Field(..., description="Acceptance criteria to test against")
    
    # Flow information
    flow_xml: Optional[str] = Field(None, description="Flow XML for analysis")
    flow_type: str = Field(..., description="Type of Flow (Screen, Record-Triggered, etc.)")
    target_objects: List[str] = Field(default_factory=list, description="Primary objects the Flow works with")
    
    # Org context
    org_alias: str = Field(..., description="Target Salesforce org alias")
    target_api_version: str = Field(default="59.0", description="Target API version")
    
    # Test requirements
    test_coverage_target: int = Field(default=85, description="Target code coverage percentage")
    include_bulk_tests: bool = Field(default=True, description="Include bulk operation tests")
    include_negative_tests: bool = Field(default=True, description="Include negative test scenarios")
    include_ui_tests: bool = Field(default=False, description="Include UI interaction tests")
    
    # Additional context
    business_context: Optional[str] = Field(None, description="Additional business context")
    existing_test_classes: List[str] = Field(default_factory=list, description="Existing test classes to consider")

class TestDesignerResponse(BaseModel):
    """Response from the TestDesigner Agent"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Response containing comprehensive test design"
        }
    )
    
    success: bool = Field(..., description="Whether test design was successful")
    request: TestDesignerRequest = Field(..., description="Original request for context")
    
    # Test design outputs
    test_scenarios: List[TestScenario] = Field(default_factory=list, description="Identified test scenarios")
    apex_test_classes: List[ApexTestClass] = Field(default_factory=list, description="Generated Apex test classes")
    
    # Supporting information
    salesforce_objects_analyzed: List[SalesforceObjectInfo] = Field(default_factory=list, description="Object metadata analyzed")
    test_data_strategy: Dict[str, Any] = Field(default_factory=dict, description="Strategy for test data creation")
    
    # Quality and coverage
    coverage_mapping: Dict[str, List[str]] = Field(default_factory=dict, description="Mapping of test scenarios to coverage areas")
    risk_analysis: List[str] = Field(default_factory=list, description="Identified testing risks and mitigations")
    implementation_recommendations: List[str] = Field(default_factory=list, description="Recommendations for test implementation")
    
    # Deployment ready output
    deployable_apex_code: List[str] = Field(default_factory=list, description="Complete Apex test class code ready for deployment")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if design failed")
    warnings: List[str] = Field(default_factory=list, description="Warnings about the test design")

class UserStoryAnalysisRequest(BaseModel):
    """Request for analyzing user stories to identify test scenarios"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for analyzing user stories for test scenario identification"
        }
    )
    
    user_story: Dict[str, Any] = Field(..., description="User story to analyze")
    acceptance_criteria: List[str] = Field(..., description="Acceptance criteria to convert to test scenarios")
    flow_type: str = Field(..., description="Type of Flow being tested")
    business_context: Optional[str] = Field(None, description="Additional business context")

class UserStoryAnalysisResponse(BaseModel):
    """Response from user story analysis"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Analysis results with identified test scenarios"
        }
    )
    
    success: bool = Field(..., description="Whether analysis was successful")
    test_scenarios: List[TestScenario] = Field(default_factory=list, description="Identified test scenarios")
    coverage_analysis: Dict[str, List[str]] = Field(default_factory=dict, description="Coverage analysis by scenario type")
    recommendations: List[str] = Field(default_factory=list, description="Testing recommendations")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")

class ApexCodeGenerationRequest(BaseModel):
    """Request for generating Apex test class code"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for generating Apex test class code"
        }
    )
    
    test_scenarios: List[TestScenario] = Field(..., description="Test scenarios to implement")
    flow_name: str = Field(..., description="Name of the Flow to test")
    flow_type: str = Field(..., description="Type of Flow")
    target_objects: List[str] = Field(default_factory=list, description="Objects involved in testing")
    salesforce_objects_info: List[SalesforceObjectInfo] = Field(default_factory=list, description="Object metadata")
    
    # Generation options
    class_name_prefix: str = Field(default="Test", description="Prefix for test class names")
    include_test_setup: bool = Field(default=True, description="Include @TestSetup method")
    target_coverage: int = Field(default=85, description="Target code coverage")
    api_version: str = Field(default="59.0", description="Salesforce API version")

class ApexCodeGenerationResponse(BaseModel):
    """Response from Apex code generation"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Generated Apex test class code"
        }
    )
    
    success: bool = Field(..., description="Whether code generation was successful")
    apex_test_classes: List[ApexTestClass] = Field(default_factory=list, description="Generated test class structures")
    deployable_code: List[str] = Field(default_factory=list, description="Complete Apex code ready for deployment")
    
    # Quality metrics
    estimated_coverage: int = Field(default=0, description="Estimated code coverage percentage")
    best_practices_applied: List[str] = Field(default_factory=list, description="Best practices incorporated")
    
    # Implementation details
    test_methods_count: int = Field(default=0, description="Total number of test methods generated")
    lines_of_code: int = Field(default=0, description="Total lines of code generated")
    
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    warnings: List[str] = Field(default_factory=list, description="Warnings about the generated code")

class SalesforceSchemaAnalysisRequest(BaseModel):
    """Request for analyzing Salesforce org schema"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Request for analyzing Salesforce org schema for test design"
        }
    )
    
    target_objects: List[str] = Field(..., description="Objects to analyze")
    org_alias: str = Field(..., description="Salesforce org alias")
    include_relationships: bool = Field(default=True, description="Include relationship analysis")
    include_validation_rules: bool = Field(default=True, description="Include validation rule analysis")

class SalesforceSchemaAnalysisResponse(BaseModel):
    """Response from Salesforce schema analysis"""
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Salesforce schema analysis results"
        }
    )
    
    success: bool = Field(..., description="Whether analysis was successful")
    objects_info: List[SalesforceObjectInfo] = Field(default_factory=list, description="Analyzed object information")
    schema_insights: Dict[str, Any] = Field(default_factory=dict, description="Schema insights for test design")
    test_data_recommendations: List[str] = Field(default_factory=list, description="Test data creation recommendations")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed") 