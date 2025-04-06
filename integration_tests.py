"""
Integration Tests for Expeta 2.0

This module contains integration tests that verify the end-to-end functionality
of the Expeta 2.0 system, from requirement input through clarification, generation,
and validation.
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from orchestrator.orchestrator import Expeta
from memory.memory_system import MemorySystem
from memory.storage.file_storage import FileStorage
from llm_router.llm_router import LLMRouter
from clarifier.clarifier import Clarifier
from generator.generator import Generator
from validator.validator import Validator

class MockLLMProvider:
    """Mock LLM provider for testing"""
    
    def __init__(self, responses=None):
        """Initialize with optional predefined responses"""
        self.responses = responses or {}
        self.default_response = "This is a mock response"
        self.calls = []
    
    def generate(self, prompt, **kwargs):
        """Generate a response based on the prompt"""
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        
        for key, response in self.responses.items():
            if key.lower() in prompt.lower():
                return response
        
        return self.default_response

class MockLLMRouter:
    """Mock LLM router for testing"""
    
    def __init__(self, responses=None):
        """Initialize with optional predefined responses"""
        self.provider = MockLLMProvider(responses)
        self.calls = []
    
    def generate(self, prompt, **kwargs):
        """Generate a response using the mock provider"""
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        return self.provider.generate(prompt, **kwargs)
    
    def get_provider(self, provider_name=None):
        """Get the mock provider"""
        return self.provider

class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.storage_dir = os.path.join(self.test_dir, "storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.mock_responses = {
            "factorial": json.dumps({
                "top_level_expectation": {
                    "id": "exp-12345",
                    "name": "Factorial Function Implementation",
                    "description": "A function that calculates factorial of positive integers",
                    "acceptance_criteria": [
                        "Function should take an integer as input",
                        "Function should return the factorial result",
                        "Function should handle edge cases (0, 1)",
                        "Function should raise an exception for negative numbers",
                        "Function should raise an exception for non-integers"
                    ],
                    "constraints": [
                        "Must be implemented in Python",
                        "Must be efficient for large numbers",
                        "Must include proper error handling"
                    ]
                },
                "sub_expectations": [
                    {
                        "id": "exp-sub-1",
                        "name": "Input Validation",
                        "parent_id": "exp-12345",
                        "description": "Validate that input is a non-negative integer"
                    },
                    {
                        "id": "exp-sub-2",
                        "name": "Factorial Calculation",
                        "parent_id": "exp-12345",
                        "description": "Calculate factorial using efficient algorithm"
                    },
                    {
                        "id": "exp-sub-3",
                        "name": "Error Handling",
                        "parent_id": "exp-12345",
                        "description": "Handle edge cases and errors appropriately"
                    }
                ]
            }),
            
            "generate": json.dumps({
                "generated_code": {
                    "language": "python",
                    "files": [
                        {
                            "path": "factorial.py",
                            "content": "def factorial(n):\n    \"\"\"Calculate factorial of n.\n    \n    Args:\n        n: A non-negative integer\n        \n    Returns:\n        The factorial of n\n        \n    Raises:\n        TypeError: If n is not an integer\n        ValueError: If n is negative\n    \"\"\"\n    if not isinstance(n, int):\n        raise TypeError('Input must be an integer')\n    if n < 0:\n        raise ValueError('Input must be non-negative')\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
                        },
                        {
                            "path": "test_factorial.py",
                            "content": "import unittest\nfrom factorial import factorial\n\nclass TestFactorial(unittest.TestCase):\n    def test_factorial_zero(self):\n        self.assertEqual(factorial(0), 1)\n        \n    def test_factorial_one(self):\n        self.assertEqual(factorial(1), 1)\n        \n    def test_factorial_positive(self):\n        self.assertEqual(factorial(5), 120)\n        \n    def test_factorial_negative(self):\n        with self.assertRaises(ValueError):\n            factorial(-1)\n            \n    def test_factorial_non_integer(self):\n        with self.assertRaises(TypeError):\n            factorial(1.5)\n\nif __name__ == '__main__':\n    unittest.main()"
                        }
                    ]
                },
                "metadata": {
                    "generation_id": "gen-12345",
                    "expectation_id": "exp-12345",
                    "timestamp": "2023-04-06T12:34:56Z"
                }
            }),
            
            "validate": json.dumps({
                "passed": True,
                "semantic_match": {
                    "match_score": 0.95,
                    "analysis": "The implementation meets all the specified requirements and constraints."
                },
                "test_results": {
                    "pass_rate": 1.0,
                    "tests_passed": 5,
                    "tests_failed": 0,
                    "test_details": [
                        {"name": "test_factorial_zero", "passed": True},
                        {"name": "test_factorial_one", "passed": True},
                        {"name": "test_factorial_positive", "passed": True},
                        {"name": "test_factorial_negative", "passed": True},
                        {"name": "test_factorial_non_integer", "passed": True}
                    ]
                },
                "validation_id": "val-12345",
                "expectation_id": "exp-12345",
                "generation_id": "gen-12345",
                "timestamp": "2023-04-06T12:35:56Z"
            })
        }
        
        self.mock_llm_router = MockLLMRouter(self.mock_responses)
        
        self.storage_provider = FileStorage(base_dir=self.storage_dir)
        
        self.memory_system = MemorySystem(storage_provider=self.storage_provider)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

class TestEndToEndWorkflow(IntegrationTestBase):
    """Test end-to-end workflow from requirement to code generation and validation"""
    
    def test_process_requirement(self):
        """Test processing a requirement through the entire workflow"""
        expeta = Expeta()
        
        expeta._llm_router = self.mock_llm_router
        
        expeta._memory_system = self.memory_system
        
        requirement = """
        Create a function that calculates the factorial of a number.
        The function should handle positive integers and return the factorial result.
        It should raise an exception for negative numbers or non-integers.
        """
        
        with patch('clarifier.clarifier.Clarifier.clarify_requirement') as mock_clarify:
            mock_clarify.return_value = json.loads(self.mock_responses["factorial"])
            
            with patch('generator.generator.Generator.generate') as mock_generate:
                mock_generate.return_value = json.loads(self.mock_responses["generate"])
                
                with patch('validator.validator.Validator.validate') as mock_validate:
                    mock_validate.return_value = json.loads(self.mock_responses["validate"])
                    
                    result = expeta.process_requirement(requirement)
        
        self.assertEqual(result["requirement"], requirement)
        self.assertIn("clarification", result)
        self.assertIn("generation", result)
        self.assertIn("validation", result)
        self.assertTrue(result["success"])
        
        clarification = result["clarification"]
        self.assertEqual(clarification["top_level_expectation"]["name"], "Factorial Function Implementation")
        self.assertEqual(len(clarification["sub_expectations"]), 3)
        
        generation = result["generation"]
        self.assertEqual(generation["generated_code"]["language"], "python")
        self.assertEqual(len(generation["generated_code"]["files"]), 2)
        
        validation = result["validation"]
        self.assertTrue(validation["passed"])
        self.assertAlmostEqual(validation["semantic_match"]["match_score"], 0.95)
        self.assertEqual(validation["test_results"]["pass_rate"], 1.0)
        

class TestComponentInteractions(IntegrationTestBase):
    """Test interactions between components"""
    
    def test_clarifier_to_generator(self):
        """Test interaction between clarifier and generator"""
        clarifier = Clarifier(llm_router=self.mock_llm_router)
        generator = Generator(llm_router=self.mock_llm_router)
        
        requirement = """
        Create a function that calculates the factorial of a number.
        """
        
        with patch.object(clarifier, 'clarify_requirement') as mock_clarify:
            mock_clarify.return_value = json.loads(self.mock_responses["factorial"])
            
            clarification = clarifier.clarify_requirement(requirement)
            
            with patch.object(generator, 'generate') as mock_generate:
                mock_generate.return_value = json.loads(self.mock_responses["generate"])
                
                generation = generator.generate(clarification["top_level_expectation"])
        
        self.assertEqual(generation["generated_code"]["language"], "python")
        self.assertEqual(len(generation["generated_code"]["files"]), 2)
        
        factorial_file = next(f for f in generation["generated_code"]["files"] if f["path"] == "factorial.py")
        self.assertIn("def factorial(n):", factorial_file["content"])
        
        test_file = next(f for f in generation["generated_code"]["files"] if f["path"] == "test_factorial.py")
        self.assertIn("class TestFactorial(unittest.TestCase):", test_file["content"])
    
    def test_generator_to_validator(self):
        """Test interaction between generator and validator"""
        generator = Generator(llm_router=self.mock_llm_router)
        validator = Validator(llm_router=self.mock_llm_router)
        
        expectation = {
            "id": "exp-12345",
            "name": "Factorial Function Implementation",
            "description": "A function that calculates factorial of positive integers"
        }
        
        with patch.object(generator, 'generate') as mock_generate:
            mock_generate.return_value = json.loads(self.mock_responses["generate"])
            
            generation = generator.generate(expectation)
            
            with patch.object(validator, 'validate') as mock_validate:
                mock_validate.return_value = json.loads(self.mock_responses["validate"])
                
                validation = validator.validate(generation["generated_code"], expectation)
        
        self.assertTrue(validation["passed"])
        self.assertAlmostEqual(validation["semantic_match"]["match_score"], 0.95)
        self.assertEqual(validation["test_results"]["pass_rate"], 1.0)

class TestMemorySystem(IntegrationTestBase):
    """Test memory system functionality"""
    
    def test_memory_persistence(self):
        """Test memory system persistence"""
        expectation = {
            "id": "exp-test-123",
            "name": "Test Expectation",
            "description": "This is a test expectation"
        }
        
        generation = {
            "id": "gen-test-123",
            "expectation_id": "exp-test-123",
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "test.py",
                        "content": "def test_function():\n    return 'test'"
                    }
                ]
            }
        }
        
        validation = {
            "id": "val-test-123",
            "expectation_id": "exp-test-123",
            "generation_id": "gen-test-123",
            "passed": True
        }
        
        self.memory_system.record_expectations(expectation)
        self.memory_system.record_generation(generation)
        self.memory_system.record_validation(validation)
        
        retrieved_expectation = self.memory_system.get_expectation("exp-test-123")
        retrieved_generation = self.memory_system.get_code_for_expectation("exp-test-123")
        retrieved_validation = self.memory_system.get_validation_results(expectation_id="exp-test-123")
        
        self.assertTrue(retrieved_expectation)
        self.assertEqual(retrieved_expectation[0]["name"], "Test Expectation")
        
        self.assertTrue(retrieved_generation)
        self.assertEqual(retrieved_generation[0]["id"], "gen-test-123")
        
        self.assertTrue(retrieved_validation)
        self.assertEqual(retrieved_validation[0]["id"], "val-test-123")
        self.assertTrue(retrieved_validation[0]["passed"])

class TestErrorHandling(IntegrationTestBase):
    """Test error handling in the workflow"""
    
    def test_invalid_requirement(self):
        """Test handling of invalid requirement"""
        expeta = Expeta()
        
        expeta._llm_router = self.mock_llm_router
        
        expeta._memory_system = self.memory_system
        
        requirement = ""
        
        with patch('clarifier.clarifier.Clarifier.clarify_requirement') as mock_clarify:
            mock_clarify.side_effect = ValueError("Requirement cannot be empty")
            
            with self.assertRaises(ValueError):
                expeta.process_requirement(requirement)
    
    def test_failed_validation(self):
        """Test handling of failed validation"""
        expeta = Expeta()
        
        expeta._llm_router = self.mock_llm_router
        
        expeta._memory_system = self.memory_system
        
        requirement = """
        Create a function that calculates the factorial of a number.
        """
        
        failed_validation = {
            "passed": False,
            "semantic_match": {
                "match_score": 0.5,
                "analysis": "The implementation does not meet all requirements."
            },
            "test_results": {
                "pass_rate": 0.6,
                "tests_passed": 3,
                "tests_failed": 2,
                "test_details": [
                    {"name": "test_factorial_zero", "passed": True},
                    {"name": "test_factorial_one", "passed": True},
                    {"name": "test_factorial_positive", "passed": True},
                    {"name": "test_factorial_negative", "passed": False},
                    {"name": "test_factorial_non_integer", "passed": False}
                ]
            }
        }
        
        with patch('clarifier.clarifier.Clarifier.clarify_requirement') as mock_clarify:
            mock_clarify.return_value = json.loads(self.mock_responses["factorial"])
            
            with patch('generator.generator.Generator.generate') as mock_generate:
                mock_generate.return_value = json.loads(self.mock_responses["generate"])
                
                with patch('validator.validator.Validator.validate') as mock_validate:
                    mock_validate.return_value = failed_validation
                    
                    result = expeta.process_requirement(requirement)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["validation"]["passed"], False)
        self.assertEqual(result["validation"]["test_results"]["pass_rate"], 0.6)

def run_tests():
    """Run all integration tests"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestEndToEndWorkflow))
    test_suite.addTest(unittest.makeSuite(TestComponentInteractions))
    test_suite.addTest(unittest.makeSuite(TestMemorySystem))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    return test_result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    
    sys.exit(0 if success else 1)
