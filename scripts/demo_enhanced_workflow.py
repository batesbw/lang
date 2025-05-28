#!/usr/bin/env python3
"""
Demo script for the Enhanced FlowBuilderAgent integrated with the main workflow

This script demonstrates how to use the enhanced FlowBuilderAgent with user stories
in the complete authentication -> flow building -> deployment workflow.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from src.main_orchestrator import run_workflow
from src.schemas.flow_builder_schemas import FlowBuildRequest, UserStory, FlowType
from src.state.agent_workforce_state import AgentWorkforceState

# Load environment variables
load_dotenv()

def demo_enhanced_workflow_with_user_story():
    """
    Demo the enhanced workflow with a user story-driven flow
    """
    print("🚀 ENHANCED FLOW BUILDER AGENT - WORKFLOW DEMO")
    print("="*60)
    
    # Check if we have the required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your Anthropic API key in the .env file.")
        return
    
    # Get org alias from user or use default
    org_alias = input("Enter your Salesforce org alias (or press Enter for 'DEMO'): ").strip()
    if not org_alias:
        org_alias = "DEMO"
    
    print(f"\n🎯 Running enhanced workflow for org: {org_alias}")
    print("This will demonstrate the enhanced FlowBuilderAgent capabilities:")
    print("  • Natural language user story processing")
    print("  • RAG-powered best practices integration")
    print("  • Advanced XML generation")
    print("  • Automated deployment")
    
    # Note: The enhanced agent will be used automatically since we updated the import
    # in main_orchestrator.py to use enhanced_flow_builder_agent
    
    try:
        # Run the workflow
        final_state = run_workflow(org_alias)
        
        # Display enhanced results
        print("\n" + "="*60)
        print("📊 ENHANCED WORKFLOW RESULTS")
        print("="*60)
        
        flow_response = final_state.get("current_flow_build_response")
        if flow_response and flow_response.success:
            print("✅ Enhanced Flow Building Results:")
            print(f"  📋 Flow Name: {flow_response.input_request.flow_api_name}")
            print(f"  📝 Elements Created: {len(flow_response.elements_created)}")
            print(f"  🎯 Best Practices Applied: {len(flow_response.best_practices_applied)}")
            print(f"  💡 Recommendations: {len(flow_response.recommendations)}")
            
            if flow_response.elements_created:
                print("\n  🔧 Generated Elements:")
                for element in flow_response.elements_created[:5]:  # Show first 5
                    print(f"    • {element}")
                if len(flow_response.elements_created) > 5:
                    print(f"    ... and {len(flow_response.elements_created) - 5} more")
            
            if flow_response.best_practices_applied:
                print("\n  🏆 Best Practices Applied:")
                for practice in flow_response.best_practices_applied[:3]:  # Show first 3
                    print(f"    • {practice}")
                if len(flow_response.best_practices_applied) > 3:
                    print(f"    ... and {len(flow_response.best_practices_applied) - 3} more")
            
            if flow_response.recommendations:
                print("\n  💡 Key Recommendations:")
                for rec in flow_response.recommendations[:3]:  # Show first 3
                    print(f"    • {rec}")
                if len(flow_response.recommendations) > 3:
                    print(f"    ... and {len(flow_response.recommendations) - 3} more")
        
        deployment_response = final_state.get("current_deployment_response")
        if deployment_response and deployment_response.success:
            print("\n✅ Enhanced Deployment Results:")
            print(f"  🚀 Deployment ID: {deployment_response.deployment_id}")
            print(f"  📊 Status: {deployment_response.status}")
            print("  🎉 Your enhanced flow has been successfully deployed!")
        
        print("\n" + "="*60)
        print("🎊 ENHANCED WORKFLOW COMPLETED!")
        print("="*60)
        print("\nThe Enhanced FlowBuilderAgent has demonstrated:")
        print("  ✅ Intelligent flow design from simple requirements")
        print("  ✅ Application of Salesforce best practices")
        print("  ✅ Production-ready XML generation")
        print("  ✅ Comprehensive validation and recommendations")
        
    except Exception as e:
        print(f"\n💥 Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

def create_custom_user_story_demo():
    """
    Allow user to create a custom user story for testing
    """
    print("\n🎨 CREATE CUSTOM USER STORY DEMO")
    print("="*50)
    
    print("Let's create a custom user story to test the enhanced agent!")
    print("(Press Enter to skip any field and use defaults)")
    
    # Get user input
    title = input("\nUser Story Title: ").strip()
    if not title:
        title = "Custom Business Process"
    
    description = input("\nUser Story Description: ").strip()
    if not description:
        description = "As a user, I want to automate a business process to improve efficiency"
    
    print("\nAcceptance Criteria (enter one per line, empty line to finish):")
    criteria = []
    while True:
        criterion = input("  • ").strip()
        if not criterion:
            break
        criteria.append(criterion)
    
    if not criteria:
        criteria = [
            "When a record is created or updated",
            "Then perform validation checks",
            "And update related records as needed"
        ]
    
    context = input("\nBusiness Context: ").strip()
    if not context:
        context = "This process needs to be automated to improve efficiency and reduce manual errors"
    
    # Create the user story
    user_story = UserStory(
        title=title,
        description=description,
        acceptance_criteria=criteria,
        business_context=context
    )
    
    print(f"\n✅ Created user story: '{title}'")
    print("This would be processed by the Enhanced FlowBuilderAgent to:")
    print("  1. Parse the natural language requirements")
    print("  2. Consult the knowledge base for best practices")
    print("  3. Design an appropriate flow structure")
    print("  4. Generate production-ready XML")
    print("  5. Provide deployment guidance and recommendations")
    
    return user_story

def main():
    """Main demo function"""
    print("🌟 ENHANCED FLOW BUILDER AGENT DEMO")
    print("="*50)
    
    while True:
        print("\nChoose a demo option:")
        print("1. Run enhanced workflow with default flow")
        print("2. Create custom user story (preview)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_enhanced_workflow_with_user_story()
        elif choice == "2":
            create_custom_user_story_demo()
        elif choice == "3":
            print("\n👋 Thanks for trying the Enhanced FlowBuilderAgent!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 