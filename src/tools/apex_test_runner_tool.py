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
import subprocess
import tempfile
import os
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
from src.schemas.auth_schemas import SalesforceAuthResponse


class ApexTestRunnerTool(BaseTool):
    """Tool for executing already-deployed Apex tests in Salesforce"""
    
    name: str = "apex_test_runner_tool"
    description: str = (
        "Executes already-deployed Apex test classes in Salesforce, retrieving detailed test results "
        "including pass/fail status, error messages, stack traces, and code coverage information. "
        "Uses both Salesforce CLI (sfdx) and Salesforce API for comprehensive test execution. "
        "Assumes test classes are already deployed to the target org."
    )
    args_schema: Type[BaseModel] = TestExecutorRequest

    def _run(self, **kwargs) -> TestExecutorResponse:
        """
        Execute the test execution workflow for already-deployed test classes.
        Accepts either a TestExecutorRequest object or individual parameters.
        """
        start_time = time.time()
        
        try:
            # Handle different input formats
            if 'full_request' in kwargs and kwargs['full_request']:
                # Use the full request if provided
                request_data = kwargs['full_request']
                if isinstance(request_data, dict):
                    request = TestExecutorRequest(**request_data)
                else:
                    request = request_data
            else:
                # Build request from individual parameters
                request = TestExecutorRequest(**kwargs)
            
            print(f"🧪 Starting test execution for {len(request.test_class_names)} test classes...")
            print(f"📋 Request ID: {request.request_id}")
            print(f"🏢 Org Alias: {request.org_alias}")
            print(f"🎯 Coverage Target: {request.coverage_target}%")
            
            # Step 1: Verify we have a valid Salesforce session
            self._verify_salesforce_session(request)
            
            # Step 2: Try dynamic CLI approach, fall back to API if needed
            test_results = self._execute_tests_with_fallback(request)
            
            # Step 3: Get code coverage
            coverage_results = self._get_code_coverage(request)
            
            # Step 4: Analyze results and create response
            return self._create_response(
                request, test_results, coverage_results, start_time
            )
            
        except Exception as e:
            error_msg = f"Test execution failed with error: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Try to extract request_id from kwargs
            request_id = kwargs.get('request_id', 'unknown')
            if 'full_request' in kwargs and kwargs['full_request']:
                request_data = kwargs['full_request']
                if isinstance(request_data, dict):
                    request_id = request_data.get('request_id', 'unknown')
            
            return TestExecutorResponse(
                request_id=request_id,
                success=False,
                request=TestExecutorRequest(
                    request_id=request_id,
                    salesforce_session=SalesforceAuthResponse(
                        success=False,
                        session_id="",
                        instance_url="",
                        user_id="unknown",
                        org_id="unknown",
                        auth_type_used="unknown"
                    ),
                    test_class_names=[],
                    org_alias="unknown"
                ),
                error_message=error_msg,
                execution_time_seconds=time.time() - start_time
            )

    def _verify_salesforce_session(self, request: TestExecutorRequest):
        """Verify that we have a valid Salesforce session"""
        print("🔍 Verifying Salesforce session...")
        
        sf_session = request.salesforce_session
        if not sf_session:
            raise Exception("No Salesforce session provided in request")
        
        if not sf_session.success:
            raise Exception(f"Salesforce session is not successful: {sf_session.error_message}")
        
        if not sf_session.session_id or not sf_session.instance_url:
            raise Exception("Incomplete Salesforce session information")
        
        print(f"✅ Valid Salesforce session found for instance: {sf_session.instance_url}")

    def _execute_tests_with_fallback(self, request: TestExecutorRequest) -> List[TestResult]:
        """Execute tests using dynamic CLI approach, fall back to API if needed"""
        print("🔄 Executing Apex tests with dynamic CLI approach...")
        
        # Try CLI approach first (either existing alias or access token)
        if self._is_sfdx_available():
            try:
                print(f"🚀 Attempting test execution with Salesforce CLI")
                return self._execute_tests_with_cli_dynamic(request)
            except Exception as e:
                print(f"⚠️ CLI execution failed: {str(e)}")
                print("🔄 Falling back to Salesforce API approach...")
        else:
            print("⚠️ sfdx not available, using Salesforce API approach")
        
        # Fall back to API approach
        return self._execute_tests_with_api(request)
    
    def _find_matching_cli_org(self, target_instance_url: str) -> Optional[str]:
        """Find existing CLI org alias that matches the target instance URL"""
        try:
            print("🔍 Checking for existing CLI org aliases...")
            
            # Run sf org list auth to get authenticated orgs
            result = subprocess.run(
                ['sf', 'org', 'list', 'auth', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"⚠️ Could not list CLI orgs: {result.stderr}")
                return None
            
            # Parse the JSON output
            orgs_data = json.loads(result.stdout)
            orgs = orgs_data.get('result', [])
            
            # Normalize our target URL for comparison
            target_url_normalized = target_instance_url.replace('https://', '').replace('http://', '').rstrip('/')
            
            print(f"🎯 Looking for orgs matching: {target_url_normalized}")
            
            for org in orgs:
                org_url = org.get('instanceUrl', '')
                org_alias = org.get('alias', '')
                org_username = org.get('username', '')
                
                # Normalize org URL for comparison
                org_url_normalized = org_url.replace('https://', '').replace('http://', '').rstrip('/')
                
                print(f"   📋 Found org: alias='{org_alias}', url='{org_url_normalized}'")
                
                if org_url_normalized == target_url_normalized:
                    print(f"✅ Found matching CLI org: alias='{org_alias}', username='{org_username}'")
                    return org_alias if org_alias else org_username
            
            print(f"⚠️ No matching CLI org found for {target_url_normalized}")
            return None
            
        except Exception as e:
            print(f"⚠️ Error checking CLI orgs: {e}")
            return None
    
    def _execute_tests_with_cli_dynamic(self, request: TestExecutorRequest) -> List[TestResult]:
        """Execute tests using CLI with dynamic org discovery"""
        sf_session = request.salesforce_session
        instance_url = sf_session.instance_url
        
        # Ensure instance URL has https://
        if not instance_url.startswith('https://'):
            instance_url = f"https://{instance_url}"
        
        # First, try to find an existing CLI org that matches our instance
        cli_org_identifier = self._find_matching_cli_org(instance_url)
        
        if cli_org_identifier:
            print(f"📋 Using existing CLI org: {cli_org_identifier}")
            return self._execute_tests_with_cli_alias(request, cli_org_identifier)
        else:
            print(f"📋 No matching CLI org found, using access token method")
            return self._execute_tests_with_access_token(request)
    
    def _execute_tests_with_cli_alias(self, request: TestExecutorRequest, org_identifier: str) -> List[TestResult]:
        """Execute tests using existing CLI org alias/username"""
        print(f"📋 Executing tests with CLI org: {org_identifier}")
        
        # Build the test command using the org identifier
        test_classes_arg = ",".join(request.test_class_names)
        
        # Try the newer 'sf' command first, fall back to 'sfdx'
        commands_to_try = [
            ['sf', 'apex', 'run', 'test', '--tests', test_classes_arg, '--target-org', org_identifier, '--code-coverage', '--result-format', 'json', '--synchronous', '--wait', '10'],
            ['sfdx', 'force:apex:test:run', '--tests', test_classes_arg, '--target-org', org_identifier, '--code-coverage', '--result-format', 'json', '--synchronous', '--wait', '10']
        ]
        
        for cmd in commands_to_try:
            try:
                print(f"🔧 Running command: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_minutes * 60
                )
                
                print(f"📊 Command result: return_code={result.returncode}")
                if result.stdout:
                    print(f"📄 stdout: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
                if result.stderr:
                    print(f"⚠️  stderr: {result.stderr}")
                
                # For CLI test execution, return code 100 means tests ran but some failed
                # Return code 0 means tests ran and all passed
                # Only other return codes are actual command failures
                if result.returncode == 0 or result.returncode == 100:
                    # Parse the JSON output
                    print(f"✅ CLI command executed successfully (tests ran with result code {result.returncode}), parsing results...")
                    try:
                        output_data = json.loads(result.stdout)
                        return self._parse_sfdx_test_results(output_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Could not parse JSON output: {e}")
                        print(f"   Raw stdout: {result.stdout}")
                        continue  # Try next command
                else:
                    print(f"⚠️ Command failed with return code {result.returncode}")
                    continue  # Try next command
                
            except subprocess.TimeoutExpired:
                raise Exception(f"Test execution timed out after {request.timeout_minutes} minutes")
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse JSON output: {e}")
                print(f"   Raw stdout: {result.stdout}")
            except Exception as e:
                print(f"⚠️ Command execution failed: {e}")
        
        # If all CLI commands failed, raise an exception to trigger next fallback
        raise Exception("All CLI alias command attempts failed")

    def _execute_tests_with_access_token(self, request: TestExecutorRequest) -> List[TestResult]:
        """Execute tests using Salesforce CLI with access token method (fallback)"""
        print("📋 Executing tests with Salesforce CLI using access token...")
        
        sf_session = request.salesforce_session
        instance_url = sf_session.instance_url
        access_token = sf_session.session_id  # In our case, session_id is the access token
        
        # Ensure instance URL has https://
        if not instance_url.startswith('https://'):
            instance_url = f"https://{instance_url}"
        
        print(f"🔧 Setting instance URL: {instance_url}")
        print(f"🔑 Using access token: {access_token[:20]}...")
        
        # Set the org-instance-url configuration (globally for this execution)
        config_cmd = ['sf', 'config', 'set', f'org-instance-url={instance_url}', '--global']
        print(f"🔧 Running config command: {' '.join(config_cmd)}")
        
        try:
            config_result = subprocess.run(
                config_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if config_result.returncode != 0:
                print(f"⚠️ Config command failed: {config_result.stderr}")
                raise Exception(f"Failed to set org-instance-url: {config_result.stderr}")
            
            print("✅ Successfully set org-instance-url")
            
        except Exception as e:
            print(f"❌ Error setting configuration: {e}")
            raise Exception(f"Configuration setup failed: {e}")
        
        # Build the test command using the access token as target-org
        test_classes_arg = ",".join(request.test_class_names)
        
        # Escape the access token properly - it may contain special characters like !
        escaped_access_token = access_token.replace('!', r'\!')
        
        # Try the newer 'sf' command first, fall back to 'sfdx'
        commands_to_try = [
            ['sf', 'apex', 'run', 'test', '--tests', test_classes_arg, '--target-org', escaped_access_token, '--code-coverage', '--result-format', 'json', '--synchronous', '--wait', '10'],
            ['sfdx', 'force:apex:test:run', '--tests', test_classes_arg, '--target-org', escaped_access_token, '--code-coverage', '--result-format', 'json', '--synchronous', '--wait', '10']
        ]
        
        for cmd in commands_to_try:
            try:
                print(f"🔧 Running command: {' '.join(cmd[:8])}... [access_token] {' '.join(cmd[9:])}")  # Hide the access token in logs
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_minutes * 60
                )
                
                print(f"📊 Command result: return_code={result.returncode}")
                if result.stdout:
                    print(f"📄 stdout: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
                if result.stderr:
                    print(f"⚠️  stderr: {result.stderr}")
                
                # For CLI test execution, return code 100 means tests ran but some failed
                # Return code 0 means tests ran and all passed
                # Only other return codes are actual command failures
                if result.returncode == 0 or result.returncode == 100:
                    # Parse the JSON output
                    print(f"✅ CLI command executed successfully (tests ran with result code {result.returncode}), parsing results...")
                    try:
                        output_data = json.loads(result.stdout)
                        return self._parse_sfdx_test_results(output_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Could not parse JSON output: {e}")
                        print(f"   Raw stdout: {result.stdout}")
                        continue  # Try next command
                else:
                    print(f"⚠️ Command failed with return code {result.returncode}")
                    continue  # Try next command
                
            except subprocess.TimeoutExpired:
                raise Exception(f"Test execution timed out after {request.timeout_minutes} minutes")
            except json.JSONDecodeError as e:
                print(f"⚠️ Could not parse JSON output: {e}")
                print(f"   Raw stdout: {result.stdout}")
            except Exception as e:
                print(f"⚠️ Command execution failed: {e}")
        
        # If all CLI commands failed, raise an exception to trigger API fallback
        raise Exception("All CLI access token command attempts failed")

    def _is_sfdx_available(self) -> bool:
        """Check if Salesforce CLI is available"""
        try:
            result = subprocess.run(['sf', '--version'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            try:
                result = subprocess.run(['sfdx', '--version'], capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except:
                return False

    def _parse_sfdx_test_results(self, sfdx_output: Dict[str, Any]) -> List[TestResult]:
        """Parse sfdx test results into our TestResult format"""
        print("📊 Parsing sfdx test results...")
        
        test_results = []
        
        # Handle CLI output format (different from legacy sfdx format)
        tests_data = sfdx_output.get('result', {}).get('tests', [])
        if not tests_data:
            # Try legacy format
            tests_data = sfdx_output.get('tests', [])
        
        print(f"📋 Found {len(tests_data)} test result records to parse")
        
        for i, test_data in enumerate(tests_data):
            try:
                # Extract class name - CLI uses ApexClass.Name
                apex_class = test_data.get('ApexClass', {})
                class_name = apex_class.get('Name') if apex_class else test_data.get('className', 'Unknown')
                
                # Extract method name - CLI uses MethodName
                method_name = test_data.get('MethodName') or test_data.get('methodName', 'Unknown')
                
                # Extract other fields with proper mapping
                outcome = test_data.get('Outcome') or test_data.get('outcome', 'Unknown')
                message = test_data.get('Message') or test_data.get('message', '')
                stack_trace = test_data.get('StackTrace') or test_data.get('stackTrace', '')
                
                # Handle runtime - CLI uses RunTime in milliseconds
                runtime_ms = test_data.get('RunTime') or test_data.get('runTime', 0)
                runtime_seconds = runtime_ms / 1000.0 if runtime_ms else 0.0
                
                # Create TestResult with our schema field names
                test_result = TestResult(
                    test_class_name=class_name,
                    test_method_name=method_name,
                    outcome=outcome,
                    message=message if message else None,
                    stack_trace=stack_trace if stack_trace else None,
                    time=runtime_seconds if runtime_seconds > 0 else None
                )
                
                test_results.append(test_result)
                
                # Log each test result as we process it
                status_emoji = "✅" if outcome == "Pass" else "❌"
                time_str = f" ({runtime_seconds:.2f}s)" if runtime_seconds > 0 else ""
                print(f"   {status_emoji} {class_name}.{method_name}: {outcome}{time_str}")
                
                # Show error details for failed tests
                if outcome != "Pass" and message:
                    print(f"      💬 Message: {message}")
                if outcome != "Pass" and stack_trace:
                    # Show first line of stack trace
                    first_stack_line = stack_trace.split('\n')[0] if stack_trace else ""
                    if first_stack_line:
                        print(f"      📋 Stack: {first_stack_line}")
                        
            except Exception as e:
                print(f"⚠️ Error parsing test result {i}: {e}")
                print(f"   Raw test data: {test_data}")
                continue
        
        print(f"✅ Successfully parsed {len(test_results)} test results")
        
        # Summary of results
        passed = len([r for r in test_results if r.outcome == "Pass"])
        failed = len([r for r in test_results if r.outcome in ["Fail", "CompileFail"]])
        print(f"📊 TEST SUMMARY: {passed} passed, {failed} failed")
        
        return test_results

    def _execute_tests_with_api(self, request: TestExecutorRequest) -> List[TestResult]:
        """Execute Apex tests using Salesforce API (fallback method)"""
        print("🔄 Executing Apex tests with Salesforce API...")
        
        try:
            # Initialize Salesforce connection
            sf_session = request.salesforce_session
            instance_url = sf_session.instance_url
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            sf = Salesforce(session_id=sf_session.session_id, instance_url=instance_url)
            
            # Verify test classes exist
            self._verify_test_classes_exist_api(sf, request.test_class_names)
            
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
            print(f"❌ Error executing tests with API: {str(e)}")
            raise

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

    def _verify_test_classes_exist_api(self, sf: Salesforce, test_class_names: List[str]):
        """Verify that the test classes exist in the target org using Salesforce API"""
        print("🔍 Verifying test classes exist in target org using Salesforce API...")
        
        try:
            # Query for the test classes
            class_names_str = "', '".join(test_class_names)
            query = f"SELECT Id, Name FROM ApexClass WHERE Name IN ('{class_names_str}')"
            
            results = sf.query(query)
            found_classes = [record['Name'] for record in results['records']]
            missing_classes = [name for name in test_class_names if name not in found_classes]
            
            if missing_classes:
                raise Exception(f"Test classes not found in org: {missing_classes}. Please ensure they are deployed first.")
            
            print(f"✅ All {len(found_classes)} test classes found in org")
            
        except Exception as e:
            print(f"❌ Error verifying test classes: {str(e)}")
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
        print(f"🔗 Test run ID: {test_run_id}")
        
        timeout_time = datetime.now() + timedelta(minutes=timeout_minutes)
        polling_interval = 10  # Poll every 10 seconds
        poll_count = 0
        
        while datetime.now() < timeout_time:
            try:
                poll_count += 1
                # Query test run status
                query = f"SELECT Id, Status, JobName, StartTime, EndTime, CompletedDate FROM AsyncApexJob WHERE Id = '{test_run_id}'"
                job_result = sf.query(query)
                
                if job_result['totalSize'] == 0:
                    raise Exception(f"Test run {test_run_id} not found")
                
                job = job_result['records'][0]
                status = job['Status']
                start_time = job.get('StartTime')
                completed_date = job.get('CompletedDate')
                job_name = job.get('JobName', 'Unknown')
                
                # Provide detailed polling status
                print(f"📊 Poll #{poll_count}: Test run status: {status}")
                if start_time:
                    print(f"   ⏰ Started: {start_time}")
                if completed_date:
                    print(f"   ✅ Completed: {completed_date}")
                print(f"   📋 Job: {job_name}")
                
                if status in ['Completed', 'Failed', 'Aborted']:
                    # Test execution completed, retrieve detailed results
                    print(f"🎯 Test execution finished with status: {status}")
                    if status == 'Completed':
                        print("✅ Retrieving test results...")
                    elif status == 'Failed':
                        print("❌ Test run failed - retrieving available results...")
                    elif status == 'Aborted':
                        print("⚠️ Test run was aborted - retrieving partial results...")
                    
                    return self._retrieve_test_results(sf, test_run_id)
                
                # Still running, provide progress info
                if status == 'Processing':
                    print(f"   🔄 Test execution in progress...")
                elif status == 'Queued':
                    print(f"   ⏳ Test execution queued, waiting for resources...")
                elif status == 'Preparing':
                    print(f"   🔧 Preparing test execution environment...")
                
                # Wait before next poll
                print(f"   💤 Waiting {polling_interval} seconds before next poll...")
                time.sleep(polling_interval)
                
            except Exception as e:
                print(f"⚠️ Error polling test results (attempt {poll_count}): {str(e)}")
                print(f"   🔄 Retrying in {polling_interval} seconds...")
                time.sleep(polling_interval)
        
        # Timeout reached
        raise Exception(f"Test execution timed out after {timeout_minutes} minutes ({poll_count} polls)")

    def _retrieve_test_results(self, sf: Salesforce, test_run_id: str) -> List[TestResult]:
        """Retrieve detailed test results from Salesforce"""
        print("📋 Retrieving detailed test results...")
        
        try:
            # Query individual test results
            query = f"""
                SELECT Id, AsyncApexJobId, MethodName, Outcome, ApexClass.Name, 
                       Message, StackTrace, TestTimestamp, RunTime
                FROM ApexTestResult 
                WHERE AsyncApexJobId = '{test_run_id}'
                ORDER BY ApexClass.Name, MethodName
            """
            
            results = sf.query_all(query)
            test_results = []
            
            print(f"📊 Processing {results['totalSize']} test result records...")
            
            for record in results['records']:
                # Parse runtime if available
                runtime = record.get('RunTime')
                test_time = None
                if runtime:
                    try:
                        test_time = float(runtime) / 1000.0  # Convert milliseconds to seconds
                    except (ValueError, TypeError):
                        test_time = None
                
                test_result = TestResult(
                    test_class_name=record['ApexClass']['Name'],
                    test_method_name=record['MethodName'],
                    outcome=record['Outcome'],
                    message=record.get('Message'),
                    stack_trace=record.get('StackTrace'),
                    time=test_time
                )
                test_results.append(test_result)
                
                # Log each test result as we process it
                status_emoji = "✅" if test_result.outcome == "Pass" else "❌"
                time_str = f" ({test_time:.2f}s)" if test_time else ""
                print(f"   {status_emoji} {test_result.test_class_name}.{test_result.test_method_name}: {test_result.outcome}{time_str}")
                
                # Show error details for failed tests
                if test_result.outcome != "Pass" and test_result.message:
                    print(f"      💬 Message: {test_result.message}")
                if test_result.outcome != "Pass" and test_result.stack_trace:
                    # Show first few lines of stack trace
                    stack_lines = test_result.stack_trace.split('\n')[:3]
                    for line in stack_lines:
                        if line.strip():
                            print(f"      📋 {line.strip()}")
            
            print(f"✅ Retrieved {len(test_results)} test results")
            
            # Summary of results
            passed = len([r for r in test_results if r.outcome == "Pass"])
            failed = len([r for r in test_results if r.outcome in ["Fail", "CompileFail"]])
            print(f"📊 TEST SUMMARY: {passed} passed, {failed} failed")
            
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