#!/usr/bin/env python3
"""
Test script for the new Test-Driven Development (TDD) workflow.

This script demonstrates the enhanced TDD approach where:
1. TestDesigner creates test scenarios first
2. Test classes are deployed
3. Flow is built to make those tests pass
4. Flow is deployed
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from src.schemas.flow_builder_schemas import UserStory
from src.main_orchestrator import run_workflow
from src.state.agent_workforce_state import AgentWorkforceState

# Load environment variables
load_dotenv()

def create_test_user_story() -> UserStory:
    """
    Create a test user story for the TDD demonstration.
    """
    return UserStory(
        title="Automated Account Contact Counter",
        description="As a sales manager, I want to automatically count and display the number of contacts for each account so that I can quickly assess account engagement",
        acceptance_criteria=[
            "When an Account record is viewed",
            "Then display the total number of related Contact records",
            "And update the count whenever contacts are added or removed",
            "And ensure the count is always accurate and up-to-date"
        ],
        priority="High",
        business_context="Sales teams need quick visibility into account engagement metrics. Contact count is a key indicator of account relationship depth.",
        affected_objects=["Account", "Contact"],
        user_personas=["Sales Manager", "Account Executive", "Sales Operations"]
    )

def demonstrate_tdd_workflow():
    """
    Demonstrate the Test-Driven Development workflow.
    """
    print("🧪 SALESFORCE AGENT WORKFORCE - TDD APPROACH DEMONSTRATION")
    print("=" * 70)
    print()
    print("This demonstration shows the new Test-Driven Development approach:")
    print("1. 🧪 TestDesigner analyzes requirements and creates test scenarios")
    print("2. 🚀 Test classes are deployed to Salesforce org")
    print("3. 🏗️  Flow Builder creates Flow to make tests pass")
    print("4. 📦 Flow is deployed to complete the TDD cycle")
    print()
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your Anthropic API key in the .env file.")
        return False
    
    # Get org alias
    org_alias = input("Enter your Salesforce org alias (e.g., 'MYSANDBOX'): ").strip()
    if not org_alias:
        print("❌ Org alias is required.")
        return False
    
    print(f"\n🎯 Target Org: {org_alias}")
    
    # Create user story for the test
    user_story = create_test_user_story()
    print(f"\n📋 Test User Story: {user_story.title}")
    print(f"Description: {user_story.description}")
    print(f"Acceptance Criteria: {len(user_story.acceptance_criteria)} criteria")
    
    # Initialize state with user story
    print(f"\n🚀 Starting TDD workflow...")
    
    try:
        # Set up initial state with user story
        os.environ["USER_STORY_TITLE"] = user_story.title
        os.environ["USER_STORY_DESCRIPTION"] = user_story.description
        os.environ["USER_STORY_CRITERIA"] = " | ".join(user_story.acceptance_criteria)
        os.environ["USER_STORY_PRIORITY"] = user_story.priority
        os.environ["USER_STORY_CONTEXT"] = user_story.business_context or ""
        
        # Run the TDD workflow
        final_state = run_workflow(org_alias, project_name="tdd-demo")
        
        # Analysis results
        print("\n" + "=" * 70)
        print("🔍 TDD WORKFLOW ANALYSIS")
        print("=" * 70)
        
        test_designer_success = final_state.get("current_test_designer_response", {}).get("success", False)
        test_deployment_success = final_state.get("current_test_deployment_response", {}).get("success", False)
        flow_build_success = final_state.get("current_flow_build_response", {}).get("success", False)
        flow_deployment_success = final_state.get("current_deployment_response", {}).get("success", False)
        
        print(f"✅ TestDesigner: {'SUCCESS' if test_designer_success else 'FAILED'}")
        print(f"✅ Test Deployment: {'SUCCESS' if test_deployment_success else 'FAILED'}")
        print(f"✅ Flow Building: {'SUCCESS' if flow_build_success else 'FAILED'}")
        print(f"✅ Flow Deployment: {'SUCCESS' if flow_deployment_success else 'FAILED'}")
        
        if test_designer_success and test_deployment_success:
            print(f"\n🧪 TDD PHASE 1 COMPLETE: Tests are deployed!")
            
            if flow_build_success:
                print(f"🏗️  TDD PHASE 2 COMPLETE: Flow built with test context!")
                
                # Check if TDD context was used
                flow_request = final_state.get("current_flow_build_request", {})
                if flow_request.get("tdd_context"):
                    print("   📋 Flow was built using deployed test scenarios as guidance")
                    test_scenarios = flow_request["tdd_context"].get("test_scenarios", [])
                    apex_test_classes = flow_request["tdd_context"].get("apex_test_classes", [])
                    print(f"   📊 Test Scenarios Used: {len(test_scenarios)}")
                    print(f"   🧪 Test Classes Used: {len(apex_test_classes)}")
                
                if flow_deployment_success:
                    print(f"🎊 TDD CYCLE COMPLETE!")
                    print(f"   Both tests and Flow are deployed and ready for validation.")
                    print(f"   Next step: Run the deployed Apex tests to verify Flow behavior.")
        
        return test_deployment_success and flow_deployment_success
        
    except Exception as e:
        print(f"\n💥 TDD workflow failed: {str(e)}")
        return False

def main():
    """
    Main function for the TDD demonstration.
    """
    success = demonstrate_tdd_workflow()
    
    if success:
        print(f"\n🎉 TDD DEMONSTRATION SUCCESSFUL!")
        print(f"The Test-Driven Development approach has been demonstrated.")
        print(f"Tests were created first, then the Flow was built to satisfy them.")
    else:
        print(f"\n❌ TDD demonstration encountered issues.")
        print(f"Check the output above for details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 