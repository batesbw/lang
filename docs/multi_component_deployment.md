# Multi-Component Deployment System

The deployment agent has been enhanced to support deploying multiple types of Salesforce metadata components simultaneously, while maintaining backward compatibility with existing flow-based deployments.

## Overview

The new deployment system can handle:
- **Multiple metadata types** in a single deployment (Flow, CustomObject, ApexClass, etc.)
- **Automatic package.xml generation** with proper type groupings
- **Flexible file structure** with configurable directories and extensions
- **Backward compatibility** with existing flow deployment code

## Key Features

### 1. Multiple Component Types Support

Deploy various Salesforce metadata types together:
- Flow
- CustomObject  
- ApexClass
- ApexTrigger
- CustomField
- Layout
- PermissionSet
- Profile
- CustomTab
- CustomApplication
- ValidationRule
- Workflow
- EmailTemplate
- StaticResource
- LightningComponentBundle
- AuraDefinitionBundle

### 2. Automatic Configuration

The system automatically determines the correct directory and file extension for each metadata type based on Salesforce standards.

### 3. Enhanced Deployment Feedback

- Component-level success/failure reporting
- Detailed error messages per component
- Summary statistics (total, successful, failed components)

## Usage Examples

### Basic Multi-Component Deployment

```python
from src.schemas.deployment_schemas import MetadataComponent, DeploymentRequest
from src.main_orchestrator import create_multi_component_deployment_request

# Define components to deploy
components_data = [
    {
        "component_type": "Flow",
        "api_name": "MyProcessFlow",
        "metadata_xml": "<Flow>...</Flow>"
    },
    {
        "component_type": "CustomObject", 
        "api_name": "MyCustomObject__c",
        "metadata_xml": "<CustomObject>...</CustomObject>"
    },
    {
        "component_type": "ApexClass",
        "api_name": "MyApexClass",
        "metadata_xml": "<ApexClass>...</ApexClass>"
    }
]

# Create deployment request
deployment_request = create_multi_component_deployment_request(
    components_data=components_data,
    salesforce_session=sf_session
)

# Deploy using the tool
from src.tools.salesforce_deployer_tool import SalesforceDeployerTool
tool = SalesforceDeployerTool()
response = tool._run(deployment_request)
```

### Direct Component Creation

```python
from src.schemas.deployment_schemas import MetadataComponent, DeploymentRequest

# Create components directly
components = [
    MetadataComponent(
        component_type="Flow",
        api_name="DirectFlow",
        metadata_xml="<Flow>...</Flow>"
    ),
    MetadataComponent(
        component_type="CustomObject",
        api_name="DirectObject__c", 
        metadata_xml="<CustomObject>...</CustomObject>",
        # Override defaults if needed
        directory="objects",
        file_extension="object"
    )
]

# Create deployment request
deployment_request = DeploymentRequest(
    request_id="my_deployment_123",
    components=components,
    salesforce_session=sf_session,
    api_version="59.0"
)
```

## Backward Compatibility

The new system maintains full backward compatibility with existing flow deployment code:

```python
# This still works exactly as before
deployment_request = DeploymentRequest(...)

# These properties still exist for backward compatibility
flow_xml = deployment_request.flow_xml      # Returns first Flow's XML
flow_name = deployment_request.flow_name    # Returns first Flow's API name
```

## Package Structure

The deployment system automatically creates the correct package structure:

```
deployment.zip
├── package.xml                           # Auto-generated with all types
├── flows/
│   └── MyFlow.flow-meta.xml
├── objects/
│   ├── MyObject__c.object
│   └── MyField__c.field  
├── classes/
│   ├── MyClass.cls
│   └── MyClass.cls-meta.xml
└── triggers/
    ├── MyTrigger.trigger
    └── MyTrigger.trigger-meta.xml
```

## Error Handling

The system provides detailed error reporting:

```python
response = tool._run(deployment_request)

if not response.success:
    print(f"Deployment failed: {response.error_message}")
    print(f"Failed components: {response.failed_components}/{response.total_components}")
    
    for error in response.component_errors:
        print(f"Error in {error['fullName']} ({error['componentType']}): {error['problem']}")
```

## Configuration

### Supported Metadata Types

The system includes built-in configuration for common metadata types. See `METADATA_TYPE_CONFIG` in `src/tools/salesforce_deployer_tool.py` for the complete list.

### Custom Metadata Types

For metadata types not in the built-in configuration, specify the directory and file extension:

```python
custom_component = MetadataComponent(
    component_type="CustomMetadataType",
    api_name="MyComponent",
    metadata_xml="<CustomMetadataType>...</CustomMetadataType>",
    directory="customMetadata",
    file_extension="md"
)
```

## Best Practices

1. **Group Related Components**: Deploy related components together (e.g., CustomObject + CustomFields + Layout)
2. **Handle Dependencies**: Deploy dependencies before dependent components
3. **Use Meaningful Request IDs**: Include timestamps or descriptive names
4. **Check Response Details**: Always check component-level errors for troubleshooting
5. **Test in Sandbox**: Test deployments in sandbox environments first

## Integration with Agent Workflow

The multi-component deployment system integrates seamlessly with the existing agent workflow:

1. **Flow Builder Agent** creates Flow components
2. **Prepare Deployment Request** converts to multi-component format
3. **Deployment Agent** deploys all components
4. **Enhanced feedback** provides detailed results

## Examples

See `examples/multi_component_deployment_example.py` for comprehensive usage examples demonstrating:
- Single component deployment
- Multi-component deployment  
- Direct component creation
- Error handling
- All supported metadata types 