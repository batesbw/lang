import os
import uuid
import warnings
from pathlib import Path
from typing import Dict, Any, Optional

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
from src.agents.flow_validation_agent import run_flow_validation_agent
from src.agents.deployment_agent import run_deployment_agent
from src.schemas.auth_schemas import AuthenticationRequest, SalesforceAuthResponse
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Ensure required API keys are set
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

if not os.getenv("LANGSMITH_API_KEY"):
    print("Warning: LANGSMITH_API_KEY not found. LangSmith tracing may not work.")

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


def flow_validation_node(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    LangGraph node for the Flow Validation Agent.
    """
    print("\n=== FLOW VALIDATION NODE ===")
    try:
        return run_flow_validation_agent(state, LLM)
    except Exception as e:
        print(f"Error in flow_validation_node: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Flow Validation Node Error: {str(e)}"
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
        print("Flow building successful, proceeding to Flow Validation.")
        return "validation"
    else:
        print("Flow building failed, ending workflow.")
        return END


def should_continue_after_validation(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after flow validation.
    """
    validation_response = state.get("current_flow_validation_response")
    validation_requires_retry = state.get("validation_requires_retry", False)
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if validation_response and validation_response.get("success") and validation_response.get("is_valid"):
        print("✅ Flow validation passed, proceeding to deployment.")
        return "deployment"
    elif validation_requires_retry and build_deploy_retry_count < max_retries:
        print(f"🔄 Flow validation failed, retrying flow build (attempt #{build_deploy_retry_count + 1})")
        return "retry_validation"
    else:
        if build_deploy_retry_count >= max_retries:
            print(f"🛑 Maximum retries ({max_retries}) reached for validation fixes, ending workflow")
        else:
            print("❌ Flow validation failed and retry not recommended, ending workflow.")
        return END


def should_continue_after_deployment(state: AgentWorkforceState) -> str:
    """
    Conditional edge function to determine workflow continuation after deployment.
    Simple retry logic for failed deployments.
    """
    deployment_response = state.get("current_deployment_response")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    max_retries = state.get("max_build_deploy_retries", MAX_BUILD_DEPLOY_RETRIES)
    
    if deployment_response and deployment_response.get("success"):
        print("✅ Deployment successful, workflow complete.")
        return END
    else:
        print(f"❌ Deployment failed (attempt #{build_deploy_retry_count + 1})")
        
        # Check if we should retry
        if build_deploy_retry_count < max_retries:
            print(f"🔄 Retrying build/deploy cycle ({build_deploy_retry_count + 1}/{max_retries})")
            return "retry_flow_build"
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
    """
    print("\n=== PREPARING ENHANCED RETRY FLOW BUILD REQUEST ===")
    
    # Increment retry count
    current_retry_count = state.get("build_deploy_retry_count", 0) + 1
    
    # Get the deployment failure details
    deployment_response = state.get("current_deployment_response")
    last_build_response_dict = state.get("current_flow_build_response")
    
    if last_build_response_dict and deployment_response:
        try:
            last_build_response = FlowBuildResponse(**last_build_response_dict)
            original_request = last_build_response.input_request
            
            print(f"🔄 Setting up enhanced retry #{current_retry_count} for flow: {original_request.flow_api_name}")
            
            # Create retry request with enhanced failure context
            retry_request = original_request.model_copy()
            
            # Analyze the deployment error for specific fixes
            error_analysis = _analyze_deployment_error(
                deployment_response.get("error_message", "Unknown error"),
                deployment_response.get("component_errors", []),
                last_build_response.flow_xml
            )
            
            # Enhanced retry context with structured analysis
            retry_request.retry_context = {
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
            
            print(f"🔧 Enhanced failure analysis completed:")
            print(f"   Primary error type: {error_analysis['error_type']}")
            print(f"   Specific fixes needed: {len(error_analysis['required_fixes'])}")
            print(f"   Error patterns detected: {len(error_analysis['error_patterns'])}")
            for fix in error_analysis['required_fixes'][:3]:  # Show first 3 fixes
                print(f"     - {fix}")
            
            updated_state = state.copy()
            updated_state["current_flow_build_request"] = retry_request.model_dump()
            updated_state["build_deploy_retry_count"] = current_retry_count
            
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
    
    # Analyze error patterns
    if "invalid name" in error_text or "api name" in error_text:
        analysis["error_type"] = "api_name_validation"
        analysis["severity"] = "high"
        analysis["api_name_issues"].append("Invalid API name format detected")
        analysis["required_fixes"].extend([
            "Fix API names to be alphanumeric and start with a letter",
            "Remove spaces, hyphens, and special characters from all API names",
            "Ensure API names follow Salesforce naming conventions"
        ])
        analysis["error_patterns"].append("API_NAME_INVALID")
    
    if "duplicate" in error_text and "element" in error_text:
        analysis["error_type"] = "duplicate_elements"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Duplicate element names detected")
        analysis["required_fixes"].extend([
            "Ensure all flow element names are unique",
            "Check for duplicate screen, decision, or assignment names",
            "Use incremental naming (e.g., Screen1, Screen2) for multiple elements"
        ])
        analysis["error_patterns"].append("DUPLICATE_ELEMENTS")
    
    if "element reference" in error_text or "target reference" in error_text:
        analysis["error_type"] = "invalid_references"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Invalid element references")
        analysis["required_fixes"].extend([
            "Fix element references to point to valid flow elements",
            "Ensure all connector targetReference values match existing element names",
            "Check start element connector references"
        ])
        analysis["error_patterns"].append("INVALID_REFERENCES")
    
    if "required field" in error_text or "missing" in error_text:
        analysis["error_type"] = "missing_required_fields"
        analysis["severity"] = "high"
        analysis["structural_issues"].append("Missing required fields or elements")
        analysis["required_fixes"].extend([
            "Add all required flow elements and properties",
            "Ensure proper flow structure with start element",
            "Include mandatory metadata elements"
        ])
        analysis["error_patterns"].append("MISSING_REQUIRED_FIELDS")
    
    if "xml" in error_text or "malformed" in error_text or "syntax" in error_text:
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


def record_build_deploy_cycle(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to record the current build/deploy cycle attempt in history - REMOVED for simplification.
    """
    print("\n=== RECORDING BUILD/DEPLOY CYCLE - SIMPLIFIED ===")
    # Just pass through the state without complex tracking
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


def prepare_deployment_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare the deployment request based on successful flow building.
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
        flow_response = FlowBuildResponse(**flow_response_dict)
        salesforce_session = SalesforceAuthResponse(**salesforce_session_dict)
        
        if not flow_response.success:
            print("Cannot prepare deployment request - flow building failed.")
            return state
        
        # Create deployment request
        deployment_request = DeploymentRequest(
            request_id=str(uuid.uuid4()),
            flow_xml=flow_response.flow_xml,
            flow_name=flow_response.input_request.flow_api_name,
            salesforce_session=salesforce_session
        )
        
        updated_state = state.copy()
        # Convert Pydantic model to dict for state storage
        updated_state["current_deployment_request"] = deployment_request.model_dump()
        print(f"Prepared deployment request for flow: {deployment_request.flow_name}")
        
        return updated_state
        
    except Exception as e:
        print(f"Error preparing deployment request: {e}")
        updated_state = state.copy()
        updated_state["error_message"] = f"Error preparing deployment request: {str(e)}"
        return updated_state


def prepare_retry_validation_request(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Node to prepare for a retry attempt after validation failure.
    Uses the validation context created by the Flow Validation Agent.
    """
    print("\n=== PREPARING RETRY REQUEST FROM VALIDATION FAILURE ===")
    
    # The validation agent already prepared the retry context
    # We just need to ensure the state is ready for flow builder retry
    validation_requires_retry = state.get("validation_requires_retry", False)
    
    if validation_requires_retry:
        print("✅ Retry request already prepared by Flow Validation Agent")
        # The validation agent already updated the flow build request and retry count
        return state
    else:
        print("❌ No validation retry context found")
        updated_state = state.copy()
        updated_state["error_message"] = "Validation retry requested but no retry context available"
        return updated_state


def create_workflow() -> StateGraph:
    """
    Creates and configures the LangGraph workflow with Flow Validation and retry capabilities.
    """
    # Create the state graph
    workflow = StateGraph(AgentWorkforceState)
    
    # Add nodes
    workflow.add_node("authentication", authentication_node)
    workflow.add_node("prepare_flow_request", prepare_flow_build_request)
    workflow.add_node("flow_builder", flow_builder_node)
    workflow.add_node("flow_validation", flow_validation_node)
    workflow.add_node("prepare_deployment_request", prepare_deployment_request)
    workflow.add_node("deployment", deployment_node)
    workflow.add_node("record_cycle", record_build_deploy_cycle)
    workflow.add_node("prepare_retry_flow_request", prepare_retry_flow_request)
    workflow.add_node("prepare_retry_validation_request", prepare_retry_validation_request)
    
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
    
    # Flow builder -> Flow validation
    workflow.add_conditional_edges(
        "flow_builder",
        should_continue_after_flow_build,
        {
            "validation": "flow_validation",
            END: END
        }
    )
    
    # Flow validation -> Deployment or Retry
    workflow.add_conditional_edges(
        "flow_validation",
        should_continue_after_validation,
        {
            "deployment": "prepare_deployment_request",
            "retry_validation": "prepare_retry_validation_request",
            END: END
        }
    )
    
    # Deployment preparation and execution
    workflow.add_edge("prepare_deployment_request", "deployment")
    
    # Add edge to record cycle after deployment
    workflow.add_edge("deployment", "record_cycle")
    
    # Add conditional edges for retry logic after recording the cycle (deployment failures)
    workflow.add_conditional_edges(
        "record_cycle",
        should_continue_after_deployment,
        {
            "retry_flow_build": "prepare_retry_flow_request",
            END: END
        }
    )
    
    # Add edge from deployment retry preparation back to flow builder
    workflow.add_edge("prepare_retry_flow_request", "flow_builder")
    
    # Add edge from validation retry preparation back to flow builder
    workflow.add_edge("prepare_retry_validation_request", "flow_builder")
    
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
        "current_flow_validation_response": None,
        "validation_requires_retry": False,
        "current_deployment_request": None,
        "current_deployment_response": None,
        "messages": [],
        "error_message": None,
        "retry_count": 0,
        # Simple retry-related fields
        "build_deploy_retry_count": 0,
        "max_build_deploy_retries": MAX_BUILD_DEPLOY_RETRIES
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
            }
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
    max_retries = final_state.get("max_build_deploy_retries", 0)
    
    if build_deploy_retry_count > 0:
        print(f"🔄 Retry attempts: {build_deploy_retry_count}/{max_retries}")
    
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
    
    # Flow validation status
    validation_response_dict = final_state.get("current_flow_validation_response")
    if validation_response_dict:
        try:
            from src.schemas.flow_validation_schemas import FlowValidationResponse
            validation_response = FlowValidationResponse(**validation_response_dict)
            if validation_response.success and validation_response.is_valid:
                print("✅ Flow Validation: SUCCESS")
                print(f"   Scanner Version: {validation_response.scanner_version or 'unknown'}")
                if validation_response.warning_count > 0:
                    print(f"   Warnings: {validation_response.warning_count}")
            elif validation_response.success and not validation_response.is_valid:
                print("❌ Flow Validation: FAILED")
                print(f"   Errors: {validation_response.error_count}")
                print(f"   Warnings: {validation_response.warning_count}")
                if validation_response.errors:
                    print(f"   Top Error: {validation_response.errors[0].rule_name}")
            else:
                print("❌ Flow Validation: TOOL ERROR")
                if validation_response.error_message:
                    print(f"   Error: {validation_response.error_message}")
        except Exception:
            print("❌ Flow Validation: FAILED (Could not parse response)")
    else:
        print("⏭️  Flow Validation: SKIPPED")
    
    # Deployment status
    deployment_response_dict = final_state.get("current_deployment_response")
    if deployment_response_dict:
        try:
            deployment_response = DeploymentResponse(**deployment_response_dict)
            if deployment_response.success:
                print("✅ Deployment: SUCCESS")
                print(f"   Deployment ID: {deployment_response.deployment_id}")
                print(f"   Status: {deployment_response.status}")
                if build_deploy_retry_count > 0:
                    print(f"   🎯 Succeeded after {build_deploy_retry_count} retry(ies)")
            else:
                print("❌ Deployment: FAILED")
                print(f"   Status: {deployment_response.status}")
                if deployment_response.error_message:
                    print(f"   Error: {deployment_response.error_message}")
                if build_deploy_retry_count >= max_retries:
                    print(f"   🛑 Maximum retries ({max_retries}) exhausted")
        except Exception:
            print("❌ Deployment: FAILED (Could not parse response)")
    else:
        print("⏭️  Deployment: SKIPPED")
        
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
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 