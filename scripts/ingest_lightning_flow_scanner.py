#!/usr/bin/env python3
"""
Lightning Flow Scanner Ingestion Script

This script ingests the Lightning Flow Scanner repository to provide proactive 
best practices context during flow generation.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.lightning_flow_scanner_rag import ingest_lightning_flow_scanner, get_proactive_flow_guidance, search_flow_scanner_rules
from src.tools.rag_tools import rag_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to ingest Lightning Flow Scanner repository"""
    
    print("🚀 Lightning Flow Scanner Repository Ingestion")
    print("=" * 60)
    
    # Check if RAG system is properly initialized
    if not rag_manager.vector_store:
        print("❌ RAG system not properly initialized. Please check your environment variables:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY") 
        print("   - OPENAI_API_KEY")
        print("   - GITHUB_TOKEN")
        return
    
    print("✅ RAG system initialized successfully")
    
    # Check if GitHub client is available
    if not rag_manager.github_client:
        print("❌ GitHub client not initialized. Please check GITHUB_TOKEN environment variable.")
        return
    
    print("✅ GitHub client initialized successfully")
    
    # Ingest the Lightning Flow Scanner repository
    print("\n📥 Ingesting Lightning Flow Scanner repository...")
    print("   Repository: https://github.com/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx")
    
    result = ingest_lightning_flow_scanner()
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"   📋 Rules found: {result['rules_found']}")
        print(f"   📄 Documentation files found: {result['docs_found']}")
        print(f"   💾 Total items added to RAG database: {result['total_added']}")
        
        # Test the newly ingested knowledge
        print("\n🧪 Testing the ingested knowledge...")
        
        # Test searching for specific rules
        print("\n1. Testing rule search:")
        test_queries = [
            "flow naming convention",
            "fault path error handling",
            "unused variable",
            "performance optimization",
            "security best practices"
        ]
        
        for query in test_queries:
            rules = search_flow_scanner_rules(query, max_results=2)
            print(f"   '{query}': {len(rules)} rules found")
            for rule in rules[:1]:  # Show first result
                rule_name = rule.get('rule_name', 'Unknown')
                severity = rule.get('severity', 'unknown')
                print(f"     - {rule_name} ({severity})")
        
        # Test proactive guidance
        print("\n2. Testing proactive flow guidance:")
        guidance_result = get_proactive_flow_guidance(
            flow_requirements="approval process for expense reports over $1000",
            flow_elements=["Screen", "Decision", "Record Update", "Email Alert"]
        )
        
        if guidance_result["success"]:
            guidance = guidance_result["guidance"]
            total_recs = guidance_result["total_recommendations"]
            print(f"   ✅ Generated {total_recs} recommendations across {len(guidance)} categories")
            
            for category, items in guidance.items():
                if isinstance(items, list) and items:
                    print(f"     - {category.replace('_', ' ').title()}: {len(items)} recommendations")
                elif not isinstance(items, list):
                    # Handle element-specific guidance structure
                    count = sum(len(item.get("guidance", [])) for item in items)
                    print(f"     - {category.replace('_', ' ').title()}: {count} recommendations")
        else:
            print(f"   ❌ Error testing proactive guidance: {guidance_result.get('message', 'Unknown error')}")
        
        print("\n🎉 Lightning Flow Scanner ingestion completed successfully!")
        print("\nYour FlowBuilderAgent can now:")
        print("✨ Apply Lightning Flow Scanner best practices proactively during flow generation")
        print("🔍 Search for specific validation rules and requirements")
        print("📋 Provide comprehensive guidance based on industry best practices")
        print("🚀 Generate higher quality flows on the first attempt")
        
        print("\n💡 Next steps:")
        print("1. The EnhancedFlowBuilderAgent will now automatically use this context")
        print("2. Test flow generation with a sample request")
        print("3. Compare validation results before/after this enhancement")
        
    else:
        print(f"❌ Failed to ingest repository: {result['message']}")
        print("\nTroubleshooting tips:")
        print("- Ensure your GitHub token has access to public repositories")
        print("- Check your internet connection")
        print("- Verify the Lightning Flow Scanner repository is accessible")

if __name__ == "__main__":
    main() 