# Simple Build/Deploy Retry Mechanism

This document describes the simplified retry mechanism for the Salesforce Agent Workforce.

## 🎯 Overview

The simplified workflow now includes:

1. **Automatic Retry Loop**: When a deployment fails, the system automatically retries the build/deploy cycle
2. **Simple Error Passing**: The FlowBuilder agent receives the original Flow XML and deployment error details
3. **Direct Fix Generation**: The system uses the LLM to analyze the error and generate a corrected Flow
4. **Runaway Prevention**: Configurable maximum retry limits prevent infinite loops

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Maximum number of build/deploy retry attempts when deployment fails
MAX_BUILD_DEPLOY_RETRIES=3
```

### Default Values

- `MAX_BUILD_DEPLOY_RETRIES`: 3 (if not set)

## 🔄 How It Works

### 1. Initial Build/Deploy Attempt

1. Authentication → Flow Builder → Deployment
2. If deployment succeeds → Workflow complete ✅
3. If deployment fails → Start retry process 🔄

### 2. Retry Process

When a deployment fails:

1. **Error Extraction**: The system extracts the deployment error message and component errors
2. **Retry Preparation**: The original Flow XML and error details are passed to the FlowBuilder agent
3. **Fix Generation**: The FlowBuilder agent uses the LLM to analyze the error and generate a corrected Flow
4. **Deployment Attempt**: The corrected Flow is deployed
5. **Success or Retry**: If successful, workflow ends; if failed, retry up to the maximum limit

### 3. Retry Context

The FlowBuilder agent receives a `retry_context` containing:
- `is_retry`: Boolean indicating this is a retry attempt
- `retry_attempt`: Current retry attempt number
- `original_flow_xml`: The original Flow XML that failed to deploy
- `deployment_error`: The error message from the failed deployment
- `component_errors`: Detailed component-level errors from Salesforce

### 4. Fix Generation

The FlowBuilder agent uses a focused prompt that includes:
- The original Flow requirements
- The deployment error message
- Component error details
- Common fix patterns (API name validation, required elements, etc.)

## 📊 Workflow Graph

```
START → Auth → Flow Builder → Deployment
                     ↑              ↓ (if failed)
                     └── Fix Logic ←┘
                          ↓ (retry)
                     Deployment → Success/Max Retries
```

## 🛠️ Key Simplifications

### Removed Complex Features:
- ❌ Failure categorization and learning
- ❌ Persistent failure memory storage
- ❌ Pattern matching from historical failures
- ❌ Complex cycle history tracking
- ❌ Failure analysis scoring

### Kept Simple Features:
- ✅ Basic retry loop with configurable max attempts
- ✅ Error message and component error passing
- ✅ Direct LLM-based fix generation
- ✅ Original Flow XML context for fixes

## 🚀 Benefits

1. **Simplicity**: Much easier to understand and maintain
2. **Reliability**: Fewer moving parts means fewer potential failure points
3. **Effectiveness**: Direct error analysis often produces better fixes than complex categorization
4. **Performance**: No overhead from failure memory storage and pattern matching
5. **Transparency**: Clear error messages and fix attempts

## 🔧 Usage

The retry mechanism is automatically enabled when you run the workflow:

```python
from src.main_orchestrator import run_workflow

# Will automatically retry failed deployments up to MAX_BUILD_DEPLOY_RETRIES times
final_state = run_workflow("YOUR_ORG_ALIAS")
```

## 📝 Example Retry Flow

1. **Initial Attempt**: Flow with invalid API name `"My-Flow"` fails deployment
2. **Error Captured**: `"Invalid API name: must be alphanumeric"`
3. **Fix Generated**: FlowBuilder corrects name to `"My_Flow"`
4. **Retry Successful**: Corrected Flow deploys successfully

## ⚙️ Configuration Examples

### Basic Setup (`.env`)
```bash
MAX_BUILD_DEPLOY_RETRIES=3
```

### Conservative Setup (fewer retries)
```bash
MAX_BUILD_DEPLOY_RETRIES=1
```

### Aggressive Setup (more retries)
```bash
MAX_BUILD_DEPLOY_RETRIES=5
```

---

This simplified approach provides effective deployment failure recovery while maintaining code simplicity and reliability.