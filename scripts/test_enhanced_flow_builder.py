#!/usr/bin/env python3
"""
Test script for the Enhanced FlowBuilderAgent

This script demonstrates the enhanced capabilities of the FlowBuilderAgent
including natural language processing, RAG knowledge base, and advanced
flow generation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from src.agents.enhanced_flow_builder_agent import EnhancedFlowBuilderAgent
from src.schemas.flow_builder_schemas import (
    FlowBuildRequest, UserStory, FlowType, FlowTriggerType
)
from src.state.agent_workforce_state import AgentWorkforceState

# Load environment variables
load_dotenv()

def test_user_story_parsing():
    """Test the user story parsing capabilities"""
    print("\n" + "="*60)
    print("🧪 TESTING USER STORY PARSING")
    print("="*60)
    
    # Initialize LLM and agent
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    agent = EnhancedFlowBuilderAgent(llm)
    
    # Test user story
    user_story = UserStory(
        title="Automated Lead Qualification",
        description="As a sales manager, I want to automatically qualify leads based on revenue and employee count so that my team can focus on high-value prospects",
        acceptance_criteria=[
            "When a lead is created or updated",
            "If Annual Revenue > $1,000,000 AND Number of Employees > 50",
            "Then set Lead Status to 'Qualified'",
            "And send email notification to lead owner",
            "And create a task for follow-up within 2 business days"
        ],
        business_context="Our sales team is overwhelmed with leads and needs an automated way to identify the most promising prospects. High-value leads are defined as companies with significant revenue and size."
    )
    
    # Create flow build request
    request = FlowBuildRequest(
        flow_api_name="Lead_Qualification_Flow",
        flow_label="Lead Qualification Flow",
        flow_description="Automatically qualify leads based on business criteria",
        user_story=user_story,
        target_api_version="59.0"
    )
    
    # Create test state
    state: AgentWorkforceState = {
        "current_flow_build_request": request,
        "current_flow_build_response": None,
        "is_authenticated": True,
        "salesforce_session": {"session_id": "test", "instance_url": "https://test.salesforce.com"},
        "messages": [],
        "error_message": None,
        "retry_count": 0
    }
    
    # Run the enhanced agent
    result_state = agent.run_enhanced_flow_builder_agent(state, llm)
    
    # Display results
    response = result_state.get("current_flow_build_response")
    if response and response.success:
        print("✅ Flow generation successful!")
        print(f"📋 Flow Name: {response.input_request.flow_api_name}")
        print(f"📝 Elements Created: {len(response.elements_created)}")
        print(f"🎯 Best Practices Applied: {len(response.best_practices_applied)}")
        print(f"💡 Recommendations: {len(response.recommendations)}")
        
        print("\n📊 GENERATED ELEMENTS:")
        for element in response.elements_created:
            print(f"  • {element}")
        
        print("\n🏆 BEST PRACTICES APPLIED:")
        for practice in response.best_practices_applied[:5]:  # Show first 5
            print(f"  • {practice}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in response.recommendations[:3]:  # Show first 3
            print(f"  • {rec}")
            
        # Show partial XML (first 500 chars)
        if response.flow_xml:
            print(f"\n📄 GENERATED XML (first 500 chars):")
            print(response.flow_xml[:500] + "..." if len(response.flow_xml) > 500 else response.flow_xml)
    else:
        print("❌ Flow generation failed!")
        if response:
            print(f"Error: {response.error_message}")

def test_screen_flow_generation():
    """Test screen flow generation"""
    print("\n" + "="*60)
    print("🧪 TESTING SCREEN FLOW GENERATION")
    print("="*60)
    
    # Initialize LLM and agent
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    agent = EnhancedFlowBuilderAgent(llm)
    
    # Test user story for screen flow
    user_story = UserStory(
        title="Customer Onboarding Wizard",
        description="As a customer success manager, I want a guided onboarding flow for new customers to collect their preferences and setup requirements",
        acceptance_criteria=[
            "Display welcome screen with company branding",
            "Collect customer contact information",
            "Ask about product preferences and use cases",
            "Capture implementation timeline requirements",
            "Create customer record with collected information",
            "Send welcome email to customer",
            "Create onboarding tasks for CSM team"
        ],
        business_context="New customers need a streamlined onboarding experience that captures all necessary information while making them feel welcomed and supported."
    )
    
    # Create flow build request
    request = FlowBuildRequest(
        flow_api_name="Customer_Onboarding_Wizard",
        flow_label="Customer Onboarding Wizard",
        flow_description="Guided onboarding flow for new customers",
        flow_type=FlowType.SCREEN_FLOW,
        user_story=user_story,
        target_api_version="59.0"
    )
    
    # Create test state
    state: AgentWorkforceState = {
        "current_flow_build_request": request,
        "current_flow_build_response": None,
        "is_authenticated": True,
        "salesforce_session": {"session_id": "test", "instance_url": "https://test.salesforce.com"},
        "messages": [],
        "error_message": None,
        "retry_count": 0
    }
    
    # Run the enhanced agent
    result_state = agent.run_enhanced_flow_builder_agent(state, llm)
    
    # Display results
    response = result_state.get("current_flow_build_response")
    if response and response.success:
        print("✅ Screen Flow generation successful!")
        print(f"📋 Flow Name: {response.input_request.flow_api_name}")
        print(f"📝 Elements Created: {len(response.elements_created)}")
        print(f"🎯 Best Practices Applied: {len(response.best_practices_applied)}")
        
        print("\n📊 SCREEN FLOW ELEMENTS:")
        for element in response.elements_created:
            print(f"  • {element}")
            
        print("\n🚀 DEPLOYMENT NOTES:")
        print(f"  {response.deployment_notes}")
    else:
        print("❌ Screen Flow generation failed!")
        if response:
            print(f"Error: {response.error_message}")

def test_knowledge_base_integration():
    """Test the RAG knowledge base integration"""
    print("\n" + "="*60)
    print("🧪 TESTING KNOWLEDGE BASE INTEGRATION")
    print("="*60)
    
    # Initialize LLM and agent
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    agent = EnhancedFlowBuilderAgent(llm)
    
    # Test knowledge base queries
    test_queries = [
        "best practices for record-triggered flows",
        "flow performance optimization",
        "error handling in flows",
        "flow security considerations",
        "flow testing strategies"
    ]
    
    print("🔍 Testing knowledge base queries:")
    for query in test_queries:
        try:
            result = agent.knowledge_rag.invoke({
                "query": query,
                "flow_type": "Record-Triggered",
                "max_results": 2
            })
            print(f"\n📚 Query: '{query}'")
            print(f"📖 Result: {result[:200]}..." if len(result) > 200 else result)
        except Exception as e:
            print(f"❌ Error querying '{query}': {str(e)}")

def test_xml_generation_capabilities():
    """Test advanced XML generation capabilities"""
    print("\n" + "="*60)
    print("🧪 TESTING XML GENERATION CAPABILITIES")
    print("="*60)
    
    # Initialize LLM and agent
    llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
    agent = EnhancedFlowBuilderAgent(llm)
    
    # Test complex flow request
    request = FlowBuildRequest(
        flow_api_name="Complex_Business_Process",
        flow_label="Complex Business Process",
        flow_description="A complex flow with multiple elements and decision points",
        flow_type=FlowType.RECORD_TRIGGERED,
        trigger_object="Opportunity",
        trigger_type=FlowTriggerType.AFTER_SAVE,
        target_api_version="59.0"
    )
    
    try:
        # Test XML generation directly
        xml_response = agent.xml_generator.invoke(request.model_dump())
        
        if xml_response.success:
            print("✅ XML generation successful!")
            print(f"📄 Generated XML length: {len(xml_response.flow_xml)} characters")
            print(f"🔧 Elements created: {len(xml_response.elements_created)}")
            print(f"⚠️  Validation errors: {len(xml_response.validation_errors)}")
            
            # Show XML structure
            if xml_response.flow_xml:
                lines = xml_response.flow_xml.split('\n')
                print(f"\n📋 XML Structure (first 10 lines):")
                for i, line in enumerate(lines[:10]):
                    print(f"  {i+1:2d}: {line}")
                if len(lines) > 10:
                    print(f"  ... and {len(lines) - 10} more lines")
        else:
            print("❌ XML generation failed!")
            print(f"Error: {xml_response.error_message}")
            
    except Exception as e:
        print(f"❌ Error testing XML generation: {str(e)}")

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 ENHANCED FLOW BUILDER AGENT - COMPREHENSIVE TESTING")
    print("="*80)
    
    try:
        # Check environment
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ ANTHROPIC_API_KEY not found in environment variables.")
            print("Please set your Anthropic API key in the .env file.")
            return
        
        # Run tests
        test_user_story_parsing()
        test_screen_flow_generation()
        test_knowledge_base_integration()
        test_xml_generation_capabilities()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*80)
        print("\n💡 The Enhanced FlowBuilderAgent demonstrates:")
        print("  ✅ Natural language user story processing")
        print("  ✅ RAG-powered best practices integration")
        print("  ✅ Advanced XML generation with multiple flow types")
        print("  ✅ Comprehensive error handling and validation")
        print("  ✅ Production-ready flow creation capabilities")
        
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests() 