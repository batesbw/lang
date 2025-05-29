#!/usr/bin/env python3
"""
Test script for the simplified Salesforce Agent Workforce with retry capabilities.

This script demonstrates:
1. Build/deploy retry loop when deployment fails
2. Simple error passing to FlowBuilder for fixes
3. Maximum retry limits to prevent runaway processes
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main_orchestrator import run_workflow


def test_retry_workflow():
    """Test the simplified retry workflow with a sample org"""
    
    print("🧪 TESTING SIMPLIFIED SALESFORCE AGENT WORKFORCE WITH RETRY CAPABILITIES")
    print("=" * 80)
    
    # Get org alias from command line or use default
    if len(sys.argv) > 1:
        org_alias = sys.argv[1]
    else:
        print("❌ No org alias provided.")
        print("Usage: python test_retry_workflow.py <ORG_ALIAS>")
        print("Example: python test_retry_workflow.py E2E_TEST_ORG")
        print("Available org aliases: SANDBOX, PRODUCTION, E2E_TEST_ORG")
        return False
    
    print(f"🎯 Target Org: {org_alias}")
    
    # Determine the correct environment variable based on org alias
    if org_alias.upper() == "SANDBOX":
        username_var = "SF_USERNAME_SANDBOX"
    elif org_alias.upper() == "PRODUCTION":
        username_var = "SF_USERNAME_PRODUCTION"
    elif org_alias.upper() == "E2E_TEST_ORG":
        username_var = "SF_USERNAME_E2E_TEST_ORG"
    else:
        # For custom org aliases, assume the pattern SF_USERNAME_{ORG_ALIAS}
        username_var = f"SF_USERNAME_{org_alias.upper()}"
    
    # Check environment variables
    required_env_vars = [
        "ANTHROPIC_API_KEY",
        username_var,
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file and try again.")
        print(f"For org alias '{org_alias}', expecting: {username_var}")
        return False
    
    # Display retry configuration
    max_retries = int(os.getenv("MAX_BUILD_DEPLOY_RETRIES", "3"))
    
    print(f"🔧 Configuration:")
    print(f"   Max Build/Deploy Retries: {max_retries}")
    print(f"   Using environment variable: {username_var}")
    print()
    
    try:
        # Run the workflow
        result = run_workflow(org_alias, project_name="retry-test-workflow")
        
        # Analyze the results
        print("\n" + "=" * 80)
        print("🔍 SIMPLIFIED RETRY WORKFLOW TEST ANALYSIS")
        print("=" * 80)
        
        if "error" in result:
            print(f"❌ Workflow failed with error: {result['error']}")
            return False
        
        # Extract retry information
        final_state = result
        retry_count = final_state.get("build_deploy_retry_count", 0)
        max_retries = final_state.get("max_build_deploy_retries", 0)
        
        print(f"📊 Retry Statistics:")
        print(f"   Retries used: {retry_count}/{max_retries}")
        
        # Check deployment success
        deployment_response = final_state.get("current_deployment_response")
        if deployment_response and deployment_response.get("success"):
            print(f"✅ Final Result: SUCCESS")
            if retry_count > 0:
                print(f"   🎯 Succeeded after {retry_count} retry(ies)")
                print(f"   💡 Demonstrates simple retry and error fixing!")
        else:
            print(f"❌ Final Result: FAILED")
            if retry_count >= max_retries:
                print(f"   🛑 Exhausted all {max_retries} retries")
            
            # Show the final error if available
            if deployment_response and deployment_response.get("error_message"):
                print(f"   Final error: {deployment_response['error_message']}")
        
        # Show authentication and flow building status
        auth_success = final_state.get("is_authenticated", False)
        print(f"\n📋 Workflow Steps:")
        print(f"   Authentication: {'✅' if auth_success else '❌'}")
        
        flow_response = final_state.get("current_flow_build_response")
        if flow_response:
            flow_success = flow_response.get("success", False)
            print(f"   Flow Building: {'✅' if flow_success else '❌'}")
            if not flow_success and flow_response.get("error_message"):
                print(f"      Error: {flow_response['error_message']}")
        
        if deployment_response:
            deploy_success = deployment_response.get("success", False)
            print(f"   Deployment: {'✅' if deploy_success else '❌'}")
            if not deploy_success and deployment_response.get("error_message"):
                error_preview = deployment_response["error_message"][:80] + "..." if len(deployment_response["error_message"]) > 80 else deployment_response["error_message"]
                print(f"      Error: {error_preview}")
        
        print("\n✅ Simplified retry workflow test completed!")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
        return False
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_retry_workflow()
    sys.exit(0 if success else 1) 