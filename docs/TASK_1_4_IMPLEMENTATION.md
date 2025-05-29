# Task 1.4: Initial LangGraph Orchestration Implementation

## Overview

Task 1.4 implements the initial LangGraph orchestration for the Salesforce Agent Workforce, creating a linear workflow that connects the three foundational agents:

**Workflow**: `START` → `AuthenticationAgent` → `FlowBuilderAgent` → `DeploymentAgent` → `END`

## Implementation Details

### Core Components

#### 1. Main Orchestrator (`src/main_orchestrator.py`)
- **Purpose**: Central orchestration logic using LangGraph
- **Key Features**:
  - Linear workflow with conditional routing
  - Comprehensive error handling
  - LangSmith tracing integration
  - State management between agents
  - Detailed logging and progress reporting

#### 2. Workflow Structure
The workflow consists of 5 main nodes:

1. **`authentication`**: Authenticates to Salesforce using provided org alias
2. **`prepare_flow_request`**: Creates a default flow build request
3. **`flow_builder`**: Generates Flow XML using the BasicFlowXmlGeneratorTool
4. **`prepare_deployment_request`**: Prepares deployment request with session details
5. **`deployment`**: Deploys the Flow to Salesforce using the SalesforceDeployerTool

#### 3. Conditional Logic
- **After Authentication**: Proceeds to flow building if successful, otherwise terminates
- **After Flow Building**: Proceeds to deployment if successful, otherwise terminates
- **After Deployment**: Always terminates (success or failure)

#### 4. State Management
Uses `AgentWorkforceState` TypedDict to pass data between agents:
- Authentication session details
- Flow build requests/responses
- Deployment requests/responses
- Error messages and retry counts

### Files Created/Modified

#### New Files:
- `src/main_orchestrator.py` - Main LangGraph orchestration logic
- `run_workflow.py` - CLI script for easy workflow execution
- `test_workflow_structure.py` - Validation tests for workflow structure
- `TASK_1_4_IMPLEMENTATION.md` - This documentation

#### Key Features:

1. **Error Handling**: Each node has try-catch blocks with meaningful error messages
2. **LangSmith Integration**: Automatic tracing with configurable metadata
3. **CLI Interface**: Simple command-line execution with validation
4. **State Validation**: Comprehensive state schema testing
5. **Modular Design**: Clean separation between orchestration and agent logic

## Usage

### Prerequisites
Ensure you have the following environment variables set:
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key

# Salesforce credentials (replace ORGALIAS with your org alias)
SF_CONSUMER_KEY_ORGALIAS=your_consumer_key
SF_CONSUMER_SECRET_ORGALIAS=your_consumer_secret
SF_MY_DOMAIN_URL_ORGALIAS=https://your-domain.my.salesforce.com
```

### Running the Workflow

#### Option 1: Using the CLI Script (Recommended)
```bash
python run_workflow.py MYSANDBOX
```

#### Option 2: Direct Python Execution
```bash
python src/main_orchestrator.py MYSANDBOX
```

#### Option 3: Programmatic Usage
```python
from src.main_orchestrator import run_workflow

final_state = run_workflow("MYSANDBOX")
if final_state.get("is_authenticated") and \
   final_state.get("current_deployment_response", {}).get("success"):
    print("Workflow completed successfully!")
```

### Testing the Implementation

#### Validate Workflow Structure
```bash
python test_workflow_structure.py
```

This test validates:
- All imports are working correctly
- State schema is properly defined
- LangGraph workflow compiles successfully
- All expected nodes and edges are present

## Workflow Output

The workflow provides detailed console output showing:

1. **Authentication Status**: Success/failure with org details
2. **Flow Building Progress**: XML generation status
3. **Deployment Results**: Deployment ID and status
4. **Error Details**: Comprehensive error reporting at each stage
5. **Final Summary**: Complete workflow results summary

### Example Output
```
🚀 Starting Salesforce Agent Workforce for org: MYSANDBOX
============================================================

=== AUTHENTICATION NODE ===
Authentication Agent: Successfully authenticated to MYSANDBOX.

=== PREPARING FLOW BUILD REQUEST ===
Prepared flow build request for: AgentGeneratedTestFlow

=== FLOW BUILDER NODE ===
Flow XML generated successfully for Flow: AgentGeneratedTestFlow

=== PREPARING DEPLOYMENT REQUEST ===
Prepared deployment request for flow: AgentGeneratedTestFlow

=== DEPLOYMENT NODE ===
Deployment successful for request ID: abc-123-def, SF Deployment ID: 0Af...

============================================================
🏁 WORKFLOW COMPLETED
============================================================

📊 WORKFLOW SUMMARY:
----------------------------------------
✅ Authentication: SUCCESS
   Org ID: 00D...
   Instance URL: https://your-domain.my.salesforce.com
✅ Flow Building: SUCCESS
   Flow Name: AgentGeneratedTestFlow
   Flow Label: Agent Generated Test Flow
✅ Deployment: SUCCESS
   Deployment ID: 0Af...
   Status: Succeeded
----------------------------------------
```

## LangSmith Integration

When `LANGSMITH_API_KEY` is configured, the workflow automatically:
- Creates traces for the entire workflow execution
- Tags runs with `["salesforce-agent-workforce", "linear-workflow"]`
- Includes metadata: org_alias, workflow_type, version
- Provides detailed step-by-step execution visibility

Access traces at: https://smith.langchain.com/

## Error Handling

The workflow includes comprehensive error handling:

1. **Authentication Failures**: Clear error messages about credential issues
2. **Flow Building Errors**: XML generation problems with detailed diagnostics
3. **Deployment Failures**: Salesforce-specific deployment errors
4. **Network Issues**: Timeout and connectivity error handling
5. **Unexpected Errors**: Graceful handling with full error context

## Next Steps

This linear workflow establishes the foundation for:
- **Phase 2**: Iterative build-deploy-test loops with conditional routing
- **Enhanced Error Recovery**: Automatic retry mechanisms
- **Human-in-the-Loop**: Approval steps for critical operations
- **Parallel Execution**: Multiple agent tasks running concurrently

## Validation

✅ **Task 1.4 Requirements Met**:
- [x] Created `main_orchestrator.py` with LangGraph implementation
- [x] Defined simple linear workflow: START → Auth → FlowBuilder → Deployment → END
- [x] Implemented state passing between agents
- [x] Added basic error handling with workflow termination on failures
- [x] Integrated LangSmith tracing for the graph
- [x] Created CLI script to trigger workflow with predefined inputs
- [x] All components tested and validated

The implementation successfully completes Task 1.4 and provides a solid foundation for the iterative workflows planned in Phase 2. 