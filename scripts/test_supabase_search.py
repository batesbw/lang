#!/usr/bin/env python3
"""
Test Supabase vector search and provide fallback search functionality
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.rag_tools import rag_manager

def test_supabase_search():
    """Test Supabase search functionality"""
    
    print("Testing Supabase search functionality...")
    
    client = rag_manager.supabase_client
    if not client:
        print("❌ Supabase client not initialized")
        return
    
    # Get all documents
    try:
        result = client.table('flow_knowledge_base').select('*').execute()
        docs = result.data
        print(f"📊 Found {len(docs)} documents in database")
        
        # Show sample documents
        for i, doc in enumerate(docs[:3]):
            print(f"\nDocument {i+1}:")
            print(f"  Title: {doc['metadata'].get('title', 'No title')}")
            print(f"  Category: {doc['metadata'].get('category', 'No category')}")
            print(f"  Content preview: {doc['content'][:100]}...")
            print(f"  Has embedding: {'Yes' if doc.get('embedding') else 'No'}")
        
        # Test text-based search as fallback
        print("\n🔍 Testing text-based search:")
        search_terms = ["flow", "metadata", "XML", "screen", "decision"]
        
        for term in search_terms:
            matching_docs = []
            for doc in docs:
                content_lower = doc['content'].lower()
                title_lower = doc['metadata'].get('title', '').lower()
                
                if term.lower() in content_lower or term.lower() in title_lower:
                    matching_docs.append(doc)
            
            print(f"  '{term}': {len(matching_docs)} matches")
            for match in matching_docs[:2]:
                print(f"    - {match['metadata'].get('title', 'No title')}")
        
        # Test vector search function directly
        print("\n🧮 Testing vector search function:")
        try:
            # Get embeddings for a test query
            embeddings = rag_manager.embeddings
            if embeddings:
                test_query = "flow metadata structure"
                query_embedding = embeddings.embed_query(test_query)
                print(f"Generated embedding for '{test_query}': {len(query_embedding)} dimensions")
                
                # Try the match_flow_documents function
                try:
                    # Call the Supabase function directly
                    rpc_result = client.rpc('match_flow_documents', {
                        'query_embedding': query_embedding,
                        'match_threshold': 0.5,  # Lower threshold
                        'match_count': 5
                    }).execute()
                    
                    print(f"RPC function returned: {len(rpc_result.data) if rpc_result.data else 0} results")
                    for result in (rpc_result.data or [])[:3]:
                        print(f"  - Similarity: {result.get('similarity', 'N/A'):.3f}")
                        print(f"    Title: {result.get('metadata', {}).get('title', 'No title')}")
                        
                except Exception as e:
                    print(f"❌ RPC function error: {e}")
                    
            else:
                print("❌ Embeddings not initialized")
                
        except Exception as e:
            print(f"❌ Vector search test error: {e}")
            
    except Exception as e:
        print(f"❌ Database query error: {e}")

def create_fallback_search_function():
    """Create a fallback search function that works with text matching"""
    
    print("\n🔧 Creating fallback search function...")
    
    # Create a simple text-based search function
    fallback_code = '''
def fallback_search_flow_knowledge_base(query: str, max_results: int = 5):
    """Fallback text-based search for flow knowledge base"""
    from src.tools.rag_tools import rag_manager
    
    try:
        client = rag_manager.supabase_client
        if not client:
            return []
        
        # Get all documents
        result = client.table('flow_knowledge_base').select('*').execute()
        docs = result.data or []
        
        # Simple text matching
        query_lower = query.lower()
        query_words = query_lower.split()
        
        scored_docs = []
        for doc in docs:
            score = 0
            content_lower = doc['content'].lower()
            title_lower = doc['metadata'].get('title', '').lower()
            
            # Score based on exact query match
            if query_lower in content_lower:
                score += 10
            if query_lower in title_lower:
                score += 15
            
            # Score based on individual words
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    if word in content_lower:
                        score += 2
                    if word in title_lower:
                        score += 3
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs[:max_results]:
            results.append({
                "content": doc['content'],
                "metadata": doc['metadata'],
                "relevance": "high" if score > 10 else "medium",
                "score": score
            })
        
        return results
        
    except Exception as e:
        print(f"Fallback search error: {e}")
        return []
'''
    
    # Write to a file
    with open('fallback_search.py', 'w') as f:
        f.write(fallback_code)
    
    print("✅ Fallback search function created in fallback_search.py")

if __name__ == "__main__":
    test_supabase_search()
    create_fallback_search_function() 