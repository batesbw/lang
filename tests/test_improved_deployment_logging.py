#!/usr/bin/env python3
"""
Test script to demonstrate the improved deployment logging functionality.
This shows how the enhanced logging provides better visibility into deployment problems.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main_orchestrator import _analyze_deployment_error, should_continue_after_deployment, prepare_retry_flow_request
from src.state.agent_workforce_state import AgentWorkforceState

def test_improved_deployment_logging():
    """Demonstrate the improved deployment error logging with the user's example"""
    print("=" * 80)
    print("🧪 TESTING IMPROVED DEPLOYMENT LOGGING")
    print("=" * 80)
    
    # Simulate the exact error from the user's log
    error_message = "Deployment failed with 1 error(s)"
    component_errors = [
        {
            'fullName': 'UserStory_Account_Contact_Counter',
            'componentType': 'Flow',
            'problem': 'field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element Get_Contact_Count.)',
            'fileName': 'flows/UserStory_Account_Contact_Counter.flow-meta.xml'
        }
    ]
    
    print("\n1. Testing Enhanced Error Analysis")
    print("-" * 40)
    
    # Test the enhanced error analysis
    analysis = _analyze_deployment_error(error_message, component_errors, "<Flow>test</Flow>")
    
    print("Enhanced Error Analysis Results:")
    print(f"   Error Type: {analysis['error_type']}")
    print(f"   Severity: {analysis['severity']}")
    print(f"   Number of Required Fixes: {len(analysis['required_fixes'])}")
    print(f"   Error Patterns: {analysis['error_patterns']}")
    
    if analysis['required_fixes']:
        print("   Specific Fixes Identified:")
        for i, fix in enumerate(analysis['required_fixes'], 1):
            print(f"      {i}. {fix}")
    
    if analysis['structural_issues']:
        print("   Structural Issues:")
        for issue in analysis['structural_issues']:
            print(f"      - {issue}")
    
    print("\n2. Testing Enhanced Deployment Failure Logging")
    print("-" * 40)
    
    # Create a test state with deployment failure
    test_state = AgentWorkforceState(
        build_deploy_retry_count=1,
        max_build_deploy_retries=3,
        current_deployment_response={
            "success": False,
            "status": "Failed",
            "error_message": error_message,
            "component_errors": component_errors
        }
    )
    
    print("Simulating should_continue_after_deployment with failure:")
    result = should_continue_after_deployment(test_state)
    print(f"Result: {result}")
    
    print("\n3. Testing Enhanced Retry Request Preparation")
    print("-" * 40)
    
    # Add a mock flow build response for retry preparation
    test_state["current_flow_build_response"] = {
        "success": True,
        "flow_xml": "<?xml version='1.0'?><Flow>...</Flow>",
        "input_request": {
            "flow_api_name": "UserStory_Account_Contact_Counter",
            "flow_label": "Account Contact Counter",
            "flow_description": "Count contacts for accounts"
        }
    }
    
    print("Simulating prepare_retry_flow_request with enhanced logging:")
    retry_state = prepare_retry_flow_request(test_state)
    
    print("\n4. Summary of Improvements")
    print("-" * 40)
    print("✅ Improvements made:")
    print("   - Detailed deployment failure breakdown with component-specific errors")
    print("   - Enhanced error analysis that identifies specific Salesforce Flow issues")
    print("   - Complete list of required fixes (not just first 3)")
    print("   - Clear explanation of how fixes were identified")
    print("   - Categorized issues (API Name, Structural, XML)")
    print("   - Better error pattern detection for specific Salesforce error types")
    
    print("\n🎯 The logging now provides clear visibility into:")
    print("   - What exactly failed in the deployment")
    print("   - Why the system identified specific fixes")
    print("   - How many fixes were identified and what they are")
    print("   - The specific error patterns that were detected")

def test_various_error_scenarios():
    """Test the error analysis with different types of Salesforce deployment errors"""
    print("\n" + "=" * 80)
    print("🧪 TESTING VARIOUS SALESFORCE ERROR SCENARIOS")
    print("=" * 80)
    
    error_scenarios = [
        {
            "name": "Invalid Flow Element Reference",
            "error": "field integrity exception: unknown (The formula expression is invalid: It contains an invalid flow element Get_Contact_Count.)",
            "component_errors": []
        },
        {
            "name": "API Name Validation",
            "error": "Invalid Name: The flow API name 'My Test Flow' contains invalid characters",
            "component_errors": []
        },
        {
            "name": "Duplicate Elements",
            "error": "Duplicate element name: Screen1 already exists in the flow",
            "component_errors": []
        },
        {
            "name": "Missing Required Fields",
            "error": "Missing required field: startElementReference is required for all flows",
            "component_errors": []
        },
        {
            "name": "XML Syntax Error",
            "error": "XML malformed: unexpected end of element at line 45",
            "component_errors": []
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print("-" * 30)
        
        analysis = _analyze_deployment_error(
            scenario['error'], 
            scenario['component_errors'], 
            "<Flow>test</Flow>"
        )
        
        print(f"   Error Type: {analysis['error_type']}")
        print(f"   Fixes Identified: {len(analysis['required_fixes'])}")
        print(f"   Patterns Detected: {analysis['error_patterns']}")

if __name__ == "__main__":
    test_improved_deployment_logging()
    test_various_error_scenarios()
    print("\n✅ Improved deployment logging test completed!") 