#!/usr/bin/env python3
import sys
sys.path.append('/home/ben/Repos/lang/src')

from src.tools.lightning_flow_scanner_rag import ingest_lightning_flow_scanner, get_proactive_flow_guidance

print('🚀 Starting Lightning Flow Scanner ingestion...')
result = ingest_lightning_flow_scanner.invoke({})

if result['success']:
    print(f'✅ Success: {result["message"]}')
    print(f'   Rules found: {result["rules_found"]}')
    print(f'   Docs found: {result["docs_found"]}')
    print(f'   Total added: {result["total_added"]}')
    
    # Test proactive guidance
    print('\n🧪 Testing proactive guidance...')
    guidance = get_proactive_flow_guidance.invoke({
        "flow_requirements": "approval process for expense reports",
        "flow_elements": ["Screen", "Decision", "Record Update", "Email Alert"]
    })
    
    if guidance["success"]:
        print(f'✅ Generated {guidance["total_recommendations"]} recommendations')
        categories = guidance["guidance"]
        for category, items in categories.items():
            if isinstance(items, list) and items:
                print(f'   - {category.replace("_", " ").title()}: {len(items)} items')
    else:
        print(f'❌ Guidance error: {guidance.get("message", "Unknown")}')
else:
    print(f'❌ Error: {result["message"]}')

print('\n🎉 Lightning Flow Scanner integration ready for proactive flow generation!') 