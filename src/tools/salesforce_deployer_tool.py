import base64
import io
import time
import zipfile
import xml.etree.ElementTree as ET
import os
import tempfile
from io import BytesIO
from typing import Type, Optional, List, Dict, Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field  # Use Pydantic v2 for consistency
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError

from src.schemas.deployment_schemas import DeploymentRequest, DeploymentResponse, MetadataComponent
from src.schemas.auth_schemas import SalesforceAuthResponse


# Metadata type configuration for different Salesforce components
METADATA_TYPE_CONFIG = {
    "Flow": {
        "directory": "flows",
        "file_extension": "flow-meta.xml"
    },
    "CustomObject": {
        "directory": "objects", 
        "file_extension": "object"
    },
    "ApexClass": {
        "directory": "classes",
        "file_extension": "cls"
    },
    "ApexTrigger": {
        "directory": "triggers",
        "file_extension": "trigger"
    },
    "CustomField": {
        "directory": "objects",
        "file_extension": "field"
    },
    "Layout": {
        "directory": "layouts",
        "file_extension": "layout"
    },
    "PermissionSet": {
        "directory": "permissionsets",
        "file_extension": "permissionset"
    },
    "Profile": {
        "directory": "profiles",
        "file_extension": "profile"
    },
    "CustomTab": {
        "directory": "tabs",
        "file_extension": "tab"
    },
    "CustomApplication": {
        "directory": "applications",
        "file_extension": "app"
    },
    "ValidationRule": {
        "directory": "objects",
        "file_extension": "validationRule"
    },
    "Workflow": {
        "directory": "workflows",
        "file_extension": "workflow"
    },
    "EmailTemplate": {
        "directory": "email",
        "file_extension": "email"
    },
    "StaticResource": {
        "directory": "staticresources",
        "file_extension": "resource"
    },
    "LightningComponentBundle": {
        "directory": "lwc",
        "file_extension": "js"
    },
    "AuraDefinitionBundle": {
        "directory": "aura",
        "file_extension": "cmp"
    }
}

class SalesforceDeployerTool(BaseTool):
    name: str = "salesforce_deployer_tool"
    description: str = (
        "Deploys multiple Salesforce metadata components (Flow, CustomObject, ApexClass, etc.) to a Salesforce org using Metadata API. "
        "Input requires component metadata XML, API names, types, and active Salesforce session details."
    )
    args_schema: Type[BaseModel] = DeploymentRequest # Pydantic model for tool arguments

    def _get_component_config(self, component: MetadataComponent) -> Dict[str, str]:
        """Get the directory and file extension for a metadata component"""
        # Use component-specific values if provided, otherwise use defaults from config
        config = METADATA_TYPE_CONFIG.get(component.component_type, {})
        
        return {
            "directory": component.directory or config.get("directory", "miscellaneous"),
            "file_extension": component.file_extension or config.get("file_extension", "xml")
        }

    def _create_package_xml(self, components: List[MetadataComponent], api_version: str = "59.0") -> str:
        """Creates the package.xml content for multiple metadata types."""
        package_element = ET.Element("Package", xmlns="http://soap.sforce.com/2006/04/metadata")
        
        # Group components by type
        components_by_type = {}
        for component in components:
            if component.component_type not in components_by_type:
                components_by_type[component.component_type] = []
            components_by_type[component.component_type].append(component.api_name)
        
        # Create types elements for each metadata type
        for metadata_type, api_names in components_by_type.items():
            types_element = ET.SubElement(package_element, "types")
            for api_name in api_names:
                ET.SubElement(types_element, "members").text = api_name
            ET.SubElement(types_element, "name").text = metadata_type
        
        ET.SubElement(package_element, "version").text = api_version
        
        return ET.tostring(package_element, encoding="unicode")

    def _create_zip_package(self, components: List[MetadataComponent], package_xml: str) -> bytes:
        """Creates a zip file in memory containing all metadata components and package.xml."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add each component
            for component in components:
                config = self._get_component_config(component)
                directory = config["directory"]
                file_extension = config["file_extension"]
                
                # Special handling for ApexClass components
                if component.component_type == "ApexClass":
                    # Create the .cls file with the Apex code
                    cls_file_path = f"{directory}/{component.api_name}.cls"
                    zf.writestr(cls_file_path, component.metadata_xml)
                    
                    # Create the .cls-meta.xml file with metadata
                    meta_xml_content = self._create_apex_class_metadata_xml(component.api_name, "59.0")
                    meta_file_path = f"{directory}/{component.api_name}.cls-meta.xml"
                    zf.writestr(meta_file_path, meta_xml_content)
                else:
                    # Standard handling for other component types
                    file_path = f"{directory}/{component.api_name}.{file_extension}"
                    zf.writestr(file_path, component.metadata_xml)
            
            # Add package.xml
            zf.writestr("package.xml", package_xml)
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def _create_apex_class_metadata_xml(self, class_name: str, api_version: str = "59.0") -> str:
        """
        Create the metadata XML for an Apex class.
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{api_version}</apiVersion>
    <status>Active</status>
</ApexClass>"""

    def _run(self, request: DeploymentRequest) -> DeploymentResponse:
        """
        Executes the deployment process for multiple metadata components.
        Input is a DeploymentRequest Pydantic model.
        Output is a DeploymentResponse Pydantic model.
        """
        try:
            sf_session: SalesforceAuthResponse = request.salesforce_session
            
            # Ensure instance URL has proper protocol
            instance_url = sf_session.instance_url
            if instance_url and not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            sf = Salesforce(session_id=sf_session.session_id, instance_url=instance_url)

            # Create package.xml and zip file with all components
            package_xml_content = self._create_package_xml(request.components, request.api_version)
            zip_bytes = self._create_zip_package(request.components, package_xml_content)
            
            # Create a temporary file to store the zip file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip_file:
                temp_zip_file.write(zip_bytes)
                temp_zip_file_path = temp_zip_file.name

            try:
                component_types = list(set(comp.component_type for comp in request.components))
                component_names = [comp.api_name for comp in request.components]
                
                print(f"Deploying {len(request.components)} components of types {component_types} to {sf_session.instance_url}...")
                print(f"Component names: {component_names}")
                
                # simple-salesforce deploy method expects a file path and sandbox flag
                deploy_result_async_id = sf.deploy(temp_zip_file_path, sandbox=False)
                
                deployment_id = deploy_result_async_id.get('asyncId') or deploy_result_async_id.get('id')
                if not deployment_id:
                    return DeploymentResponse(
                        request_id=request.request_id,
                        success=False,
                        status="Failed",
                        error_message="Failed to initiate deployment: No deployment ID received.",
                        total_components=len(request.components),
                        successful_components=0,
                        failed_components=len(request.components)
                    )

                print(f"Deployment initiated with ID: {deployment_id}. Polling for status...")

                # Polling for deployment status
                max_retries = 60  # Poll for up to 5 minutes (60 retries * 5 seconds)
                retries = 0
                final_status_info = None

                while retries < max_retries:
                    status_info = sf.checkDeployStatus(deployment_id)
                    print(f"  Raw status_info: {status_info}")
                    
                    # The actual response structure uses 'state' not 'status'
                    state = status_info.get('state', '')
                    print(f"  State: {state}")

                    # Check if deployment is complete (success or failure)
                    if state in ['Succeeded', 'Failed', 'Canceled', 'SucceededPartial']:
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
                        error_message=f"Deployment polling timed out after {max_retries * 5} seconds.",
                        total_components=len(request.components),
                        successful_components=0,
                        failed_components=len(request.components)
                    )

                # Process final deployment status
                state = final_status_info.get('state', 'Unknown')
                deployment_detail = final_status_info.get('deployment_detail', {})
                
                # Extract component errors from deployment_detail
                deployment_errors = deployment_detail.get('errors', [])
                
                # Convert deployment errors to component errors format
                component_errors = []
                for error in deployment_errors:
                    # Try to map error to specific component
                    error_file = error.get('file', '')
                    component_name = error.get('fullName', 'Unknown')
                    component_type = error.get('type', 'Unknown')
                    
                    # If we can't get component info from error, try to infer from file path
                    if component_name == 'Unknown' and error_file:
                        for comp in request.components:
                            config = self._get_component_config(comp)
                            expected_path = f"{config['directory']}/{comp.api_name}.{config['file_extension']}"
                            if expected_path in error_file:
                                component_name = comp.api_name
                                component_type = comp.component_type
                                break
                    
                    component_errors.append({
                        'fullName': component_name,
                        'componentType': component_type,
                        'problem': error.get('message', 'Unknown error'),
                        'fileName': error_file
                    })

                # Extract component successes if available
                component_successes = []
                deployment_successes = deployment_detail.get('successes', [])
                for success in deployment_successes:
                    component_successes.append({
                        'fullName': success.get('fullName', 'Unknown'),
                        'componentType': success.get('type', 'Unknown'),
                        'fileName': success.get('file', '')
                    })

                # Determine success based on state
                success = state == 'Succeeded'
                
                # Calculate summary statistics
                total_components = len(request.components)
                failed_components = len(component_errors)
                successful_components = total_components - failed_components
                
                # Extract error message
                error_message = None
                if not success and component_errors:
                    error_message = f"Deployment failed with {len(component_errors)} error(s) out of {total_components} component(s)"
                elif state == 'SucceededPartial':
                    error_message = f"Deployment partially succeeded: {successful_components} succeeded, {failed_components} failed"

                return DeploymentResponse(
                    request_id=request.request_id,
                    success=success,
                    status=state,
                    deployment_id=deployment_id,
                    error_message=error_message,
                    component_successes=component_successes,
                    component_errors=component_errors,
                    total_components=total_components,
                    successful_components=successful_components,
                    failed_components=failed_components
                )
            
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_zip_file_path)
                except OSError:
                    pass  # Ignore errors if file doesn't exist or can't be deleted

        except SalesforceError as sde:
            # This exception is raised by simple_salesforce on certain deploy errors
            return DeploymentResponse(
                request_id=request.request_id,
                success=False,
                status="Failed",
                error_message=f"Salesforce deployment API error: {str(sde)}",
                total_components=len(request.components) if request.components else 0,
                successful_components=0,
                failed_components=len(request.components) if request.components else 0
            )
        except Exception as e:
            # Catch any other unexpected errors during the process
            return DeploymentResponse(
                request_id=request.request_id,
                success=False,
                status="Failed",
                error_message=f"An unexpected error occurred in SalesforceDeployerTool: {str(e)}",
                total_components=len(request.components) if request.components else 0,
                successful_components=0,
                failed_components=len(request.components) if request.components else 0
            )

    async def _arun(self, request: DeploymentRequest) -> DeploymentResponse:
        print("Warning: SalesforceDeployerTool._arun called; running synchronous version.")
        return self._run(request)

# Example Usage (for testing, typically not part of the tool file)
if __name__ == '__main__':
    # This example requires Salesforce credentials to be available in environment variables
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
        # Example: Deploy multiple components
        components = [
            MetadataComponent(
                component_type="Flow",
                api_name="MyToolTestFlow",
                metadata_xml=f"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <interviewLabel>MyToolTestFlow $Flow.CurrentDateTime</interviewLabel>
    <label>MyToolTestFlow</label>
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
            )
        ]

        deployment_request_data = DeploymentRequest(
            request_id="test_deploy_req_123",
            components=components,
            salesforce_session=mock_sf_session
        )

        deployer_tool = SalesforceDeployerTool()
        
        print(f"Attempting to deploy {len(components)} component(s)")
        response = deployer_tool._run(deployment_request_data) # Calling _run directly for test

        print("\nDeployment Response:")
        print(f"  Request ID: {response.request_id}")
        print(f"  Success: {response.success}")
        print(f"  Status: {response.status}")
        print(f"  Deployment ID: {response.deployment_id}")
        print(f"  Error Message: {response.error_message}")
        print(f"  Total Components: {response.total_components}")
        print(f"  Successful: {response.successful_components}")
        print(f"  Failed: {response.failed_components}")
        if response.component_successes:
            print("  Component Successes:")
            for success in response.component_successes:
                print(f"    - {success.get('fullName')} ({success.get('componentType')})")
        if response.component_errors:
            print("  Component Errors:")
            for error in response.component_errors:
                print(f"    - {error.get('fullName')} ({error.get('componentType')}): {error.get('problem')}") 