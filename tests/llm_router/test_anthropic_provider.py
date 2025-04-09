"""
Unit tests for Anthropic Provider

This module contains tests for the Anthropic provider implementation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from llm_router.providers.anthropic_provider import AnthropicProvider

class TestAnthropicProvider(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'ANTHROPIC_API_KEY': 'test-api-key'
        })
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)
        
        # Create provider instance
        self.provider = AnthropicProvider()
    
    def test_initialization(self):
        """Test provider initialization"""
        self.assertIsNotNone(self.provider)
        self.assertIsNotNone(self.provider.client)
        self.assertEqual(self.provider.config, {})
    
    def test_initialization_with_config(self):
        """Test provider initialization with custom config"""
        config = {
            "model": "claude-3-opus-20240229",
            "temperature": 0.5,
            "max_tokens": 2000
        }
        provider = AnthropicProvider(config)
        
        self.assertEqual(provider.config, config)
    
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict('os.environ', clear=True):
            with self.assertRaises(ValueError) as context:
                AnthropicProvider()
            
            self.assertIn("Anthropic API key not found", str(context.exception))
    
    @patch('anthropic.Anthropic')
    def test_send_request(self, mock_anthropic_class):
        """Test sending request to Anthropic API"""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        
        # Set up mock client
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        # Create provider with mock
        provider = AnthropicProvider()
        
        # Test request
        request = {
            "prompt": "Test prompt",
            "options": {
                "temperature": 0.5,
                "max_tokens": 100
            }
        }
        
        response = provider.send_request(request)
        
        # Verify response
        self.assertEqual(response["content"], "Test response")
        self.assertEqual(response["provider"], "anthropic")
        self.assertEqual(response["model"], "claude-3-sonnet-20240229")
        self.assertEqual(response["usage"]["input_tokens"], 10)
        self.assertEqual(response["usage"]["output_tokens"], 20)
        
        # Verify API call
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            temperature=0.5,
            messages=[{"role": "user", "content": "Test prompt"}]
        )
    
    @patch('anthropic.Anthropic')
    def test_send_request_with_error(self, mock_anthropic_class):
        """Test error handling in send_request"""
        # Mock API error
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_client
        
        # Create provider with mock
        provider = AnthropicProvider()
        
        # Test request
        request = {"prompt": "Test prompt"}
        response = provider.send_request(request)
        
        # Verify error response
        self.assertTrue(response["error"])
        self.assertEqual(response["provider"], "anthropic")
        self.assertIn("API Error", response["message"])
    
    def test_prepare_parameters(self):
        """Test parameter preparation"""
        provider = AnthropicProvider()
        
        # Test with default options
        params = provider._prepare_parameters({})
        self.assertEqual(params["model"], "claude-3-sonnet-20240229")
        self.assertEqual(params["max_tokens"], 1000)
        self.assertEqual(params["temperature"], 0.7)
        
        # Test with custom options
        options = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 2000,
            "temperature": 0.5
        }
        params = provider._prepare_parameters(options)
        self.assertEqual(params["model"], "claude-3-opus-20240229")
        self.assertEqual(params["max_tokens"], 2000)
        self.assertEqual(params["temperature"], 0.5)
    
    @patch('anthropic.Anthropic')
    def test_process_response(self, mock_anthropic_class):
        """Test response processing"""
        provider = AnthropicProvider()
        
        # Test successful response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        
        result = provider._process_response(mock_response)
        
        self.assertEqual(result["content"], "Test response")
        self.assertEqual(result["provider"], "anthropic")
        self.assertEqual(result["model"], "claude-3-sonnet-20240229")
        self.assertEqual(result["usage"]["input_tokens"], 10)
        self.assertEqual(result["usage"]["output_tokens"], 20)
        
        # Test error handling
        mock_response = MagicMock()
        mock_response.content = None  # This will cause an error
        
        with self.assertRaises(Exception) as context:
            provider._process_response(mock_response)
        
        self.assertIn("Failed to process Anthropic response", str(context.exception))

if __name__ == '__main__':
    unittest.main() 