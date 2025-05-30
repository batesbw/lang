"""
Flow Validation Agent

This agent validates Salesforce Flow XML using Lightning Flow Scanner and provides
detailed feedback for retry attempts. It integrates with the existing retry mechanism
to loop back to FlowBuilderAgent when validation errors are found.
"""

import logging
import uuid
import json
from typing import Optional, Dict, Any, List

from langchain_core.language_models import BaseLanguageModel

from src.tools.flow_scanner_tool import FlowScannerTool
from src.schemas.flow_validation_schemas import (
    FlowValidationRequest,
    FlowValidationResponse,
    FlowValidationSummary,
    FlowScannerRule
)
from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from src.state.agent_workforce_state import AgentWorkforceState

logger = logging.getLogger(__name__)

class FlowValidationAgent:
    """Agent responsible for validating Flow XML using Lightning Flow Scanner"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.scanner_tool = FlowScannerTool()
        
    def validate_flow_xml(self, 
                         flow_xml: str, 
                         flow_api_name: str,
                         validation_level: str = "standard") -> FlowValidationResponse:
        """Validate Flow XML using Lightning Flow Scanner"""
        
        request = FlowValidationRequest(
            request_id=str(uuid.uuid4()),
            flow_api_name=flow_api_name,
            flow_xml=flow_xml,
            validation_level=validation_level
        )
        
        try:
            result_json = self.scanner_tool._run(
                flow_xml=request.flow_xml,
                flow_name=request.flow_api_name,
                request_id=request.request_id
            )
            
            # Parse the JSON result into a FlowValidationResponse
            result_data = json.loads(result_json)
            response = FlowValidationResponse(**result_data)
            
            logger.info(f"Flow validation completed for {flow_api_name}: "
                       f"{response.error_count} errors, {response.warning_count} warnings")
            return response
        except Exception as e:
            logger.error(f"Flow validation failed for {flow_api_name}: {str(e)}")
            return FlowValidationResponse(
                request_id=request.request_id,
                success=False,
                flow_api_name=flow_api_name,
                is_valid=False,
                error_message=f"Validation agent error: {str(e)}"
            )
    
    def create_retry_context(self, 
                           validation_response: FlowValidationResponse,
                           original_request: FlowBuildRequest,
                           current_retry_count: int,
                           failed_flow_xml: str) -> Dict[str, Any]:
        """Create enhanced retry context with validation errors"""
        
        # Create validation summary directly
        blocking_issues = [f"{error.rule_name}: {error.message}" for error in validation_response.errors]
        recommended_fixes = self._generate_fix_instructions(validation_response.errors)
        
        if validation_response.error_count == 1:
            retry_guidance = f"Fix the single critical error: {validation_response.errors[0].rule_name}"
        elif validation_response.error_count > 1:
            retry_guidance = f"Fix {validation_response.error_count} critical errors, prioritizing: {', '.join([e.rule_name for e in validation_response.errors[:3]])}"
        else:
            retry_guidance = "Address the validation warnings for better flow quality"
        
        # Categorize errors by type for targeted fixes
        error_categories = self._categorize_errors_by_type(validation_response.errors)
        
        # Generate specific fix instructions
        fix_instructions = self._generate_fix_instructions(validation_response.errors)
        
        # Create enhanced retry context
        retry_context = {
            "is_retry": True,
            "retry_attempt": current_retry_count + 1,
            "validation_failed": True,
            "scanner_validation": {
                "total_violations": len(validation_response.errors) + len(validation_response.warnings),
                "error_count": validation_response.error_count,
                "warning_count": validation_response.warning_count,
                "blocking_issues": blocking_issues,
                "recommended_fixes": recommended_fixes,
                "retry_guidance": retry_guidance
            },
            "error_analysis": {
                "error_type": "validation_failure",
                "severity": "high" if validation_response.error_count > 0 else "medium",
                "error_categories": error_categories,
                "primary_issues": [error.rule_name for error in validation_response.errors[:3]],
                "required_fixes": fix_instructions
            },
            "specific_fixes_needed": fix_instructions,
            "common_patterns": [error.rule_name for error in validation_response.errors],
            "validation_errors": [
                {
                    "rule": error.rule_name,
                    "message": error.message,
                    "location": error.location,
                    "suggested_fix": error.fix_suggestion
                }
                for error in validation_response.errors
            ],
            "previous_flow_xml": original_request.retry_context.get("original_flow_xml") if original_request.retry_context else None,
            "original_flow_xml": failed_flow_xml,
            "scanner_details": {
                "scanner_version": validation_response.scanner_version,
                "execution_time_seconds": validation_response.execution_time_seconds
            }
        }
        
        return retry_context
    
    def _categorize_errors_by_type(self, errors: List[FlowScannerRule]) -> Dict[str, List[str]]:
        """Categorize validation errors by type for targeted fixing"""
        categories = {
            "performance": [],
            "best_practices": [],
            "structure": [],
            "naming": [],
            "api_compatibility": [],
            "error_handling": []
        }
        
        rule_categories = {
            "DMLStatementInLoop": "performance",
            "SOQLQueryInLoop": "performance",
            "ActionCallsInLoop": "performance",
            "HardcodedId": "best_practices",
            "HardcodedUrl": "best_practices",
            "UnsafeRunningContext": "best_practices",
            "UnconnectedElement": "structure",
            "MissingNullHandler": "structure",
            "CopyAPIName": "naming",
            "FlowName": "naming",
            "FlowDescription": "naming",
            "APIVersion": "api_compatibility",
            "MissingFaultPath": "error_handling",
            "AutoLayout": "structure"
        }
        
        for error in errors:
            category = rule_categories.get(error.rule_name, "best_practices")
            categories[category].append(error.rule_name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_fix_instructions(self, errors: List[FlowScannerRule]) -> List[str]:
        """Generate specific fix instructions for validation errors"""
        instructions = []
        
        # Enhanced, specific fix instructions for each rule
        priority_rules = {
            # Performance Issues (Critical)
            "DMLStatementInLoop": "CRITICAL: Move all record create/update/delete operations outside of loop elements",
            "SOQLQueryInLoop": "CRITICAL: Move all Get Records operations outside of loop elements", 
            "ActionCallsInLoop": "CRITICAL: Move all action calls outside of loop elements",
            
            # Hardcoded Values (High Priority)
            "HardcodedId": "HIGH: Replace hardcoded record IDs with variables or dynamic lookups",
            "HardcodedUrl": "HIGH: Replace hardcoded URLs with custom labels or variables",
            
            # Error Handling (High Priority)
            "MissingFaultPath": "HIGH: Add fault connectors to ALL Get Records, Create Records, Update Records, and Delete Records elements. Connect fault paths to assignment elements or screen elements that handle errors gracefully.",
            
            # Flow Structure (Medium Priority)
            "UnconnectedElement": "MEDIUM: Remove unconnected flow elements or connect them to the main flow path using connectors",
            "MissingNullHandler": "MEDIUM: Add decision elements to check for null values after Get Records operations before using the results",
            "UnsafeRunningContext": "MEDIUM: Review flow trigger conditions and ensure proper user context",
            
            # Naming and Conventions (Medium Priority)
            "CopyAPIName": "MEDIUM: Update element API names to be descriptive and unique (no 'myVariable_X' or 'CopyOfElement' names)",
            "FlowName": "MEDIUM: Update flow label to follow naming convention: Domain_Description format (e.g., 'Sales_AccountContactCounter')",
            "FlowDescription": "MEDIUM: Add a clear, descriptive flow description that explains the business purpose",
            
            # Flow Status (Medium Priority) 
            "FlowStatus": "MEDIUM: Set flow status to 'Active' instead of 'Draft' by changing <status>Draft</status> to <status>Active</status>",
            "InactiveFlow": "MEDIUM: Set flow status to 'Active' instead of 'Draft' by changing <status>Draft</status> to <status>Active</status>",
            
            # API Compatibility (Low Priority)
            "APIVersion": "LOW: Update flow API version to latest (60.0 or higher) by changing <apiVersion>XX.0</apiVersion> to <apiVersion>60.0</apiVersion>",
            "AutoLayout": "LOW: Ensure flow elements have proper positioning for Flow Builder",
            
            # Lightning Flow Scanner Specific Rules (based on common error messages)
            "Flow Naming Convention": "MEDIUM: Change flow label to follow Domain_Description format. Update <label>YourFlowName</label> to something like <label>Sales_AccountContactCounter</label>",
            "Inactive Flow": "MEDIUM: Activate the flow by changing <status>Draft</status> to <status>Active</status> in the Flow XML",
            "Missing Fault Path": "HIGH: Add fault connectors to ALL data operations. For each <recordLookups>, <recordCreates>, <recordUpdates>, add a <faultConnector> element that connects to error handling logic.",
            "Unconnected Element": "MEDIUM: Ensure all flow elements are connected. Add <connector> elements between flow elements or remove unused elements.",
            "Hardcoded ID": "HIGH: Replace any hardcoded Salesforce IDs (15 or 18 character strings) with variables or Get Records operations",
            "DML Statement in Loop": "CRITICAL: Move Create/Update/Delete Records elements outside of Loop elements. Use collection variables instead.",
            "SOQL Query in Loop": "CRITICAL: Move Get Records elements outside of Loop elements. Query all records first, then loop through the collection."
        }
        
        # Add specific instructions for found errors
        for error in errors:
            rule_name = error.rule_name
            error_message = error.message or ""
            
            # Try exact match first
            if rule_name in priority_rules:
                instructions.append(f"FIX {rule_name}: {priority_rules[rule_name]}")
            # Try partial match for Lightning Flow Scanner rule descriptions
            elif any(key.lower() in rule_name.lower() for key in priority_rules.keys()):
                matching_key = next(key for key in priority_rules.keys() if key.lower() in rule_name.lower())
                instructions.append(f"FIX {rule_name}: {priority_rules[matching_key]}")
            # Try partial match in error message
            elif any(key.lower() in error_message.lower() for key in priority_rules.keys()):
                matching_key = next(key for key in priority_rules.keys() if key.lower() in error_message.lower())
                instructions.append(f"FIX {rule_name}: {priority_rules[matching_key]}")
            else:
                # Generic fix with more context
                fix_suggestion = error.fix_suggestion or "Review the validation error details"
                instructions.append(f"FIX {rule_name}: {fix_suggestion}. Error details: {error_message}")
        
        # Add specific guidance based on error patterns
        error_names = [error.rule_name for error in errors]
        
        if any("naming" in name.lower() or "name" in name.lower() for name in error_names):
            instructions.append("NAMING GUIDANCE: Use Domain_Description format for flow names (e.g., 'Sales_AccountContactCounter')")
        
        if any("inactive" in name.lower() or "status" in name.lower() for name in error_names):
            instructions.append("STATUS GUIDANCE: Change <status>Draft</status> to <status>Active</status> to activate the flow")
        
        if any("fault" in name.lower() or "error" in name.lower() for name in error_names):
            instructions.append("ERROR HANDLING GUIDANCE: Every Get Records, Create Records, Update Records, and Delete Records element MUST have a fault connector that handles failures")
        
        # Add priority guidance
        if len(errors) > 3:
            instructions.append("PRIORITY: Fix CRITICAL and HIGH priority errors first (performance and data operations)")
        
        # Add XML-specific guidance
        instructions.append("XML IMPLEMENTATION: Make changes directly in the Flow XML structure - update element properties, add missing elements, or modify existing values as specified above")
        
        return instructions
    
    def should_retry_flow_build(self, validation_response: FlowValidationResponse) -> bool:
        """Determine if the flow should be rebuilt based on validation results"""
        # Retry if there are any errors (not just warnings)
        return validation_response.error_count > 0
    
    def get_validation_feedback_message(self, validation_response: FlowValidationResponse) -> str:
        """Generate human-readable validation feedback"""
        if validation_response.is_valid:
            message = f"✅ Flow '{validation_response.flow_api_name}' passed validation!"
            if validation_response.warning_count > 0:
                message += f" ({validation_response.warning_count} warnings found)"
            return message
        else:
            message = f"❌ Flow '{validation_response.flow_api_name}' failed validation:\n"
            message += f"   • {validation_response.error_count} errors found\n"
            message += f"   • {validation_response.warning_count} warnings found\n"
            
            # Add top 3 errors
            for i, error in enumerate(validation_response.errors[:3], 1):
                message += f"   {i}. {error.rule_name}: {error.message}\n"
            
            if validation_response.error_count > 3:
                message += f"   ... and {validation_response.error_count - 3} more errors\n"
            
            return message

def run_flow_validation_agent(state: AgentWorkforceState, llm: BaseLanguageModel) -> AgentWorkforceState:
    """
    Run the Flow Validation Agent to validate Flow XML using Lightning Flow Scanner.
    
    This agent:
    1. Takes the current flow build response and validates the Flow XML
    2. Updates the Flow Builder's memory with the actual validation results (CRITICAL FIX)
    3. If validation fails, creates enhanced retry context with specific fixes
    4. Updates the state to either proceed to deployment or retry flow building
    """
    print("\n=== FLOW VALIDATION AGENT ===")
    
    flow_build_response_dict = state.get("current_flow_build_response")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    response_updates = {}
    
    if not flow_build_response_dict:
        print("❌ No flow build response found to validate")
        response_updates["error_message"] = "No flow build response available for validation"
        updated_state = state.copy()
        for key, value in response_updates.items():
            updated_state[key] = value
        return updated_state
    
    try:
        # Parse the flow build response
        flow_build_response = FlowBuildResponse(**flow_build_response_dict)
        
        if not flow_build_response.success:
            print("❌ Flow build was not successful, skipping validation")
            # No validation needed if flow build failed
            updated_state = state.copy()
            return updated_state
        
        if not flow_build_response.flow_xml:
            print("❌ No flow XML found in build response")
            response_updates["error_message"] = "No flow XML available for validation"
            updated_state = state.copy()
            for key, value in response_updates.items():
                updated_state[key] = value
            return updated_state
        
        print(f"🔍 Validating flow: {flow_build_response.input_request.flow_api_name}")
        print(f"📄 Flow XML length: {len(flow_build_response.flow_xml)} characters")
        
        # Initialize validation agent
        validation_agent = FlowValidationAgent(llm)
        
        # Validate the flow XML
        validation_response = validation_agent.validate_flow_xml(
            flow_xml=flow_build_response.flow_xml,
            flow_api_name=flow_build_response.input_request.flow_api_name,
            validation_level="standard"
        )
        
        # Store validation response in state
        response_updates["current_flow_validation_response"] = validation_response.model_dump()
        
        # Print validation results
        feedback_message = validation_agent.get_validation_feedback_message(validation_response)
        print(feedback_message)
        
        # CRITICAL FIX: Update Flow Builder memory with actual validation results
        if validation_response.success:
            try:
                from src.agents.enhanced_flow_builder_agent import EnhancedFlowBuilderAgent
                
                # Load persisted memory data from state
                persisted_memory_data = state.get("flow_builder_memory_data", {})
                
                # Create temporary agent instance to access memory update method
                temp_agent = EnhancedFlowBuilderAgent(llm, persisted_memory_data)
                
                # Determine the attempt number from retry context
                retry_context = flow_build_response.input_request.retry_context
                attempt_number = retry_context.get('retry_attempt', 1) if retry_context else 1
                
                # Update memory with validation results
                validation_passed = validation_response.is_valid
                validation_errors = []
                
                # Extract validation errors with proper structure
                if hasattr(validation_response, 'errors') and validation_response.errors:
                    for error in validation_response.errors:
                        validation_errors.append({
                            'error_type': error.rule_name,
                            'error_message': error.message,
                            'location': error.location,
                            'severity': error.severity,
                            'fix_suggestion': error.fix_suggestion
                        })
                
                temp_agent.update_memory_with_validation_result(
                    flow_api_name=flow_build_response.input_request.flow_api_name,
                    attempt_number=attempt_number,
                    validation_passed=validation_passed,
                    validation_errors=validation_errors
                )
                
                # Save updated memory back to state
                updated_memory_data = temp_agent.get_memory_data_for_persistence()
                response_updates["flow_builder_memory_data"] = updated_memory_data
                
                validation_status = "PASSED" if validation_passed else "FAILED"
                print(f"🧠 MEMORY: Updated attempt #{attempt_number} with validation result ({validation_status})")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not update Flow Builder memory with validation result: {e}")
        
        if validation_response.success and validation_response.is_valid:
            print("✅ Flow validation passed - ready for deployment")
            # Flow is valid, can proceed to deployment
            
        elif validation_response.success and not validation_response.is_valid:
            print(f"🔄 Flow validation failed - preparing retry with {validation_response.error_count} errors")
            
            # Check if we should retry
            should_retry = validation_agent.should_retry_flow_build(validation_response)
            max_retries = state.get("max_build_deploy_retries", 3)
            
            if should_retry and build_deploy_retry_count < max_retries:
                print(f"🛠️  Creating retry context for validation fixes (attempt #{build_deploy_retry_count + 1})")
                
                # Create enhanced retry context with validation errors
                retry_context = validation_agent.create_retry_context(
                    validation_response=validation_response,
                    original_request=flow_build_response.input_request,
                    current_retry_count=build_deploy_retry_count,
                    failed_flow_xml=flow_build_response.flow_xml
                )
                
                # Update the flow build request with retry context
                retry_request = flow_build_response.input_request.model_copy()
                retry_request.retry_context = retry_context
                
                # Update state for retry
                response_updates["current_flow_build_request"] = retry_request.model_dump()
                response_updates["build_deploy_retry_count"] = build_deploy_retry_count + 1
                response_updates["validation_requires_retry"] = True
                
                print(f"📝 Retry request prepared with {len(retry_context['specific_fixes_needed'])} specific fixes")
                
            else:
                print(f"🛑 Maximum retries ({max_retries}) reached for validation fixes, ending workflow")
                response_updates["error_message"] = f"Flow validation failed after {build_deploy_retry_count} retries"
                response_updates["validation_requires_retry"] = False
        
        else:
            print(f"❌ Flow validation tool failed: {validation_response.error_message}")
            response_updates["error_message"] = f"Flow validation tool error: {validation_response.error_message}"
            response_updates["validation_requires_retry"] = False
        
    except Exception as e:
        error_message = f"Flow validation agent error: {str(e)}"
        print(f"❌ {error_message}")
        logger.error(error_message)
        response_updates["error_message"] = error_message
        response_updates["validation_requires_retry"] = False
    
    # Update state
    updated_state = state.copy()
    for key, value in response_updates.items():
        updated_state[key] = value
    
    return updated_state 