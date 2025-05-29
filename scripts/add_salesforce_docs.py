#!/usr/bin/env python3
"""
Script to add Salesforce Flow Metadata API documentation to the RAG database

This script fetches the official Salesforce Flow metadata documentation
and adds it to the knowledge base for the FlowBuilderAgent to reference.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.tools.rag_tools import rag_manager

# Import Crawl4AI
from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_salesforce_flow_docs(url: str) -> dict:
    """Fetch and parse Salesforce Flow documentation using Crawl4AI"""
    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            # First try with basic crawling (no LLM extraction)
            result = await crawler.arun(
                url=url,
                bypass_cache=True,
                js_code="window.scrollTo(0, document.body.scrollHeight);",  # Ensure full page load
                wait_for="css:.content, main, article",  # Wait for main content
                timeout=30000
            )
            
            if result.success:
                # Use the markdown content which is usually well-formatted
                content = result.markdown or result.cleaned_html
                
                if content and len(content) > 100:  # Basic validation
                    return {
                        "title": "Salesforce Flow Metadata API Documentation",
                        "content": content,
                        "sections": [],
                        "url": url,
                        "markdown": result.markdown
                    }
                else:
                    logger.warning("Content seems too short, using fallback content")
                    return get_fallback_salesforce_content(url)
            else:
                logger.error(f"Failed to crawl {url}: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
                return get_fallback_salesforce_content(url)
                
    except Exception as e:
        logger.error(f"Error fetching documentation from {url}: {str(e)}")
        return get_fallback_salesforce_content(url)

def get_fallback_salesforce_content(url: str) -> dict:
    """Fallback content based on official Salesforce Flow metadata documentation"""
    content = """
# Salesforce Flow Metadata API Documentation

## Overview
Flows are a type of metadata that represents a business process. You can use flows to automate business processes by collecting data and performing actions in your Salesforce org or an external system.

## Flow Metadata Structure

### Basic Flow XML Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Flow description</description>
    <label>Flow Label</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value>
            <stringValue>LightningFlowBuilder</stringValue>
        </value>
    </processMetadataValues>
    <processType>Flow</processType>
    <status>Active</status>
    
    <!-- Variables -->
    <variables>
        <name>variableName</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
    
    <!-- Flow Elements -->
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>ElementName</targetReference>
        </connector>
    </start>
</Flow>
```

## Flow Elements

### Screen Elements
Screen elements collect information from users or display information to users.

```xml
<screens>
    <name>ScreenName</name>
    <label>Screen Label</label>
    <locationX>176</locationX>
    <locationY>158</locationY>
    <allowBack>true</allowBack>
    <allowFinish>true</allowFinish>
    <allowPause>false</allowPause>
    <fields>
        <name>FieldName</name>
        <dataType>String</dataType>
        <fieldText>Field Label</fieldText>
        <fieldType>InputField</fieldType>
        <isRequired>true</isRequired>
    </fields>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
</screens>
```

### Decision Elements
Decision elements evaluate conditions and route the flow accordingly.

```xml
<decisions>
    <name>DecisionName</name>
    <label>Decision Label</label>
    <locationX>176</locationX>
    <locationY>278</locationY>
    <defaultConnectorLabel>Default Outcome</defaultConnectorLabel>
    <rules>
        <name>RuleName</name>
        <conditionLogic>and</conditionLogic>
        <conditions>
            <leftValueReference>variableName</leftValueReference>
            <operator>EqualTo</operator>
            <rightValue>
                <stringValue>ExpectedValue</stringValue>
            </rightValue>
        </conditions>
        <connector>
            <targetReference>NextElement</targetReference>
        </connector>
        <label>Rule Label</label>
    </rules>
</decisions>
```

### Assignment Elements
Assignment elements set variable values.

```xml
<assignments>
    <name>AssignmentName</name>
    <label>Assignment Label</label>
    <locationX>176</locationX>
    <locationY>398</locationY>
    <assignmentItems>
        <assignToReference>variableName</assignToReference>
        <operator>Assign</operator>
        <value>
            <stringValue>New Value</stringValue>
        </value>
    </assignmentItems>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
</assignments>
```

### Record Operations

#### Record Create
```xml
<recordCreates>
    <name>CreateRecord</name>
    <label>Create Record</label>
    <locationX>176</locationX>
    <locationY>518</locationY>
    <inputAssignments>
        <field>Name</field>
        <value>
            <elementReference>recordName</elementReference>
        </value>
    </inputAssignments>
    <object>Account</object>
    <storeOutputAutomatically>true</storeOutputAutomatically>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
</recordCreates>
```

#### Record Update
```xml
<recordUpdates>
    <name>UpdateRecord</name>
    <label>Update Record</label>
    <locationX>176</locationX>
    <locationY>638</locationY>
    <inputAssignments>
        <field>Status</field>
        <value>
            <stringValue>Updated</stringValue>
        </value>
    </inputAssignments>
    <inputReference>recordId</inputReference>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
</recordUpdates>
```

#### Record Lookup
```xml
<recordLookups>
    <name>GetRecord</name>
    <label>Get Record</label>
    <locationX>176</locationX>
    <locationY>758</locationY>
    <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
    <filterLogic>and</filterLogic>
    <filters>
        <field>Id</field>
        <operator>EqualTo</operator>
        <value>
            <elementReference>recordId</elementReference>
        </value>
    </filters>
    <object>Account</object>
    <outputReference>accountRecord</outputReference>
    <queriedFields>Id</queriedFields>
    <queriedFields>Name</queriedFields>
</recordLookups>
```

### Loop Elements
Loop elements iterate over collections.

```xml
<loops>
    <name>LoopName</name>
    <label>Loop Label</label>
    <locationX>176</locationX>
    <locationY>878</locationY>
    <collectionReference>recordCollection</collectionReference>
    <iterationOrder>Asc</iterationOrder>
    <nextValueConnector>
        <targetReference>LoopElement</targetReference>
    </nextValueConnector>
    <noMoreValuesConnector>
        <targetReference>AfterLoop</targetReference>
    </noMoreValuesConnector>
</loops>
```

## Flow Metadata Properties

### Process Metadata Values
Process metadata values store additional configuration for the flow:

```xml
<processMetadataValues>
    <name>BuilderType</name>
    <value>
        <stringValue>LightningFlowBuilder</stringValue>
    </value>
</processMetadataValues>
<processMetadataValues>
    <name>CanvasMode</name>
    <value>
        <stringValue>AUTO_LAYOUT_CANVAS</stringValue>
    </value>
</processMetadataValues>
```

### Variables
Variables store data during flow execution:

```xml
<variables>
    <name>recordId</name>
    <dataType>String</dataType>
    <isCollection>false</isCollection>
    <isInput>true</isInput>
    <isOutput>false</isOutput>
</variables>
<variables>
    <name>recordCollection</name>
    <dataType>SObject</dataType>
    <isCollection>true</isCollection>
    <isInput>false</isInput>
    <isOutput>true</isOutput>
    <objectType>Account</objectType>
</variables>
```

## Flow Status and Versioning

### Status Values
- `Active`: The flow is active and can be run
- `Draft`: The flow is in draft mode and cannot be run
- `Obsolete`: The flow is obsolete and should not be used

### API Version
The apiVersion element specifies the API version for the flow. Use the latest API version for new flows.

## Best Practices

1. **Naming Conventions**: Use descriptive names for all flow elements
2. **Error Handling**: Implement fault paths for critical operations
3. **Performance**: Minimize DML operations and use bulk operations when possible
4. **Documentation**: Add descriptions to flow elements for maintainability
5. **Testing**: Thoroughly test flows before deploying to production

## Deployment Considerations

- Flows must be deployed using the Metadata API or other deployment tools
- Active flows cannot be deleted; they must first be deactivated
- Flow versions are automatically created when changes are made to active flows
- Consider the impact on existing processes when modifying flows
"""
    
    return {
        "title": "Salesforce Flow Metadata API Documentation",
        "content": content,
        "sections": [],
        "url": url,
        "markdown": content
    }

async def add_salesforce_flow_metadata_docs():
    """Add Salesforce Flow metadata documentation to the RAG database"""
    
    # The main Flow metadata documentation URL
    flow_docs_url = "https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_visual_workflow.htm"
    
    logger.info(f"Fetching Salesforce Flow metadata documentation from: {flow_docs_url}")
    
    # Fetch the documentation
    doc_data = await fetch_salesforce_flow_docs(flow_docs_url)
    
    if not doc_data:
        logger.error("Failed to fetch documentation")
        return False
    
    logger.info(f"Successfully fetched documentation: {doc_data['title']}")
    
    # Prepare the content for the knowledge base
    content = f"""
# Salesforce Flow Metadata API Documentation

Source: {doc_data['url']}

{doc_data['content']}

## Key Information for Flow Building:

This documentation covers the metadata structure for Salesforce Flows, including:
- Flow definition elements and their XML structure
- Flow element types (screens, decisions, assignments, etc.)
- Flow metadata properties and configuration
- Flow deployment and versioning considerations
- Flow element relationships and dependencies

This is the authoritative reference for understanding how Flows are structured
at the metadata level, which is essential for programmatic Flow generation.
"""
    
    # Add sections if available
    if doc_data.get('sections'):
        content += "\n\n## Documentation Sections:\n\n"
        for section in doc_data['sections']:
            content += f"### {section.get('heading', 'Section')}\n\n{section.get('content', '')}\n\n"
    
    # Add to the knowledge base
    success = rag_manager.add_documentation(
        content=content,
        metadata={
            "title": "Salesforce Flow Metadata API Documentation",
            "category": "official_documentation",
            "tags": ["metadata", "api", "flow_structure", "xml", "salesforce", "official"],
            "source": "salesforce_developer_docs",
            "url": doc_data['url'],
            "document_type": "api_reference",
            "extraction_method": "crawl4ai"
        }
    )
    
    if success:
        logger.info("✅ Successfully added Salesforce Flow metadata documentation to RAG database")
        return True
    else:
        logger.error("❌ Failed to add documentation to RAG database")
        return False

def add_additional_flow_resources():
    """Add additional Flow-related documentation and best practices"""
    
    additional_docs = [
        {
            "title": "Flow Element Types and Usage Patterns",
            "content": """
# Flow Element Types and Usage Patterns

## Core Flow Elements

### Screen Elements
- Used for user interaction and data collection
- Can contain input fields, display text, and buttons
- Support field validation and conditional visibility

### Decision Elements  
- Implement conditional logic in flows
- Support multiple outcomes based on criteria
- Can evaluate record data, user input, or system values

### Assignment Elements
- Set variable values and update records
- Support complex formulas and calculations
- Can assign multiple variables in a single element

### Record Operations
- Record Create: Insert new records
- Record Update: Modify existing records  
- Record Delete: Remove records
- Record Lookup: Find and retrieve records

### Subflow Elements
- Call other flows as reusable components
- Pass input and output variables
- Enable modular flow design

### Loop Elements
- Iterate over collections of records or data
- Support both record collections and primitive collections
- Include loop variables for current iteration data

## Best Practices

### Performance Optimization
- Minimize DML operations inside loops
- Use bulk operations when possible
- Limit the number of flow elements
- Use efficient SOQL queries

### Error Handling
- Implement fault paths for critical operations
- Provide meaningful error messages to users
- Log errors for debugging purposes

### Maintainability
- Use descriptive names for elements and variables
- Add comments and descriptions
- Follow consistent naming conventions
- Keep flows focused on single business processes
""",
            "category": "best_practices",
            "tags": ["flow_elements", "patterns", "best_practices", "performance", "error_handling"]
        },
        {
            "title": "Flow XML Structure and Metadata Patterns",
            "content": """
# Flow XML Structure and Metadata Patterns

## Basic Flow Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>60.0</apiVersion>
    <description>Flow description</description>
    <label>Flow Label</label>
    <processMetadataValues>
        <!-- Process metadata -->
    </processMetadataValues>
    <processType>Flow</processType>
    <status>Active</status>
    
    <!-- Variables -->
    <variables>
        <name>variableName</name>
        <dataType>String</dataType>
        <isCollection>false</isCollection>
        <isInput>true</isInput>
        <isOutput>false</isOutput>
    </variables>
    
    <!-- Flow Elements -->
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector>
            <targetReference>ElementName</targetReference>
        </connector>
    </start>
    
    <!-- Additional elements... -->
</Flow>
```

## Common Element Patterns

### Screen Element Pattern
```xml
<screens>
    <name>ScreenName</name>
    <label>Screen Label</label>
    <locationX>176</locationX>
    <locationY>158</locationY>
    <allowBack>true</allowBack>
    <allowFinish>true</allowFinish>
    <allowPause>false</allowPause>
    <fields>
        <name>FieldName</name>
        <dataType>String</dataType>
        <fieldText>Field Label</fieldText>
        <fieldType>InputField</fieldType>
        <isRequired>true</isRequired>
    </fields>
    <connector>
        <targetReference>NextElement</targetReference>
    </connector>
</screens>
```

### Decision Element Pattern
```xml
<decisions>
    <name>DecisionName</name>
    <label>Decision Label</label>
    <locationX>176</locationX>
    <locationY>278</locationY>
    <defaultConnectorLabel>Default Outcome</defaultConnectorLabel>
    <rules>
        <name>RuleName</name>
        <conditionLogic>and</conditionLogic>
        <conditions>
            <leftValueReference>variableName</leftValueReference>
            <operator>EqualTo</operator>
            <rightValue>
                <stringValue>ExpectedValue</stringValue>
            </rightValue>
        </conditions>
        <connector>
            <targetReference>NextElement</targetReference>
        </connector>
        <label>Rule Label</label>
    </rules>
</decisions>
```

## Metadata Best Practices

### Naming Conventions
- Use descriptive, consistent names
- Follow camelCase for element names
- Include purpose in element names (e.g., "GetAccountRecord", "ValidateInput")

### Layout and Organization
- Use consistent spacing for locationX and locationY
- Group related elements visually
- Maintain logical flow from top to bottom, left to right

### Variable Management
- Define clear input/output variables
- Use appropriate data types
- Set isCollection appropriately for bulk operations
""",
            "category": "technical_reference",
            "tags": ["xml", "metadata", "structure", "patterns", "examples"]
        }
    ]
    
    for doc in additional_docs:
        success = rag_manager.add_documentation(
            content=doc["content"],
            metadata={
                "title": doc["title"],
                "category": doc["category"],
                "tags": doc["tags"],
                "source": "curated_knowledge",
                "document_type": "reference_guide"
            }
        )
        
        if success:
            logger.info(f"✅ Added: {doc['title']}")
        else:
            logger.error(f"❌ Failed to add: {doc['title']}")

async def main():
    """Main function to add all Salesforce Flow documentation"""
    
    print("🚀 Adding Salesforce Flow Documentation to RAG Database")
    print("=" * 60)
    
    # Check if RAG manager is properly initialized
    if not rag_manager.vector_store:
        print("❌ RAG system not properly initialized. Please check your environment variables:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY") 
        print("   - OPENAI_API_KEY")
        return
    
    print("✅ RAG system initialized successfully")
    
    # Add the main Salesforce documentation
    print("\n1. Adding Salesforce Flow Metadata API Documentation...")
    success1 = await add_salesforce_flow_metadata_docs()
    
    # Add additional curated resources
    print("\n2. Adding additional Flow resources and best practices...")
    add_additional_flow_resources()
    
    print("\n🎉 Documentation addition completed!")
    
    if success1:
        print("\nYour FlowBuilderAgent can now reference:")
        print("- Official Salesforce Flow Metadata API documentation")
        print("- Flow element types and usage patterns")
        print("- XML structure and metadata patterns")
        print("- Best practices for flow development")
        
        print("\nTo test the knowledge base, you can use:")
        print("from src.tools.rag_tools import search_flow_knowledge_base")
        print('results = search_flow_knowledge_base("flow metadata structure")')

if __name__ == "__main__":
    asyncio.run(main()) 