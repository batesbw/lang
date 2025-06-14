# Salesforce Agent Workforce

An intelligent multi-agent system powered by LangChain and LangGraph that automates Salesforce Flow development, deployment, and testing using a **Test-Driven Development (TDD) approach**. This workforce of specialized agents collaborates to transform natural language requirements into fully tested, deployed Salesforce Flows.

## 🧪 NEW: Test-Driven Development Approach

**Revolutionary TDD Workflow**: We've completely reimagined the agent orchestration to follow Test-Driven Development principles:

```
🔄 TDD WORKFLOW:
1. 🧪 TestDesigner → Creates comprehensive test scenarios from requirements
2. 🚀 Test Deployment → Deploys Apex test classes to Salesforce
3. 🏗️  Flow Builder → Builds Flow to make tests pass (using test context)
4. 📦 Flow Deployment → Deploys the Flow to complete TDD cycle
5. ✅ Validation → Tests validate Flow behavior automatically
```

### Key TDD Benefits:
- **Quality First**: Tests define requirements before code is written
- **Better Coverage**: All Flow functionality is validated by tests
- **Faster Debugging**: Clear test failures guide development
- **Confidence**: Deployed Flows are guaranteed to meet acceptance criteria

### TDD Context Integration:
The Flow Builder now receives **test scenarios and deployed test classes** as input, ensuring the generated Flow satisfies all test requirements. This creates a tight feedback loop between requirements, tests, and implementation.

## 🎯 Project Status

**Current Phase**: Phase 3 - Test-Driven Development Approach ✅  
**Latest Milestone**: Complete TDD Workflow Implementation ✅  
**Next Steps**: Enhanced test analytics and validation reporting

## 🚀 Quick Start

### Prerequisites
```bash
# Required environment variables
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGCHAIN_API_KEY=your_langchain_api_key  # Alternative to LANGSMITH_API_KEY

# Optional (for web search integration - enhances deployment failure recovery)
TAVILY_API_KEY=your_tavily_api_key

# Salesforce credentials (replace E2E_TEST_ORG with your org alias)
SF_USERNAME_E2E_TEST_ORG=your_salesforce_username
SF_CONSUMER_KEY_E2E_TEST_ORG=your_connected_app_consumer_key
SF_PRIVATE_KEY_FILE_E2E_TEST_ORG=/path/to/your/private_key.pem
SF_INSTANCE_URL_E2E_TEST_ORG=https://your-domain.my.salesforce.com

# Optional (for enhanced RAG features)
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GITHUB_TOKEN=your_github_token
```

### Installation
```bash
# Clone the repository
git clone <repository>
cd salesforce-agent-workforce

# Create virtual environment
python -m venv langgraph-env
source langgraph-env/bin/activate  # On Windows: langgraph-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp environment_template.txt .env
# Edit .env with your credentials
```

### 🎯 How to Run the System

#### **Option 1: Quick Validation (No credentials needed)**
```bash
# Validate system structure
python scripts/test_workflow_structure.py
```

#### **Option 2: Test Individual Agents (Anthropic API key only)**
```bash
# Test agents without Salesforce setup
python scripts/simple_agent_test.py

# Interactive demo of enhanced capabilities
python scripts/demo_enhanced_workflow.py
```

#### **Option 3: Full End-to-End Workflow (Requires Salesforce credentials)**
```bash
# Set up Salesforce authentication first
python scripts/setup_jwt_auth.py

# Run the complete workflow (will prompt for org alias)
python scripts/run_workflow.py

# Or specify org alias directly
python scripts/run_workflow.py E2E_TEST_ORG
```

#### **Option 4: Visualize the System**
```bash
# Generate workflow diagrams
python scripts/visualize_workflow.py
```

> 📁 **All executable scripts are now organized in the `scripts/` directory. See [`scripts/README.md`](scripts/README.md) for detailed information about each script.**

## 🚀 Vision

Transform how Salesforce professionals work with Flows by providing:
- **Intelligent Automation**: End-to-end Flow development from requirements to deployment
- **Natural Language Processing**: Convert user stories into production-ready Flows
- **Multi-Agent Collaboration**: Specialized agents working together seamlessly
- **Expert Knowledge**: Built-in Salesforce best practices and optimization
- **Continuous Testing**: Automated validation and testing workflows

## 📋 Planning Documents

- **[PLANNING.md](PLANNING.md)**: Comprehensive project planning and multi-agent architecture
- **[TASK.md](TASK.md)**: Detailed task breakdown and implementation roadmap
- **[scripts/README.md](scripts/README.md)**: Complete guide to all executable scripts

## 🤖 Agent Workforce

### Current Agents (Phase 1 & 2 Complete)

#### 🔐 AuthenticationAgent
- **Purpose**: Secure Salesforce authentication
- **Capabilities**: JWT/OAuth flows, session management
- **Status**: ✅ Implemented

#### 🏗️ Enhanced FlowBuilderAgent ⭐ NEW!
- **Purpose**: Generate sophisticated Salesforce Flows from natural language
- **Capabilities**: 
  - 🧠 Natural language user story processing
  - 📚 RAG-powered best practices knowledge base
  - 🔧 Advanced XML generation (all flow types)
  - 🛠️ Automated error detection and repair
  - 💡 Comprehensive implementation guidance
- **Status**: ✅ Enhanced in Phase 2

#### 🚀 DeploymentAgent
- **Purpose**: Deploy Flows to Salesforce orgs
- **Capabilities**: Metadata API deployment, status tracking
- **Status**: ✅ Implemented

#### 🧪 TestDesignerAgent ⭐ NEW!
- **Purpose**: Generate comprehensive Apex test scenarios and classes
- **Capabilities**:
  - 📋 User story analysis and test scenario generation
  - 🧪 Apex test class creation with proper patterns
  - 🎯 Test data setup and teardown methods
  - ✅ Positive, negative, and edge case coverage
- **Status**: ✅ Implemented in TDD Phase

### Planned Agents (Phase 3+)

#### 🧪 FlowTestAgent
- **Purpose**: Automated Flow testing and validation
- **Capabilities**: API testing, UI testing, assertion checking
- **Status**: 📋 Future Enhancement

## 🔄 TDD Workflow

**Test-Driven Development Workflow (Phase 3)**:
```
START → Authentication → TestDesigner → Test Deployment → Flow Builder → Flow Deployment → END
```

The TDD workflow automatically:
1. **Authenticates** to your Salesforce org
2. **🧪 TestDesigner**: Analyzes requirements and creates comprehensive test scenarios
3. **🚀 Test Deployment**: Deploys Apex test classes to establish expected behavior
4. **🏗️  Flow Builder**: Generates Flow XML designed to make tests pass (with TDD context)
5. **📦 Flow Deployment**: Deploys the Flow to complete the TDD cycle
6. **✅ Validation**: Tests are already in place to validate Flow behavior

### TDD Process Details:
- **Test-First**: Test scenarios define the expected behavior before Flow development
- **Context-Aware**: Flow Builder receives test scenarios as input to guide development
- **Quality Assurance**: Every deployed Flow has comprehensive test coverage
- **Continuous Validation**: Tests can be run anytime to verify Flow behavior

## 🌟 Phase 3: Test-Driven Development

### Enhanced FlowBuilderAgent Features

#### 🧠 Natural Language Processing
- **User Story Parser**: Converts natural language requirements into structured flow specifications
- **Acceptance Criteria Analysis**: Automatically identifies flow elements needed
- **Business Context Understanding**: Considers organizational context in flow design

#### 📚 RAG Knowledge Base
- **15+ Best Practice Categories**: Flow naming, performance, security, testing, etc.
- **Semantic Search**: Context-aware retrieval of relevant guidance
- **Comprehensive Coverage**: Record-triggered flows, screen flows, error handling, and more

#### 🔧 Advanced XML Generation
- **Multiple Flow Types**: Screen, Record-Triggered, Scheduled, Platform Event flows
- **Complex Elements**: Decisions, Loops, Get Records, DML operations, Assignments
- **Proper Validation**: Extensive error checking with detailed suggestions
- **Flow Definition Support**: Automatic activation control

#### 🛠️ Automated Repair System
- **Pattern-Based Error Detection**: Common Salesforce deployment errors
- **Intelligent Repair Strategies**: Automatic fixes for access rights, version conflicts, etc.
- **Best Practices Application**: Automatic application of Salesforce standards

### Example Enhanced Output
```
🚀 Starting Salesforce Agent Workforce for org: MYSANDBOX
============================================================

=== AUTHENTICATION NODE ===
✅ Authentication successful

=== ENHANCED FLOW BUILDER NODE ===
Step 1: Parsing user story into flow requirements...
Step 2: Consulting knowledge base for best practices...
Step 3: Designing flow structure...
Step 4: Generating flow XML...
Step 5: Validating and repairing flow...
Step 6: Adding implementation guidance...
✅ Enhanced Flow generated: Lead_Qualification_Flow
📝 Elements Created: 5
🎯 Best Practices Applied: 12
💡 Recommendations: 8

=== DEPLOYMENT NODE ===
✅ Deployment successful: 0Af...

📊 ENHANCED WORKFLOW RESULTS:
✅ Enhanced Flow Building Results:
  📋 Flow Name: Lead_Qualification_Flow
  📝 Elements Created: 5
  🎯 Best Practices Applied: 12
  💡 Recommendations: 8
```

## 🏗️ Architecture

### Enhanced Multi-Agent System
```
LangGraph Orchestrator
├── AuthenticationAgent (Salesforce Auth)
├── Enhanced FlowBuilderAgent ⭐
│   ├── UserStoryParserTool (NLP)
│   ├── FlowKnowledgeRAGTool (Best Practices)
│   ├── AdvancedFlowXmlGeneratorTool (XML Generation)
│   └── FlowRepairTool (Error Handling)
├── DeploymentAgent (Metadata Deployment)
└── [Future: FlowTestAgent, ApexGeneratorAgent, etc.]
```

### Technology Stack
- **LangGraph**: Multi-agent orchestration and workflow management
- **LangChain**: Agent framework and tool integration
- **LangSmith**: Observability and tracing
- **Claude (Anthropic)**: Natural language processing and reasoning
- **simple-salesforce**: Salesforce API integration
- **xmltodict**: Flow metadata parsing and generation
- **InMemoryVectorStore**: RAG knowledge base storage
- **OpenAI Embeddings**: Semantic search capabilities

## 📊 Implementation Progress

### ✅ Phase 1: Foundation (Complete)
- [x] **Task 1.1**: AuthenticationAgent implementation
- [x] **Task 1.2**: FlowBuilderAgent (basic XML generation)
- [x] **Task 1.3**: DeploymentAgent implementation
- [x] **Task 1.4**: Initial LangGraph orchestration (linear workflow)

### ✅ Phase 2: Enhanced FlowBuilderAgent (Complete)
- [x] **Enhanced Schemas**: Comprehensive data models for complex flows
- [x] **RAG Knowledge Base**: 15+ categories of Salesforce Flow best practices
- [x] **Advanced XML Generator**: Support for all flow types and elements
- [x] **User Story Parser**: Natural language to flow requirements
- [x] **Flow Repair Tool**: Automated error detection and repair
- [x] **Enhanced Agent**: Orchestrated workflow with all tools

### 📋 Phase 2: Remaining Tasks (Next)
- [ ] **Task 2.1**: FlowTestAgent (API-based testing)
- [ ] **Task 2.3**: Iterative build-deploy-test loops

### 🔮 Phase 3: Advanced Capabilities
- [ ] UI-based testing with browser automation
- [ ] Advanced Flow repair strategies
- [ ] Knowledge base and RAG expansion

## 🎯 Use Cases

### Current Enhanced Capabilities
- **Natural Language Flow Creation**: "Create a lead qualification flow that updates status based on revenue and employee count"
- **Intelligent Flow Design**: Automatic application of Salesforce best practices
- **Complex Flow Generation**: Multi-element flows with decisions, loops, and DML operations
- **Automated Error Handling**: Detection and repair of common deployment issues
- **Production-Ready Output**: Comprehensive validation and deployment guidance

### Example User Stories Supported
```
"As a sales manager, I want to automatically qualify leads based on 
revenue and employee count so that my team can focus on high-value prospects"

"As a customer success manager, I want a guided onboarding flow for new 
customers to collect their preferences and setup requirements"

"As an operations manager, I want to automate approval processes for 
expense reports based on amount and department rules"
```

### Planned Capabilities (Phase 2+)
- **Automated Testing**: "Test this Flow with various input scenarios"
- **Flow Optimization**: "Analyze and optimize this Flow for performance"
- **Iterative Refinement**: Continuous improvement based on test results

## 📈 Success Metrics

- **Enhanced Flow Quality**: Production-ready flows with best practices applied
- **Natural Language Processing**: 95%+ accurate requirement interpretation
- **Error Prevention**: Automated detection and repair of common issues
- **Knowledge Integration**: Comprehensive best practices application
- **Workflow Success Rate**: 95%+ successful end-to-end executions

## 🔍 Observability

### LangSmith Integration
When configured, the enhanced system provides:
- Complete workflow execution traces with enhanced agent steps
- Natural language processing analysis
- Knowledge base query tracking
- XML generation and repair process visibility
- Agent-level performance metrics
- Error analysis and debugging
- Token usage tracking

Access your traces at: https://smith.langchain.com/

## 🧪 Testing

### Available Test Scripts
```bash
# System validation (no credentials needed)
python scripts/test_workflow_structure.py

# Individual agent testing (Anthropic API key only)
python scripts/simple_agent_test.py

# Enhanced agent capabilities (Anthropic API key only)
python scripts/test_enhanced_flow_builder.py

# Interactive demo (Anthropic API key only)
python scripts/demo_enhanced_workflow.py

# Full workflow visualization (no credentials needed)
python scripts/visualize_workflow.py
```

## 🤝 Contributing

We welcome contributions in:
- **Agent Development**: New specialized agents (FlowTestAgent next!)
- **Tool Enhancement**: Improved Salesforce integration and NLP capabilities
- **Knowledge Base**: Additional best practices and patterns
- **Testing**: Comprehensive test coverage
- **Documentation**: Examples and best practices

## 📚 Resources

### Project Documentation
- [Planning Document](PLANNING.md) - Overall architecture and vision
- [Task Breakdown](TASK.md) - Detailed implementation roadmap
- [Scripts Guide](scripts/README.md) - Complete guide to all executable scripts

### Salesforce Resources
- [Flow Builder Guide](https://help.salesforce.com/s/articleView?id=sf.flow.htm)
- [Metadata API Guide](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/)
- [Flow Best Practices](https://help.salesforce.com/s/articleView?id=sf.flow_prep_bestpractices.htm)

### LangChain/LangGraph Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)

## 📄 License

This project is for educational and professional development purposes. Please ensure compliance with Salesforce and Anthropic terms of service.

---

**Ready to revolutionize Salesforce Flow development with AI agents? 🚀**

*Now with enhanced natural language processing and intelligent flow generation!*

## Features

- **Authentication Agent**: Secure Salesforce org authentication
- **Flow Builder Agent**: Intelligent Flow XML generation with retry capabilities
- **Flow Validation Agent**: Automated Flow validation using Lightning Flow Scanner
- **Deployment Agent**: Automated Flow deployment with error handling
- **Intelligent Retry Logic**: Automatic retries for validation errors and deployment failures
- **Comprehensive Logging**: Detailed execution tracking and error reporting
- **Web Search Integration**: Enhanced deployment failure recovery with intelligent web search
  - Automatically searches for solutions when deployments fail
  - Prioritizes official Salesforce documentation and community solutions
  - Integrates search insights into retry attempts for improved success rates
  - Optional feature (requires TAVILY_API_KEY)

## Architecture

The system uses a multi-agent architecture orchestrated with LangGraph:

```
Authentication → Flow Building → Flow Validation → Deployment
                     ↑              ↓
                     └── Retry Loop ←┘
```

### Agents

1. **Authentication Agent**: Handles Salesforce org login and session management
2. **Flow Builder Agent**: Creates Salesforce Flow XML from requirements
3. **Flow Validation Agent**: Validates flows using Lightning Flow Scanner
4. **Deployment Agent**: Deploys flows to Salesforce orgs

### Retry Logic

The system includes intelligent retry mechanisms:
- **Validation Retry**: If Flow Scanner finds errors, the system retries with specific error context
- **Deployment Retry**: If deployment fails, the system retries with enhanced error analysis
- **Configurable Limits**: Maximum retry attempts are configurable via environment variables

## Prerequisites

### Required Software

- Python 3.9+
- Node.js 14.x+
- Salesforce CLI (`sf`)
- Lightning Flow Scanner

### Install Prerequisites

```bash
# Install Salesforce CLI
npm install -g @salesforce/cli

# Install Lightning Flow Scanner
npm install -g @salesforce/sfdx-scanner

# Initialize Flow Scanner (first time)
sf scanner rule list
```

See [FLOW_SCANNER_SETUP.md](FLOW_SCANNER_SETUP.md) for detailed Lightning Flow Scanner installation and configuration.

### Environment Variables

Create a `.env` file in the root directory:

```env
# =======================
# AI PROVIDER CONFIGURATION
# =======================

# Global AI Provider Configuration (fallback for all agents)
# Options: "anthropic" or "gemini"
AI_PROVIDER=anthropic

# Global Model Name (specific model to use for the provider)
MODEL_NAME=claude-3-5-sonnet-20241022

# Global LLM Configuration
MAX_TOKENS=4096

# ===================
# ANTHROPIC SETTINGS
# ===================

# Required: Anthropic API Key for LLM functionality
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# =================
# GEMINI SETTINGS
# =================

# Optional: Gemini API Key for Google's Gemini models
GEMINI_API_KEY=your_gemini_api_key_here

# ==================================
# PER-AGENT AI MODEL CONFIGURATION
# ==================================

# You can configure different AI models for each agent to optimize performance:

# Authentication Agent - Fast model for auth tasks
# AUTHENTICATION_AI_PROVIDER=anthropic
# AUTHENTICATION_MODEL_NAME=claude-3-haiku-20240307
# AUTHENTICATION_MAX_TOKENS=1024

# Flow Builder Agent - Powerful model for complex XML generation
# FLOW_BUILDER_AI_PROVIDER=anthropic
# FLOW_BUILDER_MODEL_NAME=claude-3-opus-20240229
# FLOW_BUILDER_MAX_TOKENS=8192

# Test Designer Agent - Creative model for test scenario generation
# TEST_DESIGNER_AI_PROVIDER=gemini
# TEST_DESIGNER_MODEL_NAME=gemini-pro
# TEST_DESIGNER_MAX_TOKENS=4096

# Web Search Agent - Efficient model for query processing
# WEB_SEARCH_AI_PROVIDER=anthropic
# WEB_SEARCH_MODEL_NAME=claude-3-5-sonnet-20241022
# WEB_SEARCH_MAX_TOKENS=2048

# Deployment Agent - Reliable model for deployment tasks
# DEPLOYMENT_AI_PROVIDER=anthropic
# DEPLOYMENT_MODEL_NAME=claude-3-5-sonnet-20241022
# DEPLOYMENT_MAX_TOKENS=4096

# =======================
# OBSERVABILITY SETTINGS
# =======================

# Optional: LangSmith API Key for tracing and observability
LANGSMITH_API_KEY=your_langsmith_api_key_here

# =======================
# WEB SEARCH SETTINGS
# =======================

# Optional: Tavily API Key for web search functionality
TAVILY_API_KEY=your_tavily_api_key_here

# =======================
# WORKFLOW SETTINGS
# =======================

# Optional: Maximum build/deploy retry attempts (default: 3)
MAX_BUILD_DEPLOY_RETRIES=3

# Optional: LangGraph recursion limit (default: 50)
LANGGRAPH_RECURSION_LIMIT=50

# =======================
# SALESFORCE SETTINGS
# =======================

# Salesforce JWT Bearer Flow Settings
SALESFORCE_CLIENT_ID=your_connected_app_client_id
SALESFORCE_PRIVATE_KEY_PATH=path/to/your/private_key.pem
SALESFORCE_USERNAME=your_salesforce_username
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd salesforce-agent-workforce
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install prerequisites (see above)

4. Configure environment variables

## Usage

### Basic Usage

Run the workflow with a Salesforce org alias:

```bash
python src/main_orchestrator.py SANDBOX_ALIAS
```

### Testing Flow Validation

Test the Flow Validation Agent:

```bash
python tests/test_flow_validation_agent.py
```

### With User Stories

You can provide user stories in the workflow state to generate flows based on specific requirements.

## Flow Validation

The Flow Validation Agent integrates with Salesforce's Lightning Flow Scanner to:

- **Detect Best Practice Violations**: Identifies Flow patterns that don't follow Salesforce best practices
- **Find Structural Issues**: Detects problems like invalid references, duplicate elements, and missing required fields
- **Validate XML Structure**: Ensures proper XML syntax and Flow metadata structure
- **Generate Retry Context**: Provides specific error context for intelligent retry attempts

### Validation Workflow

1. **Receive Flow XML**: Gets Flow XML from the Flow Builder Agent
2. **Create Temporary File**: Saves XML to temporary file for scanner
3. **Run Lightning Flow Scanner**: Executes `sf scanner run` with appropriate parameters
4. **Parse Results**: Converts scanner output to structured validation response
5. **Determine Next Action**: Decides whether to proceed to deployment or retry building

### Supported Validations

- API name format validation
- Element reference integrity
- Duplicate element detection
- Required field validation
- XML syntax validation
- Flow best practices compliance

## Error Handling and Retries

### Validation Error Handling

When the Flow Validation Agent finds errors:

1. **Error Classification**: Categorizes errors by type and severity
2. **Retry Context Generation**: Creates detailed context for the Flow Builder Agent
3. **Specific Fix Recommendations**: Provides targeted guidance for common issues
4. **Incremental Retry Counter**: Tracks retry attempts to prevent infinite loops

### Common Error Types

- **API Name Issues**: Invalid characters, spaces, or naming conventions
- **Reference Errors**: Invalid targetReference values pointing to non-existent elements
- **Duplicate Elements**: Multiple elements with the same name
- **Missing Required Fields**: Flow elements missing mandatory properties
- **XML Syntax Errors**: Malformed XML structure

## Project Structure

```
src/
├── agents/
│   ├── authentication_agent.py
│   ├── enhanced_flow_builder_agent.py
│   ├── flow_validation_agent.py       # New validation agent
│   └── deployment_agent.py
├── tools/
│   ├── salesforce_auth_tool.py
│   ├── flow_scanner_tool.py           # New scanner tool
│   └── salesforce_deployer_tool.py
├── schemas/
│   ├── auth_schemas.py
│   ├── flow_builder_schemas.py
│   ├── flow_validation_schemas.py     # New validation schemas
│   └── deployment_schemas.py
├── state/
│   └── agent_workforce_state.py       # Updated with validation fields
└── main_orchestrator.py               # Updated workflow
```

## Configuration

### Retry Limits

Control retry behavior via environment variables:

```env
MAX_BUILD_DEPLOY_RETRIES=3  # Maximum retry attempts for validation/deployment failures
```

### Flow Scanner Configuration

```env
FLOW_SCANNER_CLI_PATH=sf           # Path to Salesforce CLI
FLOW_SCANNER_TIMEOUT=30            # Scanner timeout in seconds
FLOW_SCANNER_OUTPUT_FORMAT=json    # Scanner output format
```

### Advanced Configuration

- **LANGGRAPH_RECURSION_LIMIT**: Controls the maximum number of steps LangGraph can execute before terminating. If you're experiencing recursion limit errors, increase this value from the default of 50.
- **MAX_BUILD_DEPLOY_RETRIES**: Controls how many times the system will retry building and deploying a Flow when deployment fails.
- **ANTHROPIC_MODEL**: You can use different Claude models based on your needs and API access.

## Troubleshooting

### Flow Scanner Issues

1. **Scanner not found**: Install with `npm install -g @salesforce/sfdx-scanner`
2. **Rules not initialized**: Run `sf scanner rule list` to download rules
3. **Permission errors**: Ensure CLI tools are executable
4. **Timeout errors**: Increase `FLOW_SCANNER_TIMEOUT` value

### Common Problems

- **Authentication failures**: Check Salesforce CLI configuration and org access
- **Flow build errors**: Review LLM responses and increase context if needed
- **Deployment failures**: Check org permissions and metadata API limits

## Development

### Adding New Validation Rules

1. Create custom PMD rules for Flow-specific patterns
2. Configure rule severity levels in the Flow Scanner tool
3. Update error analysis logic in the Flow Validation Agent

### Testing

Run the test suite:

```bash
# Test Flow Validation Agent
python tests/test_flow_validation_agent.py

# Test entire workflow (requires Salesforce org)
python src/main_orchestrator.py SANDBOX_ALIAS
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Your License Here]