import base64
import io
import time
import zipfile
import xml.etree.ElementTree as ET
from typing import Type, Optional, List, Dict, Any

from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field # Ensure Pydantic v1 for BaseTool compatibility if needed
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceDeployError

from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse
from src.schemas.auth_schemas import SalesforceAuthResponse


# Tool input schema should ideally be the DeploymentRequest itself
# However, BaseTool.args_schema expects a Pydantic v1 model.
# If DeploymentRequest is Pydantic v2, we might need a wrapper or adapt.
# For now, let's assume DeploymentRequest can be used or adapted.

class SalesforceDeployerTool(BaseTool):
    name: str = "salesforce_deployer_tool"
    description: str = (
        "Deploys a Salesforce Flow (provided as XML) to a Salesforce org using Metadata API. "
        "Input requires Flow XML, Flow API name, and active Salesforce session details."
    )
    args_schema: Type[BaseModel] = DeploymentRequest # Pydantic model for tool arguments

    def _create_package_xml(self, flow_name: str, api_version: str = "59.0") -> str:
        """Creates the package.xml content as a string."""
        package_element = ET.Element("Package", xmlns="http://soap.sforce.com/2006/04/metadata")
        types_element = ET.SubElement(package_element, "types")
        ET.SubElement(types_element, "members").text = flow_name
        ET.SubElement(types_element, "name").text = "Flow"
        ET.SubElement(package_element, "version").text = api_version
        
        # ET.tostring returns bytes, so decode to string
        return ET.tostring(package_element, encoding="unicode")

    def _create_zip_package(self, flow_name: str, flow_xml: str, package_xml: str) -> bytes:
        """Creates a zip file in memory containing the Flow and package.xml."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add Flow XML
            zf.writestr(f"flows/{flow_name}.flow-meta.xml", flow_xml)
            # Add package.xml
            zf.writestr("package.xml", package_xml)
        zip_buffer.seek(0)
        return zip_buffer.read()

    def _run(self, request: DeploymentRequest) -> DeploymentResponse:
        """
        Executes the deployment process.
        Input is a DeploymentRequest Pydantic model.
        Output is a DeploymentResponse Pydantic model.
        """
        try:
            sf_session: SalesforceAuthResponse = request.salesforce_session
            sf = Salesforce(session_id=sf_session.session_id, instance_url=sf_session.instance_url)

            package_xml_content = self._create_package_xml(request.flow_name)
            zip_bytes = self._create_zip_package(request.flow_name, request.flow_xml, package_xml_content)
            
            # Base64 encode the zip file
            zip_base64 = base64.b64encode(zip_bytes).decode('utf-8')

            # Define deploy options (can be customized further if needed)
            # https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_deploy.htm#deployoptions
            deploy_options = {
                'allowMissingFiles': False,
                'autoUpdatePackage': False,
                'checkOnly': False,       # Set to True for validation without actual deployment
                'ignoreWarnings': False,
                'performRetrieve': False,
                'purgeOnDelete': False,
                'rollbackOnError': True,  # Highly recommended
                'runTests': [],           # Specify test classes if needed, or use testLevel
                'singlePackage': True,    # Crucial for deploying a single package zip
                # 'testLevel': 'NoTestRun' # Options: NoTestRun, RunSpecifiedTests, RunLocalTests, RunAllTestsInOrg
            }
            
            # For simple Flow deployment without Apex, NoTestRun is often sufficient.
            # If Flow triggers Apex or has test requirements, adjust accordingly.
            # If deploying to Production, tests are usually required.
            # Default simple-salesforce behavior might handle this or might need testLevel specified.
            # Let's be explicit with 'testLevel' if not running tests.
            if not deploy_options.get('runTests'): # If no specific tests, set a testLevel
                deploy_options['testLevel'] = 'NoTestRun'


            print(f"Deploying Flow '{request.flow_name}' to {sf_session.instance_url}...")
            
            # simple-salesforce deploy method expects a dict of options
            deploy_result_async_id = sf.deploy(zip_base64, deploy_options)
            
            deployment_id = deploy_result_async_id.get('id')
            if not deployment_id:
                return DeploymentResponse(
                    request_id=request.request_id,
                    success=False,
                    status="Failed",
                    error_message="Failed to initiate deployment: No deployment ID received."
                )

            print(f"Deployment initiated with ID: {deployment_id}. Polling for status...")

            # Polling for deployment status
            max_retries = 60  # Poll for up to 5 minutes (60 retries * 5 seconds)
            retries = 0
            final_status_info = None

            while retries < max_retries:
                status_info = sf.check_deploy_status(deployment_id)
                print(f"  Status: {status_info.get('status')}, Done: {status_info.get('done')}")

                if status_info.get('done'):
                    final_status_info = status_info
                    break
                
                time.sleep(5)  # Wait 5 seconds before polling again
                retries += 1
            
            if not final_status_info:
                return DeploymentResponse(
                    request_id=request.request_id,
                    success=False,
                    status="InProgress", # Or "TimedOut"
                    deployment_id=deployment_id,
                    error_message=f"Deployment polling timed out after {max_retries * 5} seconds."
                )

            # Process final deployment status
            # The structure of status_info (DeployResult) from simple_salesforce:
            # success (bool), status (str), errorMessage (str), 
            # details (dict with componentSuccesses, componentFailures, etc.)
            
            # Map DeployResult details to DeploymentResponse
            component_successes = final_status_info.get('details', {}).get('componentSuccesses', [])
            component_errors = final_status_info.get('details', {}).get('componentFailures', [])
            
            # Ensure lists are not None if empty
            component_successes = component_successes if component_successes is not None else []
            component_errors = component_errors if component_errors is not None else []


            return DeploymentResponse(
                request_id=request.request_id,
                success=final_status_info.get('success', False),
                status=final_status_info.get('status', 'Unknown'),
                deployment_id=deployment_id,
                error_message=final_status_info.get('errorMessage'),
                component_successes=[dict(item) for item in component_successes], # Convert from SF specific types if any
                component_errors=[dict(item) for item in component_errors]
            )

        except SalesforceDeployError as sde:
            # This exception is raised by simple_salesforce on certain deploy errors
            # (e.g., if deploy() itself fails before returning an ID)
            return DeploymentResponse(
                request_id=request.request_id,
                success=False,
                status="Failed",
                error_message=f"Salesforce deployment API error: {str(sde)}"
            )
        except Exception as e:
            # Catch any other unexpected errors during the process
            return DeploymentResponse(
                request_id=request.request_id,
                success=False,
                status="Failed",
                error_message=f"An unexpected error occurred in SalesforceDeployerTool: {str(e)}"
            )

    async def _arun(self, request: DeploymentRequest) -> DeploymentResponse:
        # Asynchronous execution is not strictly necessary for this tool as deployment
        # itself is an async process on Salesforce's side, and we are polling.
        # However, if the main graph execution is async, this can be made non-blocking.
        # For now, we can delegate to the synchronous version or implement true async later.
        # For simplicity, let's raise NotImplementedError or call the sync version.
        # raise NotImplementedError("Async version not implemented for SalesforceDeployerTool")
        # Or, if the underlying simple-salesforce calls are blocking, this won't be truly async
        # without an async HTTP library and modifications to simple-salesforce or direct API calls.
        # For now, it's better to make it clear this is a blocking operation.
        print("Warning: SalesforceDeployerTool._arun called; running synchronous version.")
        return self._run(request)

# Example Usage (for testing, typically not part of the tool file)
if __name__ == '__main__':
    # This example requires Salesforce credentials to be available in environment variables
    # or by other means that simple_salesforce can use.
    # It also assumes you have a dummy flow XML to deploy.
    
    # Mock SalesforceAuthResponse for testing
    mock_sf_session = SalesforceAuthResponse(
        request_id="test_auth_req",
        success=True,
        session_id=os.environ.get("SF_SESSION_ID"), # You'd need to set these env vars
        instance_url=os.environ.get("SF_INSTANCE_URL"),
        user_id="test_user",
        org_id="test_org"
    )

    if not mock_sf_session.session_id or not mock_sf_session.instance_url:
        print("SF_SESSION_ID and SF_INSTANCE_URL environment variables must be set for this example.")
    else:
        # Dummy Flow XML content
        dummy_flow_name = "MyToolTestFlow"
        dummy_flow_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <interviewLabel>{dummy_flow_name} $Flow.CurrentDateTime</interviewLabel>
    <label>{dummy_flow_name}</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <start>
        <locationX>50</locationX>
        <locationY>50</locationY>
    </start>
    <status>Active</status>
</Flow>"""

        deployment_request_data = DeploymentRequest(
            request_id="test_deploy_req_123",
            flow_xml=dummy_flow_xml,
            flow_name=dummy_flow_name,
            salesforce_session=mock_sf_session
        )

        deployer_tool = SalesforceDeployerTool()
        
        print(f"Attempting to deploy flow: {dummy_flow_name}")
        response = deployer_tool._run(deployment_request_data) # Calling _run directly for test

        print("\nDeployment Response:")
        print(f"  Request ID: {response.request_id}")
        print(f"  Success: {response.success}")
        print(f"  Status: {response.status}")
        print(f"  Deployment ID: {response.deployment_id}")
        print(f"  Error Message: {response.error_message}")
        if response.component_successes:
            print("  Component Successes:")
            for success in response.component_successes:
                print(f"    - {success.get('fullName')} ({success.get('componentType')})")
        if response.component_errors:
            print("  Component Errors:")
            for error in response.component_errors:
                print(f"    - {error.get('fullName')} ({error.get('componentType')}): {error.get('problem')}") 