"""
Test for Enhanced Memory System - Regression Prevention

This test demonstrates how the new FlowBuildingMemory system prevents
the regression issue where the 3rd attempt goes back to making the same
errors as the 1st attempt, losing the improvements from the 2nd attempt.
"""

import pytest
from src.agents.enhanced_flow_builder_agent import FlowBuildingMemory, EnhancedFlowBuilderAgent
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.schemas.user_story_schemas import UserStory

def test_memory_prevents_regression():
    """Test that the new memory system prevents quality regression"""
    print("=== Testing Memory Regression Prevention ===\n")
    
    # Create a FlowBuildingMemory instance
    memory = FlowBuildingMemory()
    
    # Simulate 1st attempt: FAILED (5 errors)
    attempt_1 = {
        "retry_attempt": 1,
        "success": False,
        "flow_api_name": "TestFlow",
        "error_message": "Multiple validation errors: naming convention, unconnected elements, missing fault paths",
        "validation_errors": [
            {"error_type": "naming_convention", "error_message": "Flow name doesn't follow convention"},
            {"error_type": "unconnected_element", "error_message": "Element not connected"},
            {"error_type": "missing_fault_path", "error_message": "No fault handling"},
            {"error_type": "api_name_invalid", "error_message": "Invalid API names"},
            {"error_type": "hardcoded_id", "error_message": "Hardcoded ID found"}
        ],
        "elements_created": [],
        "best_practices_applied": []
    }
    
    memory.add_attempt(attempt_1)
    print("✅ Added 1st attempt (FAILED - 5 errors)")
    
    # Simulate 2nd attempt: SUCCESS (1 error fixed to success)
    attempt_2 = {
        "retry_attempt": 2,
        "success": True,
        "flow_api_name": "TestFlow",
        "flow_xml": "<Flow>...</Flow>",
        "elements_created": ["StartElement", "DecisionElement", "UpdateRecordElement", "EndElement"],
        "variables_created": ["inputVariable", "resultVariable"],
        "best_practices_applied": [
            "Proper naming convention",
            "All elements connected",
            "Fault paths included",
            "Valid API names",
            "No hardcoded values"
        ],
        "validation_errors": []
    }
    
    memory.add_attempt(attempt_2)
    print("✅ Added 2nd attempt (SUCCESS - all errors fixed)")
    
    # Now get memory context for 3rd attempt
    memory_context = memory.get_memory_context()
    print("\n📊 Memory Context for 3rd Attempt:")
    print("=" * 60)
    print(memory_context)
    print("=" * 60)
    
    # Verify memory context contains success preservation instructions
    assert "🎯 SUCCESSFUL PATTERNS TO PRESERVE:" in memory_context
    assert "✅ Successfully created elements" in memory_context
    assert "✅ Applied best practices" in memory_context
    assert "THIS APPROACH WORKED - PRESERVE IT!" in memory_context
    assert "🚨 CRITICAL MEMORY INSTRUCTION:" in memory_context
    assert "build upon that success" in memory_context
    assert "Do NOT revert to approaches that already failed" in memory_context
    
    print("\n✅ Memory context correctly prioritizes successful patterns")
    print("✅ Memory context includes explicit regression prevention instructions")
    
    # Test that failed patterns are also preserved as warnings
    assert "⚠️ PATTERNS TO AVOID:" in memory_context
    assert "Multiple validation errors" in memory_context
    
    print("✅ Memory context includes failed patterns to avoid")
    
    # Test serialization/deserialization (for state persistence)
    serialized = memory.to_dict()
    restored_memory = FlowBuildingMemory.from_dict(serialized)
    restored_context = restored_memory.get_memory_context()
    
    assert restored_context == memory_context
    print("✅ Memory serialization/deserialization works correctly")
    
    print("\n🎯 EXPECTED OUTCOME:")
    print("The 3rd attempt will now see:")
    print("- Clear instructions to preserve successful patterns from attempt #2")
    print("- Explicit warnings about failed patterns from attempt #1")
    print("- Strong emphasis on building upon previous success")
    print("- Prevention of regression to earlier failed approaches")

def test_memory_with_multiple_successes():
    """Test memory behavior with multiple successful attempts"""
    print("\n=== Testing Memory with Multiple Successes ===\n")
    
    memory = FlowBuildingMemory()
    
    # Add several attempts with improvements
    attempts = [
        {"retry_attempt": 1, "success": False, "error_message": "Initial failure"},
        {"retry_attempt": 2, "success": True, "elements_created": ["Element1"], "best_practices_applied": ["Practice1"]},
        {"retry_attempt": 3, "success": True, "elements_created": ["Element1", "Element2"], "best_practices_applied": ["Practice1", "Practice2"]},
    ]
    
    for attempt in attempts:
        memory.add_attempt(attempt)
    
    context = memory.get_memory_context()
    
    # Should preserve patterns from both successful attempts
    assert "Successfully created elements: Element1" in context
    assert "Successfully created elements: Element1, Element2" in context
    assert "Applied best practices: Practice1" in context
    assert "Applied best practices: Practice1, Practice2" in context
    
    print("✅ Memory correctly preserves patterns from multiple successful attempts")

def test_memory_limits_and_cleanup():
    """Test that memory properly limits size while preserving successful attempts"""
    print("\n=== Testing Memory Limits and Cleanup ===\n")
    
    memory = FlowBuildingMemory(max_attempts=5)  # Small limit for testing
    
    # Add more attempts than the limit
    for i in range(8):
        attempt = {
            "retry_attempt": i + 1,
            "success": i % 3 == 0,  # Every 3rd attempt succeeds
            "error_message": f"Error {i}" if i % 3 != 0 else None,
            "elements_created": [f"Element{i}"] if i % 3 == 0 else []
        }
        memory.add_attempt(attempt)
    
    # Should preserve successful attempts even when over limit
    successful_attempts = [a for a in memory.attempts if a.get('success', False)]
    assert len(successful_attempts) >= 2  # Should preserve successful attempts
    
    # Should have patterns from successful attempts
    assert len(memory.successful_patterns) > 0
    
    print(f"✅ Memory preserved {len(successful_attempts)} successful attempts")
    print(f"✅ Memory has {len(memory.successful_patterns)} successful patterns")

if __name__ == "__main__":
    test_memory_prevents_regression()
    test_memory_with_multiple_successes()
    test_memory_limits_and_cleanup()
    print("\n🎉 All memory regression prevention tests passed!")
    print("\nThe new memory system should prevent the 1st->2nd->1st error regression pattern!") 