import os
import uuid
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, List

# Suppress Pydantic v1/v2 mixing warnings from LangChain internals
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")
warnings.filterwarnings("ignore", message=".*Cannot generate a JsonSchema for core_schema.PlainValidatorFunctionSchema.*")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END, START
from langsmith import Client as LangSmithClient
from langchain_core.language_models import BaseLanguageModel

# Project imports
from src.state.agent_workforce_state import AgentWorkforceState
from src.agents.authentication_agent import run_authentication_agent
from src.agents.enhanced_flow_builder_agent import run_enhanced_flow_builder_agent
from src.agents.deployment_agent import run_deployment_agent
from src.agents.web_search_agent import run_web_search_agent
from src.agents.test_designer_agent import run_test_designer_agent
from src.schemas.auth_schemas import AuthenticationRequest, SalesforceAuthResponse
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse
from src.schemas.web_search_schemas import WebSearchRequest, WebSearchAgentRequest, WebSearchAgentResponse, SearchDepth
from src.schemas.test_designer_schemas import TestDesignerRequest, TestDesignerResponse

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Ensure required API keys are set
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

if not os.getenv("LANGSMITH_API_KEY"):
    print("Warning: LANGSMITH_API_KEY not found. LangSmith tracing may not work.")

# Check if web search is available
WEB_SEARCH_AVAILABLE = bool(os.getenv("TAVILY_API_KEY"))
if WEB_SEARCH_AVAILABLE:
    print("✅ Web search enabled (TAVILY_API_KEY found)")
else:
    print("⚠️ Web search disabled (TAVILY_API_KEY not found)")

# Initialize LLM with configurable model
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))  # Configurable max tokens

LLM = ChatAnthropic(
    model=ANTHROPIC_MODEL, 
    temperature=0, 
    max_tokens=LLM_MAX_TOKENS  # Use configurable value
)
print(f"Initialized LLM with model: {ANTHROPIC_MODEL}, max_tokens: {LLM_MAX_TOKENS}")

# Initialize retry configuration
MAX_BUILD_DEPLOY_RETRIES = int(os.getenv("MAX_BUILD_DEPLOY_RETRIES", "3"))
# Initialize recursion limit configuration
RECURSION_LIMIT = int(os.getenv("LANGGRAPH_RECURSION_LIMIT", "50"))

# Initialize LangSmith client for tracing
try:
    langsmith_client = LangSmithClient()
    print("LangSmith client initialized successfully.")
except Exception as e:
    print(f"Warning: Could not initialize LangSmith client: {e}")
    langsmith_client = None


def authentication_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for the Authentication Agent.
    """
    print("\n=== AUTHENTICATION NODE ===")
    try:
        return run_authentication_agent(state)
    except Exception as e:
        print(f"Error in authentication_node: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Authentication Node Error: {str(e)}"
        updated_state["is_authenticated"] = False
        return updated_state


def flow_builder_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for the Flow Builder Agent.
    """
    print("\n=== FLOW BUILDER NODE ===")
    try:
        return run_enhanced_flow_builder_agent(state, LLM)
    except Exception as e:
        print(f"Error in flow_builder_node: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Flow Builder Node Error: {str(e)}"
        return updated_state


def deployment_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for the Deployment Agent.
    """
    print("\n=== DEPLOYMENT NODE ===")
    try:
        return run_deployment_agent(state, LLM)
    except Exception as e:
        print(f"Error in deployment_node: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Deployment Node Error: {str(e)}"
        return updated_state


def web_search_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for the Web Search Agent.
    Searches for solutions to deployment failures.
    """
    print("\n=== WEB SEARCH NODE ===")
    try:
        return run_web_search_agent(state)
    except Exception as e:
        print(f"Error in web_search_node: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Web Search Node Error: {str(e)}"
        # Clear the web search request on error
        updated_state["current_web_search_request"] = None
        return updated_state


def should_continue_after_auth(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine if we should continue after authentication.
    """
    if state.get("is_authenticated", False):
        print("Authentication successful, proceeding to Flow Builder.")
        return "flow_builder"
    else:
        print("Authentication failed, ending workflow.")
        return END


def should_continue_after_flow_build(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine if we should continue after flow building.
    """
    flow_response = state.get("current_flow_build_response")
    if flow_response and flow_response.get("success"):
        print("Flow building successful, proceeding to deployment preparation.")
        return "prepare_deployment"
    else:
        print("Flow building failed, ending workflow.")
        return END


def should_continue_after_deployment(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after deployment.
    Enhanced to trigger TestDesigner on successful deployment.
    """
    deployment_response = state.get("current_deployment_response")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if deployment_response and deployment_response.get("success"):
        print("✅ Flow deployment successful, proceeding to TestDesigner.")
        return "test_designer"
    else:
        print(f"❌ Deployment failed (attempt #{build_deploy_retry_count + 1})")
        
        # Enhanced deployment failure logging
        if deployment_response:
            error_message = deployment_response.get("error_message")
            component_errors = deployment_response.get("component_errors", [])
            
            print("📋 DEPLOYMENT FAILURE DETAILS:")
            if error_message:
                print(f"   Main Error: {error_message}")
            
            if component_errors:
                print("   🔍 Specific Component Problems:")
                for i, error in enumerate(component_errors, 1):
                    if isinstance(error, dict):
                        component_type = error.get('componentType', 'Unknown')
                        problem = error.get('problem', 'Unknown error')
                        file_name = error.get('fileName', 'Unknown file')
                        print(f"     {i}. [{component_type}] {problem}")
                        print(f"        File: {file_name}")
                    else:
                        print(f"     {i}. {str(error)}")
            else:
                print("   No specific component error details available")
        
        # Check if we should retry
        if build_deploy_retry_count < max_retries:
            print(f"🔄 Retrying build/deploy cycle ({build_deploy_retry_count + 1}/{max_retries})")
            
            # Use web search if available, otherwise go directly to retry
            if WEB_SEARCH_AVAILABLE:
                print("🔍 Will search for solutions to this deployment error")
                return "search_for_solutions"
            else:
                print("⚠️ Web search not available, proceeding directly to retry")
                return "direct_retry"
        else:
            print(f"🛑 Maximum retries ({max_retries}) reached, ending workflow")
            return END


def should_retry_after_failure(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to check if we should continue with retry logic.
    This prepares for another build attempt after a deployment failure.
    """
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if build_deploy_retry_count < max_retries:
        print(f"📝 Preparing retry #{build_deploy_retry_count + 1}")
        return "prepare_retry_flow_request"
    else:
        print("🛑 Maximum retries reached in retry check")
        return END


def prepare_retry_flow_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare for a retry attempt after deployment failure.
    Enhanced to provide structured error analysis and specific guidance.
    Now incorporates web search results when available.
    """
    print("\n=== PREPARING ENHANCED RETRY FLOW BUILD REQUEST ===")
    
    # Increment retry count
    current_retry_count = state.get("build_deploy_retry_count", 0) + 1
    
    # Get the deployment failure details
    deployment_response = state.get("current_deployment_response")
    last_build_response_dict = state.get("current_flow_build_response")
    web_search_response_dict = state.get("current_web_search_response")
    
    if last_build_response_dict and deployment_response:
        try:
            last_build_response = FlowBuildResponse(**last_build_response_dict)
            original_request = last_build_response.input_request
            
            print(f"🔄 Setting up enhanced retry #{current_retry_count} for flow: {original_request.flow_api_name}")
            
            # Analyze the deployment error for specific fixes
            error_analysis = _analyze_deployment_error(
                deployment_response.get("error_message", "Unknown error"),
                deployment_response.get("component_errors", []),
                last_build_response.flow_xml
            )
            
            # Process web search results if available
            web_search_insights = None
            if web_search_response_dict:
                try:
                    web_search_response = WebSearchAgentResponse(**web_search_response_dict)
                    if web_search_response.success and web_search_response.search_response:
                        print("🔍 Incorporating web search results into retry strategy")
                        web_search_insights = {
                            "search_summary": web_search_response.summary,
                            "recommendations": web_search_response.recommendations,
                            "follow_up_queries": web_search_response.follow_up_queries,
                            "search_results_count": len(web_search_response.search_response.results),
                            "key_findings": []
                        }
                        
                        # Extract key findings from search results
                        for result in web_search_response.search_response.results[:3]:  # Top 3 results
                            web_search_insights["key_findings"].append({
                                "title": result.title,
                                "url": result.url,
                                "content_snippet": result.content[:200] + "..." if len(result.content) > 200 else result.content
                            })
                        
                        print(f"   📊 Search Results: {web_search_insights['search_results_count']} results found")
                        print(f"   🎯 Recommendations: {len(web_search_response.recommendations)} recommendations")
                        
                        # Enhance error analysis with web search insights
                        if web_search_response.recommendations:
                            print("   💡 Adding web search recommendations to fix strategy:")
                            for i, rec in enumerate(web_search_response.recommendations[:3], 1):
                                print(f"      {i}. {rec}")
                                error_analysis["required_fixes"].append(f"Web Search Insight: {rec}")
                    else:
                        print("⚠️ Web search was attempted but didn't return useful results")
                        web_search_insights = {"search_attempted": True, "search_successful": False}
                except Exception as e:
                    print(f"⚠️ Error processing web search results: {e}")
                    web_search_insights = {"search_attempted": True, "processing_error": str(e)}
            else:
                print("ℹ️ No web search results available for this retry")
            
            # Enhanced retry context with structured analysis and web search results
            retry_context = {
                "is_retry": True,
                "retry_attempt": current_retry_count,
                "original_flow_xml": last_build_response.flow_xml,
                "deployment_error": deployment_response.get("error_message", "Unknown error"),
                "component_errors": deployment_response.get("component_errors", []),
                "error_analysis": error_analysis,
                "specific_fixes_needed": error_analysis["required_fixes"],
                "common_patterns": error_analysis["error_patterns"],
                "previous_attempts_summary": _get_previous_attempts_summary(state, current_retry_count)
            }
            
            # Add web search insights if available
            if web_search_insights:
                retry_context["web_search_insights"] = web_search_insights
                print("✅ Web search insights integrated into retry context")
            
            retry_request = original_request.model_copy()
            retry_request.retry_context = retry_context
            
            # Enhanced failure analysis logging with complete visibility
            print(f"🔧 Enhanced failure analysis completed:")
            print(f"   📊 Error Classification:")
            print(f"      Primary error type: {error_analysis['error_type']}")
            print(f"      Severity level: {error_analysis['severity']}")
            print(f"      Error patterns detected: {len(error_analysis['error_patterns'])}")
            
            if error_analysis['error_patterns']:
                print(f"      Detected patterns: {', '.join(error_analysis['error_patterns'])}")
            
            # Show ALL required fixes, not just the first 3
            fixes = error_analysis['required_fixes']
            print(f"   🛠️  Required Fixes Identified: {len(fixes)}")
            if fixes:
                print(f"      How fixes were identified: Based on error pattern analysis, Salesforce Flow best practices, and web search insights")
                for i, fix in enumerate(fixes, 1):
                    print(f"      {i}. {fix}")
            else:
                print(f"      No specific fixes identified - using general guidance")
            
            # Show categorized issues if any
            if error_analysis['api_name_issues']:
                print(f"   🏷️  API Name Issues ({len(error_analysis['api_name_issues'])}):")
                for issue in error_analysis['api_name_issues']:
                    print(f"      - {issue}")
            
            if error_analysis['structural_issues']:
                print(f"   🏗️  Structural Issues ({len(error_analysis['structural_issues'])}):")
                for issue in error_analysis['structural_issues']:
                    print(f"      - {issue}")
            
            if error_analysis['xml_issues']:
                print(f"   📄 XML Issues ({len(error_analysis['xml_issues'])}):")
                for issue in error_analysis['xml_issues']:
                    print(f"      - {issue}")
            
            updated_state = state.copy()
            updated_state["current_flow_build_request"] = retry_request.model_dump()
            updated_state["build_deploy_retry_count"] = current_retry_count
            
            # Clear the web search response after processing
            updated_state["current_web_search_response"] = None
            
            print(f"✅ Enhanced retry request prepared - attempt #{current_retry_count}")
            return updated_state
            
        except Exception as e:
            print(f"❌ Error preparing retry request: {str(e)}")
            updated_state = state.copy()
            updated_state["error_message"] = f"Failed to prepare retry: {str(e)}"
            return updated_state
    else:
        print("❌ No previous build response or deployment response found for retry")
        updated_state = state.copy()
        updated_state["error_message"] = "Cannot retry: no previous build/deployment response"
        return updated_state


def _analyze_deployment_error(error_message: str, component_errors: list, flow_xml: str) -> dict:
    """
    Analyze deployment errors to provide structured guidance for fixes
    """
    analysis = {
        "error_type": "unknown",
        "severity": "medium",
        "required_fixes": [],
        "error_patterns": [],
        "xml_issues": [],
        "api_name_issues": [],
        "structural_issues": []
    }
    
    error_text = error_message.lower() if error_message else ""
    
    # Also check component errors for additional context
    all_error_text = error_text
    for error in component_errors:
        if isinstance(error, dict):
            problem = error.get("problem", "").lower()
            all_error_text += " " + problem
    
    # Analyze specific Salesforce Flow deployment error patterns
    
    # Type conversion errors (like xsd:double errors)
    if ("is not valid for the type" in all_error_text and "xsd:" in all_error_text):
        analysis["error_type"] = "type_conversion_error"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Data type mismatch in flow elements")
        analysis["required_fixes"].extend([
            "Fix data type mismatches in flow variables and assignments",
            "Ensure numeric values are properly formatted for xsd:double type",
            "Check that formula expressions return the expected data type",
            "Validate that variable assignments match the target field types",
            "Use proper data type conversion functions if needed"
        ])
        analysis["error_patterns"].append("TYPE_CONVERSION_ERROR")
    
    # Collection variable input assignment errors
    elif ("inputassignments field can't use a collection variable" in all_error_text):
        analysis["error_type"] = "collection_variable_input_error"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Incorrect use of collection variables in input assignments")
        analysis["required_fixes"].extend([
            "Remove collection variables from inputAssignments fields",
            "Use individual record variables instead of collection variables for assignments",
            "Initialize collection variables properly before using them",
            "Ensure assignment elements target individual variables, not collections",
            "Check flow element configurations for proper variable usage",
            "Convert collection variables to individual variables for assignment operations"
        ])
        analysis["error_patterns"].append("COLLECTION_VARIABLE_INPUT_ERROR")
    
    # Invalid flow element reference (like in the user's example) - Check both main error and component errors
    elif ("invalid flow element" in all_error_text or "unknown element" in all_error_text or 
        "contains an invalid flow element" in all_error_text):
        analysis["error_type"] = "invalid_flow_element_reference"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Flow contains references to non-existent elements")
        analysis["required_fixes"].extend([
            "Remove or fix references to invalid flow elements (e.g., Get_Contact_Count)",
            "Ensure all element references point to actually defined elements in the flow",
            "Check formula expressions for invalid element references",
            "Verify that all flow elements are properly defined with correct names",
            "Replace invalid element references with valid flow elements or variables"
        ])
        analysis["error_patterns"].append("INVALID_FLOW_ELEMENT_REFERENCE")
    
    # Formula expression errors
    elif "formula expression is invalid" in all_error_text:
        analysis["error_type"] = "invalid_formula_expression"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Invalid formula expressions detected")
        analysis["required_fixes"].extend([
            "Fix invalid formula expressions in flow elements",
            "Ensure all referenced elements exist in the flow",
            "Validate formula syntax and element references",
            "Use proper Flow expression syntax for element references"
        ])
        analysis["error_patterns"].append("INVALID_FORMULA_EXPRESSION")
    
    # Field integrity exceptions (broader category)
    elif "field integrity exception" in all_error_text:
        analysis["error_type"] = "field_integrity_violation"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Field integrity constraints violated")
        analysis["required_fixes"].extend([
            "Fix field integrity violations in flow definitions",
            "Ensure all field references are valid and accessible",
            "Check for missing required fields or invalid field types",
            "Validate flow element configurations against Salesforce schema"
        ])
        analysis["error_patterns"].append("FIELD_INTEGRITY_VIOLATION")
    
    # API Name validation errors
    elif "invalid name" in all_error_text or "api name" in all_error_text:
        analysis["error_type"] = "api_name_validation"
        analysis["severity"] = "high"
        analysis["api_name_issues"].append("Invalid API name format detected")
        analysis["required_fixes"].extend([
            "Fix API names to be alphanumeric and start with a letter",
            "Remove spaces, hyphens, and special characters from all API names",
            "Ensure API names follow Salesforce naming conventions"
        ])
        analysis["error_patterns"].append("API_NAME_INVALID")
    
    # Duplicate element errors
    elif "duplicate" in all_error_text and "element" in all_error_text:
        analysis["error_type"] = "duplicate_elements"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Duplicate element names detected")
        analysis["required_fixes"].extend([
            "Ensure all flow element names are unique",
            "Check for duplicate screen, decision, or assignment names",
            "Use incremental naming (e.g., Screen1, Screen2) for multiple elements"
        ])
        analysis["error_patterns"].append("DUPLICATE_ELEMENTS")
    
    # Element reference errors
    elif "element reference" in all_error_text or "target reference" in all_error_text:
        analysis["error_type"] = "invalid_references"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Invalid element references")
        analysis["required_fixes"].extend([
            "Fix element references to point to valid flow elements",
            "Ensure all connector targetReference values match existing element names",
            "Check start element connector references"
        ])
        analysis["error_patterns"].append("INVALID_REFERENCES")
    
    # Missing required fields
    elif "required field" in all_error_text or "missing" in all_error_text:
        analysis["error_type"] = "missing_required_fields"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Missing required fields or elements")
        analysis["required_fixes"].extend([
            "Add all required flow elements and properties",
            "Ensure proper flow structure with start element",
            "Include mandatory metadata elements"
        ])
        analysis["error_patterns"].append("MISSING_REQUIRED_FIELDS")
    
    # XML syntax errors
    elif "xml" in all_error_text or "malformed" in all_error_text or "syntax" in all_error_text:
        analysis["error_type"] = "xml_syntax"
        analysis["severity"] = "critical"
        analysis["xml_issues"].append("XML syntax or structure issues")
        analysis["required_fixes"].extend([
            "Fix XML syntax errors and malformed elements",
            "Ensure proper XML namespace and structure",
            "Validate XML against Salesforce Flow schema"
        ])
        analysis["error_patterns"].append("XML_SYNTAX_ERROR")
    
    # Analyze component errors for additional insights
    for error in component_errors:
        if isinstance(error, dict):
            problem = error.get("problem", "").lower()
            component_type = error.get("componentType", "")
            
            if "flow" in component_type.lower():
                if "name" in problem:
                    analysis["api_name_issues"].append(f"Flow component naming issue: {problem}")
                elif "reference" in problem:
                    analysis["structural_issues"].append(f"Flow reference issue: {problem}")
                elif "formula expression" in problem:
                    analysis["structural_issues"].append(f"Formula expression issue: {problem}")
    
    # If no specific pattern detected, provide general guidance
    if analysis["error_type"] == "unknown":
        analysis["error_type"] = "general_deployment_failure"
        analysis["required_fixes"] = [
            "Review the deployment error message carefully",
            "Ensure all flow elements have valid configurations",
            "Check that the flow follows Salesforce best practices",
            "Validate the flow XML structure and content"
        ]
    
    return analysis


def _get_previous_attempts_summary(state: AgentWorkforceState, current_retry: int) -> str:
    """
    Generate a summary of previous attempts for context
    """
    if current_retry <= 1:
        return "This is the first retry attempt."
    
    summary = f"This is retry attempt #{current_retry}. "
    
    # You could enhance this by storing more detailed attempt history
    # For now, provide basic context
    if current_retry == 2:
        summary += "The first retry failed. Focus on addressing the core deployment error."
    elif current_retry == 3:
        summary += "Two previous retries failed. Consider a fundamentally different approach."
    else:
        summary += f"Multiple retries ({current_retry - 1}) have failed. The error may require manual investigation."
    
    return summary


def prepare_web_search_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare a web search request based on deployment failure.
    Enhanced to create more targeted search queries based on specific error types.
    """
    print("\n=== PREPARING WEB SEARCH REQUEST ===")
    
    if not WEB_SEARCH_AVAILABLE:
        print("⚠️ Web search not available (TAVILY_API_KEY not found)")
        return state
    
    deployment_response = state.get("current_deployment_response")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    
    if not deployment_response:
        print("❌ No deployment response found for web search")
        return state
    
    error_message = deployment_response.get("error_message", "")
    component_errors = deployment_response.get("component_errors", [])
    
    # Create a comprehensive search query based on the specific error
    search_query = "Salesforce Flow deployment error"
    
    # Add specific error details to the search query
    if component_errors and len(component_errors) > 0:
        first_error = component_errors[0]
        if isinstance(first_error, dict):
            problem = first_error.get("problem", "")
            # Extract key phrases from the error for better search
            if "field integrity exception" in problem.lower():
                search_query = "Salesforce Flow field integrity exception deployment error"
            elif "inputassignments field can't use a collection variable" in problem.lower():
                search_query = "Salesforce Flow inputAssignments collection variable deployment error fix"
            elif "is not valid for the type xsd:" in problem.lower():
                search_query = "Salesforce Flow deployment error xsd type validation XML parsing"
            elif "invalid flow element" in problem.lower() or "unknown element" in problem.lower():
                search_query = "Salesforce Flow invalid flow element reference deployment error"
            else:
                # Use the first significant phrase from the error
                search_query = f"Salesforce Flow deployment error {problem[:50]}"
    
    print(f"Prepared web search for query: '{search_query}'")
    
    # Create enhanced search request with better parameters
    search_request = WebSearchRequest(
        query=search_query,
        max_results=8,  # Increased from 5 for better coverage
        search_depth=SearchDepth.ADVANCED,  # Always use advanced for deployment issues
        include_domains=['salesforce.com', 'trailhead.salesforce.com', 'developer.salesforce.com'],
        exclude_domains=None,
        include_answer=True,
        include_raw_content=False,
        topic='salesforce_flows'
    )
    
    # Enhanced context for the search agent
    search_context = f"""
    We are experiencing a Salesforce Flow deployment failure during retry attempt #{build_deploy_retry_count}.
    
    Main Error: {error_message}
    
    Component Errors: {component_errors}
    
    We need to find solutions, best practices, and common fixes for this type of deployment error.
    """
    
    # Specific instructions for the search agent
    agent_instructions = """
    Focus on finding:
    1. Specific solutions for this exact error type
    2. Salesforce documentation about Flow deployment best practices
    3. Common causes and fixes for similar deployment errors
    4. XML structure requirements and validation rules
    5. Step-by-step troubleshooting guides
    
    Prioritize official Salesforce documentation, Trailhead resources, and developer community solutions.
    """
    
    web_search_request = WebSearchAgentRequest(
        search_request=search_request,
        context=search_context,
        agent_instructions=agent_instructions
    )
    
    updated_state = state.copy()
    updated_state["current_web_search_request"] = web_search_request.model_dump()
    
    return updated_state


def record_build_deploy_cycle(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to record the current build/deploy cycle attempt with enhanced failure details.
    """
    print("\n=== RECORDING BUILD/DEPLOY CYCLE - ENHANCED ===")
    
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    deployment_response = state.get("current_deployment_response")
    
    if deployment_response and not deployment_response.get("success"):
        print(f"❌ Deployment failed (attempt #{build_deploy_retry_count})")
        
        # Show the specific reason for failure
        error_message = deployment_response.get("error_message")
        component_errors = deployment_response.get("component_errors", [])
        
        if error_message:
            print(f"   📋 Failure Reason: {error_message}")
        
        if component_errors:
            print(f"   🔍 Component Error Summary:")
            for error in component_errors[:2]:  # Show first 2 errors to keep it concise
                if isinstance(error, dict):
                    problem = error.get('problem', 'Unknown error')
                    # Truncate long error messages for summary
                    if len(problem) > 80:
                        problem = problem[:77] + "..."
                    print(f"      - {problem}")
        
        if build_deploy_retry_count < max_retries:
            print(f"🔄 Retrying build/deploy cycle ({build_deploy_retry_count + 1}/{max_retries})")
        else:
            print(f"🛑 Maximum retries ({max_retries}) will be reached - this may be the final attempt")
    
    return state


def prepare_flow_build_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare the flow build request based on authentication success.
    This creates a flow request based on user story and acceptance criteria if provided,
    or a simple default flow request for testing.
    """
    print("\n=== PREPARING FLOW BUILD REQUEST ===")
    
    if not state.get("is_authenticated", False):
        print("Cannot prepare flow build request - not authenticated.")
        return state
    
    # Check if user story and acceptance criteria are provided in the state
    user_story_data = state.get("user_story")
    
    if user_story_data:
        print("Found user story in state, creating flow request from user requirements...")
        
        # Import here to avoid circular imports
        from src.schemas.flow_builder_schemas import UserStory, FlowRequirement, FlowType
        
        # Create UserStory object from provided data
        user_story = UserStory(**user_story_data)
        
        # Create a flow build request based on the user story
        flow_request = FlowBuildRequest(
            flow_api_name=f"UserStory_{user_story.title.replace(' ', '_')}",
            flow_label=user_story.title,
            flow_description=user_story.description,
            user_story=user_story,
            flow_type=FlowType.SCREEN_FLOW,  # Default to screen flow for user stories
            target_api_version="59.0"
        )
        
        print(f"Created flow request from user story: {user_story.title}")
        print(f"Acceptance criteria: {user_story.acceptance_criteria}")
        
    else:
        print("No user story provided, creating default test flow request...")
        
        # Create a simple default flow build request for testing
        flow_request = FlowBuildRequest(
            flow_api_name="AgentGeneratedTestFlow",
            flow_label="Agent Generated Test Flow",
            flow_description="A simple test flow generated by the agent workforce",
            screen_api_name="WelcomeScreen",
            screen_label="Welcome Screen",
            display_text_api_name="WelcomeMessage",
            display_text_content="Hello! This flow was automatically generated and deployed by the Salesforce Agent Workforce.",
            target_api_version="59.0"
        )
    
    updated_state = state.copy()
    # Convert Pydantic model to dict for state storage
    updated_state["current_flow_build_request"] = flow_request.model_dump()
    print(f"Prepared flow build request for: {flow_request.flow_api_name}")
    
    return updated_state


def create_multi_component_deployment_request(
    components_data: List[Dict[str, str]], 
    salesforce_session: SalesforceAuthResponse,
    request_id: Optional[str] = None
) -> DeploymentRequest:
    """
    Helper function to create a DeploymentRequest with multiple components.
    
    Args:
        components_data: List of dicts with keys: component_type, api_name, metadata_xml
                        Optional keys: directory, file_extension
        salesforce_session: Active Salesforce session
        request_id: Optional request ID, will generate one if not provided
    
    Returns:
        DeploymentRequest ready for deployment
        
    Example:
        components = [
            {
                "component_type": "Flow",
                "api_name": "MyFlow",
                "metadata_xml": "<Flow>...</Flow>"
            },
            {
                "component_type": "CustomObject", 
                "api_name": "MyObject__c",
                "metadata_xml": "<CustomObject>...</CustomObject>"
            }
        ]
        request = create_multi_component_deployment_request(components, sf_session)
    """
    from src.schemas.deployment_schemas import MetadataComponent
    
    components = []
    for comp_data in components_data:
        component = MetadataComponent(
            component_type=comp_data["component_type"],
            api_name=comp_data["api_name"],
            metadata_xml=comp_data["metadata_xml"],
            directory=comp_data.get("directory"),
            file_extension=comp_data.get("file_extension")
        )
        components.append(component)
    
    return DeploymentRequest(
        request_id=request_id or str(uuid.uuid4()),
        components=components,
        salesforce_session=salesforce_session
    )


def prepare_deployment_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare the deployment request based on successful flow building.
    Updated to work with the new multi-component deployment system.
    """
    print("\n=== PREPARING DEPLOYMENT REQUEST ===")
    
    flow_response_dict = state.get("current_flow_build_response")
    salesforce_session_dict = state.get("salesforce_session")
    
    if not flow_response_dict:
        print("Cannot prepare deployment request - no flow build response.")
        return state
    
    if not salesforce_session_dict:
        print("Cannot prepare deployment request - no Salesforce session available.")
        return state
    
    # Convert dict back to Pydantic model for processing
    try:
        from src.schemas.deployment_schemas import MetadataComponent
        
        flow_response = FlowBuildResponse(**flow_response_dict)
        salesforce_session = SalesforceAuthResponse(**salesforce_session_dict)
        
        if not flow_response.success:
            print("Cannot prepare deployment request - flow building failed.")
            return state
        
        # Create a MetadataComponent for the Flow
        flow_component = MetadataComponent(
            component_type="Flow",
            api_name=flow_response.input_request.flow_api_name,
            metadata_xml=flow_response.flow_xml
        )
        
        # Create deployment request with the flow component
        deployment_request = DeploymentRequest(
            request_id=str(uuid.uuid4()),
            components=[flow_component],
            salesforce_session=salesforce_session
        )
        
        updated_state = state.copy()
        # Convert Pydantic model to dict for state storage
        updated_state["current_deployment_request"] = deployment_request.model_dump()
        print(f"Prepared deployment request for flow: {flow_component.api_name}")
        
        return updated_state
        
    except Exception as e:
        print(f"Error preparing deployment request: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Error preparing deployment request: {str(e)}"
        return updated_state


def test_designer_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for running the TestDesigner agent.
    """
    print("--- Executing TestDesigner Agent Node ---")
    return run_test_designer_agent(state)


def prepare_test_designer_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare TestDesigner request after successful Flow deployment.
    Enhanced to utilize all available user_story information for comprehensive test design.
    """
    print("\n=== PREPARING TEST DESIGNER REQUEST ===")
    
    # Get successful deployment details
    deployment_response_dict = state.get("current_deployment_response")
    flow_response_dict = state.get("current_flow_build_response")
    user_story_dict = state.get("user_story")
    
    if not deployment_response_dict or not deployment_response_dict.get("success"):
        print("Cannot prepare TestDesigner request - deployment was not successful.")
        return state
    
    if not flow_response_dict:
        print("Cannot prepare TestDesigner request - no flow build response.")
        return state
    
    try:
        # Convert dict back to Pydantic model for processing
        flow_response = FlowBuildResponse(**flow_response_dict)
        
        # Extract user story and acceptance criteria
        if user_story_dict:
            user_story = user_story_dict
            acceptance_criteria = user_story_dict.get("acceptance_criteria", [])
            
            # Extract additional rich information for enhanced test design
            affected_objects = user_story_dict.get("affected_objects", [])
            business_context = user_story_dict.get("business_context", "")
            user_personas = user_story_dict.get("user_personas", [])
            
            print(f"📋 Using rich user story information:")
            print(f"   Title: {user_story_dict.get('title', 'N/A')}")
            print(f"   Affected Objects: {affected_objects}")
            print(f"   User Personas: {user_personas}")
            print(f"   Acceptance Criteria: {len(acceptance_criteria)} criteria")
            
        else:
            # Create default user story for test flows
            user_story = {
                "title": f"Test Flow: {flow_response.input_request.flow_api_name}",
                "description": f"Automated testing for {flow_response.input_request.flow_description}",
                "priority": "High"
            }
            acceptance_criteria = [
                "Flow executes successfully without errors",
                "Flow produces expected outputs",
                "Flow handles edge cases appropriately"
            ]
            affected_objects = []
            business_context = ""
            user_personas = []
            
            print("📋 Using default test story (no user story provided)")
        
        # Determine flow type based on user story or default to Screen Flow
        flow_type = "Screen Flow"  # Default
        if affected_objects:
            # If objects are involved, it's likely a Record-Triggered Flow
            if len(affected_objects) > 1:
                flow_type = "Record-Triggered Flow"
            else:
                flow_type = "Screen Flow"  # Could also be Autolaunched depending on the use case
        
        # Create comprehensive TestDesigner request
        test_designer_request = TestDesignerRequest(
            flow_name=flow_response.input_request.flow_api_name,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            flow_xml=flow_response.flow_xml,
            flow_type=flow_type,
            target_objects=affected_objects,  # Use affected_objects from user story
            org_alias=state.get("current_auth_request", {}).get("org_alias", "unknown"),
            target_api_version="59.0",
            test_coverage_target=85,
            include_bulk_tests=True,
            include_negative_tests=True,
            include_ui_tests=False,  # Could be enhanced based on flow_type
            business_context=business_context,  # Pass through business context
            existing_test_classes=[]  # Could be enhanced by analyzing org
        )
        
        updated_state = state.copy()
        updated_state["current_test_designer_request"] = test_designer_request.model_dump()
        
        print(f"✅ Prepared comprehensive TestDesigner request:")
        print(f"   Flow: {test_designer_request.flow_name}")
        print(f"   Flow Type: {test_designer_request.flow_type}")
        print(f"   Target Objects: {test_designer_request.target_objects}")
        print(f"   Test Coverage Target: {test_designer_request.test_coverage_target}%")
        print(f"   Include Bulk Tests: {test_designer_request.include_bulk_tests}")
        print(f"   Include Negative Tests: {test_designer_request.include_negative_tests}")
        
        return updated_state
        
    except Exception as e:
        print(f"Error preparing TestDesigner request: {e}")
        return state


def prepare_test_class_deployment_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare deployment request for Apex test classes after successful TestDesigner completion.
    """
    print("\n=== PREPARING TEST CLASS DEPLOYMENT REQUEST ===")
    
    test_designer_response_dict = state.get("current_test_designer_response")
    salesforce_session_dict = state.get("salesforce_session")
    
    if not test_designer_response_dict:
        print("Cannot prepare test class deployment request - no TestDesigner response.")
        return state
    
    if not salesforce_session_dict:
        print("Cannot prepare test class deployment request - no Salesforce session available.")
        return state
    
    try:
        # Convert dict back to Pydantic model for processing
        test_designer_response = TestDesignerResponse(**test_designer_response_dict)
        salesforce_session = SalesforceAuthResponse(**salesforce_session_dict)
        
        if not test_designer_response.success:
            print("Cannot prepare test class deployment request - TestDesigner failed.")
            return state
        
        if not test_designer_response.deployable_apex_code:
            print("Cannot prepare test class deployment request - no deployable Apex code generated.")
            return state
        
        # Create MetadataComponents for each Apex test class
        from src.schemas.deployment_schemas import MetadataComponent
        components = []
        
        for i, apex_code in enumerate(test_designer_response.deployable_apex_code):
            # Extract class name from the Apex code
            class_name = _extract_apex_class_name(apex_code)
            if not class_name:
                class_name = f"TestClass{i+1}"
            
            # Create .cls file component
            cls_component = MetadataComponent(
                component_type="ApexClass",
                api_name=class_name,
                metadata_xml=apex_code,
                directory="classes",
                file_extension="cls"
            )
            components.append(cls_component)
            
            # Create .cls-meta.xml file component
            meta_xml = _create_apex_class_metadata_xml(class_name)
            meta_component = MetadataComponent(
                component_type="ApexClass",
                api_name=class_name,
                metadata_xml=meta_xml,
                directory="classes",
                file_extension="cls-meta.xml"
            )
            components.append(meta_component)
        
        # Create deployment request for test classes
        test_deployment_request = DeploymentRequest(
            request_id=str(uuid.uuid4()),
            components=components,
            salesforce_session=salesforce_session
        )
        
        updated_state = state.copy()
        # Store as separate request to avoid confusion with flow deployment
        updated_state["current_test_deployment_request"] = test_deployment_request.model_dump()
        print(f"Prepared test class deployment request with {len(components)} components")
        
        return updated_state
        
    except Exception as e:
        print(f"Error preparing test class deployment request: {e}")
        return state


def test_class_deployment_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for deploying Apex test classes using the deployment agent.
    """
    print("--- Executing Test Class Deployment Node ---")
    
    # Get the test class deployment request
    test_deployment_request_dict = state.get("current_test_deployment_request")
    
    if not test_deployment_request_dict:
        print("Test Class Deployment: No test deployment request provided.")
        updated_state = state.copy()
        updated_state["current_test_deployment_response"] = {
            "success": False,
            "error_message": "No test deployment request provided",
            "request_id": "unknown"
        }
        return updated_state
    
    try:
        # Convert dict back to Pydantic model
        test_deployment_request = DeploymentRequest(**test_deployment_request_dict)
        
        # Use the same deployment agent but store response separately
        from src.agents.deployment_agent import run_deployment_agent
        
        # Temporarily swap deployment request to deploy test classes
        temp_state = state.copy()
        temp_state["current_deployment_request"] = test_deployment_request_dict
        
        # Run deployment
        result_state = run_deployment_agent(temp_state)
        
        # Extract test deployment response and restore original deployment request
        test_deployment_response = result_state.get("current_deployment_response")
        updated_state = state.copy()
        updated_state["current_test_deployment_response"] = test_deployment_response
        
        # Clear the temporary test deployment request
        updated_state["current_test_deployment_request"] = None
        
        return updated_state
        
    except Exception as e:
        print(f"Test Class Deployment error: {e}")
        updated_state = state.copy()
        updated_state["current_test_deployment_response"] = {
            "success": False,
            "error_message": f"Test class deployment failed: {str(e)}",
            "request_id": test_deployment_request_dict.get("request_id", "unknown")
        }
        updated_state["current_test_deployment_request"] = None
        return updated_state


def _extract_apex_class_name(apex_code: str) -> str:
    """
    Extract the class name from Apex code.
    """
    import re
    
    # Look for "public class ClassName" or "@isTest public class ClassName"
    pattern = r'(?:@isTest\s+)?(?:public|private)\s+class\s+(\w+)'
    match = re.search(pattern, apex_code, re.IGNORECASE)
    
    if match:
        return match.group(1)
    
    return None


def _create_apex_class_metadata_xml(class_name: str, api_version: str = "59.0") -> str:
    """
    Create the metadata XML for an Apex class.
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{api_version}</apiVersion>
    <status>Active</status>
</ApexClass>"""


def should_continue_after_test_designer(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after TestDesigner.
    """
    test_designer_response = state.get("current_test_designer_response")
    
    if test_designer_response and test_designer_response.get("success"):
        deployable_code = test_designer_response.get("deployable_apex_code", [])
        if deployable_code:
            print("✅ TestDesigner successful, proceeding to test class deployment.")
            return "prepare_test_deployment"
        else:
            print("⚠️ TestDesigner successful but no deployable code generated, ending workflow.")
            return END
    else:
        print("❌ TestDesigner failed, ending workflow.")
        if test_designer_response:
            error_message = test_designer_response.get("error_message")
            if error_message:
                print(f"   Error: {error_message}")
        return END


def should_continue_after_test_deployment(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after test class deployment.
    Enhanced with retry logic similar to flow deployment.
    """
    test_deployment_response = state.get("current_test_deployment_response")
    test_deploy_retry_count = state.get("test_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if test_deployment_response and test_deployment_response.get("success"):
        print("✅ Test class deployment successful, workflow complete.")
        return END
    else:
        print(f"❌ Test class deployment failed (attempt #{test_deploy_retry_count + 1})")
        
        # Enhanced test deployment failure logging
        if test_deployment_response:
            error_message = test_deployment_response.get("error_message")
            component_errors = test_deployment_response.get("component_errors", [])
            
            print("📋 TEST DEPLOYMENT FAILURE DETAILS:")
            if error_message:
                print(f"   Main Error: {error_message}")
            
            if component_errors:
                print("   🔍 Specific Component Problems:")
                for i, error in enumerate(component_errors, 1):
                    if isinstance(error, dict):
                        component_type = error.get('componentType', 'Unknown')
                        problem = error.get('problem', 'Unknown error')
                        file_name = error.get('fileName', 'Unknown file')
                        print(f"     {i}. [{component_type}] {problem}")
                        print(f"        File: {file_name}")
                    else:
                        print(f"     {i}. {str(error)}")
            else:
                print("   No specific component error details available")
        
        # Check if we should retry test deployment
        if test_deploy_retry_count < max_retries:
            print(f"🔄 Retrying test deployment ({test_deploy_retry_count + 1}/{max_retries})")
            return "retry_test_deployment"
        else:
            print(f"🛑 Maximum test deployment retries ({max_retries}) reached, ending workflow")
            return END


def record_test_deploy_cycle(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to record test deployment cycle information.
    """
    print("\n=== RECORDING TEST DEPLOYMENT CYCLE ===")
    
    # Increment test deployment retry count
    current_retry_count = state.get("test_deploy_retry_count", 0) + 1
    
    updated_state = state.copy()
    updated_state["test_deploy_retry_count"] = current_retry_count
    
    print(f"📊 Test deployment cycle #{current_retry_count} recorded")
    
    return updated_state


def prepare_retry_test_deployment_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare for a retry attempt after test deployment failure.
    """
    print("\n=== PREPARING RETRY TEST DEPLOYMENT REQUEST ===")
    
    # Get the test deployment failure details
    test_deployment_response = state.get("current_test_deployment_response")
    test_designer_response_dict = state.get("current_test_designer_response")
    
    if test_designer_response_dict and test_deployment_response:
        try:
            test_designer_response = TestDesignerResponse(**test_designer_response_dict)
            
            current_retry_count = state.get("test_deploy_retry_count", 0)
            print(f"🔄 Setting up test deployment retry #{current_retry_count} for test classes")
            
            # For now, we'll just retry with the same test classes
            # Future enhancement: could modify test classes based on deployment errors
            
            # The prepare_test_class_deployment_request function will be called again
            # to recreate the deployment request
            
            updated_state = state.copy()
            # Clear the failed deployment response to trigger fresh preparation
            updated_state["current_test_deployment_request"] = None
            
            print(f"✅ Prepared for test deployment retry #{current_retry_count}")
            
            return updated_state
            
        except Exception as e:
            print(f"Error preparing test deployment retry: {e}")
            return state
    else:
        print("Cannot prepare test deployment retry - missing required data")
        return state


def create_workflow() -> StateGraph:
    """
    Creates and configures the LangGraph workflow with Flow Validation and retry capabilities.
    Enhanced with TestDesigner and test class deployment after successful flow deployment.
    """
    # Create the state graph
    workflow = StateGraph(AgentWorkforceState)
    
    # Add nodes
    workflow.add_node("authentication", authentication_node)
    workflow.add_node("prepare_flow_request", prepare_flow_build_request)
    workflow.add_node("flow_builder", flow_builder_node)
    workflow.add_node("prepare_deployment_request", prepare_deployment_request)
    workflow.add_node("deployment", deployment_node)
    
    # Add web search nodes only if TAVILY_API_KEY is available
    if WEB_SEARCH_AVAILABLE:
        workflow.add_node("prepare_web_search_request", prepare_web_search_request)
        workflow.add_node("web_search", web_search_node)
    
    workflow.add_node("record_cycle", record_build_deploy_cycle)
    workflow.add_node("prepare_retry_flow_request", prepare_retry_flow_request)
    
    # Add TestDesigner and test class deployment nodes
    workflow.add_node("prepare_test_designer_request", prepare_test_designer_request)
    workflow.add_node("test_designer", test_designer_node)
    workflow.add_node("prepare_test_deployment_request", prepare_test_class_deployment_request)
    workflow.add_node("test_deployment", test_class_deployment_node)
    workflow.add_node("record_test_cycle", record_test_deploy_cycle)
    workflow.add_node("prepare_retry_test_deployment_request", prepare_retry_test_deployment_request)
    
    # Set entry point
    workflow.set_entry_point("authentication")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "authentication",
        should_continue_after_auth,
        {
            "flow_builder": "prepare_flow_request",
            END: END
        }
    )
    
    # Add regular edges
    workflow.add_edge("prepare_flow_request", "flow_builder")
    
    # Flow builder -> Deployment preparation (with conditional check)
    workflow.add_conditional_edges(
        "flow_builder",
        should_continue_after_flow_build,
        {
            "prepare_deployment": "prepare_deployment_request",
            END: END
        }
    )
    
    # Deployment preparation and execution
    workflow.add_edge("prepare_deployment_request", "deployment")
    
    # Add edge to record cycle after deployment
    workflow.add_edge("deployment", "record_cycle")
    
    # Add conditional edges for retry logic after recording the cycle (deployment failures)
    # Updated to route to TestDesigner on successful deployment
    if WEB_SEARCH_AVAILABLE:
        # With web search: deployment failures -> search for solutions -> retry
        # Successful deployment -> TestDesigner
        workflow.add_conditional_edges(
            "record_cycle",
            should_continue_after_deployment,
            {
                "test_designer": "prepare_test_designer_request",
                "search_for_solutions": "prepare_web_search_request",
                END: END
            }
        )
        
        # Web search flow: prepare search -> execute search -> prepare retry
        workflow.add_edge("prepare_web_search_request", "web_search")
        workflow.add_edge("web_search", "prepare_retry_flow_request")
    else:
        # Without web search: deployment failures -> direct retry
        # Successful deployment -> TestDesigner
        workflow.add_conditional_edges(
            "record_cycle",
            should_continue_after_deployment,
            {
                "test_designer": "prepare_test_designer_request",
                "direct_retry": "prepare_retry_flow_request",
                END: END
            }
        )
    
    # Add edge from deployment retry preparation back to flow builder
    workflow.add_edge("prepare_retry_flow_request", "flow_builder")
    
    # Add TestDesigner workflow edges
    workflow.add_edge("prepare_test_designer_request", "test_designer")
    
    # TestDesigner -> Test class deployment (with conditional check)
    workflow.add_conditional_edges(
        "test_designer",
        should_continue_after_test_designer,
        {
            "prepare_test_deployment": "prepare_test_deployment_request",
            END: END
        }
    )
    
    # Test class deployment preparation and execution
    workflow.add_edge("prepare_test_deployment_request", "test_deployment")
    
    # Add edge to record test deployment cycle
    workflow.add_edge("test_deployment", "record_test_cycle")
    
    # Add conditional edges for test deployment retry logic
    workflow.add_conditional_edges(
        "record_test_cycle",
        should_continue_after_test_deployment,
        {
            "retry_test_deployment": "prepare_retry_test_deployment_request",
            END: END
        }
    )
    
    # Add edge from test deployment retry preparation back to test deployment preparation
    workflow.add_edge("prepare_retry_test_deployment_request", "prepare_test_deployment_request")
    
    return workflow


def run_workflow(org_alias: str, project_name: str = "salesforce-agent-workforce") -> Dict[str, Any]:
    """
    Runs the complete workflow for the given Salesforce org alias with retry capabilities.
    
    Args:
        org_alias: The Salesforce org alias to authenticate to
        project_name: LangSmith project name for tracing
        
    Returns:
        Final state of the workflow
    """
    print(f"\n🚀 Starting Salesforce Agent Workforce for org: {org_alias}")
    print(f"🔄 Retry configuration: max_retries={MAX_BUILD_DEPLOY_RETRIES}")
    print("=" * 60)
    
    # Create authentication request
    auth_request = AuthenticationRequest(org_alias=org_alias)
    
    # Initialize the workflow state with simple retry capabilities
    initial_state: AgentWorkforceState = {
        "current_auth_request": auth_request.model_dump(),  # Convert to dict
        "current_auth_response": None,
        "is_authenticated": False,
        "salesforce_session": None,
        "current_flow_build_request": None,
        "current_flow_build_response": None,
        "current_deployment_request": None,
        "current_deployment_response": None,
        # TestDesigner related state
        "current_test_designer_request": None,
        "current_test_designer_response": None,
        "test_scenarios": None,
        "apex_test_classes": None,
        "deployable_apex_code": None,
        # Test class deployment state
        "current_test_deployment_request": None,
        "current_test_deployment_response": None,
        # Web search related state
        "current_web_search_request": None,
        "current_web_search_response": None,
        "messages": [],
        "error_message": None,
        "retry_count": 0,
        # Simple retry-related fields
        "build_deploy_retry_count": 0,
        "max_build_deploy_retries": MAX_BUILD_DEPLOY_RETRIES,
        # Test deployment retry fields
        "test_deploy_retry_count": 0
    }
    
    # Create and compile the workflow
    workflow = create_workflow()
    app = workflow.compile()
    
    # Configure LangSmith tracing if available
    config = {}
    if langsmith_client:
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            },
            "tags": ["salesforce-agent-workforce", "retry-enabled-workflow"],
            "metadata": {
                "org_alias": org_alias,
                "workflow_type": "retry_enabled",
                "max_retries": MAX_BUILD_DEPLOY_RETRIES,
                "version": "2.0"
            },
            "recursion_limit": RECURSION_LIMIT
        }
    else:
        config = {
            "recursion_limit": RECURSION_LIMIT
        }
    
    try:
        # Run the workflow
        print("Executing workflow with retry capabilities...")
        final_state = app.invoke(initial_state, config=config)
        
        print("\n" + "=" * 60)
        print("🏁 WORKFLOW COMPLETED")
        print("=" * 60)
        
        # Print summary
        print_workflow_summary(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {e}")
        return {"error": str(e), "final_state": initial_state}


def print_workflow_summary(final_state: AgentWorkforceState) -> None:
    """
    Prints a simplified summary of the workflow execution.
    """
    print("\n📊 WORKFLOW SUMMARY:")
    print("-" * 40)
    
    # Simple retry information
    build_deploy_retry_count = final_state.get("build_deploy_retry_count", 0)
    test_deploy_retry_count = final_state.get("test_deploy_retry_count", 0)
    max_retries = final_state.get("max_build_deploy_retries", 0)
    
    if build_deploy_retry_count > 0:
        print(f"🔄 Flow Retry attempts: {build_deploy_retry_count}/{max_retries}")
    
    if test_deploy_retry_count > 0:
        print(f"🔄 Test Deployment Retry attempts: {test_deploy_retry_count}/{max_retries}")
    
    # Authentication status
    auth_response_dict = final_state.get("current_auth_response")
    if final_state.get("is_authenticated", False):
        print("✅ Authentication: SUCCESS")
        if auth_response_dict:
            try:
                auth_response = SalesforceAuthResponse(**auth_response_dict)
                print(f"   Org ID: {auth_response.org_id}")
                print(f"   Instance URL: {auth_response.instance_url}")
            except Exception:
                print("   (Could not parse auth response details)")
    else:
        print("❌ Authentication: FAILED")
        if auth_response_dict:
            try:
                auth_response = SalesforceAuthResponse(**auth_response_dict)
                if auth_response.error_message:
                    print(f"   Error: {auth_response.error_message}")
            except Exception:
                print("   (Could not parse auth response details)")
    
    # Flow building status
    flow_response_dict = final_state.get("current_flow_build_response")
    if flow_response_dict:
        try:
            flow_response = FlowBuildResponse(**flow_response_dict)
            if flow_response.success:
                print("✅ Flow Building: SUCCESS")
                print(f"   Flow Name: {flow_response.input_request.flow_api_name}")
                print(f"   Flow Label: {flow_response.input_request.flow_label}")
            else:
                print("❌ Flow Building: FAILED")
                if flow_response.error_message:
                    print(f"   Error: {flow_response.error_message}")
        except Exception:
            print("❌ Flow Building: FAILED (Could not parse response)")
    else:
        print("⏭️  Flow Building: SKIPPED")
    
    # Deployment status
    deployment_response_dict = final_state.get("current_deployment_response")
    if deployment_response_dict:
        try:
            deployment_response = DeploymentResponse(**deployment_response_dict)
            if deployment_response.success:
                print("✅ Flow Deployment: SUCCESS")
                print(f"   Deployment ID: {deployment_response.deployment_id}")
                print(f"   Status: {deployment_response.status}")
                if build_deploy_retry_count > 0:
                    print(f"   🎯 Succeeded after {build_deploy_retry_count} retry(ies)")
            else:
                print("❌ Flow Deployment: FAILED")
                print(f"   Status: {deployment_response.status}")
                if deployment_response.error_message:
                    print(f"   Error: {deployment_response.error_message}")
                if build_deploy_retry_count >= max_retries:
                    print(f"   🛑 Maximum retries ({max_retries}) exhausted")
        except Exception:
            print("❌ Flow Deployment: FAILED (Could not parse response)")
    else:
        print("⏭️  Flow Deployment: SKIPPED")
    
    # TestDesigner status
    test_designer_response_dict = final_state.get("current_test_designer_response")
    if test_designer_response_dict:
        try:
            test_designer_response = TestDesignerResponse(**test_designer_response_dict)
            if test_designer_response.success:
                print("✅ TestDesigner: SUCCESS")
                print(f"   Test Scenarios: {len(test_designer_response.test_scenarios)}")
                print(f"   Apex Test Classes: {len(test_designer_response.apex_test_classes)}")
                print(f"   Deployable Code Files: {len(test_designer_response.deployable_apex_code)}")
            else:
                print("❌ TestDesigner: FAILED")
                if test_designer_response.error_message:
                    print(f"   Error: {test_designer_response.error_message}")
        except Exception:
            print("❌ TestDesigner: FAILED (Could not parse response)")
    else:
        print("⏭️  TestDesigner: SKIPPED")
    
    # Test Class Deployment status
    test_deployment_response_dict = final_state.get("current_test_deployment_response")
    if test_deployment_response_dict:
        try:
            test_deployment_response = DeploymentResponse(**test_deployment_response_dict)
            if test_deployment_response.success:
                print("✅ Test Class Deployment: SUCCESS")
                print(f"   Deployment ID: {test_deployment_response.deployment_id}")
                print(f"   Status: {test_deployment_response.status}")
                if test_deploy_retry_count > 0:
                    print(f"   🎯 Succeeded after {test_deploy_retry_count} retry(ies)")
            else:
                print("❌ Test Class Deployment: FAILED")
                print(f"   Status: {test_deployment_response.status}")
                if test_deployment_response.error_message:
                    print(f"   Error: {test_deployment_response.error_message}")
                if test_deploy_retry_count >= max_retries:
                    print(f"   🛑 Maximum retries ({max_retries}) exhausted")
        except Exception:
            print("❌ Test Class Deployment: FAILED (Could not parse response)")
    else:
        print("⏭️  Test Class Deployment: SKIPPED")
        
    # General errors
    if final_state.get("error_message"):
        print(f"\n⚠️  General Error: {final_state['error_message']}")
    
    print("-" * 40)


if __name__ == "__main__":
    """
    CLI interface for running the workflow.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/main_orchestrator.py <org_alias>")
        print("Example: python src/main_orchestrator.py MYSANDBOX")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    try:
        final_state = run_workflow(org_alias)
        
        # Exit with appropriate code
        if final_state.get("error"):
            sys.exit(1)
        elif not final_state.get("is_authenticated", False):
            sys.exit(1)
        elif final_state.get("current_deployment_response") and not final_state["current_deployment_response"].get("success"):
            sys.exit(1)
        elif final_state.get("current_test_deployment_response") and not final_state["current_test_deployment_response"].get("success"):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 