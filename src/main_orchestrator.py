import os
import uuid
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, List

# Suppress Pydantic v1/v2 mixing warnings from LangChain internals
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")
warnings.filterwarnings("ignore", message=".*Cannot generate a JsonSchema for core_schema.PlainValidatorFunctionSchema.*")

from dotenv import load_dotenv
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
from src.config import get_llm, get_all_agent_configs

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Check if web search is available
WEB_SEARCH_AVAILABLE = bool(os.getenv("TAVILY_API_KEY"))
if WEB_SEARCH_AVAILABLE:
    print("✅ Web search enabled (TAVILY_API_KEY found)")
else:
    print("⚠️ Web search disabled (TAVILY_API_KEY not found)")

# Display AI Provider Configuration
print("\n=== AI PROVIDER CONFIGURATION ===")
all_configs = get_all_agent_configs()
for agent_name, config in all_configs.items():
    status = "✅" if config["api_key_set"] else "❌"
    print(f"{status} {agent_name.upper()}: {config['provider']} | {config['model']} | {config['max_tokens']} tokens")

# Initialize LLM with global configuration for orchestrator
LLM = get_llm(temperature=0)
print(f"\nOrchestrator LLM: {all_configs['global']['provider']} | {all_configs['global']['model']}")

# Initialize retry configuration
MAX_BUILD_DEPLOY_RETRIES = int(os.getenv("MAX_BUILD_DEPLOY_RETRIES", "3"))
# Initialize recursion limit configuration
RECURSION_LIMIT = int(os.getenv("LANGGRAPH_RECURSION_LIMIT", "50"))

# Initialize LangSmith client for tracing
try:
    langsmith_client = LangSmithClient()
    print("✅ LangSmith client initialized successfully.")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize LangSmith client: {e}")
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
        # Get Flow Builder specific LLM configuration
        flow_builder_llm = get_llm(agent_name="FLOW_BUILDER", temperature=0.1)
        return run_enhanced_flow_builder_agent(state, flow_builder_llm)
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
        # Get Deployment Agent specific LLM configuration
        deployment_llm = get_llm(agent_name="DEPLOYMENT", temperature=0)
        return run_deployment_agent(state, deployment_llm)
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
    Updated to support skip_test_design_deployment flag for direct flow building.
    """
    if state.get("is_authenticated", False):
        # Check if user wants to skip test design/deployment and go directly to flow building
        skip_tests = state.get("skip_test_design_deployment", False)
        
        if skip_tests:
            print("Authentication successful, skipping test design/deployment and proceeding directly to Flow Builder.")
            return "flow_builder"
        else:
            print("Authentication successful, proceeding to TestDesigner (TDD approach).")
            return "test_designer"
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
    Conditional edge function to determine workflow continuation after Flow deployment.
    Updated for TDD approach: after successful deployment, we're done (tests already exist).
    """
    deployment_response = state.get("current_deployment_response")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if deployment_response and deployment_response.get("success"):
        print("✅ Flow deployment successful! TDD cycle complete - tests and Flow are both deployed.")
        return END
    else:
        print(f"❌ Flow deployment failed (attempt #{build_deploy_retry_count + 1})")
        
        # Enhanced deployment failure logging
        if deployment_response:
            error_message = deployment_response.get("error_message")
            component_errors = deployment_response.get("component_errors", [])
            
            print("📋 DEPLOYMENT FAILURE DETAILS:")
            if error_message:
                print(f"   Main Error: {error_message}")
            
            if component_errors:
                print(f"   🔍 Component Error Summary:")
                for error in component_errors[:2]:  # Show first 2 errors to keep it concise
                    if isinstance(error, dict):
                        problem = error.get('problem', 'Unknown error')
                        # Truncate long error messages for summary
                        if len(problem) > 80:
                            problem = problem[:77] + "..."
                        print(f"      - {problem}")
        
        # Check if we should retry
        if build_deploy_retry_count < max_retries:
            print(f"🔄 Retrying build/deploy cycle ({build_deploy_retry_count + 1}/{max_retries})")
            
            # FIXED: Always use direct retry - web search is disabled
            print("🔄 Retrying Flow build directly (web search disabled)")
            return "direct_retry"
        else:
            print("❌ Flow deployment failed after max retries, ending workflow.")
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
    Enhanced to provide dynamic error analysis with reasoning prompts for the LLM.
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
            
            # Analyze the deployment error for dynamic reasoning
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
                        
                        # Add web search insights to reasoning prompts
                        if web_search_response.recommendations:
                            print("   💡 Adding web search recommendations to reasoning context:")
                            for i, rec in enumerate(web_search_response.recommendations[:3], 1):
                                print(f"      {i}. {rec}")
                                error_analysis["reasoning_prompts"].append(f"Web Search Insight: {rec}")
                    else:
                        print("⚠️ Web search was attempted but didn't return useful results")
                        web_search_insights = {"search_attempted": True, "search_successful": False}
                except Exception as e:
                    print(f"⚠️ Error processing web search results: {e}")
                    web_search_insights = {"search_attempted": True, "processing_error": str(e)}
            else:
                print("ℹ️ No web search results available for this retry")
            
            # Enhanced retry context with dynamic analysis and reasoning prompts
            retry_context = {
                "is_retry": True,
                "retry_attempt": current_retry_count,
                "original_flow_xml": last_build_response.flow_xml,
                "deployment_error": deployment_response.get("error_message", "Unknown error"),
                "component_errors": deployment_response.get("component_errors", []),
                "deployment_errors": deployment_response.get("component_errors", []),  # For RAG compatibility
                "validation_errors": [],  # Will be filled if validation also fails
                "error_analysis": error_analysis,
                "reasoning_prompts": error_analysis["reasoning_prompts"],
                "error_type": error_analysis["error_type"],
                "error_category": error_analysis["error_category"],
                "general_error_pattern": error_analysis["dynamic_context"].get("general_error_pattern", "Unknown"),
                "specific_fixes_needed": error_analysis.get("specific_fixes_needed", []),
                "previous_attempts_summary": _get_previous_attempts_summary(state, current_retry_count)
            }
            
            # Add web search insights if available
            if web_search_insights:
                retry_context["web_search_insights"] = web_search_insights
                print("✅ Web search insights integrated into retry context")
            
            retry_request = original_request.model_copy()
            retry_request.retry_context = retry_context
            
            # Enhanced failure analysis logging with dynamic understanding
            print(f"🔧 Dynamic error analysis completed:")
            print(f"   📊 Error Classification:")
            print(f"      Error Type: {error_analysis['error_type']}")
            print(f"      Error Category: {error_analysis['error_category']}")
            print(f"      Severity Level: {error_analysis['severity']}")
            print(f"      General Pattern: {error_analysis['dynamic_context'].get('general_error_pattern', 'Unknown')}")
            
            # Show reasoning prompts that will guide the LLM
            reasoning_prompts = error_analysis['reasoning_prompts']
            print(f"   🧠 LLM Reasoning Prompts: {len(reasoning_prompts)} prompts provided")
            if reasoning_prompts:
                print(f"      The LLM will be guided to:")
                for i, prompt in enumerate(reasoning_prompts[:4], 1):  # Show first 4 prompts
                    print(f"      {i}. {prompt}")
                if len(reasoning_prompts) > 4:
                    print(f"      ... and {len(reasoning_prompts) - 4} more reasoning prompts")
            
            # Show error patterns detected
            if error_analysis['error_patterns']:
                print(f"   🔍 Error Patterns Detected: {', '.join(error_analysis['error_patterns'])}")
            
            # Show dynamic context available to the LLM
            dynamic_context = error_analysis['dynamic_context']
            if 'xsd_type' in dynamic_context:
                print(f"   🏷️  XSD Type Context: {dynamic_context['xsd_type']}")
            
            updated_state = state.copy()
            updated_state["current_flow_build_request"] = retry_request.model_dump()
            updated_state["build_deploy_retry_count"] = current_retry_count
            
            # Clear the web search response after processing
            updated_state["current_web_search_response"] = None
            
            print(f"✅ Enhanced retry request prepared - attempt #{current_retry_count}")
            print(f"   🧠 LLM will use {len(reasoning_prompts)} reasoning prompts to fix the {error_analysis['error_type']} error")
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
    Analyze deployment errors to extract error types and patterns for dynamic LLM reasoning.
    Focus on error categories, not specific variable names or hardcoded fixes.
    """
    analysis = {
        "error_type": "unknown",
        "severity": "medium", 
        "error_category": "unknown",
        "error_patterns": [],
        "dynamic_context": {},
        "reasoning_prompts": [],
        "specific_fixes_needed": []
    }
    
    error_text = error_message.lower() if error_message else ""
    
    # Collect all error text for analysis
    all_error_text = error_text
    component_problems = []
    for error in component_errors:
        if isinstance(error, dict):
            problem = error.get("problem", "")
            component_problems.append(problem)
            all_error_text += " " + problem.lower()
    
    # Dynamic error type detection - focus on patterns, not specific content
    
    # XSD Type Validation Errors (most common pattern from the logs)
    if "is not valid for the type xsd:" in all_error_text:
        analysis["error_type"] = "xsd_type_validation"
        analysis["error_category"] = "data_type_mismatch"
        analysis["severity"] = "high"
        
        # Extract the specific XSD type that failed
        import re
        xsd_type_match = re.search(r"xsd:(\w+)", all_error_text)
        if xsd_type_match:
            xsd_type = xsd_type_match.group(1)
            analysis["dynamic_context"]["xsd_type"] = xsd_type
            analysis["dynamic_context"]["general_error_pattern"] = f"Variable reference not valid for xsd:{xsd_type} type"
        
        analysis["reasoning_prompts"] = [
            f"Analyze the error: a value is not valid for an XSD type. This typically means variable references or expressions are being used where literal values are expected.",
            f"Look for patterns like {{!VariableName}} being used in fields that expect literal values.",
            f"Consider the Flow XML structure and how to properly reference variables vs. provide literal values.",
            f"Think about what the XSD type expects (numeric, text, boolean) and ensure the value matches that format."
        ]
        
        analysis["error_patterns"].append("XSD_TYPE_VALIDATION_ERROR")
    
    # Flow Element Reference Errors
    elif "invalid flow element" in all_error_text or "unknown element" in all_error_text or "invalid reference" in all_error_text:
        analysis["error_type"] = "invalid_element_reference"
        analysis["error_category"] = "structural_reference"
        analysis["severity"] = "high"
        
        analysis["dynamic_context"]["general_error_pattern"] = "Flow references elements that don't exist or are incorrectly referenced"
        analysis["reasoning_prompts"] = [
            "CRITICAL: The Flow is referencing elements that don't exist or are incorrectly named.",
            "Common issue: Using elementName.Count instead of just elementName for Get Records elements.",
            "Check that all element references match the actual element names defined in the Flow.",
            "For Get Records elements: Reference the element name directly, not elementName.Count.",
            "Example: If element is named 'Get_Contact_Count', reference it as 'Get_Contact_Count', not 'Get_Contact_Count.Count'.",
            "Verify element names are consistent throughout the Flow (case-sensitive).",
            "Ensure all referenced elements are actually defined in the Flow XML."
        ]
        
        analysis["error_patterns"].append("INVALID_ELEMENT_REFERENCE")
        
        # Extract the specific invalid reference if possible
        import re
        invalid_ref_match = re.search(r'invalid reference to "([^"]+)"', error_message) if error_message else None
        if invalid_ref_match:
            invalid_ref = invalid_ref_match.group(1)
            analysis["dynamic_context"]["invalid_reference"] = invalid_ref
            
            # Add specific guidance based on the invalid reference pattern
            analysis["specific_fixes_needed"] = [
                f"Fix the invalid reference to '{invalid_ref}'",
                "Check if the element name exists in the Flow",
                "Verify the reference syntax is correct (no extra .Count or .Field suffixes unless needed)",
                "Ensure element names match exactly (case-sensitive)"
            ]
            
            # Specific guidance for common patterns
            if ".Count" in invalid_ref:
                analysis["specific_fixes_needed"].append(
                    f"Remove '.Count' suffix - reference the element directly as '{invalid_ref.replace('.Count', '')}'"
                )
        else:
            analysis["specific_fixes_needed"] = [
                "Review all element references in the Flow",
                "Ensure referenced elements are defined in the Flow",
                "Check element naming consistency (case-sensitive)",
                "Verify reference syntax is correct"
            ]
    
    # Formula Expression Errors  
    elif "formula expression is invalid" in all_error_text:
        analysis["error_type"] = "invalid_formula"
        analysis["error_category"] = "expression_syntax"
        analysis["severity"] = "high"
        
        analysis["dynamic_context"]["general_error_pattern"] = "Formula expressions have syntax or reference errors"
        analysis["reasoning_prompts"] = [
            "Analyze the error: a formula expression is malformed or references invalid elements.",
            "Review formula syntax and ensure all referenced elements exist in the Flow.",
            "Check for proper Flow formula syntax and valid element references.",
            "Consider if the formula logic needs to be restructured or simplified."
        ]
        
        analysis["error_patterns"].append("INVALID_FORMULA_EXPRESSION")
        analysis["specific_fixes_needed"] = [
            "Review all formula expressions in the Flow",
            "Check formula syntax for proper operators and functions",
            "Verify all referenced elements exist in the Flow",
            "Ensure formula return types match expected data types"
        ]
    
    # Collection Variable Assignment Errors
    elif "inputassignments field can't use a collection variable" in all_error_text:
        analysis["error_type"] = "collection_variable_misuse"
        analysis["error_category"] = "variable_usage"
        analysis["severity"] = "high"
        
        analysis["dynamic_context"]["general_error_pattern"] = "Collection variables used incorrectly in assignments"
        analysis["reasoning_prompts"] = [
            "CRITICAL FIX: Collection variables CANNOT be used in inputAssignments fields.",
            "Look for any <inputAssignments> elements that reference collection variables.",
            "Replace collection variable references with individual record variables in assignments.",
            "Use collection variables only as outputs from Get Records or inputs to Create/Update Records (not in field assignments).",
            "For counting records: Use the collection variable directly to get its size, not in inputAssignments.",
            "Pattern: Get Records -> outputReference to collection variable -> reference collection size in formulas.",
            "NEVER use collection variables in individual field value assignments."
        ]
        
        analysis["error_patterns"].append("COLLECTION_VARIABLE_MISUSE")
        
        # Add specific guidance for this error type
        analysis["specific_fixes_needed"] = [
            "Remove all collection variable references from inputAssignments elements",
            "Use individual record variables for field assignments instead of collections",
            "If counting records, reference the collection variable directly (not in assignments)",
            "Ensure Get Records uses outputReference for collection, not inputAssignments"
        ]
    
    # API Name/Naming Convention Errors
    elif "invalid name" in all_error_text or "name" in all_error_text and "invalid" in all_error_text:
        analysis["error_type"] = "naming_convention"
        analysis["error_category"] = "metadata_compliance"
        analysis["severity"] = "medium"
        
        analysis["dynamic_context"]["general_error_pattern"] = "Element names don't follow Salesforce naming conventions"
        analysis["reasoning_prompts"] = [
            "Analyze the error: element names violate Salesforce naming conventions.",
            "Check that all API names are alphanumeric, start with letters, and contain no spaces or special characters.",
            "Review Flow element names, variable names, and screen field names for compliance.",
            "Consider standardizing naming patterns across the Flow."
        ]
        
        analysis["error_patterns"].append("NAMING_CONVENTION_ERROR")
        analysis["specific_fixes_needed"] = [
            "Review all API names in the Flow for compliance",
            "Ensure API names are alphanumeric and start with a letter",
            "Remove spaces, hyphens, and special characters from names",
            "Use camelCase or underscore_case naming conventions"
        ]
    
    # Duplicate Element Errors
    elif "duplicate" in all_error_text or "duplicated" in all_error_text:
        analysis["error_type"] = "duplicate_elements"
        analysis["error_category"] = "structural_integrity"
        analysis["severity"] = "high"
        
        # Extract the specific element type that's duplicated
        import re
        duplicate_element_match = re.search(r"element (\w+) is duplicated", all_error_text, re.IGNORECASE)
        if not duplicate_element_match:
            duplicate_element_match = re.search(r"duplicate.*?(\w+)", all_error_text, re.IGNORECASE)
        
        duplicated_element = duplicate_element_match.group(1) if duplicate_element_match else "element"
        
        analysis["dynamic_context"]["duplicated_element"] = duplicated_element
        analysis["dynamic_context"]["general_error_pattern"] = f"Duplicate {duplicated_element} elements found in Flow XML"
        
        analysis["reasoning_prompts"] = [
            f"CRITICAL: The Flow XML contains duplicate {duplicated_element} elements.",
            f"Look for multiple {duplicated_element} elements with the same name or structure.",
            f"Salesforce Flow metadata requires unique element names within each element type.",
            f"Review the Flow XML structure to identify and remove duplicate {duplicated_element} elements.",
            f"Ensure each {duplicated_element} element has a unique name within the Flow.",
            f"Check if elements were accidentally duplicated during generation or editing.",
            f"Consolidate duplicate logic into a single {duplicated_element} element if possible."
        ]
        
        analysis["error_patterns"].append("DUPLICATE_ELEMENTS_ERROR")
        analysis["specific_fixes_needed"] = [
            f"Identify and remove duplicate {duplicated_element} elements",
            f"Ensure all {duplicated_element} elements have unique names",
            f"Review Flow XML structure for any accidental element duplication",
            f"Consolidate duplicate logic if multiple {duplicated_element} elements serve the same purpose",
            f"Validate that each element type maintains unique naming within the Flow"
        ]
    
    # XML Structure/Syntax Errors
    elif "xml" in all_error_text or "malformed" in all_error_text or "parsing" in all_error_text:
        analysis["error_type"] = "xml_structure"
        analysis["error_category"] = "syntax_error"
        analysis["severity"] = "critical"
        
        analysis["dynamic_context"]["general_error_pattern"] = "XML syntax or structure is malformed"
        analysis["reasoning_prompts"] = [
            "Analyze the error: the XML structure is malformed or doesn't follow the expected schema.",
            "Check for missing closing tags, incorrect nesting, or invalid XML syntax.",
            "Ensure the Flow XML follows the Salesforce Flow metadata format.",
            "Verify that all required XML elements and attributes are present and correctly formatted."
        ]
        
        analysis["error_patterns"].append("XML_STRUCTURE_ERROR")
        analysis["specific_fixes_needed"] = [
            "Check XML syntax for proper opening and closing tags",
            "Verify XML element nesting follows Salesforce Flow schema",
            "Ensure all required Flow XML elements are present",
            "Validate XML formatting and special character encoding"
        ]
    
    # General catch-all for unclassified errors
    else:
        analysis["error_type"] = "general_deployment_failure"
        analysis["error_category"] = "unknown"
        analysis["dynamic_context"]["general_error_pattern"] = "Deployment failed for unspecified reasons"
        analysis["reasoning_prompts"] = [
            "Analyze the deployment error carefully to understand the root cause.",
            "Look for patterns in the error message that indicate what needs to be fixed.",
            "Consider common Salesforce Flow deployment issues and best practices.",
            "Review the Flow XML structure for any obvious problems or inconsistencies."
        ]
        analysis["error_patterns"].append("GENERAL_DEPLOYMENT_ERROR")
        analysis["specific_fixes_needed"] = [
            "Review the complete error message for clues about the issue",
            "Check Flow XML structure against Salesforce Flow schema",
            "Verify all Flow elements are properly configured",
            "Ensure compliance with Salesforce Flow best practices"
        ]
    
    # Add the actual error details for LLM context
    analysis["dynamic_context"]["original_error_message"] = error_message
    analysis["dynamic_context"]["component_problems"] = component_problems
    
    # Add generic reasoning guidance
    analysis["reasoning_prompts"].append(
        "Remember: Focus on understanding the error pattern and applying the appropriate fix to the specific context in this Flow."
    )
    
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
    Enhanced to search for ERROR TYPES, not specific variable names.
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
    
    # Analyze the error to get the type, not specific details
    error_analysis = _analyze_deployment_error(error_message, component_errors, "")
    error_type = error_analysis.get("error_type", "unknown")
    error_category = error_analysis.get("error_category", "unknown")
    
    # Create search query based on ERROR TYPE, not specific variable names
    base_query = "Salesforce Flow deployment error"
    
    if error_type == "xsd_type_validation":
        # Search for general XSD type validation issues, not specific variable names
        xsd_type = error_analysis.get("dynamic_context", {}).get("xsd_type", "double")
        search_query = f"Salesforce Flow xsd:{xsd_type} type validation error deployment fix"
    elif error_type == "invalid_element_reference":
        search_query = "Salesforce Flow invalid element reference deployment error troubleshooting"
    elif error_type == "invalid_formula":
        search_query = "Salesforce Flow invalid formula expression deployment error fix"
    elif error_type == "collection_variable_misuse":
        search_query = "Salesforce Flow collection variable inputAssignments deployment error"
    elif error_type == "naming_convention":
        search_query = "Salesforce Flow invalid name deployment error naming conventions"
    elif error_type == "duplicate_elements":
        # Search for specific duplicate element issues
        duplicated_element = error_analysis.get("dynamic_context", {}).get("duplicated_element", "element")
        search_query = f"Salesforce Flow duplicate {duplicated_element} element deployment error troubleshooting"
    elif error_type == "xml_structure":
        search_query = "Salesforce Flow XML parsing deployment error malformed structure"
    else:
        # Fallback to general deployment troubleshooting
        search_query = "Salesforce Flow deployment error troubleshooting guide best practices"
    
    print(f"Prepared web search for ERROR TYPE: '{error_type}' -> query: '{search_query}'")
    
    # Create enhanced search request focused on error TYPE patterns
    search_request = WebSearchRequest(
        query=search_query,
        max_results=8,
        search_depth=SearchDepth.ADVANCED,
        include_domains=['salesforce.com', 'trailhead.salesforce.com', 'developer.salesforce.com', 'help.salesforce.com'],
        exclude_domains=None,
        include_answer=True,
        include_raw_content=False,
        topic='salesforce_flows'
    )
    
    # Enhanced context focusing on the ERROR TYPE for better LLM reasoning
    search_context = f"""
    We are experiencing a Salesforce Flow deployment failure during retry attempt #{build_deploy_retry_count}.
    
    Error Type: {error_type}
    Error Category: {error_category}
    General Pattern: {error_analysis.get('dynamic_context', {}).get('general_error_pattern', 'Unknown')}
    
    Main Error: {error_message}
    
    Component Errors: {component_errors}
    
    We need to find general solutions and patterns for this TYPE of deployment error that the LLM can reason about and apply to our specific context.
    """
    
    # Instructions focused on finding PATTERNS, not specific fixes
    agent_instructions = """
    Focus on finding:
    1. General patterns and causes for this type of error
    2. Conceptual solutions that can be applied to different scenarios
    3. Salesforce documentation about the error type and category
    4. Best practices for avoiding this category of error
    5. Troubleshooting approaches that work across different contexts
    
    DO NOT focus on:
    - Specific variable names or Flow names
    - Exact code snippets that may not apply to our context
    - Solutions tied to particular use cases
    
    Prioritize official Salesforce documentation and general troubleshooting guidance.
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
    Also updates the Flow Builder memory with deployment results.
    """
    print("\n=== RECORDING BUILD/DEPLOY CYCLE - ENHANCED ===")
    
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    deployment_response = state.get("current_deployment_response")
    flow_build_response_dict = state.get("current_flow_build_response")
    
    # Update Flow Builder memory with deployment results
    if flow_build_response_dict and deployment_response:
        try:
            from .agents.enhanced_flow_builder_agent import EnhancedFlowBuilderAgent
            
            flow_build_response = FlowBuildResponse(**flow_build_response_dict)
            flow_api_name = flow_build_response.input_request.flow_api_name
            
            # Load persisted memory data from state
            persisted_memory_data = state.get("flow_builder_memory_data", {})
            
            # Create agent instance to update memory
            memory_agent = EnhancedFlowBuilderAgent(LLM, persisted_memory_data)
            
            # Determine the attempt number
            retry_attempt = flow_build_response.input_request.retry_context.get('retry_attempt', 1) if flow_build_response.input_request.retry_context else 1
            
            # Update memory with deployment result
            deployment_success = deployment_response.get("success", False)
            deployment_errors = deployment_response.get("component_errors", [])
            error_message = deployment_response.get("error_message", "")
            
            memory_agent.update_memory_with_deployment_result(
                flow_api_name=flow_api_name,
                attempt_number=retry_attempt,
                deployment_success=deployment_success,
                deployment_errors=deployment_errors,
                error_message=error_message
            )
            
            # Save updated memory back to state
            updated_memory_data = memory_agent.get_memory_data_for_persistence()
            state = state.copy()
            state["flow_builder_memory_data"] = updated_memory_data
            
            status_msg = "SUCCESS" if deployment_success else "FAILED"
            print(f"🧠 MEMORY: Updated Flow Builder memory with deployment result ({status_msg})")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not update Flow Builder memory with deployment result: {e}")
    
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
    Enhanced for TDD approach: includes test scenarios and deployed test classes as context.
    This creates a flow request that uses test information to understand what needs to be built.
    """
    print("\n=== PREPARING FLOW BUILD REQUEST (TDD APPROACH) ===")
    
    if not state.get("is_authenticated", False):
        print("Cannot prepare flow build request - not authenticated.")
        return state
    
    # TDD Enhancement: Get test information for Flow context
    test_scenarios = state.get("test_scenarios")
    apex_test_classes = state.get("apex_test_classes")
    test_designer_response = state.get("current_test_designer_response")
    
    tdd_context = None
    if test_scenarios or apex_test_classes:
        print("🧪 TDD Context Available: Using test information to guide Flow building")
        tdd_context = {
            "test_scenarios": test_scenarios,
            "apex_test_classes": apex_test_classes,
            "test_designer_response": test_designer_response,
            "approach": "test_driven_development"
        }
        
        if test_scenarios:
            print(f"   📋 Test Scenarios: {len(test_scenarios)} scenarios found")
            for i, scenario in enumerate(test_scenarios[:3], 1):  # Show first 3
                scenario_name = scenario.get("name", f"Scenario {i}")
                print(f"      {i}. {scenario_name}")
            if len(test_scenarios) > 3:
                print(f"      ... and {len(test_scenarios) - 3} more scenarios")
        
        if apex_test_classes:
            print(f"   🧪 Apex Test Classes: {len(apex_test_classes)} classes deployed")
            for i, test_class in enumerate(apex_test_classes[:2], 1):  # Show first 2
                class_name = test_class.get("class_name", f"TestClass{i}")
                method_count = len(test_class.get("test_methods", []))
                print(f"      {i}. {class_name} ({method_count} test methods)")
    else:
        print("⚠️  No test context available - proceeding without TDD guidance")
    
    # Check if user story and acceptance criteria are provided in the state
    user_story_data = state.get("user_story")
    
    if user_story_data:
        print("Found user story in state, creating flow request from user requirements...")
        
        # Import here to avoid circular imports
        from src.schemas.flow_builder_schemas import UserStory, FlowRequirement, FlowType
        
        # Create UserStory object from provided data
        user_story = UserStory(**user_story_data)
        
        # Create a flow build request based on the user story with TDD context
        flow_request = FlowBuildRequest(
            flow_api_name=f"UserStory_{user_story.title.replace(' ', '_')}",
            flow_label=user_story.title,
            flow_description=user_story.description,
            user_story=user_story,
            flow_type=FlowType.SCREEN_FLOW,  # Default to screen flow for user stories
            target_api_version="59.0",
            tdd_context=tdd_context  # Include TDD context if available
        )
        
        print(f"Created TDD-enhanced flow request from user story: {user_story.title}")
        print(f"Acceptance criteria: {user_story.acceptance_criteria}")
        if tdd_context:
            print(f"🧪 Flow will be built to satisfy the deployed test cases")
        
    else:
        print("No user story provided, creating default test flow request...")
        
        # Create a simple default flow build request for testing with TDD context
        flow_request = FlowBuildRequest(
            flow_api_name="AgentGeneratedTestFlow",
            flow_label="Agent Generated Test Flow",
            flow_description="A simple test flow generated by the agent workforce using TDD approach",
            screen_api_name="WelcomeScreen",
            screen_label="Welcome Screen",
            display_text_api_name="WelcomeMessage",
            display_text_content="Hello! This flow was automatically generated using Test-Driven Development by the Salesforce Agent Workforce.",
            target_api_version="59.0",
            tdd_context=tdd_context  # Include TDD context if available
        )
    
    updated_state = state.copy()
    # Convert Pydantic model to dict for state storage
    updated_state["current_flow_build_request"] = flow_request.model_dump()
    
    if tdd_context:
        print(f"✅ Prepared TDD-enhanced flow build request for: {flow_request.flow_api_name}")
        print(f"   🧪 Tests are already deployed - Flow will be built to make them pass!")
    else:
        print(f"✅ Prepared flow build request for: {flow_request.flow_api_name}")
    
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
    retry_count = state.get("build_deploy_retry_count", 0)
    
    # Enhanced debugging for retry tracking
    if retry_count > 0:
        print(f"🔄 Preparing deployment for RETRY ATTEMPT #{retry_count}")
    else:
        print("🆕 Preparing deployment for INITIAL ATTEMPT")
    
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
        
        # Enhanced debugging - show key info about the Flow XML being used
        flow_xml = flow_response.flow_xml
        flow_api_name = flow_response.input_request.flow_api_name
        
        print(f"📄 Flow XML details for deployment:")
        print(f"   Flow API Name: {flow_api_name}")
        print(f"   XML Length: {len(flow_xml)} characters")
        
        # Show a snippet of the Flow XML for debugging (first 200 chars)
        xml_snippet = flow_xml[:200].replace('\n', ' ').replace('\r', ' ')
        print(f"   XML Preview: {xml_snippet}...")
        
        # Check if this is a retry by looking for retry context in the original request
        is_retry_request = flow_response.input_request.retry_context is not None
        if is_retry_request:
            retry_attempt = flow_response.input_request.retry_context.get("retry_attempt", "Unknown")
            print(f"🔄 This Flow XML was generated for RETRY #{retry_attempt}")
            
            # Show specific fixes that were applied
            fixes_applied = flow_response.input_request.retry_context.get("specific_fixes_needed", [])
            if fixes_applied:
                print(f"   🛠️  Applied fixes from error analysis:")
                for i, fix in enumerate(fixes_applied[:3], 1):  # Show first 3 fixes
                    print(f"      {i}. {fix}")
                if len(fixes_applied) > 3:
                    print(f"      ... and {len(fixes_applied) - 3} more fixes")
        else:
            print("🆕 This Flow XML was generated for the INITIAL attempt")
        
        # Create a MetadataComponent for the Flow
        flow_component = MetadataComponent(
            component_type="Flow",
            api_name=flow_api_name,
            metadata_xml=flow_xml
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
        
        print(f"✅ Prepared deployment request for flow: {flow_component.api_name}")
        if retry_count > 0:
            print(f"   🔄 This is retry attempt #{retry_count} - using UPDATED Flow XML")
        
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
    Node to prepare TestDesigner request in the TDD approach.
    This runs BEFORE any Flow is built or deployed - tests are designed from user story requirements.
    """
    print("\n=== PREPARING TEST DESIGNER REQUEST ===")
    
    # In TDD approach, we only need user story and authentication info
    user_story_dict = state.get("user_story")
    salesforce_session_dict = state.get("salesforce_session")
    
    if not salesforce_session_dict:
        print("Cannot prepare TestDesigner request - no Salesforce session available.")
        return state
    
    try:
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
            print("❌ Cannot prepare TestDesigner request - no user story provided.")
            return state
        
        # Determine flow type based on user story
        flow_type = "Screen Flow"  # Default
        if affected_objects:
            # If objects are involved, it's likely a Record-Triggered Flow
            if len(affected_objects) > 1:
                flow_type = "Record-Triggered Flow"
            else:
                flow_type = "Screen Flow"  # Could also be Autolaunched depending on the use case
        
        # Generate a flow API name from the user story title - with better error handling
        title = user_story_dict.get('title', 'GeneratedFlow')
        if not title or not isinstance(title, str):
            title = 'GeneratedFlow'
            
        flow_api_name = title.replace(' ', '_').replace('-', '_')
        
        # Remove special characters and ensure it starts with a letter
        import re
        flow_api_name = re.sub(r'[^a-zA-Z0-9_]', '', flow_api_name)
        
        # Ensure flow_api_name is not empty and starts with a letter
        if not flow_api_name or not flow_api_name[0].isalpha():
            flow_api_name = f"Flow_{flow_api_name}" if flow_api_name else "Flow_Generated"
        
        # Get org alias safely
        current_auth_request = state.get("current_auth_request")
        if current_auth_request and isinstance(current_auth_request, dict):
            org_alias = current_auth_request.get("org_alias", "unknown")
        else:
            org_alias = "unknown"
        
        # Create comprehensive TestDesigner request for TDD approach
        test_designer_request = TestDesignerRequest(
            flow_name=flow_api_name,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            flow_xml="",  # No Flow XML yet - this is TDD, tests come first
            flow_type=flow_type,
            target_objects=affected_objects,  # Use affected_objects from user story
            org_alias=org_alias,
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
        
        print(f"✅ Prepared comprehensive TestDesigner request for TDD:")
        print(f"   Flow: {test_designer_request.flow_name}")
        print(f"   Flow Type: {test_designer_request.flow_type}")
        print(f"   Target Objects: {test_designer_request.target_objects}")
        print(f"   Test Coverage Target: {test_designer_request.test_coverage_target}%")
        print(f"   Include Bulk Tests: {test_designer_request.include_bulk_tests}")
        print(f"   Include Negative Tests: {test_designer_request.include_negative_tests}")
        
        return updated_state
        
    except Exception as e:
        print(f"Error preparing TestDesigner request: {e}")
        print(f"State keys available: {list(state.keys())}")
        print(f"user_story_dict: {user_story_dict}")
        print(f"salesforce_session_dict: {salesforce_session_dict}")
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
        
        # Run deployment - FIXED: pass LLM parameter
        result_state = run_deployment_agent(temp_state, LLM)
        
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
    Conditional edge function to determine if we should continue after TestDesigner.
    Updated for TDD approach: always deploy test classes first.
    """
    test_designer_response = state.get("current_test_designer_response")
    if test_designer_response and test_designer_response.get("success"):
        print("✅ TestDesigner successful, proceeding to test class deployment.")
        return "prepare_test_deployment"
    else:
        print("❌ TestDesigner failed, ending workflow.")
        return END


def should_continue_after_test_deployment(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after test deployment.
    Updated for TDD approach: after successful test deployment, build the Flow.
    """
    test_deployment_response = state.get("current_test_deployment_response")
    test_deploy_retry_count = state.get("test_deploy_retry_count", 0)
    
    if test_deployment_response and test_deployment_response.get("success"):
        print("✅ Test class deployment successful, proceeding to Flow Builder (TDD approach).")
        return "flow_builder"
    else:
        print(f"❌ Test deployment failed (attempt #{test_deploy_retry_count + 1})")
        
        # Check if we should retry test deployment
        max_retries = 3  # Could be configurable
        if test_deploy_retry_count < max_retries:
            print(f"🔄 Retrying test deployment ({test_deploy_retry_count + 1}/{max_retries})")
            return "retry_test_deployment"
        else:
            print("❌ Test deployment failed after max retries, ending workflow.")
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
    Creates and configures the LangGraph workflow with Test-Driven Development approach.
    New flow: Authentication → TestDesigner → Test Deployment → Flow Builder → Flow Deployment → Retry Loop
    """
    # Create the state graph
    workflow = StateGraph(AgentWorkforceState)
    
    # Add nodes
    workflow.add_node("authentication", authentication_node)
    
    # TestDesigner comes first in TDD approach
    workflow.add_node("prepare_test_designer_request", prepare_test_designer_request)
    workflow.add_node("test_designer", test_designer_node)
    workflow.add_node("prepare_test_deployment_request", prepare_test_class_deployment_request)
    workflow.add_node("test_deployment", test_class_deployment_node)
    workflow.add_node("record_test_cycle", record_test_deploy_cycle)
    workflow.add_node("prepare_retry_test_deployment_request", prepare_retry_test_deployment_request)
    
    # Flow Builder comes after tests are deployed
    workflow.add_node("prepare_flow_request", prepare_flow_build_request)
    workflow.add_node("flow_builder", flow_builder_node)
    workflow.add_node("prepare_deployment_request", prepare_deployment_request)
    workflow.add_node("deployment", deployment_node)
    
    # Add web search nodes only if TAVILY_API_KEY is available
    # NOTE: Web search functionality temporarily disabled
    # if WEB_SEARCH_AVAILABLE:
    #     workflow.add_node("prepare_web_search_request", prepare_web_search_request)
    #     workflow.add_node("web_search", web_search_node)
    
    workflow.add_node("record_cycle", record_build_deploy_cycle)
    workflow.add_node("prepare_retry_flow_request", prepare_retry_flow_request)
    
    # Set entry point
    workflow.set_entry_point("authentication")
    
    # === TDD WORKFLOW EDGES ===
    
    # 1. Authentication → TestDesigner (TDD approach) OR Flow Builder (skip tests)
    workflow.add_conditional_edges(
        "authentication",
        should_continue_after_auth,
        {
            "test_designer": "prepare_test_designer_request",
            "flow_builder": "prepare_flow_request",  # Direct path when skipping tests
            END: END
        }
    )
    
    # 2. TestDesigner workflow
    workflow.add_edge("prepare_test_designer_request", "test_designer")
    
    workflow.add_conditional_edges(
        "test_designer",
        should_continue_after_test_designer,
        {
            "prepare_test_deployment": "prepare_test_deployment_request",
            END: END
        }
    )
    
    # 3. Test deployment workflow
    workflow.add_edge("prepare_test_deployment_request", "test_deployment")
    workflow.add_edge("test_deployment", "record_test_cycle")
    
    workflow.add_conditional_edges(
        "record_test_cycle",
        should_continue_after_test_deployment,
        {
            "flow_builder": "prepare_flow_request",  # TDD: tests deployed, now build Flow
            "retry_test_deployment": "prepare_retry_test_deployment_request",
            END: END
        }
    )
    
    # Test deployment retry loop
    workflow.add_edge("prepare_retry_test_deployment_request", "prepare_test_deployment_request")
    
    # 4. Flow Builder workflow (happens after tests are deployed)
    workflow.add_edge("prepare_flow_request", "flow_builder")
    
    workflow.add_conditional_edges(
        "flow_builder",
        should_continue_after_flow_build,
        {
            "prepare_deployment": "prepare_deployment_request",
            END: END
        }
    )
    
    # 5. Flow deployment workflow
    workflow.add_edge("prepare_deployment_request", "deployment")
    workflow.add_edge("deployment", "record_cycle")
    
    # Flow deployment retry logic
    # NOTE: Web search functionality temporarily disabled - using direct retry only
    # if WEB_SEARCH_AVAILABLE:
    #     # With web search: deployment failures → search for solutions → retry
    #     # Successful deployment → END (TDD complete)
    #     workflow.add_conditional_edges(
    #         "record_cycle",
    #         should_continue_after_deployment,
    #         {
    #             "search_for_solutions": "prepare_web_search_request",
    #             "direct_retry": "prepare_retry_flow_request",
    #             END: END
    #         }
    #     )
    #     
    #     # Web search flow: prepare search → execute search → prepare retry
    #     workflow.add_edge("prepare_web_search_request", "web_search")
    #     workflow.add_edge("web_search", "prepare_retry_flow_request")
    # else:
    #     # Without web search: deployment failures → direct retry
    #     # Successful deployment → END (TDD complete)
    #     workflow.add_conditional_edges(
    #         "record_cycle",
    #         should_continue_after_deployment,
    #         {
    #             "direct_retry": "prepare_retry_flow_request",
    #             END: END
    #         }
    #     )
    
    # Without web search: deployment failures → direct retry
    # Successful deployment → END (TDD complete)
    workflow.add_conditional_edges(
        "record_cycle",
        should_continue_after_deployment,
        {
            "direct_retry": "prepare_retry_flow_request",
            END: END
        }
    )
    
    # Flow deployment retry loop
    workflow.add_edge("prepare_retry_flow_request", "flow_builder")
    
    return workflow


def run_workflow(org_alias: str, project_name: str = "salesforce-agent-workforce") -> Dict[str, Any]:
    """
    Runs the complete Test-Driven Development workflow for the given Salesforce org alias.
    
    TDD Workflow Order:
    1. Authentication
    2. TestDesigner (analyzes requirements and creates test scenarios)
    3. Test Class Deployment (deploys Apex test classes)
    4. Flow Builder (builds Flow to make tests pass)
    5. Flow Deployment (deploys the Flow)
    6. Retry loops for any failures
    
    Args:
        org_alias: The Salesforce org alias to authenticate to
        project_name: LangSmith project name for tracing
        
    Returns:
        Final state of the workflow
    """
    print(f"\n🚀 Starting Salesforce Agent Workforce (TDD Approach) for org: {org_alias}")
    print(f"🧪 Test-Driven Development Flow: TestDesigner → Test Deployment → Flow Builder → Flow Deployment")
    print(f"🔄 Retry configuration: max_retries={MAX_BUILD_DEPLOY_RETRIES}")
    print("=" * 80)
    
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
        "test_deploy_retry_count": 0,
        # Workflow control flags
        "skip_test_design_deployment": False  # Default to full TDD workflow
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
    Prints a summary of the Test-Driven Development workflow execution.
    """
    print("\n📊 TDD WORKFLOW SUMMARY:")
    print("-" * 50)
    
    # Show TDD flow order status
    print("🧪 TEST-DRIVEN DEVELOPMENT FLOW:")
    print("   1. Authentication")
    print("   2. TestDesigner → Test Deployment") 
    print("   3. Flow Builder → Flow Deployment")
    print("   4. Retry loops as needed")
    print("")
    
    # Simple retry information
    build_deploy_retry_count = final_state.get("build_deploy_retry_count", 0)
    test_deploy_retry_count = final_state.get("test_deploy_retry_count", 0)
    max_retries = final_state.get("max_build_deploy_retries", 0)
    
    if test_deploy_retry_count > 0 or build_deploy_retry_count > 0:
        print("🔄 RETRY SUMMARY:")
        if test_deploy_retry_count > 0:
            print(f"   Test Deployment retries: {test_deploy_retry_count}/{max_retries}")
        if build_deploy_retry_count > 0:
            print(f"   Flow Deployment retries: {build_deploy_retry_count}/{max_retries}")
        print("")
    
    # Authentication status
    auth_response_dict = final_state.get("current_auth_response")
    if final_state.get("is_authenticated", False):
        print("✅ 1. Authentication: SUCCESS")
        if auth_response_dict:
            try:
                auth_response = SalesforceAuthResponse(**auth_response_dict)
                print(f"     Org ID: {auth_response.org_id}")
                print(f"     Instance URL: {auth_response.instance_url}")
            except Exception:
                print("     (Could not parse auth response details)")
    else:
        print("❌ 1. Authentication: FAILED")
        if auth_response_dict:
            try:
                auth_response = SalesforceAuthResponse(**auth_response_dict)
                if auth_response.error_message:
                    print(f"     Error: {auth_response.error_message}")
            except Exception:
                print("     (Could not parse auth response details)")
    
    # TestDesigner status (runs first in TDD)
    test_designer_response_dict = final_state.get("current_test_designer_response")
    skip_tests = final_state.get("skip_test_design_deployment", False)
    
    if skip_tests:
        print("⏭️  2a. TestDesigner: SKIPPED (by user request)")
    elif test_designer_response_dict:
        try:
            test_designer_response = TestDesignerResponse(**test_designer_response_dict)
            if test_designer_response.success:
                print("✅ 2a. TestDesigner: SUCCESS")
                print(f"      Test Scenarios: {len(test_designer_response.test_scenarios)}")
                print(f"      Apex Test Classes: {len(test_designer_response.apex_test_classes)}")
                print(f"      Deployable Code Files: {len(test_designer_response.deployable_apex_code)}")
            else:
                print("❌ 2a. TestDesigner: FAILED")
                if test_designer_response.error_message:
                    print(f"      Error: {test_designer_response.error_message}")
        except Exception:
            print("❌ 2a. TestDesigner: FAILED (Could not parse response)")
    else:
        print("⏭️  2a. TestDesigner: SKIPPED")
    
    # Test Class Deployment status (runs second in TDD)
    test_deployment_response_dict = final_state.get("current_test_deployment_response")
    
    if skip_tests:
        print("⏭️  2b. Test Class Deployment: SKIPPED (by user request)")
    elif test_deployment_response_dict:
        try:
            test_deployment_response = DeploymentResponse(**test_deployment_response_dict)
            if test_deployment_response.success:
                print("✅ 2b. Test Class Deployment: SUCCESS")
                print(f"      Deployment ID: {test_deployment_response.deployment_id}")
                print(f"      Status: {test_deployment_response.status}")
                if test_deploy_retry_count > 0:
                    print(f"      🎯 Succeeded after {test_deploy_retry_count} retry(ies)")
            else:
                print("❌ 2b. Test Class Deployment: FAILED")
                print(f"      Status: {test_deployment_response.status}")
                if test_deployment_response.error_message:
                    print(f"      Error: {test_deployment_response.error_message}")
                if test_deploy_retry_count >= max_retries:
                    print(f"      🛑 Maximum retries ({max_retries}) exhausted")
        except Exception:
            print("❌ 2b. Test Class Deployment: FAILED (Could not parse response)")
    else:
        print("⏭️  2b. Test Class Deployment: SKIPPED")
    
    # Flow building status (runs third in TDD)
    flow_response_dict = final_state.get("current_flow_build_response")
    if flow_response_dict:
        try:
            flow_response = FlowBuildResponse(**flow_response_dict)
            if flow_response.success:
                print("✅ 3a. Flow Building: SUCCESS")
                print(f"      Flow Name: {flow_response.input_request.flow_api_name}")
                print(f"      Flow Label: {flow_response.input_request.flow_label}")
                # Check if TDD context was used
                if hasattr(flow_response.input_request, 'tdd_context') and flow_response.input_request.tdd_context:
                    print("      🧪 Built using TDD context from deployed tests")
            else:
                print("❌ 3a. Flow Building: FAILED")
                if flow_response.error_message:
                    print(f"      Error: {flow_response.error_message}")
        except Exception:
            print("❌ 3a. Flow Building: FAILED (Could not parse response)")
    else:
        print("⏭️  3a. Flow Building: SKIPPED")
    
    # Flow Deployment status (runs fourth in TDD)
    deployment_response_dict = final_state.get("current_deployment_response")
    if deployment_response_dict:
        try:
            deployment_response = DeploymentResponse(**deployment_response_dict)
            if deployment_response.success:
                print("✅ 3b. Flow Deployment: SUCCESS")
                print(f"      Deployment ID: {deployment_response.deployment_id}")
                print(f"      Status: {deployment_response.status}")
                if build_deploy_retry_count > 0:
                    print(f"      🎯 Succeeded after {build_deploy_retry_count} retry(ies)")
                print("      🎉 TDD CYCLE COMPLETE: Tests and Flow both deployed!")
            else:
                print("❌ 3b. Flow Deployment: FAILED")
                print(f"      Status: {deployment_response.status}")
                if deployment_response.error_message:
                    print(f"      Error: {deployment_response.error_message}")
                if build_deploy_retry_count >= max_retries:
                    print(f"      🛑 Maximum retries ({max_retries}) exhausted")
        except Exception:
            print("❌ 3b. Flow Deployment: FAILED (Could not parse response)")
    else:
        print("⏭️  3b. Flow Deployment: SKIPPED")
        
    # General errors
    if final_state.get("error_message"):
        print(f"\n⚠️  General Error: {final_state['error_message']}")
    
    # Success message for complete TDD cycle
    if (final_state.get("current_test_deployment_response", {}).get("success") and 
        final_state.get("current_deployment_response", {}).get("success")):
        print("\n🎊 TDD SUCCESS: Both tests and Flow are deployed!")
        print("   You can now run the tests to verify the Flow works as expected.")
    
    print("-" * 50)


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