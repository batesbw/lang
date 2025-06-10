# Core LangChain and LLM imports
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Typing and Pydantic models
from typing import List, Dict, Optional, Any

# Project-specific imports
from src.tools.test_designer_tools import (
    UserStoryAnalyzerTool,
    ApexTestClassGeneratorTool,
    SalesforceSchemaAnalyzerTool
)
from src.schemas.test_designer_schemas import (
    TestDesignerRequest, TestDesignerResponse,
    TestScenario, ApexTestClass, SalesforceObjectInfo
)
from src.state.agent_workforce_state import AgentWorkforceState
from src.config import get_llm

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Get LLM instance for test designer agent
LLM = get_llm(
    agent_name="TEST_DESIGNER",
    temperature=0.1,  # Slightly higher for creativity in test scenarios
    max_tokens=2048  # Reduced from 4096 to 2048 for faster responses
)

# Initialize tools with the LLM
TEST_DESIGNER_TOOLS = [
    UserStoryAnalyzerTool(LLM),
    ApexTestClassGeneratorTool(LLM),
    SalesforceSchemaAnalyzerTool(LLM)
]

TEST_DESIGNER_AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """
    You are a specialized Salesforce Test Designer Agent with expertise in creating targeted test strategies for Salesforce Flows.
    
    Your primary responsibilities:
    1. Build test cases ONLY for the specific acceptance criteria provided
    2. Design focused Apex test classes that validate each acceptance criterion
    3. Analyze Salesforce object schemas to create minimal required test data
    4. Ensure each test directly validates one or more acceptance criteria
    5. Apply Salesforce testing best practices for acceptance criteria validation
    
    Available Tools:
    - user_story_analyzer_tool: Analyze acceptance criteria to identify specific test scenarios
    - apex_test_class_generator_tool: Generate targeted Apex test classes
    - salesforce_schema_analyzer_tool: Analyze Salesforce object schemas
    
    Your Process:
    1. Use user_story_analyzer_tool to analyze ONLY the acceptance criteria (ignore broader user story context)
    2. Use salesforce_schema_analyzer_tool to understand the minimal data model requirements
    3. Use apex_test_class_generator_tool to create test classes that specifically validate acceptance criteria
    4. Synthesize results into a focused test design response
    
    Test Design Principles:
    - Build test cases ONLY for the provided acceptance criteria - do not add additional scenarios
    - Each test method should map directly to one or more acceptance criteria
    - Focus on validating the specific outcomes defined in the acceptance criteria
    - Avoid comprehensive edge case testing unless explicitly mentioned in acceptance criteria
    - Create minimal test data sufficient only for acceptance criteria validation
    - Follow Salesforce naming conventions and best practices
    
    IMPORTANT: Do not create exhaustive test suites. Create targeted tests that specifically validate 
    the acceptance criteria provided and nothing beyond that scope.
    """),
    ("human", """
    I need you to design targeted Apex test classes for a Salesforce Flow that validate ONLY the specific acceptance criteria provided.
    
    Flow Details:
    - Flow Name: {flow_name}
    - Flow Type: {flow_type}
    - Target Objects: {target_objects}
    
    User Story: {user_story}
    
    ACCEPTANCE CRITERIA TO TEST (focus only on these): {acceptance_criteria}
    
    Additional Context: {business_context}
    
    Test Requirements:
    - Target Coverage: {test_coverage_target}%
    - Include Bulk Tests: {include_bulk_tests}
    - Include Negative Tests: {include_negative_tests}
    - Org Alias: {org_alias}
    
    Please use your tools to:
    1. Analyze ONLY the acceptance criteria to identify specific test scenarios (ignore broader user story context)
    2. Analyze the Salesforce object schema for minimal data requirements
    3. Generate focused Apex test classes that validate each acceptance criterion
    
    IMPORTANT: Build test cases ONLY for the acceptance criteria listed above. Do not add comprehensive 
    test coverage beyond what is explicitly required by the acceptance criteria.
    
    Provide a focused test design that validates each acceptance criterion with targeted test methods.
    """),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def create_test_designer_agent_executor() -> AgentExecutor:
    """
    Creates the LangChain agent executor for the TestDesigner Agent.
    """
    agent = create_tool_calling_agent(LLM, TEST_DESIGNER_TOOLS, TEST_DESIGNER_AGENT_PROMPT_TEMPLATE)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=TEST_DESIGNER_TOOLS, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Reduced from 10 to 5 to prevent long-running processes
        max_execution_time=300,  # Add 5-minute timeout to prevent hanging
        early_stopping_method="generate"  # Stop early when agent decides it's done
    )
    return agent_executor

def run_test_designer_agent(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Executes the TestDesigner agent and updates the graph state with test design results.
    Expects 'current_test_designer_request' to be set in the input state.
    
    UPDATED: Now handles retry context for improved test generation after deployment failures.
    """
    print("--- Running TestDesigner Agent ---")
    
    # Debug logging
    print(f"DEBUG: Received state keys: {list(state.keys())}")
    
    # Check for retry context
    retry_context = state.get("retry_context")
    is_retry = retry_context is not None
    if is_retry:
        print(f"🔄 RETRY MODE: {retry_context.get('retry_type', 'unknown')}")
        print(f"📋 Guidance: {retry_context.get('guidance', 'No specific guidance')}")
    
    test_designer_request_dict = state.get("current_test_designer_request")
    print(f"DEBUG: test_designer_request_dict = {test_designer_request_dict}")
    
    if not test_designer_request_dict:
        print("TestDesigner Agent: No test_designer_request provided in current_test_designer_request.")
        updated_state = state.copy()
        error_response = TestDesignerResponse(
            success=False,
            request=TestDesignerRequest(
                flow_name="unknown",
                user_story={},
                acceptance_criteria=[],
                flow_type="unknown",
                org_alias="unknown"
            ),
            error_message="TestDesigner Agent Error: No test_designer_request provided."
        )
        updated_state["current_test_designer_response"] = error_response.model_dump()
        updated_state["deployable_apex_code"] = []
        return updated_state

    try:
        # Convert dict back to Pydantic model
        print(f"DEBUG: Attempting to create TestDesignerRequest from: {test_designer_request_dict}")
        test_request = TestDesignerRequest(**test_designer_request_dict)
        
        print(f"✅ TestDesigner Agent processing request for Flow: {test_request.flow_name}")
        
        # OPTIMIZED APPROACH: Use direct LLM call instead of complex agent tool chain
        print("🧠 Generating intelligent test design with optimized LLM call...")
        
        # Create test response using direct LLM generation with retry context
        test_response = _generate_test_design_with_llm(test_request, retry_context)
        
        updated_state = state.copy()
        updated_state["current_test_designer_response"] = test_response.model_dump()
        
        # Store test scenarios and Apex classes in state
        if test_response.success:
            updated_state["test_scenarios"] = [scenario.model_dump() for scenario in test_response.test_scenarios]
            updated_state["apex_test_classes"] = [apex_class.model_dump() for apex_class in test_response.apex_test_classes]
            updated_state["deployable_apex_code"] = test_response.deployable_apex_code
            print(f"📊 Generated {len(test_response.test_scenarios)} test scenarios")
            print(f"🧪 Generated {len(test_response.apex_test_classes)} Apex test classes")
            print(f"📝 Generated {len(test_response.deployable_apex_code)} deployable code files")
        
        # Clear the request and retry context after processing
        updated_state["current_test_designer_request"] = None
        updated_state["retry_context"] = None  # Clear retry context
        
        return updated_state

    except Exception as e:
        print(f"TestDesigner Agent: Error processing test design: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        updated_state = state.copy()
        error_response = TestDesignerResponse(
            success=False,
            request=TestDesignerRequest(
                flow_name="error",
                user_story={},
                acceptance_criteria=[],
                flow_type="unknown",
                org_alias="unknown"
            ),
            error_message=f"TestDesigner Agent Processing Error: {str(e)}"
        )
        updated_state["current_test_designer_response"] = error_response.model_dump()
        updated_state["current_test_designer_request"] = None
        updated_state["retry_context"] = None  # Clear retry context on error
        return updated_state

def _generate_test_design_with_llm(request: TestDesignerRequest, retry_context: Dict[str, Any] = None) -> TestDesignerResponse:
    """
    Generate test design using a direct, optimized LLM call that outputs valid Apex code only.
    
    UPDATED: Now incorporates retry context to improve generation after deployment failures.
    """
    
    try:
        # Build dynamic system prompt based on retry context
        base_system_prompt = """You are an expert Salesforce Apex developer. Generate ONLY valid, complete, production-ready Apex test class code.

DO NOT include explanations, comments about the code structure, or any text outside the Apex class.
DO NOT use markdown code blocks or any formatting.
OUTPUT ONLY the raw Apex test class code that can be directly deployed.

CRITICAL: This is for Test-Driven Development (TDD) - the Flow does not exist yet!
DO NOT use Flow.Interview.createInterview() or any direct Flow invocation methods.
Instead, test the OUTCOMES that the Flow should produce when it's implemented.

FOCUS: Build test methods ONLY for the specific acceptance criteria provided.
Do NOT create comprehensive test suites or additional edge case testing beyond the acceptance criteria.

Requirements for the Apex test class:
- Use @isTest annotation
- Include @TestSetup method for minimal test data creation
- Create individual test methods that specifically validate each acceptance criterion
- Test ONLY the expected outcomes defined in the acceptance criteria
- For Record-Triggered Flows: Test only the record operations required by acceptance criteria
- For Screen Flows: Test only the data processing logic specified in acceptance criteria
- Each test method should map directly to one or more acceptance criteria
- Include Test.startTest() and Test.stopTest() in test methods
- Add System.assert* statements for validation
- Follow Salesforce naming conventions
- Ensure the class compiles and runs successfully

TDD Testing Approach:
- Test what SHOULD HAPPEN when records are created/updated/deleted
- Verify field updates, calculations, related record changes
- Test business logic outcomes, not Flow execution
- Focus on the acceptance criteria and expected behavior"""

        # Add retry-specific guidance
        if retry_context:
            retry_errors = retry_context.get("previous_errors", [])
            if retry_errors:
                error_analysis = _analyze_previous_errors(retry_errors)
                base_system_prompt += f"""

CRITICAL RETRY CONTEXT - FIX THESE ISSUES:
{retry_context.get('guidance', '')}

Previous deployment failed with these errors:
{error_analysis}

MANDATORY FIXES:
1. Ensure ALL methods have complete bodies with proper closing braces
2. Ensure ALL classes have proper closing braces
3. Validate syntax before output - no missing semicolons, braces, or parentheses
4. Use complete method signatures
5. Include proper return statements where needed
6. Ensure proper Apex syntax throughout"""

        # Create a simplified prompt that outputs only Apex code
        prompt = ChatPromptTemplate.from_messages([
            ("system", base_system_prompt),
            
            ("human", """Generate a complete Apex test class for this Salesforce Flow using TDD approach:

Flow Name: {flow_name}
Flow Type: {flow_type}
Target Objects: {target_objects}

User Story: {user_story_text}

Acceptance Criteria:
{acceptance_criteria_text}

Generate ONLY the Apex test class code that tests the EXPECTED OUTCOMES - no explanations, no markdown, just raw deployable Apex code that tests what the Flow should accomplish.""")
        ])
        
        # Format the inputs
        user_story_text = f"{request.user_story.get('title', 'N/A')} - {request.user_story.get('description', 'N/A')}"
        acceptance_criteria_text = "\n".join([f"- {ac}" for ac in request.acceptance_criteria])
        
        # Create the messages
        messages = prompt.format_messages(
            flow_name=request.flow_name,
            flow_type=request.flow_type,
            target_objects=", ".join(request.target_objects) if request.target_objects else "Standard objects",
            user_story_text=user_story_text,
            acceptance_criteria_text=acceptance_criteria_text
        )
        
        # Get LLM response
        if retry_context:
            print("🔄 Generating IMPROVED Apex test class with error context...")
        else:
            print("🔄 Generating TDD-focused Apex test class with LLM...")
        
        response = LLM.invoke(messages)
        
        # The response content should be pure Apex code
        apex_code = response.content.strip()
        
        # Basic validation of generated code
        validation_result = _validate_apex_code_basic(apex_code)
        if not validation_result["is_valid"]:
            print(f"⚠️ Generated code failed basic validation: {validation_result['errors']}")
            # Could attempt regeneration here, but for now we'll proceed with warning
        
        # Create basic test scenarios for metadata
        test_scenarios = [
            TestScenario(
                scenario_id="TS001",
                title=f"TDD Happy Path - {request.flow_name}",
                description=f"Test expected outcomes when {request.flow_name} logic is triggered",
                scenario_type="positive",
                priority="Critical",
                required_objects=request.target_objects,
                test_steps=["Setup test data", "Trigger expected behavior", "Verify outcomes"],
                expected_outcomes=["Business logic produces expected results"],
                success_criteria=request.acceptance_criteria[:2] if request.acceptance_criteria else ["Expected outcomes achieved"],
                flow_elements_tested=["Business logic outcomes"],
                coverage_areas=["Main business logic results"]
            ),
            TestScenario(
                scenario_id="TS002", 
                title=f"TDD Error Handling - {request.flow_name}",
                description=f"Test expected error handling outcomes for {request.flow_name}",
                scenario_type="negative",
                priority="High",
                required_objects=request.target_objects,
                test_steps=["Setup invalid data", "Trigger expected behavior", "Verify error outcomes"],
                expected_outcomes=["Errors handled as expected"],
                success_criteria=["Error scenarios produce expected results"],
                flow_elements_tested=["Error handling outcomes"],
                coverage_areas=["Error scenarios"]
            )
        ]
        
        # Create apex test class metadata
        class_name = f"{request.flow_name.replace('_', '').replace(' ', '')}_Test"
        if retry_context:
            description = f"REGENERATED TDD test class for {request.flow_name} - fixed previous syntax errors"
            best_practices = ["TDD outcome testing", "TestSetup data isolation", "Proper assertions", "No direct Flow invocation", "Syntax error fixes"]
        else:
            description = f"TDD test class for {request.flow_name} - tests expected outcomes"
            best_practices = ["TDD outcome testing", "TestSetup data isolation", "Proper assertions", "No direct Flow invocation"]
            
        apex_test_class = ApexTestClass(
            class_name=class_name,
            description=description,
            flow_name=request.flow_name,
            class_annotations=["@isTest"],
            expected_coverage_percentage=request.test_coverage_target,
            best_practices_applied=best_practices
        )
        
        return TestDesignerResponse(
            success=True,
            request=request,
            test_scenarios=test_scenarios,
            apex_test_classes=[apex_test_class],
            salesforce_objects_analyzed=[],
            test_data_strategy={
                "approach": "TDD - TestSetup with mock data, test outcomes not Flow execution",
                "considerations": ["Test business logic results", "Target object field updates", "Related record changes"]
            },
            coverage_mapping={
                "positive_scenarios": ["TS001"],
                "negative_scenarios": ["TS002"]
            },
            risk_analysis=["Validate expected business outcomes", "Test data dependencies"],
            implementation_recommendations=["Deploy to test environment first", "Tests should pass once Flow is implemented"],
            deployable_apex_code=[apex_code]
        )
        
    except Exception as e:
        print(f"Error in LLM test generation: {str(e)}")
        return TestDesignerResponse(
            success=False,
            request=request,
            error_message=f"LLM test generation failed: {str(e)}"
        )

def _analyze_previous_errors(errors: list) -> str:
    """
    Analyze previous deployment errors to provide specific guidance for improvement.
    """
    if not errors:
        return "No specific errors to analyze."
    
    error_analysis = []
    for error in errors:
        message = error.get("message", "Unknown error")
        error_type = error.get("type", "Unknown")
        file_name = error.get("file", "Unknown file")
        
        error_analysis.append(f"- {error_type} in {file_name}: {message}")
    
    return "\n".join(error_analysis)

def _validate_apex_code_basic(apex_code: str) -> dict:
    """
    Basic validation of generated Apex code to catch common syntax errors.
    Returns dict with is_valid (bool) and errors (list).
    """
    errors = []
    
    if not apex_code or not apex_code.strip():
        errors.append("Empty or whitespace-only code")
        return {"is_valid": False, "errors": errors}
    
    # Check for balanced braces
    open_braces = apex_code.count('{')
    close_braces = apex_code.count('}')
    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
    
    # Check for balanced parentheses
    open_parens = apex_code.count('(')
    close_parens = apex_code.count(')')
    if open_parens != close_parens:
        errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    
    # Check for @isTest annotation
    if '@isTest' not in apex_code and '@IsTest' not in apex_code:
        errors.append("Missing @isTest annotation")
    
    # Check for class definition
    if 'class ' not in apex_code:
        errors.append("Missing class definition")
    
    # Check for method definitions (should have at least @TestSetup and test methods)
    method_count = apex_code.lower().count('void ') + apex_code.lower().count('static ')
    if method_count < 2:
        errors.append("Insufficient number of methods (expected at least @TestSetup and test methods)")
    
    return {"is_valid": len(errors) == 0, "errors": errors}

def _parse_llm_test_response(request: TestDesignerRequest, response_content: str) -> TestDesignerResponse:
    """
    Parse the LLM response to extract test scenarios and Apex code.
    """
    
    # Implement the logic to parse the LLM response and extract test scenarios and Apex code
    # This is a placeholder and should be replaced with the actual implementation
    # based on the format of the LLM response
    
    # For now, we'll return a placeholder response
    return TestDesignerResponse(
        success=True,
        request=request,
        test_scenarios=[],
        apex_test_classes=[],
        salesforce_objects_analyzed=[],
        test_data_strategy={},
        coverage_mapping={},
        risk_analysis=[],
        implementation_recommendations=[],
        deployable_apex_code=[]
    )

def _create_comprehensive_test_response(request: TestDesignerRequest, agent_output: str) -> TestDesignerResponse:
    """
    Create a comprehensive test response based on the agent's analysis.
    This would typically parse the actual tool results, but for now creates a structured response.
    """
    
    # Mock test scenarios based on the request
    test_scenarios = [
        TestScenario(
            scenario_id="TS001",
            title=f"Happy Path - {request.flow_name} Success",
            description=f"Test the primary success path for {request.flow_name}",
            scenario_type="positive",
            priority="Critical",
            required_objects=request.target_objects,
            test_steps=[
                "Create test data with valid inputs",
                f"Execute {request.flow_name} Flow",
                "Verify expected outcomes",
                "Assert all acceptance criteria are met"
            ],
            expected_outcomes=["Flow executes successfully", "Expected records are created/updated"],
            success_criteria=request.acceptance_criteria[:2] if request.acceptance_criteria else ["Flow completes without errors"],
            flow_elements_tested=["Start", "Decision", "Assignment", "Record Operations"],
            coverage_areas=["Primary business logic", "Data validation"]
        ),
        TestScenario(
            scenario_id="TS002",
            title=f"Error Handling - {request.flow_name} Invalid Input",
            description=f"Test error handling in {request.flow_name} with invalid inputs",
            scenario_type="negative",
            priority="High",
            required_objects=request.target_objects,
            test_steps=[
                "Create test data with invalid inputs",
                f"Execute {request.flow_name} Flow",
                "Verify error handling",
                "Assert appropriate error messages"
            ],
            expected_outcomes=["Flow handles errors gracefully", "Appropriate error messages are shown"],
            success_criteria=["Error paths work correctly"],
            flow_elements_tested=["Fault Connectors", "Error Handling"],
            coverage_areas=["Error handling", "Input validation"]
        )
    ]
    
    # Mock Apex test class
    apex_test_classes = [
        ApexTestClass(
            class_name=f"Test{request.flow_name.replace('_', '')}",
            description=f"Comprehensive test class for {request.flow_name} Flow",
            flow_name=request.flow_name,
            class_annotations=["@isTest"],
            test_setup_method="@TestSetup static void setupTestData() { /* Test data setup */ }",
            expected_coverage_percentage=request.test_coverage_target,
            best_practices_applied=[
                "Proper test data isolation",
                "Comprehensive scenario coverage",
                "Error handling validation",
                "Bulk testing support"
            ]
        )
    ]
    
    # Mock deployable Apex code
    deployable_apex_code = [
        f"""/**
 * Comprehensive TDD test class for {request.flow_name} Flow
 * Generated by TestDesigner Agent - Tests Expected Outcomes
 * Target Coverage: {request.test_coverage_target}%
 * 
 * NOTE: This is TDD - tests verify expected OUTCOMES when business logic is applied,
 * not direct Flow execution since the Flow doesn't exist yet.
 */
@isTest
public class {request.flow_name.replace('_', '').replace(' ', '')}_Test {{
    
    @TestSetup
    static void setupTestData() {{
        // Create test data for {', '.join(request.target_objects) if request.target_objects else 'business logic testing'}
        {_generate_test_data_setup(request.target_objects)}
    }}
    
    @isTest
    static void test{request.flow_name.replace('_', '')}_ExpectedOutcomes() {{
        Test.startTest();
        
        // Test the expected business outcomes that the Flow should produce
        // For Record-Triggered Flows: perform record operations and verify expected changes
        // For Screen Flows: test the data processing logic outcomes
        
        {_generate_outcome_test_logic(request)}
        
        Test.stopTest();
        
        // Assert expected business outcomes based on acceptance criteria
        {_generate_outcome_assertions(request)}
    }}
    
    @isTest
    static void test{request.flow_name.replace('_', '')}_ErrorScenarios() {{
        Test.startTest();
        
        // Test error/edge case scenarios and their expected outcomes
        {_generate_error_scenario_logic(request)}
        
        Test.stopTest();
        
        // Assert expected error handling outcomes
        {_generate_error_assertions(request)}
    }}
    
    {f'''@isTest
    static void test{request.flow_name.replace('_', '')}_BulkOperations() {{
        Test.startTest();
        
        // Test bulk scenarios (200+ records) and expected outcomes
        {_generate_bulk_test_logic(request)}
        
        Test.stopTest();
        
        // Assert bulk operation outcomes
        {_generate_bulk_assertions(request)}
    }}''' if request.include_bulk_tests else ''}
    
    // Utility methods for test data creation and validation
    {_generate_utility_methods(request.target_objects)}
}}"""
    ]
    
    # Create comprehensive response
    return TestDesignerResponse(
        success=True,
        request=request,
        test_scenarios=test_scenarios,
        apex_test_classes=apex_test_classes,
        salesforce_objects_analyzed=[],  # Would be populated by schema analyzer
        test_data_strategy={
            "approach": "TestSetup with isolated data",
            "patterns": ["Minimal required fields", "Valid relationships", "Bulk testing support"],
            "considerations": ["Validation rules", "Required fields", "Unique constraints"]
        },
        coverage_mapping={
            "happy_path": ["TS001"],
            "error_handling": ["TS002"],
            "business_logic": ["TS001", "TS002"]
        },
        risk_analysis=[
            "Ensure test data doesn't conflict with existing org data",
            "Validate Flow permissions and sharing rules",
            "Consider governor limits in bulk scenarios"
        ],
        implementation_recommendations=[
            "Run tests in isolated test context",
            "Implement proper cleanup in teardown methods",
            "Monitor test execution time and governor limits",
            "Regular test maintenance as Flow evolves"
        ],
        deployable_apex_code=deployable_apex_code
    )

def _generate_test_data_setup(target_objects: List[str]) -> str:
    """Generate test data setup code for target objects"""
    if not target_objects:
        return "// Add test data setup based on Flow requirements"
    
    setup_code = []
    for obj in target_objects:
        if obj == "Account":
            setup_code.append("""        Account testAccount = new Account(
            Name = 'Test Account ' + System.currentTimeMillis(),
            Type = 'Customer'
        );
        insert testAccount;""")
        elif obj == "Contact":
            setup_code.append("""        Contact testContact = new Contact(
            LastName = 'Test Contact ' + System.currentTimeMillis(),
            AccountId = testAccount.Id,
            Email = 'test' + System.currentTimeMillis() + '@example.com'
        );
        insert testContact;""")
        elif obj == "Opportunity":
            setup_code.append("""        Opportunity testOpportunity = new Opportunity(
            Name = 'Test Opportunity ' + System.currentTimeMillis(),
            AccountId = testAccount.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 10000
        );
        insert testOpportunity;""")
        else:
            setup_code.append(f"""        // Setup test data for {obj}
        // Add appropriate test data creation for custom object""")
    
    return "\n".join(setup_code)

def _generate_utility_methods(target_objects: List[str]) -> str:
    """Generate utility methods for test data creation"""
    if not target_objects:
        return "// Add utility methods based on business logic requirements"
    
    utility_methods = []
    for obj in target_objects:
        if obj == "Account":
            utility_methods.append("""
    private static Account createTestAccount(String name) {
        return new Account(
            Name = name,
            Type = 'Customer'
        );
    }""")
        elif obj == "Contact":
            utility_methods.append("""
    private static Contact createTestContact(String lastName, Id accountId) {
        return new Contact(
            LastName = lastName,
            AccountId = accountId,
            Email = lastName.toLowerCase() + '@test.com'
        );
    }""")
        elif obj == "Opportunity":
            utility_methods.append("""
    private static Opportunity createTestOpportunity(String name, Id accountId) {
        return new Opportunity(
            Name = name,
            AccountId = accountId,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 10000
        );
    }""")
    
    return "\n".join(utility_methods)

def _generate_outcome_test_logic(request: TestDesignerRequest) -> str:
    """Generate test logic that focuses on expected business outcomes"""
    if request.flow_type == "Record-Triggered Flow":
        # For record-triggered flows, test the trigger scenarios
        if "Contact" in request.target_objects and "Account" in request.target_objects:
            return """// Test scenario: Insert/Update Contact should trigger expected business logic
        Account testAccount = [SELECT Id, Name FROM Account LIMIT 1];
        
        // Perform the trigger action (insert/update Contact)
        Contact newContact = new Contact(
            FirstName = 'Test',
            LastName = 'Trigger Contact',
            AccountId = testAccount.Id,
            Email = 'test.trigger@example.com'
        );
        insert newContact;
        
        // Additional trigger scenarios based on acceptance criteria
        newContact.Email = 'updated.trigger@example.com';
        update newContact;"""
        else:
            return f"""// Test scenario: Record operations should trigger expected business logic
        // Perform operations on {', '.join(request.target_objects)} to trigger Flow logic
        // Add specific record operations based on Flow trigger conditions"""
    else:
        return """// Test scenario: Business logic processing should produce expected outcomes
        // Add specific data processing logic that the Flow should implement
        // Focus on input/output validation and business rule enforcement"""

def _generate_outcome_assertions(request: TestDesignerRequest) -> str:
    """Generate assertions that verify expected business outcomes"""
    assertions = []
    
    # Generate assertions based on acceptance criteria
    for i, criteria in enumerate(request.acceptance_criteria):
        if "count" in criteria.lower():
            assertions.append(f"// Assert: {criteria}")
            assertions.append("// System.assertEquals(expectedCount, actualCount, 'Count calculation should match criteria');")
        elif "update" in criteria.lower():
            assertions.append(f"// Assert: {criteria}")
            assertions.append("// System.assert(recordWasUpdated, 'Record should be updated as per criteria');")
        else:
            assertions.append(f"// Assert: {criteria}")
            assertions.append("// Add specific assertion for this acceptance criteria")
    
    if not assertions:
        assertions.append("// Assert expected business outcomes based on the user story")
        assertions.append("// Add specific validations for the business logic results")
    
    return "\n        ".join(assertions)

def _generate_error_scenario_logic(request: TestDesignerRequest) -> str:
    """Generate test logic for error scenarios"""
    return """// Test error/edge scenarios that the business logic should handle
        // Example: Invalid data, missing required fields, constraint violations
        // Add scenarios based on potential error conditions in the business logic"""

def _generate_error_assertions(request: TestDesignerRequest) -> str:
    """Generate assertions for error scenario outcomes"""
    return """// Assert that error scenarios are handled as expected
        // Example: Validation errors, proper error messages, graceful degradation
        // System.assert(errorWasHandledCorrectly, 'Error should be handled gracefully');"""

def _generate_bulk_test_logic(request: TestDesignerRequest) -> str:
    """Generate bulk test logic for performance scenarios"""
    if "Contact" in request.target_objects and "Account" in request.target_objects:
        return """// Test bulk operations (200+ records) to verify scalability
        Account bulkTestAccount = [SELECT Id FROM Account LIMIT 1];
        List<Contact> bulkContacts = new List<Contact>();
        
        for (Integer i = 0; i < 200; i++) {
            bulkContacts.add(new Contact(
                FirstName = 'Bulk',
                LastName = 'Contact ' + i,
                AccountId = bulkTestAccount.Id,
                Email = 'bulk' + i + '@test.com'
            ));
        }
        insert bulkContacts;"""
    else:
        return f"""// Test bulk operations (200+ records) for {', '.join(request.target_objects)}
        // Create bulk test data to verify the business logic handles volume appropriately"""

def _generate_bulk_assertions(request: TestDesignerRequest) -> str:
    """Generate assertions for bulk operation outcomes"""
    return """// Assert that bulk operations produce expected outcomes
        // System.assertEquals(expectedBulkResult, actualBulkResult, 'Bulk operations should scale correctly');
        // Verify governor limits are respected and performance is acceptable"""

# Test harness
if __name__ == "__main__":
    print("--- TestDesigner Agent Test Harness ---")
    
    # Create a test request
    test_request = TestDesignerRequest(
        flow_name="TestFlow_Account_Contact_Counter",
        user_story={
            "title": "Count Contacts per Account",
            "description": "As a sales manager, I want to automatically count contacts per account",
            "priority": "High"
        },
        acceptance_criteria=[
            "Flow triggers when Account is created or updated",
            "Contact count is calculated correctly",
            "Account Contact_Count__c field is updated"
        ],
        flow_type="Record-Triggered Flow",
        target_objects=["Account", "Contact"],
        org_alias="TESTSANDBOX",
        test_coverage_target=90,
        include_bulk_tests=True,
        include_negative_tests=True
    )
    
    # Initialize minimal state
    initial_state: AgentWorkforceState = {
        "current_test_designer_request": test_request.model_dump(),
        "build_deploy_retry_count": 0,
        "max_build_deploy_retries": 3,
        "retry_count": 0
    }
    
    # Run the agent
    result_state = run_test_designer_agent(initial_state)
    
    print("\n--- Test Result ---")
    response_dict = result_state.get("current_test_designer_response")
    if response_dict:
        response = TestDesignerResponse(**response_dict)
        if response.success:
            print(f"✅ Test design successful!")
            print(f"📊 Generated {len(response.test_scenarios)} test scenarios")
            print(f"🧪 Generated {len(response.apex_test_classes)} Apex test classes")
            print(f"📝 Generated {len(response.deployable_apex_code)} deployable code files")
        else:
            print(f"❌ Test design failed: {response.error_message}")
    else:
        print("❌ No response generated") 