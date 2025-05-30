#!/usr/bin/env python3
"""
Quick test of Lightning Flow Scanner integration
"""

import asyncio
from src.tools.lightning_flow_scanner_rag import ingest_lightning_flow_scanner, search_flow_scanner_rules, get_proactive_flow_guidance

async def test_lightning_flow_scanner():
    print("🚀 Testing Lightning Flow Scanner Integration")
    print("=" * 50)
    
    # Test the ingestion
    print("1. Testing repository ingestion...")
    result = ingest_lightning_flow_scanner()
    
    if result["success"]:
        print(f"✅ Success: {result['message']}")
        print(f"   Rules found: {result['rules_found']}")
        print(f"   Docs found: {result['docs_found']}")
        print(f"   Total added: {result['total_added']}")
        
        # Test rule search
        print("\n2. Testing rule search...")
        rules = search_flow_scanner_rules("naming convention", max_results=3)
        print(f"   Found {len(rules)} naming convention rules")
        
        # Test proactive guidance
        print("\n3. Testing proactive guidance...")
        guidance = get_proactive_flow_guidance(
            "approval process for expenses",
            ["Screen", "Decision", "Record Update"]
        )
        
        if guidance["success"]:
            print(f"   Generated {guidance['total_recommendations']} recommendations")
        else:
            print(f"   Error: {guidance.get('message', 'Unknown error')}")
    else:
        print(f"❌ Error: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_lightning_flow_scanner()) 