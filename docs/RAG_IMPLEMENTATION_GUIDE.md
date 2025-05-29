# RAG Implementation Guide for Salesforce Flow Builder Agent

## Overview

This guide covers the implementation of RAG (Retrieval-Augmented Generation) capabilities for the Salesforce Flow Builder Agent. The RAG system enhances flow generation by leveraging:

1. **Supabase Vector Store** - For storing and searching documentation embeddings
2. **GitHub Integration** - For accessing sample flow repositories
3. **OpenAI Embeddings** - For semantic search capabilities
4. **Knowledge Base** - For best practices, patterns, and troubleshooting guides

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Request  │    │  Requirements   │    │   Knowledge     │
│                 │───▶│    Analysis     │───▶│   Retrieval     │
│ "Create flow    │    │                 │    │                 │
│  for approval"  │    │ • Use case      │    │ • Best practices│
└─────────────────┘    │ • Complexity    │    │ • Sample flows  │
                       │ • Key elements  │    │ • Patterns      │
                       └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐           │
│   Enhanced      │    │   Flow XML      │           │
│   Response      │◀───│   Generation    │◀──────────┘
│                 │    │                 │
│ • Flow XML      │    │ • LLM + Context │
│ • Recommendations│   │ • RAG insights  │
│ • Context used  │    │ • Best practices│
└─────────────────┘    └─────────────────┘
```

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```bash
# RAG Configuration
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GITHUB_TOKEN=your_github_personal_access_token
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Supabase Database Setup

Run the setup script to get the SQL commands:

```bash
python scripts/setup_rag.py
```

Copy and paste the generated SQL into your Supabase SQL Editor to create:
- `flow_knowledge_base` table with vector embeddings
- `sample_flows` table for GitHub flow storage
- Similarity search functions
- Proper indexes for performance

### 4. Initialize the RAG System

```bash
python scripts/setup_rag.py
```

This will:
- Validate your environment configuration
- Guide you through Supabase setup
- Seed initial documentation
- Test the RAG functionality

## Usage

### Basic Usage

```python
from src.agents.enhanced_flow_builder_agent import run_enhanced_flow_builder_agent
from src.schemas.flow_builder_schemas import FlowBuildRequest

# Create a flow request
request = FlowBuildRequest(
    flow_api_name="ApprovalFlow",
    flow_label="Approval Process Flow",
    flow_description="Create an approval flow for expense reports over $1000"
)

# The enhanced agent will automatically:
# 1. Analyze the requirements
# 2. Search for relevant best practices
# 3. Find similar sample flows
# 4. Generate enhanced flow XML
```

### RAG Tools

The system provides several tools for knowledge management:

#### 1. Search Knowledge Base

```python
from src.tools.rag_tools import search_flow_knowledge_base

results = search_flow_knowledge_base(
    query="approval process best practices",
    category="best_practices",
    max_results=5
)
```

#### 2. Find Similar Sample Flows

```python
from src.tools.rag_tools import find_similar_sample_flows

flows = find_similar_sample_flows(
    requirements="expense approval workflow",
    use_case="approval_process",
    complexity="medium"
)
```

#### 3. Add Documentation

```python
from src.tools.rag_tools import add_flow_documentation

success = add_flow_documentation(
    title="Custom Approval Pattern",
    content="Best practices for multi-level approval flows...",
    category="best_practices",
    tags=["approval", "multi-level", "performance"]
)
```

#### 4. Sync GitHub Repositories

```python
from src.tools.rag_tools import sync_github_sample_flows

result = sync_github_sample_flows(
    repo_name="salesforce-flows",
    owner="your-org"
)
```

## Knowledge Base Categories

### Best Practices
- Performance optimization techniques
- Security considerations
- Scalability patterns
- Error handling strategies

### Examples
- Common flow patterns
- Element usage examples
- Integration patterns
- Screen flow designs

### Troubleshooting
- Common deployment issues
- Performance problems
- Logic errors
- User interface issues

## Sample Flow Repository Structure

The system expects GitHub repositories with the following structure:

```
repository/
├── flows/
│   ├── ApprovalFlow.flow-meta.xml
│   ├── EmailNotification.flow-meta.xml
│   └── LeadConversion.flow-meta.xml
├── documentation/
│   └── README.md
└── metadata/
    └── flow-descriptions.json
```

### Flow Metadata Extraction

The system automatically extracts:
- **Flow Name** - From filename
- **Description** - From XML `<description>` tag
- **Use Case** - Inferred from content and naming
- **Complexity** - Based on element count and structure
- **Tags** - Based on flow elements and patterns

## Enhanced Flow Generation Process

### 1. Requirements Analysis
```python
analysis = {
    "primary_use_case": "approval_process",
    "complexity_level": "medium", 
    "key_elements": ["record_update", "email", "conditional_logic"],
    "search_queries": [
        "expense approval workflow",
        "approval_process flow best practices",
        "conditional_logic flow pattern"
    ]
}
```

### 2. Knowledge Retrieval
- Search best practices for the identified use case
- Find similar sample flows from repositories
- Retrieve relevant patterns and examples
- Get troubleshooting information

### 3. Context Enhancement
- Combine retrieved knowledge with user requirements
- Generate enhanced prompts for the LLM
- Include specific recommendations and patterns

### 4. Flow Generation
- Use LLM with enhanced context to design flow
- Apply retrieved best practices
- Generate production-ready XML
- Include implementation recommendations

## Performance Considerations

### Vector Search Optimization
- Use appropriate similarity thresholds (default: 0.78)
- Limit result counts to avoid context overflow
- Cache frequently accessed embeddings

### Database Performance
- Proper indexing on vector columns
- Regular VACUUM and ANALYZE operations
- Monitor query performance

### API Rate Limits
- OpenAI embedding API limits
- GitHub API rate limiting
- Implement retry logic with exponential backoff

## Monitoring and Observability

### LangSmith Integration
All RAG operations are traced in LangSmith:
- Knowledge retrieval performance
- LLM prompt effectiveness
- Flow generation success rates

### Logging
Comprehensive logging for:
- RAG search queries and results
- Knowledge base updates
- Error conditions and recovery

### Metrics
Track key metrics:
- Knowledge base search accuracy
- Flow generation success rates
- User satisfaction with generated flows

## Extending the RAG System

### Adding New Knowledge Sources

1. **Custom Documentation**
```python
# Add your organization's flow standards
add_flow_documentation(
    title="Company Flow Standards",
    content="Our specific requirements...",
    category="best_practices",
    tags=["company-standard", "governance"]
)
```

2. **Additional Repositories**
```python
# Sync multiple repositories
repos = [
    {"owner": "salesforce-samples", "repo": "flow-examples"},
    {"owner": "your-org", "repo": "custom-flows"},
    {"owner": "community", "repo": "flow-patterns"}
]

for repo in repos:
    sync_github_sample_flows(repo["repo"], repo["owner"])
```

### Custom Search Functions

Create specialized search functions for your use cases:

```python
def search_security_patterns(query: str):
    """Search for security-related flow patterns"""
    return search_flow_knowledge_base(
        query=query,
        category="best_practices",
        max_results=3
    )
```

## Troubleshooting

### Common Issues

1. **Supabase Connection Errors**
   - Verify URL and service key
   - Check network connectivity
   - Ensure pgvector extension is enabled

2. **OpenAI API Errors**
   - Verify API key validity
   - Check rate limits and quotas
   - Monitor embedding costs

3. **GitHub Access Issues**
   - Verify personal access token
   - Check repository permissions
   - Ensure token has repo scope

4. **Vector Search Performance**
   - Check index creation
   - Monitor query complexity
   - Adjust similarity thresholds

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Run system health checks:

```python
from src.tools.rag_tools import rag_manager

# Test connections
print("Supabase:", "✅" if rag_manager.supabase_client else "❌")
print("GitHub:", "✅" if rag_manager.github_client else "❌") 
print("OpenAI:", "✅" if rag_manager.embeddings else "❌")
```

## Best Practices

### Knowledge Base Management
- Regularly update documentation
- Remove outdated patterns
- Maintain consistent categorization
- Monitor search effectiveness

### Sample Flow Curation
- Review flows before adding to repositories
- Ensure flows follow best practices
- Include comprehensive descriptions
- Tag flows appropriately

### Performance Optimization
- Monitor embedding costs
- Cache frequently accessed data
- Optimize search queries
- Regular database maintenance

## Future Enhancements

### Planned Features
- **Semantic Clustering** - Group similar flows automatically
- **Auto-tagging** - AI-powered tag generation
- **Flow Validation** - Automated quality checks
- **Usage Analytics** - Track most useful patterns
- **Multi-modal Search** - Search by flow diagrams
- **Collaborative Filtering** - Recommend based on usage patterns

### Integration Opportunities
- **Salesforce Metadata API** - Direct org integration
- **Flow Builder UI** - Browser extension
- **CI/CD Pipelines** - Automated flow validation
- **Slack/Teams** - Conversational flow assistance

## Contributing

To contribute to the RAG system:

1. Add new documentation to the knowledge base
2. Share sample flows in GitHub repositories
3. Report issues and suggest improvements
4. Contribute code enhancements

## Support

For support with the RAG implementation:
- Check the troubleshooting section
- Review logs for error details
- Test individual components
- Consult the LangSmith traces for debugging 