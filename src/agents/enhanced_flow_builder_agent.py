from typing import Optional, Dict, Any, List
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from src.tools.flow_knowledge_rag_tool import FlowKnowledgeRAGTool
from src.tools.advanced_flow_xml_generator_tool import AdvancedFlowXmlGeneratorTool
from src.tools.user_story_parser_tool import UserStoryParserTool
from src.tools.flow_repair_tool import FlowRepairTool
from src.schemas.flow_builder_schemas import (
    FlowBuildRequest, FlowBuildResponse, UserStory, FlowType, 
    FlowElementType, FlowTriggerType, FlowElement, FlowVariable
)
from src.state.agent_workforce_state import AgentWorkforceState

class EnhancedFlowBuilderAgent:
    """
    Enhanced Flow Builder Agent that can:
    1. Parse natural language user stories into flow requirements
    2. Leverage RAG knowledge base for best practices
    3. Generate complex flow XML with multiple elements
    4. Repair common deployment errors
    5. Provide comprehensive implementation guidance
    """
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.knowledge_rag = FlowKnowledgeRAGTool()
        self.xml_generator = AdvancedFlowXmlGeneratorTool()
        self.story_parser = UserStoryParserTool(llm)
        self.flow_repair = FlowRepairTool(llm)
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompts for the agent"""
        self.system_prompt = """You are an expert Salesforce Flow Builder Agent. Your mission is to create 
        amazing, production-ready Salesforce Flows from user stories and acceptance criteria.

        Your capabilities include:
        1. Parsing natural language requirements into structured flow specifications
        2. Accessing comprehensive Flow knowledge base for best practices
        3. Generating complex Flow XML with proper structure and elements
        4. Repairing common deployment errors and validation issues
        5. Providing implementation guidance and recommendations

        Key principles:
        - Always follow Salesforce Flow best practices
        - Create maintainable, well-documented flows
        - Consider performance, security, and scalability
        - Provide clear explanations and recommendations
        - Handle errors gracefully with proper fault paths

        When building flows:
        1. First understand the business requirements thoroughly
        2. Consult the knowledge base for relevant best practices
        3. Design the flow structure with proper element sequencing
        4. Generate clean, valid XML with all necessary elements
        5. Validate and repair any issues found
        6. Provide comprehensive deployment guidance
        """
        
        self.flow_design_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """I need you to create a Salesforce Flow based on the following requirements:

            User Story: {user_story}
            Acceptance Criteria: {acceptance_criteria}
            Business Context: {business_context}
            
            Available Objects: {available_objects}
            Available Fields: {available_fields}
            
            Please follow this process:
            1. Parse the requirements to understand what type of flow is needed
            2. Consult your knowledge base for relevant best practices
            3. Design the flow structure with appropriate elements
            4. Generate the flow XML
            5. Validate and provide recommendations
            
            Focus on creating a production-ready flow that follows best practices.""")
        ])

    def run_enhanced_flow_builder_agent(
        self, 
        state: AgentWorkforceState, 
        llm: BaseLanguageModel
    ) -> AgentWorkforceState:
        """
        Enhanced Flow Builder Agent that can handle complex requirements
        """
        print("----- ENHANCED FLOW BUILDER AGENT -----")
        
        # Get the current request
        flow_build_request: Optional[FlowBuildRequest] = state.get("current_flow_build_request")
        response_updates = {}
        
        if not flow_build_request or not isinstance(flow_build_request, FlowBuildRequest):
            print("No valid FlowBuildRequest found in state")
            response_updates["current_flow_build_response"] = FlowBuildResponse(
                success=False,
                input_request=FlowBuildRequest(
                    flow_api_name="unknown",
                    flow_label="unknown"
                ),
                error_message="No valid flow build request provided"
            )
            response_updates["current_flow_build_request"] = None
            return self._update_state(state, response_updates)
        
        try:
            print(f"Processing enhanced flow request: {flow_build_request.flow_api_name}")
            
            # Step 1: If we have a user story, parse it into structured requirements
            if flow_build_request.user_story:
                print("Step 1: Parsing user story into flow requirements...")
                parsed_requirements = self._parse_user_story(flow_build_request)
                
                # Update the request with parsed requirements
                flow_build_request = self._enhance_request_with_parsed_data(
                    flow_build_request, parsed_requirements
                )
            
            # Step 2: Consult knowledge base for relevant best practices
            print("Step 2: Consulting knowledge base for best practices...")
            best_practices = self._get_relevant_best_practices(flow_build_request)
            
            # Step 3: Design flow structure if not already provided
            if not flow_build_request.flow_elements:
                print("Step 3: Designing flow structure...")
                flow_build_request = self._design_flow_structure(
                    flow_build_request, best_practices
                )
            
            # Step 4: Generate the flow XML
            print("Step 4: Generating flow XML...")
            xml_response = self.xml_generator.invoke(flow_build_request.model_dump())
            
            if not xml_response.success:
                print(f"XML generation failed: {xml_response.error_message}")
                response_updates["current_flow_build_response"] = xml_response
                response_updates["current_flow_build_request"] = None
                return self._update_state(state, response_updates)
            
            # Step 5: Validate and repair if needed
            print("Step 5: Validating and repairing flow...")
            final_response = self._validate_and_repair_flow(xml_response, best_practices)
            
            # Step 6: Add implementation guidance
            print("Step 6: Adding implementation guidance...")
            final_response = self._add_implementation_guidance(final_response, best_practices)
            
            print(f"Successfully created flow: {flow_build_request.flow_api_name}")
            print(f"Elements created: {len(final_response.elements_created)}")
            print(f"Best practices applied: {len(final_response.best_practices_applied)}")
            
            response_updates["current_flow_build_response"] = final_response
            response_updates["current_flow_build_request"] = None
            
        except Exception as e:
            error_message = f"Enhanced FlowBuilderAgent error: {str(e)}"
            print(error_message)
            
            response_updates["current_flow_build_response"] = FlowBuildResponse(
                success=False,
                input_request=flow_build_request,
                error_message=error_message
            )
            response_updates["current_flow_build_request"] = None
        
        return self._update_state(state, response_updates)
    
    def _parse_user_story(self, request: FlowBuildRequest):
        """Parse user story into structured requirements"""
        if not request.user_story:
            return None
        
        try:
            # Prepare context for parsing
            existing_objects = []
            existing_fields = {}
            
            # If we have business context about objects, use it
            if hasattr(request, 'business_context') and request.business_context:
                # This is a simplified extraction - in practice, you might have
                # more sophisticated ways to get org metadata
                pass
            
            # Parse the user story
            parsed_requirements = self.story_parser.get_structured_requirements(
                user_story_text=request.user_story.description,
                acceptance_criteria=request.user_story.acceptance_criteria,
                business_context=request.user_story.business_context,
                existing_objects=existing_objects,
                existing_fields=existing_fields
            )
            
            return parsed_requirements
            
        except Exception as e:
            print(f"Error parsing user story: {str(e)}")
            return None
    
    def _enhance_request_with_parsed_data(
        self, 
        original_request: FlowBuildRequest, 
        parsed_requirements
    ) -> FlowBuildRequest:
        """Enhance the original request with parsed data"""
        if not parsed_requirements:
            return original_request
        
        # Create enhanced request
        enhanced_data = original_request.model_dump()
        
        # Update with parsed requirements
        if parsed_requirements.flow_requirements:
            req = parsed_requirements.flow_requirements
            enhanced_data.update({
                "flow_type": req.flow_type,
                "trigger_object": req.trigger_object,
                "trigger_type": req.trigger_type,
                "entry_criteria": req.entry_criteria
            })
        
        # Add suggested elements and variables
        if parsed_requirements.suggested_flow_elements:
            enhanced_data["flow_elements"] = [
                elem.model_dump() for elem in parsed_requirements.suggested_flow_elements
            ]
        
        if parsed_requirements.suggested_variables:
            enhanced_data["flow_variables"] = [
                var.model_dump() for var in parsed_requirements.suggested_variables
            ]
        
        return FlowBuildRequest(**enhanced_data)
    
    def _get_relevant_best_practices(self, request: FlowBuildRequest) -> str:
        """Get relevant best practices from knowledge base"""
        try:
            # Determine what to search for based on flow type and elements
            search_queries = []
            
            # Flow type specific practices
            if request.flow_type:
                search_queries.append(f"best practices for {request.flow_type}")
            
            # Element specific practices
            if request.flow_elements:
                element_types = [elem.element_type for elem in request.flow_elements]
                unique_types = list(set(element_types))
                for elem_type in unique_types:
                    search_queries.append(f"{elem_type} best practices")
            
            # General practices
            search_queries.extend([
                "flow performance optimization",
                "error handling and fault paths",
                "flow security considerations"
            ])
            
            # Collect best practices
            all_practices = []
            for query in search_queries[:3]:  # Limit to avoid too many calls
                practices = self.knowledge_rag.invoke({
                    "query": query,
                    "flow_type": request.flow_type,
                    "max_results": 3
                })
                all_practices.append(practices)
            
            return "\n\n".join(all_practices)
            
        except Exception as e:
            print(f"Error getting best practices: {str(e)}")
            return "Unable to retrieve best practices from knowledge base."
    
    def _design_flow_structure(
        self, 
        request: FlowBuildRequest, 
        best_practices: str
    ) -> FlowBuildRequest:
        """Design flow structure based on requirements and best practices"""
        try:
            # If we already have elements, don't override
            if request.flow_elements:
                return request
            
            # Use LLM to design flow structure
            design_prompt = f"""
            Based on the following flow requirements and best practices, design the flow structure:
            
            Flow Type: {request.flow_type}
            Flow Description: {request.flow_description}
            Trigger Object: {request.trigger_object}
            Trigger Type: {request.trigger_type}
            
            Best Practices:
            {best_practices[:2000]}  # Limit context
            
            Design a logical sequence of flow elements that would implement the requirements.
            Consider proper error handling, performance, and maintainability.
            
            Provide your design as a list of elements with their types, names, and basic configuration.
            """
            
            # This is a simplified design process - in practice, you might want
            # more sophisticated logic here
            suggested_elements = []
            
            # Basic flow structure based on type
            if request.flow_type == FlowType.RECORD_TRIGGERED:
                # Typical record-triggered flow structure
                suggested_elements.extend([
                    FlowElement(
                        element_type=FlowElementType.DECISION,
                        name="Check_Entry_Criteria",
                        label="Check Entry Criteria",
                        description="Validate if the record meets the criteria for processing",
                        location_x=176,
                        location_y=200,
                        configuration={
                            "defaultConnectorLabel": "Default Outcome",
                            "rules": []
                        }
                    )
                ])
                
                # Add assignment for data manipulation
                suggested_elements.append(
                    FlowElement(
                        element_type=FlowElementType.ASSIGNMENT,
                        name="Set_Variables",
                        label="Set Variables",
                        description="Set variables for processing",
                        location_x=176,
                        location_y=350,
                        configuration={
                            "assignments": []
                        }
                    )
                )
            
            elif request.flow_type == FlowType.SCREEN_FLOW:
                # Typical screen flow structure
                suggested_elements.append(
                    FlowElement(
                        element_type=FlowElementType.SCREEN,
                        name="Welcome_Screen",
                        label="Welcome Screen",
                        description="Initial screen for user interaction",
                        location_x=176,
                        location_y=200,
                        configuration={
                            "allowBack": "true",
                            "allowFinish": "true",
                            "allowPause": "true",
                            "fields": []
                        }
                    )
                )
            
            # Update request with suggested elements
            enhanced_data = request.model_dump()
            enhanced_data["flow_elements"] = suggested_elements
            
            return FlowBuildRequest(**enhanced_data)
            
        except Exception as e:
            print(f"Error designing flow structure: {str(e)}")
            return request
    
    def _validate_and_repair_flow(
        self, 
        xml_response: FlowBuildResponse, 
        best_practices: str
    ) -> FlowBuildResponse:
        """Validate and repair the generated flow"""
        try:
            if not xml_response.success or not xml_response.flow_xml:
                return xml_response
            
            # Check for validation errors in the response
            if xml_response.validation_errors:
                print(f"Found {len(xml_response.validation_errors)} validation errors, attempting repair...")
                
                error_messages = [error.error_message for error in xml_response.validation_errors]
                
                repair_response = self.flow_repair.invoke({
                    "flow_xml": xml_response.flow_xml,
                    "error_messages": error_messages
                })
                
                if repair_response.success and repair_response.repaired_flow_xml:
                    # Update the response with repaired XML
                    xml_response.flow_xml = repair_response.repaired_flow_xml
                    xml_response.validation_errors = []
                    
                    # Add repair information
                    xml_response.best_practices_applied.extend(repair_response.repairs_made)
                    if repair_response.remaining_issues:
                        xml_response.recommendations.extend([
                            f"Manual attention needed: {issue}" 
                            for issue in repair_response.remaining_issues
                        ])
            
            return xml_response
            
        except Exception as e:
            print(f"Error during validation and repair: {str(e)}")
            xml_response.recommendations.append(f"Validation error: {str(e)}")
            return xml_response
    
    def _add_implementation_guidance(
        self, 
        response: FlowBuildResponse, 
        best_practices: str
    ) -> FlowBuildResponse:
        """Add comprehensive implementation guidance"""
        try:
            # Add deployment guidance
            deployment_guidance = [
                "Deploy flow as Draft status initially",
                "Test thoroughly in sandbox environment",
                "Validate all field and object dependencies",
                "Review user permissions and sharing rules",
                "Consider impact on existing automation",
                "Use FlowDefinition to activate after testing"
            ]
            
            if response.deployment_notes:
                response.deployment_notes += " " + " ".join(deployment_guidance)
            else:
                response.deployment_notes = " ".join(deployment_guidance)
            
            # Add specific recommendations based on flow type
            if response.input_request.flow_type == FlowType.RECORD_TRIGGERED:
                response.recommendations.extend([
                    "Monitor flow execution in production for performance",
                    "Consider using Before-Save flows for same-record updates",
                    "Add entry criteria to optimize execution frequency",
                    "Review order of execution with other automation"
                ])
            
            elif response.input_request.flow_type == FlowType.SCREEN_FLOW:
                response.recommendations.extend([
                    "Test with different user profiles and permission sets",
                    "Validate field-level security and record access",
                    "Consider mobile responsiveness for screen layouts",
                    "Add proper validation and error messages"
                ])
            
            # Add best practice reminders
            response.recommendations.extend([
                "Document flow purpose and business logic clearly",
                "Use meaningful naming conventions for all elements",
                "Add fault connectors to all DML operations",
                "Consider breaking complex flows into subflows"
            ])
            
            return response
            
        except Exception as e:
            print(f"Error adding implementation guidance: {str(e)}")
            return response
    
    def _update_state(self, state: AgentWorkforceState, updates: Dict[str, Any]) -> AgentWorkforceState:
        """Update the state with new values"""
        updated_state = state.copy()
        for key, value in updates.items():
            updated_state[key] = value
        return updated_state

# Convenience function for backward compatibility
def run_flow_builder_agent(state: AgentWorkforceState, llm: BaseLanguageModel) -> AgentWorkforceState:
    """
    Backward compatible function that uses the enhanced agent
    """
    agent = EnhancedFlowBuilderAgent(llm)
    return agent.run_enhanced_flow_builder_agent(state, llm)

# Example usage
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from src.schemas.flow_builder_schemas import UserStory
    
    # Initialize the agent
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    agent = EnhancedFlowBuilderAgent(llm)
    
    # Create a test user story
    test_user_story = UserStory(
        title="Automated Lead Qualification",
        description="As a sales manager, I want to automatically qualify leads based on revenue and employee count so that my team can focus on high-value prospects",
        acceptance_criteria=[
            "When a lead is created or updated",
            "If Annual Revenue > $1,000,000 AND Number of Employees > 50",
            "Then set Lead Status to 'Qualified'",
            "And send email notification to lead owner",
            "And create follow-up task"
        ],
        priority="High",
        business_context="Part of lead qualification automation to improve sales efficiency",
        affected_objects=["Lead", "Task", "User"],
        user_personas=["Sales Manager", "Sales Rep"]
    )
    
    # Create a flow build request
    test_request = FlowBuildRequest(
        flow_api_name="AutomatedLeadQualification",
        flow_label="Automated Lead Qualification",
        flow_description="Automatically qualify leads based on business criteria",
        user_story=test_user_story,
        flow_type=FlowType.RECORD_TRIGGERED,
        trigger_object="Lead",
        trigger_type=FlowTriggerType.RECORD_AFTER_SAVE
    )
    
    # Create test state
    test_state = AgentWorkforceState(
        current_flow_build_request=test_request,
        current_auth_response=None,
        current_flow_build_response=None,
        current_flow_test_request=None,
        current_flow_test_response=None,
        messages=[],
        is_authenticated=False,
        salesforce_session=None,
        retry_count=0
    )
    
    # Run the agent
    result_state = agent.run_enhanced_flow_builder_agent(test_state, llm)
    
    # Check results
    response = result_state.get("current_flow_build_response")
    if response and response.success:
        print("✅ Flow created successfully!")
        print(f"Elements: {response.elements_created}")
        print(f"Variables: {response.variables_created}")
        print(f"Best practices: {response.best_practices_applied}")
        print(f"Recommendations: {response.recommendations}")
    else:
        print("❌ Flow creation failed")
        if response:
            print(f"Error: {response.error_message}")
            print(f"Validation errors: {response.validation_errors}") 