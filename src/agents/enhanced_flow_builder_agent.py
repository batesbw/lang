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

import os
import logging
from typing import Optional, List, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
import xml.etree.ElementTree as ET

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
        """Save a flow building attempt to memory with enhanced context"""
        memory = self._get_flow_memory(flow_api_name)
        
        # Create enhanced input context
        input_context = f"""
        === FLOW BUILDING ATTEMPT #{attempt_number} ===
        
        🎯 REQUEST DETAILS:
        - Flow Name: {request.flow_api_name}
        - Flow Label: {request.flow_label}
        - Description: {request.flow_description}
        - Flow Type: {getattr(request, 'flow_type', 'Screen Flow')}
        
        📖 USER STORY:
        - Title: {request.user_story.title if request.user_story else 'None'}
        - Priority: {request.user_story.priority if request.user_story else 'None'}
        - Description: {request.user_story.description if request.user_story else 'None'}
        
        🔄 RETRY CONTEXT:
        """
        
        if request.retry_context:
            retry_context = request.retry_context
            error_analysis = retry_context.get("error_analysis", {})
            
            input_context += f"""
        - This was retry attempt #{retry_context.get('retry_attempt', 1)}
        - Previous deployment error: {retry_context.get('deployment_error', 'Unknown')}
        - Error type detected: {error_analysis.get('error_type', 'unknown')}
        - Error severity: {error_analysis.get('severity', 'medium')}
        - Required fixes attempted: {len(retry_context.get('specific_fixes_needed', []))}
        - Error patterns to avoid: {', '.join(retry_context.get('common_patterns', []))}
        """
        else:
            input_context += "- This was the initial attempt (no retry context)"
        
        # Create enhanced output context
        if response.success:
            output_context = f"""
            ✅ SUCCESS - Flow building completed successfully
            
            📊 RESPONSE DETAILS:
            - Flow XML generated successfully (length: {len(response.flow_xml) if response.flow_xml else 0} chars)
            - Elements created: {response.elements_created}
            - Variables created: {response.variables_created}
            - Best practices applied: {response.best_practices_applied}
            - Recommendations: {response.recommendations}
            - Deployment notes: {response.deployment_notes}
            
            🎯 KEY SUCCESS FACTORS:
            - Successfully generated {len(response.elements_created)} flow elements
            - Applied {len(response.best_practices_applied)} best practices
            - Provided {len(response.recommendations)} recommendations
            """
            
            if request.retry_context:
                output_context += f"""
            
            🔧 RETRY SUCCESS DETAILS:
            - Successfully addressed deployment errors from previous attempt
            - Applied structured error fixes and avoided error patterns
            - Used memory context and failure learning effectively
            """
            
            output_context += """
            
            💡 LESSONS LEARNED:
            - This approach was successful and should be replicated for similar flows
            - The XML structure and element naming worked correctly
            - Business requirements were properly translated to flow logic
            """
        else:
            output_context = f"""
            ❌ FAILURE - Flow building failed
            
            🔍 ERROR DETAILS:
            - Error message: {response.error_message}
            - Validation errors: {len(response.validation_errors)} errors found
            """
            
            if response.validation_errors:
                output_context += "\n            - Specific validation issues:"
                for i, error in enumerate(response.validation_errors[:3], 1):  # Show first 3
                    output_context += f"\n              {i}. {error.error_type}: {error.error_message}"
            
            output_context += f"""
            
            ⚠️ FAILURE ANALYSIS:
            - This attempt failed at the flow building stage (before deployment)
            - The error occurred during XML generation or validation
            - Future attempts should address the specific validation issues above
            
            🎓 LESSONS LEARNED:
            - This approach failed and should be avoided in future attempts
            - The error pattern indicates issues with: {response.error_message[:100]}...
            - Consider alternative flow structures or element configurations
            """
            
            if request.retry_context:
                output_context += f"""
            
            🔄 RETRY FAILURE CONTEXT:
            - This was retry attempt #{request.retry_context.get('retry_attempt', 1)}
            - Previous deployment fixes may not have been sufficient
            - Consider more fundamental changes to the flow structure
            """
        
        # Save to memory with enhanced context
        try:
            # Strip trailing whitespace to avoid Anthropic API errors
            cleaned_input = input_context.strip()
            cleaned_output = output_context.strip()
            
            memory.save_context(
                {"input": cleaned_input},
                {"output": cleaned_output}
            )
            logger.info(f"Saved enhanced attempt #{attempt_number} to memory for flow: {flow_api_name}")
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
        if knowledge.get("best_practices"):
            prompt_parts.append("RELEVANT BEST PRACTICES:")
            for i, doc in enumerate(knowledge["best_practices"][:3], 1):
                prompt_parts.append(f"{i}. {doc['content'][:500]}...")
            prompt_parts.append("")
        
        # Add sample flow context
        if knowledge.get("sample_flows"):
            prompt_parts.append("SIMILAR SAMPLE FLOWS FOR REFERENCE:")
            for i, flow in enumerate(knowledge["sample_flows"][:2], 1):
                prompt_parts.append(f"{i}. {flow['flow_name']}: {flow['description']}")
                prompt_parts.append(f"   Use case: {flow['use_case']}")
                prompt_parts.append(f"   Tags: {', '.join(flow['tags'])}")
            prompt_parts.append("")
        
        # Add pattern guidance
        if knowledge.get("patterns"):
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
            error_analysis = retry_context.get("error_analysis", {})
            specific_fixes = retry_context.get("specific_fixes_needed", [])
            error_patterns = retry_context.get("common_patterns", [])
            previous_summary = retry_context.get("previous_attempts_summary", "")
            
            # Handle both deployment failures and validation failures
            validation_failed = retry_context.get("validation_failed", False)
            scanner_validation = retry_context.get("scanner_validation", {})
            validation_errors = retry_context.get("validation_errors", [])
            
            if deployment_error or original_flow_xml or validation_failed:
                if validation_failed:
                    prompt_parts.extend([
                        f"🔄 VALIDATION RETRY CONTEXT (Attempt #{retry_attempt}):",
                        "The previous flow XML FAILED Lightning Flow Scanner validation and must be rebuilt to fix the errors.",
                        ""
                    ])
                else:
                    prompt_parts.extend([
                        f"🔄 DEPLOYMENT RETRY CONTEXT (Attempt #{retry_attempt}):",
                        "The previous flow deployment FAILED and must be completely rebuilt to fix the errors.",
                        ""
                    ])
                
                # Handle validation-specific context
                if validation_failed and scanner_validation:
                    prompt_parts.extend([
                        "⚠️ FLOW SCANNER VALIDATION FAILED:",
                        f"Total violations: {scanner_validation.get('total_violations', 0)}",
                        f"Errors: {scanner_validation.get('error_count', 0)}",
                        f"Warnings: {scanner_validation.get('warning_count', 0)}",
                        f"Retry guidance: {scanner_validation.get('retry_guidance', 'Fix all validation errors')}",
                        ""
                    ])
                    
                    if scanner_validation.get('blocking_issues'):
                        prompt_parts.append("🚫 BLOCKING VALIDATION ISSUES:")
                        for issue in scanner_validation['blocking_issues']:
                            prompt_parts.append(f"- {issue}")
                        prompt_parts.append("")
                
                # Handle specific validation errors
                if validation_errors:
                    prompt_parts.extend([
                        "🔍 SPECIFIC VALIDATION ERRORS TO FIX:",
                    ])
                    for i, error in enumerate(validation_errors, 1):
                        rule = error.get('rule', 'Unknown')
                        message = error.get('message', 'No message')
                        location = error.get('location', 'Unknown location')
                        suggested_fix = error.get('suggested_fix', 'See rule documentation')
                        
                        prompt_parts.extend([
                            f"{i}. {rule}:",
                            f"   Message: {message}",
                            f"   Location: {location}",
                            f"   Fix: {suggested_fix}",
                            ""
                        ])
                
                if error_analysis:
                    prompt_parts.extend([
                        "📊 STRUCTURED ERROR ANALYSIS:",
                        f"Error Type: {error_analysis.get('error_type', 'unknown')}",
                        f"Severity: {error_analysis.get('severity', 'medium')}",
                        ""
                    ])
                    
                    if error_analysis.get('api_name_issues'):
                        prompt_parts.extend([
                            "🏷️ API NAME ISSUES DETECTED:",
                            "- The previous flow had invalid API names that caused deployment failure",
                            "- ALL API names must be alphanumeric and start with a letter",
                            "- NO spaces, hyphens, or special characters allowed",
                            ""
                        ])
                    
                    if error_analysis.get('structural_issues'):
                        prompt_parts.extend([
                            "🏗️ STRUCTURAL ISSUES DETECTED:",
                        ])
                        for issue in error_analysis['structural_issues']:
                            prompt_parts.append(f"- {issue}")
                        prompt_parts.append("")
                    
                    if error_analysis.get('xml_issues'):
                        prompt_parts.extend([
                            "📄 XML ISSUES DETECTED:",
                        ])
                        for issue in error_analysis['xml_issues']:
                            prompt_parts.append(f"- {issue}")
                        prompt_parts.append("")
                
                if specific_fixes:
                    prompt_parts.extend([
                        "🔧 REQUIRED FIXES (MANDATORY TO IMPLEMENT):",
                    ])
                    for i, fix in enumerate(specific_fixes, 1):
                        prompt_parts.append(f"{i}. {fix}")
                    prompt_parts.append("")
                
                if error_patterns:
                    prompt_parts.extend([
                        "⚠️ ERROR PATTERNS TO AVOID:",
                        f"The following patterns caused the previous failure: {', '.join(error_patterns)}",
                        ""
                    ])
                
                if previous_summary:
                    prompt_parts.extend([
                        "📚 PREVIOUS ATTEMPTS CONTEXT:",
                        previous_summary,
                        ""
                    ])
                
                if deployment_error:
                    prompt_parts.extend([
                        "❌ ORIGINAL DEPLOYMENT ERROR:",
                        f"{deployment_error}",
                        ""
                    ])
                
                if component_errors:
                    prompt_parts.append("🔍 COMPONENT-LEVEL ERRORS:")
                    for error in component_errors:
                        if isinstance(error, dict):
                            prompt_parts.append(f"- {error.get('componentType', 'Unknown')}: {error.get('problem', 'Unknown error')}")
                        else:
                            prompt_parts.append(f"- {str(error)}")
                    prompt_parts.append("")
                
                if original_flow_xml:
                    prompt_parts.extend([
                        "🔍 PREVIOUS FLOW XML (FOR ANALYSIS ONLY - DO NOT COPY):",
                        f"{original_flow_xml[:1000]}{'...' if len(original_flow_xml) > 1000 else ''}",
                        ""
                    ])
                
                prompt_parts.extend([
                    "🎯 CRITICAL RETRY REQUIREMENTS:",
                    "1. You MUST fulfill ALL the original business requirements and user story",
                    "2. You MUST implement ALL the specific fixes listed above",
                    "3. You MUST avoid ALL the error patterns that caused previous failures",
                    "4. You MUST generate completely new, valid XML (do not copy from previous attempt)",
                    "5. You MUST maintain the flow's intended business functionality",
                    "6. You MUST use the memory context to build upon previous learnings",
                    ""
                ])
                
                if validation_failed:
                    prompt_parts.extend([
                        "🛠️ VALIDATION SUCCESS CHECKLIST:",
                        "✓ All flow elements follow Salesforce best practices",
                        "✓ No hardcoded IDs or URLs in the flow",
                        "✓ No DML or SOQL operations inside loops",
                        "✓ All operations include proper fault handling",
                        "✓ Flow uses appropriate null checking and error handling",
                        "✓ All elements are connected and serve a purpose",
                        "✓ Flow follows proper naming conventions",
                        "✓ Flow is using the latest API version",
                        ""
                    ])
                else:
                    prompt_parts.extend([
                        "🛠️ DEPLOYMENT SUCCESS CHECKLIST:",
                        "✓ All API names are alphanumeric and start with a letter",
                        "✓ No spaces, hyphens, or special characters in API names", 
                        "✓ All element references are valid and match existing elements",
                        "✓ Flow structure is complete with all required elements",
                        "✓ XML is well-formed and follows Salesforce schema",
                        "✓ Flow logic fulfills the business requirements",
                        ""
                    ])
                
                prompt_parts.extend([
                    "💡 STRATEGY: Start fresh with the business requirements, design the flow to meet them,",
                    "    then apply all the deployment/validation fixes as you build. Use memory context for guidance.",
                    ""
                ])
        
        prompt_parts.extend([
            "📋 FINAL REQUIREMENTS:",
            "1. Generate ONLY complete, valid Salesforce Flow XML",
            "2. Follow Salesforce flow best practices for performance and maintainability",
            "3. Include proper error handling and fault paths where appropriate",
            "4. Use descriptive names for all flow elements",
            "5. Ensure the flow is scalable and follows governor limit best practices",
            "6. If this is a retry, implement ALL required fixes and avoid previous error patterns",
            "7. DO NOT include explanations, markdown, or any text other than the XML",
            "",
            "🚀 Generate the complete Flow XML now:"
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
            
            # Step 4: Use LLM to generate flow design with structured XML output
            logger.info("Generating flow design with LLM")
            
            # Enhanced system prompt for XML generation
            xml_system_prompt = """You are an expert Salesforce Flow developer. Your task is to generate complete, production-ready Salesforce Flow XML based on user requirements and context.

CRITICAL INSTRUCTIONS:
1. Always respond with ONLY the Flow XML - no explanations, markdown, comments or other text
2. Generate complete, valid Salesforce Flow XML that can be deployed immediately
3. Include all required elements: apiVersion, label, processType, status, etc.
4. For retry attempts, carefully analyze the previous error and fix the specific issues
5. Use proper Salesforce Flow XML namespace: http://soap.sforce.com/2006/04/metadata
7. Include processMetadataValues for proper Flow Builder support
8. Ensure all API names are valid (alphanumeric, start with letter, no spaces/hyphens)
9. Start your response immediately with <?xml or <Flow - no other text
10. End your response immediately after </Flow> - no other text

RESPONSE FORMAT:
Your response must be pure XML that starts with either:
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
...
OR just:
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
...

COMMON DEPLOYMENT FIXES:
- API names must be alphanumeric and start with a letter
- Remove spaces, hyphens, and special characters from API names
- Ensure all element references are valid
- Include required flow structure elements
- Use proper XML formatting and indentation

FAILURE LEARNING:
- If this is a retry attempt, you will see specific error analysis and fixes needed
- Apply ALL the required fixes mentioned in the retry context
- Learn from the previous attempt's failures and avoid repeating them"""

            messages = [
                SystemMessage(content=xml_system_prompt),
                HumanMessage(content=enhanced_prompt)
            ]
            
            # Invoke LLM with sufficient token limit for complete Flow XML
            llm_response = self.llm.invoke(
                messages,
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096"))  # Use configurable max tokens
            )
            
            # Step 5: Extract and validate XML from LLM response
            flow_xml = self._extract_and_validate_xml(llm_response.content, request)
            
            if flow_xml:
                # Generate flow definition XML
                flow_definition_xml = self._generate_flow_definition_xml(request)
                
                # Analyze what was created (best effort from XML)
                elements_created = self._analyze_elements_from_xml(flow_xml)
                variables_created = self._analyze_variables_from_xml(flow_xml)
                
                # Enhanced insights from RAG
                enhanced_recommendations = [
                    f"Applied best practices for {analysis['primary_use_case']} flows",
                    f"Considered {len(knowledge['sample_flows'])} similar sample flows",
                    f"Incorporated {len(knowledge['best_practices'])} relevant best practices",
                    "Flow designed with performance and scalability in mind"
                ]
                
                enhanced_best_practices = [
                    f"RAG-enhanced flow for {analysis['complexity_level']} complexity",
                    f"Knowledge-based design for {analysis['primary_use_case']} use case",
                    "LLM-generated XML with structured error learning"
                ]
                
                if request.retry_context:
                    enhanced_recommendations.append(f"Addressed deployment errors from retry #{retry_attempt}")
                    enhanced_best_practices.append("Applied failure learning and memory context")
                
                enhanced_response = FlowBuildResponse(
                    success=True,
                    input_request=request,
                    flow_xml=flow_xml,
                    flow_definition_xml=flow_definition_xml,
                    validation_errors=[],
                    elements_created=elements_created,
                    variables_created=variables_created,
                    best_practices_applied=enhanced_best_practices,
                    recommendations=enhanced_recommendations,
                    deployment_notes="Flow generated using LLM with enhanced context and failure learning",
                    dependencies=[]
                )
                
                # Save successful attempt to memory
                self._save_attempt_to_memory(request.flow_api_name, request, enhanced_response, retry_attempt)
                
                logger.info(f"Successfully generated enhanced flow: {request.flow_api_name}")
                return enhanced_response
            else:
                raise Exception("Failed to extract valid XML from LLM response")
                
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
    
    def _extract_and_validate_xml(self, llm_content: str, request: FlowBuildRequest) -> Optional[str]:
        """Extract and validate XML from LLM response with improved parsing"""
        try:
            # Remove any markdown formatting or extra text
            content = llm_content.strip()
            
            # Add debugging
            logger.info(f"LLM response length: {len(content)} characters")
            logger.info(f"LLM response preview: {content[:200]}...")
            
            # Check for truncated response (critical issue!)
            if content and not content.rstrip().endswith("</Flow>"):
                logger.error("CRITICAL: LLM response appears to be truncated - does not end with </Flow>")
                logger.error(f"Response ends with: ...{content[-100:]}")
                if len(content) > 3000:  # If response is long but truncated
                    logger.error("Response was long but still truncated - increase max_tokens!")
                return None
            
            # Try different extraction methods
            xml_content = None
            
            # Method 1: Look for Flow element with proper XML declaration
            if "<?xml" in content and "<Flow" in content:
                start_idx = content.find("<?xml")
                end_idx = content.rfind("</Flow>")
                if end_idx != -1:
                    end_idx += 7  # Include "</Flow>"
                    xml_content = content[start_idx:end_idx]
                    logger.info("Extracted XML using Method 1 (full XML with declaration)")
            
            # Method 2: Look for Flow element without XML declaration
            elif "<Flow" in content:
                start_idx = content.find("<Flow")
                end_idx = content.rfind("</Flow>")
                if end_idx != -1:
                    end_idx += 7  # Include "</Flow>"
                    xml_content = content[start_idx:end_idx]
                    # Add XML declaration if missing
                    if not xml_content.startswith("<?xml"):
                        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_content
                    logger.info("Extracted XML using Method 2 (Flow without declaration)")
            
            # Method 3: Extract from code blocks
            elif "```xml" in content:
                start_marker = "```xml"
                end_marker = "```"
                start_idx = content.find(start_marker) + len(start_marker)
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    xml_content = content[start_idx:end_idx].strip()
                    if not xml_content.startswith("<?xml") and "<Flow" in xml_content:
                        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_content
                    logger.info("Extracted XML using Method 3 (from ```xml block)")
            
            # Method 4: Extract from any code block
            elif "```" in content:
                lines = content.split('\n')
                in_code_block = False
                xml_lines = []
                for line in lines:
                    if line.strip().startswith("```"):
                        if in_code_block:
                            break  # End of code block
                        else:
                            in_code_block = True  # Start of code block
                            continue
                    elif in_code_block:
                        xml_lines.append(line)
                
                if xml_lines:
                    xml_content = '\n'.join(xml_lines).strip()
                    if "<Flow" in xml_content and not xml_content.startswith("<?xml"):
                        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_content
                    logger.info("Extracted XML using Method 4 (from generic code block)")
            
            if not xml_content:
                logger.error("No XML found in LLM response using any extraction method")
                logger.error(f"Full LLM response: {content}")
                return None
            
            # Validate XML structure
            try:
                ET.fromstring(xml_content)
                logger.info("Successfully extracted and validated XML")
                return xml_content
            except ET.ParseError as e:
                logger.warning(f"XML validation failed: {e}")
                # Try to fix common XML issues
                fixed_xml = self._attempt_xml_fixes(xml_content)
                if fixed_xml:
                    try:
                        ET.fromstring(fixed_xml)
                        logger.info("Successfully fixed and validated XML")
                        return fixed_xml
                    except ET.ParseError as fix_error:
                        logger.error(f"Could not fix XML parsing errors: {fix_error}")
                        logger.error(f"Failed XML content: {xml_content[:500]}...")
                        return None
                else:
                    logger.error("Could not attempt XML fixes")
                    return None
            
        except Exception as e:
            logger.error(f"Error extracting XML: {e}")
            return None
    
    def _attempt_xml_fixes(self, xml_content: str) -> Optional[str]:
        """Attempt to fix common XML issues"""
        try:
            # Remove any content before XML declaration
            if "<?xml" in xml_content:
                xml_start = xml_content.find("<?xml")
                xml_content = xml_content[xml_start:]
            
            # Fix common namespace issues
            if '<Flow' in xml_content and 'xmlns=' not in xml_content:
                xml_content = xml_content.replace('<Flow', '<Flow xmlns="http://soap.sforce.com/2006/04/metadata"')
            
            # Remove any trailing content after </Flow>
            if "</Flow>" in xml_content:
                flow_end = xml_content.rfind("</Flow>") + 7
                xml_content = xml_content[:flow_end]
            
            return xml_content
        except Exception:
            return None
    
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
        
        from xml.dom import minidom
        xml_string = ET.tostring(flow_def_el, encoding='unicode', xml_declaration=True)
        parsed_str = minidom.parseString(xml_string)
        return parsed_str.toprettyxml(indent="    ")
    
    def _analyze_elements_from_xml(self, xml_content: str) -> List[str]:
        """Analyze elements created from XML content"""
        elements = []
        try:
            root = ET.fromstring(xml_content)
            
            # Find different element types
            for child in root:
                if child.tag in ['screens', 'decisions', 'assignments', 'recordLookups', 'recordCreates', 'recordUpdates', 'loops']:
                    name_elem = child.find('name')
                    if name_elem is not None:
                        elements.append(f"{child.tag}: {name_elem.text}")
            
            return elements
        except Exception as e:
            logger.warning(f"Could not analyze elements from XML: {e}")
            return ["XML elements (analysis failed)"]
    
    def _analyze_variables_from_xml(self, xml_content: str) -> List[str]:
        """Analyze variables created from XML content"""
        variables = []
        try:
            root = ET.fromstring(xml_content)
            
            # Find variables
            for var in root.findall('variables'):
                name_elem = var.find('name')
                data_type_elem = var.find('dataType')
                if name_elem is not None:
                    var_desc = name_elem.text
                    if data_type_elem is not None:
                        var_desc += f" ({data_type_elem.text})"
                    variables.append(var_desc)
            
            return variables
        except Exception as e:
            logger.warning(f"Could not analyze variables from XML: {e}")
            return []
    
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