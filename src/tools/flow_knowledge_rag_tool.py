from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

class FlowKnowledgeRAGInput(BaseModel):
    """Input for Flow Knowledge RAG Tool"""
    query: str = Field(description="The query to search for in the knowledge base")
    flow_type: Optional[str] = Field(default=None, description="Optional flow type to filter results")
    max_results: int = Field(default=5, description="Maximum number of results to return")

class FlowKnowledgeRAGTool(BaseTool):
    """
    RAG (Retrieval-Augmented Generation) tool for Salesforce Flow best practices.
    
    This tool maintains a comprehensive knowledge base of Salesforce Flow best practices,
    patterns, and common solutions. It uses text-based search to retrieve relevant
    information based on the current flow building context.
    """
    
    name: str = "flow_knowledge_rag"
    description: str = """
    Search the Salesforce Flow knowledge base for best practices, patterns, and guidance.
    Use this tool to get relevant information about flow design, performance optimization,
    error handling, security considerations, and deployment best practices.
    """
    args_schema = FlowKnowledgeRAGInput
    
    # Declare the knowledge_base attribute
    knowledge_base: List[Dict[str, Any]] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize after parent constructor
        object.__setattr__(self, 'knowledge_base', self._create_knowledge_base())
    
    def _create_knowledge_base(self) -> List[Dict[str, Any]]:
        """Create the knowledge base with Flow best practices"""
        
        knowledge_base = [
            # Flow Naming Conventions
            {
                "content": """
                Flow Naming Best Practices:
                - Use descriptive names that clearly indicate the flow's purpose
                - Follow naming convention: [Object]_[Action]_[Trigger] (e.g., Lead_Qualification_AfterSave)
                - Avoid spaces and special characters in API names
                - Use PascalCase for API names and Title Case for labels
                - Include version numbers for major changes (e.g., Lead_Qualification_v2)
                - Keep names under 80 characters for better readability
                """,
                "category": "naming",
                "flow_type": "all",
                "keywords": ["naming", "conventions", "api", "labels", "version"]
            },
            
            # Record-Triggered Flow Best Practices
            {
                "content": """
                Record-Triggered Flow Best Practices:
                - Use entry criteria to limit when the flow runs
                - Prefer Before-Save flows for same-record updates to avoid additional DML
                - Use After-Save flows for related record updates or external system calls
                - Always include null checks in decision criteria
                - Bulkify flows to handle multiple records efficiently
                - Avoid recursive triggers by checking if fields have actually changed
                - Use fast field updates when possible instead of record updates
                """,
                "category": "record_triggered",
                "flow_type": "Record-Triggered",
                "keywords": ["record", "triggered", "before", "after", "save", "dml", "bulkify", "recursive"]
            },
            
            # Screen Flow Best Practices
            {
                "content": """
                Screen Flow Best Practices:
                - Design mobile-friendly layouts with appropriate field sizing
                - Use clear, descriptive field labels and help text
                - Implement proper validation with custom error messages
                - Group related fields using sections and columns
                - Provide clear navigation with Back/Next buttons
                - Use dynamic visibility to show/hide fields based on user input
                - Include progress indicators for multi-step flows
                - Test with different user profiles and permission sets
                """,
                "category": "screen_flow",
                "flow_type": "Screen",
                "keywords": ["screen", "mobile", "validation", "navigation", "visibility", "progress", "user"]
            },
            
            # Performance Optimization
            {
                "content": """
                Flow Performance Optimization:
                - Minimize the number of DML operations by bulking updates
                - Use Get Records elements efficiently with proper filters
                - Avoid unnecessary loops and recursive operations
                - Use fast field updates instead of record updates when possible
                - Implement proper indexing on filter fields
                - Limit the number of records processed in loops
                - Use decision elements to avoid unnecessary processing
                - Consider using Apex for complex calculations
                """,
                "category": "performance",
                "flow_type": "all",
                "keywords": ["performance", "optimization", "dml", "loops", "indexing", "apex", "calculations"]
            },
            
            # Error Handling and Fault Paths
            {
                "content": """
                Flow Error Handling Best Practices:
                - Add fault connectors to all DML operations
                - Create meaningful error messages for users
                - Log errors for debugging and monitoring
                - Provide alternative paths when operations fail
                - Use try-catch patterns with decision elements
                - Validate input data before processing
                - Handle governor limit exceptions gracefully
                - Test error scenarios thoroughly
                """,
                "category": "error_handling",
                "flow_type": "all",
                "keywords": ["error", "fault", "connectors", "exceptions", "validation", "debugging", "monitoring"]
            },
            
            # Security Considerations
            {
                "content": """
                Flow Security Best Practices:
                - Run flows in user context when possible for proper security
                - Validate user permissions before sensitive operations
                - Use field-level security and object permissions
                - Sanitize user input to prevent injection attacks
                - Avoid exposing sensitive data in screen flows
                - Use sharing rules and record access appropriately
                - Implement proper audit trails for sensitive operations
                - Review flow access and permissions regularly
                """,
                "category": "security",
                "flow_type": "all",
                "keywords": ["security", "permissions", "field-level", "injection", "sharing", "audit", "access"]
            },
            
            # Common Deployment Errors
            {
                "content": """
                Common Flow Deployment Errors and Solutions:
                - "Insufficient access rights": Check user permissions and field-level security
                - "Version number conflict": Increment version number or use Flow Definition
                - "Active flow cannot be overwritten": Deactivate existing flow first
                - "Missing field references": Verify all field API names are correct
                - "Invalid element reference": Check all element names and connections
                - "Validation errors": Review all required fields and data types
                - "Governor limit exceeded": Optimize flow performance and bulkify operations
                """,
                "category": "deployment_errors",
                "flow_type": "all",
                "keywords": ["deployment", "errors", "access", "version", "active", "references", "validation", "governor"]
            },
            
            # Testing Strategies
            {
                "content": """
                Flow Testing Best Practices:
                - Test with different user profiles and permission sets
                - Validate all decision paths and outcomes
                - Test with edge cases and boundary conditions
                - Verify error handling and fault paths
                - Test with bulk data scenarios
                - Use debug logs to trace flow execution
                - Create test data that covers all scenarios
                - Document test cases and expected outcomes
                """,
                "category": "testing",
                "flow_type": "all",
                "keywords": ["testing", "profiles", "decision", "paths", "edge", "cases", "debug", "logs", "scenarios"]
            },
            
            # Documentation Standards
            {
                "content": """
                Flow Documentation Best Practices:
                - Include clear descriptions for all flow elements
                - Document business logic and decision criteria
                - Maintain version history and change logs
                - Create user guides for screen flows
                - Document dependencies and prerequisites
                - Include troubleshooting guides
                - Use consistent naming and labeling
                - Keep documentation up-to-date with changes
                """,
                "category": "documentation",
                "flow_type": "all",
                "keywords": ["documentation", "descriptions", "business", "logic", "version", "history", "guides", "troubleshooting"]
            },
            
            # Governor Limits and Considerations
            {
                "content": """
                Flow Governor Limits and Considerations:
                - Maximum 2,000 elements per flow
                - DML operations are limited per transaction
                - SOQL queries are limited per transaction
                - CPU time limits apply to flow execution
                - Heap size limits for data storage
                - Maximum 50 unique flows per transaction
                - Bulkify operations to stay within limits
                - Monitor flow performance and resource usage
                """,
                "category": "governor_limits",
                "flow_type": "all",
                "keywords": ["governor", "limits", "elements", "dml", "soql", "cpu", "heap", "bulkify", "performance"]
            },
            
            # Integration Patterns
            {
                "content": """
                Flow Integration Best Practices:
                - Use platform events for asynchronous communication
                - Implement proper error handling for external callouts
                - Use named credentials for secure authentication
                - Handle timeout and retry scenarios
                - Validate external system responses
                - Log integration activities for monitoring
                - Use appropriate integration patterns (sync vs async)
                - Consider data volume and performance impacts
                """,
                "category": "integration",
                "flow_type": "all",
                "keywords": ["integration", "platform", "events", "callouts", "credentials", "timeout", "retry", "monitoring"]
            },
            
            # Decision Element Best Practices
            {
                "content": """
                Decision Element Best Practices:
                - Use clear, descriptive outcome names
                - Implement proper null checking
                - Order conditions from most to least likely
                - Use AND/OR logic appropriately
                - Avoid overly complex decision criteria
                - Document decision logic clearly
                - Test all decision paths thoroughly
                - Consider using formula fields for complex logic
                """,
                "category": "decision_elements",
                "flow_type": "all",
                "keywords": ["decision", "elements", "outcomes", "null", "checking", "conditions", "logic", "formula"]
            },
            
            # Loop Element Best Practices
            {
                "content": """
                Loop Element Best Practices:
                - Limit the number of iterations to prevent timeouts
                - Use collection variables efficiently
                - Implement proper exit conditions
                - Avoid nested loops when possible
                - Bulkify DML operations outside loops
                - Use assignment elements to build collections
                - Monitor performance with large datasets
                - Consider alternative approaches for complex iterations
                """,
                "category": "loop_elements",
                "flow_type": "all",
                "keywords": ["loop", "elements", "iterations", "timeouts", "collections", "exit", "nested", "assignment"]
            },
            
            # Variable and Collection Management
            {
                "content": """
                Variable and Collection Management:
                - Use descriptive variable names
                - Choose appropriate data types
                - Initialize variables with default values
                - Use collections for bulk operations
                - Minimize variable scope and lifetime
                - Clear large collections when no longer needed
                - Use constants for fixed values
                - Document variable purposes and usage
                """,
                "category": "variables",
                "flow_type": "all",
                "keywords": ["variables", "collections", "data", "types", "initialize", "scope", "constants", "bulk"]
            },
            
            # Scheduled Flow Best Practices
            {
                "content": """
                Scheduled Flow Best Practices:
                - Use appropriate scheduling frequency
                - Implement proper batch processing
                - Handle large datasets efficiently
                - Include monitoring and alerting
                - Use start and end date filters
                - Implement proper error handling
                - Monitor execution history and performance
                - Consider timezone implications
                """,
                "category": "scheduled_flows",
                "flow_type": "Scheduled",
                "keywords": ["scheduled", "frequency", "batch", "processing", "datasets", "monitoring", "timezone", "history"]
            },
            
            # Platform Event Flow Best Practices
            {
                "content": """
                Platform Event Flow Best Practices:
                - Design events with appropriate granularity
                - Handle event processing failures gracefully
                - Implement proper retry mechanisms
                - Use event replay for recovery scenarios
                - Monitor event volume and processing times
                - Design for idempotent processing
                - Include proper event validation
                - Document event schemas and usage
                """,
                "category": "platform_events",
                "flow_type": "Platform Event",
                "keywords": ["platform", "events", "granularity", "failures", "retry", "replay", "idempotent", "schemas"]
            }
        ]
        
        return knowledge_base
    
    def _search_knowledge_base(self, query: str, flow_type: Optional[str] = None, max_results: int = 5) -> str:
        """Search the knowledge base using text matching"""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        results = []
        
        for item in self.knowledge_base:
            score = 0
            
            # Check flow type match
            if flow_type and item["flow_type"] != "all" and item["flow_type"] != flow_type:
                continue
            
            # Score based on keyword matches
            for keyword in item["keywords"]:
                if keyword in query_lower:
                    score += 3
            
            # Score based on content matches
            content_lower = item["content"].lower()
            for word in query_words:
                if word in content_lower:
                    score += 1
            
            # Score based on category match
            if any(word in item["category"] for word in query_words):
                score += 2
            
            if score > 0:
                results.append((score, item))
        
        # Sort by score and take top results
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:max_results]
        
        if not top_results:
            return "No relevant information found for your query."
        
        # Format results
        formatted_results = []
        for score, item in top_results:
            category = item["category"].upper()
            content = item["content"].strip()
            formatted_results.append(f"[{category}]\n{content}")
        
        return "\n\n".join(formatted_results)
    
    def _run(self, query: str, flow_type: Optional[str] = None, max_results: int = 5) -> str:
        """Execute the search"""
        try:
            return self._search_knowledge_base(query, flow_type, max_results)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    def invoke(self, input_data: Dict[str, Any]) -> str:
        """Invoke the tool with input data"""
        return self._run(
            query=input_data.get("query", ""),
            flow_type=input_data.get("flow_type"),
            max_results=input_data.get("max_results", 5)
        )

# Example usage
if __name__ == "__main__":
    tool = FlowKnowledgeRAGTool()
    
    # Test queries
    test_queries = [
        {
            "query": "How to handle errors in record-triggered flows?",
            "flow_type": "Record-Triggered"
        },
        {
            "query": "Best practices for screen flow design",
            "flow_type": "Screen"
        },
        {
            "query": "Performance optimization techniques"
        },
        {
            "query": "Common deployment errors and solutions"
        }
    ]
    
    for test_query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {test_query['query']}")
        print(f"{'='*50}")
        result = tool.invoke(test_query)
        print(result) 