# Core LangChain and LLM imports
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Typing and Pydantic models
from typing import List, Dict, Optional, Any

# Project-specific imports
from src.tools.apex_test_runner_tool import ApexTestRunnerTool
from src.schemas.test_executor_schemas import (
    TestExecutorRequest, TestExecutorResponse
)
from src.state.agent_workforce_state import AgentWorkforceState
from src.config import get_llm

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Get LLM instance for test executor agent
LLM = get_llm(
    agent_name="TEST_EXECUTOR",
    temperature=0.1,  # Low temperature for consistent test execution
    max_tokens=2048  # Sufficient for test analysis and reporting
)

# Initialize tools with the LLM
TEST_EXECUTOR_TOOLS = [
    ApexTestRunnerTool()
]

TEST_EXECUTOR_AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """
    You are a specialized Salesforce Test Executor Agent with expertise in running and analyzing Apex test results.
    
    Your primary responsibilities:
    1. Execute already-deployed Apex test classes in Salesforce orgs
    2. Monitor test execution progress and collect detailed results
    3. Analyze test failures and provide diagnostic information  
    4. Generate comprehensive test reports with coverage metrics
    5. Provide actionable feedback for test-driven development iterations
    
    Available Tools:
    - apex_test_runner_tool: Execute deployed Apex test classes and retrieve detailed results
    
    Your Process:
    1. Use apex_test_runner_tool to execute the specified test classes
    2. Analyze the test results for patterns and insights
    3. Generate a comprehensive report with actionable recommendations
    4. Identify specific issues for feedback to other agents (like FlowBuilder)
    
    Test Analysis Principles:
    - Categorize failures by type (compilation vs runtime vs assertion)
    - Identify patterns in test failures that suggest Flow logic issues
    - Provide specific, actionable feedback for fixing failed tests
    - Highlight code coverage gaps and recommendations
    - Focus on quality and reliability of test feedback
    
    Important: You only execute tests that are already deployed to the org. You do NOT deploy test classes.
    If test classes are missing, you should report this as an error requiring prior deployment.
    
    Always provide clear, detailed test execution reports that development teams can use immediately
    to understand test results and take corrective action.
    """),
    ("human", """
    I need you to execute Apex test classes that have already been deployed to a Salesforce org.
    
    Test Execution Request:
    - Test Classes: {test_class_names}
    - Org Alias: {org_alias}
    - Coverage Target: {coverage_target}%
    - Timeout: {timeout_minutes} minutes
    - Request ID: {request_id}
    - Salesforce Session: Available in the full_request data
    
    IMPORTANT: You have been provided with a complete TestExecutorRequest in the full_request parameter.
    When calling the apex_test_runner_tool, you MUST use this full_request object as the input.
    
    The full_request contains all necessary authentication information including:
    - Salesforce session details (session_id, instance_url, etc.)
    - Test class names to execute
    - Coverage targets and timeout settings
    - Request tracking information
    
    Please use your apex_test_runner_tool with the full_request to:
    1. Execute the specified test classes using the provided Salesforce session
    2. Retrieve detailed test results including pass/fail status, error messages, and stack traces
    3. Collect code coverage information
    4. Analyze the results and provide actionable feedback
    
    Focus on providing a comprehensive analysis that can help identify:
    - Why any tests failed and how to fix them
    - Whether code coverage meets the target
    - Specific recommendations for improving test quality or Flow logic
    
    Generate a complete test execution report with clear next steps.
    """),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def create_test_executor_agent_executor() -> AgentExecutor:
    """
    Creates the LangChain agent executor for the TestExecutor Agent.
    """
    agent = create_tool_calling_agent(LLM, TEST_EXECUTOR_TOOLS, TEST_EXECUTOR_AGENT_PROMPT_TEMPLATE)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=TEST_EXECUTOR_TOOLS, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,  # Limited iterations since this is primarily tool execution
        max_execution_time=600,  # 10-minute timeout for test execution
        early_stopping_method="generate"
    )
    return agent_executor

def run_test_executor_agent(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Executes the TestExecutor agent and updates the graph state with test execution results.
    Expects 'current_test_executor_request' to be set in the input state.
    """
    print("--- Running TestExecutor Agent ---")
    
    # Debug logging
    print(f"DEBUG: Received state keys: {list(state.keys())}")
    
    test_executor_request_dict = state.get("current_test_executor_request")
    print(f"DEBUG: test_executor_request_dict = {test_executor_request_dict}")
    
    if not test_executor_request_dict:
        print("TestExecutor Agent: No test_executor_request provided in current_test_executor_request.")
        updated_state = state.copy()
        error_response = TestExecutorResponse(
            request_id="unknown",
            success=False,
            request=TestExecutorRequest(
                request_id="unknown",
                salesforce_session=state.get("salesforce_session", {}),
                test_class_names=[],
                org_alias="unknown"
            ),
            error_message="TestExecutor Agent Error: No test_executor_request provided."
        )
        updated_state["current_test_executor_response"] = error_response.model_dump()
        return updated_state

    try:
        # Convert dict back to Pydantic model
        print(f"DEBUG: Attempting to create TestExecutorRequest from: {test_executor_request_dict}")
        test_request = TestExecutorRequest(**test_executor_request_dict)
        
        print(f"✅ TestExecutor Agent processing request for {len(test_request.test_class_names)} test classes")
        
        # Create agent executor
        agent_executor = create_test_executor_agent_executor()
        
        # Pass the COMPLETE TestExecutorRequest to the agent
        # The agent will pass this directly to the apex_test_runner_tool
        agent_input = {
            "request_id": test_request.request_id,
            "test_class_names": test_request.test_class_names,
            "org_alias": test_request.org_alias,
            "coverage_target": test_request.coverage_target,
            "timeout_minutes": test_request.timeout_minutes,
            "salesforce_session": test_request.salesforce_session.model_dump(),
            "full_request": test_request.model_dump()  # Include full request for tool
        }
        
        print("🧠 Executing test execution with TestExecutor Agent...")
        
        # Execute the agent with the test execution request
        result = agent_executor.invoke(agent_input)
        
        print(f"✅ TestExecutor Agent completed execution")
        print(f"Agent output: {result.get('output', 'No output')}")
        
        # The tool should have been called and returned a TestExecutorResponse
        # Extract the response from the tool execution
        test_response = _extract_test_response_from_agent_result(result, test_request)
        
        updated_state = state.copy()
        updated_state["current_test_executor_response"] = test_response.model_dump()
        
        # Store test execution results in state
        if test_response.success:
            updated_state["test_execution_results"] = [result.model_dump() for result in test_response.test_results]
            updated_state["code_coverage_results"] = [result.model_dump() for result in test_response.code_coverage_results]
            updated_state["test_execution_summary"] = test_response.test_run_summary.model_dump() if test_response.test_run_summary else None
            print(f"📊 Executed {len(test_response.test_results)} test methods")
            print(f"📈 Retrieved coverage for {len(test_response.code_coverage_results)} classes")
            if test_response.overall_coverage_percentage:
                print(f"🎯 Overall coverage: {test_response.overall_coverage_percentage}%")
        else:
            print(f"⚠️ Test execution completed but no test summary available")
        
        # Clear the request after processing
        updated_state["current_test_executor_request"] = None
        
        return updated_state

    except Exception as e:
        print(f"TestExecutor Agent: Error processing test execution: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        updated_state = state.copy()
        error_response = TestExecutorResponse(
            request_id=test_executor_request_dict.get("request_id", "unknown"),
            success=False,
            request=TestExecutorRequest(
                request_id="error",
                salesforce_session=state.get("salesforce_session", {}),
                test_class_names=[],
                org_alias="unknown"
            ),
            error_message=f"TestExecutor Agent Processing Error: {str(e)}"
        )
        updated_state["current_test_executor_response"] = error_response.model_dump()
        updated_state["current_test_executor_request"] = None
        
        return updated_state

def _extract_test_response_from_agent_result(agent_result: Dict[str, Any], test_request: TestExecutorRequest) -> TestExecutorResponse:
    """
    Extract TestExecutorResponse from agent execution result.
    The agent should have called the apex_test_runner_tool which returns a TestExecutorResponse.
    """
    
    # Check if we have intermediate steps with tool calls
    intermediate_steps = agent_result.get("intermediate_steps", [])
    
    for step in intermediate_steps:
        if len(step) >= 2:
            action, observation = step[0], step[1]
            
            # Check if this was a call to our test runner tool
            if hasattr(action, 'tool') and action.tool == "apex_test_runner_tool":
                # The observation should be our TestExecutorResponse
                if isinstance(observation, TestExecutorResponse):
                    return observation
                elif isinstance(observation, dict):
                    # Try to reconstruct from dict
                    try:
                        return TestExecutorResponse(**observation)
                    except Exception as e:
                        print(f"⚠️ Could not reconstruct TestExecutorResponse from dict: {e}")
    
    # If we couldn't extract a proper response, create an error response
    agent_output = agent_result.get("output", "No detailed output available")
    
    return TestExecutorResponse(
        request_id=test_request.request_id,
        success=False,
        request=test_request,
        error_message=f"Could not extract test results from agent execution. Agent output: {agent_output}"
    ) 