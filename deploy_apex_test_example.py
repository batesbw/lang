#!/usr/bin/env python3
"""
Example: Deploy AccountContactCounterFlowTest.cls using the multi-component deployment system.

This demonstrates deploying an Apex test class with the enhanced deployment agent.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.schemas.deployment_schemas import MetadataComponent, DeploymentRequest
from src.schemas.auth_schemas import SalesforceAuthResponse
from src.tools.salesforce_deployer_tool import SalesforceDeployerTool
from src.main_orchestrator import create_multi_component_deployment_request


def read_apex_class_file(file_path: str) -> str:
    """Read the Apex class file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Apex class file not found: {file_path}")


def create_apex_class_metadata_xml(class_name: str, api_version: str = "59.0") -> str:
    """Create the metadata XML for an Apex class"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{api_version}</apiVersion>
    <status>Active</status>
</ApexClass>"""


def deploy_apex_test_class():
    """Deploy the AccountContactCounterFlowTest.cls using the multi-component system"""
    
    print("🚀 Deploying AccountContactCounterFlowTest.cls with Multi-Component Deployment System")
    print("=" * 80)
    
    # Check if we have Salesforce credentials
    session_id = os.environ.get("SF_SESSION_ID")
    instance_url = os.environ.get("SF_INSTANCE_URL")
    
    if not session_id or not instance_url:
        print("❌ Error: SF_SESSION_ID and SF_INSTANCE_URL environment variables are required")
        print("\nTo get these values:")
        print("1. Authenticate to your Salesforce org using CLI: 'sf org login web'")
        print("2. Get session info: 'sf org display --target-org YOUR_ORG_ALIAS'")
        print("3. Export the values:")
        print("   export SF_SESSION_ID='your_session_id'")
        print("   export SF_INSTANCE_URL='your_instance_url'")
        return False
    
    # Read the Apex class file
    try:
        apex_class_content = read_apex_class_file("AccountContactCounterFlowTest.cls")
        print(f"✅ Successfully read Apex class file ({len(apex_class_content)} characters)")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    
    # Create Salesforce session object
    sf_session = SalesforceAuthResponse(
        request_id="apex_deploy_session",
        success=True,
        session_id=session_id,
        instance_url=instance_url,
        user_id="current_user",
        org_id="current_org"
    )
    
    # Prepare components for deployment
    # For Apex classes, we need both the .cls file and the .cls-meta.xml file
    components_data = [
        {
            "component_type": "ApexClass",
            "api_name": "AccountContactCounterFlowTest",
            "metadata_xml": apex_class_content,  # The actual Apex code goes in the .cls file
            "directory": "classes",
            "file_extension": "cls"
        },
        {
            "component_type": "ApexClass", 
            "api_name": "AccountContactCounterFlowTest",
            "metadata_xml": create_apex_class_metadata_xml("AccountContactCounterFlowTest"),
            "directory": "classes", 
            "file_extension": "cls-meta.xml"
        }
    ]
    
    print(f"\n📦 Preparing deployment package with {len(components_data)} components:")
    for i, comp in enumerate(components_data, 1):
        print(f"  {i}. {comp['component_type']} - {comp['api_name']}.{comp['file_extension']}")
    
    # Create deployment request
    try:
        deployment_request = create_multi_component_deployment_request(
            components_data=components_data,
            salesforce_session=sf_session,
            request_id="apex_test_deployment"
        )
        print(f"✅ Created deployment request: {deployment_request.request_id}")
    except Exception as e:
        print(f"❌ Error creating deployment request: {e}")
        return False
    
    # Execute deployment
    print(f"\n🚀 Starting deployment to {instance_url}...")
    print("-" * 40)
    
    try:
        deployer_tool = SalesforceDeployerTool()
        response = deployer_tool._run(deployment_request)
        
        # Display deployment results
        print(f"\n📊 DEPLOYMENT RESULTS")
        print("=" * 40)
        print(f"Request ID: {response.request_id}")
        print(f"Success: {'✅ YES' if response.success else '❌ NO'}")
        print(f"Status: {response.status}")
        print(f"Deployment ID: {response.deployment_id}")
        print(f"Total Components: {response.total_components}")
        print(f"Successful: {response.successful_components}")
        print(f"Failed: {response.failed_components}")
        
        if response.error_message:
            print(f"\n⚠️  Error Message: {response.error_message}")
        
        if response.component_successes:
            print(f"\n✅ Successfully Deployed Components:")
            for success in response.component_successes:
                print(f"   - {success.get('fullName')} ({success.get('componentType')})")
        
        if response.component_errors:
            print(f"\n❌ Failed Components:")
            for error in response.component_errors:
                component_name = error.get('fullName', 'Unknown')
                component_type = error.get('componentType', 'Unknown')
                problem = error.get('problem', 'Unknown error')
                file_name = error.get('fileName', 'Unknown file')
                print(f"   - {component_name} ({component_type})")
                print(f"     Problem: {problem}")
                print(f"     File: {file_name}")
        
        if response.success:
            print(f"\n🎉 SUCCESS! AccountContactCounterFlowTest.cls has been deployed!")
            print(f"   You can now run the test class in your Salesforce org.")
            print(f"   Deployment ID: {response.deployment_id}")
        else:
            print(f"\n💥 DEPLOYMENT FAILED!")
            print(f"   Check the error details above for troubleshooting.")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Deployment failed with exception: {e}")
        return False


def show_deployment_package_structure():
    """Show what the deployment package will look like"""
    print("\n📁 DEPLOYMENT PACKAGE STRUCTURE")
    print("-" * 40)
    print("deployment.zip")
    print("├── package.xml")
    print("├── classes/")
    print("│   ├── AccountContactCounterFlowTest.cls")
    print("│   └── AccountContactCounterFlowTest.cls-meta.xml")
    print("\npackage.xml content:")
    print("""<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>AccountContactCounterFlowTest</members>
        <name>ApexClass</name>
    </types>
    <version>59.0</version>
</Package>""")


if __name__ == "__main__":
    print("🧪 Apex Test Class Deployment with Multi-Component System")
    print("=" * 60)
    
    try:
        show_deployment_package_structure()
        success = deploy_apex_test_class()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Go to your Salesforce org")
            print("2. Navigate to Setup → Apex Test Execution")
            print("3. Run the AccountContactCounterFlowTest class")
            print("4. Check test results to ensure your contact counter logic works correctly")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ DEPLOYMENT FAILED!")
            print("=" * 60)
            print("\nTroubleshooting:")
            print("1. Check that your Salesforce session is valid")
            print("2. Ensure your org has the Account.Count_of_Contacts__c field")
            print("3. Verify you have appropriate permissions to deploy Apex classes")
            print("4. Check the error messages above for specific issues")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Deployment interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 