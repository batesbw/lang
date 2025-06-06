from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SearchDepth(str, Enum):
    """Search depth options for Tavily searches."""
    BASIC = "basic"
    ADVANCED = "advanced"

class SearchResult(BaseModel):
    """Individual search result from Tavily."""
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    content: str = Field(description="Content/snippet from the search result")
    score: Optional[float] = Field(default=None, description="Relevance score of the result")
    published_date: Optional[str] = Field(default=None, description="Publication date if available")

class WebSearchRequest(BaseModel):
    """Request schema for web search operations."""
    query: str = Field(description="The search query to execute")
    max_results: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)
    search_depth: SearchDepth = Field(default=SearchDepth.BASIC, description="Depth of search to perform")
    include_domains: Optional[List[str]] = Field(default=None, description="List of domains to include in search")
    exclude_domains: Optional[List[str]] = Field(default=None, description="List of domains to exclude from search")
    include_answer: bool = Field(default=True, description="Whether to include an AI-generated answer")
    include_raw_content: bool = Field(default=False, description="Whether to include raw content from pages")
    topic: Optional[str] = Field(default=None, description="Topic context for the search (e.g., 'salesforce', 'programming')")

class WebSearchResponse(BaseModel):
    """Response schema for web search operations."""
    success: bool = Field(description="Whether the search was successful")
    query: str = Field(description="The original search query")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")
    answer: Optional[str] = Field(default=None, description="AI-generated answer based on search results")
    total_results: int = Field(description="Total number of results found")
    search_time_ms: Optional[float] = Field(default=None, description="Search execution time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if search failed")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata from the search")

class WebSearchAgentRequest(BaseModel):
    """Request for the Web Search Agent."""
    search_request: WebSearchRequest = Field(description="The web search request to process")
    context: Optional[str] = Field(default=None, description="Additional context for the search agent")
    agent_instructions: Optional[str] = Field(default=None, description="Specific instructions for the search agent")

class WebSearchAgentResponse(BaseModel):
    """Response from the Web Search Agent."""
    success: bool = Field(description="Whether the agent operation was successful")
    search_response: Optional[WebSearchResponse] = Field(default=None, description="The search response")
    summary: Optional[str] = Field(default=None, description="Agent-generated summary of findings")
    recommendations: Optional[List[str]] = Field(default_factory=list, description="Agent recommendations based on search")
    follow_up_queries: Optional[List[str]] = Field(default_factory=list, description="Suggested follow-up search queries")
    error_message: Optional[str] = Field(default=None, description="Error message if operation failed")
    processing_notes: Optional[str] = Field(default=None, description="Notes about the search processing") 