from typing import Type, List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import re
import json

from src.schemas.flow_builder_schemas import (
    UserStory, FlowRequirement, FlowType, FlowElementType, 
    FlowTriggerType, FlowElement, FlowVariable
)

class UserStoryParseRequest(BaseModel):
    """Input for parsing user stories into flow requirements"""
    user_story_text: str = Field(..., description="The user story text to parse")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    business_context: Optional[str] = Field(None, description="Additional business context")
    existing_objects: List[str] = Field(default_factory=list, description="List of existing Salesforce objects")
    existing_fields: Dict[str, List[str]] = Field(default_factory=dict, description="Existing fields per object")

class ParsedFlowRequirements(BaseModel):
    """Structured flow requirements parsed from user story"""
    user_story: UserStory
    flow_requirements: FlowRequirement
    suggested_flow_elements: List[FlowElement]
    suggested_variables: List[FlowVariable]
    implementation_notes: List[str]
    potential_challenges: List[str]

class UserStoryParserTool(BaseTool):
    """
    Tool that parses natural language user stories and acceptance criteria
    into structured flow requirements, elements, and implementation guidance.
    """
    name: str = "user_story_parser_tool"
    description: str = (
        "Parse natural language user stories and acceptance criteria into structured "
        "Salesforce Flow requirements. Identifies flow type, required elements, "
        "variables, business logic, and provides implementation guidance."
    )
    args_schema: Type[BaseModel] = UserStoryParseRequest
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__()
        self.llm = llm
        self._setup_parser()
    
    def _setup_parser(self):
        """Setup the LLM parser with prompts"""
        self.parser = PydanticOutputParser(pydantic_object=ParsedFlowRequirements)
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Salesforce Flow architect. Your task is to analyze user stories and acceptance criteria to create detailed flow requirements.

Key responsibilities:
1. Parse user stories to identify the flow type needed
2. Determine required flow elements and their sequence
3. Identify necessary variables and data operations
4. Suggest implementation approach and potential challenges
5. Apply Salesforce Flow best practices

Flow Types to consider:
- Screen Flow: User interfaces, data collection, guided processes
- Record-Triggered Flow: Automated actions on record changes
- Scheduled Flow: Time-based automation
- Autolaunched Flow: Called by other processes
- Platform Event-Triggered Flow: Event-driven automation

Flow Elements available:
- screens: User interface elements
- decisions: Conditional logic and branching
- assignments: Variable manipulation and calculations
- recordLookups: Get Records operations
- recordCreates: Create new records
- recordUpdates: Update existing records
- recordDeletes: Delete records
- loops: Iterate over collections
- actionCalls: Call actions, send emails, etc.
- subflows: Call other flows
- waits: Pause execution

Consider these best practices:
- Use Before-Save flows for same-record updates
- Add fault paths for error handling
- Use specific entry criteria for record-triggered flows
- Minimize DML operations and avoid them in loops
- Use meaningful naming conventions
- Consider user permissions and security

{format_instructions}"""),
            ("human", """Analyze this user story and acceptance criteria:

User Story: {user_story_text}

Acceptance Criteria:
{acceptance_criteria}

Business Context: {business_context}

Available Objects: {existing_objects}
Available Fields: {existing_fields}

Please provide a comprehensive analysis including:
1. Parsed user story structure
2. Detailed flow requirements
3. Suggested flow elements with configuration
4. Required variables
5. Implementation notes and best practices
6. Potential challenges and solutions""")
        ])
    
    def _run(
        self,
        user_story_text: str,
        acceptance_criteria: List[str],
        business_context: Optional[str] = None,
        existing_objects: List[str] = None,
        existing_fields: Dict[str, List[str]] = None
    ) -> str:
        """Parse user story into flow requirements"""
        try:
            # Format acceptance criteria
            ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])
            
            # Format existing objects and fields
            objects_text = ", ".join(existing_objects or [])
            fields_text = json.dumps(existing_fields or {}, indent=2)
            
            # Create the prompt
            messages = self.prompt_template.format_messages(
                user_story_text=user_story_text,
                acceptance_criteria=ac_text,
                business_context=business_context or "Not provided",
                existing_objects=objects_text,
                existing_fields=fields_text,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Parse the response
            parsed_requirements = self.parser.parse(response.content)
            
            # Format the output
            return self._format_parsed_requirements(parsed_requirements)
            
        except Exception as e:
            return f"Error parsing user story: {str(e)}"
    
    def _format_parsed_requirements(self, requirements: ParsedFlowRequirements) -> str:
        """Format the parsed requirements into a readable string"""
        output = []
        
        # User Story Summary
        output.append("=== PARSED USER STORY ===")
        output.append(f"Title: {requirements.user_story.title}")
        output.append(f"Description: {requirements.user_story.description}")
        output.append(f"Priority: {requirements.user_story.priority}")
        output.append(f"Affected Objects: {', '.join(requirements.user_story.affected_objects)}")
        output.append(f"User Personas: {', '.join(requirements.user_story.user_personas)}")
        output.append("")
        
        # Acceptance Criteria
        output.append("Acceptance Criteria:")
        for i, ac in enumerate(requirements.user_story.acceptance_criteria, 1):
            output.append(f"  {i}. {ac}")
        output.append("")
        
        # Flow Requirements
        output.append("=== FLOW REQUIREMENTS ===")
        output.append(f"Flow Type: {requirements.flow_requirements.flow_type}")
        if requirements.flow_requirements.trigger_object:
            output.append(f"Trigger Object: {requirements.flow_requirements.trigger_object}")
        if requirements.flow_requirements.trigger_type:
            output.append(f"Trigger Type: {requirements.flow_requirements.trigger_type}")
        if requirements.flow_requirements.entry_criteria:
            output.append(f"Entry Criteria: {requirements.flow_requirements.entry_criteria}")
        output.append("")
        
        # Required Elements
        output.append("Required Flow Elements:")
        for element_type in requirements.flow_requirements.flow_elements_needed:
            output.append(f"  - {element_type}")
        output.append("")
        
        # Data Operations
        if requirements.flow_requirements.data_operations:
            output.append("Data Operations:")
            for operation in requirements.flow_requirements.data_operations:
                output.append(f"  - {operation}")
            output.append("")
        
        # Business Logic
        if requirements.flow_requirements.business_logic:
            output.append("Business Logic:")
            for logic in requirements.flow_requirements.business_logic:
                output.append(f"  - {logic}")
            output.append("")
        
        # Suggested Flow Elements
        output.append("=== SUGGESTED FLOW ELEMENTS ===")
        for i, element in enumerate(requirements.suggested_flow_elements, 1):
            output.append(f"{i}. {element.element_type} - {element.name}")
            output.append(f"   Label: {element.label}")
            if element.description:
                output.append(f"   Description: {element.description}")
            if element.configuration:
                output.append(f"   Configuration: {json.dumps(element.configuration, indent=4)}")
            output.append("")
        
        # Suggested Variables
        if requirements.suggested_variables:
            output.append("=== SUGGESTED VARIABLES ===")
            for var in requirements.suggested_variables:
                var_desc = f"{var.name} ({var.data_type}"
                if var.is_collection:
                    var_desc += " Collection"
                var_desc += ")"
                output.append(f"- {var_desc}")
                if var.description:
                    output.append(f"  Description: {var.description}")
            output.append("")
        
        # Implementation Notes
        if requirements.implementation_notes:
            output.append("=== IMPLEMENTATION NOTES ===")
            for note in requirements.implementation_notes:
                output.append(f"- {note}")
            output.append("")
        
        # Potential Challenges
        if requirements.potential_challenges:
            output.append("=== POTENTIAL CHALLENGES ===")
            for challenge in requirements.potential_challenges:
                output.append(f"- {challenge}")
            output.append("")
        
        return "\n".join(output)
    
    def get_structured_requirements(
        self,
        user_story_text: str,
        acceptance_criteria: List[str],
        business_context: Optional[str] = None,
        existing_objects: List[str] = None,
        existing_fields: Dict[str, List[str]] = None
    ) -> ParsedFlowRequirements:
        """Get structured requirements object instead of formatted string"""
        try:
            # Format acceptance criteria
            ac_text = "\n".join([f"- {ac}" for ac in acceptance_criteria])
            
            # Format existing objects and fields
            objects_text = ", ".join(existing_objects or [])
            fields_text = json.dumps(existing_fields or {}, indent=2)
            
            # Create the prompt
            messages = self.prompt_template.format_messages(
                user_story_text=user_story_text,
                acceptance_criteria=ac_text,
                business_context=business_context or "Not provided",
                existing_objects=objects_text,
                existing_fields=fields_text,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Parse and return the response
            return self.parser.parse(response.content)
            
        except Exception as e:
            # Return a basic structure on error
            return ParsedFlowRequirements(
                user_story=UserStory(
                    title="Error parsing user story",
                    description=user_story_text,
                    acceptance_criteria=acceptance_criteria
                ),
                flow_requirements=FlowRequirement(
                    flow_type=FlowType.SCREEN_FLOW,
                    flow_elements_needed=[FlowElementType.SCREEN]
                ),
                suggested_flow_elements=[],
                suggested_variables=[],
                implementation_notes=[f"Error occurred during parsing: {str(e)}"],
                potential_challenges=["Unable to parse requirements automatically"]
            )
    
    async def _arun(
        self,
        user_story_text: str,
        acceptance_criteria: List[str],
        business_context: Optional[str] = None,
        existing_objects: List[str] = None,
        existing_fields: Dict[str, List[str]] = None
    ) -> str:
        """Async version of the tool"""
        return self._run(user_story_text, acceptance_criteria, business_context, existing_objects, existing_fields)

# Example usage and testing
if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    
    # Initialize the tool
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    parser_tool = UserStoryParserTool(llm)
    
    # Test user story
    test_user_story = """
    As a sales manager, I want to automatically update the lead status to 'Qualified' 
    when a lead's annual revenue is greater than $1M and they have more than 50 employees, 
    so that my team can prioritize high-value prospects.
    """
    
    test_acceptance_criteria = [
        "When a lead record is created or updated",
        "If Annual Revenue > $1,000,000 AND Number of Employees > 50",
        "Then set Lead Status to 'Qualified'",
        "And send an email notification to the lead owner",
        "And create a task for follow-up within 24 hours"
    ]
    
    test_business_context = """
    This is part of our lead qualification process. We want to ensure that high-value 
    leads are immediately identified and prioritized by the sales team. The current 
    manual process is causing delays in follow-up.
    """
    
    # Test the parser
    result = parser_tool.invoke({
        "user_story_text": test_user_story,
        "acceptance_criteria": test_acceptance_criteria,
        "business_context": test_business_context,
        "existing_objects": ["Lead", "Task", "User"],
        "existing_fields": {
            "Lead": ["Status", "AnnualRevenue", "NumberOfEmployees", "OwnerId"],
            "Task": ["Subject", "ActivityDate", "WhoId", "OwnerId"]
        }
    })
    
    print(result) 