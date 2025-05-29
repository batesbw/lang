# Unified Build/Deploy Mechanism

This document describes the unified build/deploy mechanism for the Salesforce Agent Workforce.

## 🎯 Overview

The unified workflow uses a single approach for all attempts:

1. **Single Flow Generation Method**: One method handles both initial attempts and retries
2. **Unified Input Processing**: User story, RAG knowledge, and optional retry context are processed together
3. **Contextual Prompt Generation**: The same prompt includes all available context (business requirements + optional failure context)
4. **No Special Retry Logic**: The system doesn't distinguish between "normal" and "retry" - it just includes whatever context is available
5. **Automatic Retry Loop**: When deployment fails, the system automatically retries with failure context added

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

1. Authentication → Unified Flow Builder → Deployment
2. If deployment succeeds → Workflow complete ✅
3. If deployment fails → Start retry process 🔄

### 2. Unified Flow Generation Process

**Every attempt uses the same method with different inputs:**

**Always Included:**
- Flow name, label, description
- User story (title, description, acceptance criteria)
- Business context, priority, affected objects
- RAG knowledge (best practices, sample flows, patterns)
- Standard flow generation requirements

**Conditionally Included (only if provided):**
- Previous Flow XML (for retry context)
- Deployment error details (for retry context)
- Component-level errors (for retry context)

### 3. Retry Process

When a deployment fails:

1. **Error Extraction**: The system extracts deployment error and component errors
2. **Context Addition**: Previous flow XML and error details are added to the original request
3. **Unified Generation**: The same flow generation method is called with the enhanced context
4. **Smart Rebuild**: LLM uses business requirements + failure context to rebuild properly
5. **Deployment Attempt**: The rebuilt flow is deployed
6. **Success or Retry**: If successful, workflow ends; if failed, retry up to the maximum limit

### 4. Request Structure

**Initial Request:**
```python
FlowBuildRequest(
    flow_api_name="MyFlow",
    flow_label="My Flow",
    flow_description="Flow description",
    user_story=UserStory(...),  # Always included
    retry_context=None          # Not present
)
```

**Retry Request:**
```python
FlowBuildRequest(
    flow_api_name="MyFlow",
    flow_label="My Flow", 
    flow_description="Flow description",
    user_story=UserStory(...),  # Same user story
    retry_context={             # Added for retry
        "retry_attempt": 1,
        "deployment_error": "Error message",
        "component_errors": [...],
        "original_flow_xml": "..."
    }
)
```

## 📊 Workflow Graph

```
START → Auth → Unified Flow Builder → Deployment
                      ↑                    ↓ (if failed)
                      └── Add Failure Context ←┘
                           ↓ (retry)
                      Deployment → Success/Max Retries
```

## 🛠️ Key Benefits

### Unified Approach (✅ IMPLEMENTED):
- ✅ **Single Method**: One flow generation method for all scenarios
- ✅ **Consistent Quality**: Same sophisticated approach regardless of attempt number
- ✅ **Complete Context**: User story always preserved, failure context added when available
- ✅ **Clean Architecture**: No special case logic or separate retry methods
- ✅ **LLM Intelligence**: Let the LLM naturally handle both business requirements and technical fixes
- ✅ **Maintainable Code**: Single code path is easier to understand and maintain

### Previous Complex Approach (❌ FIXED):
- ❌ Separate methods for initial vs retry attempts
- ❌ Risk of losing business context during retries
- ❌ Complex conditional logic for retry handling
- ❌ Inconsistent quality between initial and retry flows

## 🚀 Implementation Details

### Single Flow Generation Method

```python
def generate_flow_with_rag(self, request: FlowBuildRequest) -> FlowBuildResponse:
    # Same method for all attempts
    # Automatically includes user story, RAG knowledge, and optional retry context
```

### Unified Prompt Structure

```
Create a Salesforce flow based on the following requirements:
Flow Name: [name]
Flow Label: [label]
Description: [description]

USER STORY:
Title: [title]
Description: [user story description]

ACCEPTANCE CRITERIA:
1. [criteria 1]
2. [criteria 2]
...

Priority: [priority]
Business Context: [context]

RELEVANT BEST PRACTICES:
[RAG-retrieved best practices]

SIMILAR SAMPLE FLOWS FOR REFERENCE:
[RAG-retrieved sample flows]

[OPTIONAL - only if retry_context provided]
PREVIOUS ATTEMPT CONTEXT (Retry #1):
The previous flow deployment failed and needs to be rebuilt.

Previous deployment error:
[error message]

Component-level errors:
- [error 1]
- [error 2]

Previous flow XML (for reference only):
[truncated XML]

IMPORTANT REQUIREMENTS FOR RETRY:
1. You MUST fulfill ALL the original business requirements and user story
2. You MUST address the deployment error that caused the failure
...

REQUIREMENTS:
1. Generate a complete, production-ready Salesforce flow XML
...
```

## 🔧 Usage

The unified mechanism is automatically enabled when you run the workflow:

```python
from src.main_orchestrator import run_workflow

# Will automatically retry failed deployments with unified approach
final_state = run_workflow("YOUR_ORG_ALIAS")
```

## 📝 Example Unified Flow

1. **Initial Attempt**: 
   - Input: User story + RAG knowledge
   - Output: Sophisticated flow meeting business requirements (but with deployment error)

2. **Retry Attempt**:
   - Input: Same user story + RAG knowledge + failure context
   - Output: Sophisticated flow meeting business requirements AND avoiding deployment error

3. **Key Difference**: Only the additional failure context, everything else identical

## ⚙️ Unified Generation Process

### Every Attempt (Same Process):
1. Analyze requirements from user story
2. Retrieve RAG knowledge (best practices, samples, patterns)
3. Build comprehensive prompt with user story details
4. **If retry context exists**: Add failure context to the prompt
5. Generate sophisticated flow meeting all requirements

### No Special Cases:
- ❌ No separate "retry" vs "normal" logic
- ❌ No risk of losing business context
- ❌ No different quality levels between attempts
- ✅ Single, consistent, high-quality generation process

## 🔍 Architecture Comparison

**Before (Complex)**:
```
Initial: generate_flow_with_rag() → business-aligned flow
Retry:   generate_fix_for_deployment_failure() → basic fixes only
```

**After (Unified)**:
```
All attempts: generate_flow_with_rag(request_with_optional_retry_context) → business-aligned flow with optional error avoidance
```

This ensures consistent quality and business alignment across all attempts while naturally incorporating deployment error fixes when needed.