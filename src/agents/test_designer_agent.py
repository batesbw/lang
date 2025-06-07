# Core LangChain and LLM imports
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
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

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Ensure ANTHROPIC_API_KEY is set
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

LLM = ChatAnthropic(
    model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"), 
    temperature=0.1,  # Slightly higher for creativity in test scenarios
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048"))  # Reduced from 4096 to 2048 for faster responses
)

# Initialize tools with the LLM
TEST_DESIGNER_TOOLS = [
    UserStoryAnalyzerTool(LLM),
    ApexTestClassGeneratorTool(LLM),
    SalesforceSchemaAnalyzerTool(LLM)
]

TEST_DESIGNER_AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """
    You are a specialized Salesforce Test Designer Agent with expertise in creating comprehensive test strategies for Salesforce Flows.
    
    Your primary responsibilities:
    1. Analyze user stories and acceptance criteria to identify all necessary test scenarios
    2. Design comprehensive Apex test classes that thoroughly test Flow functionality
    3. Analyze Salesforce object schemas to create appropriate test data
    4. Ensure test coverage meets or exceeds targets (typically 85%+)
    5. Apply Salesforce testing best practices throughout the design process
    
    Available Tools:
    - user_story_analyzer_tool: Analyze user stories to identify test scenarios
    - apex_test_class_generator_tool: Generate comprehensive Apex test classes
    - salesforce_schema_analyzer_tool: Analyze Salesforce object schemas
    
    Your Process:
    1. Use user_story_analyzer_tool to analyze the user story and acceptance criteria
    2. Use salesforce_schema_analyzer_tool to understand the data model for target objects
    3. Use apex_test_class_generator_tool to create comprehensive test classes
    4. Synthesize results into a complete test design response
    
    Test Design Principles:
    - Cover all acceptance criteria with specific test scenarios
    - Include positive, negative, edge case, and boundary testing
    - Design for both single record and bulk data scenarios
    - Consider error handling and fault paths
    - Ensure test data respects validation rules and constraints
    - Follow Salesforce naming conventions and best practices
    
    Always provide clear, actionable test designs that development teams can implement immediately.
    Focus on quality, completeness, and maintainability of the test suite.
    """),
    ("human", """
    I need you to design comprehensive Apex test classes for a Salesforce Flow.
    
    Flow Details:
    - Flow Name: {flow_name}
    - Flow Type: {flow_type}
    - Target Objects: {target_objects}
    
    User Story: {user_story}
    
    Acceptance Criteria: {acceptance_criteria}
    
    Additional Context: {business_context}
    
    Test Requirements:
    - Target Coverage: {test_coverage_target}%
    - Include Bulk Tests: {include_bulk_tests}
    - Include Negative Tests: {include_negative_tests}
    - Org Alias: {org_alias}
    
    Please use your tools to:
    1. Analyze the user story and acceptance criteria to identify comprehensive test scenarios
    2. Analyze the Salesforce object schema for the target objects
    3. Generate complete Apex test classes that provide thorough test coverage
    
    Provide a complete test design that includes test scenarios, Apex test classes, and deployment-ready code.
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
    """
    print("--- Running TestDesigner Agent ---")
    
    # Debug logging
    print(f"DEBUG: Received state keys: {list(state.keys())}")
    
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
        
        # Create test response using direct LLM generation
        test_response = _generate_test_design_with_llm(test_request)
        
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
        
        # Clear the request after processing
        updated_state["current_test_designer_request"] = None
        
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
        updated_state["deployable_apex_code"] = []
        return updated_state

def _generate_test_design_with_llm(request: TestDesignerRequest) -> TestDesignerResponse:
    """
    Generate test design using a direct, optimized LLM call that outputs valid Apex code only.
    """
    
    try:
        # Create a simplified prompt that outputs only Apex code
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Salesforce Apex developer. Generate ONLY valid, complete, production-ready Apex test class code.

DO NOT include explanations, comments about the code structure, or any text outside the Apex class.
DO NOT use markdown code blocks or any formatting.
OUTPUT ONLY the raw Apex test class code that can be directly deployed.

Requirements for the Apex test class:
- Use @isTest annotation
- Include @TestSetup method for test data creation
- Create individual test methods for positive, negative, and bulk scenarios
- Use proper Flow.Interview.createInterview() for Flow testing
- Include Test.startTest() and Test.stopTest() in test methods
- Add System.assert* statements for validation
- Follow Salesforce naming conventions
- Ensure the class compiles and runs successfully"""),
            
            ("human", """Generate a complete Apex test class for this Salesforce Flow:

Flow Name: {flow_name}
Flow Type: {flow_type}
Target Objects: {target_objects}

User Story: {user_story_text}

Acceptance Criteria:
{acceptance_criteria_text}

Generate ONLY the Apex test class code - no explanations, no markdown, just raw deployable Apex code.""")
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
        print("🔄 Generating Apex test class with LLM...")
        response = LLM.invoke(messages)
        
        # The response content should be pure Apex code
        apex_code = response.content.strip()
        
        # Create basic test scenarios for metadata
        test_scenarios = [
            TestScenario(
                scenario_id="TS001",
                title=f"Happy Path - {request.flow_name}",
                description=f"Test successful execution of {request.flow_name}",
                scenario_type="positive",
                priority="Critical",
                required_objects=request.target_objects,
                test_steps=["Setup test data", f"Execute {request.flow_name}", "Verify results"],
                expected_outcomes=["Flow executes successfully"],
                success_criteria=request.acceptance_criteria[:2] if request.acceptance_criteria else ["Flow completes"],
                flow_elements_tested=["Flow execution"],
                coverage_areas=["Main flow logic"]
            ),
            TestScenario(
                scenario_id="TS002", 
                title=f"Error Handling - {request.flow_name}",
                description=f"Test error conditions in {request.flow_name}",
                scenario_type="negative",
                priority="High",
                required_objects=request.target_objects,
                test_steps=["Setup invalid data", f"Execute {request.flow_name}", "Verify error handling"],
                expected_outcomes=["Errors handled gracefully"],
                success_criteria=["Error paths work correctly"],
                flow_elements_tested=["Error handling"],
                coverage_areas=["Error scenarios"]
            )
        ]
        
        # Create apex test class metadata
        class_name = f"Test{request.flow_name.replace('_', '').replace(' ', '')}"
        apex_test_class = ApexTestClass(
            class_name=class_name,
            description=f"Test class for {request.flow_name}",
            flow_name=request.flow_name,
            class_annotations=["@isTest"],
            expected_coverage_percentage=request.test_coverage_target,
            best_practices_applied=["TestSetup data isolation", "Proper assertions", "Flow testing patterns"]
        )
        
        return TestDesignerResponse(
            success=True,
            request=request,
            test_scenarios=test_scenarios,
            apex_test_classes=[apex_test_class],
            salesforce_objects_analyzed=[],
            test_data_strategy={
                "approach": "TestSetup with mock data",
                "considerations": ["Flow input validation", "Target object requirements"]
            },
            coverage_mapping={
                "positive_scenarios": ["TS001"],
                "negative_scenarios": ["TS002"]
            },
            risk_analysis=["Validate Flow permissions", "Test data dependencies"],
            implementation_recommendations=["Deploy to test environment first", "Monitor test execution"],
            deployable_apex_code=[apex_code]
        )
        
    except Exception as e:
        print(f"Error in LLM test generation: {str(e)}")
        return TestDesignerResponse(
            success=False,
            request=request,
            error_message=f"LLM test generation failed: {str(e)}"
        )

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
 * Comprehensive test class for {request.flow_name} Flow
 * Generated by TestDesigner Agent
 * Target Coverage: {request.test_coverage_target}%
 */
@isTest
public class Test{request.flow_name.replace('_', '')} {{
    
    @TestSetup
    static void setupTestData() {{
        // Create test data for {', '.join(request.target_objects) if request.target_objects else 'flow testing'}
        {_generate_test_data_setup(request.target_objects)}
    }}
    
    @isTest
    static void test{request.flow_name.replace('_', '')}_HappyPath() {{
        Test.startTest();
        
        // Execute {request.flow_name} Flow with valid inputs
        Map<String, Object> flowInputs = new Map<String, Object>();
        // Add specific input variables based on Flow requirements
        
        Flow.Interview flowInterview = Flow.Interview.createInterview('{request.flow_name}', flowInputs);
        flowInterview.start();
        
        Test.stopTest();
        
        // Assert expected outcomes
        System.assertNotEquals(null, flowInterview, 'Flow interview should be created');
        // Add specific assertions based on acceptance criteria
    }}
    
    @isTest
    static void test{request.flow_name.replace('_', '')}_ErrorHandling() {{
        Test.startTest();
        
        // Test error handling with invalid inputs
        Map<String, Object> invalidInputs = new Map<String, Object>();
        // Add invalid input scenarios
        
        try {{
            Flow.Interview flowInterview = Flow.Interview.createInterview('{request.flow_name}', invalidInputs);
            flowInterview.start();
            
            // Assert error handling if Flow doesn't throw exceptions
            // Add appropriate assertions for error scenarios
        }} catch (Exception e) {{
            // Verify expected exception handling
            System.assert(e.getMessage().contains('expected_error_pattern'), 'Expected error message not found');
        }}
        
        Test.stopTest();
    }}
    
    {f'''@isTest
    static void test{request.flow_name.replace('_', '')}_BulkProcessing() {{
        Test.startTest();
        
        // Create bulk test data (200+ records)
        List<Map<String, Object>> bulkInputs = new List<Map<String, Object>>();
        for (Integer i = 0; i < 200; i++) {{
            Map<String, Object> bulkInput = new Map<String, Object>();
            // Add bulk input data
            bulkInputs.add(bulkInput);
        }}
        
        // Execute Flow with bulk data
        for (Map<String, Object> input : bulkInputs) {{
            Flow.Interview bulkInterview = Flow.Interview.createInterview('{request.flow_name}', input);
            bulkInterview.start();
        }}
        
        Test.stopTest();
        
        // Assert bulk processing results
        // Add bulk operation validations
    }}''' if request.include_bulk_tests else ''}
    
    // Utility methods for test data creation
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
        return "// Add utility methods for test data creation"
    
    methods = []
    for obj in target_objects:
        method_name = f"create{obj}"
        methods.append(f"""    private static {obj} {method_name}() {{
        {obj} test{obj} = new {obj}();
        // Set required fields for {obj}
        return test{obj};
    }}""")
    
    return "\n\n".join(methods)

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