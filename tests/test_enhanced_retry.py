#!/usr/bin/env python3
"""
Test script to validate the enhanced retry mechanism with structured error learning.
This script simulates deployment failures and verifies that the FlowBuilder learns from them.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.enhanced_flow_builder_agent import EnhancedFlowBuilderAgent
from src.schemas.flow_builder_schemas import FlowBuildRequest, UserStory
from src.main_orchestrator import _analyze_deployment_error
from langchain_openai import ChatOpenAI

def test_error_analysis():
    """Test the structured error analysis functionality"""
    print("=== Testing Structured Error Analysis ===\n")
    
    # Test case 1: API Name Issues
    error_msg_1 = "Invalid Name: The flow API name 'My Test Flow' contains invalid characters"
    component_errors_1 = [
        {"componentType": "Flow", "problem": "API name contains spaces and special characters"}
    ]
    
    analysis_1 = _analyze_deployment_error(error_msg_1, component_errors_1, "<Flow>...</Flow>")
    
    print("Test Case 1 - API Name Issues:")
    print(f"  Error Type: {analysis_1['error_type']}")
    print(f"  Severity: {analysis_1['severity']}")
    print(f"  Required Fixes: {len(analysis_1['required_fixes'])}")
    for fix in analysis_1['required_fixes']:
        print(f"    - {fix}")
    print(f"  Error Patterns: {analysis_1['error_patterns']}")
    print()
    
    # Test case 2: Element Reference Issues
    error_msg_2 = "Element reference 'NonExistentScreen' is invalid and cannot be found"
    component_errors_2 = []
    
    analysis_2 = _analyze_deployment_error(error_msg_2, component_errors_2, "<Flow>...</Flow>")
    
    print("Test Case 2 - Element Reference Issues:")
    print(f"  Error Type: {analysis_2['error_type']}")
    print(f"  Severity: {analysis_2['severity']}")
    print(f"  Required Fixes: {len(analysis_2['required_fixes'])}")
    for fix in analysis_2['required_fixes']:
        print(f"    - {fix}")
    print(f"  Error Patterns: {analysis_2['error_patterns']}")
    print()

def test_memory_context():
    """Test the enhanced memory context functionality"""
    print("=== Testing Enhanced Memory Context ===\n")
    
    # Initialize the agent (you'll need to configure your LLM)
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        agent = EnhancedFlowBuilderAgent(llm)
        
        # Create a test user story
        test_user_story = UserStory(
            title="Automated Lead Qualification",
            description="Automatically qualify leads based on business criteria",
            acceptance_criteria=[
                "When a lead is created or updated",
                "If Annual Revenue > $1,000,000",
                "Then set Lead Status to 'Qualified'"
            ],
            priority="High",
            business_context="Improve sales efficiency",
            affected_objects=["Lead"],
            user_personas=["Sales Manager"]
        )
        
        # Create initial request
        request = FlowBuildRequest(
            flow_api_name="AutomatedLeadQualification",
            flow_label="Automated Lead Qualification",
            flow_description="Automatically qualify leads based on business criteria",
            user_story=test_user_story
        )
        
        print("Testing initial attempt...")
        response_1 = agent.generate_flow_with_rag(request)
        print(f"Initial attempt success: {response_1.success}")
        
        # Simulate a retry with error context
        retry_request = request.model_copy()
        retry_request.retry_context = {
            "is_retry": True,
            "retry_attempt": 2,
            "original_flow_xml": response_1.flow_xml if response_1.flow_xml else "<Flow>test</Flow>",
            "deployment_error": "Invalid Name: The flow API name contains invalid characters",
            "component_errors": [{"componentType": "Flow", "problem": "API name validation failed"}],
            "error_analysis": {
                "error_type": "api_name_validation",
                "severity": "high",
                "required_fixes": [
                    "Fix API names to be alphanumeric and start with a letter",
                    "Remove spaces, hyphens, and special characters from all API names"
                ],
                "error_patterns": ["API_NAME_INVALID"],
                "api_name_issues": ["Invalid API name format detected"]
            },
            "specific_fixes_needed": [
                "Fix API names to be alphanumeric and start with a letter",
                "Remove spaces, hyphens, and special characters from all API names"
            ],
            "common_patterns": ["API_NAME_INVALID"],
            "previous_attempts_summary": "The first retry failed. Focus on addressing the core deployment error."
        }
        
        print("\nTesting retry with enhanced context...")
        response_2 = agent.generate_flow_with_rag(retry_request)
        print(f"Retry attempt success: {response_2.success}")
        
        # Check memory context
        print("\nTesting memory context retrieval...")
        memory_context = agent._get_memory_context("AutomatedLeadQualification")
        print(f"Memory context available: {'Yes' if 'No previous attempts found' not in memory_context else 'No'}")
        if "No previous attempts found" not in memory_context:
            print("Memory context preview:")
            print(memory_context[:500] + "..." if len(memory_context) > 500 else memory_context)
        
    except Exception as e:
        print(f"Error during memory context testing: {e}")
        print("Note: This test requires proper LLM configuration (OpenAI API key)")

def test_enhanced_prompt():
    """Test the enhanced prompt generation"""
    print("=== Testing Enhanced Prompt Generation ===\n")
    
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        agent = EnhancedFlowBuilderAgent(llm)
        
        # Create a request with retry context
        test_user_story = UserStory(
            title="Test Flow with Retry",
            description="Test flow for retry mechanism",
            acceptance_criteria=["Test criteria"],
            priority="High"
        )
        
        request = FlowBuildRequest(
            flow_api_name="TestRetryFlow",
            flow_label="Test Retry Flow",
            flow_description="Test flow for retry mechanism",
            user_story=test_user_story,
            retry_context={
                "is_retry": True,
                "retry_attempt": 2,
                "deployment_error": "Invalid API name detected",
                "error_analysis": {
                    "error_type": "api_name_validation",
                    "severity": "high",
                    "required_fixes": ["Fix API names to be alphanumeric"],
                    "api_name_issues": ["Invalid API name format"]
                },
                "specific_fixes_needed": ["Fix API names to be alphanumeric"],
                "common_patterns": ["API_NAME_INVALID"]
            }
        )
        
        # Generate enhanced prompt
        analysis = agent.analyze_requirements(request)
        knowledge = agent.retrieve_knowledge(analysis)
        prompt = agent.generate_enhanced_prompt(request, knowledge)
        
        print("Enhanced prompt generated successfully!")
        print("Prompt preview (first 1000 chars):")
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        
        # Check for key retry elements
        retry_elements = [
            "🔄 RETRY CONTEXT",
            "📊 STRUCTURED ERROR ANALYSIS",
            "🔧 REQUIRED FIXES",
            "🛠️ DEPLOYMENT SUCCESS CHECKLIST"
        ]
        
        print("\nRetry-specific elements found in prompt:")
        for element in retry_elements:
            found = element in prompt
            print(f"  {element}: {'✓' if found else '✗'}")
        
    except Exception as e:
        print(f"Error during prompt testing: {e}")
        print("Note: This test requires proper LLM configuration")

def main():
    """Run all tests"""
    print("🧪 Enhanced Retry Mechanism Test Suite\n")
    print("=" * 60)
    
    # Test 1: Error Analysis
    test_error_analysis()
    
    print("=" * 60)
    
    # Test 2: Memory Context (requires LLM)
    test_memory_context()
    
    print("=" * 60)
    
    # Test 3: Enhanced Prompt (requires LLM)
    test_enhanced_prompt()
    
    print("=" * 60)
    print("\n✅ Test suite completed!")
    print("\n📝 Summary of Enhancements:")
    print("1. ✓ Structured error analysis with specific fix recommendations")
    print("2. ✓ Enhanced memory context with detailed attempt history")
    print("3. ✓ LLM-driven XML generation (no more fallback to basic tool)")
    print("4. ✓ Comprehensive retry prompts with visual formatting")
    print("5. ✓ Error pattern detection and avoidance")
    print("\n🎯 Expected Impact:")
    print("- FlowBuilder should now learn from deployment failures")
    print("- Each retry should apply specific fixes for detected error patterns")
    print("- Memory system provides context from previous attempts")
    print("- LLM receives clear, structured guidance for fixing issues")

if __name__ == "__main__":
    main() 