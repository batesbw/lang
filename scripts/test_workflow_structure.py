#!/usr/bin/env python3
"""
LangGraph Workflow Validation Suite

This script validates the structure and configuration of the Salesforce Agent Workforce
LangGraph workflow without requiring actual execution or external API calls.
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.main_orchestrator import create_workflow
from src.state.agent_workforce_state import AgentWorkforceState
from src.schemas.auth_schemas import AuthenticationRequest


def test_workflow_structure():
    """Test that the workflow graph is properly constructed."""
    print("🧪 Testing LangGraph Workflow Structure")
    print("=" * 45)
    
    try:
        # Create the workflow
        print("📊 Creating workflow graph...")
        workflow = create_workflow()
        
        # Compile the workflow
        print("⚙️  Compiling workflow...")
        app = workflow.compile()
        
        print("✅ Workflow compiled successfully!")
        
        # Test the graph structure
        print("\n📋 Workflow Structure:")
        print("-" * 25)
        
        # Get the graph representation
        graph = app.get_graph()
        
        # Print nodes
        print("🔗 Nodes:")
        nodes = graph.nodes
        for node_id in nodes:
            print(f"   - {node_id}")
        
        # Print edges
        print("\n➡️  Edges:")
        edges = graph.edges
        for edge in edges:
            print(f"   - {edge}")
        
        # Validate expected nodes exist
        expected_nodes = [
            "authentication", 
            "prepare_flow_request", 
            "flow_builder", 
            "prepare_deployment_request", 
            "deployment"
        ]
        
        missing_nodes = []
        for expected_node in expected_nodes:
            if expected_node not in nodes:
                missing_nodes.append(expected_node)
        
        if missing_nodes:
            print(f"\n❌ Missing expected nodes: {missing_nodes}")
            return False
        
        print(f"\n✅ All expected nodes found: {expected_nodes}")
        print("\n✅ Workflow structure validation: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow structure validation: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state_schema():
    """Test that the state schema is properly defined."""
    print("\n🧪 Testing State Schema")
    print("=" * 25)
    
    try:
        # Create a test state
        test_state: AgentWorkforceState = {
            "current_auth_request": AuthenticationRequest(org_alias="TEST"),
            "current_auth_response": None,
            "is_authenticated": False,
            "salesforce_session": None,
            "current_flow_build_request": None,
            "current_flow_build_response": None,
            "current_deployment_request": None,
            "current_deployment_response": None,
            "messages": [],
            "error_message": None,
            "retry_count": 0
        }
        
        print("✅ State schema validation: PASSED")
        print(f"   State keys: {list(test_state.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ State schema validation: FAILED")
        print(f"   Error: {e}")
        return False


def test_imports():
    """Test that all required imports are working."""
    print("\n🧪 Testing Imports")
    print("=" * 20)
    
    try:
        # Test agent imports
        from src.agents.authentication_agent import run_authentication_agent
        from src.agents.flow_builder_agent import run_flow_builder_agent
        from src.agents.deployment_agent import run_deployment_agent
        print("✅ Agent imports: OK")
        
        # Test schema imports
        from src.schemas.auth_schemas import AuthenticationRequest, AuthenticationResponse
        from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
        from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse
        print("✅ Schema imports: OK")
        
        # Test LangGraph imports
        from langgraph.graph import StateGraph, END, START
        print("✅ LangGraph imports: OK")
        
        # Test LangChain imports
        from langchain_anthropic import ChatAnthropic
        print("✅ LangChain imports: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import validation: FAILED")
        print(f"   Missing import: {e}")
        return False
    except Exception as e:
        print(f"❌ Import validation: FAILED")
        print(f"   Error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 LangGraph Workflow Validation Suite")
    print("=" * 40)
    
    tests = [
        ("Import Validation", test_imports),
        ("State Schema", test_state_schema),
        ("Workflow Structure", test_workflow_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"   ❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Workflow is ready for execution.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 