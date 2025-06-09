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

from ..tools.rag_tools import RAG_TOOLS, search_flow_knowledge_base, find_similar_sample_flows, enhance_initial_flow_knowledge
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
        logger.info(f"Generated {len(analysis['search_queries'])} search queries from requirements.")
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
        """Generates a targeted prompt for the LLM to fix a failed flow deployment."""
        
        prompt_parts = [
            "## Mission: Debug and Fix a Failed Salesforce Flow Deployment",
            "You are a Salesforce expert troubleshooter. A previous attempt to deploy a Flow failed. Your task is to analyze the error, examine the faulty XML, and produce a corrected version.",
            
            "\n" + "="*30,
            "## FAILURE ANALYSIS",
            f"**Flow Name:** `{request.flow_api_name}`",
            
            "\n### Deployment Error Message:",
            "```",
            failure_analysis.get('error_details', 'No error details provided.'),
            "```",

            "\n### Faulty Flow XML (This is the file that needs to be fixed):",
            "```xml",
            failure_analysis.get('failed_flow_xml', '<error>No XML provided</error>'),
            "```",
            "="*30 + "\n",
        ]

        # --- RAG: Knowledge to Help Fix the Error ---
        if failure_knowledge.get('documentation_results'):
            prompt_parts.append("## Relevant Documentation (Use this to find the correct syntax and fix the error):")
            for i, doc in enumerate(failure_knowledge['documentation_results'][:2], 1): # Top 2 docs for fixing
                source = doc.metadata.get('source', 'Unknown')
                content_preview = doc.page_content[:500].strip()
                prompt_parts.append(f"📄 Doc {i} (from {source}):\n---\n{content_preview}\n---\n")

        if failure_knowledge.get('sample_flow_results'):
            prompt_parts.append("## Similar Correct Flow Examples (Use these as a reference for the correct structure):")
            for i, flow in enumerate(failure_knowledge['sample_flow_results'][:1], 1): # Top 1 example for fixing
                prompt_parts.append(f"🔧 Example: {flow.get('flow_name')}")
                prompt_parts.append(f"   Description: {flow.get('description')}")
                prompt_parts.append(f"   XML Snippet:\n```xml\n{flow.get('flow_xml', '')[:600].strip()}\n```\n")

        # --- Final Instructions ---
        prompt_parts.extend([
            "\n## Your Task:",
            "1.  **Analyze the Error:** Carefully read the 'Deployment Error Message'.",
            "2.  **Inspect the XML:** Examine the 'Faulty Flow XML' to locate the source of the error.",
            "3.  **Consult the Knowledge:** Use the 'Relevant Documentation' and 'Similar Correct Flow Examples' to understand the correct implementation.",
            "4.  **Correct the XML:** Rewrite the provided 'Faulty FlowXML' to fix the specific error. Do not change other parts of the flow unless necessary to resolve the error.",
            "5.  **Generate Only the Corrected XML:** Your output must be the complete, valid, and corrected XML for the `.flow-meta.xml` file, inside a single `<?xml ...>` block.",
            "6.  **Do not** add any explanations or comments outside of the XML block."
        ])
        
        return "\n".join(prompt_parts)

    def retrieve_knowledge(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieves knowledge from RAG tools based on the analysis of the requirements."""
        
        knowledge = {
            "best_practices": [],
            "sample_flows": [],
            "patterns": [],
            "troubleshooting": [],
            "documentation_results": [],
            "foundational_knowledge": [],  # New: Core Flow Metadata API knowledge
            "preventive_guidance": []      # New: Error prevention guidance
        }
        
        try:
            # Enhanced: Get foundational Flow Metadata API knowledge for initial attempts
            from ..tools.rag_tools import enhance_initial_flow_knowledge
            foundational_knowledge = enhance_initial_flow_knowledge.invoke({
                "flow_type": analysis.get("primary_use_case", "all"),
                "use_case": analysis.get("primary_use_case")
            })
            
            if foundational_knowledge and not foundational_knowledge.get("error"):
                # Extract foundational concepts for better XML structure understanding
                if foundational_knowledge.get("foundational_concepts"):
                    knowledge["foundational_knowledge"].extend(foundational_knowledge["foundational_concepts"])
                
                # Extract Metadata API guidelines for proper Flow XML generation
                if foundational_knowledge.get("metadata_api_guidelines"):
                    knowledge["foundational_knowledge"].extend(foundational_knowledge["metadata_api_guidelines"])
                
                # Extract preventive best practices to avoid common errors
                if foundational_knowledge.get("preventive_best_practices"):
                    knowledge["preventive_guidance"].extend(foundational_knowledge["preventive_best_practices"])
                
                # Extract common patterns for the use case
                if foundational_knowledge.get("common_patterns"):
                    knowledge["patterns"].extend(foundational_knowledge["common_patterns"])
                
                logger.info(f"Retrieved enhanced foundational knowledge: "
                           f"{len(knowledge['foundational_knowledge'])} foundational docs, "
                           f"{len(knowledge['preventive_guidance'])} preventive guidance docs")
            
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
            
            # Store all documentation results for prompt building
            all_docs = (knowledge["best_practices"] + knowledge["patterns"] + 
                       knowledge["troubleshooting"] + knowledge["foundational_knowledge"] + 
                       knowledge["preventive_guidance"])
            knowledge["documentation_results"] = all_docs
            
            logger.info(f"Retrieved comprehensive knowledge: {len(knowledge['best_practices'])} best practices, "
                       f"{len(knowledge['sample_flows'])} sample flows, "
                       f"{len(knowledge['patterns'])} patterns, "
                       f"{len(knowledge['troubleshooting'])} troubleshooting guides, "
                       f"{len(knowledge['foundational_knowledge'])} foundational docs, "
                       f"{len(knowledge['preventive_guidance'])} preventive guides")
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
            # Return empty knowledge on error to allow flow generation to continue
            knowledge = {
                "best_practices": [],
                "sample_flows": [],
                "patterns": [],
                "troubleshooting": [],
                "documentation_results": [],
                "foundational_knowledge": [],
                "preventive_guidance": []
            }
        
        return knowledge

    def generate_error_specific_rag_queries(self, deployment_errors: List[Dict[str, Any]]) -> List[str]:
        """Generate targeted RAG queries based on specific deployment errors"""
        queries = []
        
        if not deployment_errors:
            return queries
            
        for error in deployment_errors:
            error_msg = error.get('problem', '').lower()
            component_type = error.get('componentType', '').lower()
            
            # Duplicate element errors
            if 'duplicate' in error_msg or 'duplicated' in error_msg:
                queries.append("Salesforce Flow XML duplicate elements prevention")
                queries.append("Flow XML validation duplicate element fixes")
            
            # Collection variable errors
            elif 'collection' in error_msg and 'variable' in error_msg:
                queries.append("Flow collection variable usage best practices")
                queries.append("Salesforce Flow collection variable inputAssignments rules")
            
            # Element reference errors
            elif 'reference' in error_msg or 'not found' in error_msg:
                queries.append("Flow element reference validation requirements")
                queries.append("Salesforce Flow element naming conventions")
            
            # API name validation errors
            elif 'api name' in error_msg or 'invalid name' in error_msg:
                queries.append("Salesforce Flow API name validation rules")
                queries.append("Flow element naming best practices")
            
            # XML structure/syntax errors
            elif 'xml' in error_msg or 'metadata' in error_msg or 'malformed' in error_msg:
                queries.append("Salesforce Flow XML structure requirements")
                queries.append("Flow metadata XML validation rules")
            
            # Flow-specific component errors
            elif component_type == 'flow':
                if 'status' in error_msg:
                    queries.append("Salesforce Flow status and activation requirements")
                elif 'process' in error_msg:
                    queries.append("Flow processType and processMetadataValues configuration")
                else:
                    queries.append(f"Salesforce Flow {error_msg[:50]} troubleshooting")
            
            # General error fallback
            else:
                # Extract key error terms for search
                error_terms = [term for term in error_msg.split() if len(term) > 3][:3]
                if error_terms:
                    query = f"Salesforce Flow {' '.join(error_terms)} error fix"
                    queries.append(query)
        
        # Remove duplicates while preserving order
        unique_queries = []
        for query in queries:
            if query not in unique_queries:
                unique_queries.append(query)
        
        logger.info(f"Generated {len(unique_queries)} error-specific RAG queries from {len(deployment_errors)} deployment errors")
        return unique_queries[:5]  # Limit to top 5 most relevant queries

    def retrieve_error_specific_knowledge(self, deployment_errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced error-specific RAG knowledge retrieval for deployment failures"""
        
        # Generate enhanced queries from deployment errors
        error_queries = self.generate_error_specific_rag_queries(deployment_errors)
        
        if not error_queries:
            logger.warning("No error-specific queries generated from deployment errors")
            return {}
        
        # Search for error-specific documentation with enhanced queries
        all_error_docs = []
        
        for query in error_queries[:3]:  # Limit to top 3 most specific queries
            logger.info(f"🔍 Error-specific RAG query: '{query}'")
            try:
                error_docs = search_flow_knowledge_base(query, k=2)  # Get 2 docs per query
                if error_docs:
                    logger.info(f"📚 Found {len(error_docs)} error-specific documents for query")
                    all_error_docs.extend(error_docs)
                else:
                    logger.info("📭 No documents found for this error query")
            except Exception as e:
                logger.error(f"❌ Error searching knowledge base for error query '{query}': {e}")
        
        # Remove duplicates and limit results
        unique_docs = []
        seen_content = set()
        for doc in all_error_docs:
            content_key = doc.page_content[:100] if hasattr(doc, 'page_content') else str(doc)[:100]
            if content_key not in seen_content:
                unique_docs.append(doc)
                seen_content.add(content_key)
                if len(unique_docs) >= 4:  # Max 4 error-specific docs
                    break
        
        logger.info(f"🎯 Final error-specific RAG results: {len(unique_docs)} unique documents")
        
        return {
            'documentation_results': unique_docs,
            'error_queries_used': error_queries[:3],
            'total_errors_analyzed': len(deployment_errors)
        }

    def _load_flow_documentation(self) -> str:
        """Load the complete Flow.md documentation file as foundational context"""
        try:
            flow_doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'documentation', 'Flow.md')
            
            if not os.path.exists(flow_doc_path):
                logger.warning(f"Flow documentation not found at: {flow_doc_path}")
                return ""
            
            with open(flow_doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"📖 Loaded Flow documentation: {len(content)} characters from Flow.md")
            return content
            
        except Exception as e:
            logger.error(f"Failed to load Flow documentation: {e}")
            return ""

    def generate_enhanced_prompt(self, request: FlowBuildRequest, knowledge: Dict[str, Any], error_specific_knowledge: Dict[str, Any] = None) -> str:
        """Builds a comprehensive prompt for the LLM, incorporating RAG, memory, error-specific knowledge, and complete Flow documentation."""
        
        memory_context = self._get_memory_context(request.flow_api_name)
        
        # Load complete Flow documentation
        flow_documentation = self._load_flow_documentation()
        
        # Start building the prompt
        prompt_parts = [
            "## Mission: Create a Salesforce Flow from a User Story",
            "Your task is to act as an expert Salesforce developer and write the complete XML for a new Salesforce Flow based on the user's requirements.",
            "You must generate a single, valid `.flow-meta.xml` file.",
            
            "\n## User Story & Requirements:",
            f"'{request.requirements}'",
            
            f"\n## Flow API Name:\n`{request.flow_api_name}`",
        ]
        
        # --- Complete Flow Documentation (Foundational Reference) ---
        if flow_documentation:
            prompt_parts.extend([
                "\n" + "="*50,
                "## 📚 COMPLETE SALESFORCE FLOW METADATA DOCUMENTATION",
                "This is the complete Salesforce Flow Metadata API documentation. Use this as your primary reference for:",
                "- Flow XML structure and syntax",
                "- All available flow elements and their properties", 
                "- Field types, enumerations, and valid values",
                "- API versioning and compatibility requirements",
                "- Deployment rules and restrictions",
                "",
                "📖 REFERENCE DOCUMENTATION:",
                "---",
                flow_documentation,
                "---",
                "="*50 + "\n",
            ])
        
        # --- Memory Context ---
        prompt_parts.extend([
            "\n" + "="*30,
            "## MEMORY & LEARNING FROM PAST ATTEMPTS",
            memory_context,
            "="*30 + "\n",
        ])

        # --- Foundational Flow Knowledge (for initial attempts) ---
        if knowledge.get('foundational_knowledge'):
            prompt_parts.append("## 🏗️ FOUNDATIONAL FLOW METADATA API KNOWLEDGE:")
            prompt_parts.append("Use this core knowledge to build proper Flow XML structure and avoid common validation errors.")
            
            foundational_docs = knowledge['foundational_knowledge'][:4]  # Top 4 foundational docs
            for i, doc in enumerate(foundational_docs, 1):
                if isinstance(doc, dict):
                    content_preview = doc.get('content', '')[:350].strip()
                    metadata = doc.get('metadata', {})
                    category = metadata.get('category', 'foundational').replace('_', ' ').title()
                    prompt_parts.append(f"📚 Foundation {i} ({category}):\n---\n{content_preview}\n---\n")
                elif hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                    content_preview = doc.page_content[:350].strip()
                    category = doc.metadata.get('category', 'foundational').replace('_', ' ').title()
                    prompt_parts.append(f"📚 Foundation {i} ({category}):\n---\n{content_preview}\n---\n")

        # --- Preventive Guidance (for initial attempts) ---
        if knowledge.get('preventive_guidance'):
            prompt_parts.append("## 🛡️ ERROR PREVENTION GUIDANCE:")
            prompt_parts.append("Apply this guidance proactively to prevent common Flow deployment failures.")
            
            preventive_docs = knowledge['preventive_guidance'][:3]  # Top 3 preventive docs
            for i, doc in enumerate(preventive_docs, 1):
                if isinstance(doc, dict):
                    content_preview = doc.get('content', '')[:300].strip()
                    prompt_parts.append(f"🚫 Prevention {i}:\n---\n{content_preview}\n---\n")
                elif hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                    content_preview = doc.page_content[:300].strip()
                    prompt_parts.append(f"🚫 Prevention {i}:\n---\n{content_preview}\n---\n")

        # --- Error-Specific RAG Knowledge (for retry attempts) ---
        if error_specific_knowledge and error_specific_knowledge.get('documentation_results'):
            prompt_parts.append("## 🚨 ERROR-SPECIFIC SOLUTIONS (from knowledge base):")
            
            error_docs = error_specific_knowledge['documentation_results'][:3]  # Top 3 error solutions
            for i, doc in enumerate(error_docs, 1):
                if hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                    source = doc.metadata.get('source', 'Knowledge Base')
                    category = doc.metadata.get('category', 'error_solution')
                    content_preview = doc.page_content[:300].strip()
                    prompt_parts.append(f"🔧 Error Solution {i} ({category} from {source}):\n---\n{content_preview}\n---\n")
                elif isinstance(doc, dict):
                    content_preview = doc.get('content', '')[:300].strip()
                    metadata = doc.get('metadata', {})
                    category = metadata.get('category', 'error_solution')
                    prompt_parts.append(f"🔧 Error Solution {i} ({category}):\n---\n{content_preview}\n---\n")

        # --- RAG: Documentation Context ---
        if knowledge.get('documentation_results'):
            prompt_parts.append("## Relevant Documentation (Use this for correct syntax and best practices):")
            for i, doc in enumerate(knowledge['documentation_results'][:3], 1): # Top 3 docs
                if hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                    source = doc.metadata.get('source', 'Unknown')
                    content_preview = doc.page_content[:400].strip()
                    prompt_parts.append(f"📄 Doc {i} (from {source}):\n---\n{content_preview}\n---\n")
                elif isinstance(doc, dict):
                    content_preview = doc.get('content', '')[:400].strip()
                    prompt_parts.append(f"📄 Doc {i}:\n---\n{content_preview}\n---\n")

        # --- RAG: Best Practices ---
        if knowledge.get('best_practices'):
            prompt_parts.append("## Best Practices (from knowledge base):")
            for i, practice in enumerate(knowledge['best_practices'][:2], 1):  # Top 2 practices
                if hasattr(practice, 'page_content'):
                    content = practice.page_content.strip()
                elif isinstance(practice, dict):
                    content = practice.get('content', '').strip()
                else:
                    content = str(practice).strip()
                prompt_parts.append(f"✅ Practice {i}: {content}\n")

        # --- RAG: Sample Flows (if any) ---
        if knowledge.get('sample_flows'):
            prompt_parts.append(f"## Similar Sample Flows ({len(knowledge['sample_flows'])} found):")
            for i, sample in enumerate(knowledge['sample_flows'][:2], 1):  # Top 2 samples
                flow_name = sample.get('flow_name', f'Sample {i}')
                description = sample.get('description', 'No description available')
                prompt_parts.append(f"🔄 Sample {i}: {flow_name}\n   Description: {description}\n")

        # --- Retry Context (if this is a retry attempt) ---
        if request.retry_context:
            retry_attempt = request.retry_context.get('retry_attempt', 1)
            deployment_errors = request.retry_context.get('deployment_errors', [])
            validation_errors = request.retry_context.get('validation_errors', [])
            
            prompt_parts.extend([
                f"\n## 🔄 RETRY ATTEMPT #{retry_attempt} - CRITICAL FIXES REQUIRED",
                "The previous Flow XML failed deployment. You MUST fix these specific errors:",
            ])
            
            # Show deployment errors
            if deployment_errors:
                prompt_parts.append("### DEPLOYMENT ERRORS TO FIX:")
                for i, error in enumerate(deployment_errors[:3], 1):  # Top 3 deployment errors
                    component = error.get('fullName', 'Unknown')
                    problem = error.get('problem', 'Unknown error')
                    prompt_parts.append(f"❌ Error {i} ({component}): {problem}")
            
            # Show validation errors
            if validation_errors:
                prompt_parts.append("### VALIDATION ERRORS TO FIX:")
                for i, error in enumerate(validation_errors[:3], 1):  # Top 3 validation errors
                    if isinstance(error, dict):
                        error_msg = error.get('error_message', str(error))
                    else:
                        error_msg = str(error)
                    prompt_parts.append(f"⚠️  Validation {i}: {error_msg}")
            
            prompt_parts.append("\n🎯 MANDATORY: Address ALL the above errors in your XML generation.\n")

        # --- Final Instructions ---
        prompt_parts.extend([
            "\n## Final Instructions:",
            "1. Generate complete, production-ready Salesforce Flow XML",
            "2. Include all required elements and proper structure", 
            "3. Set status to 'Active' for immediate deployment",
            "4. Ensure all API names are valid (alphanumeric, no spaces/hyphens)",
            "5. If this is a retry, fix ALL the specific errors mentioned above",
            "6. Use the documentation and best practices provided above",
            "7. Apply error-specific solutions if provided",
            "8. Return ONLY the XML - no explanations or markdown",
            "",
            "START YOUR RESPONSE WITH: <?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_flow_with_rag(self, request: FlowBuildRequest) -> FlowBuildResponse:
        """Generate a flow using unified RAG-enhanced approach for both initial and retry attempts"""
        
        try:
            # Step 1: Analyze requirements
            analysis = self.analyze_requirements(request)
            retry_attempt = request.retry_context.get('retry_attempt', 1) if request.retry_context else 1
            
            # Step 2: Retrieve knowledge (enhanced for retry attempts)
            knowledge = self.retrieve_knowledge(analysis)
            
            # Step 3: If this is a retry attempt, get error-specific RAG knowledge
            error_specific_knowledge = {}
            if request.retry_context:
                # Extract deployment errors from retry context
                deployment_errors = request.retry_context.get('deployment_errors', [])
                if deployment_errors:
                    print(f"🔍 Retrieving error-specific RAG knowledge for {len(deployment_errors)} deployment errors")
                    error_specific_knowledge = self.retrieve_error_specific_knowledge(deployment_errors)
                    
                    # Log what we found
                    if error_specific_knowledge.get('documentation_results'):
                        print(f"📚 Found {len(error_specific_knowledge['documentation_results'])} error-specific documentation entries")
                    else:
                        print("⚠️  No error-specific documentation found in knowledge base")
            
            # Step 4: Generate enhanced prompt with both regular and error-specific knowledge
            enhanced_prompt = self.generate_enhanced_prompt(request, knowledge, error_specific_knowledge)
            
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

RAG-ENHANCED ERROR RESOLUTION:
- When error-specific documentation is provided, prioritize those solutions
- Apply the specific fixes and patterns recommended in the knowledge base
- Use the validation rules and best practices from the documentation
- Follow the troubleshooting patterns for similar error scenarios"""

            messages = [
                SystemMessage(content=xml_system_prompt),
                HumanMessage(content=enhanced_prompt)
            ]
            
            # Invoke LLM with sufficient token limit for complete Flow XML
            llm_response = self.llm.invoke(messages)
            
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
                    
                    # Add error-specific RAG insights
                    if error_specific_knowledge.get('documentation_results'):
                        error_doc_count = len(error_specific_knowledge['documentation_results'])
                        enhanced_recommendations.append(f"Applied {error_doc_count} error-specific solutions from knowledge base")
                        enhanced_best_practices.append("RAG-enhanced error resolution from documentation")
                
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
                        "complexity": analysis['complexity_level'],
                        "error_specific_rag_applied": bool(error_specific_knowledge.get('documentation_results'))
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