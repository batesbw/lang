#!/usr/bin/env python3
"""
Independent test script for the TestExecutor Agent.
Tests the agent's ability to execute Apex tests and provide detailed feedback.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any
import uuid

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
from src.agents.test_executor_agent import run_test_executor_agent, create_test_executor_agent_executor
from src.agents.authentication_agent import run_authentication_agent
from src.schemas.test_executor_schemas import TestExecutorRequest
from src.schemas.auth_schemas import AuthenticationRequest
from src.state.agent_workforce_state import AgentWorkforceState

# Load environment variables
load_dotenv()

def setup_test_state() -> AgentWorkforceState:
    """Set up the initial state for testing the TestExecutor agent"""
    
    # Get org alias from environment or use default
    org_alias = os.getenv("ORG_ALIAS", "default")
    
    print(f"🔧 Setting up test state for org: {org_alias}")
    
    # Create authentication request
    auth_request = AuthenticationRequest(
        org_alias=org_alias
    )
    
    # Initial state with authentication request
    state = AgentWorkforceState(
        current_auth_request=auth_request.model_dump()
    )
    
    return state

def test_authentication_first(state: AgentWorkforceState) -> AgentWorkforceState:
    """Run authentication agent first to get valid Salesforce session"""
    print("🔐 Running Authentication Agent to get Salesforce session...")
    
    try:
        updated_state = run_authentication_agent(state)
        
        auth_response = updated_state.get("current_auth_response")
        if not auth_response or not auth_response.get("success"):
            error_msg = auth_response.get("error_message", "Unknown auth error") if auth_response else "No auth response"
            raise Exception(f"Authentication failed: {error_msg}")
        
        print("✅ Authentication successful!")
        print(f"   Session ID: {auth_response['session_id'][:20]}...")
        print(f"   Instance URL: {auth_response['instance_url']}")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        raise

def test_executor_agent_execution(state: AgentWorkforceState) -> AgentWorkforceState:
    """Test the TestExecutor agent with AccountContactCounterFlowTest"""
    print("\n🧪 Testing TestExecutor Agent...")
    
    # Get the authenticated Salesforce session
    auth_response = state.get("current_auth_response")
    if not auth_response:
        raise Exception("No authenticated Salesforce session available")
    
    # The user mentioned "AccountContactCounterTest" but the actual file is "AccountContactCounterFlowTest"
    # Let's test with the actual class name
    test_class_name = "AccountContactCounterFlowTest"
    
    # Create test executor request
    test_request = TestExecutorRequest(
        request_id=str(uuid.uuid4()),
        salesforce_session=auth_response,
        test_class_names=[test_class_name],
        org_alias=auth_response.get("org_alias", "default"),
        timeout_minutes=5,
        coverage_target=75.0
    )
    
    print(f"📋 Test Execution Request:")
    print(f"   Test Classes: {test_request.test_class_names}")
    print(f"   Org Alias: {test_request.org_alias}")
    print(f"   Coverage Target: {test_request.coverage_target}%")
    print(f"   Timeout: {test_request.timeout_minutes} minutes")
    
    # Add the test request to state
    updated_state = state.copy()
    updated_state["current_test_executor_request"] = test_request.model_dump()
    
    # Run the TestExecutor agent
    try:
        result_state = run_test_executor_agent(updated_state)
        return result_state
    except Exception as e:
        print(f"❌ TestExecutor agent failed: {str(e)}")
        raise

def analyze_test_results(state: AgentWorkforceState):
    """Analyze and display the test execution results"""
    print("\n📊 Analyzing Test Results...")
    
    test_response = state.get("current_test_executor_response")
    if not test_response:
        print("❌ No test response found in state")
        return
    
    print(f"🎯 Test Execution Results:")
    print(f"   Success: {test_response.get('success', False)}")
    print(f"   Request ID: {test_response.get('request_id', 'unknown')}")
    
    if test_response.get("error_message"):
        print(f"   Error: {test_response['error_message']}")
        return
    
    # Test run summary
    test_summary = test_response.get("test_run_summary")
    if test_summary:
        print(f"\n📈 Test Run Summary:")
        print(f"   Status: {test_summary.get('status', 'unknown')}")
        print(f"   Tests Ran: {test_summary.get('tests_ran', 0)}")
        print(f"   Successes: {test_summary.get('successes', 0)}")
        print(f"   Failures: {test_summary.get('failures', 0)}")
        if test_summary.get('time'):
            print(f"   Execution Time: {test_summary['time']}ms")
    
    # Individual test results
    test_results = test_response.get("test_results", [])
    if test_results:
        print(f"\n🔍 Individual Test Results ({len(test_results)} tests):")
        for result in test_results:
            status_emoji = "✅" if result.get("outcome") == "Pass" else "❌"
            print(f"   {status_emoji} {result.get('test_class_name', 'unknown')}.{result.get('test_method_name', 'unknown')}")
            if result.get("outcome") != "Pass":
                print(f"      Outcome: {result.get('outcome', 'unknown')}")
                if result.get("message"):
                    print(f"      Message: {result['message']}")
                if result.get("stack_trace"):
                    print(f"      Stack Trace: {result['stack_trace'][:200]}...")
    
    # Code coverage results
    coverage_results = test_response.get("code_coverage_results", [])
    if coverage_results:
        print(f"\n📊 Code Coverage Results ({len(coverage_results)} classes):")
        for coverage in coverage_results:
            name = coverage.get("apex_class_or_trigger_name", "unknown")
            percentage = coverage.get("coverage_percentage", 0)
            covered = coverage.get("num_lines_covered", 0)
            uncovered = coverage.get("num_lines_uncovered", 0)
            print(f"   📋 {name}: {percentage:.1f}% ({covered}/{covered + uncovered} lines)")
    
    # Overall metrics
    overall_coverage = test_response.get("overall_coverage_percentage")
    if overall_coverage is not None:
        print(f"\n🎯 Overall Coverage: {overall_coverage:.1f}%")
        target_met = test_response.get("coverage_meets_target", False)
        print(f"   Target Met: {'✅' if target_met else '❌'}")
    
    # Failed test analysis
    failed_analysis = test_response.get("failed_test_analysis", [])
    if failed_analysis:
        print(f"\n🔍 Failed Test Analysis:")
        for analysis in failed_analysis:
            print(f"   • {analysis}")
    
    # Warnings
    warnings = test_response.get("warnings", [])
    if warnings:
        print(f"\n⚠️ Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    # Execution time
    exec_time = test_response.get("execution_time_seconds")
    if exec_time:
        print(f"\n⏱️ Total Execution Time: {exec_time:.2f} seconds")

def test_agent_directly():
    """Test the agent executor directly without the full workflow"""
    print("\n🔧 Testing TestExecutor Agent Executor directly...")
    
    try:
        # Create agent executor
        agent_executor = create_test_executor_agent_executor()
        
        # Test input (mock data since we can't authenticate easily)
        test_input = {
            "test_class_names": ["AccountContactCounterFlowTest"],
            "org_alias": "test_org",
            "coverage_target": 75.0,
            "timeout_minutes": 5,
            "request_id": str(uuid.uuid4())
        }
        
        print("🧠 Testing agent executor with mock input...")
        print(f"   Input: {test_input}")
        
        # This will likely fail due to missing authentication, but will test the agent setup
        result = agent_executor.invoke(test_input)
        
        print(f"✅ Agent executor response: {result}")
        
    except Exception as e:
        print(f"⚠️ Expected error (no auth): {str(e)}")
        print("   This is expected when testing without proper Salesforce authentication")

def main():
    """Main test function"""
    print("🚀 Starting Independent TestExecutor Agent Test")
    print("=" * 60)
    
    try:
        # Option 1: Test the full workflow with authentication
        print("📝 Testing Option 1: Full workflow with authentication")
        
        # Check if we have the required environment variables
        required_vars = ["ANTHROPIC_API_KEY", "SALESFORCE_CLIENT_ID", "SALESFORCE_USERNAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️ Missing required environment variables: {missing_vars}")
            print("   Skipping full workflow test")
            print("   Please set up your .env file based on environment_template.txt")
        else:
            try:
                # Set up test state
                state = setup_test_state()
                
                # Run authentication first
                auth_state = test_authentication_first(state)
                
                # Run test executor
                result_state = test_executor_agent_execution(auth_state)
                
                # Analyze results
                analyze_test_results(result_state)
                
                print("\n✅ Full workflow test completed successfully!")
                
            except Exception as e:
                print(f"\n❌ Full workflow test failed: {str(e)}")
                print("   This might be due to:")
                print("   1. Salesforce authentication issues")
                print("   2. Test class not deployed in the target org")
                print("   3. Network connectivity issues")
        
        # Option 2: Test agent executor directly (without authentication)
        print("\n" + "=" * 60)
        print("📝 Testing Option 2: Agent executor directly (mock test)")
        test_agent_directly()
        
        print("\n" + "=" * 60)
        print("🏁 Test execution completed!")
        print("\nTo run a full test with real Salesforce data:")
        print("1. Set up your .env file with proper Salesforce credentials")
        print("2. Deploy the AccountContactCounterFlowTest class to your org")
        print("3. Run this script again")
        
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 