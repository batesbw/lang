# Salesforce Agent Workforce

An intelligent multi-agent system powered by LangChain and LangGraph that automates Salesforce Flow development, deployment, and testing. This workforce of specialized agents collaborates to transform natural language requirements into deployed Salesforce Flows.

## 🎯 Project Status

**Current Phase**: Phase 1 - Foundation Complete ✅  
**Latest Milestone**: Task 1.4 - Initial LangGraph Orchestration ✅  
**Next Steps**: Phase 2 - Core Flow Lifecycle & Enhanced Agents

## 🚀 Vision

Transform how Salesforce professionals work with Flows by providing:
- **Intelligent Automation**: End-to-end Flow development from requirements to deployment
- **Multi-Agent Collaboration**: Specialized agents working together seamlessly
- **Expert Knowledge**: Built-in Salesforce best practices and optimization
- **Continuous Testing**: Automated validation and testing workflows

## 📋 Planning Documents

- **[PLANNING.md](PLANNING.md)**: Comprehensive project planning and multi-agent architecture
- **[TASK.md](TASK.md)**: Detailed task breakdown and implementation roadmap
- **[TASK_1_4_IMPLEMENTATION.md](TASK_1_4_IMPLEMENTATION.md)**: Task 1.4 implementation details

## 🤖 Agent Workforce

### Current Agents (Phase 1 Complete)

#### 🔐 AuthenticationAgent
- **Purpose**: Secure Salesforce authentication
- **Capabilities**: JWT/OAuth flows, session management
- **Status**: ✅ Implemented

#### 🏗️ FlowBuilderAgent  
- **Purpose**: Generate Salesforce Flow XML from requirements
- **Capabilities**: Basic Flow XML generation, screen flows
- **Status**: ✅ Implemented

#### 🚀 DeploymentAgent
- **Purpose**: Deploy Flows to Salesforce orgs
- **Capabilities**: Metadata API deployment, status tracking
- **Status**: ✅ Implemented

### Planned Agents (Phase 2+)

#### 🧪 FlowTestAgent
- **Purpose**: Automated Flow testing and validation
- **Capabilities**: API testing, UI testing, assertion checking
- **Status**: 📋 Planned

## 🔄 Current Workflow

**Linear Workflow (Task 1.4)**:
```
START → AuthenticationAgent → FlowBuilderAgent → DeploymentAgent → END
```

The workflow automatically:
1. Authenticates to your Salesforce org
2. Generates a simple test Flow XML
3. Deploys the Flow to Salesforce
4. Reports success/failure with detailed logging

## 🚀 Quick Start

### Prerequisites
```bash
# Required environment variables
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional (for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key

# Salesforce credentials (replace ORGALIAS with your org alias)
SF_CONSUMER_KEY_ORGALIAS=your_consumer_key
SF_CONSUMER_SECRET_ORGALIAS=your_consumer_secret
SF_MY_DOMAIN_URL_ORGALIAS=https://your-domain.my.salesforce.com
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

### Run the Workflow
```bash
# Using the CLI script (recommended)
python run_workflow.py MYSANDBOX

# Or directly
python src/main_orchestrator.py MYSANDBOX

# Validate workflow structure
python test_workflow_structure.py
```

### Example Output
```
🚀 Starting Salesforce Agent Workforce for org: MYSANDBOX
============================================================

=== AUTHENTICATION NODE ===
✅ Authentication successful

=== FLOW BUILDER NODE ===
✅ Flow XML generated: AgentGeneratedTestFlow

=== DEPLOYMENT NODE ===
✅ Deployment successful: 0Af...

📊 WORKFLOW SUMMARY:
✅ Authentication: SUCCESS
✅ Flow Building: SUCCESS  
✅ Deployment: SUCCESS
```

## 🏗️ Architecture

### Multi-Agent System
```
LangGraph Orchestrator
├── AuthenticationAgent (Salesforce Auth)
├── FlowBuilderAgent (XML Generation)
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

## 📊 Implementation Progress

### ✅ Phase 1: Foundation (Complete)
- [x] **Task 1.1**: AuthenticationAgent implementation
- [x] **Task 1.2**: FlowBuilderAgent (basic XML generation)
- [x] **Task 1.3**: DeploymentAgent implementation
- [x] **Task 1.4**: Initial LangGraph orchestration (linear workflow)

### 📋 Phase 2: Core Flow Lifecycle (Next)
- [ ] **Task 2.1**: FlowTestAgent (API-based testing)
- [ ] **Task 2.2**: FlowBuilderAgent enhancements (NL processing, RAG)
- [ ] **Task 2.3**: Iterative build-deploy-test loops

### 🔮 Phase 3: Advanced Capabilities
- [ ] UI-based testing with browser automation
- [ ] Advanced Flow repair strategies
- [ ] Knowledge base and RAG expansion

## 🎯 Use Cases

### Current Capabilities
- **Automated Flow Deployment**: "Deploy a simple test Flow to my sandbox"
- **End-to-End Workflow**: Complete authentication → build → deploy cycle
- **Error Handling**: Comprehensive error reporting and recovery

### Planned Capabilities (Phase 2+)
- **Natural Language Flow Creation**: "Create a lead qualification Flow"
- **Automated Testing**: "Test this Flow with various input scenarios"
- **Flow Optimization**: "Analyze and optimize this Flow for performance"

## 📈 Success Metrics

- **Workflow Success Rate**: 95%+ successful end-to-end executions
- **Error Recovery**: Intelligent retry and repair mechanisms
- **Performance**: Sub-30 second complete workflow execution
- **Observability**: Complete traceability via LangSmith

## 🔍 Observability

### LangSmith Integration
When configured, the system provides:
- Complete workflow execution traces
- Agent-level performance metrics
- Error analysis and debugging
- Token usage tracking

Access your traces at: https://smith.langchain.com/

## 🧪 Testing

### Workflow Validation
```bash
# Test workflow structure
python test_workflow_structure.py

# Test individual agents (when credentials are configured)
python src/agents/authentication_agent.py
python -m pytest tests/  # When test suite is available
```

## 🤝 Contributing

We welcome contributions in:
- **Agent Development**: New specialized agents
- **Tool Enhancement**: Improved Salesforce integration
- **Testing**: Comprehensive test coverage
- **Documentation**: Examples and best practices

## 📚 Resources

### Project Documentation
- [Planning Document](PLANNING.md) - Overall architecture and vision
- [Task Breakdown](TASK.md) - Detailed implementation roadmap
- [Task 1.4 Implementation](TASK_1_4_IMPLEMENTATION.md) - Current workflow details

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