from typing import Optional

from langchain_core.language_models import BaseLanguageModel

from src.tools.salesforce_deployer_tool import SalesforceDeployerTool
from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse
from src.state.agent_workforce_state import AgentWorkforceState # Updated path

def run_deployment_agent(state: AgentWorkforceState, llm: BaseLanguageModel) -> AgentWorkforceState:
    """
    Runs the Deployment Agent.

    This agent takes a DeploymentRequest from the state, uses the
    SalesforceDeployerTool to deploy the Flow metadata to Salesforce,
    and updates the state with a DeploymentResponse.
    """
    print("----- DEPLOYMENT AGENT -----")
    deployment_request: Optional[DeploymentRequest] = state.get("current_deployment_request")
    
    response_updates = {}

    if deployment_request and isinstance(deployment_request, DeploymentRequest):
        print(f"Processing DeploymentRequest ID: {deployment_request.request_id}")
        print(f"Flow Name to deploy: {deployment_request.flow_name}")

        tool = SalesforceDeployerTool()
        
        try:
            # Call the tool's _run method directly with the DeploymentRequest
            deployment_response: DeploymentResponse = tool._run(deployment_request)
            
            if deployment_response.success:
                print(f"Deployment successful for request ID: {deployment_request.request_id}, SF Deployment ID: {deployment_response.deployment_id}")
            else:
                print(f"Deployment failed for request ID: {deployment_request.request_id}. Status: {deployment_response.status}")
                if deployment_response.error_message:
                    print(f"  Error: {deployment_response.error_message}")
                if deployment_response.component_errors:
                    print(f"  Component Errors: {deployment_response.component_errors}")

            response_updates["current_deployment_response"] = deployment_response
            response_updates["current_deployment_request"] = None # Clear the request

        except Exception as e:
            # This catch is for unexpected errors in the agent/tool interaction itself,
            # not for deployment errors which the tool should handle and return in DeploymentResponse.
            error_message = f"DeploymentAgent: Error invoking SalesforceDeployerTool: {str(e)}"
            print(error_message)
            # Create a DeploymentResponse indicating this internal failure
            error_response = DeploymentResponse(
                request_id=deployment_request.request_id,
                success=False,
                status="Failed",
                error_message=error_message
            )
            response_updates["current_deployment_response"] = error_response
            response_updates["current_deployment_request"] = None # Clear the request

    else:
        if deployment_request: # It exists but is not the expected type
             print("DeploymentAgent: deployment_request is not a valid DeploymentRequest instance.")
             response_updates["current_deployment_response"] = DeploymentResponse(
                request_id="unknown",
                success=False,
                status="Failed",
                error_message="Invalid request type received by DeploymentAgent."
             )
             response_updates["current_deployment_request"] = None # Clear the invalid request
        else:
            print("DeploymentAgent: No current_deployment_request to process.")

    # Merge updates with the current state
    updated_state = state.copy()
    for key, value in response_updates.items():
        updated_state[key] = value
        
    return updated_state

# Example Usage (Conceptual - for testing this agent node directly)
# if __name__ == '__main__':
#     from src.schemas.auth_schemas import SalesforceAuthResponse
#     from langchain_core.language_models import BaseLanguageModel as DummyLLMType # For type hinting
#     from pydantic import BaseModel as PydanticBaseModel # For creating a dummy LLM
#     import os

#     # Dummy LLM for this standalone test
#     class DummyLLM(PydanticBaseModel, DummyLLMType):
#         def invoke(self, input, config=None, stop=None, **kwargs):
#             return "Dummy LLM response for DeploymentAgent"
#         async def ainvoke(self, input, config=None, stop=None, **kwargs):
#             return "Dummy LLM response for DeploymentAgent"
#         def _llm_type(self) -> str:
#             return "dummy-deployment-llm"

#     # Mock SalesforceAuthResponse for testing the tool via the agent
#     # Ensure SF_SESSION_ID and SF_INSTANCE_URL are set as environment variables
#     mock_sf_session = SalesforceAuthResponse(
#         request_id="mock_auth_req_deploy_test",
#         success=True,
#         session_id=os.environ.get("SF_SESSION_ID"), 
#         instance_url=os.environ.get("SF_INSTANCE_URL"),
#         user_id="mock_user_deploy",
#         org_id="mock_org_deploy"
#     )

#     if not mock_sf_session.session_id or not mock_sf_session.instance_url:
#         print("SF_SESSION_ID and SF_INSTANCE_URL env vars must be set for this example.")
#     else:
#         dummy_flow_name = "MyAgentTestDeployFlow"
#         dummy_flow_xml = f\"\"\"<?xml version="1.0" encoding="UTF-8"?>
# <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
#     <apiVersion>59.0</apiVersion>
#     <interviewLabel>{dummy_flow_name} $Flow.CurrentDateTime</interviewLabel>
#     <label>{dummy_flow_name}</label>
#     <processMetadataValues><name>BuilderType</name><value><stringValue>LightningFlowBuilder</stringValue></value></processMetadataValues>
#     <processType>AutoLaunchedFlow</processType>
#     <start><locationX>50</locationX><locationY>50</locationY></start>
#     <status>Active</status>
# </Flow>\"\"\"

#         initial_state = AgentWorkforceState(
#             current_deployment_request=DeploymentRequest(
#                 request_id="agent_deploy_req_456",
#                 flow_xml=dummy_flow_xml,
#                 flow_name=dummy_flow_name,
#                 salesforce_session=mock_sf_session
#             ),
#             # ... other state fields if needed ...
#             is_authenticated=True, # Assuming authenticated for deployment
#             salesforce_session=mock_sf_session,
#             retry_count=0
#         )

#         result_state = run_deployment_agent(initial_state, DummyLLM())
#         print("\nFinal State after Deployment Agent run:")
#         print(f"  Request: {result_state.get('current_deployment_request')}")
#         response = result_state.get('current_deployment_response')
#         if response:
#             print(f"  Response: {response.model_dump_json(indent=2)}")
#         else:
#             print("  Response: None") 