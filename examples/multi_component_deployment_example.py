#!/usr/bin/env python3
"""
Example demonstrating multi-component deployment capabilities.

This example shows how to deploy multiple types of Salesforce metadata 
components (Flow, CustomObject, ApexClass, etc.) in a single deployment.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.schemas.deployment_schemas import MetadataComponent, DeploymentRequest
from src.schemas.auth_schemas import SalesforceAuthResponse
from src.tools.salesforce_deployer_tool import SalesforceDeployerTool
from src.main_orchestrator import create_multi_component_deployment_request


def create_example_flow_xml(flow_name: str) -> str:
    """Create example Flow XML"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <interviewLabel>{flow_name} $Flow.CurrentDateTime</interviewLabel>
    <label>{flow_name}</label>
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


def create_example_custom_object_xml(object_name: str) -> str:
    """Create example CustomObject XML"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <actionOverrides>
        <actionName>Accept</actionName>
        <type>Default</type>
    </actionOverrides>
    <allowInChatterGroups>false</allowInChatterGroups>
    <compactLayoutAssignment>SYSTEM</compactLayoutAssignment>
    <deploymentStatus>Deployed</deploymentStatus>
    <enableActivities>true</enableActivities>
    <enableBulkApi>true</enableBulkApi>
    <enableFeeds>false</enableFeeds>
    <enableHistory>true</enableHistory>
    <enableLicensing>false</enableLicensing>
    <enableReports>true</enableReports>
    <enableSearch>true</enableSearch>
    <enableSharing>true</enableSharing>
    <enableStreamingApi>true</enableStreamingApi>
    <fields>
        <fullName>Description__c</fullName>
        <externalId>false</externalId>
        <label>Description</label>
        <length>255</length>
        <required>false</required>
        <trackHistory>false</trackHistory>
        <trackTrending>false</trackTrending>
        <type>Text</type>
        <unique>false</unique>
    </fields>
    <label>{object_name.replace('__c', '').replace('_', ' ')}</label>
    <nameField>
        <label>{object_name.replace('__c', '').replace('_', ' ')} Name</label>
        <trackHistory>false</trackHistory>
        <type>Text</type>
    </nameField>
    <pluralLabel>{object_name.replace('__c', '').replace('_', ' ')}s</pluralLabel>
    <searchLayouts/>
    <sharingModel>ReadWrite</sharingModel>
    <visibility>Public</visibility>
</CustomObject>"""


def create_example_apex_class_xml(class_name: str) -> str:
    """Create example ApexClass XML (metadata only, not the actual class code)"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <status>Active</status>
</ApexClass>"""


def example_single_component_deployment():
    """Example: Deploy a single Flow component"""
    print("=" * 60)
    print("EXAMPLE 1: Single Component Deployment (Flow)")
    print("=" * 60)
    
    # Create components
    components_data = [
        {
            "component_type": "Flow",
            "api_name": "ExampleSingleFlow",
            "metadata_xml": create_example_flow_xml("Example Single Flow")
        }
    ]
    
    print(f"Components to deploy:")
    for comp in components_data:
        print(f"  - {comp['component_type']}: {comp['api_name']}")
    
    # This would work with real Salesforce credentials
    print("\nTo deploy, you would:")
    print("1. Set SF_SESSION_ID and SF_INSTANCE_URL environment variables")
    print("2. Use create_multi_component_deployment_request() helper")
    print("3. Call SalesforceDeployerTool._run() with the request")


def example_multi_component_deployment():
    """Example: Deploy multiple different components together"""
    print("=" * 60)
    print("EXAMPLE 2: Multi-Component Deployment")
    print("=" * 60)
    
    # Create components of different types
    components_data = [
        {
            "component_type": "Flow",
            "api_name": "MultiDeployFlow",
            "metadata_xml": create_example_flow_xml("Multi Deploy Flow")
        },
        {
            "component_type": "CustomObject", 
            "api_name": "MyCustomObject__c",
            "metadata_xml": create_example_custom_object_xml("MyCustomObject__c")
        },
        {
            "component_type": "ApexClass",
            "api_name": "MyApexClass",
            "metadata_xml": create_example_apex_class_xml("MyApexClass"),
            # ApexClass components also need the actual class file
            # In a real scenario, you'd deploy both the .cls file and .cls-meta.xml file
        }
    ]
    
    print(f"Components to deploy:")
    for comp in components_data:
        print(f"  - {comp['component_type']}: {comp['api_name']}")
    
    print(f"\nTotal components: {len(components_data)}")
    print("\nThis would create a package.xml with multiple <types> sections:")
    print("  - Flow: MultiDeployFlow")
    print("  - CustomObject: MyCustomObject__c") 
    print("  - ApexClass: MyApexClass")


def example_direct_component_creation():
    """Example: Create components directly using MetadataComponent class"""
    print("=" * 60)
    print("EXAMPLE 3: Direct Component Creation")
    print("=" * 60)
    
    # Create components directly
    flow_component = MetadataComponent(
        component_type="Flow",
        api_name="DirectCreatedFlow",
        metadata_xml=create_example_flow_xml("Direct Created Flow")
    )
    
    custom_object_component = MetadataComponent(
        component_type="CustomObject",
        api_name="DirectObject__c",
        metadata_xml=create_example_custom_object_xml("DirectObject__c"),
        # Override default directory/extension if needed
        directory="objects",
        file_extension="object"
    )
    
    print("Created components directly:")
    print(f"  - {flow_component.component_type}: {flow_component.api_name}")
    print(f"  - {custom_object_component.component_type}: {custom_object_component.api_name}")
    
    # This shows how the deployment system automatically handles file paths
    print(f"\nFile paths in deployment package:")
    print(f"  - flows/{flow_component.api_name}.flow-meta.xml")
    print(f"  - objects/{custom_object_component.api_name}.object")


def example_with_mock_credentials():
    """Example: Show how deployment would work with credentials"""
    print("=" * 60)
    print("EXAMPLE 4: Deployment with Mock Credentials")
    print("=" * 60)
    
    # Mock Salesforce session (in real use, get this from authentication)
    mock_session = SalesforceAuthResponse(
        request_id="example_auth",
        success=True,
        session_id="mock_session_id",
        instance_url="https://example.my.salesforce.com",
        user_id="mock_user_id",
        org_id="mock_org_id"
    )
    
    # Create components
    components_data = [
        {
            "component_type": "Flow",
            "api_name": "MockDeploymentFlow",
            "metadata_xml": create_example_flow_xml("Mock Deployment Flow")
        }
    ]
    
    # Use the helper function to create the request
    deployment_request = create_multi_component_deployment_request(
        components_data=components_data,
        salesforce_session=mock_session,
        request_id="example_deployment_123"
    )
    
    print("Created DeploymentRequest:")
    print(f"  Request ID: {deployment_request.request_id}")
    print(f"  Components: {len(deployment_request.components)}")
    print(f"  API Version: {deployment_request.api_version}")
    
    for i, component in enumerate(deployment_request.components):
        print(f"  Component {i+1}: {component.component_type} - {component.api_name}")
    
    print("\nTo deploy, you would:")
    print("  tool = SalesforceDeployerTool()")
    print("  response = tool._run(deployment_request)")
    print("  # Process response...")


def show_supported_metadata_types():
    """Show all supported metadata types from the configuration"""
    print("=" * 60)
    print("SUPPORTED METADATA TYPES")
    print("=" * 60)
    
    from src.tools.salesforce_deployer_tool import METADATA_TYPE_CONFIG
    
    print("The deployment system supports these metadata types:")
    print()
    
    for metadata_type, config in METADATA_TYPE_CONFIG.items():
        print(f"  {metadata_type}:")
        print(f"    Directory: {config['directory']}")
        print(f"    File Extension: {config['file_extension']}")
        print()
    
    print("You can also use custom metadata types by specifying:")
    print("  - component_type: The Salesforce metadata type name")
    print("  - directory: Custom directory for the component")
    print("  - file_extension: Custom file extension")


if __name__ == "__main__":
    print("🚀 Multi-Component Deployment Examples")
    print("=" * 60)
    
    try:
        show_supported_metadata_types()
        example_single_component_deployment()
        example_multi_component_deployment()
        example_direct_component_creation()
        example_with_mock_credentials()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\nTo use with real Salesforce credentials:")
        print("1. Set environment variables: SF_SESSION_ID, SF_INSTANCE_URL")
        print("2. Replace mock_session with real SalesforceAuthResponse")
        print("3. Use SalesforceDeployerTool._run(deployment_request)")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        sys.exit(1) 