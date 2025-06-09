# Core LangChain and LLM imports
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Typing and Pydantic models
from typing import List, Dict, Optional, Any

# Project-specific imports
from src.tools.web_search_tool import WebSearchTool
from src.schemas.web_search_schemas import (
    WebSearchRequest, 
    WebSearchResponse, 
    WebSearchAgentRequest, 
    WebSearchAgentResponse
)
from src.state.agent_workforce_state import AgentWorkforceState
from src.config import get_llm

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Note: TAVILY_API_KEY is checked when tools are actually used

# Get LLM instance for web search agent
LLM = get_llm(
    agent_name="WEB_SEARCH",
    temperature=0.1, 
    max_tokens=4096
)

def get_web_search_tools():
    """Get web search tools with proper error handling."""
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY not found in environment variables.")
    return [WebSearchTool()]

WEB_SEARCH_AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """
    You are a specialized Web Search Agent that helps other agents and users find relevant information on the internet using Tavily search.
    
    Your responsibilities:
    1. Execute web searches based on the provided query and parameters
    2. Analyze search results to extract the most relevant information
    3. Provide clear summaries of findings
    4. Suggest follow-up queries when appropriate
    5. Make recommendations based on search results
    
    Guidelines:
    - Use the web_search_tool to perform searches
    - Focus on finding accurate, current, and relevant information
    - Provide concise but comprehensive summaries
    - Include URLs of relevant sources in your response
    - When searching for technical topics, prioritize official documentation and authoritative sources
    - For Salesforce-related queries, prioritize Salesforce official documentation, Trailhead, and developer resources
    
    You should respond with:
    - A summary of what you found
    - Key insights from the search results
    - Relevant URLs for further reading
    - Recommendations for follow-up actions if applicable
    """),
    ("human", """
    Please perform a web search based on this request:
    
    Query: {query}
    Max Results: {max_results}
    Search Depth: {search_depth}
    Topic Context: {topic}
    Additional Instructions: {agent_instructions}
    
    {context}
    """),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def create_web_search_agent_executor() -> AgentExecutor:
    """
    Creates the LangChain agent executor for the WebSearchAgent.
    """
    tools = get_web_search_tools()
    agent = create_tool_calling_agent(LLM, tools, WEB_SEARCH_AGENT_PROMPT_TEMPLATE)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3  # Prevent infinite loops
    )
    return agent_executor

def run_web_search_agent(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Executes the web search agent and updates the graph state based on the outcome.
    Expects 'current_web_search_request' to be set in the input state.
    """
    print("--- Running Web Search Agent ---")
    
    # Debug logging
    print(f"DEBUG: Received state keys: {list(state.keys())}")
    
    web_search_request_dict = state.get("current_web_search_request")
    print(f"DEBUG: web_search_request_dict = {web_search_request_dict}")
    
    if not web_search_request_dict:
        print("Web Search Agent: No web search request provided in current_web_search_request.")
        updated_state = state.copy()
        response = WebSearchAgentResponse(
            success=False,
            error_message="Web Search Agent Error: No web search request provided."
        )
        updated_state["current_web_search_response"] = response.model_dump()
        return updated_state
    
    try:
        # Convert dict back to Pydantic model
        print(f"DEBUG: Attempting to create WebSearchAgentRequest from: {web_search_request_dict}")
        agent_request = WebSearchAgentRequest(**web_search_request_dict)
        search_request = agent_request.search_request
        print(f"DEBUG: Successfully created WebSearchAgentRequest, query = {search_request.query}")
        
        # Create agent executor
        agent_executor = create_web_search_agent_executor()
        
        # Prepare input for the agent
        agent_input = {
            "query": search_request.query,
            "max_results": search_request.max_results,
            "search_depth": search_request.search_depth.value,
            "topic": search_request.topic or "general",
            "agent_instructions": agent_request.agent_instructions or "No specific instructions provided.",
            "context": agent_request.context or "No additional context provided."
        }
        
        # Execute the agent
        print(f"Executing web search for query: '{search_request.query}'")
        agent_result = agent_executor.invoke(agent_input)
        
        # Extract the agent's response
        agent_output = agent_result.get("output", "")
        
        # Handle case where output might be a list of message parts
        if isinstance(agent_output, list):
            # Extract text from message parts
            text_parts = []
            for part in agent_output:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            agent_output = "\n".join(text_parts) if text_parts else str(agent_output)
        elif not isinstance(agent_output, str):
            agent_output = str(agent_output)
        
        # Also perform the direct search to get structured results
        web_search_tool = WebSearchTool()
        search_response = web_search_tool._run(
            query=search_request.query,
            max_results=search_request.max_results,
            search_depth=search_request.search_depth.value,
            include_domains=search_request.include_domains,
            exclude_domains=search_request.exclude_domains,
            include_answer=search_request.include_answer,
            include_raw_content=search_request.include_raw_content,
            topic=search_request.topic
        )
        
        # Generate follow-up queries based on the results
        follow_up_queries = _generate_follow_up_queries(search_request.query, search_response)
        
        # Generate recommendations
        recommendations = _generate_recommendations(search_response)
        
        # Create agent response
        agent_response = WebSearchAgentResponse(
            success=True,
            search_response=search_response,
            summary=agent_output,
            recommendations=recommendations,
            follow_up_queries=follow_up_queries,
            processing_notes=f"Processed search query '{search_request.query}' with {len(search_response.results)} results"
        )
        
        updated_state = state.copy()
        updated_state["current_web_search_response"] = agent_response.model_dump()
        
        # Clear the request after processing
        updated_state["current_web_search_request"] = None
        
        print(f"Web Search Agent: Successfully processed search for '{search_request.query}' with {len(search_response.results)} results")
        
        return updated_state
        
    except Exception as e:
        print(f"Web Search Agent: Error processing search: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        updated_state = state.copy()
        response = WebSearchAgentResponse(
            success=False,
            error_message=f"Web Search Agent Processing Error: {str(e)}"
        )
        updated_state["current_web_search_response"] = response.model_dump()
        updated_state["current_web_search_request"] = None
        return updated_state

def _generate_follow_up_queries(original_query: str, search_response: WebSearchResponse) -> List[str]:
    """Generate follow-up search queries based on the results."""
    follow_ups = []
    
    # If few results, suggest broader terms
    if search_response.total_results < 3:
        words = original_query.split()
        if len(words) > 1:
            follow_ups.append(" ".join(words[:-1]))  # Remove last word for broader search
    
    # If many results, suggest more specific terms
    elif search_response.total_results >= 5:
        follow_ups.append(f"{original_query} tutorial")
        follow_ups.append(f"{original_query} best practices")
        follow_ups.append(f"{original_query} examples")
    
    # Add related searches based on content
    if search_response.results:
        first_result = search_response.results[0]
        if "salesforce" in first_result.content.lower():
            follow_ups.append(f"{original_query} salesforce documentation")
        if "api" in first_result.content.lower():
            follow_ups.append(f"{original_query} api reference")
    
    return follow_ups[:3]  # Limit to 3 follow-up queries

def _generate_recommendations(search_response: WebSearchResponse) -> List[str]:
    """Generate recommendations based on search results."""
    recommendations = []
    
    if not search_response.success:
        recommendations.append("Try refining your search query or checking your internet connection")
        return recommendations
    
    if search_response.total_results == 0:
        recommendations.append("No results found - try using different keywords or broader terms")
        return recommendations
    
    # Analyze result quality
    official_sources = []
    tutorial_sources = []
    
    for result in search_response.results:
        url_lower = result.url.lower()
        title_lower = result.title.lower()
        content_lower = result.content.lower()
        
        # Check for official sources
        if any(domain in url_lower for domain in ['salesforce.com', 'trailhead.salesforce.com', 'developer.salesforce.com']):
            official_sources.append(result)
        elif any(domain in url_lower for domain in ['docs.python.org', 'github.com', 'stackoverflow.com']):
            official_sources.append(result)
        
        # Check for tutorials
        if any(term in title_lower or term in content_lower for term in ['tutorial', 'guide', 'how to', 'step by step']):
            tutorial_sources.append(result)
    
    if official_sources:
        recommendations.append(f"Found {len(official_sources)} official documentation sources - prioritize these for accuracy")
    
    if tutorial_sources:
        recommendations.append(f"Found {len(tutorial_sources)} tutorial resources for hands-on learning")
    
    if search_response.answer:
        recommendations.append("AI-generated answer provided - verify with official sources for critical implementations")
    
    # Add specific recommendations based on content
    if any("deprecated" in result.content.lower() for result in search_response.results):
        recommendations.append("Some results mention deprecated features - ensure you're using current versions")
    
    return recommendations

# Direct function for standalone usage
def search_web(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    context: Optional[str] = None,
    agent_instructions: Optional[str] = None
) -> WebSearchAgentResponse:
    """
    Standalone function to perform web search with agent analysis.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        search_depth: "basic" or "advanced"
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
        context: Additional context for the search
        agent_instructions: Specific instructions for the agent
    
    Returns:
        WebSearchAgentResponse object
    """
    from src.schemas.web_search_schemas import SearchDepth
    
    # Create request
    search_request = WebSearchRequest(
        query=query,
        max_results=max_results,
        search_depth=SearchDepth(search_depth),
        include_domains=include_domains,
        exclude_domains=exclude_domains
    )
    
    agent_request = WebSearchAgentRequest(
        search_request=search_request,
        context=context,
        agent_instructions=agent_instructions
    )
    
    # Create mock state
    mock_state: AgentWorkforceState = {
        "current_web_search_request": agent_request.model_dump()
    }
    
    # Run agent
    result_state = run_web_search_agent(mock_state)
    
    # Extract response
    response_dict = result_state.get("current_web_search_response", {})
    return WebSearchAgentResponse(**response_dict)

if __name__ == "__main__":
    # Test harness for the Web Search Agent
    print("--- Web Search Agent Test Harness ---")
    
    # Check API keys
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  TAVILY_API_KEY not found in environment variables.")
        print("Please set it in your .env file to run this test.")
        exit(1)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set it in your .env file to run this test.")
        exit(1)
    
    test_query = input("Enter a search query to test: ").strip()
    if not test_query:
        print("No query provided. Exiting test.")
        exit()
    
    print(f"Performing web search for: '{test_query}'")
    
    try:
        result = search_web(
            query=test_query,
            max_results=5,
            context="Test search from Web Search Agent"
        )
        
        print("\n--- Test Result ---")
        print(f"Success: {result.success}")
        
        if result.success and result.search_response:
            print(f"Found {result.search_response.total_results} results")
            print(f"Search time: {result.search_response.search_time_ms:.1f}ms")
            
            if result.search_response.answer:
                print(f"\nAI Answer: {result.search_response.answer}")
            
            print(f"\nAgent Summary: {result.summary}")
            
            if result.recommendations:
                print(f"\nRecommendations:")
                for i, rec in enumerate(result.recommendations, 1):
                    print(f"  {i}. {rec}")
            
            if result.follow_up_queries:
                print(f"\nSuggested follow-up queries:")
                for i, query in enumerate(result.follow_up_queries, 1):
                    print(f"  {i}. {query}")
            
            print(f"\nTop Results:")
            for i, res in enumerate(result.search_response.results[:3], 1):
                print(f"  {i}. {res.title}")
                print(f"     URL: {res.url}")
                print(f"     Content: {res.content[:100]}...")
                print()
        else:
            print(f"Search failed: {result.error_message}")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 