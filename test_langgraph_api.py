#!/usr/bin/env python3
"""
Simple test script to verify LangGraph API is working and can accept user story inputs.
"""

import requests
import json
from src.schemas.flow_builder_schemas import UserStory

def test_langgraph_api():
    """Test the LangGraph API endpoints"""
    
    base_url = "http://localhost:2024"
    
    print("Testing LangGraph API...")
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Check if API is responding
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ LangGraph API is responding")
        else:
            print(f"❌ API responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to LangGraph API: {e}")
        return False
    
    # Test 2: List available graphs
    try:
        response = requests.get(f"{base_url}/assistants", timeout=5)
        if response.status_code == 200:
            assistants = response.json()
            print(f"✅ Found {len(assistants)} assistants/graphs")
            
            # Look for our graph
            our_graph = None
            for assistant in assistants:
                if assistant.get("graph_id") == "salesforce_agent_workforce":
                    our_graph = assistant
                    break
            
            if our_graph:
                print("✅ Found 'salesforce_agent_workforce' graph")
                print(f"   Graph ID: {our_graph.get('graph_id')}")
                print(f"   Assistant ID: {our_graph.get('assistant_id')}")
            else:
                print("❌ 'salesforce_agent_workforce' graph not found")
                print("Available graphs:")
                for assistant in assistants:
                    print(f"   - {assistant.get('graph_id', 'Unknown')}")
                return False
                
        else:
            print(f"❌ Could not list assistants: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing assistants: {e}")
        return False
    
    print()
    print("🎉 LangGraph API is ready for user story testing!")
    print()
    print("Next steps:")
    print("1. Open your browser to: http://localhost:2024")
    print("2. Look for a Studio or UI interface")
    print("3. Use the JSON examples from test_user_story_workflow.py")
    print()
    
    return True

def create_simple_test_payload():
    """Create a simple test payload for API testing"""
    
    # Create a simple user story
    user_story = UserStory(
        title="Simple Test Flow",
        description="As a test user, I want to create a simple flow so that I can verify the system works",
        acceptance_criteria=[
            "Flow is created successfully",
            "Flow can be deployed to Salesforce",
            "Flow appears in Salesforce Flow list"
        ],
        priority="Medium",
        business_context="Testing the agent workforce system",
        affected_objects=["Lead"],
        user_personas=["Test User"]
    )
    
    # Create the full payload
    payload = {
        "current_auth_request": {
            "org_alias": "your-org-alias-here"  # User needs to replace this
        },
        "user_story": user_story.model_dump(),
        "is_authenticated": False,
        "retry_count": 0,
        "messages": []
    }
    
    return payload

def print_test_payload():
    """Print a test payload for manual testing"""
    
    payload = create_simple_test_payload()
    
    print("=" * 60)
    print("SIMPLE TEST PAYLOAD FOR MANUAL TESTING")
    print("=" * 60)
    print()
    print("Copy this JSON and paste it into the LangGraph Studio interface:")
    print()
    print(json.dumps(payload, indent=2))
    print()
    print("Remember to replace 'your-org-alias-here' with your actual Salesforce org alias!")
    print()

if __name__ == "__main__":
    print("LangGraph API Test")
    print("=" * 50)
    print()
    
    # Test the API
    api_working = test_langgraph_api()
    
    if api_working:
        print()
        print_test_payload()
    else:
        print()
        print("❌ API test failed. Make sure 'langgraph dev' is running.")
        print()
        print("To start LangGraph dev:")
        print("  langgraph dev")
        print()
        print("Then run this test again.") 