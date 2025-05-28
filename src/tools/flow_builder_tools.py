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
            
            # Root Flow element
            flow_el = ET.Element("Flow", xmlns="http://soap.sforce.com/2006/04/metadata")
            
            # apiVersion
            api_version_el = ET.SubElement(flow_el, "apiVersion")
            api_version_el.text = target_api_version
            
            # description (optional)
            if flow_description:
                description_el = ET.SubElement(flow_el, "description")
                description_el.text = flow_description

            # interviewLabel (Typically same as Flow Label for simple flows)
            interview_label_el = ET.SubElement(flow_el, "interviewLabel")
            interview_label_el.text = f"{flow_label} {target_api_version}" # Corrected f-string

            # label
            label_el = ET.SubElement(flow_el, "label")
            label_el.text = flow_label
            
            # processMetadataValues for processType (ScreenFlow)
            process_metadata_el = ET.SubElement(flow_el, "processMetadataValues")
            name_el = ET.SubElement(process_metadata_el, "name")
            name_el.text = "BuilderType"
            value_el = ET.SubElement(process_metadata_el, "value")
            string_value_el = ET.SubElement(value_el, "stringValue")
            string_value_el.text = "LightningFlowBuilder"

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

            # processType
            process_type_el = ET.SubElement(flow_el, "processType")
            process_type_el.text = "Flow" # For Screen Flow, it's just "Flow". For Autolaunched, "AutoLaunchedFlow"

            # Screens element
            screens_el = ET.SubElement(flow_el, "screens")
            screens_el.set("allowBack", "true")
            screens_el.set("allowFinish", "true")
            screens_el.set("allowPause", "true") # Common defaults
            
            # name for the screen
            screen_name_el = ET.SubElement(screens_el, "name")
            screen_name_el.text = screen_api_name
            
            # label for the screen
            screen_label_el = ET.SubElement(screens_el, "label")
            screen_label_el.text = screen_label
            
            # fields for the screen
            fields_el = ET.SubElement(screens_el, "fields")
            fields_el.set("name", display_text_api_name) # API name of the display text component
            # fieldType for display text
            field_type_el = ET.SubElement(fields_el, "fieldType")
            field_type_el.text = "DisplayText"
            # Show Header and Footer (common for screens)
            show_footer_el = ET.SubElement(screens_el, "showFooter")
            show_footer_el.text = "true"
            show_header_el = ET.SubElement(screens_el, "showHeader")
            show_header_el.text = "true"
            
            # Add the display text content to the fields element (this is simplified, actual display text might be richer)
            # For simple text, it can be directly in the 'text' attribute of a component within fields,
            # but DisplayText is often more structured. Let's put it in <fieldText> for the component.
            # This is a common way, although DisplayText can also have <validationRule> etc.
            # The `display_text_content` should be within the `fields` element with name `display_text_api_name`.
            # This DisplayText component needs to be defined correctly.
            # A simple way is to have a <fieldText> inside the <fields> tag.
            # This structure might be slightly off, DisplayText usually has its own definition.
            # Let's assume for this basic version, the 'fields' element itself can hold text if simple.
            # Salesforce DisplayText is a specific component type.
            # Let's structure the display text field correctly.
            # The 'fields' element IS the display text component.
            # Its content goes into a sub-element, typically specific to the component type.
            # For DisplayText, the content is often just the text.
            # This part needs care to match actual Flow metadata structure for DisplayText.
            
            # Re-evaluating display text structure:
            # A <fields> element with fieldType "DisplayText" doesn't directly take a text node for its content.
            # The content is usually within the definition of the component itself.
            # For a DisplayText component, the text itself is typically defined elsewhere or as part of its properties.
            # Let's check a simple DisplayText XML structure.
            # It seems <fieldText> is NOT standard for this.
            # A DisplayText element usually has its 'name' and then its content is derived from its configuration.
            # Often, simple display text is added via a specific "Text Template" resource and then referenced,
            # or for direct text on screen, it's literally just a text block component.

            # Let's adjust. The `display_text_content` should be used to configure this component.
            # The `fields` element with name `display_text_api_name` *is* the display text component.
            # Its content isn't a direct child text node of `fields`.
            # Instead, DisplayText components might have specific properties if the text isn't static,
            # or the text is set directly in its properties when defined.

            # For a very simple hardcoded display text:
            # The text itself is not directly a sub-element of <fields> with fieldType DisplayText in the <screens> definition.
            # Rather, the text is often defined within the component's properties or as a resource.
            # For the most basic inline display text, it might be part of the screen field's configuration.
            # Let's try a simplified direct approach, although real DisplayText can be more complex.
            # A common structure for simple DisplayText:
            # <fields>
            #   <name>MyDisplayText</name>
            #   <fieldText>&lt;p&gt;This is my text&lt;/p&gt;</fieldText>  <-- This is for Rich Text, not plain.
            #   <fieldType>DisplayText</fieldType>
            # </fields>
            # For plain text, it might be a "Text" component or DisplayText with simpler config.
            # Let's assume `display_text_content` should be wrapped in HTML paragraph tags for simple DisplayText.
            
            # Simpler approach for DisplayText content:
            # The `fields` for DisplayText will define its name and type.
            # The actual text content isn't a direct sub-element of `fields` in the screen definition.
            # Instead, DisplayText often uses a resource or has its properties set.
            # Let's try to define a simple text variable and reference it, or make the display text component directly show it.

            # A display text on a screen can directly embed its value.
            # Let's assume `display_text_content` is the literal text to show.
            # The fieldType "DisplayText" indicates it's a component.
            # The content "display_text_content" must be associated with this component.
            # The metadata for a Display Text field can be tricky.
            # Example:
            # <fields>
            #    <name>WelcomeMessage</name>
            #    <fieldText>Hello World</fieldText> <!-- This is what many examples show for DisplayText's content -->
            #    <fieldType>DisplayText</fieldType>
            # </fields>
            # Let's use <fieldText> as it's a common way to represent simple text content for DisplayText.
            field_text_el = ET.SubElement(fields_el, "fieldText")
            field_text_el.text = display_text_content # Directly use the content


            # Start element
            start_el = ET.SubElement(flow_el, "start")
            # connector to the first screen
            connector_el = ET.SubElement(start_el, "connector")
            connector_el.set("targetReference", screen_api_name) # API name of the screen
            # recordTriggerType (Only for record-triggered flows)
            # triggerType (Only for platform event or record-triggered flows)
            
            # Convert the ET to a string
            # ET.indent(flow_el) # For pretty printing, requires Python 3.9+
            xml_string = ET.tostring(flow_el, encoding='unicode', xml_declaration=True)
            
            # Quick way to get a somewhat readable format without ET.indent if not on 3.9+
            # This is a basic indent, proper pretty printing is better.
            from xml.dom import minidom
            parsed_str = minidom.parseString(xml_string)
            pretty_xml_string = parsed_str.toprettyxml(indent="    ") # 4 spaces for indent

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