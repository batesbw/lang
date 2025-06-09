#!/usr/bin/env python3
"""
Simple validation script for the skip_test_design_deployment flag implementation.

This script validates that:
1. The state schema includes the new flag
2. The routing logic handles the flag correctly
3. The workflow structure supports both paths

This doesn't require external dependencies like LangGraph or Salesforce APIs.
"""

import sys
from pathlib import Path
import ast
import re

def validate_state_schema():
    """Validate that the state schema includes the skip flag"""
    print("🔍 Validating AgentWorkforceState schema...")
    
    state_file = Path("src/state/agent_workforce_state.py")
    if not state_file.exists():
        print("❌ State file not found")
        return False
    
    content = state_file.read_text()
    
    # Check for the skip flag in the schema
    if "skip_test_design_deployment" in content:
        print("✅ skip_test_design_deployment flag found in state schema")
        
        # Check that it's properly typed as bool
        if "skip_test_design_deployment: bool" in content:
            print("✅ Flag is properly typed as bool")
            return True
        else:
            print("⚠️  Flag found but not properly typed")
            return False
    else:
        print("❌ skip_test_design_deployment flag not found in state schema")
        return False

def validate_routing_logic():
    """Validate that the routing logic handles the skip flag"""
    print("\n🔍 Validating routing logic...")
    
    orchestrator_file = Path("src/main_orchestrator.py")
    if not orchestrator_file.exists():
        print("❌ Orchestrator file not found")
        return False
    
    content = orchestrator_file.read_text()
    
    # Check for the updated should_continue_after_auth function
    if "skip_test_design_deployment" in content:
        print("✅ skip_test_design_deployment flag referenced in orchestrator")
        
        # Check for the conditional logic
        if 'if skip_tests:' in content and 'return "flow_builder"' in content:
            print("✅ Conditional routing logic found")
            
            # Check for the workflow edge configuration
            if '"flow_builder": "prepare_flow_request"' in content:
                print("✅ Workflow edge for direct flow building found")
                return True
            else:
                print("⚠️  Workflow edge configuration may be missing")
                return False
        else:
            print("❌ Conditional routing logic not found")
            return False
    else:
        print("❌ skip_test_design_deployment flag not referenced in orchestrator")
        return False

def validate_initialization():
    """Validate that the flag is properly initialized"""
    print("\n🔍 Validating flag initialization...")
    
    orchestrator_file = Path("src/main_orchestrator.py")
    content = orchestrator_file.read_text()
    
    # Check for default initialization
    if '"skip_test_design_deployment": False' in content:
        print("✅ Flag is properly initialized with default value False")
        return True
    else:
        print("❌ Flag initialization not found or incorrect")
        return False

def validate_workflow_paths():
    """Validate that both workflow paths are supported"""
    print("\n🔍 Validating workflow path support...")
    
    orchestrator_file = Path("src/main_orchestrator.py")
    content = orchestrator_file.read_text()
    
    # Check for both paths in conditional edges
    paths_found = 0
    
    if '"test_designer": "prepare_test_designer_request"' in content:
        print("✅ TDD path (test_designer) found")
        paths_found += 1
    
    if '"flow_builder": "prepare_flow_request"' in content:
        print("✅ Direct path (flow_builder) found")
        paths_found += 1
    
    if paths_found == 2:
        print("✅ Both workflow paths are supported")
        return True
    else:
        print(f"❌ Only {paths_found}/2 workflow paths found")
        return False

def validate_summary_updates():
    """Validate that the summary function shows skipped phases"""
    print("\n🔍 Validating summary function updates...")
    
    orchestrator_file = Path("src/main_orchestrator.py")
    content = orchestrator_file.read_text()
    
    # Check for skip handling in summary
    if "SKIPPED (by user request)" in content:
        print("✅ Summary function handles skipped phases")
        return True
    else:
        print("❌ Summary function may not handle skipped phases properly")
        return False

def main():
    """Run all validation checks"""
    print("🧪 SKIP FLAG IMPLEMENTATION VALIDATION")
    print("=" * 45)
    
    validations = [
        ("State Schema", validate_state_schema),
        ("Routing Logic", validate_routing_logic),
        ("Flag Initialization", validate_initialization),
        ("Workflow Paths", validate_workflow_paths),
        ("Summary Updates", validate_summary_updates)
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validator in validations:
        try:
            if validator():
                passed += 1
        except Exception as e:
            print(f"❌ {name}: Exception occurred - {e}")
    
    print(f"\n🏁 VALIDATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All validations passed! The skip flag implementation looks good.")
        print("\n📋 SUMMARY:")
        print("   • skip_test_design_deployment flag added to state schema")
        print("   • Routing logic updated to handle the flag")
        print("   • Workflow supports both TDD and direct paths")
        print("   • Summary function updated to show skipped phases")
        print("\n🎯 Ready for use in LangGraph Studio!")
        return True
    else:
        print(f"❌ {total - passed} validations failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 