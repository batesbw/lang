#!/usr/bin/env python3
"""
Debug script to test RAG functionality
"""
import os
import sys

# Add src to path for imports
sys.path.append("src")

from src.tools.rag_tools import rag_manager

def test_direct_supabase_query():
    """Test direct Supabase query to see if data exists"""
    try:
        if not rag_manager.supabase_client:
            print("❌ No Supabase client")
            return
            
        # Direct query to check row count
        result = rag_manager.supabase_client.table("flow_knowledge_base").select("id", count="exact").execute()
        print(f"✅ Total rows in flow_knowledge_base: {result.count}")
        
        # Check if embeddings exist
        embedding_check = rag_manager.supabase_client.table("flow_knowledge_base").select("id, embedding").limit(5).execute()
        
        embeddings_with_data = 0
        embeddings_null = 0
        
        for row in embedding_check.data:
            if row['embedding'] is not None:
                embeddings_with_data += 1
            else:
                embeddings_null += 1
        
        print(f"✅ Embeddings status: {embeddings_with_data} with data, {embeddings_null} null")
        
        # Get a few sample rows
        sample_result = rag_manager.supabase_client.table("flow_knowledge_base").select("content, metadata").limit(3).execute()
        print(f"✅ Sample data found: {len(sample_result.data)} rows")
        
        for i, row in enumerate(sample_result.data):
            print(f"  Row {i+1}: {row['metadata'].get('title', 'No title')} - {row['content'][:100]}...")
            
    except Exception as e:
        print(f"❌ Direct query failed: {str(e)}")

def test_vector_search_with_low_threshold():
    """Test vector search with lower similarity threshold"""
    try:
        print("\n=== Testing Vector Search with Low Threshold ===")
        
        if not rag_manager.supabase_client:
            print("❌ No Supabase client")
            return
            
        # Generate embedding for a test query
        test_query = "flow best practices"
        embedding = rag_manager.embeddings.embed_query(test_query)
        
        # Test with very low threshold
        low_threshold_result = rag_manager.supabase_client.rpc(
            "match_flow_documents",
            {
                "query_embedding": embedding,
                "match_threshold": 0.1,  # Very low threshold
                "match_count": 5
            }
        ).execute()
        
        print(f"✅ Low threshold (0.1) results: {len(low_threshold_result.data)}")
        
        if low_threshold_result.data:
            for i, doc in enumerate(low_threshold_result.data[:3]):
                print(f"  Result {i+1}: similarity={doc['similarity']:.3f} - {doc['content'][:100]}...")
        
        # Test with default threshold
        default_threshold_result = rag_manager.supabase_client.rpc(
            "match_flow_documents",
            {
                "query_embedding": embedding,
                "match_threshold": 0.78,  # Default threshold
                "match_count": 5
            }
        ).execute()
        
        print(f"✅ Default threshold (0.78) results: {len(default_threshold_result.data)}")
        
    except Exception as e:
        print(f"❌ Low threshold test failed: {str(e)}")

def test_vector_search():
    """Test vector search process"""
    try:
        print("\n=== Testing Vector Search ===")
        
        # Test different queries
        test_queries = [
            "flow best practices",
            "salesforce flow",
            "performance",
            "decision elements",
            "sales_process troubleshooting"  # This is from the logs
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            
            # Test with different parameters
            try:
                # Test with no filter
                results = rag_manager.search_knowledge_base(query, k=3)
                print(f"  No filter: {len(results)} results")
                
                # Test with filter
                results_filtered = rag_manager.search_knowledge_base(query, k=3, filter_metadata={"category": "best_practices"})
                print(f"  With filter: {len(results_filtered)} results")
                
                if results:
                    print(f"  First result preview: {results[0].page_content[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ Search failed: {str(e)}")

    except Exception as e:
        print(f"❌ Vector search test failed: {str(e)}")

def test_embedding_generation():
    """Test if embeddings are being generated properly"""
    try:
        print("\n=== Testing Embedding Generation ===")
        
        if not rag_manager.embeddings:
            print("❌ No embeddings client")
            return
            
        # Test embedding generation
        test_text = "test query for flow best practices"
        embedding = rag_manager.embeddings.embed_query(test_text)
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        
        # Check if this matches expected dimensions (1536 for text-embedding-3-small)
        if len(embedding) == 1536:
            print("✅ Embedding dimensions match expected (1536)")
        else:
            print(f"⚠️  Embedding dimensions ({len(embedding)}) don't match expected (1536)")
            
    except Exception as e:
        print(f"❌ Embedding generation failed: {str(e)}")

def main():
    print("🔍 RAG Debug Script")
    print("=" * 50)
    
    print("\n1. Testing direct Supabase connection...")
    test_direct_supabase_query()
    
    print("\n2. Testing embedding generation...")
    test_embedding_generation()
    
    print("\n3. Testing vector search with low threshold...")
    test_vector_search_with_low_threshold()
    
    print("\n4. Testing vector search...")
    test_vector_search()
    
    print("\n" + "=" * 50)
    print("Debug completed!")

if __name__ == "__main__":
    main() 