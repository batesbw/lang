"""
Pydantic schemas for TestExecutorAgent interactions.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

from src.schemas.auth_schemas import SalesforceAuthResponse


class TestExecutionStatus(str, Enum):
    """Enum for test execution status"""
    QUEUED = "Queued"
    PROCESSING = "Processing" 
    ABORTED = "Aborted"
    COMPLETED = "Completed"
    FAILED = "Failed"


class TestResult(BaseModel):
    """Individual test method result"""
    test_class_name: str = Field(description="Name of the test class")
    test_method_name: str = Field(description="Name of the test method")
    outcome: str = Field(description="Test outcome: Pass, Fail, CompileFail, Skip")
    message: Optional[str] = Field(default=None, description="Error message if test failed")
    stack_trace: Optional[str] = Field(default=None, description="Stack trace if test failed")
    time: Optional[float] = Field(default=None, description="Execution time in milliseconds")


class CodeCoverageResult(BaseModel):
    """Code coverage information for a specific class"""
    apex_class_or_trigger_name: str = Field(description="Name of the covered class/trigger")
    num_lines_covered: int = Field(description="Number of lines covered")
    num_lines_uncovered: int = Field(description="Number of lines not covered")
    coverage_percentage: float = Field(description="Percentage of code coverage")


class TestRunSummary(BaseModel):
    """Summary of test run results"""
    test_run_id: str = Field(description="Unique identifier for the test run")
    status: TestExecutionStatus = Field(description="Overall test execution status")
    tests_ran: int = Field(description="Total number of tests executed")
    failures: int = Field(description="Number of failed tests")
    successes: int = Field(description="Number of successful tests")
    time: Optional[float] = Field(default=None, description="Total execution time")
    coverage_warnings: List[str] = Field(default=[], description="Code coverage warnings")


class TestExecutorRequest(BaseModel):
    """Request for test execution"""
    request_id: str = Field(description="Unique identifier for this request")
    salesforce_session: SalesforceAuthResponse = Field(description="Active Salesforce session")
    test_class_names: List[str] = Field(description="Names of already-deployed test classes to execute")
    org_alias: str = Field(description="Salesforce org alias for reference")
    timeout_minutes: int = Field(default=10, description="Timeout for test execution in minutes")
    coverage_target: float = Field(default=75.0, description="Target code coverage percentage")


class TestExecutorResponse(BaseModel):
    """Response from test execution"""
    request_id: str = Field(description="Unique identifier matching the request")
    success: bool = Field(description="Whether the test execution completed successfully")
    request: TestExecutorRequest = Field(description="Original request for reference")
    
    # Test execution results
    test_run_summary: Optional[TestRunSummary] = Field(default=None, description="Summary of test execution")
    test_results: List[TestResult] = Field(default=[], description="Individual test method results")
    code_coverage_results: List[CodeCoverageResult] = Field(default=[], description="Code coverage results")
    
    # Deployment information
    test_deployment_id: Optional[str] = Field(default=None, description="Deployment ID for test classes")
    test_deployment_success: bool = Field(default=False, description="Whether test class deployment succeeded")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if execution failed")
    warnings: List[str] = Field(default=[], description="Non-fatal warnings during execution")
    
    # Analysis and feedback
    overall_coverage_percentage: Optional[float] = Field(default=None, description="Overall code coverage percentage")
    coverage_meets_target: bool = Field(default=False, description="Whether coverage meets target")
    failed_test_analysis: List[str] = Field(default=[], description="Analysis of failed tests for feedback to FlowBuilder")
    
    # Metrics
    execution_time_seconds: Optional[float] = Field(default=None, description="Total execution time")
    
    def has_failures(self) -> bool:
        """Check if any tests failed"""
        return any(result.outcome in ["Fail", "CompileFail"] for result in self.test_results)
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed test results"""
        return [result for result in self.test_results if result.outcome in ["Fail", "CompileFail"]]
    
    def get_failure_summary(self) -> str:
        """Get a summary of test failures for feedback"""
        failed_tests = self.get_failed_tests()
        if not failed_tests:
            return "All tests passed successfully."
        
        summary_lines = [f"Found {len(failed_tests)} failed test(s):"]
        for test in failed_tests:
            summary_lines.append(f"- {test.test_class_name}.{test.test_method_name}: {test.message}")
            if test.stack_trace:
                summary_lines.append(f"  Stack trace: {test.stack_trace[:200]}...")
        
        return "\n".join(summary_lines) 