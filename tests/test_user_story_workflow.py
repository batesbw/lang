#!/usr/bin/env python3
"""
Test script for demonstrating user story and acceptance criteria workflow
through LangGraph Studio interface.

This script shows how to structure the input for testing user stories
via the LangGraph Studio web interface.
"""

import json
from src.schemas.flow_builder_schemas import UserStory

def create_sample_user_stories():
    """
    Creates sample user stories that can be used for testing.
    These can be copied and pasted into the LangGraph Studio interface.
    """
    
    # Sample User Story 1: Lead Assignment Automation
    lead_assignment_story = UserStory(
        title="Automate Lead Assignment",
        description="As a sales manager, I want leads to be automatically assigned to the right sales rep based on territory and workload so that response time is improved and leads are distributed fairly",
        acceptance_criteria=[
            "Leads are assigned within 5 minutes of creation",
            "Assignment follows territory rules based on lead location",
            "Workload balancing considers current open opportunities per rep",
            "High-priority leads are assigned to senior reps",
            "Email notifications are sent to assigned rep and manager",
            "Assignment history is tracked for reporting"
        ],
        priority="High",
        business_context="Current manual assignment process takes 2-4 hours and leads to uneven distribution. Sales team has 15 reps across 3 territories.",
        affected_objects=["Lead", "User", "Territory", "Opportunity"],
        user_personas=["Sales Manager", "Sales Representative", "Lead Routing Admin"]
    )
    
    # Sample User Story 2: Case Escalation
    case_escalation_story = UserStory(
        title="Automatic Case Escalation",
        description="As a customer service manager, I want high-priority cases to be automatically escalated to senior agents when SLA thresholds are approaching so that we maintain our service level commitments",
        acceptance_criteria=[
            "Cases are escalated 2 hours before SLA breach",
            "Escalation considers case priority and customer tier",
            "Senior agents receive immediate notification",
            "Case ownership is transferred automatically",
            "Customer is notified of escalation",
            "Escalation metrics are tracked for reporting"
        ],
        priority="Critical",
        business_context="Current SLA breach rate is 15%. Manual escalation process is inconsistent and reactive.",
        affected_objects=["Case", "User", "Account", "Contact"],
        user_personas=["Customer Service Manager", "Senior Support Agent", "Support Agent"]
    )
    
    # Sample User Story 3: Opportunity Approval Workflow
    opportunity_approval_story = UserStory(
        title="Opportunity Approval Workflow",
        description="As a sales director, I want large opportunities to require approval before they can be marked as closed-won so that we maintain deal quality and pricing standards",
        acceptance_criteria=[
            "Opportunities over $50K require manager approval",
            "Opportunities over $100K require director approval",
            "Approval requests include discount analysis",
            "Approvers have 48 hours to respond",
            "Auto-approval for standard pricing",
            "Rejection reasons are captured and tracked"
        ],
        priority="Medium",
        business_context="Need to implement deal governance while maintaining sales velocity. Current process is email-based and slow.",
        affected_objects=["Opportunity", "User", "Account", "Product2"],
        user_personas=["Sales Representative", "Sales Manager", "Sales Director"]
    )
    
    return {
        "lead_assignment": lead_assignment_story,
        "case_escalation": case_escalation_story,
        "opportunity_approval": opportunity_approval_story
    }

def print_studio_input_examples():
    """
    Prints formatted JSON that can be copied into LangGraph Studio interface.
    """
    stories = create_sample_user_stories()
    
    print("=" * 80)
    print("LANGGRAPH STUDIO INPUT EXAMPLES")
    print("=" * 80)
    print()
    print("Copy and paste any of these JSON objects into the LangGraph Studio")
    print("interface as the initial state to test user story workflows.")
    print()
    
    for story_name, story in stories.items():
        print(f"--- {story_name.upper().replace('_', ' ')} USER STORY ---")
        print()
        
        # Create the state object that should be input to LangGraph Studio
        studio_input = {
            "current_auth_request": {
                "org_alias": "your-org-alias-here"  # User needs to replace this
            },
            "user_story": story.model_dump(),
            "is_authenticated": False,
            "retry_count": 0,
            "messages": []
        }
        
        print("LangGraph Studio Input:")
        print(json.dumps(studio_input, indent=2))
        print()
        print("Story Summary:")
        print(f"  Title: {story.title}")
        print(f"  Priority: {story.priority}")
        print(f"  Acceptance Criteria: {len(story.acceptance_criteria)} items")
        print(f"  Affected Objects: {', '.join(story.affected_objects)}")
        print()
        print("-" * 60)
        print()

def print_simple_test_input():
    """
    Prints a simple test input without user story for comparison.
    """
    print("--- SIMPLE TEST (NO USER STORY) ---")
    print()
    
    simple_input = {
        "current_auth_request": {
            "org_alias": "your-org-alias-here"  # User needs to replace this
        },
        "is_authenticated": False,
        "retry_count": 0,
        "messages": []
    }
    
    print("LangGraph Studio Input (will use default test flow):")
    print(json.dumps(simple_input, indent=2))
    print()

def print_instructions():
    """
    Prints instructions for using LangGraph Studio with user stories.
    """
    print("=" * 80)
    print("HOW TO TEST USER STORIES IN LANGGRAPH STUDIO")
    print("=" * 80)
    print()
    print("1. Make sure LangGraph Studio is running:")
    print("   langgraph dev")
    print()
    print("2. Open your browser to: http://localhost:8123")
    print()
    print("3. Select the 'salesforce_agent_workforce' graph")
    print()
    print("4. Click 'New Thread' to start a new conversation")
    print()
    print("5. In the input field, paste one of the JSON objects from above")
    print("   (Make sure to replace 'your-org-alias-here' with your actual Salesforce org alias)")
    print()
    print("6. Click 'Submit' to start the workflow")
    print()
    print("7. Watch the workflow execute through each node:")
    print("   - Authentication: Connects to your Salesforce org")
    print("   - Prepare Flow Request: Creates flow request from user story")
    print("   - Flow Builder: Generates Salesforce Flow XML")
    print("   - Prepare Deployment: Prepares for deployment")
    print("   - Deployment: Deploys the flow to Salesforce")
    print()
    print("8. Check the logs and state at each step to see how the user story")
    print("   is processed and converted into a Salesforce Flow")
    print()
    print("=" * 80)

if __name__ == "__main__":
    print_instructions()
    print()
    print_studio_input_examples()
    print()
    print_simple_test_input() 