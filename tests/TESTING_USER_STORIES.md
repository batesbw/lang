# Testing User Stories with Salesforce Agent Workforce

This document provides a comprehensive guide for testing user stories and acceptance criteria with the Salesforce Agent Workforce system.

## Overview

The Salesforce Agent Workforce now supports user stories and acceptance criteria as input, allowing you to:

1. **Provide business requirements** in a structured format
2. **Generate Salesforce Flows** that address specific acceptance criteria
3. **Test different scenarios** through multiple interfaces
4. **Validate flow generation** against business needs

## What's Been Implemented

### 1. User Story Schema Support
- **UserStory model** with title, description, acceptance criteria, priority, business context
- **FlowRequirement model** for detailed technical requirements
- **Enhanced FlowBuildRequest** that accepts user stories
- **State management** for user story data throughout the workflow

### 2. Workflow Integration
- **Modified prepare_flow_build_request** node to process user stories
- **Automatic flow specification** generation from user story requirements
- **Acceptance criteria analysis** for flow element creation
- **Business context consideration** in flow design

### 3. Multiple Testing Interfaces
- **LangGraph Studio Web Interface** for interactive testing
- **Direct API calls** for programmatic testing
- **Command-line scripts** for batch testing
- **Sample user stories** for quick validation

## Testing Methods

### Method 1: LangGraph Studio Web Interface (Recommended)

**Best for**: Interactive testing, debugging, visual workflow monitoring

**Steps**:
1. Ensure LangGraph dev is running: `langgraph dev`
2. Open browser to: **http://localhost:2024**
3. Look for Studio/UI interface
4. Create new thread
5. Paste JSON input with user story
6. Monitor workflow execution in real-time

**Sample Input**:
```json
{
  "current_auth_request": {
    "org_alias": "E2E_TEST_ORG"
  },
  "user_story": {
    "title": "Automate Lead Assignment",
    "description": "As a sales manager, I want leads to be automatically assigned to the right sales rep based on territory and workload so that response time is improved and leads are distributed fairly",
    "acceptance_criteria": [
      "Leads are assigned within 5 minutes of creation",
      "Assignment follows territory rules based on lead location",
      "Workload balancing considers current open opportunities per rep",
      "High-priority leads are assigned to senior reps",
      "Email notifications are sent to assigned rep and manager",
      "Assignment history is tracked for reporting"
    ],
    "priority": "High",
    "business_context": "Current manual assignment process takes 2-4 hours and leads to uneven distribution. Sales team has 15 reps across 3 territories.",
    "affected_objects": ["Lead", "User", "Territory", "Opportunity"],
    "user_personas": ["Sales Manager", "Sales Representative", "Lead Routing Admin"]
  },
  "is_authenticated": false,
  "retry_count": 0,
  "messages": []
}
```

**Sample Input**:
```json
{
  "current_auth_request": {
    "org_alias": "E2E_TEST_ORG"
  },
  "user_story": {
    "title": "Account Contact Counter",
    "description": "As a sales manager, I want the number of Contacts directly associated with an Account to appear on the account record, so I can quickly check the size of the Account",
    "acceptance_criteria": [
      "Count of contacts should update immediately when creating and/or deleting contacts",
      "Count should be saved the Count_of_Contacts__c field on the Account",
      "If there are no contacts associated with an account, the count should be 0"
    ],
    "priority": "High",
    "business_context": "Staff just need a quick way to view the size of their accounts",
    "affected_objects": ["Account", "Contact"],
    "user_personas": ["Sales Manager", "Sales Representative", "Lead Routing Admin"]
  },
  "is_authenticated": false,
  "retry_count": 0,
  "messages": []
}
```

### Method 2: Direct API Testing

**Best for**: Automated testing, CI/CD integration, programmatic validation

**Usage**:
```bash
python test_api_workflow.py your-org-alias
```

**Features**:
- Programmatic workflow execution
- Automatic status monitoring
- Detailed result reporting
- Error handling and debugging

### Method 3: Sample Generation Scripts

**Best for**: Getting started, exploring examples, learning the format

**Usage**:
```bash
python test_user_story_workflow.py
```

**Provides**:
- Multiple sample user stories
- Formatted JSON for copy/paste
- Different business scenarios
- Complete acceptance criteria examples

## Sample User Stories Included

### 1. Lead Assignment Automation
- **Priority**: High
- **Focus**: Territory-based routing, workload balancing
- **Objects**: Lead, User, Territory, Opportunity
- **Acceptance Criteria**: 6 specific, measurable requirements

### 2. Case Escalation
- **Priority**: Critical
- **Focus**: SLA management, automatic escalation
- **Objects**: Case, User, Account, Contact
- **Acceptance Criteria**: Time-based triggers, notification requirements

### 3. Opportunity Approval Workflow
- **Priority**: Medium
- **Focus**: Deal governance, approval processes
- **Objects**: Opportunity, User, Account, Product2
- **Acceptance Criteria**: Threshold-based approvals, audit trail

## What to Observe During Testing

### 1. In the Workflow Logs
- **"Found user story in state"** message in Prepare Flow Request node
- **User story analysis** and conversion to flow specifications
- **Acceptance criteria processing** by the Flow Builder
- **Business logic generation** based on requirements

### 2. In the State Data
- **user_story**: Original user story data preserved
- **current_flow_build_request**: Translated flow requirements
- **current_flow_build_response**: Generated flow XML and metadata
- **current_deployment_response**: Deployment results and status

### 3. In the Generated Flow
- **Flow elements** that address each acceptance criterion
- **Business logic** implementing user story requirements
- **Error handling** for edge cases mentioned in criteria
- **Data operations** aligned with affected objects

## Comparison Testing

### With User Story
- Flow generated based on specific business requirements
- Acceptance criteria drive flow element creation
- Business context influences design decisions
- Affected objects determine data operations

### Without User Story (Default)
- Simple test flow with basic screen and display text
- Generic structure for validation purposes
- No business logic implementation
- Minimal data operations

## File Structure

```
├── src/
│   ├── state/agent_workforce_state.py          # Updated with user_story field
│   ├── main_orchestrator.py                    # Modified prepare_flow_build_request
│   └── schemas/flow_builder_schemas.py         # UserStory and FlowRequirement models
├── test_user_story_workflow.py                 # Sample generation script
├── test_api_workflow.py                        # Direct API testing script
├── test_langgraph_api.py                       # API connectivity testing
├── USER_STORY_TESTING_GUIDE.md                 # Detailed web interface guide
└── TESTING_USER_STORIES_SUMMARY.md             # This comprehensive summary
```

## Quick Start Commands

```bash
# 1. Start LangGraph dev server
langgraph dev

# 2. Generate sample user stories
python test_user_story_workflow.py

# 3. Test API connectivity
python test_langgraph_api.py

# 4. Run full API test (replace 'myorg' with your org alias)
python test_api_workflow.py myorg

# 5. Open web interface
# Navigate to http://localhost:2024 in your browser
```

## Troubleshooting

### Common Issues

1. **LangGraph not responding**
   - Check if `langgraph dev` is running
   - Verify port 2024 is accessible
   - Look for error messages in terminal

2. **Authentication failures**
   - Verify org alias is correct
   - Check JWT configuration in .env file
   - Ensure Salesforce org is accessible

3. **User story not processed**
   - Verify JSON format is correct
   - Check that user_story field is included
   - Look for parsing errors in logs

4. **Flow generation fails**
   - Review acceptance criteria for clarity
   - Ensure affected objects are valid Salesforce objects
   - Check for conflicting requirements

### Debug Tips

1. **Use the web interface first** for visual debugging
2. **Check logs at each workflow node** for detailed error messages
3. **Start with simple user stories** before testing complex scenarios
4. **Compare with default behavior** to isolate user story-specific issues
5. **Verify state data** at each step to track data flow

## Next Steps

1. **Test with your own user stories** based on real business requirements
2. **Iterate on acceptance criteria** based on generated flow quality
3. **Scale to more complex scenarios** with multiple objects and integrations
4. **Integrate with CI/CD pipelines** using the API testing scripts
5. **Extend the schema** for additional business requirements as needed

## Benefits of This Approach

- **Business-driven development**: Flows generated from actual business requirements
- **Traceability**: Clear connection between requirements and implementation
- **Validation**: Acceptance criteria provide measurable success criteria
- **Iteration**: Easy to refine requirements and regenerate flows
- **Documentation**: User stories serve as living documentation
- **Testing**: Multiple interfaces support different testing scenarios 