"""
Apex Test Runner Tool for TestExecutorAgent.

This tool handles:
1. Executing already-deployed Apex test classes asynchronously 
2. Polling for test results
3. Retrieving code coverage information
4. Analyzing test failures

Note: This tool assumes test classes are already deployed by the DeploymentAgent.
"""

import time
import json
from typing import Type, List, Dict, Any, Optional
from datetime import datetime, timedelta

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError

from src.schemas.test_executor_schemas import (
    TestExecutorRequest, TestExecutorResponse, TestResult, 
    CodeCoverageResult, TestRunSummary, TestExecutionStatus
)


class ApexTestRunnerTool(BaseTool):
    """Tool for executing already-deployed Apex tests in Salesforce"""
    
    name: str = "apex_test_runner_tool"
    description: str = (
        "Executes already-deployed Apex test classes in Salesforce, retrieving detailed test results "
        "including pass/fail status, error messages, stack traces, and code coverage information. "
        "Assumes test classes are already deployed to the target org."
    )
    args_schema: Type[BaseModel] = TestExecutorRequest

    def _run(self, request: TestExecutorRequest) -> TestExecutorResponse:
        """
        Execute the test execution workflow for already-deployed test classes.
        """
        start_time = time.time()
        
        try:
            print(f"🧪 Starting test execution for {len(request.test_class_names)} test classes...")
            
            # Step 1: Verify test classes exist in the org
            self._verify_test_classes_exist(request)
            
            # Step 2: Execute tests
            test_results = self._execute_tests(request)
            
            # Step 3: Get code coverage
            coverage_results = self._get_code_coverage(request)
            
            # Step 4: Analyze results
            return self._create_response(
                request, test_results, coverage_results, start_time
            )
            
        except Exception as e:
            error_msg = f"Test execution failed with error: {str(e)}"
            print(f"❌ {error_msg}")
            return TestExecutorResponse(
                request_id=request.request_id,
                success=False,
                request=request,
                error_message=error_msg,
                execution_time_seconds=time.time() - start_time
            )

    def _verify_test_classes_exist(self, request: TestExecutorRequest):
        """Verify that the test classes exist in the target org"""
        print("🔍 Verifying test classes exist in target org...")
        
        try:
            sf_session = request.salesforce_session
            instance_url = sf_session.instance_url
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            sf = Salesforce(session_id=sf_session.session_id, instance_url=instance_url)
            
            # Query for the test classes
            class_names_str = "', '".join(request.test_class_names)
            query = f"SELECT Id, Name FROM ApexClass WHERE Name IN ('{class_names_str}')"
            
            results = sf.query(query)
            found_classes = [record['Name'] for record in results['records']]
            missing_classes = [name for name in request.test_class_names if name not in found_classes]
            
            if missing_classes:
                raise Exception(f"Test classes not found in org: {missing_classes}. Please ensure they are deployed first.")
            
            print(f"✅ All {len(found_classes)} test classes found in org")
            
        except Exception as e:
            print(f"❌ Error verifying test classes: {str(e)}")
            raise

    def _execute_tests(self, request: TestExecutorRequest) -> List[TestResult]:
        """Execute Apex tests using Tooling API"""
        print("🔄 Executing Apex tests...")
        
        try:
            # Initialize Salesforce connection
            sf_session = request.salesforce_session
            instance_url = sf_session.instance_url
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            sf = Salesforce(session_id=sf_session.session_id, instance_url=instance_url)
            
            # Get class IDs for the test classes
            class_ids = self._get_test_class_ids(sf, request.test_class_names)
            
            # Queue test execution for all test classes
            test_request_data = {
                "tests": [{"classId": class_id} for class_id in class_ids],
                "maxFailedTests": 100  # Allow up to 100 failures before stopping
            }
            
            # Use Tooling API to queue tests
            tooling_url = f"{instance_url}/services/data/v59.0/tooling/runTestsAsynchronous/"
            
            response = sf.session.post(
                tooling_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_request_data)
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to queue tests: {response.text}")
            
            test_run_id = response.json()
            print(f"✅ Tests queued with ID: {test_run_id}")
            
            # Poll for test completion
            return self._poll_test_results(sf, test_run_id, request.timeout_minutes)
            
        except Exception as e:
            print(f"❌ Error executing tests: {str(e)}")
            raise

    def _get_test_class_ids(self, sf: Salesforce, test_class_names: List[str]) -> List[str]:
        """Get the Salesforce IDs for test classes"""
        print("🔍 Getting test class IDs...")
        
        class_names_str = "', '".join(test_class_names)
        query = f"SELECT Id, Name FROM ApexClass WHERE Name IN ('{class_names_str}')"
        
        results = sf.query(query)
        class_id_map = {record['Name']: record['Id'] for record in results['records']}
        
        # Ensure we have IDs for all requested classes
        missing_classes = [name for name in test_class_names if name not in class_id_map]
        if missing_classes:
            raise Exception(f"Could not find IDs for test classes: {missing_classes}")
        
        class_ids = [class_id_map[name] for name in test_class_names]
        print(f"✅ Retrieved {len(class_ids)} test class IDs")
        
        return class_ids

    def _poll_test_results(self, sf: Salesforce, test_run_id: str, timeout_minutes: int) -> List[TestResult]:
        """Poll for test execution completion and retrieve results"""
        print(f"⏳ Polling for test results (timeout: {timeout_minutes} minutes)...")
        
        timeout_time = datetime.now() + timedelta(minutes=timeout_minutes)
        polling_interval = 10  # Poll every 10 seconds
        
        while datetime.now() < timeout_time:
            try:
                # Query test run status
                query = f"SELECT Id, Status, JobName, StartTime, EndTime FROM AsyncApexJob WHERE Id = '{test_run_id}'"
                job_result = sf.query(query)
                
                if job_result['totalSize'] == 0:
                    raise Exception(f"Test run {test_run_id} not found")
                
                job = job_result['records'][0]
                status = job['Status']
                
                print(f"📊 Test run status: {status}")
                
                if status in ['Completed', 'Failed', 'Aborted']:
                    # Test execution completed, retrieve detailed results
                    return self._retrieve_test_results(sf, test_run_id)
                
                # Wait before next poll
                time.sleep(polling_interval)
                
            except Exception as e:
                print(f"⚠️ Error polling test results: {str(e)}")
                time.sleep(polling_interval)
        
        # Timeout reached
        raise Exception(f"Test execution timed out after {timeout_minutes} minutes")

    def _retrieve_test_results(self, sf: Salesforce, test_run_id: str) -> List[TestResult]:
        """Retrieve detailed test results from Salesforce"""
        print("📋 Retrieving detailed test results...")
        
        try:
            # Query individual test results
            query = f"""
                SELECT Id, AsyncApexJobId, MethodName, Outcome, ApexClass.Name, 
                       Message, StackTrace, TestTimestamp
                FROM ApexTestResult 
                WHERE AsyncApexJobId = '{test_run_id}'
            """
            
            results = sf.query_all(query)
            test_results = []
            
            for record in results['records']:
                test_result = TestResult(
                    test_class_name=record['ApexClass']['Name'],
                    test_method_name=record['MethodName'],
                    outcome=record['Outcome'],
                    message=record.get('Message'),
                    stack_trace=record.get('StackTrace'),
                    time=None  # TestTimestamp format may need conversion
                )
                test_results.append(test_result)
            
            print(f"📊 Retrieved {len(test_results)} test results")
            return test_results
            
        except Exception as e:
            print(f"❌ Error retrieving test results: {str(e)}")
            raise

    def _get_code_coverage(self, request: TestExecutorRequest) -> List[CodeCoverageResult]:
        """Retrieve code coverage information"""
        print("📈 Retrieving code coverage information...")
        
        try:
            sf_session = request.salesforce_session
            instance_url = sf_session.instance_url
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            sf = Salesforce(session_id=sf_session.session_id, instance_url=instance_url)
            
            # Query code coverage for all classes
            query = """
                SELECT ApexClassOrTrigger.Name, NumLinesCovered, NumLinesUncovered,
                       Coverage
                FROM ApexCodeCoverage
                WHERE NumLinesCovered > 0 OR NumLinesUncovered > 0
            """
            
            results = sf.query_all(query)
            coverage_results = []
            
            for record in results['records']:
                total_lines = record['NumLinesCovered'] + record['NumLinesUncovered']
                coverage_percentage = (record['NumLinesCovered'] / total_lines * 100) if total_lines > 0 else 0
                
                coverage_result = CodeCoverageResult(
                    apex_class_or_trigger_name=record['ApexClassOrTrigger']['Name'],
                    num_lines_covered=record['NumLinesCovered'],
                    num_lines_uncovered=record['NumLinesUncovered'],
                    coverage_percentage=round(coverage_percentage, 2)
                )
                coverage_results.append(coverage_result)
            
            print(f"📊 Retrieved coverage for {len(coverage_results)} classes/triggers")
            return coverage_results
            
        except Exception as e:
            print(f"⚠️ Error retrieving code coverage: {str(e)}")
            return []  # Non-fatal error, return empty list

    def _create_response(
        self, 
        request: TestExecutorRequest, 
        test_results: List[TestResult], 
        coverage_results: List[CodeCoverageResult],
        start_time: float
    ) -> TestExecutorResponse:
        """Create the final TestExecutorResponse with all results and analysis"""
        
        # Calculate summary statistics
        total_tests = len(test_results)
        failures = len([r for r in test_results if r.outcome in ['Fail', 'CompileFail']])
        successes = total_tests - failures
        
        # Calculate overall coverage
        overall_coverage = self._calculate_overall_coverage(coverage_results)
        coverage_meets_target = overall_coverage >= request.coverage_target if overall_coverage is not None else False
        
        # Analyze failed tests for feedback
        failed_test_analysis = self._analyze_failed_tests(test_results)
        
        # Create test run summary
        test_run_summary = TestRunSummary(
            test_run_id="test_execution_" + str(int(start_time)),
            status=TestExecutionStatus.COMPLETED if failures == 0 else TestExecutionStatus.FAILED,
            tests_ran=total_tests,
            failures=failures,
            successes=successes,
            time=None,  # Could calculate from individual test times
            coverage_warnings=self._get_coverage_warnings(coverage_results, request.coverage_target)
        )
        
        execution_time = time.time() - start_time
        
        return TestExecutorResponse(
            request_id=request.request_id,
            success=failures == 0,  # Success only if no failures
            request=request,
            test_run_summary=test_run_summary,
            test_results=test_results,
            code_coverage_results=coverage_results,
            test_deployment_id=None,  # No deployment handled by this agent
            test_deployment_success=True,  # Assume deployment was successful since we're executing
            overall_coverage_percentage=overall_coverage,
            coverage_meets_target=coverage_meets_target,
            failed_test_analysis=failed_test_analysis,
            execution_time_seconds=round(execution_time, 2),
            warnings=self._get_warnings(test_results, coverage_results)
        )

    def _calculate_overall_coverage(self, coverage_results: List[CodeCoverageResult]) -> Optional[float]:
        """Calculate overall code coverage percentage"""
        if not coverage_results:
            return None
        
        total_covered = sum(result.num_lines_covered for result in coverage_results)
        total_uncovered = sum(result.num_lines_uncovered for result in coverage_results)
        total_lines = total_covered + total_uncovered
        
        if total_lines == 0:
            return None
        
        return round((total_covered / total_lines) * 100, 2)

    def _analyze_failed_tests(self, test_results: List[TestResult]) -> List[str]:
        """Analyze failed tests to provide feedback for FlowBuilder"""
        failed_tests = [r for r in test_results if r.outcome in ['Fail', 'CompileFail']]
        
        if not failed_tests:
            return []
        
        analysis = []
        
        # Group failures by type
        compile_failures = [t for t in failed_tests if t.outcome == 'CompileFail']
        runtime_failures = [t for t in failed_tests if t.outcome == 'Fail']
        
        if compile_failures:
            analysis.append(f"Compilation errors in {len(compile_failures)} test(s) - likely syntax or dependency issues in Flow")
        
        if runtime_failures:
            analysis.append(f"Runtime failures in {len(runtime_failures)} test(s) - Flow logic may not match expected behavior")
            
            # Look for common failure patterns
            for test in runtime_failures:
                if test.message:
                    if "assertion failed" in test.message.lower():
                        analysis.append(f"Test assertion failed in {test.test_class_name}.{test.test_method_name} - Flow output doesn't match expectations")
                    elif "null pointer" in test.message.lower():
                        analysis.append(f"Null pointer exception in {test.test_class_name}.{test.test_method_name} - Flow may not be handling null values properly")
                    elif "dml" in test.message.lower():
                        analysis.append(f"DML error in {test.test_class_name}.{test.test_method_name} - Flow database operations may have issues")
        
        return analysis

    def _get_coverage_warnings(self, coverage_results: List[CodeCoverageResult], target: float) -> List[str]:
        """Generate coverage warnings"""
        warnings = []
        
        low_coverage_classes = [
            result for result in coverage_results 
            if result.coverage_percentage < target
        ]
        
        if low_coverage_classes:
            warnings.append(f"{len(low_coverage_classes)} classes have coverage below {target}% target")
        
        return warnings

    def _get_warnings(self, test_results: List[TestResult], coverage_results: List[CodeCoverageResult]) -> List[str]:
        """Generate general warnings"""
        warnings = []
        
        skipped_tests = [r for r in test_results if r.outcome == 'Skip']
        if skipped_tests:
            warnings.append(f"{len(skipped_tests)} tests were skipped")
        
        if not coverage_results:
            warnings.append("No code coverage information available")
        
        return warnings

    async def _arun(self, request: TestExecutorRequest) -> TestExecutorResponse:
        """Async version - delegate to sync implementation"""
        return self._run(request) 