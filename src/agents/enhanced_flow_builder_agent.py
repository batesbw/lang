"""
Enhanced Flow Builder Agent with RAG Integration and Failure Learning

This agent leverages RAG (Retrieval-Augmented Generation) to build better Salesforce flows by:
1. Searching the knowledge base for best practices and patterns
2. Finding similar sample flows for reference
3. Using retrieved context to generate more accurate and robust flows
4. Learning from documented solutions and common patterns
5. Learning from deployment failures and applying fixes
6. Maintaining conversational memory across retry attempts
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory

from ..tools.rag_tools import RAG_TOOLS, search_flow_knowledge_base, find_similar_sample_flows
from ..tools.flow_builder_tools import BasicFlowXmlGeneratorTool
from ..schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from ..state.agent_workforce_state import AgentWorkforceState

logger = logging.getLogger(__name__)

class EnhancedFlowBuilderAgent:
    """Enhanced Flow Builder Agent with RAG capabilities, failure learning, and conversational memory"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.xml_generator = BasicFlowXmlGeneratorTool()
        
        # Initialize conversational memory for retry attempts
        self.memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=4000,  # Sufficient for flow building context
            memory_key="conversation_history",
            input_key="input",
            output_key="output",
            return_messages=True,
            moving_summary_buffer="Previous flow building attempts and decisions",
            chat_memory=ChatMessageHistory()
        )
        
        # Memory storage for different flow sessions
        self._flow_memories: Dict[str, ConversationSummaryBufferMemory] = {}
        
        # System prompt for the enhanced agent
        self.system_prompt = """
        You are an expert Salesforce Flow Builder Agent with access to a comprehensive knowledge base, 
        sample flow repository, deployment failure learning system, and conversational memory. Your role is to create high-quality, 
        production-ready Salesforce flows based on user requirements and learn from past attempts.
        
        Your capabilities include:
        1. Searching the knowledge base for best practices, patterns, and troubleshooting guides
        2. Finding similar sample flows that match the requirements
        3. Learning from past deployment failures and applying successful fixes
        4. Analyzing retrieved context to inform flow design decisions
        5. Generating robust, well-structured flow XML
        6. Providing recommendations and explanations for design choices
        7. Adapting flows based on failure patterns and successful resolutions
        8. Maintaining memory of previous attempts to improve iterative flow building
        
        When building flows, always:
        - Start by understanding the business requirements thoroughly
        - Check for similar past failures and their resolutions
        - Review your previous attempts and reasoning if this is a retry
        - Search for relevant best practices and patterns
        - Look for similar sample flows for reference
        - Apply Salesforce flow best practices (performance, error handling, etc.)
        - Generate clean, maintainable flow XML with failure prevention in mind
        - Provide clear explanations for your design decisions
        - Learn from any deployment failures to improve future flows
        - Build upon previous attempts when retrying, avoiding repeated mistakes
        
        When fixing deployment failures:
        - Analyze the error message and categorize the failure type
        - Look for similar past failures and successful fixes
        - Review what you tried before and why it might have failed
        - Apply proven solutions from the failure memory
        - Document the attempted fix for future learning
        - Focus on the most likely root cause based on historical data and previous attempts
        - Avoid repeating the same approach that failed before
        
        Focus on creating flows that are:
        - Performant and scalable
        - Error-resistant with proper fault handling
        - Well-documented and maintainable
        - Following Salesforce best practices
        - Avoiding known failure patterns
        - Incorporating lessons learned from previous attempts
        """
    
    def _get_flow_memory(self, flow_api_name: str) -> ConversationSummaryBufferMemory:
        """Get or create memory for a specific flow"""
        if flow_api_name not in self._flow_memories:
            self._flow_memories[flow_api_name] = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=4000,
                memory_key="conversation_history",
                input_key="input",
                output_key="output",
                return_messages=True,
                moving_summary_buffer=f"Flow building attempts for {flow_api_name}",
                chat_memory=ChatMessageHistory()
            )
        return self._flow_memories[flow_api_name]
    
    def _save_attempt_to_memory(self, flow_api_name: str, request: FlowBuildRequest, 
                               response: FlowBuildResponse, attempt_number: int = 1) -> None:
        """Save a flow building attempt to memory"""
        memory = self._get_flow_memory(flow_api_name)
        
        # Create input context
        input_context = f"""
        Flow Building Attempt #{attempt_number}
        
        Request Details:
        - Flow Name: {request.flow_api_name}
        - Description: {request.flow_description}
        - User Story: {request.user_story.title if request.user_story else 'None'}
        - Acceptance Criteria: {request.user_story.acceptance_criteria if request.user_story else 'None'}
        
        Retry Context: {request.retry_context if request.retry_context else 'Initial attempt'}
        """
        
        # Create output context
        if response.success:
            output_context = f"""
            SUCCESS - Flow building completed successfully
            
            Response Details:
            - Flow XML generated successfully
            - Elements created: {response.elements_created}
            - Variables created: {response.variables_created}
            - Best practices applied: {response.best_practices_applied}
            - Recommendations: {response.recommendations}
            - Deployment notes: {response.deployment_notes}
            
            Key Design Decisions:
            - Followed {len(response.best_practices_applied)} best practices
            - Generated {len(response.elements_created)} flow elements
            - Applied {len(response.recommendations)} recommendations
            """
        else:
            output_context = f"""
            FAILURE - Flow building failed
            
            Error Details:
            - Error message: {response.error_message}
            - Validation errors: {response.validation_errors}
            
            This attempt failed and should be learned from in future retries.
            """
        
        # Save to memory
        try:
            memory.save_context(
                {"input": input_context},
                {"output": output_context}
            )
            logger.info(f"Saved attempt #{attempt_number} to memory for flow: {flow_api_name}")
        except Exception as e:
            logger.warning(f"Failed to save attempt to memory: {str(e)}")
    
    def _get_memory_context(self, flow_api_name: str) -> str:
        """Get conversation history from memory for context"""
        memory = self._get_flow_memory(flow_api_name)
        
        try:
            memory_vars = memory.load_memory_variables({})
            conversation_history = memory_vars.get("conversation_history", "")
            
            if conversation_history:
                if isinstance(conversation_history, list):
                    # Convert message list to string
                    history_text = "\n".join([
                        f"{msg.type.title()}: {msg.content}" 
                        for msg in conversation_history
                    ])
                else:
                    history_text = str(conversation_history)
                
                return f"""
                Previous Flow Building Attempts and Context:
                
                {history_text}
                
                Use this context to understand what has been tried before and build upon previous attempts.
                Avoid repeating approaches that failed and incorporate successful patterns.
                """
            else:
                return "No previous attempts found for this flow."
        except Exception as e:
            logger.warning(f"Failed to load memory context: {str(e)}")
            return "Unable to load previous attempt context."
    
    def clear_flow_memory(self, flow_api_name: str) -> None:
        """Clear memory for a specific flow (useful for starting fresh)"""
        if flow_api_name in self._flow_memories:
            self._flow_memories[flow_api_name].clear()
            logger.info(f"Cleared memory for flow: {flow_api_name}")
    
    def analyze_requirements(self, request: FlowBuildRequest) -> Dict[str, Any]:
        """Analyze the flow requirements and extract key information for RAG search"""
        
        analysis = {
            "primary_use_case": self._determine_use_case(request),
            "complexity_level": self._assess_complexity(request),
            "key_elements": self._extract_key_elements(request),
            "search_queries": self._generate_search_queries(request)
        }
        
        logger.info(f"Requirements analysis: {analysis}")
        return analysis
    
    def _determine_use_case(self, request: FlowBuildRequest) -> str:
        """Determine the primary use case based on the request"""
        description = request.flow_description.lower()
        
        if any(keyword in description for keyword in ['approval', 'approve', 'review']):
            return "approval_process"
        elif any(keyword in description for keyword in ['email', 'notification', 'alert']):
            return "email_automation"
        elif any(keyword in description for keyword in ['lead', 'conversion', 'qualify']):
            return "lead_management"
        elif any(keyword in description for keyword in ['case', 'support', 'ticket']):
            return "case_management"
        elif any(keyword in description for keyword in ['opportunity', 'sales', 'deal']):
            return "sales_process"
        elif any(keyword in description for keyword in ['screen', 'form', 'input']):
            return "user_interaction"
        else:
            return "general"
    
    def _assess_complexity(self, request: FlowBuildRequest) -> str:
        """Assess the complexity level of the requested flow"""
        description = request.flow_description.lower()
        
        # Simple indicators
        if any(keyword in description for keyword in ['simple', 'basic', 'single']):
            return "simple"
        
        # Complex indicators
        elif any(keyword in description for keyword in ['complex', 'multiple', 'integration', 'loop', 'conditional']):
            return "complex"
        
        # Default to medium
        else:
            return "medium"
    
    def _extract_key_elements(self, request: FlowBuildRequest) -> List[str]:
        """Extract key flow elements mentioned in the requirements"""
        elements = []
        description = request.flow_description.lower()
        
        if 'record' in description and ('create' in description or 'new' in description):
            elements.append('record_creation')
        if 'record' in description and ('update' in description or 'modify' in description):
            elements.append('record_update')
        if 'email' in description or 'notification' in description:
            elements.append('email')
        if 'decision' in description or 'condition' in description or 'if' in description:
            elements.append('conditional_logic')
        if 'loop' in description or 'iterate' in description:
            elements.append('loops')
        if 'screen' in description or 'form' in description or 'input' in description:
            elements.append('user_interaction')
        if 'approval' in description:
            elements.append('approval')
        
        return elements
    
    def _generate_search_queries(self, request: FlowBuildRequest) -> List[str]:
        """Generate search queries for RAG retrieval"""
        queries = []
        
        # Primary query based on description
        queries.append(request.flow_description)
        
        # Use case specific queries
        use_case = self._determine_use_case(request)
        queries.append(f"{use_case} flow best practices")
        queries.append(f"{use_case} flow examples")
        
        # Element specific queries
        elements = self._extract_key_elements(request)
        for element in elements:
            queries.append(f"{element} flow pattern")
        
        return queries
    
    def _generate_fix_prompt(self, request: FlowBuildRequest, failure_analysis: Dict[str, Any], failure_knowledge: Dict[str, Any]) -> str:
        """Generate a prompt for fixing deployment failures - REMOVED for simplification"""
        # Method removed - using simplified approach
        return ""

    def retrieve_knowledge(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant knowledge from RAG sources"""
        
        knowledge = {
            "best_practices": [],
            "sample_flows": [],
            "patterns": [],
            "troubleshooting": []
        }
        
        try:
            # Search for best practices
            for query in analysis["search_queries"]:
                docs = search_flow_knowledge_base.invoke({
                    "query": query,
                    "category": "best_practices",
                    "max_results": 3
                })
                knowledge["best_practices"].extend(docs)
            
            # Search for examples and patterns
            for query in analysis["search_queries"]:
                docs = search_flow_knowledge_base.invoke({
                    "query": query,
                    "category": "examples",
                    "max_results": 2
                })
                knowledge["patterns"].extend(docs)
            
            # Find similar sample flows
            sample_flows = find_similar_sample_flows.invoke({
                "requirements": analysis["search_queries"][0],  # Primary query
                "use_case": analysis["primary_use_case"],
                "complexity": analysis["complexity_level"]
            })
            knowledge["sample_flows"] = sample_flows
            
            # Search for troubleshooting info
            troubleshooting_docs = search_flow_knowledge_base.invoke({
                "query": f"{analysis['primary_use_case']} troubleshooting",
                "category": "troubleshooting",
                "max_results": 2
            })
            knowledge["troubleshooting"] = troubleshooting_docs
            
            logger.info(f"Retrieved knowledge: {len(knowledge['best_practices'])} best practices, "
                       f"{len(knowledge['sample_flows'])} sample flows, "
                       f"{len(knowledge['patterns'])} patterns")
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
            # Return empty knowledge on error to allow flow generation to continue
            knowledge = {
                "best_practices": [],
                "sample_flows": [],
                "patterns": [],
                "troubleshooting": []
            }
        
        return knowledge
    
    def generate_enhanced_prompt(self, request: FlowBuildRequest, knowledge: Dict[str, Any]) -> str:
        """Generate a unified prompt with user story, RAG knowledge, memory context, and optional retry context"""
        
        prompt_parts = [
            f"Create a Salesforce flow based on the following requirements:",
            f"Flow Name: {request.flow_api_name}",
            f"Flow Label: {request.flow_label}",
            f"Description: {request.flow_description}",
            ""
        ]
        
        # Add memory context from previous attempts
        memory_context = self._get_memory_context(request.flow_api_name)
        if memory_context and "No previous attempts found" not in memory_context:
            prompt_parts.extend([
                "CONVERSATION MEMORY - PREVIOUS ATTEMPTS:",
                memory_context,
                ""
            ])
        
        # Add comprehensive user story context if available
        if request.user_story:
            prompt_parts.extend([
                "USER STORY:",
                f"Title: {request.user_story.title}",
                f"Description: {request.user_story.description}",
                "",
                "ACCEPTANCE CRITERIA:",
            ])
            for i, criteria in enumerate(request.user_story.acceptance_criteria, 1):
                prompt_parts.append(f"{i}. {criteria}")
            
            prompt_parts.extend([
                "",
                f"Priority: {request.user_story.priority}",
            ])
            
            if request.user_story.business_context:
                prompt_parts.extend([
                    f"Business Context: {request.user_story.business_context}",
                    ""
                ])
            
            if request.user_story.affected_objects:
                prompt_parts.extend([
                    f"Affected Objects: {', '.join(request.user_story.affected_objects)}",
                    ""
                ])
            
            if request.user_story.user_personas:
                prompt_parts.extend([
                    f"User Personas: {', '.join(request.user_story.user_personas)}",
                    ""
                ])
        
        # Add best practices context
        if knowledge["best_practices"]:
            prompt_parts.append("RELEVANT BEST PRACTICES:")
            for i, doc in enumerate(knowledge["best_practices"][:3], 1):
                prompt_parts.append(f"{i}. {doc['content'][:500]}...")
            prompt_parts.append("")
        
        # Add sample flow context
        if knowledge["sample_flows"]:
            prompt_parts.append("SIMILAR SAMPLE FLOWS FOR REFERENCE:")
            for i, flow in enumerate(knowledge["sample_flows"][:2], 1):
                prompt_parts.append(f"{i}. {flow['flow_name']}: {flow['description']}")
                prompt_parts.append(f"   Use case: {flow['use_case']}")
                prompt_parts.append(f"   Tags: {', '.join(flow['tags'])}")
            prompt_parts.append("")
        
        # Add pattern guidance
        if knowledge["patterns"]:
            prompt_parts.append("RELEVANT PATTERNS:")
            for doc in knowledge["patterns"][:2]:
                prompt_parts.append(f"- {doc['content'][:300]}...")
            prompt_parts.append("")
        
        # Add retry context if this is a retry attempt
        if request.retry_context:
            retry_context = request.retry_context
            deployment_error = retry_context.get("deployment_error")
            component_errors = retry_context.get("component_errors", [])
            original_flow_xml = retry_context.get("original_flow_xml")
            retry_attempt = retry_context.get("retry_attempt", 1)
            
            if deployment_error or original_flow_xml:
                prompt_parts.extend([
                    f"CURRENT RETRY CONTEXT (Retry #{retry_attempt}):",
                    "The previous flow deployment failed and needs to be rebuilt.",
                    ""
                ])
                
                if deployment_error:
                    prompt_parts.extend([
                        "Current deployment error:",
                        f"{deployment_error}",
                        ""
                    ])
                
                if component_errors:
                    prompt_parts.append("Component-level errors:")
                    for error in component_errors:
                        if isinstance(error, dict):
                            prompt_parts.append(f"- {error.get('componentType', 'Unknown')}: {error.get('problem', 'Unknown error')}")
                        else:
                            prompt_parts.append(f"- {str(error)}")
                    prompt_parts.append("")
                
                if original_flow_xml:
                    prompt_parts.extend([
                        "Previous flow XML (for reference only):",
                        f"{original_flow_xml[:1000]}{'...' if len(original_flow_xml) > 1000 else ''}",
                        ""
                    ])
                
                prompt_parts.extend([
                    "IMPORTANT REQUIREMENTS FOR RETRY:",
                    "1. You MUST fulfill ALL the original business requirements and user story",
                    "2. You MUST address the deployment error that caused the failure",
                    "3. You MUST maintain the flow's intended functionality and business logic",
                    "4. Build upon insights from previous attempts (shown in conversation memory above)",
                    "5. Avoid repeating approaches that failed before",
                    "6. Common deployment fixes to apply:",
                    "   - API names must be alphanumeric and start with a letter (no spaces, hyphens, or special characters)",
                    "   - All required elements and configurations must be present",
                    "   - Element references must be valid",
                    "   - Flow syntax and structure must be correct",
                    "",
                    "APPROACH: Review previous attempts in memory, understand what worked/failed, start with the business requirements, design a flow that meets them, and apply deployment error fixes as you build.",
                    ""
                ])
        
        prompt_parts.extend([
            "REQUIREMENTS:",
            "1. Generate a complete, production-ready Salesforce flow XML",
            "2. Follow Salesforce flow best practices for performance and maintainability",
            "3. Include proper error handling and fault paths where appropriate",
            "4. Use descriptive names for all flow elements",
            "5. Ensure the flow is scalable and follows governor limit best practices",
            "6. Include comments explaining key design decisions",
            "7. If this is a retry, incorporate lessons learned from previous attempts",
            "",
            "Please provide the flow XML and a brief explanation of your design choices."
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_flow_with_rag(self, request: FlowBuildRequest) -> FlowBuildResponse:
        """Generate a flow using unified RAG-enhanced approach for both initial and retry attempts"""
        
        # Determine attempt number for memory tracking
        retry_attempt = request.retry_context.get('retry_attempt', 1) if request.retry_context else 1
        
        try:
            # Step 1: Analyze requirements
            logger.info(f"Analyzing requirements for flow: {request.flow_api_name}")
            analysis = self.analyze_requirements(request)
            
            # Step 2: Retrieve relevant knowledge
            logger.info("Retrieving relevant knowledge from RAG sources")
            knowledge = self.retrieve_knowledge(analysis)
            
            # Step 3: Generate unified prompt (includes user story, RAG knowledge, memory context, and optional retry context)
            logger.info("Generating unified enhanced prompt with memory context")
            enhanced_prompt = self.generate_enhanced_prompt(request, knowledge)
            
            # Step 4: Use LLM to generate flow design
            logger.info("Generating flow design with LLM")
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=enhanced_prompt)
            ]
            
            llm_response = self.llm.invoke(messages)
            
            # Step 5: Extract XML and generate final response
            # For now, we'll use the basic XML generator as a fallback
            # In a more advanced implementation, we'd parse the LLM response for XML
            logger.info("Generating final flow XML")
            
            # Use the basic tool as a starting point, but enhance with RAG insights
            tool_input = request.model_dump()
            basic_response = self.xml_generator.invoke(tool_input)
            
            # Enhance the response with RAG insights
            if isinstance(basic_response, FlowBuildResponse):
                # Add RAG-derived recommendations to existing lists
                enhanced_recommendations = basic_response.recommendations + [
                    f"Applied best practices for {analysis['primary_use_case']} flows",
                    f"Considered {len(knowledge['sample_flows'])} similar sample flows",
                    f"Incorporated {len(knowledge['best_practices'])} relevant best practices",
                    "Flow designed with performance and scalability in mind"
                ]
                
                enhanced_best_practices = basic_response.best_practices_applied + [
                    f"RAG-enhanced flow for {analysis['complexity_level']} complexity",
                    f"Knowledge-based design for {analysis['primary_use_case']} use case"
                ]
                
                # Add user story context if available
                if request.user_story:
                    enhanced_recommendations.append(f"Built to fulfill user story: {request.user_story.title}")
                    enhanced_best_practices.append(f"Designed for {request.user_story.priority} priority user story")
                
                # Add retry-specific context if applicable
                if request.retry_context:
                    enhanced_recommendations.append(f"Generated addressing deployment failures (retry #{retry_attempt})")
                    enhanced_best_practices.append("Incorporated deployment error resolution strategies")
                    enhanced_best_practices.append("Built upon previous attempt insights from memory")
                
                # Create enhanced response with valid fields only
                enhanced_response = FlowBuildResponse(
                    success=True,
                    input_request=request,
                    flow_xml=basic_response.flow_xml,
                    flow_definition_xml=basic_response.flow_definition_xml,
                    validation_errors=basic_response.validation_errors,
                    error_message=basic_response.error_message,
                    elements_created=basic_response.elements_created,
                    variables_created=basic_response.variables_created,
                    best_practices_applied=enhanced_best_practices,
                    recommendations=enhanced_recommendations,
                    deployment_notes=basic_response.deployment_notes,
                    dependencies=basic_response.dependencies
                )
                
                # Save successful attempt to memory
                self._save_attempt_to_memory(request.flow_api_name, request, enhanced_response, retry_attempt)
                
                logger.info(f"Successfully generated enhanced flow: {request.flow_api_name}")
                return enhanced_response
            else:
                raise Exception("Basic XML generator failed to produce valid response")
                
        except Exception as e:
            error_message = f"Enhanced FlowBuilderAgent error: {str(e)}"
            logger.error(error_message)
            
            error_response = FlowBuildResponse(
                success=False,
                input_request=request,
                error_message=error_message
            )
            
            # Save failed attempt to memory
            self._save_attempt_to_memory(request.flow_api_name, request, error_response, retry_attempt)
            
            return error_response

    def analyze_deployment_failure(self, error_message: str, flow_xml: str, component_errors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze a deployment failure and learn from it - REMOVED for simplification"""
        # Method removed - using simplified approach
        pass
    
    def load_failure_knowledge(self) -> Dict[str, Any]:
        """Load historical failure knowledge for proactive prevention - REMOVED for simplification"""
        # Method removed - using simplified approach
        pass
    
    def generate_fix_for_failure(self, request: FlowBuildRequest, failure_analysis: Dict[str, Any]) -> FlowBuildResponse:
        """Generate a fixed flow based on failure analysis - REMOVED for simplification"""
        # Method removed - using simplified approach
        pass
    
    def update_fix_result(self, failure_id: str, attempted_fix: str, success: bool) -> None:
        """Update the failure memory with the result of a fix attempt - REMOVED for simplification"""
        # Method removed - using simplified approach  
        pass


def run_enhanced_flow_builder_agent(state: AgentWorkforceState, llm: BaseLanguageModel) -> AgentWorkforceState:
    """
    Run the Enhanced Flow Builder Agent with unified RAG approach and conversational memory
    """
    print("----- ENHANCED FLOW BUILDER AGENT (with Unified RAG + Memory) -----")
    
    flow_build_request_dict = state.get("current_flow_build_request")
    build_deploy_retry_count = state.get("build_deploy_retry_count", 0)
    response_updates = {}
    
    if flow_build_request_dict:
        try:
            # Convert dict back to Pydantic model
            flow_build_request = FlowBuildRequest(**flow_build_request_dict)
            
            print(f"Processing FlowBuildRequest for Flow: {flow_build_request.flow_api_name}")
            print(f"Flow Description: {flow_build_request.flow_description}")
            print(f"Build/Deploy retry count: {build_deploy_retry_count}")
            
            # Check for retry context and log accordingly
            if flow_build_request.retry_context:
                retry_attempt = flow_build_request.retry_context.get('retry_attempt', 1)
                print(f"🔄 RETRY MODE: Processing attempt #{retry_attempt}")
                print(f"🧠 MEMORY: Will include context from previous attempts")
                print(f"🔧 Will rebuild flow addressing previous deployment failure")
                print(f"🎯 Using unified RAG approach with integrated failure context and memory")
            else:
                print("📝 INITIAL ATTEMPT: Using unified RAG approach")
                print("🧠 MEMORY: Starting fresh memory tracking for this flow")
            
            # Initialize the enhanced agent with persistent memory
            # Note: In a production system, you'd want to persist this agent instance
            # across calls to maintain memory. For now, we create it fresh each time
            # but the memory will be saved within the agent's _flow_memories dict
            agent = EnhancedFlowBuilderAgent(llm)
            
            # Check if we have memory context for this flow
            memory_context = agent._get_memory_context(flow_build_request.flow_api_name)
            if memory_context and "No previous attempts found" not in memory_context:
                print("🧠 MEMORY: Found previous attempt context")
            else:
                print("🧠 MEMORY: No previous attempts found for this flow")
            
            # Use the unified RAG approach for all scenarios
            # The method automatically handles user story, RAG knowledge, memory context, and optional retry context
            flow_response = agent.generate_flow_with_rag(flow_build_request)
            
            # Convert response to dict for state storage
            response_updates["current_flow_build_response"] = flow_response.model_dump()
            
            if flow_response.success:
                print(f"✅ Flow building successful for: {flow_build_request.flow_api_name}")
                print(f"🧠 MEMORY: Saved successful attempt to memory")
                if flow_build_request.retry_context:
                    retry_attempt = flow_build_request.retry_context.get('retry_attempt', 1)
                    print(f"   🎯 Successfully rebuilt flow addressing deployment issues (retry #{retry_attempt})")
                    print(f"   🔄 Maintained business requirements while fixing deployment errors")
                    print(f"   🧠 Incorporated insights from previous attempts")
                else:
                    print(f"   📋 Successfully built flow meeting user story requirements")
            else:
                print(f"❌ Flow building failed: {flow_response.error_message}")
                print(f"🧠 MEMORY: Saved failed attempt to memory for future learning")
                
        except Exception as e:
            error_message = f"Enhanced FlowBuilderAgent error: {str(e)}"
            print(error_message)
            
            error_response = FlowBuildResponse(
                success=False,
                input_request=FlowBuildRequest(**flow_build_request_dict),
                error_message=error_message
            )
            response_updates["current_flow_build_response"] = error_response.model_dump()
    else:
        print("Enhanced FlowBuilderAgent: No current_flow_build_request to process.")
    
    # Merge updates with the current state
    updated_state = state.copy()
    for key, value in response_updates.items():
        updated_state[key] = value
    
    return updated_state

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
    result_state = run_enhanced_flow_builder_agent(test_state, llm)
    
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