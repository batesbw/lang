from typing import Type, List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import uuid
import re

from src.schemas.test_designer_schemas import (
    UserStoryAnalysisRequest, UserStoryAnalysisResponse,
    ApexCodeGenerationRequest, ApexCodeGenerationResponse,
    SalesforceSchemaAnalysisRequest, SalesforceSchemaAnalysisResponse,
    TestScenario, TestScenarioType, ApexTestClass, ApexTestMethod,
    ApexTestMethodType, TestDataPattern, SalesforceObjectInfo
)

class UserStoryAnalyzerTool(BaseTool):
    """
    Tool that analyzes user stories and acceptance criteria to identify 
    comprehensive test scenarios for Salesforce Flows.
    """
    name: str = "user_story_analyzer_tool"
    description: str = (
        "Analyze user stories and acceptance criteria to identify comprehensive test scenarios "
        "for Salesforce Flow testing. Generates positive, negative, edge case, and boundary "
        "test scenarios with detailed test steps and expected outcomes."
    )
    args_schema: Type[BaseModel] = UserStoryAnalysisRequest
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__()
        self._llm = llm  # Store as private attribute
    
    def _create_parser_and_prompt(self):
        """Create parser and prompt template when needed"""
        parser = PydanticOutputParser(pydantic_object=UserStoryAnalysisResponse)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Salesforce Test Architect specializing in comprehensive test scenario design. 
Your task is to analyze user stories and acceptance criteria to create detailed test scenarios that ensure thorough testing of Salesforce Flows.

Key responsibilities:
1. Identify all possible test scenarios including positive, negative, edge cases, and boundary conditions
2. Create detailed test steps with specific input parameters and expected outcomes
3. Map test scenarios to acceptance criteria for complete coverage
4. Consider Flow-specific testing requirements (triggers, variables, error paths)
5. Apply Salesforce testing best practices

Test Scenario Types to consider:
- POSITIVE: Happy path scenarios that should succeed
- NEGATIVE: Error scenarios that should fail gracefully
- EDGE_CASE: Unusual but valid scenarios
- BOUNDARY: Testing limits and boundaries
- ERROR_HANDLING: Testing error conditions and fault paths
- INTEGRATION: Testing interactions with other systems/objects

For Flow testing, consider:
- Input variable validation
- Flow element testing (screens, decisions, assignments, record operations)
- Error path testing
- Bulk data scenarios
- Permission and security testing
- Performance under load

Test Scenario Structure:
- Clear, descriptive titles
- Detailed test steps
- Specific input parameters
- Expected outcomes and success criteria
- Prerequisites and test data requirements
- Coverage areas and Flow elements tested

{format_instructions}"""),
            ("human", """Analyze this user story and acceptance criteria for comprehensive test scenario identification:

User Story: {user_story}

Acceptance Criteria:
{acceptance_criteria}

Flow Type: {flow_type}

Business Context: {business_context}

Please provide a comprehensive analysis that includes:
1. Identification of all test scenarios (positive, negative, edge cases, boundaries)
2. Detailed test steps for each scenario
3. Specific input parameters and expected outcomes
4. Test data requirements and prerequisites
5. Coverage analysis mapping scenarios to acceptance criteria
6. Recommendations for additional testing considerations""")
        ])
        
        return parser, prompt_template
    
    def _run(
        self,
        user_story: Dict[str, Any],
        acceptance_criteria: List[str],
        flow_type: str,
        business_context: Optional[str] = None
    ) -> str:
        """Analyze user story to identify test scenarios"""
        try:
            parser, prompt_template = self._create_parser_and_prompt()
            
            # Format acceptance criteria
            ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])
            
            # Format user story
            user_story_text = json.dumps(user_story, indent=2)
            
            # Create the prompt
            messages = prompt_template.format_messages(
                user_story=user_story_text,
                acceptance_criteria=ac_text,
                flow_type=flow_type,
                business_context=business_context or "Not provided",
                format_instructions=parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self._llm.invoke(messages)
            
            # Parse the response
            analysis_response = parser.parse(response.content)
            
            # Format the output
            return self._format_analysis_response(analysis_response)
            
        except Exception as e:
            return f"Error analyzing user story: {str(e)}"
    
    def _format_analysis_response(self, response: UserStoryAnalysisResponse) -> str:
        """Format the analysis response into a readable string"""
        output = []
        
        if not response.success:
            output.append(f"❌ Analysis failed: {response.error_message}")
            return "\n".join(output)
        
        output.append("=== USER STORY ANALYSIS RESULTS ===")
        output.append(f"✅ Successfully identified {len(response.test_scenarios)} test scenarios\n")
        
        # Test scenarios by type
        scenarios_by_type = {}
        for scenario in response.test_scenarios:
            scenario_type = scenario.scenario_type.value
            if scenario_type not in scenarios_by_type:
                scenarios_by_type[scenario_type] = []
            scenarios_by_type[scenario_type].append(scenario)
        
        for scenario_type, scenarios in scenarios_by_type.items():
            output.append(f"=== {scenario_type.upper()} SCENARIOS ({len(scenarios)}) ===")
            for scenario in scenarios:
                output.append(f"\n📋 {scenario.title} ({scenario.priority} Priority)")
                output.append(f"   ID: {scenario.scenario_id}")
                output.append(f"   Description: {scenario.description}")
                
                if scenario.test_steps:
                    output.append("   Test Steps:")
                    for i, step in enumerate(scenario.test_steps, 1):
                        output.append(f"     {i}. {step}")
                
                if scenario.expected_outcomes:
                    output.append("   Expected Outcomes:")
                    for outcome in scenario.expected_outcomes:
                        output.append(f"     ✓ {outcome}")
                
                if scenario.input_parameters:
                    output.append(f"   Input Parameters: {scenario.input_parameters}")
                
                if scenario.flow_elements_tested:
                    output.append(f"   Flow Elements Tested: {', '.join(scenario.flow_elements_tested)}")
            
            output.append("")
        
        # Coverage analysis
        if response.coverage_analysis:
            output.append("=== COVERAGE ANALYSIS ===")
            for area, scenarios in response.coverage_analysis.items():
                output.append(f"{area}: {len(scenarios)} scenarios")
                for scenario in scenarios:
                    output.append(f"  - {scenario}")
            output.append("")
        
        # Recommendations
        if response.recommendations:
            output.append("=== TESTING RECOMMENDATIONS ===")
            for rec in response.recommendations:
                output.append(f"💡 {rec}")
        
        return "\n".join(output)

    def get_structured_response(
        self,
        user_story: Dict[str, Any],
        acceptance_criteria: List[str],
        flow_type: str,
        business_context: Optional[str] = None
    ) -> UserStoryAnalysisResponse:
        """Get structured response instead of formatted string"""
        try:
            parser, prompt_template = self._create_parser_and_prompt()
            
            # Format acceptance criteria
            ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])
            
            # Format user story
            user_story_text = json.dumps(user_story, indent=2)
            
            # Create the prompt
            messages = prompt_template.format_messages(
                user_story=user_story_text,
                acceptance_criteria=ac_text,
                flow_type=flow_type,
                business_context=business_context or "Not provided",
                format_instructions=parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self._llm.invoke(messages)
            
            # Parse and return the response
            return parser.parse(response.content)
            
        except Exception as e:
            return UserStoryAnalysisResponse(
                success=False,
                error_message=f"Error analyzing user story: {str(e)}"
            )

class ApexTestClassGeneratorTool(BaseTool):
    """
    Tool that generates comprehensive Apex test classes for Salesforce Flow testing
    based on identified test scenarios and object metadata.
    """
    name: str = "apex_test_class_generator_tool"
    description: str = (
        "Generate comprehensive Apex test classes for Salesforce Flow testing. "
        "Creates test methods for each scenario with proper setup, execution, "
        "and assertion logic following Salesforce testing best practices."
    )
    args_schema: Type[BaseModel] = ApexCodeGenerationRequest
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__()
        self._llm = llm  # Store as private attribute
    
    def _create_parser_and_prompt(self):
        """Create parser and prompt template when needed"""
        parser = PydanticOutputParser(pydantic_object=ApexCodeGenerationResponse)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Salesforce Apex developer specializing in comprehensive test class creation for Flow testing.

Your task is to generate production-ready Apex test classes that thoroughly test Salesforce Flows based on provided test scenarios.

Key requirements:
1. Generate complete, compilable Apex test classes
2. Include proper annotations (@isTest, @TestSetup)
3. Create comprehensive test data setup methods
4. Implement test methods for each scenario with proper assertions
5. Follow Salesforce testing best practices
6. Include error handling and negative test cases
7. Ensure proper test isolation and cleanup

Apex Testing Best Practices to follow:
- Use @TestSetup for data creation when possible
- Use Test.startTest() and Test.stopTest() for governor limit resets
- Create meaningful test data that respects validation rules
- Use System.assert*, Test.getFlowVars() for Flow testing
- Test bulk scenarios (200+ records when applicable)
- Include negative test cases with expected exceptions
- Use descriptive test method names (testFlowName_Scenario_ExpectedResult)
- Add proper comments explaining test logic
- Avoid hardcoded IDs, use dynamic queries
- Test with different user profiles/permissions when relevant

Flow Testing Specifics:
- Use Flow.Interview class to invoke flows programmatically
- Test input and output variables
- Verify record operations (create, update, delete)
- Test decision paths and conditional logic
- Validate error handling and fault paths
- Test with both single records and bulk data

Code Structure:
- Class annotations (@isTest)
- Constants for test data
- @TestSetup method for common data
- Individual test methods for each scenario
- Utility methods for test data creation
- Proper exception handling

{format_instructions}"""),
            ("human", """Generate comprehensive Apex test classes for the following Flow testing requirements:

Flow Name: {flow_name}
Flow Type: {flow_type}
Target Objects: {target_objects}

Test Scenarios:
{test_scenarios}

Salesforce Object Information:
{object_info}

Generation Options:
- Class Name Prefix: {class_name_prefix}
- Include Test Setup: {include_test_setup}
- Target Coverage: {target_coverage}%
- API Version: {api_version}

Please generate:
1. Complete Apex test class(es) with proper structure
2. @TestSetup method for common test data
3. Individual test methods for each scenario
4. Proper assertions and validations
5. Error handling and negative test cases
6. Comments explaining test logic
7. Best practices implementation

Ensure the code is production-ready, follows naming conventions, and provides comprehensive test coverage.""")
        ])
        
        return parser, prompt_template
    
    def _run(
        self,
        test_scenarios: List[TestScenario],
        flow_name: str,
        flow_type: str,
        target_objects: List[str] = None,
        salesforce_objects_info: List[SalesforceObjectInfo] = None,
        class_name_prefix: str = "Test",
        include_test_setup: bool = True,
        target_coverage: int = 85,
        api_version: str = "59.0"
    ) -> str:
        """Generate Apex test class code"""
        try:
            parser, prompt_template = self._create_parser_and_prompt()
            
            # Format test scenarios
            scenarios_text = []
            for scenario in test_scenarios:
                scenario_dict = scenario.model_dump()
                scenarios_text.append(json.dumps(scenario_dict, indent=2))
            
            # Format object info
            object_info_text = "No object information provided"
            if salesforce_objects_info:
                object_info_list = []
                for obj_info in salesforce_objects_info:
                    obj_dict = obj_info.model_dump()
                    object_info_list.append(json.dumps(obj_dict, indent=2))
                object_info_text = "\n".join(object_info_list)
            
            # Create the prompt
            messages = prompt_template.format_messages(
                flow_name=flow_name,
                flow_type=flow_type,
                target_objects=", ".join(target_objects or []),
                test_scenarios="\n\n".join(scenarios_text),
                object_info=object_info_text,
                class_name_prefix=class_name_prefix,
                include_test_setup=include_test_setup,
                target_coverage=target_coverage,
                api_version=api_version,
                format_instructions=parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self._llm.invoke(messages)
            
            # Parse the response
            generation_response = parser.parse(response.content)
            
            # Format the output
            return self._format_generation_response(generation_response)
            
        except Exception as e:
            return f"Error generating Apex test class: {str(e)}"
    
    def _format_generation_response(self, response: ApexCodeGenerationResponse) -> str:
        """Format the generation response into a readable string"""
        output = []
        
        if not response.success:
            output.append(f"❌ Code generation failed: {response.error_message}")
            return "\n".join(output)
        
        output.append("=== APEX TEST CLASS GENERATION RESULTS ===")
        output.append(f"✅ Successfully generated {len(response.apex_test_classes)} test class(es)")
        output.append(f"📊 Estimated Coverage: {response.estimated_coverage}%")
        output.append(f"🧪 Total Test Methods: {response.test_methods_count}")
        output.append(f"📝 Lines of Code: {response.lines_of_code}")
        output.append("")
        
        # Generated code
        if response.deployable_code:
            output.append("=== GENERATED APEX TEST CLASSES ===")
            for i, code in enumerate(response.deployable_code, 1):
                output.append(f"\n--- Test Class {i} ---")
                output.append(code)
        
        # Best practices applied
        if response.best_practices_applied:
            output.append("\n=== BEST PRACTICES APPLIED ===")
            for practice in response.best_practices_applied:
                output.append(f"✅ {practice}")
        
        # Warnings
        if response.warnings:
            output.append("\n=== WARNINGS ===")
            for warning in response.warnings:
                output.append(f"⚠️ {warning}")
        
        return "\n".join(output)

    def get_structured_response(
        self,
        test_scenarios: List[TestScenario],
        flow_name: str,
        flow_type: str,
        target_objects: List[str] = None,
        salesforce_objects_info: List[SalesforceObjectInfo] = None,
        class_name_prefix: str = "Test",
        include_test_setup: bool = True,
        target_coverage: int = 85,
        api_version: str = "59.0"
    ) -> ApexCodeGenerationResponse:
        """Get structured response instead of formatted string"""
        try:
            parser, prompt_template = self._create_parser_and_prompt()
            
            # Format test scenarios
            scenarios_text = []
            for scenario in test_scenarios:
                scenario_dict = scenario.model_dump()
                scenarios_text.append(json.dumps(scenario_dict, indent=2))
            
            # Format object info
            object_info_text = "No object information provided"
            if salesforce_objects_info:
                object_info_list = []
                for obj_info in salesforce_objects_info:
                    obj_dict = obj_info.model_dump()
                    object_info_list.append(json.dumps(obj_dict, indent=2))
                object_info_text = "\n".join(object_info_list)
            
            # Create the prompt
            messages = prompt_template.format_messages(
                flow_name=flow_name,
                flow_type=flow_type,
                target_objects=", ".join(target_objects or []),
                test_scenarios="\n\n".join(scenarios_text),
                object_info=object_info_text,
                class_name_prefix=class_name_prefix,
                include_test_setup=include_test_setup,
                target_coverage=target_coverage,
                api_version=api_version,
                format_instructions=parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self._llm.invoke(messages)
            
            # Parse and return the response
            return parser.parse(response.content)
            
        except Exception as e:
            return ApexCodeGenerationResponse(
                success=False,
                error_message=f"Error generating Apex test class: {str(e)}"
            )

class SalesforceSchemaAnalyzerTool(BaseTool):
    """
    Tool that analyzes Salesforce org schema to provide object metadata
    needed for comprehensive test data creation and Flow testing.
    """
    name: str = "salesforce_schema_analyzer_tool"
    description: str = (
        "Analyze Salesforce org schema to retrieve object metadata including "
        "required fields, relationships, validation rules, and constraints. "
        "Provides insights for test data creation and Flow testing requirements."
    )
    args_schema: Type[BaseModel] = SalesforceSchemaAnalysisRequest
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__()
        self._llm = llm  # Store as private attribute
    
    def _run(
        self,
        target_objects: List[str],
        org_alias: str,
        include_relationships: bool = True,
        include_validation_rules: bool = True
    ) -> str:
        """Analyze Salesforce schema for the specified objects"""
        try:
            # For now, this is a mock implementation
            # In a real implementation, this would use Salesforce APIs to retrieve schema
            
            mock_objects_info = []
            
            for obj_name in target_objects:
                # Create mock object info based on common Salesforce objects
                obj_info = self._create_mock_object_info(obj_name)
                mock_objects_info.append(obj_info)
            
            response = SalesforceSchemaAnalysisResponse(
                success=True,
                objects_info=mock_objects_info,
                schema_insights={
                    "total_objects_analyzed": len(target_objects),
                    "relationships_found": sum(len(obj.parent_relationships) for obj in mock_objects_info),
                    "validation_rules_found": sum(len(obj.validation_rules) for obj in mock_objects_info)
                },
                test_data_recommendations=[
                    "Use TestDataFactory pattern for consistent test data creation",
                    "Create test data that respects validation rules and required fields",
                    "Consider using @TestSetup for data that can be shared across test methods",
                    "Test with both minimal and comprehensive data sets"
                ]
            )
            
            return self._format_schema_response(response)
            
        except Exception as e:
            return f"Error analyzing Salesforce schema: {str(e)}"
    
    def _create_mock_object_info(self, object_name: str) -> SalesforceObjectInfo:
        """Create mock object information for common Salesforce objects"""
        
        # Common object patterns
        common_objects = {
            "Account": SalesforceObjectInfo(
                object_name="Account",
                label="Account",
                required_fields=["Name"],
                optional_fields=["Type", "Industry", "Phone", "Website", "BillingCity", "BillingState"],
                parent_relationships={},
                child_relationships=["Contact", "Opportunity", "Case"],
                validation_rules=["Account_Name_Required", "Phone_Format_Validation"],
                unique_fields=[],
                picklist_fields={"Type": ["Prospect", "Customer", "Partner"], "Industry": ["Technology", "Finance", "Healthcare"]},
                test_data_considerations=[
                    "Name field is required and must be unique in test context",
                    "Consider different Account types for varied test scenarios"
                ]
            ),
            "Contact": SalesforceObjectInfo(
                object_name="Contact",
                label="Contact",
                required_fields=["LastName"],
                optional_fields=["FirstName", "Email", "Phone", "Title", "Department"],
                parent_relationships={"AccountId": "Account"},
                child_relationships=["Case", "Opportunity"],
                validation_rules=["Email_Format_Validation", "Contact_LastName_Required"],
                unique_fields=["Email"],
                picklist_fields={"Salutation": ["Mr.", "Ms.", "Dr."]},
                test_data_considerations=[
                    "LastName is required",
                    "Email should be unique if provided",
                    "AccountId relationship should be valid"
                ]
            ),
            "Opportunity": SalesforceObjectInfo(
                object_name="Opportunity",
                label="Opportunity",
                required_fields=["Name", "StageName", "CloseDate"],
                optional_fields=["Amount", "Probability", "Type", "LeadSource"],
                parent_relationships={"AccountId": "Account"},
                child_relationships=["OpportunityLineItem"],
                validation_rules=["CloseDate_Future_Validation", "Amount_Positive_Validation"],
                unique_fields=[],
                picklist_fields={
                    "StageName": ["Prospecting", "Qualification", "Needs Analysis", "Proposal", "Closed Won", "Closed Lost"],
                    "Type": ["New Customer", "Existing Customer - Upgrade", "Existing Customer - Replacement"]
                },
                test_data_considerations=[
                    "StageName must be valid picklist value",
                    "CloseDate should be in the future for open opportunities",
                    "Amount should be positive if provided"
                ]
            )
        }
        
        # Return specific object info if available, otherwise create generic info
        if object_name in common_objects:
            return common_objects[object_name]
        else:
            return SalesforceObjectInfo(
                object_name=object_name,
                label=object_name,
                required_fields=["Name"],
                optional_fields=["Description", "CreatedDate", "LastModifiedDate"],
                parent_relationships={},
                child_relationships=[],
                validation_rules=[],
                unique_fields=[],
                picklist_fields={},
                test_data_considerations=[
                    f"Custom object {object_name} - verify actual field requirements",
                    "Consider custom validation rules and business logic"
                ]
            )
    
    def _format_schema_response(self, response: SalesforceSchemaAnalysisResponse) -> str:
        """Format the schema analysis response"""
        output = []
        
        if not response.success:
            output.append(f"❌ Schema analysis failed: {response.error_message}")
            return "\n".join(output)
        
        output.append("=== SALESFORCE SCHEMA ANALYSIS RESULTS ===")
        output.append(f"✅ Successfully analyzed {len(response.objects_info)} object(s)")
        output.append("")
        
        # Object details
        for obj_info in response.objects_info:
            output.append(f"=== {obj_info.object_name} ({obj_info.label}) ===")
            
            output.append(f"Required Fields: {', '.join(obj_info.required_fields)}")
            if obj_info.optional_fields:
                output.append(f"Optional Fields: {', '.join(obj_info.optional_fields[:5])}...")  # Show first 5
            
            if obj_info.parent_relationships:
                output.append("Parent Relationships:")
                for field, parent_obj in obj_info.parent_relationships.items():
                    output.append(f"  - {field} → {parent_obj}")
            
            if obj_info.child_relationships:
                output.append(f"Child Objects: {', '.join(obj_info.child_relationships)}")
            
            if obj_info.validation_rules:
                output.append(f"Validation Rules: {', '.join(obj_info.validation_rules)}")
            
            if obj_info.unique_fields:
                output.append(f"Unique Fields: {', '.join(obj_info.unique_fields)}")
            
            if obj_info.test_data_considerations:
                output.append("Test Data Considerations:")
                for consideration in obj_info.test_data_considerations:
                    output.append(f"  💡 {consideration}")
            
            output.append("")
        
        # Recommendations
        if response.test_data_recommendations:
            output.append("=== TEST DATA RECOMMENDATIONS ===")
            for rec in response.test_data_recommendations:
                output.append(f"📋 {rec}")
        
        return "\n".join(output)
    
    def get_structured_response(
        self,
        target_objects: List[str],
        org_alias: str,
        include_relationships: bool = True,
        include_validation_rules: bool = True
    ) -> SalesforceSchemaAnalysisResponse:
        """Get structured response instead of formatted string"""
        try:
            # Mock implementation - same as _run but returns structured response
            mock_objects_info = []
            
            for obj_name in target_objects:
                obj_info = self._create_mock_object_info(obj_name)
                mock_objects_info.append(obj_info)
            
            return SalesforceSchemaAnalysisResponse(
                success=True,
                objects_info=mock_objects_info,
                schema_insights={
                    "total_objects_analyzed": len(target_objects),
                    "relationships_found": sum(len(obj.parent_relationships) for obj in mock_objects_info),
                    "validation_rules_found": sum(len(obj.validation_rules) for obj in mock_objects_info)
                },
                test_data_recommendations=[
                    "Use TestDataFactory pattern for consistent test data creation",
                    "Create test data that respects validation rules and required fields",
                    "Consider using @TestSetup for data that can be shared across test methods",
                    "Test with both minimal and comprehensive data sets"
                ]
            )
            
        except Exception as e:
            return SalesforceSchemaAnalysisResponse(
                success=False,
                error_message=f"Error analyzing Salesforce schema: {str(e)}"
            ) 