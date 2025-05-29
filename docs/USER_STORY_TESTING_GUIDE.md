# User Story Testing Guide for LangGraph Studio

This guide explains how to test the Salesforce Agent Workforce with user stories and acceptance criteria using the LangGraph Studio web interface.

## Prerequisites

1. **LangGraph Studio Running**: Make sure `langgraph dev` is running in your terminal
2. **Salesforce Org**: Have a Salesforce org configured with JWT authentication
3. **Environment Setup**: Ensure your `.env` file is properly configured

## Quick Start

### 1. Access LangGraph Studio
- Open your browser to: **http://localhost:2024**
- Navigate to the Studio interface (usually at `/studio` or similar)
- Select the `salesforce_agent_workforce` graph
- Click "New Thread" to start a new conversation

### 2. Test with a User Story

Copy and paste this JSON into the LangGraph Studio input field (replace `your-org-alias-here` with your actual Salesforce org alias):

```json
{
  "current_auth_request": {
    "org_alias": "your-org-alias-here"
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

### 3. Watch the Workflow Execute

The workflow will proceed through these steps:

1. **Authentication Node**: Connects to your Salesforce org using JWT
2. **Prepare Flow Request**: Analyzes the user story and creates a flow specification
3. **Flow Builder Node**: Generates Salesforce Flow XML based on the user story and acceptance criteria
4. **Prepare Deployment**: Prepares the flow for deployment
5. **Deployment Node**: Deploys the flow to your Salesforce org

## Sample User Stories

### Lead Assignment Automation
**Use Case**: Automate lead routing based on territory and workload
**Priority**: High
**Objects**: Lead, User, Territory, Opportunity

### Case Escalation
**Use Case**: Automatically escalate high-priority cases before SLA breach
**Priority**: Critical  
**Objects**: Case, User, Account, Contact

### Opportunity Approval Workflow
**Use Case**: Require approval for large deals to maintain quality
**Priority**: Medium
**Objects**: Opportunity, User, Account, Product2

## Getting Full Examples

Run this command to see all formatted examples:

```bash
python test_user_story_workflow.py
```

This will output complete JSON objects for each sample user story that you can copy directly into LangGraph Studio.

## User Story Structure

When creating your own user stories, use this structure:

```json
{
  "title": "Short descriptive title",
  "description": "As a [user type], I want [goal] so that [benefit]",
  "acceptance_criteria": [
    "Specific, measurable criteria",
    "Another criteria",
    "..."
  ],
  "priority": "Critical|High|Medium|Low",
  "business_context": "Background information about current state and pain points",
  "affected_objects": ["SalesforceObject1", "SalesforceObject2"],
  "user_personas": ["User Type 1", "User Type 2"]
}
```

## What to Observe

### In the Logs
- Look for "Found user story in state" message in the Prepare Flow Request node
- Check how the user story is converted into flow specifications
- Monitor the Flow Builder's analysis of acceptance criteria

### In the State
- `user_story`: Your original user story data
- `current_flow_build_request`: How the user story was translated into flow requirements
- `current_flow_build_response`: The generated flow XML and metadata
- `current_deployment_response`: Deployment results

### In the Generated Flow
- Flow elements that address each acceptance criterion
- Business logic that implements the user story requirements
- Error handling for edge cases mentioned in acceptance criteria

## Testing Without User Stories

For comparison, you can test the default behavior by omitting the `user_story` field:

```json
{
  "current_auth_request": {
    "org_alias": "your-org-alias-here"
  },
  "is_authenticated": false,
  "retry_count": 0,
  "messages": []
}
```

This will create a simple test flow instead of analyzing user requirements.

## Troubleshooting

### Common Issues

1. **Authentication Fails**: Check your org alias and JWT configuration
2. **Flow Build Fails**: Review the user story for clarity and completeness
3. **Deployment Fails**: Ensure your org has the necessary permissions and features

### Debug Tips

1. Check the state at each node to see how data flows through the workflow
2. Look at the logs for detailed error messages
3. Verify that your user story follows the expected structure
4. Test with simpler user stories first before trying complex scenarios

## Advanced Testing

### Custom User Stories
Create your own user stories based on your specific business requirements. Focus on:
- Clear acceptance criteria
- Specific Salesforce objects
- Realistic business context

### Multiple Scenarios
Test different types of flows:
- Screen flows for user interaction
- Record-triggered flows for automation
- Scheduled flows for batch processing

### Error Scenarios
Test edge cases:
- Invalid acceptance criteria
- Missing required fields
- Conflicting requirements

## Next Steps

After successful testing:
1. Review the generated flow XML
2. Test the deployed flow in Salesforce
3. Iterate on user story clarity based on results
4. Scale to more complex business scenarios 