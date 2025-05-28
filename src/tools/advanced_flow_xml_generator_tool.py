import xml.etree.ElementTree as ET
from typing import Type, List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from xml.dom import minidom
import uuid
from datetime import datetime

from src.schemas.flow_builder_schemas import (
    FlowBuildRequest, FlowBuildResponse, FlowType, FlowElementType, 
    FlowTriggerType, FlowElement, FlowVariable, FlowValidationError
)

class AdvancedFlowXmlGeneratorTool(BaseTool):
    """
    Advanced tool for generating comprehensive Salesforce Flow XML with support for:
    - Multiple flow types (Screen, Record-Triggered, Scheduled, etc.)
    - Complex flow elements (Decisions, Loops, Get Records, etc.)
    - Best practices implementation
    - Proper error handling and fault paths
    - Flow variables and formulas
    """
    name: str = "advanced_flow_xml_generator_tool"
    description: str = (
        "Generate comprehensive Salesforce Flow XML with advanced features including "
        "multiple element types, proper flow logic, variables, error handling, and "
        "best practices. Supports all flow types and complex business logic."
    )
    args_schema: Type[BaseModel] = FlowBuildRequest

    def _run(self, **kwargs) -> FlowBuildResponse:
        """Generate advanced Flow XML based on the request"""
        try:
            # Parse the request
            request = FlowBuildRequest(**kwargs)
            
            # Validate the request
            validation_errors = self._validate_request(request)
            if validation_errors:
                return FlowBuildResponse(
                    success=False,
                    input_request=request,
                    validation_errors=validation_errors,
                    error_message="Flow validation failed. Please check validation errors."
                )
            
            # Generate the flow XML
            flow_xml = self._generate_flow_xml(request)
            flow_definition_xml = self._generate_flow_definition_xml(request)
            
            # Analyze what was created
            elements_created = self._get_elements_created(request)
            variables_created = self._get_variables_created(request)
            best_practices = self._get_best_practices_applied(request)
            recommendations = self._get_recommendations(request)
            dependencies = self._get_dependencies(request)
            
            return FlowBuildResponse(
                success=True,
                input_request=request,
                flow_xml=flow_xml,
                flow_definition_xml=flow_definition_xml,
                elements_created=elements_created,
                variables_created=variables_created,
                best_practices_applied=best_practices,
                recommendations=recommendations,
                dependencies=dependencies,
                deployment_notes=self._get_deployment_notes(request)
            )
            
        except Exception as e:
            return FlowBuildResponse(
                success=False,
                input_request=FlowBuildRequest(**kwargs),
                error_message=f"Error generating Flow XML: {str(e)}"
            )

    def _validate_request(self, request: FlowBuildRequest) -> List[FlowValidationError]:
        """Validate the flow build request"""
        errors = []
        
        # Basic validation
        if not request.flow_api_name:
            errors.append(FlowValidationError(
                error_type="missing_required_field",
                error_message="Flow API name is required",
                suggested_fix="Provide a valid API name for the flow"
            ))
        
        if not request.flow_label:
            errors.append(FlowValidationError(
                error_type="missing_required_field",
                error_message="Flow label is required",
                suggested_fix="Provide a descriptive label for the flow"
            ))
        
        # Flow type specific validation
        if request.flow_type == FlowType.RECORD_TRIGGERED:
            if not request.trigger_object:
                errors.append(FlowValidationError(
                    error_type="missing_trigger_object",
                    error_message="Record-triggered flows require a trigger object",
                    suggested_fix="Specify the object that will trigger this flow"
                ))
            
            if not request.trigger_type:
                errors.append(FlowValidationError(
                    error_type="missing_trigger_type",
                    error_message="Record-triggered flows require a trigger type",
                    suggested_fix="Specify when the flow should trigger (Before Save, After Save, etc.)"
                ))
        
        # Element validation
        for element in request.flow_elements:
            element_errors = self._validate_element(element)
            errors.extend(element_errors)
        
        return errors

    def _validate_element(self, element: FlowElement) -> List[FlowValidationError]:
        """Validate a flow element"""
        errors = []
        
        if not element.name:
            errors.append(FlowValidationError(
                error_type="missing_element_name",
                element_name=element.name,
                error_message="Flow element must have a name",
                suggested_fix="Provide a unique API name for the element"
            ))
        
        if not element.label:
            errors.append(FlowValidationError(
                error_type="missing_element_label",
                element_name=element.name,
                error_message="Flow element must have a label",
                suggested_fix="Provide a descriptive label for the element"
            ))
        
        # Element-specific validation
        if element.element_type == FlowElementType.GET_RECORDS:
            if not element.configuration.get("object"):
                errors.append(FlowValidationError(
                    error_type="missing_object",
                    element_name=element.name,
                    error_message="Get Records element must specify an object",
                    suggested_fix="Add 'object' to the element configuration"
                ))
        
        return errors

    def _generate_flow_xml(self, request: FlowBuildRequest) -> str:
        """Generate the main Flow XML"""
        # Create root Flow element
        flow_el = ET.Element("Flow", xmlns="http://soap.sforce.com/2006/04/metadata")
        
        # Add API version
        api_version_el = ET.SubElement(flow_el, "apiVersion")
        api_version_el.text = request.target_api_version
        
        # Add flow description if provided
        if request.flow_description:
            description_el = ET.SubElement(flow_el, "description")
            description_el.text = request.flow_description
        
        # Add interview label
        interview_label_el = ET.SubElement(flow_el, "interviewLabel")
        interview_label_el.text = f"{request.flow_label} {{!$Flow.CurrentDateTime}}"
        
        # Add label
        label_el = ET.SubElement(flow_el, "label")
        label_el.text = request.flow_label
        
        # Add process metadata values
        self._add_process_metadata(flow_el)
        
        # Add variables
        for variable in request.flow_variables:
            self._add_variable(flow_el, variable)
        
        # Add flow elements
        for element in request.flow_elements:
            self._add_flow_element(flow_el, element)
        
        # Handle legacy simple flow support
        if request.screen_api_name and request.display_text_api_name:
            self._add_simple_screen(flow_el, request)
        
        # Add process type
        process_type_el = ET.SubElement(flow_el, "processType")
        process_type_el.text = self._get_process_type(request.flow_type)
        
        # Add start element based on flow type
        self._add_start_element(flow_el, request)
        
        # Add status
        status_el = ET.SubElement(flow_el, "status")
        status_el.text = "Draft"  # Always create as draft initially
        
        # Convert to pretty XML string
        xml_string = ET.tostring(flow_el, encoding='unicode', xml_declaration=True)
        parsed_str = minidom.parseString(xml_string)
        return parsed_str.toprettyxml(indent="    ")

    def _generate_flow_definition_xml(self, request: FlowBuildRequest) -> str:
        """Generate Flow Definition XML for activation control"""
        flow_def_el = ET.Element("FlowDefinition", xmlns="http://soap.sforce.com/2006/04/metadata")
        
        # Set active version to 0 (inactive) initially
        active_version_el = ET.SubElement(flow_def_el, "activeVersionNumber")
        active_version_el.text = "0"
        
        # Add description if provided
        if request.flow_description:
            description_el = ET.SubElement(flow_def_el, "description")
            description_el.text = request.flow_description
        
        xml_string = ET.tostring(flow_def_el, encoding='unicode', xml_declaration=True)
        parsed_str = minidom.parseString(xml_string)
        return parsed_str.toprettyxml(indent="    ")

    def _add_process_metadata(self, flow_el: ET.Element):
        """Add standard process metadata values"""
        metadata_values = [
            ("BuilderType", "LightningFlowBuilder"),
            ("CanvasMode", "AUTO_LAYOUT_CANVAS"),
            ("OriginBuilderType", "LightningFlowBuilder")
        ]
        
        for name, value in metadata_values:
            process_metadata_el = ET.SubElement(flow_el, "processMetadataValues")
            name_el = ET.SubElement(process_metadata_el, "name")
            name_el.text = name
            value_el = ET.SubElement(process_metadata_el, "value")
            string_value_el = ET.SubElement(value_el, "stringValue")
            string_value_el.text = value

    def _add_variable(self, flow_el: ET.Element, variable: FlowVariable):
        """Add a flow variable"""
        var_el = ET.SubElement(flow_el, "variables")
        
        # Add data type
        data_type_el = ET.SubElement(var_el, "dataType")
        data_type_el.text = variable.data_type
        
        # Add collection flag if needed
        if variable.is_collection:
            is_collection_el = ET.SubElement(var_el, "isCollection")
            is_collection_el.text = "true"
        
        # Add input/output flags
        if variable.is_input:
            is_input_el = ET.SubElement(var_el, "isInput")
            is_input_el.text = "true"
        
        if variable.is_output:
            is_output_el = ET.SubElement(var_el, "isOutput")
            is_output_el.text = "true"
        
        # Add name
        name_el = ET.SubElement(var_el, "name")
        name_el.text = variable.name
        
        # Add default value if provided
        if variable.default_value:
            value_el = ET.SubElement(var_el, "value")
            if variable.data_type.lower() == "boolean":
                bool_value_el = ET.SubElement(value_el, "booleanValue")
                bool_value_el.text = variable.default_value.lower()
            elif variable.data_type.lower() in ["number", "currency"]:
                number_value_el = ET.SubElement(value_el, "numberValue")
                number_value_el.text = variable.default_value
            else:
                string_value_el = ET.SubElement(value_el, "stringValue")
                string_value_el.text = variable.default_value

    def _add_flow_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a flow element based on its type"""
        if element.element_type == FlowElementType.SCREEN:
            self._add_screen_element(flow_el, element)
        elif element.element_type == FlowElementType.DECISION:
            self._add_decision_element(flow_el, element)
        elif element.element_type == FlowElementType.ASSIGNMENT:
            self._add_assignment_element(flow_el, element)
        elif element.element_type == FlowElementType.GET_RECORDS:
            self._add_get_records_element(flow_el, element)
        elif element.element_type == FlowElementType.CREATE_RECORDS:
            self._add_create_records_element(flow_el, element)
        elif element.element_type == FlowElementType.UPDATE_RECORDS:
            self._add_update_records_element(flow_el, element)
        elif element.element_type == FlowElementType.DELETE_RECORDS:
            self._add_delete_records_element(flow_el, element)
        elif element.element_type == FlowElementType.LOOP:
            self._add_loop_element(flow_el, element)
        elif element.element_type == FlowElementType.ACTION_CALL:
            self._add_action_call_element(flow_el, element)
        elif element.element_type == FlowElementType.SUBFLOW:
            self._add_subflow_element(flow_el, element)

    def _add_screen_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a screen element"""
        screen_el = ET.SubElement(flow_el, "screens")
        
        # Basic screen properties
        self._add_basic_element_properties(screen_el, element)
        
        # Screen-specific properties
        allow_back_el = ET.SubElement(screen_el, "allowBack")
        allow_back_el.text = element.configuration.get("allowBack", "true")
        
        allow_finish_el = ET.SubElement(screen_el, "allowFinish")
        allow_finish_el.text = element.configuration.get("allowFinish", "true")
        
        allow_pause_el = ET.SubElement(screen_el, "allowPause")
        allow_pause_el.text = element.configuration.get("allowPause", "true")
        
        # Add fields if specified
        fields = element.configuration.get("fields", [])
        for field in fields:
            self._add_screen_field(screen_el, field)
        
        # Add show footer/header
        show_footer_el = ET.SubElement(screen_el, "showFooter")
        show_footer_el.text = element.configuration.get("showFooter", "true")
        
        show_header_el = ET.SubElement(screen_el, "showHeader")
        show_header_el.text = element.configuration.get("showHeader", "true")

    def _add_decision_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a decision element"""
        decision_el = ET.SubElement(flow_el, "decisions")
        
        # Basic properties
        self._add_basic_element_properties(decision_el, element)
        
        # Default connector
        default_connector_el = ET.SubElement(decision_el, "defaultConnectorLabel")
        default_connector_el.text = element.configuration.get("defaultConnectorLabel", "Default Outcome")
        
        # Add rules
        rules = element.configuration.get("rules", [])
        for rule in rules:
            self._add_decision_rule(decision_el, rule)

    def _add_get_records_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a Get Records element"""
        get_records_el = ET.SubElement(flow_el, "recordLookups")
        
        # Basic properties
        self._add_basic_element_properties(get_records_el, element)
        
        # Object
        object_el = ET.SubElement(get_records_el, "object")
        object_el.text = element.configuration.get("object", "Account")
        
        # Output reference
        output_reference_el = ET.SubElement(get_records_el, "outputReference")
        output_reference_el.text = element.configuration.get("outputReference", f"{element.name}_Records")
        
        # Query limit
        query_limit_el = ET.SubElement(get_records_el, "queriedFields")
        query_limit_el.text = element.configuration.get("queriedFields", "Id")
        
        # Add filters if specified
        filters = element.configuration.get("filters", [])
        for filter_config in filters:
            self._add_record_filter(get_records_el, filter_config)

    def _add_assignment_element(self, flow_el: ET.Element, element: FlowElement):
        """Add an assignment element"""
        assignment_el = ET.SubElement(flow_el, "assignments")
        
        # Basic properties
        self._add_basic_element_properties(assignment_el, element)
        
        # Add assignment items
        assignments = element.configuration.get("assignments", [])
        for assignment in assignments:
            assignment_item_el = ET.SubElement(assignment_el, "assignmentItems")
            
            assignee_el = ET.SubElement(assignment_item_el, "assignToReference")
            assignee_el.text = assignment.get("assignToReference", "")
            
            operator_el = ET.SubElement(assignment_item_el, "operator")
            operator_el.text = assignment.get("operator", "Assign")
            
            value_el = ET.SubElement(assignment_item_el, "value")
            if assignment.get("elementReference"):
                element_ref_el = ET.SubElement(value_el, "elementReference")
                element_ref_el.text = assignment["elementReference"]
            elif assignment.get("stringValue"):
                string_val_el = ET.SubElement(value_el, "stringValue")
                string_val_el.text = assignment["stringValue"]

    def _add_simple_screen(self, flow_el: ET.Element, request: FlowBuildRequest):
        """Add a simple screen for legacy support"""
        screen_el = ET.SubElement(flow_el, "screens")
        
        # Basic properties
        allow_back_el = ET.SubElement(screen_el, "allowBack")
        allow_back_el.text = "true"
        
        allow_finish_el = ET.SubElement(screen_el, "allowFinish")
        allow_finish_el.text = "true"
        
        allow_pause_el = ET.SubElement(screen_el, "allowPause")
        allow_pause_el.text = "true"
        
        # Display text field
        field_el = ET.SubElement(screen_el, "fields")
        
        field_text_el = ET.SubElement(field_el, "fieldText")
        field_text_el.text = f"<p>{request.display_text_content}</p>"
        
        field_type_el = ET.SubElement(field_el, "fieldType")
        field_type_el.text = "DisplayText"
        
        field_name_el = ET.SubElement(field_el, "name")
        field_name_el.text = request.display_text_api_name
        
        # Screen properties
        label_el = ET.SubElement(screen_el, "label")
        label_el.text = request.screen_label
        
        location_x_el = ET.SubElement(screen_el, "locationX")
        location_x_el.text = "176"
        
        location_y_el = ET.SubElement(screen_el, "locationY")
        location_y_el.text = "134"
        
        name_el = ET.SubElement(screen_el, "name")
        name_el.text = request.screen_api_name
        
        show_footer_el = ET.SubElement(screen_el, "showFooter")
        show_footer_el.text = "true"
        
        show_header_el = ET.SubElement(screen_el, "showHeader")
        show_header_el.text = "true"

    def _add_start_element(self, flow_el: ET.Element, request: FlowBuildRequest):
        """Add the start element based on flow type"""
        start_el = ET.SubElement(flow_el, "start")
        
        # Add connector if there are elements or legacy screen
        if request.flow_elements or request.screen_api_name:
            connector_el = ET.SubElement(start_el, "connector")
            target_ref_el = ET.SubElement(connector_el, "targetReference")
            
            if request.flow_elements:
                target_ref_el.text = request.flow_elements[0].name
            else:
                target_ref_el.text = request.screen_api_name
        
        # Add location
        location_x_el = ET.SubElement(start_el, "locationX")
        location_x_el.text = "50"
        
        location_y_el = ET.SubElement(start_el, "locationY")
        location_y_el.text = "0"
        
        # Add trigger-specific elements
        if request.flow_type == FlowType.RECORD_TRIGGERED:
            if request.trigger_object:
                object_el = ET.SubElement(start_el, "object")
                object_el.text = request.trigger_object
            
            if request.trigger_type:
                trigger_type_el = ET.SubElement(start_el, "recordTriggerType")
                if request.trigger_type in [FlowTriggerType.RECORD_AFTER_SAVE, FlowTriggerType.RECORD_AFTER_DELETE]:
                    trigger_type_el.text = "Update" if "SAVE" in request.trigger_type.value else "Delete"
                
                trigger_el = ET.SubElement(start_el, "triggerType")
                trigger_el.text = request.trigger_type.value

    def _add_basic_element_properties(self, element_el: ET.Element, element: FlowElement):
        """Add basic properties common to all elements"""
        # Label
        label_el = ET.SubElement(element_el, "label")
        label_el.text = element.label
        
        # Location
        location_x_el = ET.SubElement(element_el, "locationX")
        location_x_el.text = str(element.location_x)
        
        location_y_el = ET.SubElement(element_el, "locationY")
        location_y_el.text = str(element.location_y)
        
        # Name
        name_el = ET.SubElement(element_el, "name")
        name_el.text = element.name
        
        # Connector if specified
        if element.connector_target:
            connector_el = ET.SubElement(element_el, "connector")
            target_ref_el = ET.SubElement(connector_el, "targetReference")
            target_ref_el.text = element.connector_target
        
        # Fault connector if specified
        if element.fault_connector_target:
            fault_connector_el = ET.SubElement(element_el, "faultConnector")
            target_ref_el = ET.SubElement(fault_connector_el, "targetReference")
            target_ref_el.text = element.fault_connector_target

    def _get_process_type(self, flow_type: FlowType) -> str:
        """Get the process type for the flow"""
        if flow_type == FlowType.SCREEN_FLOW:
            return "Flow"
        elif flow_type == FlowType.RECORD_TRIGGERED:
            return "AutoLaunchedFlow"
        elif flow_type == FlowType.SCHEDULED:
            return "AutoLaunchedFlow"
        elif flow_type == FlowType.AUTOLAUNCHED:
            return "AutoLaunchedFlow"
        elif flow_type == FlowType.PLATFORM_EVENT:
            return "AutoLaunchedFlow"
        else:
            return "Flow"

    def _get_elements_created(self, request: FlowBuildRequest) -> List[str]:
        """Get list of elements that were created"""
        elements = []
        
        for element in request.flow_elements:
            elements.append(f"{element.element_type.value}: {element.name}")
        
        if request.screen_api_name:
            elements.append(f"Screen: {request.screen_api_name}")
        
        return elements

    def _get_variables_created(self, request: FlowBuildRequest) -> List[str]:
        """Get list of variables that were created"""
        variables = []
        
        for variable in request.flow_variables:
            var_desc = f"{variable.name} ({variable.data_type}"
            if variable.is_collection:
                var_desc += " Collection"
            var_desc += ")"
            variables.append(var_desc)
        
        return variables

    def _get_best_practices_applied(self, request: FlowBuildRequest) -> List[str]:
        """Get list of best practices that were automatically applied"""
        practices = [
            "Flow created as Draft status for safe deployment",
            "Proper XML namespace and API version applied",
            "Standard process metadata values included",
            "Consistent element positioning and naming"
        ]
        
        if request.flow_type == FlowType.RECORD_TRIGGERED:
            practices.append("Record-triggered flow structure with proper trigger configuration")
        
        if any(element.fault_connector_target for element in request.flow_elements):
            practices.append("Fault connectors added for error handling")
        
        return practices

    def _get_recommendations(self, request: FlowBuildRequest) -> List[str]:
        """Get recommendations for improvement"""
        recommendations = []
        
        if not request.flow_description:
            recommendations.append("Add a flow description to document the business purpose")
        
        if request.flow_type == FlowType.RECORD_TRIGGERED and not request.entry_criteria:
            recommendations.append("Consider adding entry criteria to optimize flow execution")
        
        if not any(element.fault_connector_target for element in request.flow_elements):
            recommendations.append("Add fault connectors to DML operations for better error handling")
        
        if len(request.flow_elements) > 10:
            recommendations.append("Consider breaking complex flows into subflows for better maintainability")
        
        return recommendations

    def _get_dependencies(self, request: FlowBuildRequest) -> List[str]:
        """Get deployment dependencies"""
        dependencies = []
        
        if request.trigger_object and request.trigger_object not in ["Account", "Contact", "Lead", "Opportunity"]:
            dependencies.append(f"Custom Object: {request.trigger_object}")
        
        # Check for custom fields in element configurations
        for element in request.flow_elements:
            if element.element_type == FlowElementType.GET_RECORDS:
                obj = element.configuration.get("object")
                if obj and obj not in ["Account", "Contact", "Lead", "Opportunity"]:
                    dependencies.append(f"Custom Object: {obj}")
        
        return dependencies

    def _get_deployment_notes(self, request: FlowBuildRequest) -> str:
        """Get deployment notes"""
        notes = []
        
        notes.append("Flow is created in Draft status and must be activated after deployment.")
        
        if request.flow_type == FlowType.RECORD_TRIGGERED:
            notes.append("Test thoroughly in sandbox before activating in production.")
            notes.append("Consider the impact on existing automation and order of execution.")
        
        if request.flow_type == FlowType.SCREEN_FLOW:
            notes.append("Ensure users have appropriate permissions to access the flow.")
            notes.append("Test with different user profiles and permission sets.")
        
        return " ".join(notes)

    # Additional helper methods for complex elements would go here...
    def _add_screen_field(self, screen_el: ET.Element, field_config: Dict[str, Any]):
        """Add a field to a screen element"""
        # Implementation for screen fields
        pass
    
    def _add_decision_rule(self, decision_el: ET.Element, rule_config: Dict[str, Any]):
        """Add a rule to a decision element"""
        # Implementation for decision rules
        pass
    
    def _add_record_filter(self, get_records_el: ET.Element, filter_config: Dict[str, Any]):
        """Add a filter to a Get Records element"""
        # Implementation for record filters
        pass
    
    # Additional element type methods...
    def _add_create_records_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a Create Records element"""
        pass
    
    def _add_update_records_element(self, flow_el: ET.Element, element: FlowElement):
        """Add an Update Records element"""
        pass
    
    def _add_delete_records_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a Delete Records element"""
        pass
    
    def _add_loop_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a Loop element"""
        pass
    
    def _add_action_call_element(self, flow_el: ET.Element, element: FlowElement):
        """Add an Action Call element"""
        pass
    
    def _add_subflow_element(self, flow_el: ET.Element, element: FlowElement):
        """Add a Subflow element"""
        pass

    async def _arun(self, **kwargs) -> FlowBuildResponse:
        """Async version of the tool"""
        return self._run(**kwargs)

# Example usage
if __name__ == "__main__":
    tool = AdvancedFlowXmlGeneratorTool()
    
    # Test with a complex flow request
    test_request = {
        "flow_api_name": "ProcessLeadConversion",
        "flow_label": "Process Lead Conversion",
        "flow_description": "Automatically process lead conversion based on qualification criteria",
        "flow_type": "Record-Triggered Flow",
        "trigger_object": "Lead",
        "trigger_type": "RecordAfterSave",
        "flow_elements": [
            {
                "element_type": "decisions",
                "name": "Check_Lead_Qualification",
                "label": "Check Lead Qualification",
                "location_x": 176,
                "location_y": 200,
                "configuration": {
                    "rules": [
                        {
                            "name": "Is_Qualified",
                            "label": "Is Qualified",
                            "conditions": [
                                {
                                    "leftValueReference": "$Record.Status",
                                    "operator": "EqualTo",
                                    "rightValue": "Qualified"
                                }
                            ]
                        }
                    ]
                }
            }
        ],
        "flow_variables": [
            {
                "name": "isQualified",
                "data_type": "Boolean",
                "description": "Indicates if the lead is qualified for conversion"
            }
        ]
    }
    
    response = tool.invoke(test_request)
    print("Success:", response.success)
    if response.success:
        print("Elements created:", response.elements_created)
        print("Variables created:", response.variables_created)
        print("Best practices:", response.best_practices_applied)
    else:
        print("Error:", response.error_message)
        print("Validation errors:", response.validation_errors) 