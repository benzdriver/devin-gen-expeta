"""
Unit tests for REST API Access Layer
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.rest_api.src.api import app

class TestRESTAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.json())
        self.assertIn("version", response.json())
        self.assertIn("description", response.json())
    
    @patch('access.rest_api.src.api.expeta')
    def test_process_requirement(self, mock_expeta):
        """Test processing a requirement"""
        mock_result = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_requirement.return_value = mock_result
        
        response = self.client.post(
            "/process",
            json={"text": "Create a user authentication system"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_result)
        mock_expeta.process_requirement.assert_called_once_with("Create a user authentication system")
    
    @patch('access.rest_api.src.api.expeta')
    def test_process_expectation(self, mock_expeta):
        """Test processing an expectation"""
        mock_result = {
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_expectation.return_value = mock_result
        
        expectation = {
            "name": "User Authentication",
            "description": "A system for user authentication",
            "acceptance_criteria": ["Must support login", "Must support registration"]
        }
        
        response = self.client.post(
            "/process/expectation",
            json={"expectation": expectation}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_result)
        mock_expeta.process_expectation.assert_called_once()
    
    @patch('access.rest_api.src.api.expeta')
    def test_clarify_endpoint(self, mock_expeta):
        """Test the clarify endpoint"""
        mock_clarifier = MagicMock()
        mock_expeta.clarifier = mock_clarifier
        mock_clarifier.clarify_requirement.return_value = {
            "top_level_expectation": {"name": "User Authentication"}
        }
        
        response = self.client.post(
            "/clarify",
            json={"text": "Create a user authentication system"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"top_level_expectation": {"name": "User Authentication"}})
        mock_clarifier.clarify_requirement.assert_called_once_with("Create a user authentication system")
        mock_clarifier.sync_to_memory.assert_called_once()
    
    @patch('access.rest_api.src.api.expeta')
    def test_generate_endpoint(self, mock_expeta):
        """Test the generate endpoint"""
        mock_generator = MagicMock()
        mock_expeta.generator = mock_generator
        mock_generator.generate.return_value = {
            "generated_code": {"files": []}
        }
        
        expectation = {
            "name": "User Authentication",
            "description": "A system for user authentication"
        }
        
        response = self.client.post(
            "/generate",
            json=expectation
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"generated_code": {"files": []}})
        mock_generator.generate.assert_called_once_with(expectation)
        mock_generator.sync_to_memory.assert_called_once()
    
    @patch('access.rest_api.src.api.expeta')
    def test_validate_endpoint(self, mock_expeta):
        """Test the validate endpoint"""
        mock_validator = MagicMock()
        mock_expeta.validator = mock_validator
        mock_validator.validate.return_value = {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        }
        
        code = {"language": "python", "files": []}
        expectation = {"name": "User Authentication"}
        
        response = self.client.post(
            "/validate",
            json={"code": code, "expectation": expectation}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        })
        mock_validator.validate.assert_called_once_with(code, expectation)
        mock_validator.sync_to_memory.assert_called_once()
    
    @patch('access.rest_api.src.api.expeta')
    def test_memory_endpoints(self, mock_expeta):
        """Test the memory endpoints"""
        mock_memory = MagicMock()
        mock_expeta.memory_system = mock_memory
        
        mock_memory.get_expectation.return_value = {"name": "User Authentication"}
        response = self.client.get("/memory/expectations/exp-12345678")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"name": "User Authentication"})
        
        mock_memory.get_code_for_expectation.return_value = {"generated_code": {"files": []}}
        response = self.client.get("/memory/generations/exp-12345678")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"generated_code": {"files": []}})
        
        mock_memory.get_validation_results.return_value = {"passed": True}
        response = self.client.get("/memory/validations/exp-12345678")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"passed": True})
    
    def test_protected_route_without_auth(self):
        """Test protected route without authentication"""
        response = self.client.get("/protected")
        self.assertEqual(response.status_code, 403)
    
    def test_protected_route_with_auth(self):
        """Test protected route with authentication"""
        response = self.client.get(
            "/protected",
            headers={"Authorization": "Bearer valid-token"}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        response = self.client.post(
            "/process",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 422)
        
        response = self.client.post(
            "/process",
            json={"invalid_field": "data"}
        )
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
