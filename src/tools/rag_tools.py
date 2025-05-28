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

from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client
from github import Github
import requests

from ..schemas.flow_schemas import FlowMetadata, FlowElement

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
                self.supabase_client = create_client(supabase_url, supabase_key)
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
                    model="text-embedding-3-large",
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
                embedding VECTOR(3072), -- text-embedding-3-large uses 3072 dimensions
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create index for vector similarity search
            CREATE INDEX IF NOT EXISTS flow_knowledge_base_embedding_idx 
            ON flow_knowledge_base USING ivfflat (embedding vector_cosine_ops);
            
            -- Create function for similarity search
            CREATE OR REPLACE FUNCTION match_flow_documents (
                query_embedding VECTOR(3072),
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
                flow_name TEXT NOT NULL,
                flow_xml TEXT NOT NULL,
                description TEXT,
                use_case TEXT,
                complexity_level TEXT,
                tags TEXT[],
                github_url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create index for sample flows search
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
        """Search for relevant sample flows"""
        try:
            if not self.supabase_client:
                logger.error("Supabase client not initialized")
                return []
            
            # Build query
            query_builder = self.supabase_client.table("sample_flows").select("*")
            
            # Add filters
            if use_case:
                query_builder = query_builder.eq("use_case", use_case)
            
            if complexity:
                query_builder = query_builder.eq("complexity_level", complexity)
            
            # Execute query
            result = query_builder.execute()
            
            flows = result.data if result.data else []
            
            # If we have a text query, filter by relevance
            if query and flows:
                # Simple text matching for now - could be enhanced with vector search
                filtered_flows = []
                query_lower = query.lower()
                
                for flow in flows:
                    score = 0
                    if query_lower in flow.get('flow_name', '').lower():
                        score += 3
                    if query_lower in flow.get('description', '').lower():
                        score += 2
                    if any(query_lower in tag.lower() for tag in flow.get('tags', [])):
                        score += 1
                    
                    if score > 0:
                        flow['relevance_score'] = score
                        filtered_flows.append(flow)
                
                # Sort by relevance
                flows = sorted(filtered_flows, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Found {len(flows)} relevant sample flows")
            return flows
            
        except Exception as e:
            logger.error(f"Error searching sample flows: {str(e)}")
            return []
    
    def _extract_flow_description(self, xml_content: str) -> str:
        """Extract description from flow XML"""
        try:
            # Simple regex to find description - could be enhanced with proper XML parsing
            import re
            description_match = re.search(r'<description>(.*?)</description>', xml_content, re.DOTALL)
            if description_match:
                return description_match.group(1).strip()
            return "No description available"
        except:
            return "No description available"
    
    def _infer_use_case(self, filename: str, xml_content: str) -> str:
        """Infer use case from filename and content"""
        filename_lower = filename.lower()
        content_lower = xml_content.lower()
        
        # Common use case patterns
        if any(keyword in filename_lower or keyword in content_lower for keyword in ['approval', 'approve']):
            return "approval_process"
        elif any(keyword in filename_lower or keyword in content_lower for keyword in ['email', 'notification']):
            return "email_automation"
        elif any(keyword in filename_lower or keyword in content_lower for keyword in ['lead', 'conversion']):
            return "lead_management"
        elif any(keyword in filename_lower or keyword in content_lower for keyword in ['case', 'support']):
            return "case_management"
        elif any(keyword in filename_lower or keyword in content_lower for keyword in ['opportunity', 'sales']):
            return "sales_process"
        else:
            return "general"
    
    def _assess_complexity(self, xml_content: str) -> str:
        """Assess flow complexity based on content"""
        try:
            # Count elements to determine complexity
            element_count = xml_content.count('<')
            
            if element_count < 50:
                return "simple"
            elif element_count < 150:
                return "medium"
            else:
                return "complex"
        except:
            return "unknown"
    
    def _extract_tags(self, xml_content: str) -> List[str]:
        """Extract relevant tags from flow content"""
        tags = []
        content_lower = xml_content.lower()
        
        # Common flow element types
        if 'recordcreate' in content_lower:
            tags.append('record_creation')
        if 'recordupdate' in content_lower:
            tags.append('record_update')
        if 'recorddelete' in content_lower:
            tags.append('record_deletion')
        if 'emailsimple' in content_lower or 'emailalert' in content_lower:
            tags.append('email')
        if 'decision' in content_lower:
            tags.append('conditional_logic')
        if 'loop' in content_lower:
            tags.append('loops')
        if 'subflow' in content_lower:
            tags.append('subflows')
        if 'screen' in content_lower:
            tags.append('user_interaction')
        
        return tags


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
    Find sample flows that match the given requirements.
    
    Args:
        requirements: Description of what the flow should accomplish
        use_case: Optional use case filter (e.g., 'approval_process', 'email_automation')
        complexity: Optional complexity filter ('simple', 'medium', 'complex')
    
    Returns:
        List of relevant sample flows with metadata
    """
    try:
        flows = rag_manager.search_sample_flows(
            query=requirements,
            use_case=use_case,
            complexity=complexity
        )
        
        # Format results for the agent
        results = []
        for flow in flows[:5]:  # Limit to top 5 results
            results.append({
                "flow_name": flow.get("flow_name"),
                "description": flow.get("description"),
                "use_case": flow.get("use_case"),
                "complexity_level": flow.get("complexity_level"),
                "tags": flow.get("tags", []),
                "github_url": flow.get("github_url"),
                "xml_content": flow.get("flow_xml")[:1000] + "..." if len(flow.get("flow_xml", "")) > 1000 else flow.get("flow_xml"),  # Truncate for readability
                "relevance_score": flow.get("relevance_score", 0)
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in find_similar_sample_flows: {str(e)}")
        return []

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

# Export tools for use in agents
RAG_TOOLS = [
    search_flow_knowledge_base,
    find_similar_sample_flows,
    add_flow_documentation,
    sync_github_sample_flows
] 