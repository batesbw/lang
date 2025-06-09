#!/usr/bin/env python3
"""
Simple test script for TestExecutor Agent functionality.
Tests authentication and Apex test execution with AccountContactCounterTest.
"""

import os
import sys
import uuid
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
from src.agents.authentication_agent import run_authentication_agent
from src.agents.test_executor_agent import run_test_executor_agent
from src.schemas.auth_schemas import AuthenticationRequest, SalesforceAuthResponse
from src.schemas.test_executor_schemas import TestExecutorRequest
from src.state.agent_workforce_state import AgentWorkforceState

# Load environment
load_dotenv()

def main():
    print("🧪 APEX TEST EXECUTION DEMO")
    print("=" * 50)
    
    try:
        # Step 1: Authenticate
        print("\n🔐 STEP 1: Authenticate to Salesforce")
        print("-" * 30)
        org_alias = os.getenv("ORG_ALIAS", "E2E_TEST_ORG")
        print(f"Using org alias: {org_alias}")
        
        auth_state = authenticate_to_salesforce(org_alias)
        
        # Step 2: Execute tests
        print("\n🧪 STEP 2: Execute Apex Tests")
        print("-" * 30)
        test_class = "AccountContactCounterTest"
        print(f"Executing test class: {test_class}")
        
        test_state = execute_apex_tests(auth_state, test_class)
        
        # Display results
        display_results(test_state)
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        return 1
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    return 0

def authenticate_to_salesforce(org_alias: str) -> AgentWorkforceState:
    """Authenticate to Salesforce using the Authentication Agent"""
    
    # Create initial state with auth request
    auth_request = AuthenticationRequest(
        org_alias=org_alias,
        credential_type="env_alias"
    )
    
    initial_state = AgentWorkforceState()
    initial_state["current_auth_request"] = auth_request.model_dump()
    
    print("--- Running Authentication Agent ---")
    auth_state = run_authentication_agent(initial_state)
    
    # Verify authentication
    salesforce_session = auth_state.get("salesforce_session")
    if not salesforce_session or not salesforce_session.get("success"):
        raise Exception("Authentication failed")
    
    print("✅ Authentication successful!")
    print(f"Instance: {salesforce_session.get('instance_url', 'Unknown')}")
    print(f"Session ID: {salesforce_session.get('session_id', 'Unknown')[:20]}...")
    
    return auth_state

def execute_apex_tests(auth_state: AgentWorkforceState, test_class: str) -> AgentWorkforceState:
    """Execute Apex tests using the TestExecutor Agent"""
    
    request_id = str(uuid.uuid4())
    print(f"Request ID: {request_id}")
    
    # Get authenticated session from auth state
    salesforce_session = auth_state.get("salesforce_session")
    if not salesforce_session:
        raise Exception("No authenticated Salesforce session available")
    
    # Create test execution request
    test_executor_request = TestExecutorRequest(
        request_id=request_id,
        salesforce_session=salesforce_session,
        test_class_names=[test_class],
        org_alias=os.getenv("ORG_ALIAS", "E2E_TEST_ORG"),
        coverage_target=75.0,
        timeout_minutes=10
    )
    
    # Add request to state
    test_state = auth_state.copy()
    test_state["current_test_executor_request"] = test_executor_request.model_dump()
    
    print("--- Running TestExecutor Agent ---")
    result_state = run_test_executor_agent(test_state)
    
    return result_state

def display_results(test_state: AgentWorkforceState):
    """Display test execution results"""
    print("\n📊 TEST RESULTS:")
    print("-" * 20)
    
    # Get test response from state
    test_response = test_state.get("current_test_executor_response")
    
    if not test_response:
        print("❌ No test results found in state")
        return
    
    success = test_response.get("success", False)
    error_message = test_response.get("error_message")
    
    if success:
        print("✅ Test execution successful!")
        
        # Display test results if available
        test_results = test_response.get("test_results", [])
        if test_results:
            print(f"\n📋 {len(test_results)} tests executed:")
            for result in test_results:
                outcome = result.get("outcome", "Unknown")
                class_name = result.get("test_class_name", "Unknown")
                method_name = result.get("test_method_name", "Unknown")
                time_str = f" ({result.get('time', 0):.2f}s)" if result.get('time') else ""
                
                status_emoji = "✅" if outcome == "Pass" else "❌"
                print(f"   {status_emoji} {class_name}.{method_name}: {outcome}{time_str}")
                
                # Show error details for failed tests
                if outcome != "Pass":
                    message = result.get("message")
                    if message:
                        print(f"      💬 {message}")
        
        # Display summary if available
        test_summary = test_response.get("test_run_summary")
        if test_summary:
            total_tests = test_summary.get("tests_ran", 0)
            failures = test_summary.get("failures", 0)
            successes = test_summary.get("successes", 0)
            print(f"\n📊 SUMMARY: {successes} passed, {failures} failed out of {total_tests} total")
    else:
        print("❌ Test execution failed!")
        if error_message:
            print(f"Error: {error_message}")

if __name__ == "__main__":
    sys.exit(main()) 