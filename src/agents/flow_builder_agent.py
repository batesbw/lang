from typing import Optional

from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel

from src.tools.flow_builder_tools import BasicFlowXmlGeneratorTool
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.state.agent_workforce_state import AgentWorkforceState


def run_flow_builder_agent(state: AgentWorkforceState, llm: BaseLanguageModel) -> AgentWorkforceState:
    """
    Runs the Flow Builder Agent.

    This agent takes a FlowBuildRequest from the state, uses the
    BasicFlowXmlGeneratorTool to generate Flow XML, and updates the
    state with a FlowBuildResponse.
    """
    print("----- FLOW BUILDER AGENT -----")
    flow_build_request: Optional[FlowBuildRequest] = state.get("current_flow_build_request")
    
    response_updates = {}

    if flow_build_request and isinstance(flow_build_request, FlowBuildRequest):
        print(f"Processing FlowBuildRequest for Flow: {flow_build_request.flow_api_name}")
        print(f"Flow Label: {flow_build_request.flow_label}")
        print(f"Flow Description: {flow_build_request.flow_description}")

        tool = BasicFlowXmlGeneratorTool()
        
        try:
            # The tool expects individual keyword arguments, so convert the model to dict
            tool_input = flow_build_request.model_dump()
            tool_output = tool.invoke(tool_input) # tool_output is expected to be FlowBuildResponse

            # BasicFlowXmlGeneratorTool returns a FlowBuildResponse object
            if isinstance(tool_output, FlowBuildResponse):
                print(f"Flow XML generated successfully for Flow: {flow_build_request.flow_api_name}")
                response_updates["current_flow_build_response"] = tool_output
            else:
                # Handle unexpected response type (shouldn't happen with correct tool)
                error_message = f"Unexpected response type from BasicFlowXmlGeneratorTool: {type(tool_output)}"
                print(error_message)
                flow_build_response = FlowBuildResponse(
                    success=False,
                    input_request=flow_build_request,
                    error_message=error_message
                )
                response_updates["current_flow_build_response"] = flow_build_response
            
            response_updates["current_flow_build_request"] = None # Clear the request

        except Exception as e:
            error_message = f"FlowBuilderAgent: Error invoking BasicFlowXmlGeneratorTool: {str(e)}"
            print(error_message)
            flow_build_response = FlowBuildResponse(
                success=False,
                input_request=flow_build_request,
                error_message=error_message
            )
            response_updates["current_flow_build_response"] = flow_build_response
            response_updates["current_flow_build_request"] = None # Clear the request

    else:
        if flow_build_request: # It exists but is not the expected type
             print("FlowBuilderAgent: flow_build_request is not a valid FlowBuildRequest instance.")
             # Create a dummy request for the response since input_request is required
             dummy_request = FlowBuildRequest(
                 flow_api_name="unknown",
                 flow_label="unknown",
                 screen_api_name="unknown",
                 screen_label="unknown",
                 display_text_api_name="unknown",
                 display_text_content="unknown"
             )
             response_updates["current_flow_build_response"] = FlowBuildResponse(
                success=False,
                input_request=dummy_request,
                error_message="Invalid request type received by FlowBuilderAgent."
             )
             response_updates["current_flow_build_request"] = None # Clear the invalid request
        else:
            # No request to process
            print("FlowBuilderAgent: No current_flow_build_request to process.")
            # No changes to current_flow_build_response if no request

    # Merge updates with the current state
    updated_state = state.copy()
    for key, value in response_updates.items():
        updated_state[key] = value
        
    return updated_state

# Example of how this agent might be integrated into a LangGraph (conceptual)
# from langchain_openai import ChatOpenAI
# from langgraph.graph import StateGraph, END
#
# llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
#
# # Define the graph
# workflow = StateGraph(AgentWorkforceState)
# workflow.add_node("flow_builder_agent", lambda state: run_flow_builder_agent(state, llm)) # Wrap in lambda if extra args needed
# # ... define edges and entry/finish points ...
# # workflow.set_entry_point("flow_builder_agent") # Example entry
# # workflow.add_edge("flow_builder_agent", END) # Example exit
# # app = workflow.compile()

# Example usage (for testing this agent node directly):
# if __name__ == "__main__":
# from src.schemas.flow_schemas import FlowElement
# initial_state = AgentWorkforceState(
# current_flow_build_request=FlowBuildRequest(
# request_id="test_req_123",
# flow_name="TestFlow",
# elements=[
# FlowElement(type="Screen", name="Screen1", label="My First Screen", fields=[]),
# FlowElement(type="Action", name="Action1", action_name=" κάποιαΕνέργεια ", inputs={})
# ]
# ),
# # Initialize other state fields as needed
# current_auth_response=None,
# current_flow_build_response=None,
# current_flow_test_request=None,
# current_flow_test_response=None,
# messages=[],
# is_authenticated=False,
# salesforce_session=None,
# retry_count=0
# )
#
#     # Dummy LLM for this standalone test
# class DummyLLM(BaseModel, BaseLanguageModel):
#         def invoke(self, input, config=None, stop=None, **kwargs):
# return "Dummy LLM response"
#         async defainvoke(self, input, config=None, stop=None, **kwargs):
# return "Dummy LLM response"
#         def _llm_type(self) -> str:
# return "dummy"

#     result_state = run_flow_builder_agent(initial_state, DummyLLM())
# print("\\nFinal State:")
# print(f"  Request: {result_state.get('current_flow_build_request')}")
# print(f"  Response: {result_state.get('current_flow_build_response').model_dump_json(indent=2) if result_state.get('current_flow_build_response') else 'None'}")

#     # Test error case
#     error_initial_state = AgentWorkforceState(
# current_flow_build_request=FlowBuildRequest(
# request_id="test_req_456_error",
# flow_name="ErrorFlow", # Tool might be designed to fail with this name for testing
# elements=[] # e.g. empty elements list might be an error
# ),
# current_auth_response=None,
# current_flow_build_response=None,
# current_flow_test_request=None,
# current_flow_test_response=None,
# messages=[],
# is_authenticated=False,
# salesforce_session=None,
# retry_count=0
# )
#     result_error_state = run_flow_builder_agent(error_initial_state, DummyLLM())
# print("\\nFinal Error State:")
# print(f"  Request: {result_error_state.get('current_flow_build_request')}")
# print(f"  Response: {result_error_state.get('current_flow_build_response').model_dump_json(indent=2) if result_error_state.get('current_flow_build_response') else 'None'}") 