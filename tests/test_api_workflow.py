#!/usr/bin/env python3
"""
Test script to run the Salesforce Agent Workforce via LangGraph API with user stories.
This demonstrates how to test user stories programmatically via the API.
"""

import requests
import json
import time
from src.schemas.flow_builder_schemas import UserStory

def get_assistant_id():
    """Get the assistant ID for the salesforce_agent_workforce"""
    
    url = "http://localhost:2024/assistants/search"
    response = requests.post(url, json={})
    
    if response.status_code == 200:
        assistants = response.json()
        for assistant in assistants:
            if assistant.get("graph_id") == "salesforce_agent_workforce":
                return assistant.get("assistant_id")
    
    return None

def create_thread():
    """Create a new thread for the workflow"""
    
    url = "http://localhost:2024/threads"
    response = requests.post(url, json={})
    
    if response.status_code == 200:
        thread = response.json()
        return thread.get("thread_id")
    
    return None

def run_workflow_with_user_story(assistant_id, thread_id, org_alias, user_story_data=None):
    """Run the workflow with a user story"""
    
    # Create the initial state
    initial_state = {
        "current_auth_request": {
            "org_alias": org_alias
        },
        "is_authenticated": False,
        "retry_count": 0,
        "messages": []
    }
    
    # Add user story if provided
    if user_story_data:
        initial_state["user_story"] = user_story_data
    
    # Start the run
    url = f"http://localhost:2024/threads/{thread_id}/runs"
    payload = {
        "assistant_id": assistant_id,
        "input": initial_state
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        run_data = response.json()
        return run_data.get("run_id")
    else:
        print(f"Failed to start run: {response.status_code}")
        print(response.text)
        return None

def wait_for_run_completion(thread_id, run_id, timeout=300):
    """Wait for the run to complete and return the final state"""
    
    url = f"http://localhost:2024/threads/{thread_id}/runs/{run_id}"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(url)
        
        if response.status_code == 200:
            run_data = response.json()
            status = run_data.get("status")
            
            print(f"Run status: {status}")
            
            if status in ["success", "error", "timeout", "interrupted"]:
                return run_data
            
            time.sleep(2)  # Wait 2 seconds before checking again
        else:
            print(f"Error checking run status: {response.status_code}")
            break
    
    print("Timeout waiting for run completion")
    return None

def get_thread_state(thread_id):
    """Get the final state of the thread"""
    
    url = f"http://localhost:2024/threads/{thread_id}/state"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting thread state: {response.status_code}")
        return None

def create_sample_user_story():
    """Create a sample user story for testing"""
    
    user_story = UserStory(
        title="API Test Flow",
        description="As a developer, I want to test the agent workforce via API so that I can verify user story processing works correctly",
        acceptance_criteria=[
            "User story is processed by the prepare flow request node",
            "Flow request is created based on user story requirements",
            "Flow XML is generated that addresses the acceptance criteria",
            "Workflow completes successfully"
        ],
        priority="High",
        business_context="Testing the API integration for user story processing",
        affected_objects=["Lead", "User"],
        user_personas=["Developer", "Test User"]
    )
    
    return user_story.model_dump()

def test_workflow_api(org_alias):
    """Test the complete workflow via API"""
    
    print("Testing Salesforce Agent Workforce via API")
    print("=" * 50)
    print()
    
    # Step 1: Get assistant ID
    print("1. Getting assistant ID...")
    assistant_id = get_assistant_id()
    if not assistant_id:
        print("❌ Could not find salesforce_agent_workforce assistant")
        return False
    print(f"✅ Assistant ID: {assistant_id}")
    
    # Step 2: Create thread
    print("\n2. Creating thread...")
    thread_id = create_thread()
    if not thread_id:
        print("❌ Could not create thread")
        return False
    print(f"✅ Thread ID: {thread_id}")
    
    # Step 3: Create user story
    print("\n3. Creating user story...")
    user_story_data = create_sample_user_story()
    print(f"✅ User story: {user_story_data['title']}")
    print(f"   Acceptance criteria: {len(user_story_data['acceptance_criteria'])} items")
    
    # Step 4: Run workflow
    print(f"\n4. Starting workflow for org: {org_alias}")
    run_id = run_workflow_with_user_story(assistant_id, thread_id, org_alias, user_story_data)
    if not run_id:
        print("❌ Could not start workflow run")
        return False
    print(f"✅ Run ID: {run_id}")
    
    # Step 5: Wait for completion
    print("\n5. Waiting for workflow completion...")
    run_result = wait_for_run_completion(thread_id, run_id)
    if not run_result:
        print("❌ Workflow did not complete successfully")
        return False
    
    print(f"✅ Workflow completed with status: {run_result.get('status')}")
    
    # Step 6: Get final state
    print("\n6. Getting final state...")
    final_state = get_thread_state(thread_id)
    if final_state:
        print("✅ Final state retrieved")
        
        # Print summary
        print("\n" + "=" * 50)
        print("WORKFLOW SUMMARY")
        print("=" * 50)
        
        values = final_state.get("values", {})
        
        # Authentication
        if values.get("is_authenticated"):
            print("✅ Authentication: SUCCESS")
        else:
            print("❌ Authentication: FAILED")
        
        # Flow building
        flow_response = values.get("current_flow_build_response")
        if flow_response and flow_response.get("success"):
            print("✅ Flow Building: SUCCESS")
            print(f"   Flow Name: {flow_response.get('input_request', {}).get('flow_api_name', 'Unknown')}")
        else:
            print("❌ Flow Building: FAILED")
        
        # Deployment
        deployment_response = values.get("current_deployment_response")
        if deployment_response and deployment_response.get("success"):
            print("✅ Deployment: SUCCESS")
        else:
            print("❌ Deployment: FAILED")
        
        # User story processing
        if values.get("user_story"):
            print("✅ User Story: PROCESSED")
            print(f"   Title: {values['user_story'].get('title', 'Unknown')}")
        else:
            print("⚠️  User Story: NOT FOUND IN FINAL STATE")
        
        return True
    else:
        print("❌ Could not retrieve final state")
        return False

def test_without_user_story(org_alias):
    """Test the workflow without a user story for comparison"""
    
    print("\nTesting workflow WITHOUT user story (default behavior)")
    print("=" * 50)
    
    assistant_id = get_assistant_id()
    thread_id = create_thread()
    
    if not assistant_id or not thread_id:
        print("❌ Could not set up test")
        return False
    
    # Run without user story
    run_id = run_workflow_with_user_story(assistant_id, thread_id, org_alias, None)
    if not run_id:
        print("❌ Could not start workflow")
        return False
    
    print(f"✅ Started workflow without user story")
    print("   This should create a default test flow")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_api_workflow.py <org_alias>")
        print("Example: python test_api_workflow.py myorg")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    print(f"Testing with Salesforce org: {org_alias}")
    print()
    
    # Test with user story
    success = test_workflow_api(org_alias)
    
    if success:
        print("\n🎉 API test completed successfully!")
        print("\nYou can also test via the web interface:")
        print("1. Open http://localhost:2024 in your browser")
        print("2. Look for a Studio or UI interface")
        print("3. Use the JSON examples from test_user_story_workflow.py")
    else:
        print("\n❌ API test failed")
        print("\nTroubleshooting:")
        print("1. Make sure 'langgraph dev' is running")
        print("2. Check your Salesforce org alias")
        print("3. Verify your JWT authentication is set up correctly") 