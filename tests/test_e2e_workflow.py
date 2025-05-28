import os
import unittest
from dotenv import load_dotenv
import uuid
from typing import Optional
from simple_salesforce import Salesforce
import tempfile
import zipfile

from langchain_core.language_models import BaseLanguageModel
from langchain_core.language_models.fake import FakeListLLM
from pydantic import BaseModel as PydanticBaseModel

# Schemas
from src.schemas.auth_schemas import AuthenticationRequest, AuthenticationResponse, SalesforceSessionDetails
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse

# State
from src.state.agent_workforce_state import AgentWorkforceState

# Agent Runners
from src.agents.authentication_agent import run_authentication_agent
from src.agents.flow_builder_agent import run_flow_builder_agent
from src.agents.deployment_agent import run_deployment_agent

# Load environment variables from .env file
load_dotenv()

class TestSimpleFlowDeploymentE2E(unittest.TestCase):

    def setUp(self):
        self.llm = FakeListLLM(responses=["Dummy LLM E2E Test Response"])
        self.org_alias_for_test = "E2E_TEST_ORG"  # Updated to match the env vars in .env file
        self.state = AgentWorkforceState(
            # For run_authentication_agent, current_auth_request is key
            current_auth_request=None,
            current_auth_response=None,
            is_authenticated=False,
            salesforce_session=None,
            # Initialize other fields for completeness, though not all used by every step directly
            current_flow_build_request=None,
            current_flow_build_response=None,
            current_deployment_request=None,
            current_deployment_response=None,
            retry_count=0,
            messages=[],
            error_message=None
        )
        
        # Environment variables for JWT Bearer Flow authentication
        self.sf_username = os.getenv(f"SF_USERNAME_{self.org_alias_for_test}")
        self.sf_consumer_key = os.getenv(f"SF_CONSUMER_KEY_{self.org_alias_for_test}")
        self.sf_private_key_file = os.getenv(f"SF_PRIVATE_KEY_FILE_{self.org_alias_for_test}")
        self.sf_instance_url = os.getenv(f"SF_INSTANCE_URL_{self.org_alias_for_test}")

        if not all([self.sf_username, self.sf_consumer_key, self.sf_private_key_file]):
            self.fail(
                f"Salesforce JWT Bearer Flow environment variables for alias '{self.org_alias_for_test}' must be set: "
                f"SF_USERNAME_{self.org_alias_for_test}, "
                f"SF_CONSUMER_KEY_{self.org_alias_for_test}, "
                f"SF_PRIVATE_KEY_FILE_{self.org_alias_for_test}"
            )
        
        # Check if private key file exists
        if not os.path.exists(self.sf_private_key_file):
            self.fail(f"Private key file not found: {self.sf_private_key_file}")
        
        self.test_flow_api_name = f"E2ETestFlow_{uuid.uuid4().hex[:8]}"

    def test_authenticate_build_and_deploy_simple_screen_flow(self):
        print(f"Starting E2E test with Flow Name: {self.test_flow_api_name} for Org Alias: {self.org_alias_for_test}")

        # 1. Authentication Step
        print("\n----- E2E: AUTHENTICATION -----")
        # Create authentication request
        auth_request = AuthenticationRequest(
            org_alias=self.org_alias_for_test,
            credential_type="env_alias"
        )
        self.state['current_auth_request'] = auth_request
        
        self.state = run_authentication_agent(self.state) # LLM is not strictly needed if agent logic is direct
        
        auth_response: Optional[AuthenticationResponse] = self.state.get('current_auth_response')
        
        self.assertIsNotNone(auth_response, "Authentication response should not be None")
        self.assertTrue(auth_response.success, f"Authentication failed: {auth_response.error_message}")
        self.assertTrue(self.state.get('is_authenticated', False), "is_authenticated should be True")
        self.assertIsNotNone(self.state.get('salesforce_session'), "Salesforce session should be set")
        
        print(f"Authentication successful for {self.org_alias_for_test}.")

        # 2. Flow Building Step
        print("\n----- E2E: FLOW BUILDING -----")
        flow_build_req = FlowBuildRequest(
            flow_api_name=self.test_flow_api_name,
            flow_label=f"{self.test_flow_api_name} Label",
            flow_description="A very simple screen flow created by an E2E test.",
            screen_api_name="Screen1",
            screen_label="Welcome Screen",
            display_text_api_name="DisplayText1",
            display_text_content="Hello from the E2E test!",
            target_api_version="59.0"
        )
        # The flow_builder_agent expects 'current_flow_build_request' in state
        self.state['current_flow_build_request'] = flow_build_req
        
        # run_flow_builder_agent needs llm as the second argument
        self.state = run_flow_builder_agent(self.state, self.llm) 
        
        flow_build_response: Optional[FlowBuildResponse] = self.state.get('current_flow_build_response')
        self.assertIsNotNone(flow_build_response, "Flow build response should not be None")
        self.assertTrue(flow_build_response.success, f"Flow building failed: {flow_build_response.error_message}")
        self.assertIsNotNone(flow_build_response.flow_xml, "Generated flow XML should not be None")
        self.assertIn(f"<label>{flow_build_req.flow_label}</label>", flow_build_response.flow_xml)
        print(f"Flow XML generated successfully for {self.test_flow_api_name}.")

        # 3. Deployment Step
        print("\n----- E2E: DEPLOYMENT -----")
        # Get the salesforce session from state
        salesforce_session = self.state.get('salesforce_session')
        self.assertIsNotNone(salesforce_session, "Salesforce session should be available for deployment")

        deployment_req = DeploymentRequest(
            request_id=f"e2e_deployment_{uuid.uuid4().hex[:4]}",
            flow_xml=flow_build_response.flow_xml,
            flow_name=self.test_flow_api_name,
            salesforce_session=salesforce_session 
        )
        
        self.state['current_deployment_request'] = deployment_req
        
        # run_deployment_agent needs llm as the second argument
        self.state = run_deployment_agent(self.state, self.llm)
        
        deployment_response: Optional[DeploymentResponse] = self.state.get('current_deployment_response')
        self.assertIsNotNone(deployment_response, "Deployment response should not be None")
        
        if not deployment_response.success:
            print(f"Deployment Status: {deployment_response.status}")
            print(f"Deployment Error: {deployment_response.error_message}")
            if deployment_response.component_errors:
                for err in deployment_response.component_errors:
                    print(f"  Component Error: {err}")
        
        self.assertTrue(deployment_response.success, f"Deployment failed: Status '{deployment_response.status}', Error: {deployment_response.error_message or deployment_response.component_errors}")
        self.assertEqual(deployment_response.status, "Succeeded", f"Deployment status was {deployment_response.status}, not Succeeded.")
        self.assertIsNotNone(deployment_response.deployment_id, "Salesforce deployment ID should be populated")
        print(f"Flow {self.test_flow_api_name} deployed successfully. Deployment ID: {deployment_response.deployment_id}")

        # 4. Cleanup Step - Delete the Flow
        print("\n----- E2E: CLEANUP -----")
        try:
            deletion_success = self._delete_flow(self.test_flow_api_name, salesforce_session)
            if deletion_success:
                print(f"Flow {self.test_flow_api_name} deleted successfully.")
            else:
                print(f"Warning: Failed to delete Flow {self.test_flow_api_name}")
        except Exception as e:
            print(f"Warning: Exception during Flow deletion: {e}")
            # Don't fail the test if cleanup fails

    def _delete_flow(self, flow_name: str, salesforce_session):
        """Delete a Flow from Salesforce using Tooling API"""
        print(f"Deleting Flow: {flow_name}")
        
        # Create Salesforce connection
        instance_url = salesforce_session.instance_url
        if instance_url and not instance_url.startswith('https://'):
            instance_url = f"https://{instance_url}"
        
        sf = Salesforce(session_id=salesforce_session.session_id, instance_url=instance_url)
        
        try:
            # First, find the Flow Definition and Flow records
            query = f"SELECT Id, DeveloperName, MasterLabel, LatestVersionId FROM FlowDefinition WHERE DeveloperName = '{flow_name}'"
            result = sf.toolingexecute(f"query/?q={query}")
            
            if not result.get('records'):
                print(f"Flow {flow_name} not found")
                return True  # Consider it deleted if not found
            
            flow_def = result['records'][0]
            flow_definition_id = flow_def['Id']
            latest_version_id = flow_def['LatestVersionId']
            
            print(f"Found Flow Definition ID: {flow_definition_id}, Latest Version ID: {latest_version_id}")
            
            # Try to delete the Flow version first using Tooling API
            try:
                print(f"Attempting to delete Flow version: {latest_version_id}")
                delete_result = sf.toolingexecute(f"sobjects/Flow/{latest_version_id}", method='DELETE')
                print(f"Flow version deletion result: {delete_result}")
                
                # Check if the Flow still exists after version deletion
                check_query = f"SELECT Id FROM FlowDefinition WHERE DeveloperName = '{flow_name}'"
                check_result = sf.toolingexecute(f"query/?q={check_query}")
                
                if not check_result.get('records'):
                    print(f"Flow {flow_name} successfully deleted via Tooling API")
                    return True
                    
            except Exception as e:
                print(f"Failed to delete Flow version: {e}")
            
            # Try to delete the Flow Definition using Tooling API
            try:
                print(f"Attempting to delete Flow Definition: {flow_definition_id}")
                delete_result = sf.toolingexecute(f"sobjects/FlowDefinition/{flow_definition_id}", method='DELETE')
                print(f"Flow Definition deletion result: {delete_result}")
                
                # Verify deletion
                check_query = f"SELECT Id FROM FlowDefinition WHERE DeveloperName = '{flow_name}'"
                check_result = sf.toolingexecute(f"query/?q={check_query}")
                
                if not check_result.get('records'):
                    print(f"Flow {flow_name} successfully deleted via Tooling API")
                    return True
                    
            except Exception as e:
                print(f"Failed to delete Flow Definition: {e}")
                
            # Check one more time if the Flow still exists before trying destructive changes
            final_check_query = f"SELECT Id FROM FlowDefinition WHERE DeveloperName = '{flow_name}'"
            final_check_result = sf.toolingexecute(f"query/?q={final_check_query}")
            
            if not final_check_result.get('records'):
                print(f"Flow {flow_name} was already deleted successfully")
                return True
                
            # If Tooling API deletion fails, try the destructive changes approach
            print("Tooling API deletion failed, trying destructive changes...")
            return self._delete_flow_destructive(flow_name, sf)
            
        except Exception as e:
            print(f"Error during Flow deletion: {e}")
            return False
    
    def _delete_flow_destructive(self, flow_name: str, sf):
        """Delete a Flow using destructive changes as fallback"""
        # Create empty package.xml (required for destructive changes)
        package_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <version>59.0</version>
</Package>"""
        
        # Create destructiveChanges.xml to specify what to delete
        destructive_changes_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>{flow_name}</members>
        <name>Flow</name>
    </types>
    <version>59.0</version>
</Package>"""
        
        # Create a temporary zip file for deletion
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip_file:
            with zipfile.ZipFile(temp_zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("package.xml", package_xml)
                zf.writestr("destructiveChanges.xml", destructive_changes_xml)
            temp_zip_file_path = temp_zip_file.name

        try:
            # Deploy the destructive changes
            print(f"Deploying destructive changes to delete {flow_name}")
            deploy_result = sf.deploy(temp_zip_file_path, sandbox=False)
            deployment_id = deploy_result.get('asyncId') or deploy_result.get('id')
            
            if deployment_id:
                print(f"Deletion deployment initiated with ID: {deployment_id}")
                
                # Poll for deletion completion
                max_retries = 20  # Shorter timeout for cleanup
                retries = 0
                
                while retries < max_retries:
                    status_info = sf.checkDeployStatus(deployment_id)
                    state = status_info.get('state', '')
                    
                    if state in ['Succeeded', 'Failed', 'Canceled']:
                        if state == 'Succeeded':
                            print(f"Flow {flow_name} deleted successfully via destructive changes")
                            return True
                        else:
                            print(f"Destructive deletion failed with state: {state}")
                            deployment_detail = status_info.get('deployment_detail', {})
                            errors = deployment_detail.get('errors', [])
                            for error in errors:
                                print(f"  Deletion error: {error.get('message', 'Unknown error')}")
                            return False
                    
                    import time
                    time.sleep(3)  # Shorter polling interval
                    retries += 1
                
                print(f"Destructive deletion polling timed out for Flow {flow_name}")
                return False
            else:
                print(f"Failed to initiate destructive deletion for Flow {flow_name}")
                return False
                
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_zip_file_path)
            except OSError:
                pass

if __name__ == '__main__':
    # Setup environment variables like:
    # export SF_USERNAME_E2E_TEST_ORG="your_salesforce_username@domain.com"
    # export SF_CONSUMER_KEY_E2E_TEST_ORG="your_consumer_key"
    # export SF_PRIVATE_KEY_FILE_E2E_TEST_ORG="/path/to/your/private_key.pem"
    # export SF_INSTANCE_URL_E2E_TEST_ORG="https://yourdomain.my.salesforce.com" (optional)
    unittest.main() 