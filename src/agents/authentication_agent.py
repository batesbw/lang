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
from src.schemas.auth_schemas import AuthenticationResponse, SalesforceSessionDetails, AuthenticationRequest
from src.state.graph_state import AgentWorkforceState # Assuming this will be the shared state type

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

LLM = ChatAnthropic(model="claude-3-opus-20240229", temperature=0)
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
    It expects 'current_org_alias_request' to be set in the input state.
    """
    print("--- Running Authentication Agent ---")
    org_alias_to_authenticate = state.get("current_org_alias_request")

    if not org_alias_to_authenticate:
        print("Authentication Agent: No org_alias provided in current_org_alias_request.")
        updated_state = state.copy()
        updated_state["authentication_error"] = "Authentication Agent Error: No org_alias provided for authentication."
        updated_state["last_authenticated_org_alias"] = None 
        updated_state["active_salesforce_sessions"] = state.get("active_salesforce_sessions") or {}
        return updated_state

    # Note: The prompt guides the LLM to use the tool. 
    # For this specific agent, the primary goal is to get the structured AuthenticationResponse
    # from the tool and update the state. Invoking the tool directly here after LLM has (in theory)
    # decided to use it ensures we get the structured Pydantic model for state update,
    # rather than trying to parse it from a natural language LLM summary.
    # The LLM ensures the right tool is picked with the right input (org_alias).
    # The create_authentication_agent_executor() and its prompt are still valuable for agent definition,
    # LangSmith tracing of LLM decision-making, and if the agent had more complex logic or tools.
    
    # agent_executor = create_authentication_agent_executor() # Executor created but not strictly used for tool call below
                                                            # for simplified state update.

    try:
        auth_tool = SalesforceAuthenticatorTool()
        # The agent's prompt has {input_org_alias}. Tool's input schema is org_alias.
        auth_response: AuthenticationResponse = auth_tool.invoke({"org_alias": org_alias_to_authenticate})

        updated_state = state.copy() # Start with a fresh copy of the current state
        
        # Ensure active_salesforce_sessions is initialized if it's None
        if updated_state.get("active_salesforce_sessions") is None:
            updated_state["active_salesforce_sessions"] = {}

        if auth_response.success and auth_response.session_details:
            print(f"Authentication Agent: Successfully authenticated to {org_alias_to_authenticate}.")
            # Directly update the mutable dictionary obtained from the copied state
            updated_state["active_salesforce_sessions"][org_alias_to_authenticate] = auth_response.session_details
            updated_state["last_authenticated_org_alias"] = org_alias_to_authenticate
            updated_state["authentication_error"] = None
        else:
            error_msg = auth_response.error_message or "Unknown authentication error."
            print(f"Authentication Agent: Failed to authenticate to {org_alias_to_authenticate}. Error: {error_msg}")
            updated_state["authentication_error"] = error_msg
            updated_state["last_authenticated_org_alias"] = None # Clear last authenticated on failure for this alias
            # Optionally remove from active sessions if a previous session for this alias existed and now failed
            if org_alias_to_authenticate in updated_state["active_salesforce_sessions"]:
                del updated_state["active_salesforce_sessions"][org_alias_to_authenticate]
        
        return updated_state

    except Exception as e:
        print(f"Authentication Agent: Error invoking tool directly: {str(e)}")
        updated_state = state.copy()
        updated_state["authentication_error"] = f"Authentication Agent Tool Invocation Error: {str(e)}"
        updated_state["last_authenticated_org_alias"] = None
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
        "current_org_alias_request": test_org_alias,
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