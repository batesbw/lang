import os
import json
import tempfile
import subprocess
import time
from pathlib import Path
from typing import Type, Dict, Any, List, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from src.schemas.flow_validation_schemas import (
    FlowValidationRequest, 
    FlowValidationResponse, 
    FlowScannerRule,
    FlowValidationSummary
)

class FlowScannerTool(BaseTool):
    """Tool to validate Salesforce Flow XML using Lightning Flow Scanner CLI"""
    
    name: str = "flow_scanner_tool"
    description: str = (
        "Validates Salesforce Flow XML using Lightning Flow Scanner CLI. "
        "Detects Flow best practices violations, potential errors, and provides recommendations."
    )
    args_schema: Type[BaseModel] = FlowValidationRequest

    def _run(
        self,
        flow_xml: str,
        flow_name: str,
        request_id: str,
        config_path: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Run Lightning Flow Scanner on the provided Flow XML.
        
        Args:
            flow_xml: The Flow XML content to validate
            flow_name: Name of the flow for identification
            request_id: Unique request identifier
            config_path: Optional path to scanner configuration file
            
        Returns:
            JSON string containing validation results
        """
        try:
            # Get configuration from environment variables
            cli_path = os.getenv("FLOW_SCANNER_CLI_PATH", "sfdx")
            timeout = int(os.getenv("FLOW_SCANNER_TIMEOUT", "30"))
            
            # Create temporary file for the Flow XML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.flow-meta.xml', delete=False) as temp_file:
                temp_file.write(flow_xml)
                temp_file_path = temp_file.name
            
            try:
                # Build the scanner command
                cmd = [cli_path, "flow:scan", "--files", temp_file_path, "--json"]
                
                # Add config file if provided
                if config_path and os.path.exists(config_path):
                    cmd.extend(["--config", config_path])
                
                # Set failon to 'never' so we always get results
                cmd.extend(["--failon", "never"])
                
                print(f"🔍 Running Lightning Flow Scanner: {' '.join(cmd)}")
                
                # Execute the scanner
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=os.getcwd()
                )
                execution_time = time.time() - start_time
                
                print(f"⏱️  Scanner execution time: {execution_time:.2f} seconds")
                print(f"📋 Scanner return code: {result.returncode}")
                
                # Parse the scanner output
                scanner_output = self._parse_scanner_output(
                    result.stdout,
                    result.stderr,
                    result.returncode,
                    flow_name,
                    request_id,
                    execution_time
                )
                
                return json.dumps(scanner_output, indent=2)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            return json.dumps({
                "request_id": request_id,
                "flow_name": flow_name,
                "flow_api_name": flow_name,
                "success": False,
                "is_valid": False,
                "error_message": f"Lightning Flow Scanner timed out after {timeout} seconds",
                "scanner_version": None,
                "execution_time_seconds": timeout,
                "errors": [],
                "warnings": [],
                "notes": [],
                "error_count": 0,
                "warning_count": 0,
                "note_count": 0,
                "summary": {
                    "total_issues": 0,
                    "critical_issues": 0,
                    "flow_passed": False,
                    "scan_timestamp": time.time()
                }
            })
            
        except Exception as e:
            return json.dumps({
                "request_id": request_id,
                "flow_name": flow_name,
                "flow_api_name": flow_name,
                "success": False,
                "is_valid": False,
                "error_message": f"Flow Scanner execution failed: {str(e)}",
                "scanner_version": None,
                "execution_time_seconds": 0,
                "errors": [],
                "warnings": [],
                "notes": [],
                "error_count": 0,
                "warning_count": 0,
                "note_count": 0,
                "summary": {
                    "total_issues": 0,
                    "critical_issues": 0,
                    "flow_passed": False,
                    "scan_timestamp": time.time()
                }
            })

    def _parse_scanner_output(
        self,
        stdout: str,
        stderr: str,
        return_code: int,
        flow_name: str,
        request_id: str,
        execution_time: float
    ) -> Dict[str, Any]:
        """
        Parse Lightning Flow Scanner output into structured format.
        """
        issues = []
        scanner_version = None
        
        # Try to parse JSON output from stdout
        if stdout.strip():
            try:
                scanner_data = json.loads(stdout)
                print(f"📊 Scanner JSON output parsed successfully")
                
                # Check if this is an error response from the scanner
                if isinstance(scanner_data, dict) and "name" in scanner_data and scanner_data.get("name") in ["TypeError", "Error"]:
                    # This is a Flow validation error, not a scanner crash
                    # The scanner encountered a structural issue with the Flow XML
                    error_message = scanner_data.get("message", "Unknown scanner error")
                    print(f"❌ Scanner detected Flow XML structural issue: {error_message}")
                    
                    # Convert this to a validation rule instead of treating as a crash
                    structural_error = FlowScannerRule(
                        rule_name="FlowStructuralError",
                        severity="error",
                        message=f"Flow XML structural issue: {error_message}",
                        location=None,
                        element_name=None,
                        details={"scanner_error_type": scanner_data.get("name"), "scanner_error_message": error_message},
                        category="Structure",
                        fix_suggestion="Check Flow XML structure for missing or malformed elements"
                    )
                    
                    return {
                        "request_id": request_id,
                        "flow_name": flow_name,
                        "flow_api_name": flow_name,
                        "success": True,  # Scanner ran successfully and detected an issue
                        "is_valid": False,  # Flow is not valid due to structural issue
                        "error_message": None,  # No tool error - this is a validation error
                        "scanner_version": scanner_version,
                        "execution_time_seconds": execution_time,
                        "errors": [structural_error.model_dump()],
                        "warnings": [],
                        "notes": [],
                        "error_count": 1,
                        "warning_count": 0,
                        "note_count": 0,
                        "summary": {
                            "total_issues": 1,
                            "critical_issues": 1,
                            "flow_passed": False,
                            "scan_timestamp": time.time(),
                            "scanner_crashed": False
                        }
                    }
                
                # Extract issues from successful scanner output
                if isinstance(scanner_data, dict):
                    # Handle the actual scanner output format
                    result_data = scanner_data.get("result", {})
                    
                    if isinstance(result_data, dict):
                        # The actual format uses "results" array, not "violations"
                        violations = result_data.get("results", [])
                        
                        for violation in violations:
                            if isinstance(violation, dict):
                                issues.append(self._convert_scanner_result_to_rule(violation))
                    
                    # Handle legacy format as fallback (result as array with violations)
                    results = scanner_data.get("result", [])
                    if isinstance(results, list):
                        for result in results:
                            if isinstance(result, dict) and "violations" in result:
                                for violation in result.get("violations", []):
                                    issues.append(self._convert_violation_to_rule(violation))
                
                # Try to extract scanner version if available
                if "version" in scanner_data:
                    scanner_version = scanner_data["version"]
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  Could not parse scanner JSON output: {e}")
                print(f"Raw stdout: {stdout[:500]}")
                
                # Fall back to parsing text output
                issues = self._parse_text_output(stdout)
        
        # If stderr has content, it might contain important information
        if stderr.strip():
            print(f"⚠️  Scanner stderr: {stderr}")
        
        # Categorize issues by severity
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]
        notes = [issue for issue in issues if issue.severity == "note"]
        
        # Determine if flow is valid (no errors)
        is_valid = len(errors) == 0
        flow_passed = is_valid and return_code == 0
        
        return {
            "request_id": request_id,
            "flow_name": flow_name,
            "flow_api_name": flow_name,
            "success": True,  # Scanner ran successfully (even if it found issues)
            "is_valid": is_valid,
            "error_message": None,
            "scanner_version": scanner_version,
            "execution_time_seconds": execution_time,
            "errors": [rule.model_dump() for rule in errors],
            "warnings": [rule.model_dump() for rule in warnings],
            "notes": [rule.model_dump() for rule in notes],
            "error_count": len(errors),
            "warning_count": len(warnings),
            "note_count": len(notes),
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len(errors),
                "flow_passed": flow_passed,
                "scan_timestamp": time.time(),
                "scanner_crashed": False
            }
        }

    def _convert_violation_to_rule(self, violation: Dict[str, Any]) -> FlowScannerRule:
        """
        Convert a Lightning Flow Scanner violation to our FlowScannerRule format.
        """
        return FlowScannerRule(
            rule_name=violation.get("ruleName", "UnknownRule"),
            severity=violation.get("severity", "error").lower(),
            message=violation.get("message", "No message provided"),
            location=violation.get("line", None),
            element_name=violation.get("elementName", None),
            details=violation.get("details", {}),
            category=violation.get("category", "General"),
            fix_suggestion=violation.get("suggestion", None)
        )

    def _convert_scanner_result_to_rule(self, result: Dict[str, Any]) -> FlowScannerRule:
        """
        Convert a Lightning Flow Scanner result to our FlowScannerRule format.
        """
        return FlowScannerRule(
            rule_name=result.get("rule", result.get("ruleName", "UnknownRule")),
            severity=result.get("severity", "error").lower(),
            message=result.get("ruleDescription", result.get("message", "No message provided")),
            location=result.get("line", None),
            element_name=result.get("name", result.get("elementName", None)),
            details=result.get("details", {}),
            category=result.get("type", result.get("category", "General")),
            fix_suggestion=result.get("suggestion", None)
        )

    def _parse_text_output(self, output: str) -> List[FlowScannerRule]:
        """
        Parse text output when JSON parsing fails.
        """
        issues = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for common patterns in scanner output
            if "ERROR" in line.upper() or "WARNING" in line.upper():
                # Try to extract basic information
                severity = "error" if "ERROR" in line.upper() else "warning"
                
                issues.append(FlowScannerRule(
                    rule_name="ParsedFromText",
                    severity=severity,
                    message=line,
                    location=None,
                    element_name=None,
                    details={},
                    category="General",
                    fix_suggestion=None
                ))
        
        return issues

    async def _arun(self, *args, **kwargs) -> str:
        """Async version of _run"""
        return self._run(*args, **kwargs) 