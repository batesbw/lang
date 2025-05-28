import xml.etree.ElementTree as ET
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from src.schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse

class BasicFlowXmlGeneratorTool(BaseTool):
    """
    A LangChain tool to generate the XML for a basic Salesforce Screen Flow.
    
    The generated Flow will contain:
    - One screen.
    - One display text component on that screen.
    """
    name: str = "basic_flow_xml_generator_tool"
    description: str = (
        "Generates XML for a simple Salesforce Screen Flow based on structured input. "
        "The Flow will have one screen with a display text component. "
        "Input includes API names for Flow, screen, display text, labels, and content."
    )
    args_schema: Type[BaseModel] = FlowBuildRequest

    def _run(
        self, 
        flow_api_name: str,
        flow_label: str,
        screen_api_name: str,
        screen_label: str,
        display_text_api_name: str,
        display_text_content: str,
        target_api_version: str,
        flow_description: str | None = None,
        **kwargs # To absorb any other potential fields if FlowBuildRequest is expanded
    ) -> FlowBuildResponse:
        """Execute the Flow XML generation process."""
        
        input_request_data = {
            "flow_api_name": flow_api_name,
            "flow_label": flow_label,
            "flow_description": flow_description,
            "screen_api_name": screen_api_name,
            "screen_label": screen_label,
            "display_text_api_name": display_text_api_name,
            "display_text_content": display_text_content,
            "target_api_version": target_api_version
        }
        current_request = FlowBuildRequest(**input_request_data)

        try:
            # --- XML Generation Logic using xml.etree.ElementTree ---
            # Based on the actual Salesforce Flow metadata structure retrieved from MultiAgentTestFlow1
            
            # Root Flow element
            flow_el = ET.Element("Flow", xmlns="http://soap.sforce.com/2006/04/metadata")
            
            # apiVersion
            api_version_el = ET.SubElement(flow_el, "apiVersion")
            api_version_el.text = target_api_version
            
            # interviewLabel (matches the pattern from retrieved Flow)
            interview_label_el = ET.SubElement(flow_el, "interviewLabel")
            interview_label_el.text = f"{flow_label} {{!$Flow.CurrentDateTime}}"

            # label
            label_el = ET.SubElement(flow_el, "label")
            label_el.text = flow_label
            
            # processMetadataValues (exactly as in retrieved Flow)
            process_metadata_el1 = ET.SubElement(flow_el, "processMetadataValues")
            name_el1 = ET.SubElement(process_metadata_el1, "name")
            name_el1.text = "BuilderType"
            value_el1 = ET.SubElement(process_metadata_el1, "value")
            string_value_el1 = ET.SubElement(value_el1, "stringValue")
            string_value_el1.text = "LightningFlowBuilder"

            process_metadata_el2 = ET.SubElement(flow_el, "processMetadataValues")
            name_el2 = ET.SubElement(process_metadata_el2, "name")
            name_el2.text = "CanvasMode"
            value_el2 = ET.SubElement(process_metadata_el2, "value")
            string_value_el2 = ET.SubElement(value_el2, "stringValue")
            string_value_el2.text = "AUTO_LAYOUT_CANVAS"
            
            process_metadata_el3 = ET.SubElement(flow_el, "processMetadataValues")
            name_el3 = ET.SubElement(process_metadata_el3, "name")
            name_el3.text = "OriginBuilderType"
            value_el3 = ET.SubElement(process_metadata_el3, "value")
            string_value_el3 = ET.SubElement(value_el3, "stringValue")
            string_value_el3.text = "LightningFlowBuilder"

            # processType (exactly as in retrieved Flow)
            process_type_el = ET.SubElement(flow_el, "processType")
            process_type_el.text = "Flow"

            # screens (exactly matching the retrieved Flow structure)
            screens_el = ET.SubElement(flow_el, "screens")
            
            # allowBack, allowFinish, allowPause
            allow_back_el = ET.SubElement(screens_el, "allowBack")
            allow_back_el.text = "true"
            allow_finish_el = ET.SubElement(screens_el, "allowFinish")
            allow_finish_el.text = "true"
            allow_pause_el = ET.SubElement(screens_el, "allowPause")
            allow_pause_el.text = "true"
            
            # fields (DisplayText component)
            fields_el = ET.SubElement(screens_el, "fields")
            
            # fieldText (the actual content)
            field_text_el = ET.SubElement(fields_el, "fieldText")
            field_text_el.text = f"<p>{display_text_content}</p>"
            
            # fieldType
            field_type_el = ET.SubElement(fields_el, "fieldType")
            field_type_el.text = "DisplayText"
            
            # name (API name of the display text component)
            field_name_el = ET.SubElement(fields_el, "name")
            field_name_el.text = display_text_api_name
            
            # label for the screen
            screen_label_el = ET.SubElement(screens_el, "label")
            screen_label_el.text = screen_label
            
            # locationX and locationY (from retrieved Flow)
            location_x_el = ET.SubElement(screens_el, "locationX")
            location_x_el.text = "176"
            location_y_el = ET.SubElement(screens_el, "locationY")
            location_y_el.text = "134"
            
            # name for the screen
            screen_name_el = ET.SubElement(screens_el, "name")
            screen_name_el.text = screen_api_name
            
            # showFooter and showHeader
            show_footer_el = ET.SubElement(screens_el, "showFooter")
            show_footer_el.text = "true"
            show_header_el = ET.SubElement(screens_el, "showHeader")
            show_header_el.text = "true"

            # start element (exactly as in retrieved Flow)
            start_el = ET.SubElement(flow_el, "start")
            
            # connector
            connector_el = ET.SubElement(start_el, "connector")
            target_ref_el = ET.SubElement(connector_el, "targetReference")
            target_ref_el.text = screen_api_name
            
            # locationX and locationY for start
            start_location_x_el = ET.SubElement(start_el, "locationX")
            start_location_x_el.text = "50"
            start_location_y_el = ET.SubElement(start_el, "locationY")
            start_location_y_el.text = "0"
            
            # Convert the ET to a string
            xml_string = ET.tostring(flow_el, encoding='unicode', xml_declaration=True)
            
            # Pretty print using minidom
            from xml.dom import minidom
            parsed_str = minidom.parseString(xml_string)
            pretty_xml_string = parsed_str.toprettyxml(indent="    ")

            return FlowBuildResponse(
                success=True, 
                input_request=current_request, 
                flow_xml=pretty_xml_string
            )

        except Exception as e:
            return FlowBuildResponse(
                success=False, 
                input_request=current_request,
                error_message=f"Error generating Flow XML: {str(e)}"
            )

    async def _arun(
        self, 
        flow_api_name: str,
        flow_label: str,
        screen_api_name: str,
        screen_label: str,
        display_text_api_name: str,
        display_text_content: str,
        target_api_version: str,
        flow_description: str | None = None,
        **kwargs
    ) -> FlowBuildResponse:
        """Asynchronously execute the Flow XML generation. Wraps sync version for now."""
        # For true async, XML generation logic itself might need to be async
        # if it involved I/O, but for CPU-bound ElementTree, this is fine.
        return self._run(
            flow_api_name=flow_api_name,
            flow_label=flow_label,
            flow_description=flow_description,
            screen_api_name=screen_api_name,
            screen_label=screen_label,
            display_text_api_name=display_text_api_name,
            display_text_content=display_text_content,
            target_api_version=target_api_version,
            **kwargs
        )

# Example Usage (for local testing of the tool structure)
if __name__ == "__main__":
    tool = BasicFlowXmlGeneratorTool()

    # Valid input
    valid_input_data = {
        "flow_api_name": "TestFlowTool1",
        "flow_label": "Test Flow Tool 1",
        "flow_description": "A test flow generated by the tool.",
        "screen_api_name": "ScreenA",
        "screen_label": "Screen A Label",
        "display_text_api_name": "DisplayTextA",
        "display_text_content": "Hello from the tool!",
        "target_api_version": "59.0"
    }
    response = tool.invoke(valid_input_data)
    print("--- Valid Input Response ---")
    if response.success:
        print("Successfully generated XML (placeholder):")
        print(response.flow_xml)
    else:
        print(f"Error: {response.error_message}")
    print("Input request:", response.input_request.model_dump_json(indent=2))
    
    print("\n--- Test with Pydantic model directly ---")
    request_model = FlowBuildRequest(**valid_input_data)
    response_direct_model = tool.invoke(request_model.model_dump()) # invoke expects dict
    if response_direct_model.success:
        print("Success (direct model):")
        # print(response_direct_model.flow_xml)
    else:
        print(f"Error (direct model): {response_direct_model.error_message}")

    # Example of how the agent might call it using .run() which takes keyword args
    print("\n--- Test with .run() method (simulating agent call) ---")
    run_response = tool.run(**valid_input_data) # .run() passes args as keywords
    print("Run response type:", type(run_response)) # Should be FlowBuildResponse
    if isinstance(run_response, FlowBuildResponse) and run_response.success:
        print("Success (.run())")
        # print(run_response.flow_xml)
    elif isinstance(run_response, FlowBuildResponse):
        print(f"Error (.run()): {run_response.error_message}")
    else:
        print("Unexpected response type from .run()") 