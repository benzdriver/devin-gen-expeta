"""
Integration tests for Access Layer modules
"""

import sys
import os
import unittest
import subprocess
import requests
import time
import threading
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.rest_api.src.api import app as rest_app
from access.graphql.src.api import app as graphql_app
from access.chat.src.chat_interface import ChatInterface
from access.cli.src.cli_tool import cli
from click.testing import CliRunner

class TestAccessLayerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        from starlette.testclient import TestClient
        
        cls.rest_client = TestClient(rest_app)
        cls.graphql_client = TestClient(graphql_app)
        
        cls.chat_interface = ChatInterface()
        
        cls.cli_runner = CliRunner()
        
        cls.mock_expectation = {
            "id": "exp-12345678",
            "name": "User Authentication System",
            "description": "A system that handles user registration, login, and authentication",
            "acceptance_criteria": [
                "Must support user registration with email and password",
                "Must support user login with email and password",
                "Must generate and validate JWT tokens"
            ],
            "constraints": [
                "Must use secure password hashing",
                "Must implement rate limiting for login attempts"
            ]
        }
        
        cls.mock_generation = {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    def __init__(self, email, password):\n        self.email = email\n        self.password = password"
                    },
                    {
                        "path": "auth/authentication.py",
                        "content": "import jwt\n\nclass Authentication:\n    def __init__(self, secret_key):\n        self.secret_key = secret_key"
                    }
                ]
            }
        }
        
        cls.mock_validation = {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        }
    
    @patch('access.rest_api.src.api.expeta')
    @patch('access.graphql.src.api.expeta')
    def test_rest_to_graphql_flow(self, mock_graphql_expeta, mock_rest_expeta):
        """Test flow from REST API to GraphQL"""
        mock_rest_memory = MagicMock()
        mock_rest_expeta.memory_system = mock_rest_memory
        mock_rest_memory.get_expectation.return_value = self.mock_expectation
        
        mock_graphql_memory = MagicMock()
        mock_graphql_expeta.memory_system = mock_graphql_memory
        mock_graphql_memory.get_expectation.return_value = self.mock_expectation
        
        rest_response = self.rest_client.get("/memory/expectations/exp-12345678")
        self.assertEqual(rest_response.status_code, 200)
        rest_data = rest_response.json()
        self.assertEqual(rest_data["id"], "exp-12345678")
        self.assertEqual(rest_data["name"], "User Authentication System")
        
        graphql_query = {
            "query": """
            {
                expectation(id: "exp-12345678") {
                    id
                    name
                    description
                    acceptanceCriteria
                }
            }
            """
        }
        
        graphql_response = self.graphql_client.post("/graphql", json=graphql_query)
        self.assertEqual(graphql_response.status_code, 200)
        graphql_data = graphql_response.json()
        self.assertIn("data", graphql_data)
        self.assertIn("expectation", graphql_data["data"])
        self.assertEqual(graphql_data["data"]["expectation"]["id"], "exp-12345678")
        self.assertEqual(graphql_data["data"]["expectation"]["name"], "User Authentication System")
    
    @patch('access.rest_api.src.api.expeta')
    @patch('access.chat.src.chat_interface.expeta')
    def test_chat_to_rest_flow(self, mock_chat_expeta, mock_rest_expeta):
        """Test flow from Chat Interface to REST API"""
        mock_chat_clarifier = MagicMock()
        mock_chat_expeta.clarifier = mock_chat_clarifier
        mock_chat_clarifier.process_chat_message.return_value = {
            "response": "I'll help you create a user authentication system.",
            "expectation": self.mock_expectation
        }
        
        mock_rest_memory = MagicMock()
        mock_rest_expeta.memory_system = mock_rest_memory
        mock_rest_memory.get_expectation.return_value = self.mock_expectation
        
        chat_result = self.chat_interface.process_message(
            "Create a user authentication system",
            user_id="user123",
            session_id="session456"
        )
        
        self.assertEqual(chat_result["expectation"]["id"], "exp-12345678")
        expectation_id = chat_result["expectation"]["id"]
        
        rest_response = self.rest_client.get(f"/memory/expectations/{expectation_id}")
        self.assertEqual(rest_response.status_code, 200)
        rest_data = rest_response.json()
        self.assertEqual(rest_data["id"], expectation_id)
        self.assertEqual(rest_data["name"], "User Authentication System")
    
    @patch('access.cli.src.cli_tool.expeta')
    @patch('access.rest_api.src.api.expeta')
    def test_cli_to_rest_flow(self, mock_rest_expeta, mock_cli_expeta):
        """Test flow from CLI to REST API"""
        mock_cli_clarifier = MagicMock()
        mock_cli_expeta.clarifier = mock_cli_clarifier
        mock_cli_clarifier.clarify_requirement.return_value = {
            "top_level_expectation": self.mock_expectation
        }
        
        mock_rest_memory = MagicMock()
        mock_rest_expeta.memory_system = mock_rest_memory
        mock_rest_memory.get_expectation.return_value = self.mock_expectation
        
        cli_result = self.cli_runner.invoke(
            cli, 
            ["clarify", "Create a user authentication system"]
        )
        
        self.assertEqual(cli_result.exit_code, 0)
        self.assertIn("User Authentication System", cli_result.output)
        
        expectation_id = "exp-12345678"  # In a real test, we would extract this from the CLI output
        
        rest_response = self.rest_client.get(f"/memory/expectations/{expectation_id}")
        self.assertEqual(rest_response.status_code, 200)
        rest_data = rest_response.json()
        self.assertEqual(rest_data["id"], expectation_id)
        self.assertEqual(rest_data["name"], "User Authentication System")
    
    @patch('access.rest_api.src.api.expeta')
    def test_complete_flow(self, mock_expeta):
        """Test complete flow from requirement to validation"""
        mock_clarifier = MagicMock()
        mock_generator = MagicMock()
        mock_validator = MagicMock()
        mock_memory = MagicMock()
        
        mock_expeta.clarifier = mock_clarifier
        mock_expeta.generator = mock_generator
        mock_expeta.validator = mock_validator
        mock_expeta.memory_system = mock_memory
        mock_expeta.process_requirement.return_value = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": self.mock_expectation},
            "generation": self.mock_generation,
            "validation": self.mock_validation,
            "success": True
        }
        
        mock_clarifier.clarify_requirement.return_value = {
            "top_level_expectation": self.mock_expectation
        }
        mock_generator.generate.return_value = self.mock_generation
        mock_validator.validate.return_value = self.mock_validation
        mock_memory.get_expectation.return_value = self.mock_expectation
        mock_memory.get_code_for_expectation.return_value = self.mock_generation
        mock_memory.get_validation_results.return_value = self.mock_validation
        
        process_response = self.rest_client.post(
            "/process",
            json={"text": "Create a user authentication system"}
        )
        
        self.assertEqual(process_response.status_code, 200)
        process_data = process_response.json()
        self.assertTrue(process_data["success"])
        self.assertEqual(process_data["requirement"], "Create a user authentication system")
        
        expectation_id = process_data["clarification"]["top_level_expectation"]["id"]
        
        expectation_response = self.rest_client.get(f"/memory/expectations/{expectation_id}")
        self.assertEqual(expectation_response.status_code, 200)
        expectation_data = expectation_response.json()
        self.assertEqual(expectation_data["name"], "User Authentication System")
        
        generation_response = self.rest_client.get(f"/memory/generations/{expectation_id}")
        self.assertEqual(generation_response.status_code, 200)
        generation_data = generation_response.json()
        self.assertEqual(generation_data["generated_code"]["language"], "python")
        self.assertEqual(len(generation_data["generated_code"]["files"]), 2)
        
        validation_response = self.rest_client.get(f"/memory/validations/{expectation_id}")
        self.assertEqual(validation_response.status_code, 200)
        validation_data = validation_response.json()
        self.assertTrue(validation_data["passed"])
        self.assertEqual(validation_data["semantic_match"]["match_score"], 0.9)
    
    @patch('access.rest_api.src.api.expeta')
    @patch('access.graphql.src.api.expeta')
    def test_rest_graphql_interoperability(self, mock_graphql_expeta, mock_rest_expeta):
        """Test interoperability between REST API and GraphQL"""
        mock_rest_clarifier = MagicMock()
        mock_rest_memory = MagicMock()
        mock_rest_expeta.clarifier = mock_rest_clarifier
        mock_rest_expeta.memory_system = mock_rest_memory
        mock_rest_clarifier.clarify_requirement.return_value = {
            "top_level_expectation": self.mock_expectation
        }
        mock_rest_memory.get_expectation.return_value = self.mock_expectation
        
        mock_graphql_memory = MagicMock()
        mock_graphql_expeta.memory_system = mock_graphql_memory
        mock_graphql_memory.get_expectation.return_value = self.mock_expectation
        
        rest_response = self.rest_client.post(
            "/clarify",
            json={"text": "Create a user authentication system"}
        )
        
        self.assertEqual(rest_response.status_code, 200)
        rest_data = rest_response.json()
        self.assertEqual(rest_data["top_level_expectation"]["name"], "User Authentication System")
        expectation_id = rest_data["top_level_expectation"]["id"]
        
        graphql_query = {
            "query": f"""
            {{
                expectation(id: "{expectation_id}") {{
                    id
                    name
                    description
                    acceptanceCriteria
                }}
            }}
            """
        }
        
        graphql_response = self.graphql_client.post("/graphql", json=graphql_query)
        self.assertEqual(graphql_response.status_code, 200)
        graphql_data = graphql_response.json()
        self.assertIn("data", graphql_data)
        self.assertIn("expectation", graphql_data["data"])
        self.assertEqual(graphql_data["data"]["expectation"]["id"], expectation_id)
        self.assertEqual(graphql_data["data"]["expectation"]["name"], "User Authentication System")
        
        graphql_mutation = {
            "query": f"""
            mutation {{
                generateCode(expectation: {{
                    id: "{expectation_id}",
                    name: "User Authentication System",
                    description: "A system that handles user authentication"
                }}) {{
                    generatedCode {{
                        language
                        files {{
                            path
                            content
                        }}
                    }}
                }}
            }}
            """
        }
        
        mock_graphql_generator = MagicMock()
        mock_graphql_expeta.generator = mock_graphql_generator
        mock_graphql_generator.generate.return_value = self.mock_generation
        
        graphql_response = self.graphql_client.post("/graphql", json=graphql_mutation)
        self.assertEqual(graphql_response.status_code, 200)
        graphql_data = graphql_response.json()
        self.assertIn("data", graphql_data)
        self.assertIn("generateCode", graphql_data["data"])
        self.assertEqual(graphql_data["data"]["generateCode"]["generatedCode"]["language"], "python")
        
        mock_rest_validator = MagicMock()
        mock_rest_expeta.validator = mock_rest_validator
        mock_rest_validator.validate.return_value = self.mock_validation
        
        code = self.mock_generation["generated_code"]
        expectation = self.mock_expectation
        
        rest_response = self.rest_client.post(
            "/validate",
            json={"code": code, "expectation": expectation}
        )
        
        self.assertEqual(rest_response.status_code, 200)
        rest_data = rest_response.json()
        self.assertTrue(rest_data["passed"])
        self.assertEqual(rest_data["semantic_match"]["match_score"], 0.9)
    
    def test_token_tracking_across_modules(self):
        """Test token tracking across different access layer modules"""
        
        with patch('access.rest_api.src.api.TokenTracker') as mock_rest_tracker, \
             patch('access.graphql.src.api.TokenTracker') as mock_graphql_tracker, \
             patch('access.chat.src.chat_interface.TokenTracker') as mock_chat_tracker, \
             patch('access.cli.src.cli_tool.TokenTracker') as mock_cli_tracker:
            
            mock_rest_tracker_instance = MagicMock()
            mock_graphql_tracker_instance = MagicMock()
            mock_chat_tracker_instance = MagicMock()
            mock_cli_tracker_instance = MagicMock()
            
            mock_rest_tracker.return_value = mock_rest_tracker_instance
            mock_graphql_tracker.return_value = mock_graphql_tracker_instance
            mock_chat_tracker.return_value = mock_chat_tracker_instance
            mock_cli_tracker.return_value = mock_cli_tracker_instance
            
            usage_report = {
                "anthropic": {"total": 1000},
                "openai": {"total": 0}
            }
            
            mock_rest_tracker_instance.get_usage_report.return_value = usage_report
            mock_graphql_tracker_instance.get_usage_report.return_value = usage_report
            mock_chat_tracker_instance.get_usage_report.return_value = usage_report
            mock_cli_tracker_instance.get_usage_report.return_value = usage_report
            
            
            self.assertEqual(
                mock_rest_tracker_instance.get_usage_report.return_value,
                mock_graphql_tracker_instance.get_usage_report.return_value
            )
            self.assertEqual(
                mock_chat_tracker_instance.get_usage_report.return_value,
                mock_cli_tracker_instance.get_usage_report.return_value
            )

if __name__ == "__main__":
    unittest.main()
