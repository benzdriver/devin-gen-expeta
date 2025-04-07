"""
Integration tests for real LLM interactions with access layer modules
"""

import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.rest_api.src.api import app as rest_app
from access.graphql.src.api import app as graphql_app
from access.chat.src.chat_interface import ChatInterface
from enhanced_clarifier.enhanced_clarifier import EnhancedClarifier
from llm_router.llm_router import LLMRouter
from utils.token_tracker import TokenTracker

class TestRealLLMIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        from starlette.testclient import TestClient
        
        cls.rest_client = TestClient(rest_app)
        cls.graphql_client = TestClient(graphql_app)
        
        cls.token_tracker = TokenTracker()
        cls.llm_router = LLMRouter()
        cls.llm_router.token_tracker = cls.token_tracker
        
        cls.enhanced_clarifier = EnhancedClarifier(
            llm_router=cls.llm_router,
            token_tracker=cls.token_tracker
        )
        
        cls.chat_interface = ChatInterface()
        
        cls.test_requirement = "Create a simple user authentication system"
    
    def test_default_provider_is_anthropic(self):
        """Test that the default provider is Anthropic"""
        self.assertEqual(self.llm_router.config["default_provider"], "anthropic")
        self.assertEqual(self.llm_router.config["fallback_order"][0], "anthropic")
        self.assertEqual(self.llm_router.config["fallback_order"][1], "openai")
    
    @unittest.skip("Skip real LLM test to avoid token usage in CI")
    def test_enhanced_clarifier_with_real_llm(self):
        """Test enhanced clarifier with real LLM"""
        result = self.enhanced_clarifier.clarify_requirement(self.test_requirement)
        
        self.assertIsNotNone(result)
        self.assertIn("top_level_expectation", result)
        self.assertIn("name", result["top_level_expectation"])
        
        token_usage = self.token_tracker.total_usage
        self.assertGreater(token_usage["anthropic"]["total_tokens"], 0)
        
        report = self.enhanced_clarifier.generate_report(output_file="clarifier_report.json")
        self.assertIn("token_usage", report)
        self.assertIn("clarification_results", report)
        self.assertIn("summary", report)
    
    @unittest.skip("Skip real LLM test to avoid token usage in CI")
    def test_rest_api_with_real_llm(self):
        """Test REST API with real LLM"""
        with patch('access.rest_api.src.api.expeta') as mock_expeta:
            mock_expeta.clarifier = self.enhanced_clarifier
            
            response = self.rest_client.post(
                "/clarify",
                json={"text": self.test_requirement}
            )
            
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertIn("top_level_expectation", result)
            
            token_usage = self.token_tracker.total_usage
            self.assertGreater(token_usage["anthropic"]["total_tokens"], 0)
    
    @unittest.skip("Skip real LLM test to avoid token usage in CI")
    def test_graphql_with_real_llm(self):
        """Test GraphQL with real LLM"""
        with patch('access.graphql.src.api.expeta') as mock_expeta:
            mock_expeta.clarifier = self.enhanced_clarifier
            
            graphql_mutation = {
                "query": """
                mutation {
                    processRequirement(text: "Create a simple user authentication system") {
                        requirement
                        clarification {
                            topLevelExpectation {
                                id
                                name
                                description
                            }
                        }
                        success
                    }
                }
                """
            }
            
            response = self.graphql_client.post("/graphql", json=graphql_mutation)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertIn("data", result)
            self.assertIn("processRequirement", result["data"])
            self.assertIn("clarification", result["data"]["processRequirement"])
            
            token_usage = self.token_tracker.total_usage
            self.assertGreater(token_usage["anthropic"]["total_tokens"], 0)
    
    @unittest.skip("Skip real LLM test to avoid token usage in CI")
    def test_chat_interface_with_real_llm(self):
        """Test chat interface with real LLM"""
        with patch('access.chat.src.chat_interface.expeta') as mock_expeta:
            mock_expeta.clarifier = self.enhanced_clarifier
            
            result = self.chat_interface.process_message(
                self.test_requirement,
                user_id="test_user",
                session_id="test_session"
            )
            
            self.assertIn("response", result)
            self.assertIn("expectation", result)
            
            token_usage = self.token_tracker.total_usage
            self.assertGreater(token_usage["anthropic"]["total_tokens"], 0)
    
    def test_fallback_mechanism(self):
        """Test fallback mechanism from Anthropic to OpenAI"""
        with patch('llm_router.providers.anthropic_provider.AnthropicProvider.send_request') as mock_anthropic:
            mock_anthropic.side_effect = Exception("Anthropic provider failed")
            
            with patch('llm_router.providers.openai_provider.OpenAIProvider.send_request') as mock_openai:
                mock_openai.return_value = {
                    "text": "This is a response from OpenAI",
                    "provider": "openai",
                    "model": "gpt-4",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 20,
                        "total_tokens": 30
                    }
                }
                
                test_router = LLMRouter()
                
                response = test_router.generate("Test prompt")
                
                self.assertEqual(response["provider"], "openai")
                self.assertEqual(response["model"], "gpt-4")
                
                mock_anthropic.assert_called_once()
                mock_openai.assert_called_once()

if __name__ == "__main__":
    unittest.main()
