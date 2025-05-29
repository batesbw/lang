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
LLM = ChatAnthropic(model=ANTHROPIC_MODEL, temperature=0)
print(f"Initialized LLM with model: {ANTHROPIC_MODEL}")

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
        print("Flow building successful, proceeding to Deployment.")
        return "deployment"
    else:
        print("Flow building failed, ending workflow.")
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
    Simply passes the original Flow XML and failure reason to FlowBuilder.
    """
    print("\n=== PREPARING RETRY FLOW BUILD REQUEST ===")
    
    # Increment retry count
    current_retry_count = state.get("build_deploy_retry_count", 0) + 1
    
    # Get the deployment failure details
    deployment_response = state.get("current_deployment_response")
    last_build_response_dict = state.get("current_flow_build_response")
    
    if last_build_response_dict and deployment_response:
        try:
            last_build_response = FlowBuildResponse(**last_build_response_dict)
            original_request = last_build_response.input_request
            
            print(f"🔄 Setting up retry #{current_retry_count} for flow: {original_request.flow_api_name}")
            
            # Create retry request with simple failure context
            retry_request = original_request.model_copy()
            
            # Add simple failure context for the FlowBuilder to use
            retry_request.retry_context = {
                "is_retry": True,
                "retry_attempt": current_retry_count,
                "original_flow_xml": last_build_response.flow_xml,
                "deployment_error": deployment_response.get("error_message", "Unknown error"),
                "component_errors": deployment_response.get("component_errors", [])
            }
            
            print(f"🔧 Passing failure details to FlowBuilder:")
            print(f"   Error: {deployment_response.get('error_message', 'Unknown error')}")
            print(f"   Component errors: {len(deployment_response.get('component_errors', []))}")
            
            updated_state = state.copy()
            updated_state["current_flow_build_request"] = retry_request.model_dump()
            updated_state["build_deploy_retry_count"] = current_retry_count
            
            print(f"✅ Retry request prepared - attempt #{current_retry_count}")
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


def create_workflow() -> StateGraph:
    """
    Creates and configures the LangGraph workflow with build/deploy retry capabilities.
    """
    # Create the state graph
    workflow = StateGraph(AgentWorkforceState)
    
    # Add nodes
    workflow.add_node("authentication", authentication_node)
    workflow.add_node("prepare_flow_request", prepare_flow_build_request)
    workflow.add_node("flow_builder", flow_builder_node)
    workflow.add_node("prepare_deployment_request", prepare_deployment_request)
    workflow.add_node("deployment", deployment_node)
    workflow.add_node("record_cycle", record_build_deploy_cycle)
    workflow.add_node("prepare_retry_flow_request", prepare_retry_flow_request)
    
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
    
    workflow.add_conditional_edges(
        "flow_builder",
        should_continue_after_flow_build,
        {
            "deployment": "prepare_deployment_request",
            END: END
        }
    )
    
    workflow.add_edge("prepare_deployment_request", "deployment")
    
    # Add edge to record cycle after deployment
    workflow.add_edge("deployment", "record_cycle")
    
    # Add conditional edges for retry logic after recording the cycle
    workflow.add_conditional_edges(
        "record_cycle",
        should_continue_after_deployment,
        {
            "retry_flow_build": "prepare_retry_flow_request",
            END: END
        }
    )
    
    # Add edge from retry preparation back to flow builder
    workflow.add_edge("prepare_retry_flow_request", "flow_builder")
    
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