"""
Unit tests for GraphQL Access Layer
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.graphql.src.api import app

class TestGraphQL(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        from starlette.testclient import TestClient
        self.client = TestClient(app)
    
    def test_graphql_endpoint(self):
        """Test that the GraphQL endpoint is accessible"""
        response = self.client.get("/graphql")
        self.assertEqual(response.status_code, 200)
    
    def test_schema_introspection(self):
        """Test GraphQL schema introspection"""
        query = """
        {
          __schema {
            queryType {
              name
            }
            types {
              name
              kind
            }
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("__schema", data["data"])
        self.assertIn("queryType", data["data"]["__schema"])
        self.assertIn("types", data["data"]["__schema"])
    
    @patch('access.graphql.src.api.expeta')
    def test_query_expectation(self, mock_expeta):
        """Test querying an expectation"""
        mock_memory = MagicMock()
        mock_expeta.memory_system = mock_memory
        
        mock_expectation = {
            "id": "exp-12345678",
            "name": "User Authentication",
            "description": "A system for user authentication",
            "acceptance_criteria": ["Must support login", "Must support registration"]
        }
        mock_memory.get_expectation.return_value = mock_expectation
        
        query = """
        {
          expectation(id: "exp-12345678") {
            id
            name
            description
            acceptanceCriteria
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("expectation", data["data"])
        self.assertEqual(data["data"]["expectation"]["id"], "exp-12345678")
        self.assertEqual(data["data"]["expectation"]["name"], "User Authentication")
        mock_memory.get_expectation.assert_called_once_with("exp-12345678")
    
    @patch('access.graphql.src.api.expeta')
    def test_query_expectations(self, mock_expeta):
        """Test querying multiple expectations"""
        mock_memory = MagicMock()
        mock_expeta.memory_system = mock_memory
        
        mock_expectations = [
            {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            },
            {
                "id": "exp-87654321",
                "name": "Data Validation",
                "description": "A system for data validation"
            }
        ]
        mock_memory.get_expectations.return_value = mock_expectations
        
        query = """
        {
          expectations {
            id
            name
            description
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("expectations", data["data"])
        self.assertEqual(len(data["data"]["expectations"]), 2)
        self.assertEqual(data["data"]["expectations"][0]["id"], "exp-12345678")
        self.assertEqual(data["data"]["expectations"][1]["id"], "exp-87654321")
        mock_memory.get_expectations.assert_called_once()
    
    @patch('access.graphql.src.api.expeta')
    def test_mutation_process_requirement(self, mock_expeta):
        """Test processing a requirement mutation"""
        mock_result = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_requirement.return_value = mock_result
        
        mutation = """
        mutation {
          processRequirement(text: "Create a user authentication system") {
            requirement
            success
            clarification {
              topLevelExpectation {
                name
              }
            }
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": mutation}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("processRequirement", data["data"])
        self.assertEqual(data["data"]["processRequirement"]["requirement"], "Create a user authentication system")
        self.assertEqual(data["data"]["processRequirement"]["success"], True)
        mock_expeta.process_requirement.assert_called_once_with("Create a user authentication system")
    
    @patch('access.graphql.src.api.expeta')
    def test_mutation_clarify_requirement(self, mock_expeta):
        """Test clarifying a requirement mutation"""
        mock_clarifier = MagicMock()
        mock_expeta.clarifier = mock_clarifier
        
        mock_result = {
            "top_level_expectation": {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            },
            "sub_expectations": []
        }
        mock_clarifier.clarify_requirement.return_value = mock_result
        
        mutation = """
        mutation {
          clarifyRequirement(text: "Create a user authentication system") {
            topLevelExpectation {
              id
              name
              description
            }
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": mutation}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("clarifyRequirement", data["data"])
        self.assertEqual(data["data"]["clarifyRequirement"]["topLevelExpectation"]["id"], "exp-12345678")
        mock_clarifier.clarify_requirement.assert_called_once_with("Create a user authentication system")
        mock_clarifier.sync_to_memory.assert_called_once()
    
    @patch('access.graphql.src.api.expeta')
    def test_mutation_generate_code(self, mock_expeta):
        """Test generating code mutation"""
        mock_generator = MagicMock()
        mock_expeta.generator = mock_generator
        
        mock_result = {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    pass"
                    }
                ]
            }
        }
        mock_generator.generate.return_value = mock_result
        
        mutation = """
        mutation {
          generateCode(expectation: {
            id: "exp-12345678",
            name: "User Authentication",
            description: "A system for user authentication"
          }) {
            generatedCode {
              language
              files {
                path
                content
              }
            }
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": mutation}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("generateCode", data["data"])
        self.assertEqual(data["data"]["generateCode"]["generatedCode"]["language"], "python")
        mock_generator.generate.assert_called_once()
        mock_generator.sync_to_memory.assert_called_once()
    
    @patch('access.graphql.src.api.expeta')
    def test_mutation_validate_code(self, mock_expeta):
        """Test validating code mutation"""
        mock_validator = MagicMock()
        mock_expeta.validator = mock_validator
        
        mock_result = {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        }
        mock_validator.validate.return_value = mock_result
        
        mutation = """
        mutation {
          validateCode(
            code: {
              language: "python",
              files: [
                {
                  path: "auth/user.py",
                  content: "class User:\\n    pass"
                }
              ]
            },
            expectation: {
              id: "exp-12345678",
              name: "User Authentication"
            }
          ) {
            passed
            semanticMatch {
              matchScore
            }
            testResults {
              passRate
            }
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": mutation}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("validateCode", data["data"])
        self.assertEqual(data["data"]["validateCode"]["passed"], True)
        mock_validator.validate.assert_called_once()
        mock_validator.sync_to_memory.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling for invalid queries"""
        response = self.client.post(
            "/graphql",
            json={"query": "invalid query"}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)
        
        query = """
        {
          nonExistentField {
            id
          }
        }
        """
        
        response = self.client.post(
            "/graphql",
            json={"query": query}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

if __name__ == "__main__":
    unittest.main()
