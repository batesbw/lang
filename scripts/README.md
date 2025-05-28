# Scripts Directory

This directory contains all the executable scripts for the Salesforce Agent Workforce project. Each script has a specific purpose and is organized by category.

## 🚀 Main Execution Scripts

### `run_workflow.py` - **Main Entry Point**
**Purpose**: Run the complete end-to-end Salesforce Agent Workforce workflow
**Requirements**: Full Salesforce credentials configured in `.env`
**Usage**:
```bash
python scripts/run_workflow.py YOUR_ORG_ALIAS
```
**What it does**:
- Authenticates to Salesforce
- Generates a Flow using Enhanced FlowBuilderAgent
- Deploys the Flow to your Salesforce org
- Reports success/failure with detailed feedback

### `demo_enhanced_workflow.py` - **Interactive Demo**
**Purpose**: Interactive demonstration of the Enhanced FlowBuilderAgent capabilities
**Requirements**: Anthropic API key only
**Usage**:
```bash
python scripts/demo_enhanced_workflow.py
```
**What it does**:
- Shows enhanced workflow capabilities
- Allows custom user story creation
- Demonstrates natural language processing
- Works without real Salesforce credentials

## 🧪 Testing & Validation Scripts

### `test_workflow_structure.py` - **System Validation**
**Purpose**: Validate that the LangGraph workflow is properly structured
**Requirements**: Basic dependencies only
**Usage**:
```bash
python scripts/test_workflow_structure.py
```
**What it does**:
- Tests imports and dependencies
- Validates state schema
- Checks workflow graph structure
- Confirms all nodes and edges are correct

### `test_enhanced_flow_builder.py` - **Agent Testing**
**Purpose**: Comprehensive testing of the Enhanced FlowBuilderAgent
**Requirements**: Anthropic API key
**Usage**:
```bash
python scripts/test_enhanced_flow_builder.py
```
**What it does**:
- Tests user story parsing
- Validates RAG knowledge base
- Tests XML generation
- Checks error handling

### `simple_agent_test.py` - **Individual Agent Testing**
**Purpose**: Test individual agents in isolation without full setup
**Requirements**: Anthropic API key only
**Usage**:
```bash
python scripts/simple_agent_test.py
```
**What it does**:
- Tests FlowBuilderAgent independently
- Tests Enhanced FlowBuilderAgent
- Tests AuthenticationAgent (mock mode)
- Provides clear pass/fail results

## 🔍 Visualization & Analysis Scripts

### `visualize_workflow.py` - **Workflow Visualization**
**Purpose**: Generate visual representation of the LangGraph workflow
**Requirements**: Basic dependencies only
**Usage**:
```bash
python scripts/visualize_workflow.py
```
**What it does**:
- Creates workflow diagram
- Shows agent relationships
- Exports visualization files
- Helps understand system architecture

## ⚙️ Setup & Configuration Scripts

### `setup_rag.py` - **RAG Knowledge Base Setup**
**Purpose**: Initialize and populate the RAG knowledge base with Salesforce best practices
**Requirements**: OpenAI API key for embeddings
**Usage**:
```bash
python scripts/setup_rag.py
```
**What it does**:
- Creates vector store for best practices
- Populates knowledge base with Flow guidance
- Sets up semantic search capabilities
- Prepares RAG system for Enhanced FlowBuilderAgent

### `setup_jwt_auth.py` - **JWT Authentication Setup**
**Purpose**: Help set up JWT authentication for Salesforce
**Requirements**: None (guidance script)
**Usage**:
```bash
python scripts/setup_jwt_auth.py
```
**What it does**:
- Guides through JWT setup process
- Helps generate certificates
- Validates JWT configuration
- Tests authentication flow

### `debug_jwt_auth.py` - **JWT Debugging**
**Purpose**: Debug JWT authentication issues
**Requirements**: Salesforce credentials
**Usage**:
```bash
python scripts/debug_jwt_auth.py
```
**What it does**:
- Tests JWT token generation
- Validates certificates
- Checks Salesforce connectivity
- Provides detailed error diagnostics

## 📚 Example Scripts

### `weather_agent_example.py` - **LangChain Agent Example**
**Purpose**: Simple example of how to build a LangChain agent (not Salesforce-related)
**Requirements**: Anthropic API key, OpenWeather API key
**Usage**:
```bash
python scripts/weather_agent_example.py
```
**What it does**:
- Demonstrates basic LangChain agent patterns
- Shows tool integration
- Provides interactive chat interface
- Educational reference for agent development

## 🚦 Quick Start Guide

### 1. **First Time Setup**
```bash
# Validate system structure
python scripts/test_workflow_structure.py

# Set up RAG knowledge base
python scripts/setup_rag.py

# Test individual agents
python scripts/simple_agent_test.py
```

### 2. **Development & Testing**
```bash
# Test enhanced capabilities
python scripts/demo_enhanced_workflow.py

# Visualize workflow
python scripts/visualize_workflow.py

# Test specific agents
python scripts/test_enhanced_flow_builder.py
```

### 3. **Production Use**
```bash
# Set up Salesforce authentication
python scripts/setup_jwt_auth.py

# Run full workflow
python scripts/run_workflow.py YOUR_ORG_ALIAS
```

## 📋 Script Dependencies

| Script | Anthropic API | Salesforce Creds | OpenAI API | Other |
|--------|---------------|------------------|------------|-------|
| `run_workflow.py` | ✅ | ✅ | ❌ | - |
| `demo_enhanced_workflow.py` | ✅ | ❌ | ❌ | - |
| `test_workflow_structure.py` | ❌ | ❌ | ❌ | - |
| `test_enhanced_flow_builder.py` | ✅ | ❌ | ❌ | - |
| `simple_agent_test.py` | ✅ | ❌ | ❌ | - |
| `visualize_workflow.py` | ❌ | ❌ | ❌ | - |
| `setup_rag.py` | ❌ | ❌ | ✅ | - |
| `setup_jwt_auth.py` | ❌ | ❌ | ❌ | - |
| `debug_jwt_auth.py` | ❌ | ✅ | ❌ | - |
| `weather_agent_example.py` | ✅ | ❌ | ❌ | OpenWeather |

## 🔧 Troubleshooting

### Common Issues:
1. **Import Errors**: Make sure you're running scripts from the project root directory
2. **Missing API Keys**: Check your `.env` file has the required keys
3. **Salesforce Auth**: Use `debug_jwt_auth.py` to diagnose connection issues
4. **Dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed

### Getting Help:
- Start with `test_workflow_structure.py` to validate basic setup
- Use `simple_agent_test.py` for isolated testing
- Check the main `README.md` for detailed setup instructions
- Review `environment_template.txt` for required environment variables

---

**Note**: All scripts should be run from the project root directory to ensure proper Python path resolution. 