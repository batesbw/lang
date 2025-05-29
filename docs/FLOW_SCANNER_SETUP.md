# Lightning Flow Scanner Setup Guide

This guide covers the installation and configuration of the Lightning Flow Scanner CLI plugin, which is required for the Flow Validation Agent.

## Prerequisites

- Salesforce CLI (`sfdx`) installed and configured
- Node.js 14.x or higher

## Installation

### 1. Install Lightning Flow Scanner plugin

```bash
# Install the Lightning Flow Scanner plugin
sfdx plugins:install lightning-flow-scanner
```

### 2. Verify installation

```bash
sfdx flow:scan --help
```

Expected output should show the flow:scan command help with all available options.

### 3. Test the scanner (optional)

```bash
# List all available plugins to confirm installation
sfdx plugins
```

You should see `lightning-flow-scanner` in the list of installed plugins.

## Configuration for Flow Validation

### 1. Test with a sample Flow XML

Create a test file `test-flow.flow-meta.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <label>Test Flow</label>
    <processType>Flow</processType>
    <status>Draft</status>
    <start>
        <locationX>50</locationX>
        <locationY>50</locationY>
        <connector>
            <targetReference>TestScreen</targetReference>
        </connector>
    </start>
    <screens>
        <name>TestScreen</name>
        <label>Test Screen</label>
        <locationX>50</locationX>
        <locationY>200</locationY>
        <allowBack>false</allowBack>
        <allowFinish>true</allowFinish>
        <allowPause>false</allowPause>
        <fields>
            <name>WelcomeMessage</name>
            <fieldText>Welcome to the test flow!</fieldText>
            <fieldType>DisplayText</fieldType>
        </fields>
        <showFooter>true</showFooter>
        <showHeader>true</showHeader>
    </screens>
</Flow>
```

### 2. Test the scanner

```bash
sfdx flow:scan --files test-flow.flow-meta.xml --json
```

Expected output should be a JSON report with any rule violations found.

## Configuration in Project

### Environment Variables

Add to your `.env` file:

```env
# Lightning Flow Scanner Configuration
FLOW_SCANNER_CLI_PATH=sfdx
FLOW_SCANNER_TIMEOUT=30
```

### Python Dependencies

The Flow Scanner tool uses subprocess to call the CLI. No additional Python packages are required beyond what's already in the project.

## Troubleshooting

### Common Issues

1. **"sfdx: command not found"**
   - Install Salesforce CLI: `npm install -g @salesforce/cli`
   - Verify with: `sfdx --version`

2. **"Plugin not found" errors**
   - Install the plugin: `sfdx plugins:install lightning-flow-scanner`
   - Verify installation: `sfdx plugins`

3. **"Permission denied" errors**
   - Ensure the CLI is executable: `chmod +x $(which sfdx)`
   - Try running with sudo if needed during installation

4. **Timeout errors**
   - Increase `FLOW_SCANNER_TIMEOUT` in environment variables
   - Check if the XML file is very large or complex

### Testing the Integration

Use the provided test script to verify the Flow Validation Agent works correctly:

```bash
python tests/test_flow_validation_agent.py
```

## Advanced Configuration

### Custom Rules

You can create custom Flow validation rules as described in the [Lightning Flow Scanner documentation](https://github.com/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx).

### Configuration File

Create a `.flow-scanner.json` file for custom rule configurations:

```json
{
    "rules": {
        "FlowDescription": {
            "severity": "warning"
        },
        "UnusedVariable": {
            "severity": "error"
        }
    },
    "exceptions": {
        "MyFlow": {
            "UnusedVariable": [
                "someVariable"
            ]
        }
    }
}
```

### Integration with CI/CD

The Flow Scanner can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Validate Flows
  run: |
    sfdx flow:scan --directory force-app/main/default/flows --json --failon error
```

## References

- [Lightning Flow Scanner GitHub](https://github.com/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx)
- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [Flow Best Practices](https://help.salesforce.com/s/articleView?id=sf.flow_prep_bestpractices.htm) 