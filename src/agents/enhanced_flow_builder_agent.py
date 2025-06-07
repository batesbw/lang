"""
Enhanced Flow Builder Agent with RAG Integration and Failure Learning

This agent leverages RAG (Retrieval-Augmented Generation) to build better Salesforce flows by:
1. Searching the knowledge base for best practices and patterns
2. Finding similar sample flows for reference
3. Using retrieved context to generate more accurate and robust flows
4. Learning from documented solutions and common patterns
5. Learning from deployment failures and applying fixes
6. Maintaining conversational memory across retry attempts with preserved successful patterns
"""

import os
import logging
from typing import Optional, List, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import xml.etree.ElementTree as ET

from ..tools.rag_tools import RAG_TOOLS, search_flow_knowledge_base, find_similar_sample_flows
from ..tools.flow_builder_tools import BasicFlowXmlGeneratorTool
from ..schemas.flow_builder_schemas import FlowBuildRequest, FlowBuildResponse
from ..state.agent_workforce_state import AgentWorkforceState

logger = logging.getLogger(__name__)

def _log_flow_error(error_type: str, flow_name: str, error_message: str, details: Optional[Dict[str, Any]] = None, retry_attempt: int = 1) -> None:
    """Log Flow errors with improved formatting and readability"""
    separator = "=" * 80
    
    logger.error(f"\n{separator}")
    logger.error(f"🚨 FLOW ERROR: {error_type}")
    logger.error(f"📋 Flow Name: {flow_name}")
    logger.error(f"🔄 Attempt: #{retry_attempt}")
    logger.error(f"❌ Error: {error_message}")
    
    if details:
        logger.error("📊 Additional Details:")
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                logger.error(f"  {key}: {len(value)} items" if isinstance(value, list) else f"  {key}: {value}")
            else:
                logger.error(f"  {key}: {value}")
    
    logger.error(separator)

def _log_flow_success(flow_name: str, details: Optional[Dict[str, Any]] = None, retry_attempt: int = 1) -> None:
    """Log Flow success with improved formatting and readability"""
    separator = "=" * 80
    
    logger.info(f"\n{separator}")
    logger.info(f"✅ FLOW SUCCESS: {flow_name}")
    logger.info(f"🔄 Attempt: #{retry_attempt}")
    
    if details:
        logger.info("📊 Success Details:")
        for key, value in details.items():
            if isinstance(value, list):
                logger.info(f"  {key}: {len(value)} items")
                if value:  # Show first few items
                    for item in value[:3]:
                        logger.info(f"    - {item}")
                    if len(value) > 3:
                        logger.info(f"    ... and {len(value) - 3} more")
            else:
                logger.info(f"  {key}: {value}")
    
    logger.info(separator)

class FlowBuildingMemory:
    """Custom memory system that preserves successful patterns and key improvements"""
    
    def __init__(self, max_attempts: int = 10):
        self.max_attempts = max_attempts
        self.attempts: List[Dict[str, Any]] = []
        self.successful_patterns: List[str] = []
        self.failed_patterns: List[str] = []
        self.key_insights: List[str] = []
    
    def add_attempt(self, attempt_data: Dict[str, Any]) -> None:
        """Add a new attempt and extract patterns"""
        # Check if this attempt number already exists and remove it (deduplication)
        attempt_num = attempt_data.get('retry_attempt', 1)
        self.attempts = [a for a in self.attempts if a.get('retry_attempt', 1) != attempt_num]
        
        # Now add the new attempt
        self.attempts.append(attempt_data)
        
        # Extract patterns based on success/failure
        if attempt_data.get('success', False):
            # Extract successful patterns
            if attempt_data.get('flow_xml'):
                xml_length = len(attempt_data['flow_xml'])
                self.successful_patterns.append(f"Generated valid XML of length {xml_length}")
            
            if attempt_data.get('elements_created'):
                elements = attempt_data['elements_created']
                self.successful_patterns.append(f"Successfully created elements: {', '.join(elements)}")
            
            if attempt_data.get('best_practices_applied'):
                practices = attempt_data['best_practices_applied']
                self.successful_patterns.append(f"Applied best practices: {', '.join(practices)}")
            
            # Add key insights from successful attempts
            if attempt_data.get('retry_attempt', 1) > 1:
                self.key_insights.append(f"Retry attempt #{attempt_data['retry_attempt']} succeeded - this approach should be preserved")
        else:
            # Extract failed patterns with more detail
            error_msg = attempt_data.get('error_message', '')
            if error_msg:
                self.failed_patterns.append(f"Failed approach: {error_msg}")
            
            # CRITICAL: Extract specific validation errors as failed patterns
            validation_errors = attempt_data.get('validation_errors', [])
            for error in validation_errors[:3]:  # Track top 3 validation errors
                error_type = error.get('error_type', 'unknown')
                error_msg = error.get('error_message', '')[:80]
                self.failed_patterns.append(f"Validation error: {error_type} - {error_msg}")
        
        # Limit memory size
        if len(self.attempts) > self.max_attempts:
            # Keep most recent attempts and preserve successful ones
            successful_attempts = [a for a in self.attempts if a.get('success', False)]
            recent_attempts = self.attempts[-5:]  # Keep last 5
            
            # Combine, avoiding duplicates
            preserved_attempts = successful_attempts + recent_attempts
            # Remove duplicates by attempt number
            seen_attempts = set()
            unique_attempts = []
            for attempt in preserved_attempts:
                attempt_id = f"{attempt.get('retry_attempt', 1)}_{attempt.get('success', False)}"
                if attempt_id not in seen_attempts:
                    unique_attempts.append(attempt)
                    seen_attempts.add(attempt_id)
            
            self.attempts = unique_attempts
    
    def get_memory_context(self) -> str:
        """Generate memory context that prioritizes successful patterns"""
        if not self.attempts:
            return "No previous attempts found for this flow."
        
        context_parts = []
        
        # Add successful patterns first (most important)
        if self.successful_patterns:
            context_parts.append("🎯 SUCCESSFUL PATTERNS TO PRESERVE:")
            for pattern in self.successful_patterns[-5:]:  # Last 5 successful patterns
                context_parts.append(f"  ✅ {pattern}")
            context_parts.append("")
        
        # Add key insights
        if self.key_insights:
            context_parts.append("💡 KEY INSIGHTS:")
            for insight in self.key_insights[-3:]:  # Last 3 insights
                context_parts.append(f"  🧠 {insight}")
            context_parts.append("")
        
        # Add recent attempt summary
        context_parts.append("📊 RECENT ATTEMPTS SUMMARY:")
        for attempt in self.attempts[-3:]:  # Last 3 attempts
            attempt_num = attempt.get('retry_attempt', 1)
            success = attempt.get('success', False)
            status = "✅ SUCCESS" if success else "❌ FAILED"
            
            if success:
                context_parts.append(f"  Attempt #{attempt_num}: {status}")
                context_parts.append(f"    - Generated valid flow XML")
                if attempt.get('elements_created'):
                    context_parts.append(f"    - Created {len(attempt['elements_created'])} elements")
                if attempt.get('best_practices_applied'):
                    context_parts.append(f"    - Applied {len(attempt['best_practices_applied'])} best practices")
                context_parts.append(f"    - THIS APPROACH WORKED - PRESERVE IT!")
            else:
                error_msg = attempt.get('error_message', 'Unknown error')
                context_parts.append(f"  Attempt #{attempt_num}: {status} - {error_msg}")
                
                # CRITICAL FIX: Include specific validation errors!
                validation_errors = attempt.get('validation_errors', [])
                if validation_errors:
                    context_parts.append(f"    Specific errors that caused failure:")
                    for i, error in enumerate(validation_errors[:5], 1):  # Show up to 5 errors
                        error_type = error.get('error_type', 'unknown')
                        error_msg = error.get('error_message', 'No details')[:100]
                        context_parts.append(f"      {i}. {error_type}: {error_msg}")
                    if len(validation_errors) > 5:
                        context_parts.append(f"      ... and {len(validation_errors) - 5} more errors")
        
        context_parts.append("")
        
        # Add patterns to avoid WITH SPECIFIC DETAILS
        if self.failed_patterns:
            context_parts.append("⚠️ PATTERNS TO AVOID (from failed attempts):")
            for pattern in self.failed_patterns[-5:]:  # Last 5 failed patterns
                context_parts.append(f"  ❌ {pattern}")
            context_parts.append("")
        
        # Add critical instruction
        context_parts.extend([
            "🚨 CRITICAL MEMORY INSTRUCTION:",
            "If a previous attempt succeeded (marked with ✅), you MUST build upon that success.",
            "Do NOT revert to approaches that already failed. Preserve successful patterns.",
            "Each retry should be BETTER than the last successful attempt, not worse.",
            "LEARN from the specific errors listed above - do not repeat them!",
            ""
        ])
        
        return "\n".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory for persistence"""
        return {
            "attempts": self.attempts,
            "successful_patterns": self.successful_patterns,
            "failed_patterns": self.failed_patterns,
            "key_insights": self.key_insights
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowBuildingMemory":
        """Deserialize memory from persistence"""
        memory = cls()
        memory.attempts = data.get("attempts", [])
        memory.successful_patterns = data.get("successful_patterns", [])
        memory.failed_patterns = data.get("failed_patterns", [])
        memory.key_insights = data.get("key_insights", [])
        return memory

class EnhancedFlowBuilderAgent:
    """Enhanced Flow Builder Agent with RAG capabilities, failure learning, and improved memory"""
    
    def __init__(self, llm: BaseLanguageModel, persisted_memory_data: Optional[Dict[str, Any]] = None):
        self.llm = llm
        self.xml_generator = BasicFlowXmlGeneratorTool()
        
        # Use custom memory system instead of ConversationSummaryBufferMemory
        self._flow_memories: Dict[str, FlowBuildingMemory] = {}
        if persisted_memory_data:
            self._load_persisted_memory(persisted_memory_data)
        
        # System prompt for the enhanced agent
        self.system_prompt = """
        You are an expert Salesforce Flow Builder Agent with access to a comprehensive knowledge base, 
        sample flow repository, deployment failure learning system, and enhanced memory. Your role is to create high-quality, 
        production-ready Salesforce flows based on user requirements and learn from past attempts.
        
        Your capabilities include:
        1. Searching the knowledge base for best practices, patterns, and troubleshooting guides
        2. Finding similar sample flows that match the requirements
        3. Learning from past deployment failures and applying successful fixes
        4. Analyzing retrieved context to inform flow design decisions
        5. Generating robust, well-structured flow XML
        6. Providing recommendations and explanations for design choices
        7. Adapting flows based on failure patterns and successful resolutions
        8. Maintaining memory of previous attempts with preserved successful patterns
        
        When building flows, always:
        - Start by understanding the business requirements thoroughly
        - Check for similar past failures and their resolutions
        - Review your previous attempts and PRESERVE successful patterns from earlier attempts
        - Search for relevant best practices and patterns
        - Look for similar sample flows for reference
        - Apply Salesforce flow best practices (performance, error handling, etc.)
        - Generate clean, maintainable flow XML with failure prevention in mind
        - Provide clear explanations for your design decisions
        - Learn from any deployment failures to improve future flows
        - BUILD UPON previous successful attempts - never regress to failed approaches
        
        When fixing deployment failures:
        - Analyze the error message and categorize the failure type
        - Look for similar past failures and successful fixes
        - Review what you tried before and what WORKED in previous attempts
        - Apply proven solutions from successful attempts
        - Document the attempted fix for future learning
        - Focus on the most likely root cause based on historical data and previous attempts
        - NEVER repeat approaches that already failed
        - ALWAYS preserve elements and patterns from successful attempts
        
        Focus on creating flows that are:
        - Performant and scalable
        - Error-resistant with proper fault handling
        - Well-documented and maintainable
        - Following Salesforce best practices
        - Avoiding known failure patterns
        - Building upon successful patterns from previous attempts
        
        CRITICAL: If you see successful patterns from previous attempts, you MUST preserve and build upon them.
        Never regress to approaches that already failed. Each attempt should be better than the last.
        """
    
    def _load_persisted_memory(self, persisted_memory_data: Dict[str, Any]) -> None:
        """Load persisted memory data back into the agent"""
        try:
            for flow_api_name, memory_data in persisted_memory_data.items():
                if memory_data:
                    # Create new memory instance for this flow
                    memory = FlowBuildingMemory()
                    
                    # Restore memory data
                    memory.attempts = memory_data.get("attempts", [])
                    memory.successful_patterns = memory_data.get("successful_patterns", [])
                    memory.failed_patterns = memory_data.get("failed_patterns", [])
                    memory.key_insights = memory_data.get("key_insights", [])
                    
                    self._flow_memories[flow_api_name] = memory
                    logger.info(f"Restored memory for flow: {flow_api_name} with {len(memory_data['attempts'])} attempts")
        except Exception as e:
            logger.warning(f"Failed to load persisted memory: {str(e)}")
    
    def get_memory_data_for_persistence(self) -> Dict[str, Any]:
        """Extract memory data for persistence in state"""
        memory_data = {}
        try:
            for flow_api_name, memory in self._flow_memories.items():
                memory_data[flow_api_name] = memory.to_dict()
        except Exception as e:
            logger.warning(f"Failed to extract memory data for persistence: {str(e)}")
            
        return memory_data
    
    def _get_flow_memory(self, flow_api_name: str) -> FlowBuildingMemory:
        """Get or create memory for a specific flow"""
        if flow_api_name not in self._flow_memories:
            self._flow_memories[flow_api_name] = FlowBuildingMemory()
        return self._flow_memories[flow_api_name]
    
    def _save_attempt_to_memory(self, flow_api_name: str, request: FlowBuildRequest, 
                               response: FlowBuildResponse, attempt_number: int = 1, validation_passed: Optional[bool] = None) -> None:
        """Save a flow building attempt to memory with enhanced context"""
        memory = self._get_flow_memory(flow_api_name)
        
        # CRITICAL FIX: Only mark as successful if BOTH XML generation AND validation succeed
        # If validation_passed is provided, use that to override the response.success
        actual_success = response.success
        if validation_passed is not None:
            actual_success = validation_passed
        
        # Create enhanced attempt data for the new memory system
        attempt_data = {
            "retry_attempt": attempt_number,
            "success": actual_success,  # Use actual_success instead of response.success
            "flow_api_name": request.flow_api_name,
            "flow_label": request.flow_label,
            "flow_description": request.flow_description,
            "user_story_title": request.user_story.title if request.user_story else None,
            "user_story_priority": request.user_story.priority if request.user_story else None,
            "flow_xml": response.flow_xml if response.success else None,
            "elements_created": response.elements_created if response.success else [],
            "variables_created": response.variables_created if response.success else [],
            "best_practices_applied": response.best_practices_applied if response.success else [],
            "recommendations": response.recommendations if response.success else [],
            "error_message": response.error_message if not actual_success else None,
            "validation_errors": self._extract_validation_errors(response.validation_errors) if response.validation_errors else [],
            "retry_context": request.retry_context
        }
        
        # Save to our custom memory system
        try:
            memory.add_attempt(attempt_data)
            status_msg = "SUCCESS" if actual_success else "FAILED"
            logger.info(f"Saved enhanced attempt #{attempt_number} ({status_msg}) to memory for flow: {flow_api_name}")
        except Exception as e:
            logger.warning(f"Failed to save attempt to memory: {str(e)}")
    
    def _extract_validation_errors(self, validation_errors: List[Any]) -> List[Dict[str, str]]:
        """Extract validation error information safely"""
        extracted_errors = []
        for error in validation_errors:
            try:
                if hasattr(error, 'error_type') and hasattr(error, 'error_message'):
                    extracted_errors.append({
                        "error_type": error.error_type,
                        "error_message": error.error_message
                    })
                elif isinstance(error, dict):
                    extracted_errors.append({
                        "error_type": error.get('error_type', 'unknown'),
                        "error_message": error.get('error_message', str(error))
                    })
                else:
                    extracted_errors.append({
                        "error_type": "unknown",
                        "error_message": str(error)
                    })
            except Exception as e:
                logger.warning(f"Failed to extract validation error: {e}")
                extracted_errors.append({
                    "error_type": "extraction_error",
                    "error_message": str(error)
                })
        return extracted_errors
    
    def _get_memory_context(self, flow_api_name: str) -> str:
        """Get conversation history from memory for context"""
        memory = self._get_flow_memory(flow_api_name)
        
        try:
            return memory.get_memory_context()
        except Exception as e:
            logger.warning(f"Failed to load memory context: {str(e)}")
            return "Unable to load previous attempt context."
    
    def clear_flow_memory(self, flow_api_name: str) -> None:
        """Clear memory for a specific flow (useful for starting fresh)"""
        if flow_api_name in self._flow_memories:
            self._flow_memories[flow_api_name] = FlowBuildingMemory()
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
        
        # TODO: RAG searches temporarily commented out - will return to them later
        logger.info("RAG searches temporarily disabled - returning empty knowledge")
        
        # try:
        #     # Search for best practices
        #     for query in analysis["search_queries"]:
        #         docs = search_flow_knowledge_base.invoke({
        #             "query": query,
        #             "category": "best_practices",
        #             "max_results": 3
        #         })
        #         knowledge["best_practices"].extend(docs)
        #     
        #     # Search for examples and patterns
        #     for query in analysis["search_queries"]:
        #         docs = search_flow_knowledge_base.invoke({
        #             "query": query,
        #             "category": "examples",
        #             "max_results": 2
        #         })
        #         knowledge["patterns"].extend(docs)
        #     
        #     # Find similar sample flows
        #     sample_flows = find_similar_sample_flows.invoke({
        #         "requirements": analysis["search_queries"][0],  # Primary query
        #         "use_case": analysis["primary_use_case"],
        #         "complexity": analysis["complexity_level"]
        #     })
        #     knowledge["sample_flows"] = sample_flows
        #     
        #     # Search for troubleshooting info
        #     troubleshooting_docs = search_flow_knowledge_base.invoke({
        #         "query": f"{analysis['primary_use_case']} troubleshooting",
        #         "category": "troubleshooting",
        #         "max_results": 2
        #     })
        #     knowledge["troubleshooting"] = troubleshooting_docs
        #     
        #     logger.info(f"Retrieved comprehensive knowledge: {len(knowledge['best_practices'])} best practices, "
        #                f"{len(knowledge['sample_flows'])} sample flows, "
        #                f"{len(knowledge['patterns'])} patterns, "
        #                f"{len(knowledge['troubleshooting'])} troubleshooting guides")
        #     
        # except Exception as e:
        #     logger.error(f"Error retrieving knowledge: {str(e)}")
        #     # Return empty knowledge on error to allow flow generation to continue
        #     knowledge = {
        #         "best_practices": [],
        #         "sample_flows": [],
        #         "patterns": [],
        #         "troubleshooting": []
        #     }
        
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
        
        # Add TDD context if available - this is the key enhancement for test-driven development
        if request.tdd_context:
            tdd_context = request.tdd_context
            prompt_parts.extend([
                "🧪 TEST-DRIVEN DEVELOPMENT CONTEXT:",
                "This Flow is being built using a Test-Driven Development approach.",
                "The test scenarios and Apex test classes have already been deployed.",
                "Your job is to build a Flow that will make these tests PASS.",
                ""
            ])
            
            # Add test scenarios information
            test_scenarios = tdd_context.get("test_scenarios", [])
            if test_scenarios:
                prompt_parts.extend([
                    "📋 DEPLOYED TEST SCENARIOS (Build Flow to satisfy these):",
                ])
                for i, scenario in enumerate(test_scenarios, 1):
                    scenario_name = scenario.get("title", scenario.get("name", f"Scenario {i}"))
                    scenario_desc = scenario.get("description", "")
                    scenario_type = scenario.get("scenario_type", "").title()
                    priority = scenario.get("priority", "Medium")
                    
                    prompt_parts.extend([
                        f"{i}. {scenario_name} ({scenario_type} - {priority} Priority)",
                        f"   Description: {scenario_desc}",
                    ])
                    
                    # Add test steps if available
                    test_steps = scenario.get("test_steps", [])
                    if test_steps:
                        prompt_parts.append("   Test Steps:")
                        for step in test_steps[:3]:  # Show first 3 steps
                            prompt_parts.append(f"     • {step}")
                        if len(test_steps) > 3:
                            prompt_parts.append(f"     ... and {len(test_steps) - 3} more steps")
                    
                    # Add expected outcomes
                    expected_outcomes = scenario.get("expected_outcomes", [])
                    if expected_outcomes:
                        prompt_parts.append("   Expected Outcomes:")
                        for outcome in expected_outcomes[:2]:  # Show first 2 outcomes
                            prompt_parts.append(f"     ✓ {outcome}")
                        if len(expected_outcomes) > 2:
                            prompt_parts.append(f"     ... and {len(expected_outcomes) - 2} more outcomes")
                    
                    # Add success criteria
                    success_criteria = scenario.get("success_criteria", [])
                    if success_criteria:
                        prompt_parts.append("   Success Criteria:")
                        for criteria in success_criteria[:2]:  # Show first 2 criteria
                            prompt_parts.append(f"     ✓ {criteria}")
                        if len(success_criteria) > 2:
                            prompt_parts.append(f"     ... and {len(success_criteria) - 2} more criteria")
                    
                    prompt_parts.append("")
                
                prompt_parts.extend([
                    "🎯 TDD REQUIREMENT:",
                    "Your Flow MUST be designed to make all these test scenarios pass.",
                    "Focus on implementing the exact functionality that the tests expect.",
                    ""
                ])
            
            # Add Apex test classes information
            apex_test_classes = tdd_context.get("apex_test_classes", [])
            if apex_test_classes:
                prompt_parts.extend([
                    "🧪 DEPLOYED APEX TEST CLASSES (Flow must pass these tests):",
                ])
                for i, test_class in enumerate(apex_test_classes, 1):
                    class_name = test_class.get("class_name", f"TestClass{i}")
                    test_methods = test_class.get("test_methods", [])
                    
                    prompt_parts.extend([
                        f"{i}. {class_name} ({len(test_methods)} test methods)",
                    ])
                    
                    # Show test method names and descriptions
                    for method in test_methods[:3]:  # Show first 3 methods
                        method_name = method.get("method_name", "Unknown")
                        method_desc = method.get("description", "")
                        prompt_parts.append(f"     • {method_name}: {method_desc}")
                    
                    if len(test_methods) > 3:
                        prompt_parts.append(f"     ... and {len(test_methods) - 3} more test methods")
                    
                    prompt_parts.append("")
                
                prompt_parts.extend([
                    "⚠️ CRITICAL TDD CONSTRAINT:",
                    "The Apex test classes are already deployed and expecting specific Flow behavior.",
                    "Your Flow implementation must match what these tests are validating.",
                    "Study the test scenarios above to understand the exact requirements.",
                    ""
                ])
            
            # Add TDD best practices
            prompt_parts.extend([
                "🔬 TDD DEVELOPMENT PRINCIPLES:",
                "1. RED-GREEN-REFACTOR: Tests are already written (RED), now make them pass (GREEN)",
                "2. Focus on making tests pass with the simplest implementation that works",
                "3. Implement only the functionality that is actually tested",
                "4. Ensure your Flow logic aligns with the test expectations",
                "5. Consider edge cases and error scenarios covered by the tests",
                ""
            ])
        
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
        
        # Add best practices from general RAG
        if knowledge.get("best_practices"):
            prompt_parts.append("SALESFORCE FLOW BEST PRACTICES:")
            for doc in knowledge["best_practices"][:3]:
                prompt_parts.append(f"- {doc['content'][:200]}...")
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
            
            # Handle deployment failures only (validation removed from workflow)
            if deployment_error or original_flow_xml:
                prompt_parts.extend([
                    f"🔄 DEPLOYMENT RETRY CONTEXT (Attempt #{retry_attempt}):",
                    "The previous flow deployment FAILED and must be completely rebuilt to fix the errors.",
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
                    # Don't truncate the XML - include it all for proper analysis
                    # But add a clear separator to show where it ends
                    prompt_parts.extend([
                        "🔍 PREVIOUS FLOW XML (ANALYZE FOR SPECIFIC ERRORS TO FIX):",
                        "```xml",
                        original_flow_xml,
                        "```",
                        "⚠️ END OF PREVIOUS FLOW XML",
                        ""
                    ])
                
                prompt_parts.extend([
                    "🎯 CRITICAL RETRY REQUIREMENTS:",
                    "1. ANALYZE the previous flow XML above to understand what was implemented",
                    "2. IDENTIFY the specific errors mentioned in the deployment error",
                    "3. FIX ONLY those specific errors - do not make unnecessary changes",
                    "4. PRESERVE all other aspects of the flow that were working correctly",
                    "5. MAINTAIN the same business logic and flow structure where possible",
                    "6. ENSURE the flow still fulfills the original user story requirements",
                    ""
                ])
            
            if error_analysis:
                prompt_parts.extend([
                    "📊 STRUCTURED ERROR ANALYSIS:",
                    f"Error Type: {error_analysis.get('error_type', 'unknown')}",
                    f"Severity: {error_analysis.get('severity', 'medium')}",
                    ""
                ])
                
                # Special handling for duplicate elements error
                if error_analysis.get('error_type') == 'duplicate_elements':
                    duplicated_element = error_analysis.get('dynamic_context', {}).get('duplicated_element', 'element')
                    prompt_parts.extend([
                        "🚨 CRITICAL DUPLICATE ELEMENT ERROR DETECTED:",
                        f"The previous XML contains duplicate '{duplicated_element}' elements with the same name.",
                        "",
                        "🔍 DUPLICATE ELEMENT FIX INSTRUCTIONS:",
                        f"1. Scan the previous XML for ALL <{duplicated_element}> elements",
                        f"2. Look for multiple <{duplicated_element}> elements that have the same <name> value",
                        f"3. REMOVE the duplicate <{duplicated_element}> elements - keep only ONE of each unique name",
                        f"4. If the duplicate logic is needed, CONSOLIDATE it into a single <{duplicated_element}> element",
                        f"5. Ensure each remaining <{duplicated_element}> element has a UNIQUE <name> within the Flow",
                        "",
                        "⚠️ CRITICAL: Salesforce Flow metadata does NOT allow duplicate element names within the same element type.",
                        f"You MUST ensure NO two <{duplicated_element}> elements share the same <name> value.",
                        ""
                    ])
                
                # Add specific fixes if available
                specific_fixes = error_analysis.get('specific_fixes_needed', [])
                if specific_fixes:
                    prompt_parts.extend([
                        "🔧 SPECIFIC FIXES REQUIRED:",
                        "These are the exact issues you MUST fix in the Flow XML:"
                    ])
                    for i, fix in enumerate(specific_fixes, 1):
                        prompt_parts.append(f"{i}. {fix}")
                    prompt_parts.extend([
                        "",
                        "⚠️ CRITICAL: Apply ALL fixes listed above - these address the exact deployment error.",
                        ""
                    ])
                
                if error_analysis.get('api_name_issues'):
                    prompt_parts.extend([
                        "🏷️ API NAME ISSUES DETECTED:",
                        "- Review API names in the previous XML and fix any that are invalid",
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
                    "🔧 SPECIFIC FIXES REQUIRED:",
                    "Based on the deployment error, these are the exact issues to address:",
                ])
                for i, fix in enumerate(specific_fixes, 1):
                    prompt_parts.append(f"{i}. {fix}")
                prompt_parts.extend([
                    "",
                    "🎯 FIXING APPROACH:",
                    "- Take the previous flow XML as your starting point",
                    "- Make ONLY the minimal changes needed to fix the specific errors listed above",
                    "- Do NOT redesign or restructure the flow unnecessarily", 
                    "- Preserve the existing business logic and flow elements where they work",
                    "- Focus on the root cause of each specific error",
                    ""
                ])
            
            if error_patterns:
                prompt_parts.extend([
                    "⚠️ ERROR PATTERNS TO AVOID:",
                    f"The following patterns caused the previous failure: {', '.join(error_patterns)}",
                    "- Analyze these patterns in the context of the previous XML",
                    "- Ensure your fixes address these specific failure patterns",
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
                    "🔥 SPECIFIC DEPLOYMENT ERROR TO FIX:",
                    deployment_error,
                    "",
                    "💡 ERROR ANALYSIS APPROACH:",
                    "- Read the deployment error message carefully",
                    "- Locate the problematic elements/sections in the previous XML",
                    "- Apply the precise fix needed for this specific error",
                    "- Verify that your fix resolves the exact issue mentioned",
                    ""
                ])
            
            prompt_parts.extend([
                "🛠️ DEPLOYMENT SUCCESS CHECKLIST:",
                "Review your changes against these criteria:",
                "✓ The specific deployment error has been addressed",
                "✓ No unnecessary changes were made to working parts of the flow",
                "✓ The flow still meets the original business requirements",
                "✓ All API names are valid (alphanumeric, start with letter, no spaces/hyphens)",
                "✓ Flow structure and references are correct",
                "✓ XML is well-formed and follows Salesforce schema",
                ""
            ])
            
            prompt_parts.extend([
                "💡 FIXING STRATEGY:",
                "1. ANALYZE - Study the previous XML and identify the problematic sections",
                "2. LOCATE - Find the exact elements/attributes causing the deployment error",
                "3. FIX - Make precise, minimal changes to resolve the specific issues",
                "4. PRESERVE - Keep everything else from the previous flow intact",
                "5. VALIDATE - Ensure your changes address the deployment error completely",
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
4. ALWAYS set the Flow status to 'Active' - use <status>Active</status> in your XML
5. For retry attempts, carefully analyze the previous error and fix the specific issues
6. Use proper Salesforce Flow XML namespace: http://soap.sforce.com/2006/04/metadata
7. Record Triggered Flows can't combine Create/Update AND Delete operations in the same flow. A separate flow is required for the Delete operation.
8. Include processMetadataValues for proper Flow Builder support
9. Ensure all API names are valid (alphanumeric, start with letter, no spaces/hyphens)
10. Start your response immediately with <?xml or <Flow - no other text
11. End your response immediately after </Flow> - no other text

RESPONSE FORMAT:
Your response must be pure XML that starts with either:
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
...
OR just:
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
...

FLOW STATUS REQUIREMENT:
ALWAYS set the Flow status to 'Active' - use <status>Active</status> in your XML
NEVER use <status>Draft</status> - ALWAYS use <status>Active</status>
ALWAYS include <status>Active</status> in your Flow XML to deploy the Flow in an active state.

CRITICAL SALESFORCE FLOW RESTRICTIONS:
1. COLLECTION VARIABLES:
   - Collection variables CANNOT be used directly in inputAssignments
   - Use Assignment elements to add items to collections
   - In Get Records, use outputReference for the collection variable
   - In Create/Update Records, reference the collection variable directly as the input
   - NEVER use collection variables in individual field assignments

2. ELEMENT REFERENCES:
   - All element references must point to actual elements that exist in the flow
   - Element names are case-sensitive and must match exactly
   - Use proper syntax: elementName.fieldName or elementName.variableName
   - For Get Records elements, reference the count using: elementName (not elementName.Count)

3. VARIABLE USAGE:
   - Record variables for individual records
   - Collection variables for multiple records  
   - Number variables for counts/calculations
   - Text variables for strings
   - Boolean variables for true/false values

4. DUPLICATE ELEMENTS (CRITICAL XML VALIDATION):
   - NEVER create duplicate XML elements with the same name within the same element type
   - Each element type (recordLookups, recordCreates, recordUpdates, etc.) must have unique names
   - If you see duplicate elements in previous XML, REMOVE the duplicates and keep only one
   - Example: If there are two <recordLookups> elements with the same <name>, keep only one
   - Consolidate duplicate logic into a single element rather than creating duplicates
   - Review the entire XML structure to ensure no element names are repeated within their type

COMMON DEPLOYMENT FIXES:
- API names must be alphanumeric and start with a letter
- Remove spaces, hyphens, and special characters from API names
- Ensure all element references are valid and point to existing elements
- Include required flow structure elements
- Use proper XML formatting and indentation
- For aggregating/counting: Use Get Records with collection output, then reference the collection size
- ELIMINATE DUPLICATE ELEMENTS: Check for and remove any duplicate elements (same name within same type)

FAILURE LEARNING:
- If this is a retry attempt, you will see specific error analysis and fixes needed
- Apply ALL the required fixes mentioned in the retry context
- Learn from the previous attempt's failures and avoid repeating them
- Pay special attention to collection variable usage restrictions
- Verify all element references are correct and point to existing elements
- SPECIAL ATTENTION: If the error mentions "duplicate" or "duplicated", carefully scan the XML for duplicate elements and remove them

FAILURE LEARNING:
- If this is a retry attempt, you will see specific error analysis and fixes needed
- Apply ALL the required fixes mentioned in the retry context
- Learn from the previous attempt's failures and avoid repeating them
- Pay special attention to collection variable usage restrictions
- Verify all element references are correct and point to existing elements"""

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
                
                # Save attempt to memory as "pending validation" - real success depends on validation
                self._save_attempt_to_memory(request.flow_api_name, request, enhanced_response, retry_attempt, validation_passed=False)  # Mark as failed until validation confirms success
                
                # Use structured success logging
                _log_flow_success(
                    flow_name=request.flow_api_name,
                    details={
                        "elements_created": elements_created,
                        "variables_created": variables_created,
                        "best_practices": enhanced_best_practices,
                        "xml_length": len(flow_xml),
                        "use_case": analysis['primary_use_case'],
                        "complexity": analysis['complexity_level']
                    },
                    retry_attempt=retry_attempt
                )
                
                return enhanced_response
            else:
                raise Exception("Failed to extract valid XML from LLM response")
                
        except Exception as e:
            error_message = f"Enhanced FlowBuilderAgent error: {str(e)}"
            
            # Use structured error logging
            _log_flow_error(
                error_type="Flow Generation Error",
                flow_name=request.flow_api_name,
                error_message=str(e),
                details={
                    "flow_description": request.flow_description,
                    "retry_context": "Yes" if request.retry_context else "No",
                    "user_story": request.user_story.title if request.user_story else "None",
                    "exception_type": type(e).__name__
                },
                retry_attempt=retry_attempt
            )
            
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
                error_details = {
                    "response_length": len(content),
                    "response_ending": content[-100:] if len(content) > 100 else content,
                    "is_long_response": len(content) > 3000,
                    "contains_flow_start": "<Flow" in content
                }
                
                _log_flow_error(
                    error_type="XML Extraction - Truncated Response",
                    flow_name=request.flow_api_name,
                    error_message="LLM response appears to be truncated - does not end with </Flow>",
                    details=error_details
                )
                
                if len(content) > 3000:  # If response is long but truncated
                    logger.error("⚠️  Response was long but still truncated - consider increasing max_tokens!")
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
                error_details = {
                    "response_length": len(content),
                    "response_preview": content[:300],
                    "contains_xml_declaration": "<?xml" in content,
                    "contains_flow_tag": "<Flow" in content,
                    "contains_code_blocks": "```" in content
                }
                
                _log_flow_error(
                    error_type="XML Extraction - No XML Found",
                    flow_name=request.flow_api_name,
                    error_message="No XML found in LLM response using any extraction method",
                    details=error_details
                )
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
                        error_details = {
                            "original_parse_error": str(e),
                            "fix_attempt_error": str(fix_error),
                            "xml_length": len(xml_content),
                            "xml_preview": xml_content[:500],
                            "xml_has_declaration": xml_content.startswith("<?xml"),
                            "xml_has_namespace": "xmlns=" in xml_content
                        }
                        
                        _log_flow_error(
                            error_type="XML Validation - Parse Error (Unfixable)",
                            flow_name=request.flow_api_name,
                            error_message=f"Could not fix XML parsing errors: {fix_error}",
                            details=error_details
                        )
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

    def update_memory_with_deployment_result(self, flow_api_name: str, attempt_number: int, deployment_success: bool, deployment_errors: Optional[List[Any]] = None, error_message: str = "") -> None:
        """Update memory with deployment results - critical for learning from deployment failures"""
        memory = self._get_flow_memory(flow_api_name)
        
        try:
            # Find the attempt to update
            target_attempt = None
            for i, attempt in enumerate(reversed(memory.attempts)):
                if attempt.get('retry_attempt') == attempt_number:
                    target_attempt = attempt
                    break
            
            if target_attempt:
                # Update success status based on deployment
                old_success = target_attempt.get('success', False)
                target_attempt['success'] = deployment_success
                
                # Add deployment error details if failed
                if not deployment_success:
                    # Convert deployment errors to validation error format for consistency
                    validation_errors = []
                    if deployment_errors:
                        for error in deployment_errors:
                            if isinstance(error, dict):
                                validation_errors.append({
                                    'error_type': 'deployment_error',
                                    'error_message': error.get('problem', str(error)),
                                    'component': error.get('fullName', 'Unknown'),
                                    'component_type': error.get('componentType', 'Unknown')
                                })
                            else:
                                validation_errors.append({
                                    'error_type': 'deployment_error', 
                                    'error_message': str(error),
                                    'component': 'Unknown',
                                    'component_type': 'Unknown'
                                })
                    
                    target_attempt['validation_errors'] = validation_errors
                    target_attempt['error_message'] = error_message or f"Deployment failed with {len(validation_errors)} errors"
                    
                    # Update failed patterns with deployment errors
                    for error in validation_errors[:3]:
                        error_type = error.get('error_type', 'deployment_error')
                        error_msg = error.get('error_message', '')[:80]
                        pattern = f"Deployment error: {error_type} - {error_msg}"
                        if pattern not in memory.failed_patterns:
                            memory.failed_patterns.append(pattern)
                
                # Update patterns based on success/failure change
                if old_success != deployment_success:
                    if old_success and not deployment_success:
                        # Was marked successful but deployment failed
                        self._remove_false_success_patterns(memory, target_attempt)
                    elif not old_success and deployment_success:
                        # Was marked failed but deployment succeeded
                        self._add_success_patterns(memory, target_attempt)
                
                status_msg = "SUCCESS" if deployment_success else "FAILED"
                logger.info(f"Updated memory attempt #{attempt_number} with deployment result ({status_msg}) for flow: {flow_api_name}")
                
            else:
                logger.warning(f"Could not find attempt #{attempt_number} in memory to update with deployment result")
                
        except Exception as e:
            logger.warning(f"Failed to update memory with deployment result: {str(e)}")
    
    def _remove_false_success_patterns(self, memory: FlowBuildingMemory, attempt_data: Dict[str, Any]) -> None:
        """Remove patterns that were added for a false success"""
        try:
            # Remove patterns that would have been added for this attempt
            xml_pattern = f"Generated valid XML of length {len(attempt_data.get('flow_xml', ''))}"
            if xml_pattern in memory.successful_patterns:
                memory.successful_patterns.remove(xml_pattern)
            
            elements = attempt_data.get('elements_created', [])
            if elements:
                element_pattern = f"Successfully created elements: {', '.join(elements)}"
                if element_pattern in memory.successful_patterns:
                    memory.successful_patterns.remove(element_pattern)
            
            practices = attempt_data.get('best_practices_applied', [])
            if practices:
                practice_pattern = f"Applied best practices: {', '.join(practices)}"
                if practice_pattern in memory.successful_patterns:
                    memory.successful_patterns.remove(practice_pattern)
                    
            # Remove key insight about this retry succeeding
            retry_insight = f"Retry attempt #{attempt_data.get('retry_attempt', 1)} succeeded - this approach should be preserved"
            if retry_insight in memory.key_insights:
                memory.key_insights.remove(retry_insight)
                
        except Exception as e:
            logger.warning(f"Failed to remove false success patterns: {str(e)}")
    
    def _add_success_patterns(self, memory: FlowBuildingMemory, attempt_data: Dict[str, Any]) -> None:
        """Add success patterns for a newly validated successful attempt"""
        try:
            # Add patterns that should be added for this successful attempt
            if attempt_data.get('flow_xml'):
                xml_length = len(attempt_data['flow_xml'])
                memory.successful_patterns.append(f"Generated valid XML of length {xml_length}")
            
            elements = attempt_data.get('elements_created', [])
            if elements:
                memory.successful_patterns.append(f"Successfully created elements: {', '.join(elements)}")
            
            practices = attempt_data.get('best_practices_applied', [])
            if practices:
                memory.successful_patterns.append(f"Applied best practices: {', '.join(practices)}")
            
            # Add key insight if this was a retry
            if attempt_data.get('retry_attempt', 1) > 1:
                memory.key_insights.append(f"Retry attempt #{attempt_data['retry_attempt']} succeeded - this approach should be preserved")
                
        except Exception as e:
            logger.warning(f"Failed to add success patterns: {str(e)}")

    def update_memory_with_validation_result(self, flow_api_name: str, attempt_number: int, validation_passed: bool, validation_errors: Optional[List[Any]] = None) -> None:
        """Update the most recent memory entry with validation results - CRITICAL FOR PREVENTING REGRESSION"""
        memory = self._get_flow_memory(flow_api_name)
        
        try:
            # Log current memory state for debugging
            logger.info(f"Updating memory for flow {flow_api_name}, attempt #{attempt_number}")
            logger.info(f"Current memory has {len(memory.attempts)} attempts")
            
            # Find the most recent attempt with matching attempt number
            target_attempt = None
            for i, attempt in enumerate(reversed(memory.attempts)):
                if attempt.get('retry_attempt') == attempt_number:
                    target_attempt = attempt
                    logger.info(f"Found matching attempt at index {len(memory.attempts) - i - 1}")
                    break
            
            if target_attempt:
                # Update the success status based on validation
                old_success = target_attempt.get('success', False)
                target_attempt['success'] = validation_passed
                
                # Add validation error details if failed
                if not validation_passed and validation_errors:
                    target_attempt['validation_errors'] = validation_errors  # Already extracted properly
                    if not target_attempt.get('error_message'):
                        target_attempt['error_message'] = f"Flow validation failed with {len(validation_errors)} errors"
                    
                    # Also update failed patterns with validation errors
                    for error in validation_errors[:3]:
                        error_type = error.get('error_type', 'unknown')
                        error_msg = error.get('error_message', '')[:80]
                        pattern = f"Validation error: {error_type} - {error_msg}"
                        if pattern not in memory.failed_patterns:
                            memory.failed_patterns.append(pattern)
                
                # Re-extract patterns since success status changed
                if old_success != validation_passed:
                    # Remove old patterns from this attempt
                    if old_success and not validation_passed:
                        # Was marked successful but validation failed - remove false success patterns
                        self._remove_false_success_patterns(memory, target_attempt)
                    elif not old_success and validation_passed:
                        # Was marked failed but validation passed - add success patterns
                        self._add_success_patterns(memory, target_attempt)
                
                status_msg = "SUCCESS" if validation_passed else "FAILED"
                logger.info(f"Updated memory attempt #{attempt_number} with validation result ({status_msg}) for flow: {flow_api_name}")
                
                # Log validation errors for debugging
                if validation_errors:
                    logger.info(f"Stored {len(validation_errors)} validation errors in memory")
                    for error in validation_errors[:3]:
                        logger.debug(f"  - {error.get('error_type', 'unknown')}: {error.get('error_message', 'no message')[:60]}")
            else:
                logger.warning(f"Could not find attempt #{attempt_number} in memory to update with validation result")
                
        except Exception as e:
            logger.warning(f"Failed to update memory with validation result: {str(e)}")


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
                
                # Show specific fixes that will be applied
                specific_fixes = flow_build_request.retry_context.get('specific_fixes_needed', [])
                if specific_fixes:
                    print(f"🛠️  RETRY FIXES to apply in this attempt:")
                    for i, fix in enumerate(specific_fixes[:5], 1):  # Show first 5 fixes
                        print(f"      {i}. {fix}")
                    if len(specific_fixes) > 5:
                        print(f"      ... and {len(specific_fixes) - 5} more fixes")
                
                # Show deployment error being addressed
                deployment_error = flow_build_request.retry_context.get('deployment_error', '')
                if deployment_error:
                    truncated_error = deployment_error[:150] + "..." if len(deployment_error) > 150 else deployment_error
                    print(f"📋 ADDRESSING DEPLOYMENT ERROR: {truncated_error}")
                
            else:
                print("📝 INITIAL ATTEMPT: Using unified RAG approach")
                print("🧠 MEMORY: Starting fresh memory tracking for this flow")
            
            # Load persisted memory data from state
            persisted_memory_data = state.get("flow_builder_memory_data", {})
            
            # Initialize the enhanced agent with persistent memory
            agent = EnhancedFlowBuilderAgent(llm, persisted_memory_data)
            
            # Check if we have memory context for this flow
            memory_context = agent._get_memory_context(flow_build_request.flow_api_name)
            if memory_context and "No previous attempts found" not in memory_context:
                print("🧠 MEMORY: Found previous attempt context - using it for retry")
                print(f"🔍 MEMORY: Previous attempts will inform this retry attempt")
            else:
                print("🧠 MEMORY: No previous attempts found for this flow")
            
            # Use the unified RAG approach for all scenarios
            # The method automatically handles user story, RAG knowledge, memory context, and optional retry context
            flow_response = agent.generate_flow_with_rag(flow_build_request)
            
            # Enhanced debugging for the generated Flow XML
            if flow_response.success and flow_response.flow_xml:
                xml_length = len(flow_response.flow_xml)
                xml_snippet = flow_response.flow_xml[:200].replace('\n', ' ').replace('\r', ' ')
                
                print(f"📄 GENERATED FLOW XML:")
                print(f"   XML Length: {xml_length} characters")
                print(f"   XML Preview: {xml_snippet}...")
                
                if flow_build_request.retry_context:
                    retry_attempt = flow_build_request.retry_context.get('retry_attempt', 1)
                    print(f"   🔄 This is UPDATED XML for retry #{retry_attempt}")
                    print(f"   🛠️  Applied fixes to address deployment failure")
                    
                    # Show what elements were created/modified
                    if flow_response.elements_created:
                        print(f"   🧱 Elements created: {', '.join(flow_response.elements_created)}")
                    if flow_response.variables_created:
                        print(f"   📊 Variables created: {', '.join(flow_response.variables_created)}")
                else:
                    print(f"   🆕 This is INITIAL XML for first attempt")
                    
            # Save updated memory data back to state for persistence
            updated_memory_data = agent.get_memory_data_for_persistence()
            response_updates["flow_builder_memory_data"] = updated_memory_data
            print(f"🧠 MEMORY: Persisted memory data for {len(updated_memory_data)} flows")
            
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
                    print(f"   ➡️  This UPDATED XML will now go to deployment agent")
                else:
                    print(f"   📋 Successfully built flow meeting user story requirements")
                    print(f"   ➡️  This INITIAL XML will now go to deployment agent")
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