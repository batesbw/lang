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

# Get LLM instance for test executor agent (keeping for potential future use)
LLM = get_llm(
    agent_name="TEST_EXECUTOR",
    temperature=0.1,  # Low temperature for consistent test execution
    max_tokens=2048  # Sufficient for test analysis and reporting
)

# Initialize tools
TEST_EXECUTOR_TOOLS = [
    ApexTestRunnerTool()
]

def run_test_executor_agent(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Executes the TestExecutor agent and updates the graph state with test execution results.
    Now directly calls the ApexTestRunnerTool instead of using LLM agent to avoid processing raw results.
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
        print(f"📋 Test classes: {test_request.test_class_names}")
        print(f"🏢 Org: {test_request.salesforce_session.instance_url}")
        print(f"🎯 Coverage target: {test_request.coverage_target}%")
        
        # Create the ApexTestRunnerTool directly
        apex_test_tool = ApexTestRunnerTool()
        
        print("🧪 Executing test execution directly with ApexTestRunnerTool...")
        
        # Call the tool directly with the full request
        # This bypasses the LLM agent and provides raw test execution results
        test_response = apex_test_tool._run(full_request=test_request.model_dump())
        
        print(f"✅ TestExecutor Tool completed execution")
        print(f"📊 Success: {test_response.success}")
        
        if test_response.success:
            print(f"📈 Test Results: {len(test_response.test_results)} test methods")
            print(f"📊 Coverage Results: {len(test_response.code_coverage_results)} classes")
            if test_response.overall_coverage_percentage:
                print(f"🎯 Overall Coverage: {test_response.overall_coverage_percentage}%")
        else:
            print(f"❌ Test execution failed: {test_response.error_message}")
        
        updated_state = state.copy()
        updated_state["current_test_executor_response"] = test_response.model_dump()
        
        # Store test execution results in state for other agents to use
        if test_response.success:
            updated_state["test_execution_results"] = [result.model_dump() for result in test_response.test_results]
            updated_state["code_coverage_results"] = [result.model_dump() for result in test_response.code_coverage_results]
            updated_state["test_execution_summary"] = test_response.test_run_summary.model_dump() if test_response.test_run_summary else None
            
            # Log detailed results for transparency
            print(f"📊 DETAILED TEST RESULTS:")
            for test_result in test_response.test_results:
                status_emoji = "✅" if test_result.outcome == "Pass" else "❌"
                print(f"   {status_emoji} {test_result.test_class_name}.{test_result.test_method_name}: {test_result.outcome}")
                if test_result.message and test_result.outcome != "Pass":
                    print(f"      Message: {test_result.message}")
            
            print(f"📈 COVERAGE RESULTS:")
            for coverage in test_response.code_coverage_results:
                print(f"   📋 {coverage.apex_class_or_trigger_name}: {coverage.coverage_percentage}% ({coverage.num_lines_covered}/{coverage.num_lines_covered + coverage.num_lines_uncovered} lines)")
        else:
            print(f"⚠️ Test execution failed: {test_response.error_message}")
        
        # Clear the request after processing
        updated_state["current_test_executor_request"] = None
        
        return updated_state

    except Exception as e:
        print(f"TestExecutor Agent: Error processing test execution: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        updated_state = state.copy()
        
        # Try to get request_id from the original request
        request_id = "unknown"
        if test_executor_request_dict and isinstance(test_executor_request_dict, dict):
            request_id = test_executor_request_dict.get("request_id", "unknown")
        
        error_response = TestExecutorResponse(
            request_id=request_id,
            success=False,
            request=TestExecutorRequest(
                request_id=request_id,
                salesforce_session=state.get("salesforce_session") or {
                    "success": False,
                    "session_id": "",
                    "instance_url": "",
                    "user_id": "unknown",
                    "org_id": "unknown",
                    "auth_type_used": "unknown"
                },
                test_class_names=[],
                org_alias="unknown"
            ),
            error_message=f"TestExecutor Agent Processing Error: {str(e)}"
        )
        updated_state["current_test_executor_response"] = error_response.model_dump()
        updated_state["current_test_executor_request"] = None
        
        return updated_state

# Keeping the legacy functions for backward compatibility but they won't be used
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
    ("user", """
    Please execute the Apex test classes with the following request:
    
    Request ID: {request_id}
    Test Classes: {test_class_names}
    Org Alias: {org_alias}
    Coverage Target: {coverage_target}%
    Timeout: {timeout_minutes} minutes
    
    Full Request Data: {full_request}
    
    Use the apex_test_runner_tool to execute these tests and provide detailed analysis of the results.
    Focus on returning actionable feedback for any failures and comprehensive coverage information.
    """)
])

def create_test_executor_agent_executor() -> AgentExecutor:
    """
    Creates the LangChain agent executor for the TestExecutor Agent.
    NOTE: This is now deprecated in favor of direct tool calling for raw results.
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

def _extract_test_response_from_agent_result(agent_result: Dict[str, Any], test_request: TestExecutorRequest) -> TestExecutorResponse:
    """
    Extract TestExecutorResponse from agent execution result.
    NOTE: This is now deprecated in favor of direct tool calling.
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