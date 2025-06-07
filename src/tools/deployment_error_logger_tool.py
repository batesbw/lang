import os
import json
from datetime import datetime
from typing import Type, List, Dict, Any
from pathlib import Path

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from src.tools.web_search_tool import WebSearchTool
from src.schemas.deployment_schemas import DeploymentResponse, MetadataComponent
from src.schemas.web_search_schemas import WebSearchResponse


class DeploymentErrorLogRequest(BaseModel):
    """Request model for logging deployment errors"""
    deployment_response: DeploymentResponse = Field(description="The deployment response containing error details")
    components: List[MetadataComponent] = Field(description="The components that were attempted to be deployed")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of the error")


class DeploymentErrorLoggerTool(BaseTool):
    """Tool for logging deployment errors with web search suggestions to the deploymentErrors/errorsDB.md file"""
    
    name: str = "deployment_error_logger_tool"
    description: str = (
        "Logs deployment errors to the deploymentErrors/errorsDB.md file. "
        "Includes full error text, deployment package content, and web search suggestions for fixes."
    )
    args_schema: Type[BaseModel] = DeploymentErrorLogRequest
    
    # Use PrivateAttr for internal tools
    _web_search_tool: WebSearchTool = PrivateAttr(default_factory=WebSearchTool)
    _errors_db_path: Path = PrivateAttr(default_factory=lambda: Path("deploymentErrors/errorsDB.md"))

    def model_post_init(self, __context: Any) -> None:
        """Initialize after model creation"""
        super().model_post_init(__context)
        # Ensure the directory exists
        self._errors_db_path.parent.mkdir(exist_ok=True)

    def _generate_search_query(self, error_message: str, component_type: str) -> str:
        """Generate a search query for the deployment error"""
        # Clean up the error message for better search results
        cleaned_error = error_message.replace("\\n", " ").replace("\\r", " ").strip()
        
        # Limit the error message length for search
        if len(cleaned_error) > 200:
            cleaned_error = cleaned_error[:200]
        
        return f"Salesforce {component_type} deployment error: {cleaned_error}"

    def _format_search_results(self, search_response: WebSearchResponse) -> str:
        """Format web search results for markdown display"""
        if not search_response.success:
            return f"❌ **Search failed:** {search_response.error_message or 'Unknown error'}"
        
        formatted_output = []
        
        # Add AI-generated answer if available
        if search_response.answer:
            formatted_output.append(f"**AI Summary:**\n{search_response.answer}\n")
        
        # Add search results
        if search_response.results:
            formatted_output.append("**Relevant Resources:**")
            for i, result in enumerate(search_response.results, 1):
                formatted_output.append(f"{i}. **[{result.title}]({result.url})**")
                if result.content:
                    # Limit content length for readability
                    content = result.content[:500] + "..." if len(result.content) > 500 else result.content
                    formatted_output.append(f"   {content}")
                formatted_output.append("")  # Empty line between results
        else:
            formatted_output.append("❌ No search results found.")
        
        return "\n".join(formatted_output)

    def _get_web_search_suggestions(self, component_errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get web search suggestions for each component error"""
        suggestions = []
        
        for error in component_errors:
            component_type = error.get('componentType', 'Unknown')
            problem = error.get('problem', 'Unknown error')
            component_name = error.get('fullName', 'Unknown')
            
            try:
                # Generate search query
                search_query = self._generate_search_query(problem, component_type)
                
                # Perform web search using the tool's interface
                search_response = self._web_search_tool._run(
                    query=search_query,
                    max_results=5,
                    search_depth="basic",
                    include_answer=True,
                    topic="salesforce"
                )
                
                # Format the search results for display
                formatted_results = self._format_search_results(search_response)
                
                suggestions.append({
                    'component_name': component_name,
                    'component_type': component_type,
                    'error_message': problem,
                    'search_query': search_query,
                    'search_results': formatted_results,
                    'search_success': search_response.success
                })
                
            except Exception as e:
                suggestions.append({
                    'component_name': component_name,
                    'component_type': component_type,
                    'error_message': problem,
                    'search_query': f"Failed to generate query: {str(e)}",
                    'search_results': f"❌ **Error performing web search:** {str(e)}",
                    'search_success': False
                })
        
        return suggestions

    def _format_component_content(self, components: List[MetadataComponent]) -> str:
        """Format the content of deployment components for logging"""
        content_sections = []
        
        for i, component in enumerate(components, 1):
            section = f"""
#### Component {i}: {component.api_name} ({component.component_type})

```xml
{component.metadata_xml}
```
"""
            content_sections.append(section)
        
        return "\n".join(content_sections)

    def _format_error_entry(self, request: DeploymentErrorLogRequest, suggestions: List[Dict[str, Any]]) -> str:
        """Format the complete error entry for the database"""
        timestamp = request.timestamp
        deployment_response = request.deployment_response
        components = request.components
        
        # Header section
        entry = f"""
---

## Deployment Error - {timestamp}

**Request ID:** {deployment_response.request_id}  
**Deployment ID:** {deployment_response.deployment_id or 'N/A'}  
**Status:** {deployment_response.status}  
**Total Components:** {deployment_response.total_components}  
**Failed Components:** {deployment_response.failed_components}  

### Full Deployment Error Text

"""
        
        # Add main error message
        if deployment_response.error_message:
            entry += f"**Main Error:** {deployment_response.error_message}\n\n"
        
        # Add component-specific errors
        if deployment_response.component_errors:
            entry += "**Component Errors:**\n\n"
            for error in deployment_response.component_errors:
                entry += f"- **{error.get('fullName')} ({error.get('componentType')}):** {error.get('problem')}\n"
            entry += "\n"
        
        # Add deployment package content
        entry += "### Deployment Package Content\n"
        entry += self._format_component_content(components)
        
        # Add web search suggestions
        entry += "\n### Suggested Fixes (Web Search Results)\n\n"
        
        for suggestion in suggestions:
            status_icon = "✅" if suggestion['search_success'] else "❌"
            entry += f"""
#### {status_icon} Fix for {suggestion['component_name']} ({suggestion['component_type']})

**Error:** {suggestion['error_message']}

**Search Query:** `{suggestion['search_query']}`

**Suggested Solutions:**

{suggestion['search_results']}

---
"""
        
        return entry

    def _run(self, request: DeploymentErrorLogRequest) -> str:
        """
        Log deployment error with web search suggestions to the deploymentErrors/errorsDB.md file
        """
        try:
            deployment_response = request.deployment_response
            
            # Only log if deployment actually failed
            if deployment_response.success:
                return "Deployment was successful, no error logging needed."
            
            # Get web search suggestions for component errors
            suggestions = []
            if deployment_response.component_errors:
                suggestions = self._get_web_search_suggestions(deployment_response.component_errors)
            
            # Format the complete error entry
            error_entry = self._format_error_entry(request, suggestions)
            
            # Append to the errors database file
            with open(self._errors_db_path, 'a', encoding='utf-8') as f:
                f.write(error_entry)
                f.write("\n")
            
            successful_searches = len([s for s in suggestions if s.get('search_success', False)])
            
            return f"Successfully logged deployment error to {self._errors_db_path}. " \
                   f"Logged {len(suggestions)} component errors with web search suggestions " \
                   f"({successful_searches} successful searches)."
            
        except Exception as e:
            error_msg = f"Failed to log deployment error: {str(e)}"
            print(f"DeploymentErrorLoggerTool Error: {error_msg}")
            return error_msg

    async def _arun(self, request: DeploymentErrorLogRequest) -> str:
        """Async version of _run"""
        return self._run(request) 