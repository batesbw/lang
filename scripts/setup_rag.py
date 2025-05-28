#!/usr/bin/env python3
"""
RAG Setup Script for Salesforce Flow Builder Agent

This script helps set up the RAG (Retrieval-Augmented Generation) system including:
1. Supabase database tables
2. Initial documentation seeding
3. Sample flow repository sync
4. Environment validation
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.rag_tools import rag_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY", 
        "OPENAI_API_KEY",
        "GITHUB_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these variables in your .env file or environment")
        return False
    
    logger.info("All required environment variables are set")
    return True

def print_supabase_setup_sql():
    """Print the SQL needed to set up Supabase tables"""
    sql = """
-- RAG Setup SQL for Supabase
-- Run this in your Supabase SQL Editor

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create knowledge base table for flow documentation
CREATE TABLE IF NOT EXISTS flow_knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536), -- text-embedding-3-small uses 1536 dimensions (compatible with ivfflat)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search using HNSW (better for higher dimensions)
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

-- Create indexes for sample flows search
CREATE INDEX IF NOT EXISTS sample_flows_tags_idx ON sample_flows USING GIN (tags);
CREATE INDEX IF NOT EXISTS sample_flows_use_case_idx ON sample_flows (use_case);
CREATE INDEX IF NOT EXISTS sample_flows_complexity_idx ON sample_flows (complexity_level);

-- Create RLS policies (optional, for security)
ALTER TABLE flow_knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE sample_flows ENABLE ROW LEVEL SECURITY;

-- Allow all operations for service role (adjust as needed)
CREATE POLICY "Allow all for service role" ON flow_knowledge_base
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow all for service role" ON sample_flows
    FOR ALL USING (auth.role() = 'service_role');
"""
    
    print("=" * 80)
    print("SUPABASE SETUP SQL")
    print("=" * 80)
    print("Copy and paste the following SQL into your Supabase SQL Editor:")
    print()
    print(sql)
    print("=" * 80)

def seed_initial_documentation():
    """Seed the knowledge base with initial Salesforce Flow documentation"""
    
    initial_docs = [
        {
            "title": "Salesforce Flow Best Practices",
            "content": """
            Best practices for building Salesforce Flows:
            
            1. **Planning and Design**
               - Always start with a clear understanding of the business requirement
               - Map out the flow logic before building
               - Consider error handling and edge cases
               - Plan for scalability and performance
            
            2. **Flow Structure**
               - Use descriptive names for flow elements
               - Group related elements logically
               - Minimize the number of DML operations
               - Use bulk processing for large data volumes
            
            3. **Performance Optimization**
               - Avoid unnecessary loops
               - Use Get Records efficiently with proper filters
               - Minimize SOQL queries in loops
               - Consider using Fast Field Updates when appropriate
            
            4. **Error Handling**
               - Always include fault paths for critical operations
               - Provide meaningful error messages
               - Log errors for debugging
               - Consider rollback scenarios
            
            5. **Testing and Deployment**
               - Test with various data scenarios
               - Test error conditions
               - Use proper deployment practices
               - Document the flow functionality
            """,
            "category": "best_practices",
            "tags": ["performance", "design", "testing", "deployment"]
        },
        {
            "title": "Common Flow Elements and Usage",
            "content": """
            Common Salesforce Flow elements and when to use them:
            
            **Data Elements:**
            - Get Records: Retrieve data from Salesforce objects
            - Create Records: Insert new records
            - Update Records: Modify existing records
            - Delete Records: Remove records
            
            **Logic Elements:**
            - Decision: Branch flow based on conditions
            - Loop: Iterate through collections
            - Assignment: Set variable values
            - Wait: Pause flow execution
            
            **Screen Elements:**
            - Screen: Display information and collect input
            - Screen Components: Input fields, display text, etc.
            
            **Integration Elements:**
            - Apex Action: Call custom Apex code
            - Flow Action: Call another flow
            - Platform Event: Publish or subscribe to events
            
            **Best Practices for Each:**
            - Use Get Records with proper filters to avoid governor limits
            - Batch DML operations when possible
            - Use Decision elements for complex branching logic
            - Implement proper error handling for all elements
            """,
            "category": "examples",
            "tags": ["elements", "data", "logic", "screens", "integration"]
        },
        {
            "title": "Flow Troubleshooting Guide",
            "content": """
            Common Salesforce Flow issues and solutions:
            
            **Performance Issues:**
            - Too many SOQL queries: Consolidate Get Records operations
            - Slow execution: Review loop efficiency and data volume
            - Governor limit errors: Implement bulk processing
            
            **Logic Errors:**
            - Incorrect branching: Review Decision element criteria
            - Missing data: Check Get Records filters and field access
            - Null pointer exceptions: Add null checks in formulas
            
            **User Interface Issues:**
            - Screen not displaying: Check field-level security
            - Validation errors: Review required fields and validation rules
            - Navigation problems: Verify screen flow connections
            
            **Deployment Issues:**
            - Flow not activating: Check for missing references
            - Version conflicts: Manage flow versions properly
            - Permission errors: Verify user access and profiles
            
            **Debugging Tips:**
            - Use Debug mode to trace execution
            - Add Screen elements to display variable values
            - Check system debug logs for detailed error information
            - Test with different user profiles and data scenarios
            """,
            "category": "troubleshooting",
            "tags": ["debugging", "performance", "errors", "deployment"]
        }
    ]
    
    logger.info("Seeding initial documentation...")
    
    for doc in initial_docs:
        success = rag_manager.add_documentation(
            content=doc["content"],
            metadata={
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc["tags"],
                "source": "initial_seed"
            }
        )
        
        if success:
            logger.info(f"✓ Added: {doc['title']}")
        else:
            logger.error(f"✗ Failed to add: {doc['title']}")

def setup_sample_repository():
    """Set up a sample GitHub repository for flows"""
    
    logger.info("Setting up sample flow repository...")
    
    # You can customize this to point to your own repository
    sample_repos = [
        {
            "owner": "flows",
            "repo": "batesbw",
            "description": "Salesforce sample application with flows"
        }
        # Add more repositories as needed
    ]
    
    for repo_info in sample_repos:
        logger.info(f"Attempting to sync flows from {repo_info['owner']}/{repo_info['repo']}")
        
        try:
            # This would sync flows if the repository contains .flow-meta.xml files
            result = rag_manager.get_sample_flows_from_github(
                repo_name=repo_info["repo"],
                owner=repo_info["owner"]
            )
            
            if result:
                logger.info(f"Found {len(result)} flows in {repo_info['repo']}")
                # Store the flows
                rag_manager.store_sample_flows(result)
            else:
                logger.info(f"No flows found in {repo_info['repo']}")
                
        except Exception as e:
            logger.warning(f"Could not access repository {repo_info['repo']}: {str(e)}")

def test_rag_functionality():
    """Test the RAG system functionality"""
    
    logger.info("Testing RAG functionality...")
    
    # Test knowledge base search
    logger.info("Testing knowledge base search...")
    results = rag_manager.search_knowledge_base("flow best practices")
    logger.info(f"Found {len(results)} documents for 'flow best practices'")
    
    # Test sample flow search
    logger.info("Testing sample flow search...")
    flows = rag_manager.search_sample_flows("approval process")
    logger.info(f"Found {len(flows)} sample flows for 'approval process'")
    
    logger.info("RAG functionality test completed")

def main():
    """Main setup function"""
    
    print("🚀 Salesforce Flow Builder Agent - RAG Setup")
    print("=" * 50)
    
    # Step 1: Validate environment
    print("\n1. Validating environment...")
    if not validate_environment():
        print("❌ Environment validation failed. Please fix the issues above.")
        return
    print("✅ Environment validation passed")
    
    # Step 2: Print Supabase setup instructions
    print("\n2. Supabase Database Setup")
    print_supabase_setup_sql()
    
    input("\nPress Enter after you've run the SQL in Supabase...")
    
    # Step 3: Test connections
    print("\n3. Testing connections...")
    if rag_manager.supabase_client:
        print("✅ Supabase connection successful")
    else:
        print("❌ Supabase connection failed")
        return
    
    if rag_manager.github_client:
        print("✅ GitHub connection successful")
    else:
        print("⚠️  GitHub connection failed (optional)")
    
    if rag_manager.embeddings:
        print("✅ OpenAI embeddings initialized")
    else:
        print("❌ OpenAI embeddings failed")
        return
    
    # Step 4: Seed initial documentation
    print("\n4. Seeding initial documentation...")
    seed_initial_documentation()
    print("✅ Initial documentation seeded")
    
    # Step 5: Setup sample repositories (optional)
    print("\n5. Setting up sample repositories...")
    setup_sample_repository()
    print("✅ Sample repository setup completed")
    
    # Step 6: Test functionality
    print("\n6. Testing RAG functionality...")
    test_rag_functionality()
    print("✅ RAG functionality test completed")
    
    print("\n🎉 RAG setup completed successfully!")
    print("\nYour RAG system is now ready to use. The FlowBuilderAgent can now:")
    print("- Search the knowledge base for best practices and examples")
    print("- Find similar sample flows from your repositories")
    print("- Learn from documented patterns and solutions")
    
    print("\nNext steps:")
    print("1. Add more documentation using the add_flow_documentation tool")
    print("2. Sync additional GitHub repositories with sample flows")
    print("3. Start using the enhanced FlowBuilderAgent with RAG capabilities")

if __name__ == "__main__":
    main() 