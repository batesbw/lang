# Web Search Agent

The Web Search Agent provides intelligent web search capabilities to assist other agents in the Salesforce Agent Workforce. It uses Tavily API to perform high-quality web searches and provides AI-enhanced analysis of results.

## Features

- **Intelligent Web Search**: Uses Tavily API for high-quality search results
- **AI-Enhanced Analysis**: Provides summaries and recommendations based on search results
- **Domain Filtering**: Can include or exclude specific domains
- **Context-Aware**: Provides search results tailored to the agent's specific needs
- **Follow-up Suggestions**: Generates relevant follow-up queries
- **Integration Ready**: Designed to work seamlessly with other agents in the workforce

## Setup

### Prerequisites

1. **Tavily API Key**: Sign up at [Tavily](https://tavily.com) and get your API key
2. **Anthropic API Key**: Required for AI analysis and agent functionality

### Environment Variables

Add these to your `.env` file:

```env
TAVILY_API_KEY=your_tavily_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Installation

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

### Direct Usage

```python
from src.agents.web_search_agent import search_web

# Simple search
result = search_web(
    query="Salesforce Flow best practices",
    max_results=5
)

print(f"Found {result.search_response.total_results} results")
print(f"AI Answer: {result.search_response.answer}")
print(f"Agent Summary: {result.summary}")
```

### Advanced Search Options

```python
result = search_web(
    query="Salesforce Marketing Cloud API integration",
    max_results=10,
    search_depth="advanced",
    include_domains=["salesforce.com", "trailhead.salesforce.com"],
    context="Building a Flow integration",
    agent_instructions="Focus on latest API versions and best practices"
)
```

### LangGraph Integration

The agent integrates with the LangGraph workflow system:

```python
from src.agents.web_search_agent import run_web_search_agent
from src.state.agent_workforce_state import AgentWorkforceState

# Create state with search request
state: AgentWorkforceState = {
    "current_web_search_request": {
        "search_request": {
            "query": "Salesforce Flow troubleshooting",
            "max_results": 5
        },
        "context": "Debugging deployment issues"
    }
}

# Run agent
result_state = run_web_search_agent(state)
response = result_state["current_web_search_response"]
```

## Integration Patterns

### 1. Enhanced Flow Building

Flow Builder agents can use web search to:
- Find current API documentation
- Discover best practices
- Get examples of similar implementations
- Verify feature availability

```python
# Example: Flow Builder searching for API info
api_search = search_web(
    query="Salesforce External Service API Flow integration 2024",
    include_domains=["salesforce.com", "developer.salesforce.com"],
    agent_instructions="Focus on current API versions and Flow examples"
)
```

### 2. Troubleshooting Support

When deployment or validation fails:
- Search for specific error messages
- Find solutions from the community
- Get official Salesforce guidance

```python
# Example: Troubleshooting deployment error
error_search = search_web(
    query="Salesforce Flow field integrity exception invalid flow element",
    include_domains=["salesforce.com", "success.salesforce.com", "salesforce.stackexchange.com"],
    agent_instructions="Focus on specific solutions and error resolution"
)
```

### 3. Knowledge Enhancement

Keep agent knowledge current:
- Research new Salesforce features
- Find updated documentation
- Discover community best practices

## Search Parameters

### WebSearchRequest Fields

- **query** (str): The search query to execute
- **max_results** (int): Maximum number of results (1-20, default: 5)
- **search_depth** (str): "basic" or "advanced" (default: "basic")
- **include_domains** (List[str], optional): Domains to include in search
- **exclude_domains** (List[str], optional): Domains to exclude from search
- **include_answer** (bool): Whether to include AI-generated answer (default: True)
- **include_raw_content** (bool): Whether to include raw page content (default: False)
- **topic** (str, optional): Topic context for the search

### WebSearchAgentRequest Fields

- **search_request** (WebSearchRequest): The search parameters
- **context** (str, optional): Additional context for the agent
- **agent_instructions** (str, optional): Specific instructions for the search agent

## Response Structure

### WebSearchResponse

- **success** (bool): Whether the search was successful
- **query** (str): The original search query
- **results** (List[SearchResult]): List of search results
- **answer** (str, optional): AI-generated answer
- **total_results** (int): Total number of results found
- **search_time_ms** (float): Search execution time
- **error_message** (str, optional): Error message if search failed

### WebSearchAgentResponse

- **success** (bool): Whether the agent operation was successful
- **search_response** (WebSearchResponse): The search response
- **summary** (str): Agent-generated summary of findings
- **recommendations** (List[str]): Agent recommendations
- **follow_up_queries** (List[str]): Suggested follow-up searches
- **error_message** (str, optional): Error message if operation failed

## Best Practices

### 1. Query Construction

- Use specific, relevant keywords
- Include context (e.g., "Salesforce", "Flow", "API")
- For troubleshooting, include error message keywords

### 2. Domain Filtering

- For official information: `["salesforce.com", "trailhead.salesforce.com"]`
- For community help: `["salesforce.stackexchange.com", "success.salesforce.com"]`
- For general programming: `["stackoverflow.com", "github.com"]`

### 3. Search Depth

- Use "basic" for quick searches and current information
- Use "advanced" for comprehensive research and complex topics

### 4. Result Analysis

- Prioritize official Salesforce sources for accuracy
- Use community sources for troubleshooting and examples
- Verify information with multiple sources for critical implementations

## Examples

See `examples/web_search_integration_example.py` for comprehensive examples of:
- Direct search usage
- Integration with Flow Builder agents
- Troubleshooting with search
- State-based LangGraph integration

## Testing

Run the agent test harness:

```bash
cd src/agents
python web_search_agent.py
```

Run integration examples:

```bash
python examples/web_search_integration_example.py
```

## Future Enhancements

Planned improvements for the Web Search Agent:

1. **Search History**: Track and learn from previous searches
2. **Result Caching**: Cache frequently accessed results
3. **Smart Routing**: Automatically choose best search parameters based on query type
4. **Multi-Agent Coordination**: Coordinate searches across multiple agents
5. **Custom Search Profiles**: Predefined search configurations for different use cases

## Error Handling

The agent includes comprehensive error handling:

- API key validation
- Network error recovery
- Malformed query handling
- Rate limiting management
- Timeout handling

All errors are logged and returned in the response structure for proper debugging and recovery.

## Performance Considerations

- Search time typically ranges from 1-5 seconds
- Advanced searches may take longer but provide more comprehensive results
- Rate limits apply based on your Tavily plan
- Consider caching results for frequently accessed information

## Support

For issues with the Web Search Agent:

1. Check API key configuration
2. Verify network connectivity
3. Review query construction
4. Check Tavily API status
5. Examine agent logs for detailed error information 