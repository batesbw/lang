from typing import Type, List, Dict, Any, Optional, Tuple
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

from src.schemas.flow_builder_schemas import FlowRepairRequest, FlowRepairResponse

class FlowRepairTool(BaseTool):
    """
    Tool that analyzes and repairs common Salesforce Flow deployment errors,
    validation issues, and best practice violations.
    """
    name: str = "flow_repair_tool"
    description: str = (
        "Analyze and repair Salesforce Flow XML for common deployment errors, "
        "validation issues, and best practice violations. Provides automated "
        "fixes for known issues and detailed explanations of repairs made."
    )
    args_schema: Type[BaseModel] = FlowRepairRequest
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        super().__init__()
        self.llm = llm
        self._setup_error_patterns()
    
    def _setup_error_patterns(self):
        """Setup patterns for common flow errors"""
        self.error_patterns = {
            "insufficient_access_rights": {
                "patterns": [
                    r"insufficient access rights on cross-reference id",
                    r"insufficient access rights",
                    r"access denied"
                ],
                "repair_method": self._repair_access_rights
            },
            "invalid_version_number": {
                "patterns": [
                    r"invalid version number",
                    r"version.*not found",
                    r"flow version.*does not exist"
                ],
                "repair_method": self._repair_version_issues
            },
            "active_flow_overwrite": {
                "patterns": [
                    r"active.*cannot be overwritten",
                    r"flow is active",
                    r"cannot overwrite active flow"
                ],
                "repair_method": self._repair_active_flow_issues
            },
            "missing_dependencies": {
                "patterns": [
                    r"field.*does not exist",
                    r"object.*does not exist",
                    r"custom field.*not found",
                    r"invalid field"
                ],
                "repair_method": self._repair_missing_dependencies
            },
            "invalid_references": {
                "patterns": [
                    r"invalid element reference",
                    r"element.*not found",
                    r"connector.*invalid"
                ],
                "repair_method": self._repair_invalid_references
            },
            "validation_errors": {
                "patterns": [
                    r"validation error",
                    r"required field missing",
                    r"invalid configuration"
                ],
                "repair_method": self._repair_validation_errors
            },
            "governor_limits": {
                "patterns": [
                    r"too many.*elements",
                    r"execution limit",
                    r"governor limit"
                ],
                "repair_method": self._repair_governor_limits
            }
        }
    
    def _run(
        self,
        flow_xml: str,
        error_messages: List[str],
        error_context: Optional[str] = None,
        target_org_info: Optional[Dict[str, Any]] = None
    ) -> FlowRepairResponse:
        """Repair flow based on error messages"""
        try:
            # Parse the flow XML
            root = ET.fromstring(flow_xml)
            
            # Analyze errors and determine repair strategies
            repairs_needed = self._analyze_errors(error_messages)
            
            # Apply repairs
            repairs_made = []
            remaining_issues = []
            repaired_xml = flow_xml
            
            for error_type, repair_info in repairs_needed.items():
                try:
                    repair_result = repair_info["repair_method"](
                        root, repair_info["messages"], target_org_info
                    )
                    
                    if repair_result["success"]:
                        repairs_made.extend(repair_result["repairs"])
                        # Update the XML
                        repaired_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
                        parsed_str = minidom.parseString(repaired_xml)
                        repaired_xml = parsed_str.toprettyxml(indent="    ")
                    else:
                        remaining_issues.extend(repair_result["issues"])
                        
                except Exception as e:
                    remaining_issues.append(f"Failed to repair {error_type}: {str(e)}")
            
            # Apply general best practices if no specific errors
            if not repairs_needed:
                best_practice_repairs = self._apply_best_practices(root)
                repairs_made.extend(best_practice_repairs)
                repaired_xml = ET.tostring(root, encoding='unicode', xml_declaration=True)
                parsed_str = minidom.parseString(repaired_xml)
                repaired_xml = parsed_str.toprettyxml(indent="    ")
            
            # Generate repair explanation
            explanation = self._generate_repair_explanation(repairs_made, remaining_issues)
            
            return FlowRepairResponse(
                success=len(repairs_made) > 0 or len(remaining_issues) == 0,
                repaired_flow_xml=repaired_xml if repairs_made else None,
                repairs_made=repairs_made,
                remaining_issues=remaining_issues,
                repair_explanation=explanation
            )
            
        except Exception as e:
            return FlowRepairResponse(
                success=False,
                remaining_issues=[f"Error during repair process: {str(e)}"],
                repair_explanation=f"Failed to repair flow: {str(e)}"
            )
    
    def _analyze_errors(self, error_messages: List[str]) -> Dict[str, Dict[str, Any]]:
        """Analyze error messages to determine repair strategies"""
        repairs_needed = {}
        
        for error_msg in error_messages:
            error_msg_lower = error_msg.lower()
            
            for error_type, error_info in self.error_patterns.items():
                for pattern in error_info["patterns"]:
                    if re.search(pattern, error_msg_lower):
                        if error_type not in repairs_needed:
                            repairs_needed[error_type] = {
                                "repair_method": error_info["repair_method"],
                                "messages": []
                            }
                        repairs_needed[error_type]["messages"].append(error_msg)
                        break
        
        return repairs_needed
    
    def _repair_access_rights(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair access rights issues"""
        repairs = []
        issues = []
        
        try:
            # Check for system mode settings
            process_type = root.find("processType")
            if process_type is not None and process_type.text == "AutoLaunchedFlow":
                # Add run in system mode for autolaunched flows
                run_in_mode = root.find("runInMode")
                if run_in_mode is None:
                    run_in_mode = ET.SubElement(root, "runInMode")
                    run_in_mode.text = "SystemModeWithoutSharing"
                    repairs.append("Added system mode execution for autolaunched flow")
                elif run_in_mode.text != "SystemModeWithoutSharing":
                    run_in_mode.text = "SystemModeWithoutSharing"
                    repairs.append("Updated flow to run in system mode")
            
            # Check for field-level security issues
            for element in root.iter():
                if element.tag in ["recordLookups", "recordCreates", "recordUpdates"]:
                    # Add comments about field access requirements
                    if element.find("description") is None:
                        desc = ET.SubElement(element, "description")
                        desc.text = "Ensure running user has access to all referenced fields"
                        repairs.append(f"Added field access note to {element.tag}")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair access rights: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_version_issues(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair version-related issues"""
        repairs = []
        issues = []
        
        try:
            # Ensure proper API version
            api_version = root.find("apiVersion")
            if api_version is None:
                api_version = ET.SubElement(root, "apiVersion")
                api_version.text = "59.0"
                repairs.append("Added missing API version")
            elif float(api_version.text) < 44.0:
                api_version.text = "59.0"
                repairs.append("Updated API version to 59.0 for better flow support")
            
            # Ensure status is set to Active for deployments
            status = root.find("status")
            if status is None:
                status = ET.SubElement(root, "status")
                status.text = "Active"
                repairs.append("Set flow status to Active for deployment")
            elif status.text == "Draft":
                status.text = "Active"
                repairs.append("Changed status from Draft to Active for deployment")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair version issues: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_active_flow_issues(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair active flow overwrite issues"""
        repairs = []
        issues = []
        
        try:
            # Set status to Active
            status = root.find("status")
            if status is not None:
                status.text = "Active"
                repairs.append("Set flow status to Active for deployment")
            
            # Add note about flow definition management
            description = root.find("description")
            if description is None:
                description = ET.SubElement(root, "description")
                description.text = "Flow deployed as Active and ready for use."
            else:
                if "FlowDefinition" in description.text:
                    description.text = description.text.replace("Flow deployed as Draft. Use FlowDefinition to activate.", "Flow deployed as Active and ready for use.")
                else:
                    description.text += " Flow deployed as Active and ready for use."
            
            repairs.append("Updated flow description for Active deployment")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair active flow issues: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_missing_dependencies(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair missing dependency issues"""
        repairs = []
        issues = []
        
        try:
            # Extract field/object names from error messages
            missing_items = []
            for msg in error_messages:
                # Look for field references
                field_match = re.search(r"field['\s]*([a-zA-Z_][a-zA-Z0-9_]*)", msg, re.IGNORECASE)
                if field_match:
                    missing_items.append(f"Field: {field_match.group(1)}")
                
                # Look for object references
                object_match = re.search(r"object['\s]*([a-zA-Z_][a-zA-Z0-9_]*)", msg, re.IGNORECASE)
                if object_match:
                    missing_items.append(f"Object: {object_match.group(1)}")
            
            if missing_items:
                # Add description with dependency information
                description = root.find("description")
                if description is None:
                    description = ET.SubElement(root, "description")
                    description.text = f"Dependencies: {', '.join(missing_items)}"
                else:
                    description.text += f" Dependencies: {', '.join(missing_items)}"
                
                repairs.append(f"Documented missing dependencies: {', '.join(missing_items)}")
            
            # Look for hardcoded IDs and suggest using DeveloperName
            for element in root.iter():
                if element.text and re.match(r'^[a-zA-Z0-9]{15,18}$', element.text.strip()):
                    # This looks like a Salesforce ID
                    if element.tag in ["value", "rightValue"]:
                        # Add comment about using DeveloperName
                        comment = ET.Comment(f" Consider using DeveloperName instead of ID: {element.text} ")
                        element.getparent().insert(0, comment)
                        repairs.append(f"Added comment about hardcoded ID in {element.tag}")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair missing dependencies: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_invalid_references(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair invalid element references"""
        repairs = []
        issues = []
        
        try:
            # Collect all element names
            element_names = set()
            for element in root.iter():
                name_elem = element.find("name")
                if name_elem is not None and name_elem.text:
                    element_names.add(name_elem.text)
            
            # Check connector references
            for connector in root.iter("connector"):
                target_ref = connector.find("targetReference")
                if target_ref is not None and target_ref.text:
                    if target_ref.text not in element_names:
                        # Invalid reference found
                        issues.append(f"Invalid connector reference: {target_ref.text}")
                        # Remove the invalid connector
                        connector.getparent().remove(connector)
                        repairs.append(f"Removed invalid connector to {target_ref.text}")
            
            # Check fault connectors
            for fault_connector in root.iter("faultConnector"):
                target_ref = fault_connector.find("targetReference")
                if target_ref is not None and target_ref.text:
                    if target_ref.text not in element_names:
                        # Invalid reference found
                        issues.append(f"Invalid fault connector reference: {target_ref.text}")
                        # Remove the invalid fault connector
                        fault_connector.getparent().remove(fault_connector)
                        repairs.append(f"Removed invalid fault connector to {target_ref.text}")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair invalid references: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_validation_errors(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair validation errors"""
        repairs = []
        issues = []
        
        try:
            # Ensure required elements exist
            required_elements = {
                "apiVersion": "59.0",
                "label": "Generated Flow",
                "processType": "Flow",
                "status": "Active"
            }
            
            for elem_name, default_value in required_elements.items():
                elem = root.find(elem_name)
                if elem is None:
                    elem = ET.SubElement(root, elem_name)
                    elem.text = default_value
                    repairs.append(f"Added missing required element: {elem_name}")
                elif not elem.text:
                    elem.text = default_value
                    repairs.append(f"Set default value for {elem_name}")
            
            # Ensure all flow elements have required properties
            for element in root.iter():
                if element.tag in ["screens", "decisions", "assignments", "recordLookups", 
                                 "recordCreates", "recordUpdates", "recordDeletes"]:
                    # Check for required name and label
                    name_elem = element.find("name")
                    label_elem = element.find("label")
                    
                    if name_elem is None or not name_elem.text:
                        if name_elem is None:
                            name_elem = ET.SubElement(element, "name")
                        name_elem.text = f"{element.tag}_{len(list(root.iter(element.tag)))}"
                        repairs.append(f"Added missing name to {element.tag}")
                    
                    if label_elem is None or not label_elem.text:
                        if label_elem is None:
                            label_elem = ET.SubElement(element, "label")
                        label_elem.text = f"{element.tag.title()} Element"
                        repairs.append(f"Added missing label to {element.tag}")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair validation errors: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _repair_governor_limits(
        self, 
        root: ET.Element, 
        error_messages: List[str], 
        target_org_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Repair governor limit issues"""
        repairs = []
        issues = []
        
        try:
            # Count flow elements
            element_count = 0
            for element in root.iter():
                if element.tag in ["screens", "decisions", "assignments", "recordLookups", 
                                 "recordCreates", "recordUpdates", "recordDeletes", "loops"]:
                    element_count += 1
            
            if element_count > 50:  # Arbitrary threshold for complex flows
                # Add recommendation for subflows
                description = root.find("description")
                if description is None:
                    description = ET.SubElement(root, "description")
                    description.text = f"Complex flow with {element_count} elements. Consider breaking into subflows."
                else:
                    description.text += f" Complex flow with {element_count} elements. Consider breaking into subflows."
                
                repairs.append(f"Added recommendation to break complex flow into subflows ({element_count} elements)")
            
            # Look for DML operations in loops
            for loop in root.iter("loops"):
                loop_name = loop.find("name")
                loop_name_text = loop_name.text if loop_name is not None else "Unknown"
                
                # Check if there are DML operations after this loop
                # This is a simplified check - in practice, you'd need to trace the flow path
                issues.append(f"Review loop '{loop_name_text}' for DML operations that could cause governor limits")
            
            return {"success": True, "repairs": repairs, "issues": issues}
            
        except Exception as e:
            issues.append(f"Failed to repair governor limit issues: {str(e)}")
            return {"success": False, "repairs": repairs, "issues": issues}
    
    def _apply_best_practices(self, root: ET.Element) -> List[str]:
        """Apply general best practices to the flow"""
        repairs = []
        
        try:
            # Ensure proper process metadata
            metadata_values = [
                ("BuilderType", "LightningFlowBuilder"),
                ("CanvasMode", "AUTO_LAYOUT_CANVAS"),
                ("OriginBuilderType", "LightningFlowBuilder")
            ]
            
            existing_metadata = {}
            for metadata in root.iter("processMetadataValues"):
                name_elem = metadata.find("name")
                if name_elem is not None:
                    existing_metadata[name_elem.text] = metadata
            
            for name, value in metadata_values:
                if name not in existing_metadata:
                    metadata_elem = ET.SubElement(root, "processMetadataValues")
                    name_elem = ET.SubElement(metadata_elem, "name")
                    name_elem.text = name
                    value_elem = ET.SubElement(metadata_elem, "value")
                    string_value_elem = ET.SubElement(value_elem, "stringValue")
                    string_value_elem.text = value
                    repairs.append(f"Added missing process metadata: {name}")
            
            # Ensure interview label exists
            interview_label = root.find("interviewLabel")
            if interview_label is None:
                label = root.find("label")
                label_text = label.text if label is not None else "Flow"
                interview_label = ET.SubElement(root, "interviewLabel")
                interview_label.text = f"{label_text} {{!$Flow.CurrentDateTime}}"
                repairs.append("Added missing interview label")
            
            # Add fault connectors to DML operations if missing
            dml_elements = ["recordCreates", "recordUpdates", "recordDeletes"]
            for element in root.iter():
                if element.tag in dml_elements:
                    fault_connector = element.find("faultConnector")
                    if fault_connector is None:
                        # Add a comment about adding fault handling
                        comment = ET.Comment(" Consider adding fault connector for error handling ")
                        element.insert(0, comment)
                        repairs.append(f"Added comment about fault handling for {element.tag}")
            
        except Exception as e:
            repairs.append(f"Error applying best practices: {str(e)}")
        
        return repairs
    
    def _generate_repair_explanation(self, repairs_made: List[str], remaining_issues: List[str]) -> str:
        """Generate explanation of repairs made"""
        explanation_parts = []
        
        if repairs_made:
            explanation_parts.append("=== REPAIRS MADE ===")
            for i, repair in enumerate(repairs_made, 1):
                explanation_parts.append(f"{i}. {repair}")
            explanation_parts.append("")
        
        if remaining_issues:
            explanation_parts.append("=== REMAINING ISSUES ===")
            explanation_parts.append("The following issues require manual attention:")
            for i, issue in enumerate(remaining_issues, 1):
                explanation_parts.append(f"{i}. {issue}")
            explanation_parts.append("")
        
        if not repairs_made and not remaining_issues:
            explanation_parts.append("No issues found. Flow appears to be valid.")
        
        explanation_parts.append("=== RECOMMENDATIONS ===")
        explanation_parts.append("- Test the flow thoroughly in a sandbox environment")
        explanation_parts.append("- Review all field and object dependencies before deployment")
        explanation_parts.append("- Ensure proper user permissions for flow execution")
        explanation_parts.append("- Consider adding fault paths for error handling")
        
        return "\n".join(explanation_parts)
    
    async def _arun(
        self,
        flow_xml: str,
        error_messages: List[str],
        error_context: Optional[str] = None,
        target_org_info: Optional[Dict[str, Any]] = None
    ) -> FlowRepairResponse:
        """Async version of the tool"""
        return self._run(flow_xml, error_messages, error_context, target_org_info)

# Example usage
if __name__ == "__main__":
    repair_tool = FlowRepairTool()
    
    # Test flow XML with issues
    test_flow_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
        <label>Test Flow</label>
        <processType>Flow</processType>
        <status>Active</status>
        <screens>
            <name>TestScreen</name>
            <allowBack>true</allowBack>
            <allowFinish>true</allowFinish>
            <allowPause>true</allowPause>
            <fields>
                <fieldText><p>Test</p></fieldText>
                <fieldType>DisplayText</fieldType>
                <name>TestText</name>
            </fields>
            <showFooter>true</showFooter>
            <showHeader>true</showHeader>
        </screens>
    </Flow>"""
    
    test_errors = [
        "Flow is active and cannot be overwritten",
        "Missing API version",
        "Invalid field reference: CustomField__c"
    ]
    
    result = repair_tool.invoke({
        "flow_xml": test_flow_xml,
        "error_messages": test_errors
    })
    
    print("Success:", result.success)
    print("Repairs made:", result.repairs_made)
    print("Remaining issues:", result.remaining_issues)
    print("\nExplanation:")
    print(result.repair_explanation) 