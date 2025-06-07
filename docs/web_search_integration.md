# Web Search Integration for Deployment Failures

## Overview

The Salesforce Agent Workforce now includes intelligent web search integration that automatically searches for solutions when Flow deployments fail. This feature enhances the retry mechanism by incorporating real-world solutions and best practices found online.

## How It Works

### 1. Deployment Failure Detection
When a Salesforce Flow deployment fails, the system:
- Captures the specific error message and component errors
- Analyzes the error patterns to categorize the failure type
- Determines if a retry should be attempted

### 2. Automatic Web Search (if TAVILY_API_KEY is available)
If web search is enabled, the system:
- Prepares a targeted search query based on the specific error
- Searches for Salesforce-specific solutions and documentation
- Prioritizes official Salesforce resources (salesforce.com, trailhead.salesforce.com, developer.salesforce.com)
- Extracts key insights and recommendations from search results

### 3. Enhanced Retry with Search Insights
The retry mechanism incorporates:
- Original error analysis
- Web search findings and recommendations
- Structured guidance for the Flow Builder Agent
- Specific fixes based on both pattern analysis and web research

## Configuration

### Environment Variables

```bash
# Required for basic functionality
ANTHROPIC_API_KEY=your_anthropic_api_key
LANGSMITH_API_KEY=your_langsmith_api_key  # Optional

# Required for web search integration
TAVILY_API_KEY=your_tavily_api_key  # Optional - enables web search
```

### Web Search Availability

The system automatically detects if web search is available:

- ✅ **With TAVILY_API_KEY**: Full web search integration enabled
- ⚠️ **Without TAVILY_API_KEY**: Falls back to pattern-based retry without web search

## Workflow Changes

### With Web Search Enabled

```
Deployment Failure → Record Cycle → Search for Solutions → Web Search → Enhanced Retry → Flow Builder
```

### Without Web Search

```
Deployment Failure → Record Cycle → Direct Retry → Flow Builder
```

## Search Query Generation

The system creates intelligent search queries based on error patterns:

| Error Type | Example Search Query |
|------------|---------------------|
| Invalid Flow Element | "Salesforce Flow invalid flow element reference error" |
| Field Integrity Exception | "Salesforce Flow field integrity exception deployment error" |
| Formula Expression Error | "Salesforce Flow invalid formula expression error" |
| API Name Issues | "Salesforce Flow invalid API name error" |
| Duplicate Elements | "Salesforce Flow duplicate element error" |

## Search Results Processing

### Information Extracted
- **Search Summary**: AI-generated summary of findings
- **Recommendations**: Specific actionable recommendations
- **Key Findings**: Top 3 most relevant search results with snippets
- **Follow-up Queries**: Suggested additional searches

### Integration with Flow Builder
Search insights are integrated into the retry context:
```python
retry_context = {
    "error_analysis": {...},
    "web_search_insights": {
        "search_summary": "...",
        "recommendations": [...],
        "key_findings": [...],
        "search_results_count": 8
    }
}
```

## Benefits

### 1. **Real-World Solutions**
- Access to community solutions and best practices
- Official Salesforce documentation and troubleshooting guides
- Current and up-to-date information

### 2. **Improved Success Rate**
- Enhanced retry attempts with external knowledge
- Specific guidance for complex deployment issues
- Reduced manual intervention required

### 3. **Learning and Adaptation**
- System learns from successful web search patterns
- Builds knowledge base of common solutions
- Improves over time with usage

## Example Usage

### Deployment Failure Scenario
```
❌ Deployment failed (attempt #1)
📋 DEPLOYMENT FAILURE DETAILS:
   Main Error: Invalid flow element reference
   🔍 Specific Component Problems:
     1. [Flow] Flow contains an invalid flow element reference: Get_Contact_Count

🔍 Will search for solutions to this deployment error
```

### Web Search Process
```
=== PREPARING WEB SEARCH REQUEST ===
Prepared web search for query: 'Salesforce Flow invalid flow element reference error'

=== WEB SEARCH NODE ===
🔍 Incorporating web search results into retry strategy
   📊 Search Results: 8 results found
   🎯 Recommendations: 3 recommendations
   💡 Adding web search recommendations to fix strategy:
      1. Remove or fix references to invalid flow elements
      2. Ensure all element references point to actually defined elements
      3. Validate formula expressions for invalid element references
```

### Enhanced Retry
```
🔧 Enhanced failure analysis completed:
   📊 Error Classification:
      Primary error type: invalid_flow_element_reference
      Severity level: high
   🛠️ Required Fixes Identified: 8
      How fixes were identified: Based on error pattern analysis, Salesforce Flow best practices, and web search insights
```

## Testing

Run the integration tests to verify functionality:

```bash
python3 tests/test_web_search_integration.py
```

The tests verify:
- Web search availability detection
- Proper workflow routing based on API key availability
- Search request preparation from deployment failures
- Integration of search results into retry context

## Troubleshooting

### Common Issues

1. **Web Search Not Working**
   - Verify TAVILY_API_KEY is set in environment
   - Check internet connectivity
   - Ensure Tavily API quota is available

2. **Search Results Not Helpful**
   - System automatically generates follow-up queries
   - Error analysis provides fallback guidance
   - Manual intervention may be required for complex issues

3. **Performance Impact**
   - Web search adds ~2-5 seconds per retry attempt
   - Results are cached within the same workflow execution
   - Can be disabled by removing TAVILY_API_KEY

## Future Enhancements

- **Search Result Caching**: Persistent cache for common error patterns
- **Custom Search Domains**: Configurable domain preferences
- **Search Quality Scoring**: Automatic evaluation of search result relevance
- **Learning from Success**: Track which search insights lead to successful deployments 