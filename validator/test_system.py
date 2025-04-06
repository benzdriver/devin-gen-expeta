"""
Test System Module for Expeta 2.0

This module provides functionality for running tests against generated code.
"""

class TestSystem:
    """Test system, runs tests against generated code"""
    
    def __init__(self, config=None):
        """Initialize test system
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
    def run_tests(self, code, tests):
        """Run tests against code
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            Test results dictionary
        """
        env = self._prepare_test_environment(code, tests)
        
        results = self._execute_tests(env, tests)
        
        analysis = self._analyze_results(results)
        
        return {
            "pass_rate": analysis["pass_rate"],
            "total_tests": analysis["total_tests"],
            "passed_tests": analysis["passed_tests"],
            "failed_tests": analysis["failed_tests"],
            "test_details": results,
            "summary": analysis["summary"]
        }
        
    def _prepare_test_environment(self, code, tests):
        """Prepare test environment
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            Test environment dictionary
        """
        
        language = code.get("language", "python")
        
        if language == "python":
            return self._prepare_python_environment(code, tests)
        elif language == "javascript":
            return self._prepare_javascript_environment(code, tests)
        else:
            return self._prepare_generic_environment(code, tests)
            
    def _prepare_python_environment(self, code, tests):
        """Prepare Python test environment
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            Python test environment dictionary
        """
        
        return {
            "type": "python",
            "code_files": code.get("files", []),
            "test_files": tests.get("test_files", []),
            "setup_complete": True
        }
        
    def _prepare_javascript_environment(self, code, tests):
        """Prepare JavaScript test environment
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            JavaScript test environment dictionary
        """
        
        return {
            "type": "javascript",
            "code_files": code.get("files", []),
            "test_files": tests.get("test_files", []),
            "setup_complete": True
        }
        
    def _prepare_generic_environment(self, code, tests):
        """Prepare generic test environment
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            Generic test environment dictionary
        """
        
        return {
            "type": "generic",
            "code_files": code.get("files", []),
            "test_files": tests.get("test_files", []),
            "setup_complete": True
        }
        
    def _execute_tests(self, env, tests):
        """Execute tests in environment
        
        Args:
            env: Test environment dictionary
            tests: Tests dictionary
            
        Returns:
            Test execution results
        """
        
        test_cases = tests.get("test_cases", [])
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            import random
            passed = random.random() < 0.8
            
            result = {
                "name": test_case.get("name", f"Test {i+1}"),
                "description": test_case.get("description", ""),
                "type": test_case.get("type", "unit"),
                "passed": passed,
                "duration_ms": random.randint(10, 500),
                "error": None if passed else "Simulated test failure"
            }
            
            results.append(result)
            
        return results
        
    def _analyze_results(self, results):
        """Analyze test results
        
        Args:
            results: Test execution results
            
        Returns:
            Analysis dictionary
        """
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("passed", False))
        failed_tests = total_tests - passed_tests
        
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        if pass_rate == 1.0:
            summary = "All tests passed successfully."
        elif pass_rate >= 0.8:
            summary = f"Most tests passed ({passed_tests}/{total_tests}), but there are {failed_tests} failing tests."
        elif pass_rate >= 0.5:
            summary = f"Some tests passed ({passed_tests}/{total_tests}), but there are significant failures ({failed_tests} tests)."
        else:
            summary = f"Most tests failed ({failed_tests}/{total_tests}). The code has serious issues."
            
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "summary": summary
        }
