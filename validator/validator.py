"""
Validator Module for Expeta 2.0

This module validates generated code against semantic expectations.
"""

class Validator:
    """Validator, checks if code meets expectations"""

    def __init__(self, llm_router=None, test_system=None):
        """Initialize with optional dependencies
        
        Args:
            llm_router: Optional LLM router. If not provided, default router will be created.
            test_system: Optional test system. If not provided, default test system will be created.
        """
        self.llm_router = llm_router or self._create_default_llm_router()
        self.test_system = test_system or self._create_default_test_system()
        self._validation_results = []

    def validate(self, code, expectation):
        """Validate if code meets expectation
        
        Args:
            code: Code dictionary to validate
            expectation: Expectation dictionary
            
        Returns:
            Dictionary with validation results
        """
        analysis = self._analyze_code(code)
        semantic_match = self._evaluate_semantic_match(code, expectation)
        tests = self._generate_tests(code, expectation, analysis)
        test_results = self._run_tests(code, tests)

        result = {
            "code_id": self._generate_code_id(code),
            "expectation_id": expectation.get("id"),
            "semantic_match": semantic_match,
            "test_results": test_results,
            "passed": semantic_match.get("match_score", 0) > 0.8 and test_results.get("pass_rate", 0) > 0.9
        }

        self._validation_results.append(result)

        return result

    def sync_to_memory(self, memory_system):
        """Sync validation results to memory system (delayed call)
        
        Args:
            memory_system: Memory system to sync to
            
        Returns:
            Dictionary with sync results
        """
        for result in self._validation_results:
            memory_system.record_validation(result)

        synced_count = len(self._validation_results)
        self._validation_results = []

        return {"synced_count": synced_count}
        
    def _create_default_llm_router(self):
        """Create default LLM router
        
        Returns:
            Default LLM router instance
        """
        from ..llm_router.llm_router import LLMRouter
        return LLMRouter()
        
    def _create_default_test_system(self):
        """Create default test system
        
        Returns:
            Default test system instance
        """
        from .test_system import TestSystem
        return TestSystem()
        
    def _analyze_code(self, code):
        """Analyze code structure and quality
        
        Args:
            code: Code dictionary to analyze
            
        Returns:
            Analysis results dictionary
        """
        prompt = self._create_code_analysis_prompt(code)
        
        response = self.llm_router.generate(prompt)
        
        analysis = self._parse_analysis_from_response(response)
        
        return analysis
        
    def _evaluate_semantic_match(self, code, expectation):
        """Evaluate semantic match between code and expectation
        
        Args:
            code: Code dictionary
            expectation: Expectation dictionary
            
        Returns:
            Semantic match evaluation dictionary
        """
        prompt = self._create_semantic_match_prompt(code, expectation)
        
        response = self.llm_router.generate(prompt)
        
        semantic_match = self._parse_semantic_match_from_response(response)
        
        return semantic_match
        
    def _generate_tests(self, code, expectation, analysis):
        """Generate tests for code based on expectation
        
        Args:
            code: Code dictionary
            expectation: Expectation dictionary
            analysis: Code analysis results
            
        Returns:
            Generated tests dictionary
        """
        prompt = self._create_test_generation_prompt(code, expectation, analysis)
        
        response = self.llm_router.generate(prompt)
        
        tests = self._parse_tests_from_response(response)
        
        return tests
        
    def _run_tests(self, code, tests):
        """Run tests against code
        
        Args:
            code: Code dictionary
            tests: Tests dictionary
            
        Returns:
            Test results dictionary
        """
        test_results = self.test_system.run_tests(code, tests)
        
        return test_results
        
    def _create_code_analysis_prompt(self, code):
        """Create prompt for code analysis
        
        Args:
            code: Code dictionary
            
        Returns:
            Prompt text
        """
        import json
        
        code_json = json.dumps(code, indent=2)
        
        return f"""
        You are an expert code reviewer. Your task is to analyze the following code for structure, quality, and potential issues.
        
        Code:
        {code_json}
        
        Please provide a detailed analysis of the code, including:
        1. Overall structure and organization
        2. Code quality and readability
        3. Potential issues or bugs
        4. Adherence to best practices
        5. Performance considerations
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "structure_score": 0-10,
            "quality_score": 0-10,
            "issues": [
                {{
                    "type": "bug/performance/readability/etc.",
                    "description": "Description of the issue",
                    "severity": "high/medium/low",
                    "location": "file/line number"
                }},
                ...
            ],
            "strengths": [
                "Strength 1",
                "Strength 2",
                ...
            ],
            "summary": "Overall summary of the code analysis"
        }}
        ```
        """
        
    def _create_semantic_match_prompt(self, code, expectation):
        """Create prompt for semantic match evaluation
        
        Args:
            code: Code dictionary
            expectation: Expectation dictionary
            
        Returns:
            Prompt text
        """
        import json
        
        code_json = json.dumps(code, indent=2)
        expectation_json = json.dumps(expectation, indent=2)
        
        return f"""
        You are an expert software evaluator. Your task is to evaluate how well the provided code meets the semantic expectations.
        
        Code:
        {code_json}
        
        Expectation:
        {expectation_json}
        
        Please evaluate how well the code implements the semantic expectations, focusing on:
        1. Functional completeness (does it implement all required functionality?)
        2. Semantic correctness (does it correctly implement the expected behavior?)
        3. Constraint adherence (does it respect all constraints?)
        4. Acceptance criteria fulfillment (does it meet all acceptance criteria?)
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "match_score": 0.0-1.0,
            "functional_completeness": 0.0-1.0,
            "semantic_correctness": 0.0-1.0,
            "constraint_adherence": 0.0-1.0,
            "acceptance_criteria_fulfillment": 0.0-1.0,
            "missing_elements": [
                {{
                    "type": "functionality/constraint/criterion",
                    "description": "Description of the missing element"
                }},
                ...
            ],
            "summary": "Overall summary of the semantic match evaluation"
        }}
        ```
        """
        
    def _create_test_generation_prompt(self, code, expectation, analysis):
        """Create prompt for test generation
        
        Args:
            code: Code dictionary
            expectation: Expectation dictionary
            analysis: Code analysis results
            
        Returns:
            Prompt text
        """
        import json
        
        code_json = json.dumps(code, indent=2)
        expectation_json = json.dumps(expectation, indent=2)
        analysis_json = json.dumps(analysis, indent=2)
        
        return f"""
        You are an expert test engineer. Your task is to generate comprehensive tests for the provided code based on the expectations and code analysis.
        
        Code:
        {code_json}
        
        Expectation:
        {expectation_json}
        
        Code Analysis:
        {analysis_json}
        
        Please generate a comprehensive test suite that verifies:
        1. Functional correctness (does it work as expected?)
        2. Edge cases and error handling
        3. Performance under expected load
        4. Adherence to all acceptance criteria
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "language": "python/javascript/etc.",
            "test_files": [
                {{
                    "path": "path/to/test_file.ext",
                    "content": "test file content"
                }},
                ...
            ],
            "test_cases": [
                {{
                    "name": "Test case name",
                    "description": "Description of what is being tested",
                    "type": "unit/integration/performance/etc.",
                    "expected_result": "Expected result of the test"
                }},
                ...
            ],
            "setup_instructions": "Instructions for setting up the test environment"
        }}
        ```
        """
        
    def _parse_analysis_from_response(self, response):
        """Parse code analysis from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Analysis results dictionary
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            analysis = json.loads(json_content)
        except Exception:
            analysis = {
                "structure_score": 5,
                "quality_score": 5,
                "issues": [],
                "strengths": [],
                "summary": "Failed to parse analysis results"
            }
            
        return analysis
        
    def _parse_semantic_match_from_response(self, response):
        """Parse semantic match evaluation from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Semantic match evaluation dictionary
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            semantic_match = json.loads(json_content)
        except Exception:
            semantic_match = {
                "match_score": 0.5,
                "functional_completeness": 0.5,
                "semantic_correctness": 0.5,
                "constraint_adherence": 0.5,
                "acceptance_criteria_fulfillment": 0.5,
                "missing_elements": [],
                "summary": "Failed to parse semantic match evaluation"
            }
            
        return semantic_match
        
    def _parse_tests_from_response(self, response):
        """Parse tests from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Tests dictionary
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            tests = json.loads(json_content)
        except Exception:
            tests = {
                "language": "python",
                "test_files": [],
                "test_cases": [],
                "setup_instructions": "Failed to parse test generation results"
            }
            
        return tests
        
    def _generate_code_id(self, code):
        """Generate unique ID for code
        
        Args:
            code: Code dictionary
            
        Returns:
            Unique ID string
        """
        import hashlib
        import json
        
        code_str = json.dumps(code, sort_keys=True)
        
        hash_obj = hashlib.md5(code_str.encode())
        
        return f"code-{hash_obj.hexdigest()[:8]}"
