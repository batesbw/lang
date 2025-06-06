import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("tavily-python is required. Install it with: pip install tavily-python")

from src.schemas.web_search_schemas import (
    WebSearchRequest, 
    WebSearchResponse, 
    SearchResult, 
    SearchDepth
)

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

class WebSearchToolInput(BaseModel):
    """Input schema for the web search tool."""
    query: str = Field(description="The search query to execute")
    max_results: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)
    search_depth: str = Field(default="basic", description="Search depth: 'basic' or 'advanced'")
    include_domains: Optional[List[str]] = Field(default=None, description="List of domains to include")
    exclude_domains: Optional[List[str]] = Field(default=None, description="List of domains to exclude")
    include_answer: bool = Field(default=True, description="Whether to include AI-generated answer")
    include_raw_content: bool = Field(default=False, description="Whether to include raw content")
    topic: Optional[str] = Field(default=None, description="Topic context for the search")

class WebSearchTool(BaseTool):
    """Tool for performing web searches using Tavily API."""
    
    name: str = "web_search_tool"
    description: str = """
    Performs web searches using Tavily API to find relevant information on the internet.
    Use this tool when you need to:
    - Find current information about topics
    - Research solutions to technical problems
    - Get up-to-date documentation or examples
    - Verify facts or find additional context
    
    The tool returns search results with titles, URLs, content snippets, and optionally an AI-generated answer.
    """
    
    args_schema = WebSearchToolInput
    
    def _get_client(self):
        """Get Tavily client with proper API key handling."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        return TavilyClient(api_key=api_key)
    
    def _run(self, **kwargs) -> WebSearchResponse:
        """Execute the web search using Tavily."""
        try:
            # Parse input
            search_input = WebSearchToolInput(**kwargs)
            
            # Convert to WebSearchRequest
            search_request = WebSearchRequest(
                query=search_input.query,
                max_results=search_input.max_results,
                search_depth=SearchDepth(search_input.search_depth),
                include_domains=search_input.include_domains,
                exclude_domains=search_input.exclude_domains,
                include_answer=search_input.include_answer,
                include_raw_content=search_input.include_raw_content,
                topic=search_input.topic
            )
            
            return self._perform_search(search_request)
            
        except Exception as e:
            return WebSearchResponse(
                success=False,
                query=kwargs.get("query", ""),
                results=[],
                total_results=0,
                error_message=f"Web search tool error: {str(e)}"
            )
    
    def _perform_search(self, request: WebSearchRequest) -> WebSearchResponse:
        """Perform the actual search using Tavily client."""
        start_time = time.time()
        
        try:
            # Get client
            client = self._get_client()
            
            # Prepare Tavily search parameters
            search_params = {
                "query": request.query,
                "search_depth": request.search_depth.value,
                "max_results": request.max_results,
                "include_answer": request.include_answer,
                "include_raw_content": request.include_raw_content,
            }
            
            # Add domain filters if provided
            if request.include_domains:
                search_params["include_domains"] = request.include_domains
            if request.exclude_domains:
                search_params["exclude_domains"] = request.exclude_domains
            
            # Execute the search
            raw_results = client.search(**search_params)
            
            # Calculate search time
            search_time_ms = (time.time() - start_time) * 1000
            
            # Parse results
            search_results = []
            if "results" in raw_results:
                for result in raw_results["results"]:
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("url", ""),
                        content=result.get("content", ""),
                        score=result.get("score"),
                        published_date=result.get("published_date")
                    )
                    search_results.append(search_result)
            
            # Extract answer if available
            answer = raw_results.get("answer") if request.include_answer else None
            
            # Prepare metadata
            metadata = {
                "raw_response_keys": list(raw_results.keys()),
                "search_depth": request.search_depth.value,
                "topic": request.topic
            }
            
            return WebSearchResponse(
                success=True,
                query=request.query,
                results=search_results,
                answer=answer,
                total_results=len(search_results),
                search_time_ms=search_time_ms,
                metadata=metadata
            )
            
        except Exception as e:
            search_time_ms = (time.time() - start_time) * 1000
            return WebSearchResponse(
                success=False,
                query=request.query,
                results=[],
                total_results=0,
                search_time_ms=search_time_ms,
                error_message=f"Tavily search error: {str(e)}"
            )

# Convenience function for direct usage
def perform_web_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_answer: bool = True,
    include_raw_content: bool = False,
    topic: Optional[str] = None
) -> WebSearchResponse:
    """
    Convenience function to perform web search directly.
    
    Args:
        query: Search query
        max_results: Maximum number of results (1-20)
        search_depth: "basic" or "advanced"
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
        include_answer: Whether to include AI-generated answer
        include_raw_content: Whether to include raw content
        topic: Topic context for the search
    
    Returns:
        WebSearchResponse object
    """
    tool = WebSearchTool()
    return tool._run(
        query=query,
        max_results=max_results,
        search_depth=search_depth,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        topic=topic
    ) 