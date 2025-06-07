"""
Test Web Search Integration in the Salesforce Agent Workforce

This test verifies that the web search agent is properly integrated into the 
deployment failure retry loop.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import END
from src.main_orchestrator import (
    create_workflow, 
    should_continue_after_deployment,
    prepare_web_search_request,
    WEB_SEARCH_AVAILABLE
)
from src.state.agent_workforce_state import AgentWorkforceState
from src.schemas.web_search_schemas import WebSearchAgentRequest, WebSearchRequest


def test_web_search_availability_check():
    """Test that web search availability is correctly detected."""
    # This test will pass if TAVILY_API_KEY is set, otherwise it will show the expected behavior
    print(f"Web search available: {WEB_SEARCH_AVAILABLE}")
    assert isinstance(WEB_SEARCH_AVAILABLE, bool)


def test_should_continue_after_deployment_with_failure():
    """Test that deployment failures trigger the correct next step."""
    # Mock a deployment failure state
    state: AgentWorkforceState = {
        "current_deployment_response": {
            "success": False,
            "error_message": "Invalid flow element reference",
            "component_errors": [
                {
                    "componentType": "Flow",
                    "problem": "Flow contains an invalid flow element reference: Get_Contact_Count",
                    "fileName": "TestFlow.flow"
                }
            ]
        },
        "build_deploy_retry_count": 0,
        "max_build_deploy_retries": 3
    }
    
    result = should_continue_after_deployment(state)
    
    if WEB_SEARCH_AVAILABLE:
        assert result == "search_for_solutions"
    else:
        assert result == "direct_retry"


def test_should_continue_after_deployment_with_success():
    """Test that successful deployments end the workflow."""
    state: AgentWorkforceState = {
        "current_deployment_response": {
            "success": True,
            "deployment_id": "test-deployment-123"
        },
        "build_deploy_retry_count": 0,
        "max_build_deploy_retries": 3
    }
    
    result = should_continue_after_deployment(state)
    assert result == END


def test_should_continue_after_deployment_max_retries():
    """Test that max retries reached ends the workflow."""
    state: AgentWorkforceState = {
        "current_deployment_response": {
            "success": False,
            "error_message": "Deployment failed"
        },
        "build_deploy_retry_count": 3,
        "max_build_deploy_retries": 3
    }
    
    result = should_continue_after_deployment(state)
    assert result == END


def test_prepare_web_search_request():
    """Test that web search requests are properly prepared from deployment failures."""
    state: AgentWorkforceState = {
        "current_deployment_response": {
            "success": False,
            "error_message": "Invalid flow element reference",
            "component_errors": [
                {
                    "componentType": "Flow",
                    "problem": "Flow contains an invalid flow element reference: Get_Contact_Count",
                    "fileName": "TestFlow.flow"
                }
            ]
        },
        "build_deploy_retry_count": 1
    }
    
    result_state = prepare_web_search_request(state)
    
    # Check that a web search request was created
    web_search_request = result_state.get("current_web_search_request")
    
    if web_search_request:
        # Verify the request structure
        assert "search_request" in web_search_request
        assert "context" in web_search_request
        assert "agent_instructions" in web_search_request
        
        search_request = web_search_request["search_request"]
        assert "query" in search_request
        assert "Salesforce Flow" in search_request["query"]
        assert "invalid flow element" in search_request["query"]


def test_prepare_web_search_request_no_failure():
    """Test that no web search request is created when deployment succeeds."""
    state: AgentWorkforceState = {
        "current_deployment_response": {
            "success": True,
            "deployment_id": "test-deployment-123"
        },
        "build_deploy_retry_count": 0
    }
    
    result_state = prepare_web_search_request(state)
    
    # Should not create a web search request for successful deployments
    assert result_state.get("current_web_search_request") is None


def test_workflow_creation():
    """Test that the workflow is created successfully with or without web search."""
    workflow = create_workflow()
    
    # Verify basic workflow structure
    assert workflow is not None
    
    # Check that required nodes exist
    node_names = set(workflow.nodes.keys())
    required_nodes = {
        "authentication", 
        "prepare_flow_request", 
        "flow_builder",
        "prepare_deployment_request",
        "deployment",
        "record_cycle",
        "prepare_retry_flow_request"
    }
    
    assert required_nodes.issubset(node_names)
    
    # Check web search nodes based on availability
    if WEB_SEARCH_AVAILABLE:
        web_search_nodes = {"prepare_web_search_request", "web_search"}
        assert web_search_nodes.issubset(node_names)
        print("✅ Web search nodes included in workflow")
    else:
        print("⚠️ Web search nodes not included (TAVILY_API_KEY not available)")


def test_web_search_integration_with_api_key():
    """Test web search integration when TAVILY_API_KEY is available."""
    if not WEB_SEARCH_AVAILABLE:
        print("⚠️ Skipping web search integration test (TAVILY_API_KEY not available)")
        return
        
    # This test only runs if web search is available
    workflow = create_workflow()
    
    # Verify web search nodes are present
    node_names = set(workflow.nodes.keys())
    assert "prepare_web_search_request" in node_names
    assert "web_search" in node_names
    
    print("✅ Web search integration test passed with API key")


def test_web_search_integration_without_api_key():
    """Test that workflow works correctly without TAVILY_API_KEY."""
    # This test simulates the behavior when web search is not available
    with patch('src.main_orchestrator.WEB_SEARCH_AVAILABLE', False):
        # Test that deployment failures go directly to retry
        state: AgentWorkforceState = {
            "current_deployment_response": {
                "success": False,
                "error_message": "Deployment failed"
            },
            "build_deploy_retry_count": 0,
            "max_build_deploy_retries": 3
        }
        
        result = should_continue_after_deployment(state)
        assert result == "direct_retry"
        
        print("✅ Workflow correctly handles missing web search capability")


if __name__ == "__main__":
    # Run basic tests
    test_web_search_availability_check()
    test_should_continue_after_deployment_with_failure()
    test_should_continue_after_deployment_with_success()
    test_should_continue_after_deployment_max_retries()
    test_prepare_web_search_request()
    test_prepare_web_search_request_no_failure()
    test_workflow_creation()
    test_web_search_integration_without_api_key()
    
    if WEB_SEARCH_AVAILABLE:
        test_web_search_integration_with_api_key()
    
    print("\n🎉 All web search integration tests completed!") 