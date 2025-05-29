# Core LangChain and LLM imports
import os
from pathlib import Path # Added for robust path handling
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Typing and Pydantic models
from typing import List, Dict, Optional

# Project-specific imports
from src.tools.salesforce_tools import SalesforceAuthenticatorTool
from src.schemas.auth_schemas import AuthenticationResponse, SalesforceSessionDetails, AuthenticationRequest, SalesforceAuthResponse
from src.state.agent_workforce_state import AgentWorkforceState # Using the correct state module

# Load environment variables from .env file
# Construct the path to the .env file in the project root
# __file__ is src/agents/authentication_agent.py
# .parent is src/agents/
# .parent.parent is src/
# .parent.parent.parent is the project root /home/ben/Repos/lang
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Ensure ANTHROPIC_API_KEY is set
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

LLM = ChatAnthropic(
    model="claude-3-opus-20240229", 
    temperature=0, 
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048"))  # Use configurable max tokens, smaller default for auth
)
AUTHENTICATION_TOOLS = [SalesforceAuthenticatorTool()]

AUTHENTICATION_AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """
    You are a specialized Salesforce Authentication Agent.
    Your sole responsibility is to attempt authentication to a Salesforce organization 
    using the provided organization alias (`org_alias`).
    You MUST use the 'salesforce_authenticator_tool' to perform this action.
    Do not attempt any other actions or provide conversational responses beyond the authentication result.
    Based on the tool's output, clearly state if authentication was successful or if it failed, including any error messages from the tool.
    """),
    ("human", "Please attempt to authenticate to the Salesforce org with alias: '{input_org_alias}'."),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def create_authentication_agent_executor() -> AgentExecutor:
    """
    Creates the LangChain agent executor for the AuthenticationAgent.
    """
    agent = create_tool_calling_agent(LLM, AUTHENTICATION_TOOLS, AUTHENTICATION_AGENT_PROMPT_TEMPLATE)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=AUTHENTICATION_TOOLS, 
        verbose=True, # Set to False in production if desired
        handle_parsing_errors=True # Handles errors if LLM output is not parsable for tool use
    )
    return agent_executor

# This will be the node function in LangGraph
def run_authentication_agent(state: AgentWorkforceState) -> AgentWorkforceState:
    """
    Executes the authentication agent and updates the graph state based on the outcome.
    It expects 'current_auth_request' to be set in the input state.
    """
    print("--- Running Authentication Agent ---")
    
    # Debug logging to help diagnose state issues
    print(f"DEBUG: Received state keys: {list(state.keys())}")
    print(f"DEBUG: Full state: {state}")
    
    auth_request_dict = state.get("current_auth_request")
    print(f"DEBUG: auth_request_dict = {auth_request_dict}")
    print(f"DEBUG: auth_request_dict type = {type(auth_request_dict)}")
    print(f"DEBUG: auth_request_dict truthiness = {bool(auth_request_dict)}")

    if not auth_request_dict:
        print("Authentication Agent: No auth_request provided in current_auth_request.")
        updated_state = state.copy()
        auth_response = AuthenticationResponse(
            success=False,
            error_message="Authentication Agent Error: No auth_request provided for authentication."
        )
        updated_state["current_auth_response"] = auth_response.model_dump()
        updated_state["is_authenticated"] = False
        updated_state["salesforce_session"] = None
        return updated_state

    try:
        # Convert dict back to Pydantic model
        print(f"DEBUG: Attempting to create AuthenticationRequest from: {auth_request_dict}")
        auth_request = AuthenticationRequest(**auth_request_dict)
        org_alias_to_authenticate = auth_request.org_alias
        print(f"DEBUG: Successfully created AuthenticationRequest, org_alias = {org_alias_to_authenticate}")

        auth_tool = SalesforceAuthenticatorTool()
        # The tool's input schema is org_alias.
        auth_response: AuthenticationResponse = auth_tool.invoke({"org_alias": org_alias_to_authenticate})

        updated_state = state.copy() # Start with a fresh copy of the current state
        
        if auth_response.success and auth_response.session_details:
            print(f"Authentication Agent: Successfully authenticated to {org_alias_to_authenticate}.")
            
            # Create SalesforceAuthResponse for the salesforce_session field
            salesforce_session = SalesforceAuthResponse(
                success=True,
                session_id=auth_response.session_details.session_id,
                instance_url=auth_response.session_details.instance_url,
                user_id=auth_response.session_details.user_id,
                org_id=auth_response.session_details.org_id,
                auth_type_used="env_alias"
            )
            
            # Convert to dicts for state storage
            updated_state["current_auth_response"] = auth_response.model_dump()
            updated_state["is_authenticated"] = True
            updated_state["salesforce_session"] = salesforce_session.model_dump()
        else:
            error_msg = auth_response.error_message or "Unknown authentication error."
            print(f"Authentication Agent: Failed to authenticate to {org_alias_to_authenticate}. Error: {error_msg}")
            updated_state["current_auth_response"] = auth_response.model_dump()
            updated_state["is_authenticated"] = False
            updated_state["salesforce_session"] = None
        
        # Clear the request after processing
        updated_state["current_auth_request"] = None
        
        return updated_state

    except Exception as e:
        print(f"Authentication Agent: Error processing authentication: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        print(f"DEBUG: Exception args: {e.args}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        updated_state = state.copy()
        auth_response = AuthenticationResponse(
            success=False,
            error_message=f"Authentication Agent Processing Error: {str(e)}"
        )
        updated_state["current_auth_response"] = auth_response.model_dump()
        updated_state["is_authenticated"] = False
        updated_state["salesforce_session"] = None
        updated_state["current_auth_request"] = None
        return updated_state

# For the `run_authentication_agent` node to work correctly with LangGraph,
# the `AgentWorkforceState` TypedDict in `src/state/graph_state.py` will need
# a field like `current_org_alias_request: Optional[str]`.
# This field will be set by the orchestrator or a preceding node to tell the
# AuthenticationAgent which org to attempt to connect to.
# I will add this to the graph_state.py file next. 

if __name__ == "__main__":
    # This is a simple test harness for the AuthenticationAgent.
    # Ensure you have the necessary environment variables set for the org_alias you want to test.
    # For example, if your alias is "MYSANDBOX":
    # export SF_CONSUMER_KEY_MYSANDBOX="your_consumer_key"
    # export SF_CONSUMER_SECRET_MYSANDBOX="your_consumer_secret"
    # export SF_MY_DOMAIN_URL_MYSANDBOX="https://your_domain.my.salesforce.com"
    # Also, ensure ANTHROPIC_API_KEY is set.

    print("--- Authentication Agent Test Harness ---")
    
    # Get the org alias from user input or use a default
    test_org_alias = input("Enter the Salesforce org alias to test (e.g., MYSANDBOX): ").strip()
    if not test_org_alias:
        print("No org alias provided. Exiting test.")
        exit()

    print(f"Attempting authentication for org_alias: {test_org_alias}")

    # Initialize a minimal state
    initial_state: AgentWorkforceState = {
        "active_salesforce_sessions": {},
        "authentication_error": None,
        "last_authenticated_org_alias": None,
        "current_auth_request": AuthenticationRequest(org_alias=test_org_alias),
        # Add other keys from AgentWorkforceState with None or default values if required by other parts,
        # but for run_authentication_agent, these are the primary ones.
    }

    # Run the agent
    result_state = run_authentication_agent(initial_state)

    print("\n--- Test Result ---")
    if result_state.get("authentication_error"):
        print(f"Authentication Failed: {result_state['authentication_error']}")
    elif result_state.get("last_authenticated_org_alias") == test_org_alias and \
          test_org_alias in result_state.get("active_salesforce_sessions", {}):
        print(f"Authentication Successful for {test_org_alias}!")
        session_details = result_state["active_salesforce_sessions"][test_org_alias]
        print(f"  Session ID: {session_details.session_id[:15]}... (truncated)") # Truncate for brevity
        print(f"  Instance URL: {session_details.instance_url}")
        print(f"  Org ID: {session_details.org_id}")
        print(f"  User ID: {session_details.user_id}")
    else:
        print("Authentication outcome uncertain. Full final state:")
        import pprint
        pprint.pprint(result_state)

    print("--------------------------------------") 