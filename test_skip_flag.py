#!/usr/bin/env python3
"""
Test script demonstrating the skip_test_design_deployment flag functionality.

This script shows examples of how to:
1. Run the full TDD workflow (with tests)
2. Skip test design/deployment and go directly to flow building

Usage:
    python test_skip_flag.py
"""

import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def create_example_input_with_tests():
    """Example input for full TDD workflow (tests included)"""
    return {
        "current_auth_request": {
            "org_alias": "E2E_TEST_ORG"
        },
        "user_story": {
            "title": "Account Contact Counter",
            "description": "As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account",
            "acceptance_criteria": [
                "Count of contacts should update immediately when creating and/or deleting contacts",
                "Count should be saved the Count_of_Contacts__c field on the Account",
                "If there are no contacts associated with an account, the count should be 0"
            ],
            "priority": "High",
            "business_context": "Staff just need a quick way to view the size of their accounts",
            "affected_objects": ["Account", "Contact"],
            "user_personas": ["Sales Manager", "Sales Representative", "Lead Routing Admin"]
        },
        "is_authenticated": False,
        "retry_count": 0,
        "messages": [],
        "skip_test_design_deployment": False  # Full TDD workflow
    }

def create_example_input_skip_tests():
    """Example input for skipping test design/deployment"""
    return {
        "current_auth_request": {
            "org_alias": "E2E_TEST_ORG"
        },
        "user_story": {
            "title": "Account Contact Counter",
            "description": "As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account",
            "acceptance_criteria": [
                "Count of contacts should update immediately when creating and/or deleting contacts",
                "Count should be saved the Count_of_Contacts__c field on the Account",
                "If there are no contacts associated with an account, the count should be 0"
            ],
            "priority": "High",
            "business_context": "Staff just need a quick way to view the size of their accounts",
            "affected_objects": ["Account", "Contact"],
            "user_personas": ["Sales Manager", "Sales Representative", "Lead Routing Admin"]
        },
        "is_authenticated": False,
        "retry_count": 0,
        "messages": [],
        "skip_test_design_deployment": True  # Skip tests, go directly to flow building
    }

def print_workflow_comparison():
    """Print a comparison of the two workflow paths"""
    print("🔄 WORKFLOW PATH COMPARISON")
    print("=" * 50)
    print()
    
    print("📋 FULL TDD WORKFLOW (skip_test_design_deployment: false)")
    print("   1. Authentication")
    print("   2. TestDesigner → Design test scenarios and Apex test classes")
    print("   3. Test Deployment → Deploy Apex test classes to org")
    print("   4. Flow Builder → Build flow to make tests pass")
    print("   5. Flow Deployment → Deploy the flow")
    print()
    
    print("⚡ DIRECT FLOW WORKFLOW (skip_test_design_deployment: true)")
    print("   1. Authentication")
    print("   2. Flow Builder → Build flow directly from user story")
    print("   3. Flow Deployment → Deploy the flow")
    print()
    
    print("💡 Use Cases:")
    print("   Full TDD: Production implementations, complex business logic")
    print("   Direct:   Prototyping, simple flows, quick demos")
    print()

def main():
    """Main function to demonstrate the skip flag examples"""
    print("🧪 SKIP TEST DESIGN/DEPLOYMENT FLAG DEMO")
    print("=" * 45)
    print()
    
    print_workflow_comparison()
    
    print("📝 EXAMPLE INPUTS FOR LANGGRAPH STUDIO:")
    print("-" * 40)
    print()
    
    print("1️⃣  FULL TDD WORKFLOW INPUT:")
    print("```json")
    import json
    full_input = create_example_input_with_tests()
    print(json.dumps(full_input, indent=2))
    print("```")
    print()
    
    print("2️⃣  SKIP TESTS WORKFLOW INPUT:")
    print("```json")
    skip_input = create_example_input_skip_tests()
    print(json.dumps(skip_input, indent=2))
    print("```")
    print()
    
    print("🔧 HOW TO USE IN LANGGRAPH STUDIO:")
    print("   1. Copy one of the JSON inputs above")
    print("   2. Paste it into the LangGraph Studio UI input field")
    print("   3. Click 'Run' to start the workflow")
    print("   4. The workflow will follow the appropriate path based on the flag")
    print()
    
    print("✨ Key difference: The 'skip_test_design_deployment' boolean flag")
    print("   • false = Full TDD workflow with test design and deployment")
    print("   • true  = Skip directly to flow building after authentication")

if __name__ == "__main__":
    main() 