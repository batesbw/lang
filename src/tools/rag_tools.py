"""
RAG (Retrieval-Augmented Generation) Tools for Salesforce Flow Builder Agent

This module provides tools for:
1. Supabase vector store management for documentation
2. GitHub repository integration for sample flows
3. Document embedding and retrieval
4. Knowledge base search and management
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import xml.etree.ElementTree as ET

from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client
from github import Github
import requests

# Remove the problematic import for now since we don't actually use these classes
# from ..schemas.flow_builder_schemas import FlowMetadata, FlowElement

logger = logging.getLogger(__name__)

class RAGManager:
    """Manages RAG operations for the Salesforce Flow Builder Agent"""
    
    def __init__(self):
        self.supabase_client = None
        self.github_client = None
        self.embeddings = None
        self.vector_store = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase, GitHub, and OpenAI clients"""
        try:
            # Initialize Supabase client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
            
            if supabase_url and supabase_key:
                # Create Supabase client with minimal configuration to avoid proxy issues
                self.supabase_client = create_client(
                    supabase_url=supabase_url,
                    supabase_key=supabase_key
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not found in environment variables")
            
            # Initialize GitHub client
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                self.github_client = Github(github_token)
                logger.info("GitHub client initialized successfully")
            else:
                logger.warning("GitHub token not found in environment variables")
            
            # Initialize OpenAI embeddings
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",  # 1536 dimensions, compatible with ivfflat
                    openai_api_key=openai_api_key
                )
                logger.info("OpenAI embeddings initialized successfully")
            else:
                logger.warning("OpenAI API key not found in environment variables")
            
            # Initialize vector store if all components are available
            if self.supabase_client and self.embeddings:
                self.vector_store = SupabaseVectorStore(
                    embedding=self.embeddings,
                    client=self.supabase_client,
                    table_name="flow_knowledge_base",
                    query_name="match_flow_documents"
                )
                logger.info("Vector store initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing RAG clients: {str(e)}")
            # Don't re-raise the exception to prevent startup failures
            # The tools will handle missing clients gracefully
    
    def setup_supabase_tables(self) -> bool:
        """Setup required Supabase tables for RAG"""
        try:
            if not self.supabase_client:
                logger.error("Supabase client not initialized")
                return False
            
            # SQL to create the knowledge base table
            create_table_sql = """
            -- Enable the pgvector extension
            CREATE EXTENSION IF NOT EXISTS vector;
            
            -- Create knowledge base table for flow documentation
            CREATE TABLE IF NOT EXISTS flow_knowledge_base (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                metadata JSONB,
                embedding VECTOR(1536), -- text-embedding-3-small uses 1536 dimensions
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create index for vector similarity search using HNSW
            CREATE INDEX IF NOT EXISTS flow_knowledge_base_embedding_idx 
            ON flow_knowledge_base USING hnsw (embedding vector_cosine_ops);
            
            -- Create function for similarity search
            CREATE OR REPLACE FUNCTION match_flow_documents (
                query_embedding VECTOR(1536),
                filter JSONB DEFAULT '{}',
                match_threshold FLOAT DEFAULT 0.78,
                match_count INT DEFAULT 10
            ) RETURNS TABLE (
                id UUID,
                content TEXT,
                metadata JSONB,
                similarity FLOAT
            ) LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    flow_knowledge_base.id,
                    flow_knowledge_base.content,
                    flow_knowledge_base.metadata,
                    1 - (flow_knowledge_base.embedding <=> query_embedding) AS similarity
                FROM flow_knowledge_base
                WHERE flow_knowledge_base.metadata @> filter
                    AND 1 - (flow_knowledge_base.embedding <=> query_embedding) > match_threshold
                ORDER BY flow_knowledge_base.embedding <=> query_embedding
                LIMIT match_count;
            END;
            $$;
            
            -- Create sample flows table
            CREATE TABLE IF NOT EXISTS sample_flows (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                flow_name TEXT NOT NULL UNIQUE,
                flow_xml TEXT NOT NULL,
                description TEXT,
                use_case TEXT,
                complexity_level TEXT,
                tags TEXT[],
                github_url TEXT,
                embedding VECTOR(1536),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create index for sample flows search
            CREATE INDEX IF NOT EXISTS sample_flows_embedding_idx 
            ON sample_flows USING hnsw (embedding vector_cosine_ops);
            
            -- Create function for similarity search on sample flows
            CREATE OR REPLACE FUNCTION match_sample_flows (
                query_embedding VECTOR(1536),
                filter JSONB DEFAULT '{}',
                match_threshold FLOAT DEFAULT 0.7,
                match_count INT DEFAULT 5
            ) RETURNS TABLE (
                id UUID,
                flow_name TEXT,
                description TEXT,
                similarity FLOAT,
                flow_xml TEXT
            ) LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    sample_flows.id,
                    sample_flows.flow_name,
                    sample_flows.description,
                    1 - (sample_flows.embedding <=> query_embedding) AS similarity,
                    sample_flows.flow_xml
                FROM sample_flows
                WHERE 1 - (sample_flows.embedding <=> query_embedding) > match_threshold
                ORDER BY sample_flows.embedding <=> query_embedding
                LIMIT match_count;
            END;
            $$;

            -- Create index for sample flows tags
            CREATE INDEX IF NOT EXISTS sample_flows_tags_idx ON sample_flows USING GIN (tags);
            CREATE INDEX IF NOT EXISTS sample_flows_use_case_idx ON sample_flows (use_case);
            """
            
            # Execute the SQL (Note: This would need to be run manually in Supabase SQL editor)
            logger.info("Supabase table setup SQL generated. Please run this in your Supabase SQL editor:")
            logger.info(create_table_sql)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Supabase tables: {str(e)}")
            return False
    
    def add_sample_flow_from_xml(self, flow_name: str, xml_content: str) -> bool:
        """Adds a sample flow from XML content to the 'sample_flows' table."""
        if not self.supabase_client:
            logger.error("Supabase client not initialized. Cannot add sample flow.")
            return False
        
        try:
            # Extract metadata from the XML content
            description = self._extract_flow_description(xml_content)
            use_case = self._infer_use_case(flow_name, xml_content)
            complexity = self._assess_complexity(xml_content)
            tags = self._extract_tags(xml_content)
            
            flow_data = {
                "flow_name": flow_name,
                "flow_xml": xml_content,
                "description": description,
                "use_case": use_case,
                "complexity_level": complexity,
                "tags": tags,
                # Embed the full XML content for semantic search
                "embedding": self.embeddings.embed_query(xml_content)
            }
            
            self.supabase_client.table("sample_flows").upsert(flow_data, on_conflict='flow_name').execute()
            logger.info(f"Successfully upserted sample flow '{flow_name}' in the database.")
            return True
        except Exception as e:
            logger.error(f"Error upserting sample flow from XML for '{flow_name}': {e}")
            return False
    
    def add_documentation(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add documentation to the knowledge base"""
        try:
            if not self.vector_store:
                logger.error("Vector store not initialized")
                return False
            
            # Create document
            doc = Document(page_content=content, metadata=metadata)
            
            # Add to vector store
            self.vector_store.add_documents([doc])
            
            logger.info(f"Added documentation: {metadata.get('title', 'Untitled')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documentation: {str(e)}")
            return False
    
    def search_knowledge_base(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Document]:
        """Search the knowledge base for relevant documents"""
        try:
            if not self.vector_store:
                logger.error("Vector store not initialized")
                return []
            
            # Perform similarity search
            if filter_metadata:
                docs = self.vector_store.similarity_search(
                    query, 
                    k=k, 
                    filter=filter_metadata
                )
            else:
                docs = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(docs)} relevant documents for query: {query}")
            return docs
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_sample_flows_from_github(self, repo_name: str, owner: str = None) -> List[Dict[str, Any]]:
        """Retrieve sample flows from a GitHub repository"""
        try:
            if not self.github_client:
                logger.error("GitHub client not initialized")
                return []
            
            # Get repository
            if owner:
                repo = self.github_client.get_repo(f"{owner}/{repo_name}")
            else:
                repo = self.github_client.get_repo(repo_name)
            
            flows = []
            
            # Search for flow files (typically .flow-meta.xml files)
            contents = repo.get_contents("")
            
            def search_flows_recursive(contents):
                flow_files = []
                for content in contents:
                    if content.type == "dir":
                        # Recursively search subdirectories
                        subcontents = repo.get_contents(content.path)
                        flow_files.extend(search_flows_recursive(subcontents))
                    elif content.name.endswith('.flow-meta.xml'):
                        flow_files.append(content)
                return flow_files
            
            flow_files = search_flows_recursive(contents)
            
            for flow_file in flow_files:
                try:
                    # Get file content
                    file_content = flow_file.decoded_content.decode('utf-8')
                    
                    # Extract flow metadata
                    flow_data = {
                        'flow_name': flow_file.name.replace('.flow-meta.xml', ''),
                        'flow_xml': file_content,
                        'github_url': flow_file.html_url,
                        'path': flow_file.path,
                        'description': self._extract_flow_description(file_content),
                        'use_case': self._infer_use_case(flow_file.name, file_content),
                        'complexity_level': self._assess_complexity(file_content),
                        'tags': self._extract_tags(file_content)
                    }
                    
                    flows.append(flow_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing flow file {flow_file.name}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(flows)} sample flows from {repo_name}")
            return flows
            
        except Exception as e:
            logger.error(f"Error retrieving sample flows from GitHub: {str(e)}")
            return []
    
    def store_sample_flows(self, flows: List[Dict[str, Any]]) -> bool:
        """Store sample flows in Supabase"""
        try:
            if not self.supabase_client:
                logger.error("Supabase client not initialized")
                return False
            
            for flow in flows:
                # Insert into sample_flows table
                result = self.supabase_client.table("sample_flows").insert(flow).execute()
                
                if result.data:
                    logger.info(f"Stored sample flow: {flow['flow_name']}")
                else:
                    logger.warning(f"Failed to store sample flow: {flow['flow_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing sample flows: {str(e)}")
            return False
    
    def search_sample_flows(self, query: str, use_case: str = None, complexity: str = None) -> List[Dict[str, Any]]:
        """Search for sample flows based on a query and/or metadata filters."""
        if not self.supabase_client:
            logger.error("Supabase client not initialized")
            return []

        try:
            # If the query is empty, return all flows
            if not query:
                return self.supabase_client.table("sample_flows").select("*").execute().data

            query_embedding = self.embeddings.embed_query(query)
            
            rpc_params = {
                'query_embedding': query_embedding,
                'match_threshold': 0.7,
                'match_count': 5
            }
            
            results = self.supabase_client.rpc('match_sample_flows', rpc_params).execute().data
            
            # Additional filtering based on use_case or complexity if provided
            if use_case:
                results = [r for r in results if r.get('use_case') == use_case]
            if complexity:
                results = [r for r in results if r.get('complexity_level') == complexity]
                
            logger.info(f"Found {len(results)} matching sample flows for query: '{query}'")
            return results
        except Exception as e:
            logger.error(f"Error searching for sample flows: {e}")
            return []
    
    def _extract_flow_description(self, xml_content: str) -> str:
        """Extracts the description from the flow's XML content."""
        try:
            root = ET.fromstring(xml_content)
            # Namespace is required to find elements in Salesforce metadata XML
            namespace = {'sfdc': 'http://soap.sforce.com/2006/04/metadata'}
            description_element = root.find('sfdc:description', namespace)
            if description_element is not None and description_element.text:
                return description_element.text.strip()
        except ET.ParseError:
            logger.warning("Could not parse XML to extract description.")
        return "No description available."
    
    def _infer_use_case(self, filename: str, xml_content: str) -> str:
        """Infers the primary use case of a flow from its name and content."""
        content_lower = xml_content.lower()
        if "screen" in content_lower:
            return "User Interaction"
        if "recordcreate" in content_lower or "recorddelete" in content_lower or "recordupdate" in content_lower:
            return "Data Management"
        if "email" in content_lower:
            return "Notification"
        if "autolaunched" in filename.lower():
            return "Automated Process"
        return "General"
    
    def _assess_complexity(self, xml_content: str) -> str:
        """Assesses the complexity of a flow based on its element count."""
        try:
            root = ET.fromstring(xml_content)
            # A simple proxy for complexity is the number of elements
            num_elements = len(root.findall(".//*"))
            if num_elements > 50:
                return "Advanced"
            if num_elements > 20:
                return "Intermediate"
            return "Beginner"
        except ET.ParseError:
            logger.warning("Could not parse XML to assess complexity.")
            return "Unknown"
    
    def _extract_tags(self, xml_content: str) -> List[str]:
        """Extracts a list of relevant tags from the flow's XML content."""
        tags = set()
        try:
            root = ET.fromstring(xml_content)
            namespace = {'sfdc': 'http://soap.sforce.com/2006/04/metadata'}
            
            # Add process type as a tag
            process_type = root.find('sfdc:processType', namespace)
            if process_type is not None and process_type.text:
                tags.add(process_type.text.strip())

            # Add key element types as tags
            for element in root.findall(".//*"):
                # The tag name is the local name (without namespace)
                tag_name = element.tag.split('}')[-1]
                if tag_name in ['actionCalls', 'apexPluginCalls', 'assignments', 'decisions', 'loops', 'screens', 'recordCreates', 'recordUpdates', 'recordDeletes']:
                    tags.add(tag_name)
        except ET.ParseError:
            logger.warning("Could not parse XML to extract tags.")
        return list(tags)


# Initialize global RAG manager
rag_manager = RAGManager()

@tool
def search_flow_knowledge_base(query: str, category: str = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the flow knowledge base for relevant documentation and examples.
    
    Args:
        query: The search query describing what you're looking for
        category: Optional category filter (e.g., 'best_practices', 'examples', 'troubleshooting')
        max_results: Maximum number of results to return
    
    Returns:
        List of relevant documents with content and metadata
    """
    try:
        filter_metadata = {"category": category} if category else None
        
        docs = rag_manager.search_knowledge_base(
            query=query,
            k=max_results,
            filter_metadata=filter_metadata
        )
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance": "high"  # Could be enhanced with actual similarity scores
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in search_flow_knowledge_base: {str(e)}")
        return []

@tool
def find_similar_sample_flows(requirements: str, use_case: str = None, complexity: str = None) -> List[Dict[str, Any]]:
    """
    Finds sample Salesforce flows that are semantically similar to the given requirements.
    
    This tool is useful for finding complete, working examples of flows that can be used
    as a starting point or reference for building a new flow. It searches a curated

    Args:
        requirements: A natural language description of the flow's requirements.
        use_case: (Optional) Filter by a specific use case (e.g., 'Record Creation', 'User Interaction').
        complexity: (Optional) Filter by complexity level ('Beginner', 'Intermediate', 'Advanced').

    Returns:
        A list of dictionaries, where each dictionary represents a similar sample flow,
        including its name, description, and XML content.
    """
    return rag_manager.search_sample_flows(query=requirements, use_case=use_case, complexity=complexity)

@tool
def add_flow_documentation(title: str, content: str, category: str, tags: List[str] = None) -> bool:
    """
    Add new documentation to the flow knowledge base.
    
    Args:
        title: Title of the documentation
        content: The documentation content
        category: Category (e.g., 'best_practices', 'examples', 'troubleshooting')
        tags: Optional list of tags for categorization
    
    Returns:
        True if successful, False otherwise
    """
    try:
        metadata = {
            "title": title,
            "category": category,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "source": "manual_entry"
        }
        
        success = rag_manager.add_documentation(content, metadata)
        return success
        
    except Exception as e:
        logger.error(f"Error in add_flow_documentation: {str(e)}")
        return False

@tool
def sync_github_sample_flows(repo_name: str, owner: str = None) -> Dict[str, Any]:
    """
    Sync sample flows from a GitHub repository.
    
    Args:
        repo_name: Name of the GitHub repository
        owner: Optional repository owner (if different from authenticated user)
    
    Returns:
        Summary of the sync operation
    """
    try:
        # Get flows from GitHub
        flows = rag_manager.get_sample_flows_from_github(repo_name, owner)
        
        if not flows:
            return {
                "success": False,
                "message": "No flows found in repository",
                "flows_synced": 0
            }
        
        # Store flows in Supabase
        success = rag_manager.store_sample_flows(flows)
        
        return {
            "success": success,
            "message": f"Successfully synced {len(flows)} flows from {repo_name}",
            "flows_synced": len(flows),
            "flows": [{"name": f["flow_name"], "use_case": f["use_case"]} for f in flows]
        }
        
    except Exception as e:
        logger.error(f"Error in sync_github_sample_flows: {str(e)}")
        return {
            "success": False,
            "message": f"Error syncing flows: {str(e)}",
            "flows_synced": 0
        }

@tool
def populate_basic_flow_knowledge(populate_troubleshooting: bool = True, populate_best_practices: bool = True) -> Dict[str, Any]:
    """
    Populate the knowledge base with basic Flow troubleshooting and best practices content.
    This provides immediate value for error-specific RAG queries.
    
    Args:
        populate_troubleshooting: Whether to add troubleshooting content
        populate_best_practices: Whether to add best practices content
    
    Returns:
        Dictionary with population results
    """
    try:
        results = {
            "troubleshooting_added": 0,
            "best_practices_added": 0,
            "errors": []
        }
        
        if populate_troubleshooting:
            troubleshooting_docs = [
                {
                    "content": """Duplicate Elements Error Fix:
When Flow deployment fails with 'duplicate element' errors, check for elements with the same name within the same type (e.g., two recordLookups elements named 'Get_Records').
Fix: Remove duplicate elements and consolidate logic into a single element. Each element type must have unique names within the Flow.
Common patterns: recordLookups, recordCreates, recordUpdates, assignments, decisions.""",
                    "metadata": {
                        "category": "troubleshooting",
                        "error_type": "duplicate_elements",
                        "source": "Flow_Builder_Agent",
                        "priority": "high"
                    }
                },
                {
                    "content": """Collection Variable Usage Rules:
Collection variables CANNOT be used directly in inputAssignments for Record operations.
Correct pattern: Use Assignment elements to add items to collections, then reference the collection variable directly as input for Create/Update Records.
Error pattern: Trying to use collection variables in individual field assignments will cause deployment failures.""",
                    "metadata": {
                        "category": "troubleshooting",
                        "error_type": "collection_variable",
                        "source": "Flow_Builder_Agent",
                        "priority": "high"
                    }
                },
                {
                    "content": """Element Reference Validation:
All element references must point to actual elements that exist in the flow. Element names are case-sensitive.
Fix: Ensure referenced elements exist and names match exactly. Use proper syntax: elementName.fieldName
Common issue: Referencing elements that were renamed or removed during flow modifications.""",
                    "metadata": {
                        "category": "troubleshooting",
                        "error_type": "element_reference",
                        "source": "Flow_Builder_Agent",
                        "priority": "medium"
                    }
                },
                {
                    "content": """API Name Validation Rules:
Flow API names must be alphanumeric and start with a letter. No spaces, hyphens, or special characters.
Fix: Replace invalid characters with underscores. Example: 'My-Flow Name' becomes 'My_Flow_Name'
Apply this rule to all element names, variable names, and the Flow API name itself.""",
                    "metadata": {
                        "category": "troubleshooting",
                        "error_type": "api_name_validation",
                        "source": "Flow_Builder_Agent",
                        "priority": "medium"
                    }
                },
                {
                    "content": """XML Structure Requirements:
Flow XML must include proper namespace: xmlns="http://soap.sforce.com/2006/04/metadata"
Required elements: apiVersion, label, processType, status
Status must be 'Active' for deployment, not 'Draft'
Include processMetadataValues for Flow Builder compatibility.""",
                    "metadata": {
                        "category": "troubleshooting",
                        "error_type": "xml_structure",
                        "source": "Flow_Builder_Agent",
                        "priority": "high"
                    }
                }
            ]
            
            for doc_data in troubleshooting_docs:
                success = rag_manager.add_documentation(
                    content=doc_data["content"],
                    metadata=doc_data["metadata"]
                )
                if success:
                    results["troubleshooting_added"] += 1
                else:
                    results["errors"].append(f"Failed to add troubleshooting doc: {doc_data['metadata']['error_type']}")
        
        if populate_best_practices:
            best_practices_docs = [
                {
                    "content": """Flow XML Best Practices:
1. Always set status to 'Active' for immediate deployment
2. Use descriptive, alphanumeric API names without spaces/hyphens
3. Include all required processMetadataValues for Flow Builder support
4. Validate all element references point to existing elements
5. Consolidate duplicate logic instead of creating duplicate elements""",
                    "metadata": {
                        "category": "best_practices",
                        "topic": "xml_generation",
                        "source": "Flow_Builder_Agent",
                        "priority": "high"
                    }
                },
                {
                    "content": """Collection Variable Best Practices:
1. Use Assignment elements to populate collections
2. Reference collections directly in recordCreates/recordUpdates
3. Never use collections in individual inputAssignments
4. Use Get Records with outputReference for collection variables
5. Access collection size using proper syntax""",
                    "metadata": {
                        "category": "best_practices",
                        "topic": "collection_variables",
                        "source": "Flow_Builder_Agent",
                        "priority": "high"
                    }
                },
                {
                    "content": """Error Prevention Strategies:
1. Validate API names before creating elements
2. Check for duplicate element names within types
3. Verify all element references exist
4. Include proper XML namespace and declarations
5. Test Flow XML structure before deployment""",
                    "metadata": {
                        "category": "best_practices",
                        "topic": "error_prevention",
                        "source": "Flow_Builder_Agent",
                        "priority": "medium"
                    }
                }
            ]
            
            for doc_data in best_practices_docs:
                success = rag_manager.add_documentation(
                    content=doc_data["content"],
                    metadata=doc_data["metadata"]
                )
                if success:
                    results["best_practices_added"] += 1
                else:
                    results["errors"].append(f"Failed to add best practices doc: {doc_data['metadata']['topic']}")
        
        logger.info(f"Populated knowledge base: {results['troubleshooting_added']} troubleshooting docs, "
                   f"{results['best_practices_added']} best practices docs")
        
        return results
        
    except Exception as e:
        logger.error(f"Error populating basic flow knowledge: {str(e)}")
        return {
            "troubleshooting_added": 0,
            "best_practices_added": 0,
            "errors": [str(e)]
        }

@tool
def populate_flow_metadata_api_knowledge(populate_core_elements: bool = True, populate_validation_rules: bool = True) -> Dict[str, Any]:
    """
    Populate the knowledge base with core Flow Metadata API knowledge for better initial Flow generation.
    This provides foundational understanding of Flow XML structure, elements, and validation rules.
    
    Args:
        populate_core_elements: Whether to add core Flow elements documentation
        populate_validation_rules: Whether to add Flow validation rules
    
    Returns:
        Dictionary with population results
    """
    try:
        results = {
            "core_elements_added": 0,
            "validation_rules_added": 0,
            "errors": []
        }
        
        if populate_core_elements:
            core_elements_docs = [
                {
                    "content": """
Flow XML Core Structure:
- <?xml version="1.0" encoding="UTF-8"?>
- <Flow xmlns="http://soap.sforce.com/2006/04/metadata">
- Required elements: apiVersion, label, processType, status
- Element types: screens, decisions, assignments, recordLookups, recordCreates, recordUpdates
- Variables: dataType, isCollection, isInput, isOutput, name, value
- Connectors: targetReference links elements together
- Start element: has no connector input, begins flow execution
                    """,
                    "metadata": {
                        "category": "core_structure",
                        "source": "Flow_Metadata_API",
                        "topic": "xml_structure",
                        "priority": "high"
                    }
                },
                {
                    "content": """
Flow Element Naming Requirements:
- API names must be alphanumeric, start with letter
- No spaces, hyphens, or special characters allowed  
- Use camelCase or underscore_case consistently
- Element references are case-sensitive
- Must be unique within each element type
- Examples: Get_Records, CreateRecord, UpdateOpportunity
                    """,
                    "metadata": {
                        "category": "naming_conventions",
                        "source": "Flow_Metadata_API",
                        "topic": "api_names",
                        "priority": "high"
                    }
                },
                {
                    "content": """
Flow Variable Types and Usage:
- Record variables: Single SObject records (dataType="SObject")
- Collection variables: Multiple records (isCollection="true")
- Primitive types: Text, Number, Boolean, Date, DateTime
- Variable references: Use {!VariableName} in formulas
- Input/Output variables: isInput="true" or isOutput="true"
- Assignment vs direct reference patterns
                    """,
                    "metadata": {
                        "category": "variables",
                        "source": "Flow_Metadata_API", 
                        "topic": "data_types",
                        "priority": "high"
                    }
                },
                {
                    "content": """
Flow Connector Rules:
- Each element (except Start) needs incoming connector
- Decision elements have outcome-based connectors
- Loops have done/next connectors
- Use targetReference to link elements
- No circular references allowed
- End flow with explicit termination or screen
                    """,
                    "metadata": {
                        "category": "connectors",
                        "source": "Flow_Metadata_API",
                        "topic": "flow_logic",
                        "priority": "medium"
                    }
                }
            ]
            
            for doc in core_elements_docs:
                if rag_manager.add_documentation(doc["content"], doc["metadata"]):
                    results["core_elements_added"] += 1
        
        if populate_validation_rules:
            validation_rules_docs = [
                {
                    "content": """
Common Flow XML Validation Errors:
- Duplicate elements: Each element must have unique name within type
- Invalid references: All targetReference values must point to existing elements
- XSD type mismatches: Variables references vs literal values in wrong contexts
- Collection variable restrictions: Cannot use in inputAssignments fields
- Required element children: Each element type has mandatory child elements
                    """,
                    "metadata": {
                        "category": "validation_rules",
                        "source": "Flow_Metadata_API",
                        "topic": "error_prevention",
                        "priority": "high"
                    }
                },
                {
                    "content": """
Flow Status and Lifecycle:
- status: Active (deployed), Draft (not deployed), Obsolete
- API Version: Use latest supported version (59.0)
- processType: Flow, Workflow, AutoLaunchedFlow
- processMetadataValues: Required for Flow Builder compatibility
- activeVersionNumber: Controls which version is active
                    """,
                    "metadata": {
                        "category": "lifecycle",
                        "source": "Flow_Metadata_API",
                        "topic": "deployment",
                        "priority": "medium"
                    }
                },
                {
                    "content": """
Get Records Element Best Practices:
- Use getFirstRecordOnly for single records
- outputReference should point to collection variable for multiple records
- Reference element directly (not elementName.Count) for record counting
- Apply SOQL query limits and filters appropriately
- Handle no records found scenarios
                    """,
                    "metadata": {
                        "category": "get_records",
                        "source": "Flow_Metadata_API",
                        "topic": "data_operations",
                        "priority": "high"
                    }
                }
            ]
            
            for doc in validation_rules_docs:
                if rag_manager.add_documentation(doc["content"], doc["metadata"]):
                    results["validation_rules_added"] += 1
        
        logger.info(f"Added {results['core_elements_added']} core elements docs and {results['validation_rules_added']} validation rules docs")
        return results
        
    except Exception as e:
        error_msg = f"Error populating Flow Metadata API knowledge: {str(e)}"
        logger.error(error_msg)
        return {"core_elements_added": 0, "validation_rules_added": 0, "errors": [error_msg]}

@tool
def enhance_initial_flow_knowledge(flow_type: str = "all", use_case: str = None) -> Dict[str, Any]:
    """
    Retrieve enhanced knowledge specifically for initial Flow building attempts.
    This complements the existing RAG system with targeted foundational knowledge.
    
    Args:
        flow_type: Type of flow being built (Screen, Record-Triggered, etc.)
        use_case: Specific use case (approval, automation, etc.)
    
    Returns:
        Dictionary with enhanced knowledge for initial Flow building
    """
    try:
        enhanced_knowledge = {
            "foundational_concepts": [],
            "metadata_api_guidelines": [],
            "common_patterns": [],
            "preventive_best_practices": []
        }
        
        # Search for foundational Flow concepts
        foundational_docs = rag_manager.search_knowledge_base(
            query="Flow XML core structure elements variables connectors",
            k=3,
            filter_metadata={"category": "core_structure"}
        )
        enhanced_knowledge["foundational_concepts"] = [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in foundational_docs
        ]
        
        # Get Metadata API specific guidelines
        api_docs = rag_manager.search_knowledge_base(
            query="Flow Metadata API validation naming conventions",
            k=3,
            filter_metadata={"source": "Flow_Metadata_API"}
        )
        enhanced_knowledge["metadata_api_guidelines"] = [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in api_docs
        ]
        
        # Get preventive best practices
        preventive_docs = rag_manager.search_knowledge_base(
            query="Flow validation error prevention best practices",
            k=2,
            filter_metadata={"topic": "error_prevention"}
        )
        enhanced_knowledge["preventive_best_practices"] = [
            {"content": doc.page_content, "metadata": doc.metadata} for doc in preventive_docs
        ]
        
        # Use case specific patterns if provided
        if use_case:
            pattern_docs = rag_manager.search_knowledge_base(
                query=f"{use_case} flow patterns examples",
                k=2
            )
            enhanced_knowledge["common_patterns"] = [
                {"content": doc.page_content, "metadata": doc.metadata} for doc in pattern_docs
            ]
        
        total_docs = (len(enhanced_knowledge["foundational_concepts"]) + 
                     len(enhanced_knowledge["metadata_api_guidelines"]) + 
                     len(enhanced_knowledge["common_patterns"]) + 
                     len(enhanced_knowledge["preventive_best_practices"]))
        
        logger.info(f"Enhanced initial Flow knowledge retrieved: {total_docs} total documents")
        return enhanced_knowledge
        
    except Exception as e:
        error_msg = f"Error retrieving enhanced initial Flow knowledge: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

# Export tools for use in agents
RAG_TOOLS = [
    search_flow_knowledge_base,
    find_similar_sample_flows,
    add_flow_documentation,
    sync_github_sample_flows,
    populate_basic_flow_knowledge,
    populate_flow_metadata_api_knowledge,
    enhance_initial_flow_knowledge
] 