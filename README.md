# Salesforce Agent Workforce

An intelligent multi-agent system powered by LangChain and LangGraph that automates Salesforce Flow development, deployment, and testing. This workforce of specialized agents collaborates to transform natural language requirements into deployed Salesforce Flows.

## 🎯 Project Status

**Current Phase**: Phase 2 - Enhanced FlowBuilderAgent Complete ✅  
**Latest Milestone**: Enhanced FlowBuilderAgent with Natural Language Processing ✅  
**Next Steps**: FlowTestAgent Implementation & Iterative Workflows

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
- **[TASK_1_4_IMPLEMENTATION.md](TASK_1_4_IMPLEMENTATION.md)**: Task 1.4 implementation details

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

### Planned Agents (Phase 2+)

#### 🧪 FlowTestAgent
- **Purpose**: Automated Flow testing and validation
- **Capabilities**: API testing, UI testing, assertion checking
- **Status**: 📋 Next Priority

## 🔄 Current Workflow

**Enhanced Workflow (Phase 2)**:
```
START → AuthenticationAgent → Enhanced FlowBuilderAgent → DeploymentAgent → END
```

The enhanced workflow automatically:
1. Authenticates to your Salesforce org
2. **NEW**: Processes natural language requirements using advanced NLP
3. **NEW**: Consults knowledge base for Salesforce best practices
4. **NEW**: Generates sophisticated Flow XML with multiple elements
5. **NEW**: Validates and repairs common deployment errors
6. Deploys the Flow to Salesforce with comprehensive guidance
7. Reports success/failure with detailed recommendations

## 🌟 Phase 2 Enhancements

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

### Run the Enhanced Workflow
```bash
# Using the enhanced demo (recommended)
python demo_enhanced_workflow.py

# Test enhanced capabilities
python test_enhanced_flow_builder.py

# Or run the main workflow
python run_workflow.py MYSANDBOX
```

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

### Enhanced Testing Options
```bash
# Test enhanced FlowBuilderAgent capabilities
python test_enhanced_flow_builder.py

# Demo enhanced workflow
python demo_enhanced_workflow.py

# Test workflow structure
python test_workflow_structure.py

# Test individual components
python -m pytest tests/  # When test suite is available
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

*Now with enhanced natural language processing and intelligent flow generation!*