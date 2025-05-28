#!/usr/bin/env python3
"""
Simple CLI script to trigger the Salesforce Agent Workforce workflow.

This script provides an easy way to run the linear workflow:
START -> AuthenticationAgent -> FlowBuilderAgent -> DeploymentAgent -> END

Usage:
    python scripts/run_workflow.py <org_alias>
    
Example:
    python scripts/run_workflow.py MYSANDBOX
"""

import sys
import os
from pathlib import Path

# Add src to Python path so we can import our modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.main_orchestrator import run_workflow


def main():
    """Main CLI entry point."""
    print("🤖 Salesforce Agent Workforce - Linear Workflow")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("❌ Error: Org alias is required")
        print("\nUsage:")
        print("  python scripts/run_workflow.py <org_alias>")
        print("\nExample:")
        print("  python scripts/run_workflow.py MYSANDBOX")
        print("\nMake sure you have the following environment variables set:")
        print("  - ANTHROPIC_API_KEY")
        print("  - LANGSMITH_API_KEY (optional, for tracing)")
        print("  - SF_CONSUMER_KEY_<ORG_ALIAS>")
        print("  - SF_CONSUMER_SECRET_<ORG_ALIAS>")
        print("  - SF_MY_DOMAIN_URL_<ORG_ALIAS>")
        sys.exit(1)
    
    org_alias = sys.argv[1].upper()
    
    # Validate required environment variables
    required_env_vars = [
        "ANTHROPIC_API_KEY",
        f"SF_CONSUMER_KEY_{org_alias}",
        f"SF_CONSUMER_SECRET_{org_alias}",
        f"SF_MY_DOMAIN_URL_{org_alias}"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        sys.exit(1)
    
    print(f"🎯 Target Org: {org_alias}")
    print(f"🔑 Using credentials for: {org_alias}")
    
    # Optional: Show LangSmith status
    if os.getenv("LANGSMITH_API_KEY"):
        print("📊 LangSmith tracing: ENABLED")
    else:
        print("📊 LangSmith tracing: DISABLED (LANGSMITH_API_KEY not set)")
    
    print("\n🚀 Starting workflow execution...")
    print("-" * 50)
    
    try:
        # Run the workflow
        final_state = run_workflow(org_alias)
        
        # Check final status and exit appropriately
        if final_state.get("error"):
            print(f"\n💥 Workflow failed with error: {final_state['error']}")
            sys.exit(1)
        
        # Check if authentication succeeded
        if not final_state.get("is_authenticated", False):
            print("\n🔐 Authentication failed - workflow terminated")
            sys.exit(1)
        
        # Check deployment status
        deployment_response = final_state.get("current_deployment_response")
        if deployment_response:
            if deployment_response.success:
                print("\n🎉 SUCCESS: Flow deployed successfully!")
                print(f"   Deployment ID: {deployment_response.deployment_id}")
                print(f"   Flow Name: {deployment_response.request_id}")
                sys.exit(0)
            else:
                print("\n❌ FAILED: Deployment unsuccessful")
                print(f"   Status: {deployment_response.status}")
                if deployment_response.error_message:
                    print(f"   Error: {deployment_response.error_message}")
                sys.exit(1)
        else:
            print("\n⚠️  WARNING: Workflow completed but no deployment response found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error during workflow execution:")
        print(f"   {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 