#!/usr/bin/env python3
"""
Test script to debug LLM XML generation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.enhanced_flow_builder_agent import EnhancedFlowBuilderAgent
from src.schemas.flow_builder_schemas import FlowBuildRequest, UserStory
from langchain_anthropic import ChatAnthropic

def test_llm_xml_generation():
    """Test what the LLM actually returns"""
    print("=== Testing LLM XML Generation ===\n")
    
    try:
        # Initialize with Claude (since that's what the error shows)
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
        agent = EnhancedFlowBuilderAgent(llm)
        
        # Create a simple test request
        test_user_story = UserStory(
            title="Simple Welcome Flow",
            description="Create a simple welcome screen flow",
            acceptance_criteria=[
                "Display a welcome message",
                "Allow user to finish the flow"
            ],
            priority="High"
        )
        
        request = FlowBuildRequest(
            flow_api_name="SimpleWelcomeFlow",
            flow_label="Simple Welcome Flow",
            flow_description="A simple welcome screen flow for testing",
            user_story=test_user_story
        )
        
        print("Testing LLM XML generation...")
        print(f"Request: {request.flow_api_name}")
        
        # Generate the flow
        response = agent.generate_flow_with_rag(request)
        
        print(f"\nResult:")
        print(f"Success: {response.success}")
        if response.success:
            print(f"XML generated: {'Yes' if response.flow_xml else 'No'}")
            if response.flow_xml:
                print(f"XML length: {len(response.flow_xml)} characters")
                print(f"XML preview:\n{response.flow_xml[:500]}...")
        else:
            print(f"Error: {response.error_message}")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_llm_xml_generation() 