#!/usr/bin/env python3
"""
Example demonstrating how other agents can integrate with the Web Search Agent.

This example shows:
1. How to call the Web Search Agent directly
2. How to use web search results to enhance other agent capabilities
3. Integration patterns for the multi-agent workflow
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.agents.web_search_agent import search_web
from src.schemas.web_search_schemas import WebSearchRequest, WebSearchAgentRequest, SearchDepth
from src.state.agent_workforce_state import AgentWorkforceState

def example_direct_search():
    """Example of directly calling the web search agent."""
    print("=== Direct Web Search Example ===")
    
    # Simple search
    result = search_web(
        query="Salesforce Flow best practices",
        max_results=5,
        search_depth="basic",
        context="Looking for Flow development best practices for a multi-agent system",
        agent_instructions="Focus on official Salesforce documentation and recent best practices"
    )
    
    print(f"Search Success: {result.success}")
    if result.success and result.search_response:
        print(f"Found {result.search_response.total_results} results")
        
        if result.search_response.answer:
            print(f"\nAI Answer:\n{result.search_response.answer}")
        
        print(f"\nAgent Summary:\n{result.summary}")
        
        print(f"\nTop 3 Results:")
        for i, res in enumerate(result.search_response.results[:3], 1):
            print(f"  {i}. {res.title}")
            print(f"     URL: {res.url}")
            print(f"     Snippet: {res.content[:150]}...")
            print()
        
        if result.recommendations:
            print(f"Recommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")

def example_enhanced_flow_builder_with_search():
    """Example showing how a Flow Builder Agent could use web search for enhanced capabilities."""
    print("\n=== Enhanced Flow Builder with Web Search Example ===")
    
    # Simulate a scenario where Flow Builder needs current information
    flow_requirement = "Create a Flow that integrates with the latest Salesforce Marketing Cloud APIs"
    
    print(f"Flow Requirement: {flow_requirement}")
    print("Flow Builder Agent would search for current information...")
    
    # Search for current API information
    api_search = search_web(
        query="Salesforce Marketing Cloud API latest version integration Flow",
        max_results=5,
        search_depth="advanced",
        include_domains=["salesforce.com", "trailhead.salesforce.com", "developer.salesforce.com"],
        context="Flow Builder Agent needs current API information",
        agent_instructions="Focus on API versions, integration patterns, and Flow-specific examples"
    )
    
    if api_search.success:
        print(f"\n✅ Found {api_search.search_response.total_results} API resources")
        
        # Extract key insights for flow building
        print("Key insights for Flow development:")
        if api_search.search_response.answer:
            print(f"- API Overview: {api_search.search_response.answer[:200]}...")
        
        # Use search results to inform flow design
        print("- Relevant documentation sources:")
        for result in api_search.search_response.results[:2]:
            print(f"  * {result.title}: {result.url}")
        
        print("\nFlow Builder Agent could now use this information to:")
        print("1. Use the correct API version in the Flow")
        print("2. Follow current best practices")
        print("3. Include proper error handling based on latest docs")
        print("4. Ensure compliance with current Salesforce guidelines")

def example_troubleshooting_with_search():
    """Example showing how web search can help with troubleshooting deployment issues."""
    print("\n=== Troubleshooting with Web Search Example ===")
    
    # Simulate a deployment error (from the log data in the conversation)
    error_message = "field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element Get_Contact_Count.)"
    
    print(f"Deployment Error: {error_message}")
    print("Searching for solutions...")
    
    # Search for solutions to this specific error
    troubleshoot_search = search_web(
        query="Salesforce Flow field integrity exception invalid flow element formula expression",
        max_results=7,
        search_depth="advanced",
        include_domains=["salesforce.com", "trailhead.salesforce.com", "success.salesforce.com", "salesforce.stackexchange.com"],
        context="Troubleshooting Flow deployment error",
        agent_instructions="Focus on specific solutions for formula expression errors and flow element validation"
    )
    
    if troubleshoot_search.success:
        print(f"\n✅ Found {troubleshoot_search.search_response.total_results} troubleshooting resources")
        
        if troubleshoot_search.search_response.answer:
            print(f"\nSolution Overview:\n{troubleshoot_search.search_response.answer}")
        
        print(f"\nAgent Analysis:\n{troubleshoot_search.summary}")
        
        print("\nRecommended Actions:")
        for rec in troubleshoot_search.recommendations:
            print(f"  - {rec}")
        
        print("\nRelevant Resources:")
        for i, result in enumerate(troubleshoot_search.search_response.results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     URL: {result.url}")
            print(f"     Solution hint: {result.content[:100]}...")
            print()

def example_state_based_integration():
    """Example showing how web search integrates with the LangGraph state system."""
    print("\n=== State-Based Integration Example ===")
    
    # Create a mock state as if it came from the workflow
    mock_state: AgentWorkforceState = {
        "current_web_search_request": {
            "search_request": {
                "query": "Salesforce Lightning Flow Record Update best practices",
                "max_results": 5,
                "search_depth": "basic",
                "include_answer": True,
                "include_raw_content": False,
                "topic": "salesforce"
            },
            "context": "Flow Builder Agent needs guidance on record update patterns",
            "agent_instructions": "Focus on performance and best practices"
        }
    }
    
    print("Mock state created with web search request")
    print(f"Query: {mock_state['current_web_search_request']['search_request']['query']}")
    
    # Import and run the actual agent function
    from src.agents.web_search_agent import run_web_search_agent
    
    # This would be called by LangGraph in the actual workflow
    result_state = run_web_search_agent(mock_state)
    
    print(f"\nSearch completed: {result_state.get('current_web_search_response', {}).get('success', False)}")
    
    response = result_state.get('current_web_search_response', {})
    if response.get('success'):
        search_resp = response.get('search_response', {})
        print(f"Found {search_resp.get('total_results', 0)} results")
        print(f"Processing time: {search_resp.get('search_time_ms', 0):.1f}ms")
        
        print(f"\nAgent Summary:\n{response.get('summary', 'No summary available')}")

def main():
    """Run all examples."""
    print("Web Search Agent Integration Examples")
    print("=" * 50)
    
    try:
        # Check if API key is set
        if not os.getenv("TAVILY_API_KEY"):
            print("⚠️  TAVILY_API_KEY not found in environment variables.")
            print("Please set it in your .env file to run these examples.")
            return
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  ANTHROPIC_API_KEY not found in environment variables.")
            print("Please set it in your .env file to run these examples.")
            return
        
        example_direct_search()
        example_enhanced_flow_builder_with_search()
        example_troubleshooting_with_search()
        example_state_based_integration()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 